# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""UART terminal widget for EoSim simulation UI."""
import tkinter as tk
from tkinter import ttk


class UARTTerminal(ttk.Frame):
    """Scrolling terminal display for UART output with input injection."""

    def __init__(self, parent):
        super().__init__(parent)
        self._build()

    def _build(self):
        header = ttk.Frame(self)
        header.pack(fill=tk.X)
        ttk.Label(header, text="UART Terminal", font=("", 9, "bold")).pack(
            side=tk.LEFT, padx=4
        )
        ttk.Button(header, text="Clear", width=5, command=self.clear).pack(
            side=tk.RIGHT, padx=2
        )
        ttk.Button(header, text="Copy", width=5, command=self._copy).pack(
            side=tk.RIGHT, padx=2
        )

        text_frame = ttk.Frame(self)
        text_frame.pack(fill=tk.BOTH, expand=True)

        self.text = tk.Text(
            text_frame, wrap=tk.WORD, font=("Consolas", 10),
            bg="#1e1e1e", fg="#d4d4d4", insertbackground="#d4d4d4",
            selectbackground="#264f78", state=tk.DISABLED,
            height=12, width=60,
        )
        scrollbar = ttk.Scrollbar(
            text_frame, orient=tk.VERTICAL, command=self.text.yview
        )
        self.text.configure(yscrollcommand=scrollbar.set)
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        input_frame = ttk.Frame(self)
        input_frame.pack(fill=tk.X, pady=(2, 0))
        ttk.Label(input_frame, text=">").pack(side=tk.LEFT, padx=(4, 2))
        self.input_var = tk.StringVar()
        self.input_entry = ttk.Entry(
            input_frame, textvariable=self.input_var,
            font=("Consolas", 10),
        )
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        self.input_entry.bind("<Return>", self._on_send)
        ttk.Button(
            input_frame, text="Send", width=5, command=self._on_send,
        ).pack(side=tk.RIGHT, padx=2)

        self._on_inject = None

    def set_inject_callback(self, callback):
        self._on_inject = callback

    def _on_send(self, event=None):
        text = self.input_var.get()
        if text and self._on_inject:
            self._on_inject(text + "\n")
        self.input_var.set("")

    def append(self, text: str):
        self.text.configure(state=tk.NORMAL)
        self.text.insert(tk.END, text)
        self.text.see(tk.END)
        self.text.configure(state=tk.DISABLED)

    def clear(self):
        self.text.configure(state=tk.NORMAL)
        self.text.delete("1.0", tk.END)
        self.text.configure(state=tk.DISABLED)

    def _copy(self):
        try:
            content = self.text.get("1.0", tk.END).strip()
            self.clipboard_clear()
            self.clipboard_append(content)
        except tk.TclError:
            pass
