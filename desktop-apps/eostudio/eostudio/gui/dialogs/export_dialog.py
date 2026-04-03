"""Export dialog — format selection, options, output path, and progress bar."""

from __future__ import annotations

import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
from typing import Any, Callable, Dict, Optional


class ExportDialog(tk.Toplevel):
    """Multi-format export dialog with format-specific options and progress."""

    FORMATS = {
        "STL": {"ext": ".stl", "options": ["Binary", "ASCII"]},
        "OBJ": {"ext": ".obj", "options": []},
        "SVG": {"ext": ".svg", "options": []},
        "PNG": {"ext": ".png", "options": ["Resolution"]},
        "HTML": {"ext": ".html", "options": []},
        "glTF": {"ext": ".gltf", "options": ["Embedded textures"]},
        "DXF": {"ext": ".dxf", "options": ["Version"]},
    }

    def __init__(
        self,
        master: tk.Widget,
        on_export: Optional[Callable[[str, str, Dict[str, Any]], None]] = None,
        bg: str = "#1e1e2e",
        fg: str = "#cdd6f4",
        **kwargs: Any,
    ) -> None:
        super().__init__(master, bg=bg, **kwargs)
        self.title("Export")
        self.geometry("450x400")
        self.transient(master)  # type: ignore[call-overload]
        self._bg = bg
        self._fg = fg
        self._on_export = on_export

        self._build_ui()
        self._update_options()

    def _build_ui(self) -> None:
        tk.Label(self, text="Export Design", bg=self._bg, fg=self._fg,
                 font=("Segoe UI", 14, "bold")).pack(padx=16, pady=(16, 8), anchor=tk.W)

        fmt_frame = tk.Frame(self, bg=self._bg)
        fmt_frame.pack(fill=tk.X, padx=16, pady=4)
        tk.Label(fmt_frame, text="Format:", bg=self._bg, fg=self._fg,
                 font=("Segoe UI", 10)).pack(side=tk.LEFT)
        self._format_var = tk.StringVar(value="STL")
        fmt_combo = ttk.Combobox(fmt_frame, textvariable=self._format_var,
                                 values=list(self.FORMATS.keys()), width=12, state="readonly")
        fmt_combo.pack(side=tk.LEFT, padx=8)
        fmt_combo.bind("<<ComboboxSelected>>", lambda e: self._update_options())

        path_frame = tk.Frame(self, bg=self._bg)
        path_frame.pack(fill=tk.X, padx=16, pady=4)
        tk.Label(path_frame, text="Output:", bg=self._bg, fg=self._fg,
                 font=("Segoe UI", 10)).pack(side=tk.LEFT)
        self._path_var = tk.StringVar(value="")
        tk.Entry(path_frame, textvariable=self._path_var, width=28,
                 bg="#313244", fg=self._fg, insertbackground=self._fg,
                 font=("Consolas", 9), relief=tk.FLAT).pack(side=tk.LEFT, padx=8)
        tk.Button(path_frame, text="Browse…", bg="#313244", fg=self._fg,
                  relief=tk.FLAT, font=("Segoe UI", 8), padx=6,
                  command=self._browse).pack(side=tk.LEFT)

        self._options_frame = tk.LabelFrame(self, text="Format Options", bg=self._bg,
                                            fg="#f9e2af", font=("Segoe UI", 9, "bold"),
                                            bd=1, relief=tk.GROOVE)
        self._options_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=8)

        self._stl_mode_var = tk.StringVar(value="Binary")
        self._png_width_var = tk.StringVar(value="1920")
        self._png_height_var = tk.StringVar(value="1080")
        self._gltf_embed_var = tk.BooleanVar(value=True)
        self._dxf_ver_var = tk.StringVar(value="R2010")

        prog_frame = tk.Frame(self, bg=self._bg)
        prog_frame.pack(fill=tk.X, padx=16, pady=4)
        self._progress = ttk.Progressbar(prog_frame, orient=tk.HORIZONTAL,
                                         length=300, mode="determinate")
        self._progress.pack(fill=tk.X)

        btn_frame = tk.Frame(self, bg=self._bg)
        btn_frame.pack(fill=tk.X, padx=16, pady=(8, 16))
        tk.Button(btn_frame, text="Cancel", bg="#313244", fg=self._fg,
                  relief=tk.FLAT, font=("Segoe UI", 10), padx=16, pady=4,
                  command=self.destroy).pack(side=tk.RIGHT, padx=4)
        tk.Button(btn_frame, text="Export", bg="#89b4fa", fg="#1e1e2e",
                  relief=tk.FLAT, font=("Segoe UI", 10, "bold"), padx=16, pady=4,
                  command=self._do_export).pack(side=tk.RIGHT, padx=4)

    def _update_options(self) -> None:
        for w in self._options_frame.winfo_children():
            w.destroy()

        fmt = self._format_var.get()
        if fmt == "STL":
            tk.Label(self._options_frame, text="Mode:", bg=self._bg, fg=self._fg,
                     font=("Segoe UI", 9)).pack(anchor=tk.W, padx=8, pady=4)
            for mode in ["Binary", "ASCII"]:
                tk.Radiobutton(self._options_frame, text=mode, variable=self._stl_mode_var,
                               value=mode, bg=self._bg, fg=self._fg, selectcolor="#313244",
                               activebackground=self._bg, font=("Segoe UI", 9)).pack(
                    anchor=tk.W, padx=20)

        elif fmt == "PNG":
            res_row = tk.Frame(self._options_frame, bg=self._bg)
            res_row.pack(fill=tk.X, padx=8, pady=8)
            tk.Label(res_row, text="Width:", bg=self._bg, fg=self._fg,
                     font=("Segoe UI", 9)).pack(side=tk.LEFT)
            tk.Entry(res_row, textvariable=self._png_width_var, width=6,
                     bg="#313244", fg=self._fg, insertbackground=self._fg,
                     font=("Consolas", 9), relief=tk.FLAT).pack(side=tk.LEFT, padx=4)
            tk.Label(res_row, text="Height:", bg=self._bg, fg=self._fg,
                     font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(8, 0))
            tk.Entry(res_row, textvariable=self._png_height_var, width=6,
                     bg="#313244", fg=self._fg, insertbackground=self._fg,
                     font=("Consolas", 9), relief=tk.FLAT).pack(side=tk.LEFT, padx=4)

        elif fmt == "glTF":
            tk.Checkbutton(self._options_frame, text="Embed textures",
                           variable=self._gltf_embed_var, bg=self._bg, fg=self._fg,
                           selectcolor="#313244", activebackground=self._bg,
                           font=("Segoe UI", 9)).pack(anchor=tk.W, padx=8, pady=8)

        elif fmt == "DXF":
            tk.Label(self._options_frame, text="DXF Version:", bg=self._bg, fg=self._fg,
                     font=("Segoe UI", 9)).pack(anchor=tk.W, padx=8, pady=4)
            ttk.Combobox(self._options_frame, textvariable=self._dxf_ver_var,
                         values=["R12", "R2000", "R2007", "R2010", "R2018"],
                         width=10, state="readonly").pack(anchor=tk.W, padx=8, pady=4)

        else:
            tk.Label(self._options_frame, text="No additional options for this format.",
                     bg=self._bg, fg="#6c7086", font=("Segoe UI", 9)).pack(pady=20)

    def _browse(self) -> None:
        fmt = self._format_var.get()
        ext = self.FORMATS[fmt]["ext"]
        path = filedialog.asksaveasfilename(
            title=f"Export as {fmt}",
            defaultextension=ext,  # type: ignore[arg-type]
            filetypes=[(fmt, f"*{ext}"), ("All files", "*.*")],
        )
        if path:
            self._path_var.set(path)

    def _do_export(self) -> None:
        fmt = self._format_var.get()
        path = self._path_var.get()
        if not path:
            self._browse()
            path = self._path_var.get()
            if not path:
                return

        options: Dict[str, Any] = {}
        if fmt == "STL":
            options["mode"] = self._stl_mode_var.get()
        elif fmt == "PNG":
            options["width"] = int(self._png_width_var.get() or 1920)
            options["height"] = int(self._png_height_var.get() or 1080)
        elif fmt == "glTF":
            options["embed_textures"] = self._gltf_embed_var.get()
        elif fmt == "DXF":
            options["version"] = self._dxf_ver_var.get()

        self._progress["value"] = 0
        self.update_idletasks()

        for i in range(1, 11):
            self._progress["value"] = i * 10
            self.update_idletasks()
            self.after(50)  # type: ignore[call-arg]

        if self._on_export:
            self._on_export(fmt, path, options)

        self._progress["value"] = 100
        tk.Label(self, text=f"✅ Exported to {path}", bg=self._bg, fg="#a6e3a1",
                 font=("Segoe UI", 9)).pack(pady=4)
