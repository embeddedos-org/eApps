"""EoStudio project file format (.EoStudio JSON)."""
from __future__ import annotations
import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass
class EoStudioProject:
    """Represents a complete EoStudio project.

    Serialised as a `.EoStudio` JSON file containing scenes, settings,
    and metadata needed to fully reconstruct the design workspace.
    """

    name: str = "Untitled"
    project_name: str = ""
    version: str = "1.0.0"
    author: str = ""
    created: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    modified: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    scenes: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    active_scene: str = ""
    components: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    settings: Dict[str, Any] = field(default_factory=lambda: {
        "units": "mm",
        "grid_size": 10.0,
        "theme": "dark",
        "ai_endpoint": "",
        "ai_model": "gpt-4",
    })

    def __post_init__(self) -> None:
        if not self.project_name:
            self.project_name = self.name

    # ------------------------------------------------------------------
    # Component management
    # ------------------------------------------------------------------

    def add_component(self, component: Dict[str, Any]) -> None:
        """Add a component to the project.

        Args:
            component: Component data dictionary.
        """
        self.components.append(component)

    # ------------------------------------------------------------------
    # Scene management
    # ------------------------------------------------------------------

    def add_scene(self, name: str, scene_data: Optional[Dict[str, Any]] = None) -> None:
        """Add a scene to the project.

        Args:
            name: Unique scene name.
            scene_data: Arbitrary scene payload (meshes, lights, cameras ...).
        """
        if scene_data is None:
            scene_data = {"objects": [], "lights": [], "cameras": []}
        self.scenes[name] = scene_data
        if not self.active_scene:
            self.active_scene = name

    def remove_scene(self, name: str) -> None:
        """Remove a scene by name."""
        self.scenes.pop(name, None)
        if self.active_scene == name:
            self.active_scene = next(iter(self.scenes), "")

    def get_scene(self, name: str) -> Optional[Dict[str, Any]]:
        """Return scene data or `None`."""
        return self.scenes.get(name)

    # ------------------------------------------------------------------
    # Serialisation helpers
    # ------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """Serialise the project to a plain dictionary."""
        return {
            "name": self.name,
            "project_name": self.project_name,
            "version": self.version,
            "author": self.author,
            "created": self.created,
            "modified": self.modified,
            "scenes": self.scenes,
            "active_scene": self.active_scene,
            "components": self.components,
            "metadata": self.metadata,
            "settings": self.settings,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> EoStudioProject:
        """Deserialise from a dictionary."""
        return cls(
            name=data.get("name", data.get("project_name", "Untitled")),
            project_name=data.get("project_name", data.get("name", "Untitled")),
            version=data.get("version", "1.0.0"),
            author=data.get("author", ""),
            created=data.get("created", datetime.now(timezone.utc).isoformat()),
            modified=data.get("modified", datetime.now(timezone.utc).isoformat()),
            scenes=data.get("scenes", {}),
            active_scene=data.get("active_scene", ""),
            components=data.get("components", []),
            metadata=data.get("metadata", {}),
            settings=data.get("settings", {}),
        )

    # ------------------------------------------------------------------
    # File I/O
    # ------------------------------------------------------------------

    def save(self, filepath: str) -> None:
        """Save the project to a `.EoStudio` JSON file.

        Args:
            filepath: Destination path (will be created/overwritten).
        """
        self.modified = datetime.now(timezone.utc).isoformat()
        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as fh:
            json.dump(self.to_dict(), fh, indent=2, ensure_ascii=False)

    @classmethod
    def load(cls, filepath: str) -> EoStudioProject:
        """Load a project from a `.EoStudio` JSON file.

        Args:
            filepath: Path to the file.

        Returns:
            A fully-populated `EoStudioProject` instance.
        """
        with open(filepath, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        return cls.from_dict(data)

    # ------------------------------------------------------------------
    # Export dispatcher
    # ------------------------------------------------------------------

    def export(self, fmt: str, output_path: str, **kwargs: Any) -> None:
        """Export project data in the given format.

        Args:
            fmt: One of `obj`, `stl`, `stl_binary`, `svg`, `gltf`, `dxf`.
            output_path: Destination file path.
            **kwargs: Forwarded to the format-specific exporter.
        """
        from eostudio.formats.obj import export_obj  # type: ignore[attr-defined]
        from eostudio.formats.stl import export_stl_ascii, export_stl_binary
        from eostudio.formats.svg import export_svg  # type: ignore[attr-defined]
        from eostudio.formats.gltf import export_gltf  # type: ignore[attr-defined]
        from eostudio.formats.dxf import export_dxf

        scene_data = self.scenes.get(self.active_scene, {})

        if fmt == "obj":
            mesh = kwargs.get("mesh")
            if mesh is None:
                raise ValueError("OBJ export requires a 'mesh' keyword argument.")
            export_obj(mesh, output_path)
        elif fmt == "stl":
            mesh = kwargs.get("mesh")
            if mesh is None:
                raise ValueError("STL export requires a 'mesh' keyword argument.")
            export_stl_ascii(mesh, output_path)
        elif fmt == "stl_binary":
            mesh = kwargs.get("mesh")
            if mesh is None:
                raise ValueError("STL binary export requires a 'mesh' keyword argument.")
            export_stl_binary(mesh, output_path)
        elif fmt == "svg":
            shapes = kwargs.get("shapes", scene_data.get("objects", []))
            width = kwargs.get("width", 800)
            height = kwargs.get("height", 600)
            export_svg(shapes, output_path, width=width, height=height)
        elif fmt == "gltf":
            mesh = kwargs.get("mesh")
            if mesh is None:
                raise ValueError("glTF export requires a 'mesh' keyword argument.")
            export_gltf(mesh, output_path)
        elif fmt == "dxf":
            entities = kwargs.get("entities", scene_data.get("objects", []))
            export_dxf(entities, output_path)
        else:
            raise ValueError(f"Unsupported export format: {fmt!r}")
