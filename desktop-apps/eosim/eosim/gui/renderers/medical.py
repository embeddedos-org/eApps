# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""3D renderer for medical patient monitors (domain: medical)."""

import math

from eosim.gui.renderers import BaseRenderer, register_renderer


class MedicalRenderer(BaseRenderer):
    DOMAIN = "medical"
    DISPLAY_NAME = "Medical"

    _ALARM_COLORS = {
        "NONE": "#00cc00",
        1: "#dddd00",
        2: "#ff8800",
        3: "#ff2200",
    }
    _ECG_MAX_SAMPLES = 200

    def __init__(self):
        self._ecg_buf: list = []
        self._pulse_phase = 0.0

    # ---- renderer interface ----
    def setup(self, ax):
        ax.set_xlim(0, self._ECG_MAX_SAMPLES)
        ax.set_ylim(-1, 1)
        ax.set_zlim(-2, 3)
        ax.set_xlabel("Sample", fontsize=7)
        ax.set_ylabel("", fontsize=7)
        ax.set_zlabel("mV", fontsize=7)
        ax.set_title("Medical Monitor", fontsize=9)

    def update(self, ax, state: dict):
        hr = state.get("heart_rate", 72)
        spo2 = state.get("spo2", 98)
        temp = state.get("temperature", 36.6)
        ecg = state.get("ecg_waveform", [])
        alarm = state.get("alarm", "NONE")
        alarm_pri = state.get("alarm_priority", 0)

        # accumulate ECG samples
        if ecg:
            self._ecg_buf.extend(ecg)
        else:
            # generate synthetic blip
            self._pulse_phase += 0.15
            v = 0.3 * math.sin(self._pulse_phase)
            if abs(self._pulse_phase % (2 * math.pi) - math.pi / 2) < 0.3:
                v = 1.5
            self._ecg_buf.append(v)

        if len(self._ecg_buf) > self._ECG_MAX_SAMPLES:
            self._ecg_buf = self._ecg_buf[-self._ECG_MAX_SAMPLES:]

        # alarm colour
        if alarm != "NONE":
            colour = self._ALARM_COLORS.get(alarm_pri, "#ff2200")
        else:
            colour = self._ALARM_COLORS["NONE"]

        # scrolling ECG ribbon: x=sample index, y=0, z=voltage
        n = len(self._ecg_buf)
        if n > 1:
            xs = list(range(n))
            ys = [0.0] * n
            zs = self._ecg_buf[:]
            ax.plot(xs, ys, zs, color=colour, linewidth=1.2)

            # ribbon fill — draw thin vertical lines for "ribbon" effect
            step = max(1, n // 60)
            for i in range(0, n, step):
                ax.plot([xs[i], xs[i]], [0, 0], [0, zs[i]],
                        color=colour, linewidth=0.3, alpha=0.25)

        # heart-rate pulsing sphere
        self._pulse_phase += 0.05
        beat_scale = 0.5 + 0.5 * abs(math.sin(self._pulse_phase * hr / 30))
        sphere_size = (hr / 100.0) * beat_scale * 120
        sphere_x = self._ECG_MAX_SAMPLES + 15
        ax.scatter([sphere_x], [0], [1.0], color="#ff4466", s=sphere_size,
                   depthshade=False, alpha=0.8)
        ax.text(sphere_x, 0, -0.3, f"{hr} bpm",
                fontsize=7, color="#ff4466", ha="center")

        # SpO2 and temperature readouts as text
        ax.text(sphere_x, 0, 2.2, f"SpO2 {spo2}%",
                fontsize=7, color="#44ccff", ha="center")
        ax.text(sphere_x, 0, 1.8, f"Temp {temp:.1f}\u00b0C",
                fontsize=7, color="#ffaa44", ha="center")

        # alarm indicator bar along top
        if alarm != "NONE":
            bar_z = 2.8
            ax.plot([0, self._ECG_MAX_SAMPLES], [0, 0], [bar_z, bar_z],
                    color=colour, linewidth=4, alpha=0.7)
            ax.text(self._ECG_MAX_SAMPLES / 2, 0, bar_z + 0.2,
                    f"ALARM P{alarm_pri}",
                    fontsize=8, color=colour, ha="center",
                    fontweight="bold")

        ax.set_title(
            f"Patient  HR={hr}  SpO2={spo2}%  T={temp:.1f}\u00b0C",
            fontsize=8,
        )


register_renderer("medical", MedicalRenderer)
