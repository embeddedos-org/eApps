# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""3D renderer for quadrotor drones (domain: robotics_drone)."""

import math

from eosim.gui.renderers import BaseRenderer, register_renderer


class DroneRenderer(BaseRenderer):
    DOMAIN = "robotics_drone"
    DISPLAY_NAME = "Drone"

    _FLIGHT_COLORS = {
        "STABILIZE": "#00cc00",
        "ALT_HOLD": "#3388ff",
        "LOITER": "#00cccc",
        "RTL": "#ff8800",
        "DISARMED": "#cc0000",
    }
    _ARM_LENGTH = 0.6

    def __init__(self):
        self._trail: list = []

    # ---- rotation helpers (math module only) ----
    @staticmethod
    def _rot_x(px, py, pz, a):
        c, s = math.cos(a), math.sin(a)
        return px, py * c - pz * s, py * s + pz * c

    @staticmethod
    def _rot_y(px, py, pz, a):
        c, s = math.cos(a), math.sin(a)
        return px * c + pz * s, py, -px * s + pz * c

    @staticmethod
    def _rot_z(px, py, pz, a):
        c, s = math.cos(a), math.sin(a)
        return px * c - py * s, px * s + py * c, pz

    def _rotate(self, px, py, pz, roll, pitch, yaw):
        px, py, pz = self._rot_x(px, py, pz, roll)
        px, py, pz = self._rot_y(px, py, pz, pitch)
        px, py, pz = self._rot_z(px, py, pz, yaw)
        return px, py, pz

    # ---- renderer interface ----
    def setup(self, ax):
        ax.set_xlim(-2, 2)
        ax.set_ylim(-2, 2)
        ax.set_zlim(0, 20)
        ax.set_xlabel("X", fontsize=7)
        ax.set_ylabel("Y", fontsize=7)
        ax.set_zlabel("Alt (m)", fontsize=7)
        ax.set_title("Drone", fontsize=9)

    def update(self, ax, state: dict):
        alt = state.get("altitude_m", 0.0)
        roll = math.radians(state.get("roll_deg", 0.0))
        pitch = math.radians(state.get("pitch_deg", 0.0))
        yaw = math.radians(state.get("yaw_deg", 0.0))
        motors = state.get("motor_rpm", [0, 0, 0, 0])
        mode = state.get("flight_mode", "DISARMED")
        soc = state.get("soc_pct", 100)

        color = self._FLIGHT_COLORS.get(mode, "#888888")

        # arm endpoints in body frame (X-config)
        arm_dirs = [(1, 1, 0), (-1, 1, 0), (-1, -1, 0), (1, -1, 0)]
        L = self._ARM_LENGTH
        cx, cy, cz = 0.0, 0.0, alt

        for i, (dx, dy, dz) in enumerate(arm_dirs):
            norm = math.sqrt(dx * dx + dy * dy)
            bx, by, bz = L * dx / norm, L * dy / norm, 0.0
            rx, ry, rz = self._rotate(bx, by, bz, roll, pitch, yaw)
            tx, ty, tz = cx + rx, cy + ry, cz + rz

            # arm line
            ax.plot([cx, tx], [cy, ty], [cz, tz], color=color, linewidth=1.5)

            # motor circle sized by RPM
            rpm = motors[i] if i < len(motors) else 0
            radius = max(rpm, 500) / 10000.0
            for t in range(0, 360, 30):
                a = math.radians(t)
                a2 = math.radians(t + 30)
                x1 = tx + radius * math.cos(a)
                y1 = ty + radius * math.sin(a)
                x2 = tx + radius * math.cos(a2)
                y2 = ty + radius * math.sin(a2)
                ax.plot([x1, x2], [y1, y2], [tz, tz], color=color,
                        linewidth=0.8)

        # centre dot
        ax.scatter([cx], [cy], [cz], color=color, s=30, depthshade=False)

        # altitude trail
        tick = state.get("tick", len(self._trail))
        self._trail.append((tick, 0.0, alt))
        if len(self._trail) > 200:
            self._trail = self._trail[-200:]
        if len(self._trail) > 1:
            xs = [p[0] * 0.02 for p in self._trail]
            ys = [p[1] for p in self._trail]
            zs = [p[2] for p in self._trail]
            ax.plot(xs, ys, zs, color="#aaaaaa", linewidth=0.6, alpha=0.5)

        # info text
        ax.set_title(
            f"Drone  {mode}  alt={alt:.1f}m  SoC={soc:.0f}%",
            fontsize=8,
        )


register_renderer("robotics_drone", DroneRenderer)
