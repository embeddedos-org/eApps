# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""Memory hex dump inspector for EoSim simulation UI."""
import tkinter as tk
from tkinter import ttk


class MemoryView(ttk.LabelFrame):
    """Hex dump memory viewer with address navigation and region selector."""

    def __init__(self, parent):
        super().__init__(parent, text="Memory Inspector", padding=4)
        self._bus = None
        self._build()

    def _build(self):
        ctrl_frame = ttk.Frame(self)
        ctrl_frame.pack(fill=tk.X, pady=(0, 4))

        ttk.Label(ctrl_frame, text="Addr:").pack(side=tk.LEFT, padx=(0, 2))
        self.addr_var = tk.StringVar(value="0x20000000")
        self.addr_entry = ttk.Entry(
            ctrl_frame, textvariable=self.addr_var,
            font=("Consolas", 9), width=12,
        )
        self.addr_entry.pack(side=tk.LEFT, padx=(0, 4))
        self.addr_entry.bind("<Return>", self._on_go)

        ttk.Button(ctrl_frame, text="Go", width=4, command=self._on_go).pack(
            side=tk.LEFT, padx=(0, 8)
        )

        ttk.Label(ctrl_frame, text="Region:").pack(side=tk.LEFT, padx=(0, 2))
        self.region_var = tk.StringVar(value="ram")
        self.region_combo = ttk.Combobox(
            ctrl_frame, textvariable=self.region_var,
            values=["ram"], state="readonly", width=10,
        )
        self.region_combo.pack(side=tk.LEFT, padx=(0, 4))
        self.region_combo.bind("<<ComboboxSelected>>", self._on_region_select)

        # Hex dump display
        self.hex_text = tk.Text(
            self, wrap=tk.NONE, font=("Consolas", 9),
            bg="#1e1e1e", fg="#d4d4d4", insertbackground="#d4d4d4",
            state=tk.DISABLED, height=8, width=75,
        )
        hex_scroll_y = ttk.Scrollbar(
            self, orient=tk.VERTICAL, command=self.hex_text.yview
        )
        hex_scroll_x = ttk.Scrollbar(
            self, orient=tk.HORIZONTAL, command=self.hex_text.xview
        )
        self.hex_text.configure(
            yscrollcommand=hex_scroll_y.set, xscrollcommand=hex_scroll_x.set
        )
        self.hex_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        hex_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        hex_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        # Memory map info
        self.map_label = ttk.Label(
            self, text="", font=("Consolas", 8), foreground="gray",
        )
        self.map_label.pack(fill=tk.X, side=tk.BOTTOM, pady=(4, 0))

    def set_bus(self, bus):
        self._bus = bus
        regions = [r.name for r in bus.regions]
        self.region_combo.configure(values=regions)
        if regions:
            self.region_var.set(regions[0])
        map_lines = []
        for r in bus.regions:
            map_lines.append(
                f"{r.name}: 0x{r.base:08X} ({r.size // 1024}KB)"
            )
        self.map_label.configure(text="  |  ".join(map_lines))

    def _on_go(self, event=None):
        self._refresh_dump()

    def _on_region_select(self, event=None):
        if not self._bus:
            return
        name = self.region_var.get()
        for r in self._bus.regions:
            if r.name == name:
                self.addr_var.set(f"0x{r.base:08X}")
                self._refresh_dump()
                return

    def _refresh_dump(self):
        if not self._bus:
            return
        try:
            addr = int(self.addr_var.get(), 16)
        except ValueError:
            return
        dump = self._bus.dump(addr, 256)

        # Add ASCII sidebar
        lines = []
        for line in dump.split("\n"):
            if not line:
                continue
            parts = line.split(": ", 1)
            if len(parts) == 2:
                hex_part = parts[1]
                bytes_str = hex_part.split()
                ascii_chars = []
                for b in bytes_str:
                    try:
                        val = int(b, 16)
                        ascii_chars.append(
                            chr(val) if 32 <= val < 127 else "."
                        )
                    except ValueError:
                        ascii_chars.append(".")
                ascii_str = "".join(ascii_chars)
                lines.append(f"{parts[0]}: {hex_part:<48s}  |{ascii_str}|")
            else:
                lines.append(line)

        self.hex_text.configure(state=tk.NORMAL)
        self.hex_text.delete("1.0", tk.END)
        self.hex_text.insert("1.0", "\n".join(lines))
        self.hex_text.configure(state=tk.DISABLED)

    def refresh(self):
        self._refresh_dump()

    def reset(self):
        self.hex_text.configure(state=tk.NORMAL)
        self.hex_text.delete("1.0", tk.END)
        self.hex_text.configure(state=tk.DISABLED)
        self.map_label.configure(text="")
        self._bus = None
