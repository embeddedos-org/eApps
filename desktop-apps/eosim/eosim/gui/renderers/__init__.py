# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""3D renderer registry — base class and domain-specific renderer lookup."""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Type

_REGISTRY: Dict[str, "BaseRenderer"] = {}


class BaseRenderer(ABC):
    """Abstract base for domain-specific 3D renderers."""

    DOMAIN: str = ""
    DISPLAY_NAME: str = ""

    def __init__(self):
        self._trail = []
        self._max_trail = 200

    @abstractmethod
    def setup(self, ax) -> None:
        """Configure axes limits, labels, and static geometry."""

    @abstractmethod
    def update(self, ax, state: dict) -> None:
        """Draw one frame of the 3D scene from *state*."""

    def clear(self, ax):
        ax.cla()
        self._trail.clear()
        self.setup(ax)

    def _add_trail(self, point):
        self._trail.append(point)
        if len(self._trail) > self._max_trail:
            self._trail.pop(0)


class _FallbackRenderer(BaseRenderer):
    DOMAIN = "generic"
    DISPLAY_NAME = "Generic"

    def setup(self, ax):
        ax.set_xlim(-1, 1)
        ax.set_ylim(-1, 1)
        ax.set_zlim(-1, 1)
        ax.set_title("No renderer", fontsize=9)

    def update(self, ax, state: dict):
        ax.set_title("No domain renderer", fontsize=9)


_FALLBACK = _FallbackRenderer()


def register_renderer(domain: str, cls: Type[BaseRenderer]) -> None:
    """Register a renderer class for *domain*."""
    _REGISTRY[domain] = cls()


def get_renderer(domain: str) -> BaseRenderer:
    """Return the renderer for *domain*, or the fallback."""
    return _REGISTRY.get(domain, _FALLBACK)


def list_renderers():
    """Return list of registered domain renderer names."""
    return sorted(_REGISTRY.keys())


def _auto_import():
    import importlib
    import pathlib
    pkg = pathlib.Path(__file__).parent
    for f in pkg.glob("*.py"):
        name = f.stem
        if name.startswith("_"):
            continue
        try:
            importlib.import_module(f".{name}", __package__)
        except Exception:
            pass


_auto_import()
