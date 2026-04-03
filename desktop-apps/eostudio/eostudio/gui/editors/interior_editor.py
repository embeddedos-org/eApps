"""Interior design editor for EoStudio."""
from __future__ import annotations

import tkinter as tk
from typing import Any


class InteriorEditor(tk.Frame):
    """Interior / architectural design editor with room planner."""

    def __init__(self, master: tk.Widget, bg: str = "#1e1e2e", fg: str = "#cdd6f4", **kw: Any) -> None:
        super().__init__(master, bg=bg, **kw)
        self._bg = bg
        self._fg = fg
        self._build_ui()

    def _build_ui(self) -> None:
        header = tk.Label(self, text="Interior Editor", bg=self._bg, fg=self._fg,
                          font=("Segoe UI", 12, "bold"))
        header.pack(fill=tk.X, padx=8, pady=8)
        self._canvas = tk.Canvas(self, bg="#11111b", highlightthickness=0)
        self._canvas.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
