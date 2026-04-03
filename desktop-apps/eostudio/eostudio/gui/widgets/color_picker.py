"""HSV color wheel picker with RGB sliders, hex input, preview swatch, and recent colors."""

from __future__ import annotations

import colorsys
import math
import tkinter as tk
from typing import Any, Callable, List, Optional, Tuple


class ColorPicker(tk.Frame):
    """Full-featured color picker widget."""

    MAX_RECENT = 10

    def __init__(
        self,
        master: tk.Widget,
        initial_color: str = "#89b4fa",
        bg: str = "#1e1e2e",
        fg: str = "#cdd6f4",
        on_color_change: Optional[Callable[[str], None]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(master, bg=bg, **kwargs)
        self._bg = bg
        self._fg = fg
        self._on_color_change = on_color_change
        self._current_color = initial_color
        self._previous_color = initial_color
        self._recent_colors: List[str] = ["#ff0000", "#00ff00", "#0000ff",
                                          "#ffff00", "#ff00ff", "#00ffff"]
        self._hue: float = 0.0
        self._sat: float = 1.0
        self._val: float = 1.0
        self._updating = False

        self._parse_color(initial_color)
        self._build_ui()
        self.after(50, self._draw_wheel)

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        tk.Label(self, text="Color Picker", bg=self._bg, fg=self._fg,
                 font=("Segoe UI", 10, "bold"), anchor=tk.W).pack(fill=tk.X, padx=6, pady=(6, 2))

        wheel_frame = tk.Frame(self, bg=self._bg)
        wheel_frame.pack(padx=6, pady=4)
        self._wheel_canvas = tk.Canvas(wheel_frame, width=150, height=150,
                                       bg=self._bg, highlightthickness=0)
        self._wheel_canvas.pack()
        self._wheel_canvas.bind("<ButtonPress-1>", self._on_wheel_click)
        self._wheel_canvas.bind("<B1-Motion>", self._on_wheel_click)

        preview_frame = tk.Frame(self, bg=self._bg)
        preview_frame.pack(fill=tk.X, padx=6, pady=2)
        tk.Label(preview_frame, text="Current", bg=self._bg, fg="#6c7086",
                 font=("Segoe UI", 7)).pack(side=tk.LEFT)
        self._current_swatch = tk.Frame(preview_frame, bg=self._current_color,
                                        width=30, height=20, relief=tk.SUNKEN, bd=1)
        self._current_swatch.pack(side=tk.LEFT, padx=2)
        self._current_swatch.pack_propagate(False)
        tk.Label(preview_frame, text="Prev", bg=self._bg, fg="#6c7086",
                 font=("Segoe UI", 7)).pack(side=tk.LEFT, padx=(8, 0))
        self._prev_swatch = tk.Frame(preview_frame, bg=self._previous_color,
                                     width=30, height=20, relief=tk.SUNKEN, bd=1)
        self._prev_swatch.pack(side=tk.LEFT, padx=2)
        self._prev_swatch.pack_propagate(False)
        self._prev_swatch.bind("<Button-1>", self._make_prev_swatch_handler())

        sliders_frame = tk.Frame(self, bg=self._bg)
        sliders_frame.pack(fill=tk.X, padx=6, pady=4)

        self._r_var = tk.IntVar(value=0)
        self._g_var = tk.IntVar(value=0)
        self._b_var = tk.IntVar(value=0)

        for label, var, color in [("R", self._r_var, "#f38ba8"),
                                  ("G", self._g_var, "#a6e3a1"),
                                  ("B", self._b_var, "#89b4fa")]:
            row = tk.Frame(sliders_frame, bg=self._bg)
            row.pack(fill=tk.X, pady=1)
            tk.Label(row, text=label, bg=self._bg, fg=color,
                     font=("Consolas", 8, "bold"), width=2).pack(side=tk.LEFT)
            scale = tk.Scale(row, variable=var, from_=0, to=255, orient=tk.HORIZONTAL,
                             bg=self._bg, fg=self._fg, troughcolor="#313244",
                             highlightthickness=0, length=110, showvalue=False,
                             font=("Consolas", 7),
                             command=self._make_slider_cmd())
            scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
            val_lbl = tk.Label(row, textvariable=var, bg=self._bg, fg=self._fg,
                               font=("Consolas", 7), width=4)
            val_lbl.pack(side=tk.LEFT)

        hex_frame = tk.Frame(self, bg=self._bg)
        hex_frame.pack(fill=tk.X, padx=6, pady=2)
        tk.Label(hex_frame, text="Hex:", bg=self._bg, fg=self._fg,
                 font=("Segoe UI", 8)).pack(side=tk.LEFT)
        self._hex_var = tk.StringVar(value=self._current_color)
        hex_entry = tk.Entry(hex_frame, textvariable=self._hex_var, width=8,
                             bg="#313244", fg=self._fg, insertbackground=self._fg,
                             font=("Consolas", 9), relief=tk.FLAT)
        hex_entry.pack(side=tk.LEFT, padx=4)
        hex_entry.bind("<Return>", self._on_hex_entry)

        eyedropper_btn = tk.Button(hex_frame, text="🔍", bg="#313244", fg=self._fg,
                                   relief=tk.FLAT, font=("Segoe UI", 9),
                                   command=self._eyedropper, padx=4)
        eyedropper_btn.pack(side=tk.LEFT)

        recent_frame = tk.Frame(self, bg=self._bg)
        recent_frame.pack(fill=tk.X, padx=6, pady=(4, 6))
        tk.Label(recent_frame, text="Recent:", bg=self._bg, fg="#6c7086",
                 font=("Segoe UI", 7)).pack(side=tk.LEFT)
        self._recent_frame_inner = tk.Frame(recent_frame, bg=self._bg)
        self._recent_frame_inner.pack(side=tk.LEFT, padx=4)
        self._draw_recent()

        self._sync_sliders_from_hsv()

    # ------------------------------------------------------------------
    # Wheel rendering
    # ------------------------------------------------------------------

    def _draw_wheel(self) -> None:
        self._wheel_canvas.delete("all")
        cx, cy = 75, 75
        radius = 65

        for angle in range(0, 360, 3):
            rad = math.radians(angle)
            for r in range(0, radius, 3):
                h = angle / 360.0
                s = r / radius
                v = self._val
                rgb = colorsys.hsv_to_rgb(h, s, v)
                color = "#{:02x}{:02x}{:02x}".format(
                    int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))
                x = cx + r * math.cos(rad)
                y = cy - r * math.sin(rad)
                self._wheel_canvas.create_rectangle(x - 2, y - 2, x + 2, y + 2,
                                                    fill=color, outline="")

        sel_angle = self._hue * 2 * math.pi
        sel_r = self._sat * radius
        sx = cx + sel_r * math.cos(sel_angle)
        sy = cy - sel_r * math.sin(sel_angle)
        self._wheel_canvas.create_oval(sx - 5, sy - 5, sx + 5, sy + 5,
                                       outline="white", width=2)

    def _on_wheel_click(self, event: tk.Event) -> None:
        cx, cy = 75, 75
        dx = event.x - cx
        dy = -(event.y - cy)
        radius = 65
        dist = math.hypot(dx, dy)
        if dist > radius:
            dist = radius

        angle = math.atan2(dy, dx)
        if angle < 0:
            angle += 2 * math.pi

        self._hue = angle / (2 * math.pi)
        self._sat = dist / radius
        self._sync_sliders_from_hsv()
        self._update_color()

    # ------------------------------------------------------------------
    # Color sync
    # ------------------------------------------------------------------

    def _sync_sliders_from_hsv(self) -> None:
        if self._updating:
            return
        self._updating = True
        r, g, b = colorsys.hsv_to_rgb(self._hue, self._sat, self._val)
        self._r_var.set(int(r * 255))
        self._g_var.set(int(g * 255))
        self._b_var.set(int(b * 255))
        self._current_color = "#{:02x}{:02x}{:02x}".format(
            int(r * 255), int(g * 255), int(b * 255))
        self._hex_var.set(self._current_color)
        self._current_swatch.config(bg=self._current_color)
        self._draw_wheel()
        self._updating = False

    def _on_slider_change(self) -> None:
        if self._updating:
            return
        self._updating = True
        r = self._r_var.get() / 255.0
        g = self._g_var.get() / 255.0
        b = self._b_var.get() / 255.0
        self._hue, self._sat, self._val = colorsys.rgb_to_hsv(r, g, b)
        self._current_color = "#{:02x}{:02x}{:02x}".format(
            int(r * 255), int(g * 255), int(b * 255))
        self._hex_var.set(self._current_color)
        self._current_swatch.config(bg=self._current_color)
        self._draw_wheel()
        self._updating = False
        self._fire_change()

    def _on_hex_entry(self, event: tk.Event) -> None:
        hex_val = self._hex_var.get().strip()
        if not hex_val.startswith("#"):
            hex_val = "#" + hex_val
        try:
            self.set_color(hex_val)
        except (ValueError, tk.TclError):
            pass

    def _update_color(self) -> None:
        self._sync_sliders_from_hsv()
        self._fire_change()

    def _fire_change(self) -> None:
        if self._on_color_change:
            self._on_color_change(self._current_color)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_color(self, hex_color: str) -> None:
        self._previous_color = self._current_color
        self._prev_swatch.config(bg=self._previous_color)
        self._parse_color(hex_color)
        self._sync_sliders_from_hsv()
        self._add_recent(self._current_color)
        self._fire_change()

    def get_color(self) -> str:
        return self._current_color

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _parse_color(self, hex_color: str) -> None:
        hex_color = hex_color.lstrip("#")
        if len(hex_color) == 6:
            r = int(hex_color[0:2], 16) / 255.0
            g = int(hex_color[2:4], 16) / 255.0
            b = int(hex_color[4:6], 16) / 255.0
            self._hue, self._sat, self._val = colorsys.rgb_to_hsv(r, g, b)

    def _add_recent(self, color: str) -> None:
        if color in self._recent_colors:
            self._recent_colors.remove(color)
        self._recent_colors.insert(0, color)
        self._recent_colors = self._recent_colors[:self.MAX_RECENT]
        self._draw_recent()

    def _draw_recent(self) -> None:
        for w in self._recent_frame_inner.winfo_children():
            w.destroy()
        for color in self._recent_colors[:self.MAX_RECENT]:
            swatch = tk.Frame(self._recent_frame_inner, bg=color,
                              width=14, height=14, relief=tk.RAISED, bd=1)
            swatch.pack(side=tk.LEFT, padx=1)
            swatch.pack_propagate(False)
            swatch.bind("<Button-1>", self._make_swatch_handler(color))

    def _make_slider_cmd(self) -> Callable[[str], None]:
        def cmd(v: str) -> None:
            self._on_slider_change()
        return cmd

    def _make_prev_swatch_handler(self) -> Callable[[tk.Event], None]:
        def handler(event: tk.Event) -> None:
            self.set_color(self._previous_color)
        return handler

    def _make_swatch_handler(self, color: str) -> Callable[[tk.Event], None]:
        def handler(event: tk.Event) -> None:
            self.set_color(color)
        return handler

    def _eyedropper(self) -> None:
        pass
