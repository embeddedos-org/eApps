# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""GPIO pin grid widget for EoSim simulation UI."""
import tkinter as tk
from tkinter import ttk


class GPIOPanel(ttk.LabelFrame):
    """Visual 32-pin GPIO display with clickable input toggles."""

    PIN_SIZE = 24
    COLS = 8
    ROWS = 4

    def __init__(self, parent):
        super().__init__(parent, text="GPIO Pins (32)", padding=4)
        self._pin_rects = []
        self._pin_texts = []
        self._gpio_device = None
        self._build()

    def _build(self):
        canvas_w = self.COLS * (self.PIN_SIZE + 6) + 10
        canvas_h = self.ROWS * (self.PIN_SIZE + 14) + 10
        self.canvas = tk.Canvas(
            self, width=canvas_w, height=canvas_h,
            bg="#2d2d2d", highlightthickness=0,
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self._pin_rects = []
        self._pin_texts = []
        for pin in range(32):
            row, col = divmod(pin, self.COLS)
            x = 8 + col * (self.PIN_SIZE + 6)
            y = 8 + row * (self.PIN_SIZE + 14)

            rect = self.canvas.create_rectangle(
                x, y, x + self.PIN_SIZE, y + self.PIN_SIZE,
                fill="#555555", outline="#888888", width=1,
            )
            label = self.canvas.create_text(
                x + self.PIN_SIZE // 2, y + self.PIN_SIZE + 6,
                text=str(pin), fill="#aaaaaa", font=("Consolas", 7),
            )
            self._pin_rects.append(rect)
            self._pin_texts.append(label)

            self.canvas.tag_bind(rect, "<Button-1>",
                                 lambda e, p=pin: self._on_pin_click(p))

        # Legend
        legend_y = canvas_h - 2
        self.canvas.create_text(
            8, legend_y, anchor=tk.W, fill="#888888",
            text="Green=HIGH  Gray=LOW  Click input pins to toggle",
            font=("", 7),
        )

    def set_gpio_device(self, gpio_device):
        self._gpio_device = gpio_device

    def _on_pin_click(self, pin: int):
        if not self._gpio_device:
            return
        direction = self._gpio_device.direction
        is_output = bool(direction & (1 << pin))
        if is_output:
            return
        current = bool(self._gpio_device.input_val & (1 << pin))
        self._gpio_device.set_input(pin, not current)
        self.update_display(self._gpio_device)

    def update_display(self, gpio_device):
        self._gpio_device = gpio_device
        direction = gpio_device.direction
        output_val = gpio_device.output_val
        input_val = gpio_device.input_val
        irq_pending = gpio_device.irq_pending

        for pin in range(32):
            is_output = bool(direction & (1 << pin))
            if is_output:
                value = bool(output_val & (1 << pin))
            else:
                value = bool(input_val & (1 << pin))

            has_irq = bool(irq_pending & (1 << pin))

            if value:
                fill = "#4ec9b0"
            else:
                fill = "#555555"

            outline = "#ff6b6b" if has_irq else "#888888"
            self.canvas.itemconfigure(self._pin_rects[pin], fill=fill, outline=outline)

            arrow = "\u2191" if is_output else "\u2193"
            self.canvas.itemconfigure(
                self._pin_texts[pin],
                text=f"{arrow}{pin}",
            )

    def reset(self):
        for pin in range(32):
            self.canvas.itemconfigure(
                self._pin_rects[pin], fill="#555555", outline="#888888"
            )
            self.canvas.itemconfigure(self._pin_texts[pin], text=str(pin))
        self._gpio_device = None
