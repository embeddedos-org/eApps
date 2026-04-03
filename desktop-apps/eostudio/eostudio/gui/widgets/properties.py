"""Dynamic properties panel — adapts to the selected object type."""

from __future__ import annotations

import tkinter as tk
import tkinter.ttk as ttk
from typing import Any, Callable, Dict, List, Optional, Tuple


class PropertiesPanel(tk.Frame):
    """Inspectable property panel with transform, material, and custom sections."""

    def __init__(
        self,
        master: tk.Widget,
        bg: str = "#1e1e2e",
        fg: str = "#cdd6f4",
        on_change: Optional[Callable[[str, str, Any], None]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(master, bg=bg, **kwargs)
        self._bg = bg
        self._fg = fg
        self._on_change = on_change
        self._widgets: Dict[str, tk.Widget] = {}
        self._sections: List[tk.Frame] = []

        self._header = tk.Label(self, text="Properties", bg=bg, fg=fg,
                                font=("Segoe UI", 11, "bold"), anchor=tk.W)
        self._header.pack(fill=tk.X, padx=8, pady=(8, 4))

        self._scroll_frame = tk.Frame(self, bg=bg)
        self._scroll_frame.pack(fill=tk.BOTH, expand=True, padx=4)

        self._no_sel_label = tk.Label(self._scroll_frame, text="No object selected",
                                      bg=bg, fg="#6c7086", font=("Segoe UI", 9))
        self._no_sel_label.pack(pady=20)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def show_properties(self, obj_type: str, props: Dict[str, Any]) -> None:
        self._clear()
        self._no_sel_label.pack_forget()

        type_label = tk.Label(self._scroll_frame, text=f"Type: {obj_type}",
                              bg=self._bg, fg="#89b4fa", font=("Segoe UI", 9, "bold"))
        type_label.pack(fill=tk.X, padx=4, pady=(4, 8))
        self._sections.append(type_label)

        if "position" in props or "rotation" in props or "scale" in props:
            self._add_section("Transform")
            if "position" in props:
                self._add_vector3_field("position", "Position", props["position"])
            if "rotation" in props:
                self._add_vector3_field("rotation", "Rotation", props["rotation"])
            if "scale" in props:
                self._add_vector3_field("scale", "Scale", props["scale"])

        if "color" in props or "shininess" in props:
            self._add_section("Material")
            if "color" in props:
                self._add_color_field("color", "Color", props["color"])
            if "shininess" in props:
                self._add_slider_field("shininess", "Shininess", props["shininess"], 0, 128)

        custom_keys = [k for k in props if k not in
                       ("position", "rotation", "scale", "color", "shininess")]
        if custom_keys:
            self._add_section("Properties")
            for key in custom_keys:
                val = props[key]
                if isinstance(val, bool):
                    self._add_check_field(key, key.replace("_", " ").title(), val)
                elif isinstance(val, (int, float)):
                    self._add_entry_field(key, key.replace("_", " ").title(), str(val))
                elif isinstance(val, str):
                    self._add_entry_field(key, key.replace("_", " ").title(), val)
                elif isinstance(val, list) and len(val) <= 5:
                    self._add_combo_field(key, key.replace("_", " ").title(), val)

    def clear_properties(self) -> None:
        self._clear()
        self._no_sel_label.pack(pady=20)

    # ------------------------------------------------------------------
    # Section builders
    # ------------------------------------------------------------------

    def _clear(self) -> None:
        for w in self._sections:
            w.destroy()
        self._sections.clear()
        self._widgets.clear()

    def _add_section(self, title: str) -> None:
        sep = ttk.Separator(self._scroll_frame, orient=tk.HORIZONTAL)
        sep.pack(fill=tk.X, padx=4, pady=4)
        self._sections.append(sep)
        lbl = tk.Label(self._scroll_frame, text=title, bg=self._bg, fg="#f9e2af",
                       font=("Segoe UI", 9, "bold"), anchor=tk.W)
        lbl.pack(fill=tk.X, padx=8, pady=(2, 4))
        self._sections.append(lbl)

    def _add_vector3_field(self, key: str, label: str, values: Tuple[float, float, float]) -> None:
        row = tk.Frame(self._scroll_frame, bg=self._bg)
        row.pack(fill=tk.X, padx=8, pady=1)
        self._sections.append(row)

        tk.Label(row, text=label, bg=self._bg, fg=self._fg,
                 font=("Segoe UI", 8), width=8, anchor=tk.W).pack(side=tk.LEFT)

        for i, (axis, val) in enumerate(zip("XYZ", values)):
            colors = ["#f38ba8", "#a6e3a1", "#89b4fa"]
            tk.Label(row, text=axis, bg=self._bg, fg=colors[i],
                     font=("Consolas", 8, "bold")).pack(side=tk.LEFT)
            var = tk.StringVar(value=f"{val:.2f}")
            ent = tk.Entry(row, textvariable=var, width=6, bg="#313244", fg=self._fg,
                           insertbackground=self._fg, font=("Consolas", 8), relief=tk.FLAT)
            ent.pack(side=tk.LEFT, padx=(0, 4))
            ent.bind("<Return>", lambda e, k=key, idx=i, v=var: self._on_vec_change(k, idx, v))
            self._widgets[f"{key}_{axis}"] = ent

    def _add_entry_field(self, key: str, label: str, value: str) -> None:
        row = tk.Frame(self._scroll_frame, bg=self._bg)
        row.pack(fill=tk.X, padx=8, pady=1)
        self._sections.append(row)
        tk.Label(row, text=label, bg=self._bg, fg=self._fg,
                 font=("Segoe UI", 8), width=12, anchor=tk.W).pack(side=tk.LEFT)
        var = tk.StringVar(value=value)
        ent = tk.Entry(row, textvariable=var, width=14, bg="#313244", fg=self._fg,
                       insertbackground=self._fg, font=("Consolas", 8), relief=tk.FLAT)
        ent.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ent.bind("<Return>", lambda e, k=key, v=var: self._fire_change(k, v.get()))
        self._widgets[key] = ent

    def _add_slider_field(self, key: str, label: str, value: float,
                          from_: float, to: float) -> None:
        row = tk.Frame(self._scroll_frame, bg=self._bg)
        row.pack(fill=tk.X, padx=8, pady=1)
        self._sections.append(row)
        tk.Label(row, text=label, bg=self._bg, fg=self._fg,
                 font=("Segoe UI", 8), width=12, anchor=tk.W).pack(side=tk.LEFT)
        var = tk.DoubleVar(value=value)
        scale = tk.Scale(row, variable=var, from_=from_, to=to, orient=tk.HORIZONTAL,
                         bg=self._bg, fg=self._fg, troughcolor="#313244",
                         highlightthickness=0, length=120, showvalue=True,
                         font=("Consolas", 7),
                         command=lambda v, k=key: self._fire_change(k, float(v)))
        scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self._widgets[key] = scale

    def _add_color_field(self, key: str, label: str, value: str) -> None:
        row = tk.Frame(self._scroll_frame, bg=self._bg)
        row.pack(fill=tk.X, padx=8, pady=1)
        self._sections.append(row)
        tk.Label(row, text=label, bg=self._bg, fg=self._fg,
                 font=("Segoe UI", 8), width=12, anchor=tk.W).pack(side=tk.LEFT)
        swatch = tk.Frame(row, bg=value, width=20, height=20, relief=tk.SUNKEN, bd=1)
        swatch.pack(side=tk.LEFT, padx=(0, 4))
        swatch.pack_propagate(False)
        var = tk.StringVar(value=value)
        ent = tk.Entry(row, textvariable=var, width=8, bg="#313244", fg=self._fg,
                       insertbackground=self._fg, font=("Consolas", 8), relief=tk.FLAT)
        ent.pack(side=tk.LEFT)
        ent.bind("<Return>", lambda e, k=key, v=var, s=swatch: self._on_color_change(k, v, s))
        self._widgets[key] = ent

    def _add_check_field(self, key: str, label: str, value: bool) -> None:
        row = tk.Frame(self._scroll_frame, bg=self._bg)
        row.pack(fill=tk.X, padx=8, pady=1)
        self._sections.append(row)
        var = tk.BooleanVar(value=value)
        cb = tk.Checkbutton(row, text=label, variable=var, bg=self._bg, fg=self._fg,
                            selectcolor="#313244", activebackground=self._bg,
                            font=("Segoe UI", 8),
                            command=lambda k=key, v=var: self._fire_change(k, v.get()))
        cb.pack(side=tk.LEFT)
        self._widgets[key] = cb

    def _add_combo_field(self, key: str, label: str, values: List[str]) -> None:
        row = tk.Frame(self._scroll_frame, bg=self._bg)
        row.pack(fill=tk.X, padx=8, pady=1)
        self._sections.append(row)
        tk.Label(row, text=label, bg=self._bg, fg=self._fg,
                 font=("Segoe UI", 8), width=12, anchor=tk.W).pack(side=tk.LEFT)
        var = tk.StringVar(value=values[0] if values else "")
        combo = ttk.Combobox(row, textvariable=var, values=values, width=12, state="readonly")
        combo.pack(side=tk.LEFT)
        combo.bind("<<ComboboxSelected>>",
                   lambda e, k=key, v=var: self._fire_change(k, v.get()))
        self._widgets[key] = combo

    # ------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------

    def _on_vec_change(self, key: str, idx: int, var: tk.StringVar) -> None:
        try:
            val = float(var.get())
            self._fire_change(key, (idx, val))
        except ValueError:
            pass

    def _on_color_change(self, key: str, var: tk.StringVar, swatch: tk.Frame) -> None:
        color = var.get()
        try:
            swatch.config(bg=color)
            self._fire_change(key, color)
        except tk.TclError:
            pass

    def _fire_change(self, key: str, value: Any) -> None:
        if self._on_change:
            self._on_change("property", key, value)
