# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""3D renderer for patient physiology (domain: physiology)."""
import math
from eosim.gui.renderers import BaseRenderer, register_renderer


class PhysiologyRenderer(BaseRenderer):
    DOMAIN = "physiology"
    DISPLAY_NAME = "Patient Physiology"

    def __init__(self):
        super().__init__()
        self._ecg_history = []

    def setup(self, ax):
        ax.set_xlim(-2, 2)
        ax.set_ylim(-2, 2)
        ax.set_zlim(-1, 3)
        ax.set_xlabel("X", fontsize=7)
        ax.set_ylabel("Y", fontsize=7)
        ax.set_zlabel("Z", fontsize=7)
        ax.set_title("Patient Physiology", fontsize=9)

    def _draw_heart(self, ax, hr, phase, color):
        scale = 0.3 + 0.1 * math.sin(phase * 2 * math.pi)
        n = 20
        for i in range(n):
            t = i / n * 2 * math.pi
            x = scale * 16 * math.sin(t) ** 3 * 0.05
            z = scale * (13 * math.cos(t) - 5 * math.cos(2 * t) -
                         2 * math.cos(3 * t) - math.cos(4 * t)) * 0.05 + 1.5
            ax.scatter([x], [0], [z], color=color, s=8, alpha=0.7)

    def _draw_lungs(self, ax, rr, color):
        expansion = 0.8 + 0.2 * math.sin(rr * 0.1)
        for side in [-1, 1]:
            cx = side * 0.8
            for i in range(10):
                t = i / 10 * math.pi
                x = cx + side * expansion * 0.3 * math.sin(t)
                z = 1.0 + 0.8 * math.cos(t)
                ax.scatter([x], [0], [z], color=color, s=6, alpha=0.5)

    def update(self, ax, state: dict):
        hr = state.get("heart_rate", 72)
        spo2 = state.get("spo2", 98)
        bp_sys = state.get("bp_sys", 120)
        bp_dia = state.get("bp_dia", 80)
        rr = state.get("respiratory_rate", 16)
        temp = state.get("temperature", 37.0)

        heart_color = "#ff0000" if hr > 100 else "#cc0000" if hr > 0 else "#666666"
        phase = (hr / 60.0 * 0.01) % 1.0
        self._draw_heart(ax, hr, phase, heart_color)

        lung_color = "#3399ff" if spo2 > 90 else "#ff6600" if spo2 > 80 else "#ff0000"
        self._draw_lungs(ax, rr, lung_color)

        vitals = [
            f"HR: {hr:.0f} bpm", f"SpO2: {spo2:.0f}%",
            f"BP: {bp_sys:.0f}/{bp_dia:.0f}", f"RR: {rr:.0f}",
            f"Temp: {temp:.1f}°C",
        ]
        y_offset = 1.8
        for i, txt in enumerate(vitals):
            ax.text(-1.8, -1.5, 2.5 - i * 0.3, txt,
                    fontsize=7, color="#cccccc")

        ax.set_title(
            f"Patient  HR={hr:.0f}  SpO₂={spo2:.0f}%  "
            f"BP={bp_sys:.0f}/{bp_dia:.0f}  T={temp:.1f}°C",
            fontsize=8)


register_renderer("physiology", PhysiologyRenderer)
