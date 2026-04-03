"""EoStudio main GUI application.

Integrates the DisplayBackend, PluginManager, and EditorManager
to provide the unified design suite experience.
"""

from __future__ import annotations

import logging
from typing import Any, Callable, Dict, List, Optional

log = logging.getLogger(__name__)


class EditorManager:
    """Registry of editors with tab-switching support."""

    EDITOR_REGISTRY: Dict[str, str] = {
        "3d": "eostudio.gui.editors.modeler_3d",
        "cad": "eostudio.gui.editors.cad_editor",
        "paint": "eostudio.gui.editors.image_editor",
        "game": "eostudio.gui.editors.game_editor",
        "ui": "eostudio.gui.editors.ui_designer",
        "product": "eostudio.gui.editors.product_designer",
        "interior": "eostudio.gui.editors.interior_editor",
        "uml": "eostudio.gui.editors.uml_editor",
        "simulation": "eostudio.gui.editors.simulation_editor",
        "database": "eostudio.gui.editors.database_editor",
        "hardware": "eostudio.gui.editors.hardware_editor",
        "ide": "eostudio.gui.editors.ide_editor",
    }

    def __init__(self) -> None:
        self._editors: Dict[str, Any] = {}
        self._active: Optional[str] = None

    def open_editor(self, name: str) -> bool:
        if name not in self.EDITOR_REGISTRY:
            log.warning("Unknown editor: %s", name)
            return False
        if name not in self._editors:
            self._editors[name] = {"module": self.EDITOR_REGISTRY[name],
                                   "state": "loaded"}
        self._active = name
        log.info("Switched to editor: %s", name)
        return True

    def close_editor(self, name: str) -> bool:
        if name in self._editors:
            del self._editors[name]
            if self._active == name:
                self._active = next(iter(self._editors), None)
            return True
        return False

    @property
    def active_editor(self) -> Optional[str]:
        return self._active

    def list_editors(self) -> List[str]:
        return sorted(self.EDITOR_REGISTRY.keys())

    def list_open(self) -> List[str]:
        return list(self._editors.keys())


