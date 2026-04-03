"""macOS-specific display backend extending TkinterBackend."""

from __future__ import annotations

import platform as _platform
from typing import Any

from eostudio.platform.tkinter_backend import TkinterBackend
from eostudio.platform.display_backend import WindowConfig


class MacOSBackend(TkinterBackend):
    """TkinterBackend with macOS-specific enhancements.

    - Native menu bar integration
    - Retina / HiDPI awareness
    - macOS-specific keyboard shortcuts (Cmd instead of Ctrl)
    """

    def is_available(self) -> bool:
        return _platform.system().lower() == "darwin" and super().is_available()

    def create_window(self, config: WindowConfig) -> int:
        wid = super().create_window(config)
        win = self._windows.get(wid)
        if win and self._tk:
            try:
                self._tk.createcommand("tk::mac::Quit",
                                       lambda: self.request_quit())
            except Exception:
                pass
            try:
                win.tk.call("tk", "scaling", 2.0)
            except Exception:
                pass
        return wid

    def _setup_macos_menu(self, app_name: str = "EoStudio") -> None:
        if not self._tk:
            return
        import tkinter as tk
        menubar = tk.Menu(self._tk)
        app_menu = tk.Menu(menubar, name="apple", tearoff=0)
        app_menu.add_command(label=f"About {app_name}")
        app_menu.add_separator()
        menubar.add_cascade(menu=app_menu)
        self._tk.config(menu=menubar)
