"""STL format handler for EoStudio meshes (ASCII and binary)."""

from __future__ import annotations

import os
import struct
from typing import List

from eostudio.core.geometry.primitives import Face, Mesh, Vec3


def export_stl_ascii(mesh: Mesh, filepath: str) -> None:
    """Export a :class:`Mesh` as an ASCII STL file.

    Each triangle face is written with its computed normal and three vertices.

    Args:
        mesh: The mesh to export.
        filepath: Destination ``.stl`` file path.
    """
    if not mesh.normals or len(mesh.normals) != len(mesh.vertices):
        mesh.compute_normals()

    os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)

    with open(filepath, "w", encoding="utf-8") as fh:
        fh.write(f"solid {mesh.name}\n")
        for face in mesh.faces:
            v0 = mesh.vertices[face.v0]
            v1 = mesh.vertices[face.v1]
            v2 = mesh.vertices[face.v2]

            edge1 = v1 - v0
            edge2 = v2 - v0
            n = edge1.cross(edge2).normalized()

            fh.write(f"  facet normal {n.x:.6e} {n.y:.6e} {n.z:.6e}\n")
            fh.write("    outer loop\n")
            fh.write(f"      vertex {v0.x:.6e} {v0.y:.6e} {v0.z:.6e}\n")
            fh.write(f"      vertex {v1.x:.6e} {v1.y:.6e} {v1.z:.6e}\n")
            fh.write(f"      vertex {v2.x:.6e} {v2.y:.6e} {v2.z:.6e}\n")
            fh.write("    endloop\n")
            fh.write("  endfacet\n")
        fh.write(f"endsolid {mesh.name}\n")


def export_stl_binary(mesh: Mesh, filepath: str) -> None:
    """Export a :class:`Mesh` as a binary STL file.

    Binary STL layout:
    - 80-byte header
    - 4-byte uint32 triangle count
    - Per triangle: normal (3×float32) + 3 vertices (9×float32) + 2-byte attribute

    Args:
        mesh: The mesh to export.
        filepath: Destination ``.stl`` file path.
    """
    if not mesh.normals or len(mesh.normals) != len(mesh.vertices):
        mesh.compute_normals()

    os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)

    with open(filepath, "wb") as fh:
        header = f"EoStudio STL - {mesh.name}".encode("ascii")
        header = header[:80].ljust(80, b"\0")
        fh.write(header)

        fh.write(struct.pack("<I", len(mesh.faces)))

        for face in mesh.faces:
            v0 = mesh.vertices[face.v0]
            v1 = mesh.vertices[face.v1]
            v2 = mesh.vertices[face.v2]

            edge1 = v1 - v0
            edge2 = v2 - v0
            n = edge1.cross(edge2).normalized()

            fh.write(struct.pack("<fff", n.x, n.y, n.z))
            fh.write(struct.pack("<fff", v0.x, v0.y, v0.z))
            fh.write(struct.pack("<fff", v1.x, v1.y, v1.z))
            fh.write(struct.pack("<fff", v2.x, v2.y, v2.z))
            fh.write(struct.pack("<H", 0))


def import_stl(filepath: str) -> Mesh:
    """Import an STL file, auto-detecting ASCII vs binary format.

    Args:
        filepath: Path to the ``.stl`` file.

    Returns:
        A :class:`Mesh` built from the triangles in the file.
    """
    with open(filepath, "rb") as fh:
        start = fh.read(80)

    if _is_ascii_stl(filepath, start):
        return _import_stl_ascii(filepath)
    return _import_stl_binary(filepath)


def _is_ascii_stl(filepath: str, header: bytes) -> bool:
    """Heuristic: the file begins with ``solid`` and is not valid binary."""
    try:
        text = header.decode("ascii", errors="ignore").strip()
    except Exception:
        return False
    if not text.lower().startswith("solid"):
        return False
    file_size = os.path.getsize(filepath)
    expected_binary_size = 84 + 50 * struct.unpack_from("<I", header if len(header) >= 84 else header.ljust(84, b"\0"), 80)[0]
    if expected_binary_size == file_size:
        return False
    return True


