"""UI Designer — canvas with snap grid, component palette, flow view, and code export."""

from __future__ import annotations

import tkinter as tk
import tkinter.ttk as ttk
from typing import Any, Dict, List, Optional, Tuple

from eostudio.gui.widgets.canvas_2d import Canvas2D
from eostudio.gui.widgets.toolbar import ToolBar
from eostudio.gui.widgets.properties import PropertiesPanel


class UIDesigner(tk.Frame):
    """Drag-and-drop UI design editor with flow view and multi-framework code export."""

    COMPONENTS = [
        ("button", "Button", "#89b4fa"),
        ("text", "Text", "#cdd6f4"),
        ("input", "Input", "#a6e3a1"),
        ("image", "Image", "#f9e2af"),
        ("container", "Container", "#585b70"),
        ("card", "Card", "#cba6f7"),
        ("appbar", "AppBar", "#f38ba8"),
        ("bottomnav", "BottomNav", "#fab387"),
    ]

    FRAMEWORKS = ["HTML/CSS", "Flutter", "Compose", "React"]

    def __init__(self, master: tk.Widget, bg: str = "#1e1e2e", fg: str = "#cdd6f4", **kw: Any):
        super().__init__(master, bg=bg, **kw)
        self._bg = bg
        self._fg = fg
        self._placed: List[Dict[str, Any]] = []
        self._drag_comp: Optional[str] = None
        self._selected_idx: Optional[int] = None
        self._screens: List[Dict[str, Any]] = [
            {"name": "Home", "x": 100, "y": 100},
            {"name": "Detail", "x": 350, "y": 100},
            {"name": "Settings", "x": 250, "y": 300},
        ]
        self._flows: List[Tuple[int, int]] = [(0, 1), (0, 2)]

        self._build_ui()

    def _build_ui(self) -> None:
        left_panel = tk.Frame(self, bg=self._bg, width=160)
        left_panel.pack(side=tk.LEFT, fill=tk.Y)
        left_panel.pack_propagate(False)

        tk.Label(left_panel, text="Components", bg=self._bg, fg=self._fg,
                 font=("Segoe UI", 10, "bold"), anchor=tk.W).pack(
            fill=tk.X, padx=8, pady=(8, 4))

        for comp_id, comp_name, color in self.COMPONENTS:
            btn = tk.Button(left_panel, text=comp_name, bg="#313244", fg=self._fg,
                            relief=tk.FLAT, font=("Segoe UI", 9), anchor=tk.W,
                            padx=8, pady=4)
            btn.pack(fill=tk.X, padx=4, pady=1)
            btn.bind("<ButtonPress-1>",
                     lambda e, cid=comp_id: self._start_drag(cid))

        right_panel = tk.Frame(self, bg=self._bg, width=220)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y)
        right_panel.pack_propagate(False)

        self._properties = PropertiesPanel(right_panel, bg=self._bg, fg=self._fg,
                                           on_change=self._on_prop_change)
        self._properties.pack(fill=tk.BOTH, expand=True)

        export_frame = tk.LabelFrame(right_panel, text="Code Export", bg=self._bg,
                                     fg="#f9e2af", font=("Segoe UI", 9, "bold"),
                                     bd=1, relief=tk.GROOVE)
        export_frame.pack(fill=tk.X, padx=4, pady=4)

        self._framework_var = tk.StringVar(value=self.FRAMEWORKS[0])
        ttk.Combobox(export_frame, textvariable=self._framework_var,
                     values=self.FRAMEWORKS, width=14, state="readonly").pack(
            padx=4, pady=4)
        tk.Button(export_frame, text="Generate Code", bg="#89b4fa", fg="#1e1e2e",
                  relief=tk.FLAT, font=("Segoe UI", 9), padx=8,
                  command=self._generate_code).pack(padx=4, pady=(0, 4))

        preview_frame = tk.LabelFrame(right_panel, text="Live Preview", bg=self._bg,
                                      fg="#a6e3a1", font=("Segoe UI", 9, "bold"),
                                      bd=1, relief=tk.GROOVE)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        self._preview_canvas = tk.Canvas(preview_frame, bg="#181825", highlightthickness=0)
        self._preview_canvas.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        center = tk.Frame(self, bg=self._bg)
        center.pack(fill=tk.BOTH, expand=True)

        self._tab_nb = ttk.Notebook(center)
        self._tab_nb.pack(fill=tk.BOTH, expand=True)

        design_frame = tk.Frame(self._tab_nb, bg=self._bg)
        self._tab_nb.add(design_frame, text="Design")

        self._canvas = Canvas2D(design_frame, bg="#11111b", grid_size=10, snap=True)
        self._canvas.pack(fill=tk.BOTH, expand=True)
        self._canvas.bind("<ButtonPress-1>", self._on_canvas_click)
        self._canvas.bind("<B1-Motion>", self._on_canvas_drag)
        self._canvas.bind("<ButtonRelease-1>", self._on_canvas_release)

        self._draw_phone_frame()

        flow_frame = tk.Frame(self._tab_nb, bg=self._bg)
        self._tab_nb.add(flow_frame, text="Flow View")

        self._flow_canvas = tk.Canvas(flow_frame, bg="#11111b", highlightthickness=0)
        self._flow_canvas.pack(fill=tk.BOTH, expand=True)
        self._flow_canvas.bind("<Configure>", lambda e: self._draw_flow())

    # ------------------------------------------------------------------
    # Phone frame on design canvas
    # ------------------------------------------------------------------

    def _draw_phone_frame(self) -> None:
        self._canvas.draw_rect(150, 20, 450, 680, color="#45475a", fill="#181825", tag="user")
        self._canvas.draw_rect(150, 20, 450, 60, color="#45475a", fill="#313244", tag="user")
        self._canvas.draw_text(300, 40, "Status Bar", color="#6c7086", tag="user")
        self._canvas.draw_rect(150, 640, 450, 680, color="#45475a", fill="#313244", tag="user")
        self._canvas.draw_text(300, 660, "Navigation", color="#6c7086", tag="user")

    # ------------------------------------------------------------------
    # Drag and drop
    # ------------------------------------------------------------------

    def _start_drag(self, comp_id: str) -> None:
        self._drag_comp = comp_id

    def _on_canvas_click(self, event: tk.Event) -> None:
        if self._drag_comp:
            wx, wy = self._canvas.screen_to_world(event.x, event.y)
            wx, wy = self._canvas.snap_point(wx, wy)
            self._place_component(self._drag_comp, wx, wy)
            self._drag_comp = None
            return

        wx, wy = self._canvas.screen_to_world(event.x, event.y)
        self._selected_idx = None
        for i, comp in enumerate(self._placed):
            cx, cy, cw, ch = comp["x"], comp["y"], comp["width"], comp["height"]
            if cx <= wx <= cx + cw and cy <= wy <= cy + ch:
                self._selected_idx = i
                self._show_comp_properties(comp)
                break

        if self._selected_idx is None:
            self._properties.clear_properties()
        self._redraw_components()

    def _on_canvas_drag(self, event: tk.Event) -> None:
        if self._selected_idx is not None:
            wx, wy = self._canvas.screen_to_world(event.x, event.y)
            wx, wy = self._canvas.snap_point(wx, wy)
            comp = self._placed[self._selected_idx]
            comp["x"] = wx - comp["width"] / 2
            comp["y"] = wy - comp["height"] / 2
            self._redraw_components()

    def _on_canvas_release(self, event: tk.Event) -> None:
        self._update_preview()

    def _place_component(self, comp_id: str, x: float, y: float) -> None:
        sizes = {
            "button": (120, 40), "text": (100, 24), "input": (200, 36),
            "image": (100, 100), "container": (250, 200), "card": (200, 150),
            "appbar": (300, 50), "bottomnav": (300, 50),
        }
        w, h = sizes.get(comp_id, (100, 40))
        color = "#89b4fa"
        for cid, cname, cc in self.COMPONENTS:
            if cid == comp_id:
                color = cc
                break

        self._placed.append({
            "type": comp_id, "x": x, "y": y, "width": w, "height": h,
            "color": color, "text": comp_id.title(),
            "font_size": 12, "padding": 8,
        })
        self._redraw_components()
        self._update_preview()

    def _redraw_components(self) -> None:
        self._canvas.delete("comp")
        for i, comp in enumerate(self._placed):
            outline = "#f9e2af" if i == self._selected_idx else comp["color"]
            width = 2 if i == self._selected_idx else 1
            self._canvas.draw_rect(comp["x"], comp["y"],
                                   comp["x"] + comp["width"],
                                   comp["y"] + comp["height"],
                                   color=outline, fill="#313244", width=width, tag="comp")
            self._canvas.draw_text(comp["x"] + comp["width"] / 2,
                                   comp["y"] + comp["height"] / 2,
                                   comp["text"], color=comp["color"], tag="comp")

    def _show_comp_properties(self, comp: Dict[str, Any]) -> None:
        self._properties.show_properties(comp["type"].title(), {
            "position": (comp["x"], comp["y"], 0),
            "width": comp["width"],
            "height": comp["height"],
            "text": comp["text"],
            "color": comp["color"],
            "font_size": comp["font_size"],
            "padding": comp["padding"],
        })

    def _on_prop_change(self, section: str, key: str, value: Any) -> None:
        if self._selected_idx is not None and self._selected_idx < len(self._placed):
            comp = self._placed[self._selected_idx]
            if key in comp:
                comp[key] = value
                self._redraw_components()

    # ------------------------------------------------------------------
    # Flow view
    # ------------------------------------------------------------------

    def _draw_flow(self) -> None:
        self._flow_canvas.delete("all")
        for si, di in self._flows:
            s, d = self._screens[si], self._screens[di]
            self._flow_canvas.create_line(
                s["x"] + 60, s["y"] + 40, d["x"] + 60, d["y"] + 40,
                fill="#585b70", width=2, arrow=tk.LAST, arrowshape=(10, 12, 5))

        for i, screen in enumerate(self._screens):
            x, y = screen["x"], screen["y"]
            self._flow_canvas.create_rectangle(x, y, x + 120, y + 80,
                                               fill="#313244", outline="#89b4fa", width=2)
            self._flow_canvas.create_text(x + 60, y + 40, text=screen["name"],
                                          fill=self._fg, font=("Segoe UI", 10, "bold"))

    # ------------------------------------------------------------------
    # Preview and code export
    # ------------------------------------------------------------------

    def _update_preview(self) -> None:
        self._preview_canvas.delete("all")
        pw = self._preview_canvas.winfo_width() or 200
        ph = self._preview_canvas.winfo_height() or 300
        scale = min(pw / 300, ph / 660) * 0.9

        self._preview_canvas.create_rectangle(
            10, 10, 10 + 300 * scale, 10 + 660 * scale,
            fill="#181825", outline="#45475a")

        for comp in self._placed:
            x = 10 + (comp["x"] - 150) * scale
            y = 10 + (comp["y"] - 20) * scale
            w = comp["width"] * scale
            h = comp["height"] * scale
            self._preview_canvas.create_rectangle(x, y, x + w, y + h,
                                                  fill="#313244", outline=comp["color"])
            if w > 20 and h > 10:
                self._preview_canvas.create_text(x + w / 2, y + h / 2,
                                                 text=comp["text"][:8],
                                                 fill=comp["color"],
                                                 font=("Segoe UI", max(6, int(8 * scale))))

    def _generate_code(self) -> None:
        framework = self._framework_var.get()
        win = tk.Toplevel(self, bg=self._bg)
        win.title(f"Generated Code — {framework}")
        win.geometry("600x400")
        win.transient(self)

        text = tk.Text(win, bg="#181825", fg=self._fg, insertbackground=self._fg,
                       font=("Consolas", 10), wrap=tk.NONE, relief=tk.FLAT)
        text.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        code = self._build_code(framework)
        text.insert("1.0", code)
        text.config(state=tk.DISABLED)

    def _build_code(self, framework: str) -> str:
        lines: List[str] = []
        if framework == "HTML/CSS":
            lines.append("<!DOCTYPE html>")
            lines.append('<html lang="en"><head><meta charset="UTF-8">')
            lines.append("<style>")
            lines.append("  body { font-family: sans-serif; background: #1e1e2e; color: #cdd6f4; }")
            lines.append("  .container { position: relative; width: 300px; margin: auto; }")
            lines.append("</style></head><body>")
            lines.append('<div class="container">')
            for comp in self._placed:
                tag = {"button": "button", "text": "p", "input": "input",
                       "image": "img", "container": "div", "card": "div",
                       "appbar": "header", "bottomnav": "nav"}.get(comp["type"], "div")
                style = (f"position:absolute;left:{comp['x'] - 150}px;"
                         f"top:{comp['y'] - 20}px;"
                         f"width:{comp['width']}px;height:{comp['height']}px;")
                if tag == "input":
                    lines.append(f'  <input style="{style}" placeholder="{comp["text"]}"/>')
                elif tag == "img":
                    lines.append(f'  <img style="{style}" alt="{comp["text"]}"/>')
                else:
                    lines.append(f'  <{tag} style="{style}">{comp["text"]}</{tag}>')
            lines.append("</div></body></html>")

        elif framework == "Flutter":
            lines.append("import 'package:flutter/material.dart';")
            lines.append("")
            lines.append("class GeneratedScreen extends StatelessWidget {")
            lines.append("  @override")
            lines.append("  Widget build(BuildContext context) {")
            lines.append("    return Scaffold(")
            lines.append("      body: Stack(children: [")
            for comp in self._placed:
                widget = {"button": "ElevatedButton(onPressed: (){}, child: Text('%s'))",
                          "text": "Text('%s')", "input": "TextField(decoration: InputDecoration(hintText: '%s'))",
                          "image": "Image.asset('%s')", "container": "Container(child: Text('%s'))",
                          "card": "Card(child: Center(child: Text('%s')))",
                          "appbar": "AppBar(title: Text('%s'))",
                          "bottomnav": "BottomNavigationBar(items: [])"}.get(comp["type"], "Text('%s')")
                widget_str = widget % comp["text"] if "%s" in widget else widget
                lines.append(f"        Positioned(left: {comp['x']:.0f}, top: {comp['y']:.0f},")
                lines.append(f"          width: {comp['width']:.0f}, height: {comp['height']:.0f},")
                lines.append(f"          child: {widget_str}),")
            lines.append("      ]),")
            lines.append("    );")
            lines.append("  }")
            lines.append("}")

        elif framework == "Compose":
            lines.append("@Composable")
            lines.append("fun GeneratedScreen() {")
            lines.append("    Box(modifier = Modifier.fillMaxSize()) {")
            for comp in self._placed:
                lines.append(f"        // {comp['type']}: {comp['text']}")
                lines.append(f"        Box(modifier = Modifier.offset(x = {comp['x']:.0f}.dp, y = {comp['y']:.0f}.dp)")
                lines.append(f"            .size(width = {comp['width']:.0f}.dp, height = {comp['height']:.0f}.dp)) {{")
                lines.append(f'            Text("{comp["text"]}")')
                lines.append("        }")
            lines.append("    }")
            lines.append("}")

        elif framework == "React":
            lines.append("import React from 'react';")
            lines.append("")
            lines.append("export default function GeneratedScreen() {")
            lines.append("  return (")
            lines.append("    <div style={{position: 'relative', width: 300}}>")
            for comp in self._placed:
                tag = {"button": "button", "text": "span", "input": "input",
                       "container": "div", "card": "div"}.get(comp["type"], "div")
                lines.append(f"      <{tag} style={{{{position:'absolute',")
                lines.append(f"        left:{comp['x']:.0f},top:{comp['y']:.0f},")
                lines.append(f"        width:{comp['width']:.0f},height:{comp['height']:.0f}}}}}>")
                lines.append(f"        {comp['text']}")
                lines.append(f"      </{tag}>")
            lines.append("    </div>")
            lines.append("  );")
            lines.append("}")

        return "\n".join(lines)
