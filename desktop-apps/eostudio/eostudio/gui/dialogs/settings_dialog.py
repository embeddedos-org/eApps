"""Settings dialog for EoStudio."""
from __future__ import annotations

import tkinter as tk
import tkinter.ttk as ttk
from typing import Any, Callable, Dict, Optional


class SettingsDialog(tk.Toplevel):
    """Application settings dialog with theme, LLM, and editor options."""

    def __init__(
        self,
        master: tk.Widget,
        on_apply: Optional[Callable[[Dict[str, Any]], None]] = None,
        bg: str = "#1e1e2e",
        fg: str = "#cdd6f4",
        **kwargs: Any,
    ) -> None:
        super().__init__(master, bg=bg, **kwargs)
        self.title("Settings")
        self.geometry("500x450")
        self.transient(master)  # type: ignore[call-overload]
        self._bg = bg
        self._fg = fg
        self._on_apply = on_apply
        self._build_ui()

    def _build_ui(self) -> None:
        tk.Label(self, text="Settings", bg=self._bg, fg=self._fg,
                 font=("Segoe UI", 14, "bold")).pack(padx=16, pady=(16, 8), anchor=tk.W)

        nb = ttk.Notebook(self)
        nb.pack(fill=tk.BOTH, expand=True, padx=16, pady=4)

        general = tk.Frame(nb, bg=self._bg)
        nb.add(general, text="General")
        tk.Label(general, text="Theme:", bg=self._bg, fg=self._fg,
                 font=("Segoe UI", 10)).pack(anchor=tk.W, padx=12, pady=(12, 4))
        self._theme_var = tk.StringVar(value="dark")
        ttk.Combobox(general, textvariable=self._theme_var,
                     values=["dark", "light"], state="readonly", width=14).pack(anchor=tk.W, padx=12)

        ai_frame = tk.Frame(nb, bg=self._bg)
        nb.add(ai_frame, text="AI / LLM")
        tk.Label(ai_frame, text="Endpoint:", bg=self._bg, fg=self._fg,
                 font=("Segoe UI", 10)).pack(anchor=tk.W, padx=12, pady=(12, 4))
        self._endpoint_var = tk.StringVar(value="http://localhost:11434")
        tk.Entry(ai_frame, textvariable=self._endpoint_var, width=40,
                 bg="#313244", fg=self._fg, insertbackground=self._fg,
                 font=("Consolas", 9), relief=tk.FLAT).pack(anchor=tk.W, padx=12)

        tk.Label(ai_frame, text="Model:", bg=self._bg, fg=self._fg,
                 font=("Segoe UI", 10)).pack(anchor=tk.W, padx=12, pady=(8, 4))
        self._model_var = tk.StringVar(value="llama3")
        tk.Entry(ai_frame, textvariable=self._model_var, width=40,
                 bg="#313244", fg=self._fg, insertbackground=self._fg,
                 font=("Consolas", 9), relief=tk.FLAT).pack(anchor=tk.W, padx=12)

        btn_frame = tk.Frame(self, bg=self._bg)
        btn_frame.pack(fill=tk.X, padx=16, pady=(8, 16))
        tk.Button(btn_frame, text="Cancel", bg="#313244", fg=self._fg,
                  relief=tk.FLAT, font=("Segoe UI", 10), padx=16, pady=4,
                  command=self.destroy).pack(side=tk.RIGHT, padx=4)
        tk.Button(btn_frame, text="Apply", bg="#89b4fa", fg="#1e1e2e",
                  relief=tk.FLAT, font=("Segoe UI", 10, "bold"), padx=16, pady=4,
                  command=self._apply).pack(side=tk.RIGHT, padx=4)

    def _apply(self) -> None:
        settings: Dict[str, Any] = {
            "theme": self._theme_var.get(),
            "llm_endpoint": self._endpoint_var.get(),
            "llm_model": self._model_var.get(),
        }
        if self._on_apply:
            self._on_apply(settings)
        self.destroy()