class EoStudioApp:
    """Main EoStudio application shell.

    Coordinates the display backend, plugin manager, editor manager,
    and project I/O into a unified application.
    """

    def __init__(self, editor: Optional[str] = None,
                 theme: str = "dark") -> None:
        self._backend: Any = None
        self._plugin_manager: Any = None
        self._editor_manager = EditorManager()
        self._project: Any = None
        self._window_id: int = 0
        self._running: bool = False
        self._menu_items: List[Dict[str, Any]] = []
        self._toolbar_items: List[Dict[str, Any]] = []
        self._status_text: str = "Ready"
        self._initial_editor: Optional[str] = editor
        self._theme: str = theme

    def init(self, editor: Optional[str] = None) -> None:
        """Initialize the application with platform auto-detection."""
        from eostudio.platform import get_backend
        from eostudio.platform.display_backend import WindowConfig

        self._backend = get_backend()
        self._backend.init()

        config = WindowConfig(title="EoStudio", width=1280, height=800)
        self._window_id = self._backend.create_window(config)

        self._init_plugin_manager()
        self._build_menus()

        target_editor = editor or self._initial_editor
        if target_editor and target_editor != "all":
            self._editor_manager.open_editor(target_editor)
        else:
            self._editor_manager.open_editor("3d")

        log.info("EoStudio initialized (editor=%s, theme=%s)",
                 self._editor_manager.active_editor, self._theme)

    def _init_plugin_manager(self) -> None:
        try:
            from eostudio.plugins.plugin_base import PluginManager
            self._plugin_manager = PluginManager()
            self._plugin_manager.discover()

            for pid in list(self._plugin_manager._manifests.keys()):
                try:
                    self._plugin_manager.load(pid)
                    self._plugin_manager.activate(pid, {
                        "app": self,
                        "editor_manager": self._editor_manager,
                    })
                except Exception as exc:
                    log.warning("Failed to activate plugin %s: %s", pid, exc)
        except Exception as exc:
            log.warning("Plugin system unavailable: %s", exc)

    def _build_menus(self) -> None:
        self._menu_items = [
            {"label": "File", "children": [
                {"label": "New Project", "shortcut": "Ctrl+N"},
                {"label": "Open Project", "shortcut": "Ctrl+O"},
                {"label": "Save Project", "shortcut": "Ctrl+S"},
                {"label": "Export", "shortcut": "Ctrl+E"},
                {"label": "Exit", "shortcut": "Alt+F4"},
            ]},
            {"label": "Edit", "children": [
                {"label": "Undo", "shortcut": "Ctrl+Z"},
                {"label": "Redo", "shortcut": "Ctrl+Y"},
                {"label": "Preferences"},
            ]},
            {"label": "View", "children": [
                {"label": f"Open {name.title()} Editor"}
                for name in self._editor_manager.list_editors()
            ]},
            {"label": "Simulate", "children": [
                {"label": "Run with EoSim"},
                {"label": "Select Platform"},
                {"label": "View 3D Product"},
            ]},
            {"label": "Help", "children": [
                {"label": "About EoStudio"},
                {"label": "Documentation"},
                {"label": "AI Tutor"},
            ]},
        ]

        if self._plugin_manager:
            for plugin in self._plugin_manager.plugins.values():
                items = plugin.get_menu_items()
                if items:
                    self._menu_items.append({
                        "label": plugin.manifest.name,
                        "children": items,
                    })

    def run(self) -> None:
        """Run the main event loop."""
        if not self._backend:
            self.init()

        self._running = True
        self._backend.run(on_frame=self._on_frame)

    def _on_frame(self) -> None:
        bg = 0x1E1E2E if self._theme == "dark" else 0xF0F2F5
        self._backend.clear(self._window_id, bg)
        self._draw_toolbar()
        self._draw_status_bar()
        self._backend.flush(self._window_id)

    def _draw_toolbar(self) -> None:
        self._backend.draw_rect(self._window_id, 0, 0, 1280, 40, 0x2563EB)
        self._backend.draw_text(self._window_id, 12, 10, "EoStudio",
                                color=0xFFFFFF, font_size=16)
        x = 120
        for editor in self._editor_manager.list_open():
            is_active = editor == self._editor_manager.active_editor
            bg = 0x1D4ED8 if is_active else 0x3B82F6
            self._backend.draw_rect(self._window_id, x, 4, 80, 32, bg)
            self._backend.draw_text(self._window_id, x + 8, 10,
                                    editor.title(), color=0xFFFFFF,
                                    font_size=12)
            x += 88

    def _draw_status_bar(self) -> None:
        w, h = self._backend.get_window_size(self._window_id)
        self._backend.draw_rect(self._window_id, 0, h - 24, w, 24, 0xE5E7EB)
        self._backend.draw_text(self._window_id, 8, h - 20,
                                self._status_text, color=0x6B7280,
                                font_size=11)
        eosim_text = "EoSim: Connected" if self._is_eosim_connected() else "EoSim: Not connected"
        self._backend.draw_text(self._window_id, w - 200, h - 20,
                                eosim_text, color=0x6B7280, font_size=11)

    def _is_eosim_connected(self) -> bool:
        if self._plugin_manager and "eosim" in self._plugin_manager.plugins:
            plugin = self._plugin_manager.plugins["eosim"]
            from eostudio.plugins.plugin_base import PluginState
            return plugin.state == PluginState.ACTIVE  # type: ignore[no-any-return]
        return False

    def set_status(self, text: str) -> None:
        self._status_text = text

    def load_project(self, path: str) -> bool:
        try:
            from eostudio.formats.project import EoStudioProject
            self._project = EoStudioProject.load(path)
            self.set_status(f"Loaded: {path}")
            return True
        except Exception as exc:
            log.error("Failed to load project: %s", exc)
            return False

    def save_project(self, path: str) -> bool:
        if self._project:
            try:
                self._project.save(path)
                self.set_status(f"Saved: {path}")
                return True
            except Exception as exc:
                log.error("Failed to save project: %s", exc)
        return False

    def shutdown(self) -> None:
        if self._plugin_manager:
            for pid in list(self._plugin_manager.plugins.keys()):
                try:
                    self._plugin_manager.deactivate(pid)
                except Exception:
                    pass
        if self._backend:
            self._backend.shutdown()
        log.info("EoStudio shutdown complete")

    @property
    def editor_manager(self) -> EditorManager:
        return self._editor_manager

    @property
    def plugin_manager(self) -> Any:
        return self._plugin_manager
