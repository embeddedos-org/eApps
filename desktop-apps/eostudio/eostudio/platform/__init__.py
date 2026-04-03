"""Platform abstraction layer for EoStudio.

Provides automatic platform detection and display backend selection
so that EoStudio runs on Windows, Linux, macOS, EoS, and browsers.
"""

from __future__ import annotations

import os
import platform
import sys
from typing import Callable, Dict, List, Optional, Type

from eostudio.platform.display_backend import DisplayBackend


class PlatformDetector:
    """Detect the current operating system / runtime environment."""

    @staticmethod
    def detect() -> str:
        if os.environ.get("EOS_DISPLAY"):
            return "eos"
        if os.environ.get("EOSTUDIO_WEB"):
            return "browser"
        system = platform.system().lower()
        if system == "windows":
            return "windows"
        elif system == "darwin":
            return "macos"
        elif system == "linux":
            if os.path.exists("/proc/eos") or os.environ.get("EOS_ROOT"):
                return "eos"
            return "linux"
        return "linux"

    @staticmethod
    def get_info() -> Dict[str, str]:
        return {
            "platform": PlatformDetector.detect(),
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "python": platform.python_version(),
            "arch": platform.architecture()[0],
        }


class BackendRegistry:
    """Registry mapping platform identifiers to backend factories."""

    def __init__(self) -> None:
        self._backends: Dict[str, Callable[[], DisplayBackend]] = {}
        self._fallback_order: List[str] = []

    def register(self, platform_id: str,
                 factory: Callable[[], DisplayBackend],
                 priority: int = 0) -> None:
        self._backends[platform_id] = factory
        if platform_id not in self._fallback_order:
            self._fallback_order.insert(priority, platform_id)

    def get(self, platform_id: Optional[str] = None) -> DisplayBackend:
        if platform_id is None:
            platform_id = PlatformDetector.detect()
        factory = self._backends.get(platform_id)
        if factory is not None:
            return factory()
        for pid in self._fallback_order:
            try:
                backend = self._backends[pid]()
                if backend.is_available():
                    return backend
            except Exception:
                continue
        raise RuntimeError(
            f"No display backend available for platform {platform_id!r}. "
            f"Registered: {', '.join(sorted(self._backends))}"
        )

    def list_backends(self) -> List[str]:
        return sorted(self._backends.keys())


_registry = BackendRegistry()


def _register_tkinter() -> DisplayBackend:
    from eostudio.platform.tkinter_backend import TkinterBackend
    return TkinterBackend()


def _register_eos() -> DisplayBackend:
    from eostudio.platform.eos_backend import EosBackend
    return EosBackend()


def _register_web() -> DisplayBackend:
    from eostudio.platform.web_backend import WebBackend
    return WebBackend()


def _register_macos() -> DisplayBackend:
    from eostudio.platform.macos_backend import MacOSBackend
    return MacOSBackend()


_registry.register("windows", _register_tkinter, priority=0)
_registry.register("linux", _register_tkinter, priority=1)
_registry.register("macos", _register_macos, priority=2)
_registry.register("eos", _register_eos, priority=3)
_registry.register("browser", _register_web, priority=4)


def get_backend(platform_id: Optional[str] = None) -> DisplayBackend:
    """Return the appropriate display backend for the current platform."""
    return _registry.get(platform_id)


def get_registry() -> BackendRegistry:
    """Return the global backend registry."""
    return _registry
