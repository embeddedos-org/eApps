"""Configurable toolbar with icon buttons, grouping, active tool indicator, and tooltips."""

from __future__ import annotations

import tkinter as tk
from typing import Any, Callable, Dict, List, Literal, Optional, Tuple


class ToolBar(tk.Frame):
    """Vertical or horizontal toolbar with grouped icon buttons."""

    def __init__(
        self,
        master: tk.Widget,
        orientation: str = "vertical",
        bg: str = "#1e1e2e",
        fg: str = "#cdd6f4",
        on_tool_select: Optional[Callable[[str], None]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(master, bg=bg, **kwargs)
        self._bg = bg
        self._fg = fg
        self._orientation = orientation
        self._on_tool_select = on_tool_select
        self._buttons: Dict[str, tk.Button] = {}
        self._active_tool: Optional[str] = None
        self._tooltip_win: Optional[tk.Toplevel] = None

        self._container = tk.Frame(self, bg=bg)
        side: Literal["top", "bottom", "left", "right"] = "top" if orientation == "vertical" else "left"
        self._container.pack(side=side, fill=tk.BOTH, expand=True)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_tools(self, tool_groups: List[Tuple[str, List[Tuple[str, str]]]]) -> None:
        for w in self._container.winfo_children():
            w.destroy()
        self._buttons.clear()

        side: Literal["top", "bottom", "left", "right"] = "top" if self._orientation == "vertical" else "left"

        for group_name, tools in tool_groups:
            group_frame = tk.Frame(self._container, bg=self._bg)
            group_frame.pack(side=side, padx=2, pady=2)

            if group_name:
                lbl = tk.Label(group_frame, text=group_name, bg=self._bg, fg="#6c7086",
                               font=("Segoe UI", 7), anchor=tk.W)
                lbl.pack(side=side, padx=2, pady=(4, 1))

            for tool_id, icon_text in tools:
                btn = tk.Button(
                    group_frame,
                    text=icon_text,
                    width=3 if self._orientation == "vertical" else None,
                    bg="#313244",
                    fg=self._fg,
                    activebackground="#45475a",
                    activeforeground="#f9e2af",
                    relief=tk.FLAT,
                    font=("Segoe UI", 10),
                    padx=4, pady=2,
                    command=self._make_tool_cmd(tool_id),
                )
                btn.pack(side=side, padx=1, pady=1)
                btn.bind("<Enter>", self._make_enter_handler(tool_id))
                btn.bind("<Leave>", self._make_leave_handler())
                self._buttons[tool_id] = btn

            sep = tk.Frame(self._container, bg="#45475a",
                           width=2 if self._orientation == "vertical" else 1,
                           height=1 if self._orientation == "vertical" else 20)
            sep.pack(side=side, padx=2, pady=4,
                     fill=tk.X if self._orientation == "vertical" else tk.Y)

    def select_tool(self, tool_id: str) -> None:
        self._select_tool(tool_id)

    def get_active_tool(self) -> Optional[str]:
        return self._active_tool

    def _make_tool_cmd(self, tool_id: str) -> Callable[[], None]:
        def cmd() -> None:
            self._select_tool(tool_id)
        return cmd

    def _make_enter_handler(self, tool_id: str) -> Callable[[tk.Event], None]:
        def handler(event: tk.Event) -> None:
            self._show_tooltip(event, tool_id)
        return handler

    def _make_leave_handler(self) -> Callable[[tk.Event], None]:
        def handler(event: tk.Event) -> None:
            self._hide_tooltip()
        return handler

        # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _select_tool(self, tool_id: str) -> None:
        if self._active_tool and self._active_tool in self._buttons:
            self._buttons[self._active_tool].config(bg="#313244", fg=self._fg)

        self._active_tool = tool_id
        if tool_id in self._buttons:
            self._buttons[tool_id].config(bg="#89b4fa", fg="#1e1e2e")

        if self._on_tool_select:
            self._on_tool_select(tool_id)

    def _show_tooltip(self, event: tk.Event, tool_id: str) -> None:
        self._hide_tooltip()
        x = event.widget.winfo_rootx() + event.widget.winfo_width() + 4
        y = event.widget.winfo_rooty()
        self._tooltip_win = tw = tk.Toplevel(self)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=tool_id.replace("_", " ").title(),
                         bg="#313244", fg=self._fg, font=("Segoe UI", 8),
                         padx=6, pady=2, relief=tk.SOLID, bd=1)
        label.pack()

    def _hide_tooltip(self) -> None:
        if self._tooltip_win:
            self._tooltip_win.destroy()
            self._tooltip_win = None
