"""CAD editor — split sketch/model view with parametric feature tree."""

from __future__ import annotations

import math
import tkinter as tk
import tkinter.ttk as ttk
from typing import Any, Dict, List, Optional, Tuple

from eostudio.gui.widgets.canvas_2d import Canvas2D
from eostudio.gui.widgets.viewport_3d import Viewport3D
from eostudio.gui.widgets.toolbar import ToolBar


class CADEditor(tk.Frame):
    """Parametric CAD editor with 2D sketch + 3D model view and feature tree."""

    def __init__(self, master: tk.Widget, bg: str = "#1e1e2e", fg: str = "#cdd6f4", **kw: Any):
        super().__init__(master, bg=bg, **kw)
        self._bg = bg
        self._fg = fg
        self._sketch_tool = "line"
        self._sketch_entities: List[Dict[str, Any]] = []
        self._features: List[Dict[str, str]] = []
        self._constraints_count = 0
        self._draw_start: Optional[Tuple[float, float]] = None

        self._build_ui()

    def _build_ui(self) -> None:
        self._toolbar = ToolBar(self, orientation="vertical", bg=self._bg, fg=self._fg,
                                on_tool_select=self._on_tool_change)
        self._toolbar.pack(side=tk.LEFT, fill=tk.Y)
        self._toolbar.set_tools([
            ("Sketch", [
                ("line", "╱"), ("circle", "○"), ("arc", "◠"),
                ("rect", "□"), ("dimension", "↔"),
            ]),
            ("View", [("select", "⬚"), ("pan", "✥")]),
        ])
        self._toolbar.select_tool("line")

        right_panel = tk.Frame(self, bg=self._bg, width=220)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y)
        right_panel.pack_propagate(False)

        feat_label = tk.Label(right_panel, text="Features", bg=self._bg, fg=self._fg,
                              font=("Segoe UI", 10, "bold"), anchor=tk.W)
        feat_label.pack(fill=tk.X, padx=8, pady=(8, 4))

        btn_frame = tk.Frame(right_panel, bg=self._bg)
        btn_frame.pack(fill=tk.X, padx=4, pady=2)
        btn_style = {"bg": "#313244", "fg": self._fg, "relief": tk.FLAT,
                     "font": ("Segoe UI", 8), "padx": 6, "pady": 2}
        for label, cmd in [("Extrude", "extrude"), ("Revolve", "revolve"),
                           ("Fillet", "fillet"), ("Chamfer", "chamfer")]:
            tk.Button(btn_frame, text=label, command=lambda c=cmd: self._add_feature(c),
                      **btn_style).pack(side=tk.LEFT, padx=1)

        style = ttk.Style()
        style.configure("CAD.Treeview", background="#181825", foreground=self._fg,
                        fieldbackground="#181825", rowheight=20, font=("Segoe UI", 9))
        style.map("CAD.Treeview", background=[("selected", "#45475a")],
                  foreground=[("selected", "#f9e2af")])

        self._feature_tree = ttk.Treeview(right_panel, style="CAD.Treeview",
                                          show="tree", height=10)
        self._feature_tree.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        self._feature_tree.insert("", tk.END, text="Origin")
        self._feature_tree.insert("", tk.END, text="Sketch 1")

        self._constraint_label = tk.Label(right_panel, text="Constraints: 0",
                                          bg=self._bg, fg="#6c7086",
                                          font=("Consolas", 8))
        self._constraint_label.pack(fill=tk.X, padx=8, pady=4)

        center = tk.PanedWindow(self, orient=tk.VERTICAL, bg=self._bg,
                                sashwidth=4, sashrelief=tk.FLAT)
        center.pack(fill=tk.BOTH, expand=True)

        sketch_frame = tk.Frame(center, bg=self._bg)
        center.add(sketch_frame, stretch="always")
        sketch_header = tk.Label(sketch_frame, text="2D Sketch", bg="#181825", fg=self._fg,
                                 font=("Segoe UI", 9, "bold"), anchor=tk.W)
        sketch_header.pack(fill=tk.X)
        self._sketch = Canvas2D(sketch_frame, bg="#11111b", grid_size=20, snap=True)
        self._sketch.pack(fill=tk.BOTH, expand=True)
        self._sketch.bind("<ButtonPress-1>", self._on_sketch_press)
        self._sketch.bind("<ButtonRelease-1>", self._on_sketch_release)
        self._sketch.bind("<Motion>", self._on_sketch_motion)

        model_frame = tk.Frame(center, bg=self._bg)
        center.add(model_frame, stretch="always")
        model_header = tk.Label(model_frame, text="3D Model", bg="#181825", fg=self._fg,
                                font=("Segoe UI", 9, "bold"), anchor=tk.W)
        model_header.pack(fill=tk.X)
        self._model_view = Viewport3D(model_frame, bg="#11111b")
        self._model_view.pack(fill=tk.BOTH, expand=True)

    # ------------------------------------------------------------------
    # Sketch interaction
    # ------------------------------------------------------------------

    def _on_tool_change(self, tool_id: str) -> None:
        self._sketch_tool = tool_id

    def _on_sketch_press(self, event: tk.Event) -> None:
        wx, wy = self._sketch.screen_to_world(event.x, event.y)
        wx, wy = self._sketch.snap_point(wx, wy)
        self._draw_start = (wx, wy)

    def _on_sketch_motion(self, event: tk.Event) -> None:
        if self._draw_start is None:
            return
        self._sketch.delete("preview")
        wx, wy = self._sketch.screen_to_world(event.x, event.y)
        wx, wy = self._sketch.snap_point(wx, wy)
        x0, y0 = self._draw_start
        if self._sketch_tool == "line":
            self._sketch.draw_line(x0, y0, wx, wy, color="#585b70", tag="preview")
        elif self._sketch_tool == "rect":
            self._sketch.draw_rect(x0, y0, wx, wy, color="#585b70", tag="preview")
        elif self._sketch_tool == "circle":
            r = math.hypot(wx - x0, wy - y0)
            self._sketch.draw_circle(x0, y0, r, color="#585b70", tag="preview")

    def _on_sketch_release(self, event: tk.Event) -> None:
        if self._draw_start is None:
            return
        self._sketch.delete("preview")
        wx, wy = self._sketch.screen_to_world(event.x, event.y)
        wx, wy = self._sketch.snap_point(wx, wy)
        x0, y0 = self._draw_start

        if self._sketch_tool == "line":
            self._sketch.draw_line(x0, y0, wx, wy, color="#89b4fa")
            self._sketch_entities.append({"type": "line", "p0": (x0, y0), "p1": (wx, wy)})
        elif self._sketch_tool == "rect":
            self._sketch.draw_rect(x0, y0, wx, wy, color="#89b4fa")
            self._sketch_entities.append({"type": "rect", "p0": (x0, y0), "p1": (wx, wy)})
        elif self._sketch_tool == "circle":
            r = math.hypot(wx - x0, wy - y0)
            self._sketch.draw_circle(x0, y0, r, color="#89b4fa")
            self._sketch_entities.append({"type": "circle", "center": (x0, y0), "radius": r})
        elif self._sketch_tool == "arc":
            r = math.hypot(wx - x0, wy - y0)
            self._sketch.draw_circle(x0, y0, r, color="#89b4fa")
            self._sketch_entities.append({"type": "arc", "center": (x0, y0), "radius": r})
        elif self._sketch_tool == "dimension":
            mid_x = (x0 + wx) / 2
            mid_y = (y0 + wy) / 2
            dist = math.hypot(wx - x0, wy - y0)
            self._sketch.draw_line(x0, y0, wx, wy, color="#f9e2af", width=1, tag="user")
            self._sketch.draw_text(mid_x, mid_y - 10, f"{dist:.1f}",
                                   color="#f9e2af", tag="user")
            self._constraints_count += 1
            self._constraint_label.config(text=f"Constraints: {self._constraints_count}")

        self._draw_start = None

    # ------------------------------------------------------------------
    # Feature operations
    # ------------------------------------------------------------------

    def _add_feature(self, feat_type: str) -> None:
        name = f"{feat_type.title()} {len(self._features) + 1}"
        self._features.append({"type": feat_type, "name": name})
        self._feature_tree.insert("", tk.END, text=name)