def _import_stl_ascii(filepath: str) -> Mesh:
    """Parse an ASCII STL file."""
    vertices: List[Vec3] = []
    faces: List[Face] = []
    idx = 0

    with open(filepath, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line.startswith("vertex"):
                parts = line.split()
                vertices.append(Vec3(float(parts[1]), float(parts[2]), float(parts[3])))
                if len(vertices) % 3 == 0:
                    base = idx * 3
                    faces.append(Face(base, base + 1, base + 2))
                    idx += 1

    mesh = Mesh(name="imported_stl", vertices=vertices, faces=faces)
    mesh.compute_normals()
    return mesh


def _import_stl_binary(filepath: str) -> Mesh:
    """Parse a binary STL file."""
    vertices: List[Vec3] = []
    faces: List[Face] = []

    with open(filepath, "rb") as fh:
        fh.read(80)
        num_triangles = struct.unpack("<I", fh.read(4))[0]

        for i in range(num_triangles):
            _nx, _ny, _nz = struct.unpack("<fff", fh.read(12))
            v0x, v0y, v0z = struct.unpack("<fff", fh.read(12))
            v1x, v1y, v1z = struct.unpack("<fff", fh.read(12))
            v2x, v2y, v2z = struct.unpack("<fff", fh.read(12))
            fh.read(2)

            base = i * 3
            vertices.extend([
                Vec3(v0x, v0y, v0z),
                Vec3(v1x, v1y, v1z),
                Vec3(v2x, v2y, v2z),
            ])
            faces.append(Face(base, base + 1, base + 2))

    mesh = Mesh(name="imported_stl", vertices=vertices, faces=faces)
    mesh.compute_normals()
    return mesh


class STLExporter:
    """Class-based wrapper for STL export operations."""

    def export_ascii(self, mesh: Mesh) -> str:
        """Export a mesh as an ASCII STL string."""
        if not mesh.normals or len(mesh.normals) != len(mesh.vertices):
            mesh.compute_normals()
        lines = [f"solid {mesh.name}"]
        for face in mesh.faces:
            v0 = mesh.vertices[face.v0]
            v1 = mesh.vertices[face.v1]
            v2 = mesh.vertices[face.v2]
            edge1 = v1 - v0
            edge2 = v2 - v0
            n = edge1.cross(edge2).normalized()
            lines.append(f"  facet normal {n.x:.6e} {n.y:.6e} {n.z:.6e}")
            lines.append("    outer loop")
            lines.append(f"      vertex {v0.x:.6e} {v0.y:.6e} {v0.z:.6e}")
            lines.append(f"      vertex {v1.x:.6e} {v1.y:.6e} {v1.z:.6e}")
            lines.append(f"      vertex {v2.x:.6e} {v2.y:.6e} {v2.z:.6e}")
            lines.append("    endloop")
            lines.append("  endfacet")
        lines.append(f"endsolid {mesh.name}")
        return "\n".join(lines) + "\n"

    def export_binary(self, mesh: Mesh) -> bytes:
        """Export a mesh as binary STL bytes."""
        if not mesh.normals or len(mesh.normals) != len(mesh.vertices):
            mesh.compute_normals()
        import io
        buf = io.BytesIO()
        header = f"EoStudio STL - {mesh.name}".encode("ascii")
        header = header[:80].ljust(80, b"\0")
        buf.write(header)
        buf.write(struct.pack("<I", len(mesh.faces)))
        for face in mesh.faces:
            v0 = mesh.vertices[face.v0]
            v1 = mesh.vertices[face.v1]
            v2 = mesh.vertices[face.v2]
            edge1 = v1 - v0
            edge2 = v2 - v0
            n = edge1.cross(edge2).normalized()
            buf.write(struct.pack("<fff", n.x, n.y, n.z))
            buf.write(struct.pack("<fff", v0.x, v0.y, v0.z))
            buf.write(struct.pack("<fff", v1.x, v1.y, v1.z))
            buf.write(struct.pack("<fff", v2.x, v2.y, v2.z))
            buf.write(struct.pack("<H", 0))
        return buf.getvalue()
