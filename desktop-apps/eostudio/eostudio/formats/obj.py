"""Wavefront OBJ format exporter for EoStudio meshes."""
from __future__ import annotations

import os
from typing import Optional

from eostudio.core.geometry.primitives import Mesh


class OBJExporter:
    """Export a :class:`Mesh` to Wavefront OBJ format.

    OBJ is a simple text-based format widely supported by 3D applications.
    Each vertex is written as ``v x y z`` and each triangular face as
    ``f v0 v1 v2`` (1-indexed).
    """

    def export(self, mesh: Mesh, name: Optional[str] = None) -> str:
        """Export a mesh to an OBJ-formatted string.

        Parameters
        ----------
        mesh : Mesh
            The mesh to export.
        name : str | None
            Optional object name.  Defaults to ``mesh.name``.

        Returns
        -------
        str
            The OBJ file content.
        """
        lines: list[str] = []
        obj_name = name or mesh.name
        lines.append(f"# EoStudio OBJ Export")
        lines.append(f"o {obj_name}")

        for v in mesh.vertices:
            lines.append(f"v {v.x:.6f} {v.y:.6f} {v.z:.6f}")

        if mesh.normals and len(mesh.normals) == len(mesh.vertices):
            for n in mesh.normals:
                lines.append(f"vn {n.x:.6f} {n.y:.6f} {n.z:.6f}")

        for face in mesh.faces:
            # OBJ faces are 1-indexed
            lines.append(f"f {face.v0 + 1} {face.v1 + 1} {face.v2 + 1}")

        return "\n".join(lines) + "\n"

    def export_to_file(self, mesh: Mesh, filepath: str, name: Optional[str] = None) -> None:
        """Export a mesh to a ``.obj`` file.

        Parameters
        ----------
        mesh : Mesh
            The mesh to export.
        filepath : str
            Destination file path.
        name : str | None
            Optional object name.
        """
        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
        content = self.export(mesh, name=name)
        with open(filepath, "w", encoding="utf-8") as fh:
            fh.write(content)
