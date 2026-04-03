# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""3D renderer for automotive vehicles (domain: automotive)."""

import math

from eosim.gui.renderers import BaseRenderer, register_renderer


class VehicleRenderer(BaseRenderer):
    DOMAIN = "automotive"
    DISPLAY_NAME = "Vehicle"

    _CAR_L = 2.0   # length
    _CAR_W = 1.0   # width
    _CAR_H = 0.6   # height

    def __init__(self):
        self._trail: list = []
        self._pos_x = 0.0
        self._pos_y = 0.0
        self._heading = 0.0

    @staticmethod
    def _rot_z(px, py, a):
        c, s = math.cos(a), math.sin(a)
        return px * c - py * s, px * s + py * c

    def _box(self, ax, cx, cy, cz, l, w, h, heading, color):
        """Draw a rectangular prism centred at (cx, cy, cz)."""
        hl, hw, hh = l / 2, w / 2, h / 2
        corners = [
            (-hl, -hw), (hl, -hw), (hl, hw), (-hl, hw),
        ]
        rot = [(self._rot_z(x, y, heading)) for x, y in corners]
        bot = [(cx + x, cy + y, cz - hh) for x, y in rot]
        top = [(cx + x, cy + y, cz + hh) for x, y in rot]

        # bottom + top rectangles
        for face in (bot, top):
            xs = [p[0] for p in face] + [face[0][0]]
            ys = [p[1] for p in face] + [face[0][1]]
            zs = [p[2] for p in face] + [face[0][2]]
            ax.plot(xs, ys, zs, color=color, linewidth=1.2)

        # verticals
        for b, t in zip(bot, top):
            ax.plot([b[0], t[0]], [b[1], t[1]], [b[2], t[2]],
                    color=color, linewidth=1.0)

    def _speed_color(self, speed_kmh):
        if speed_kmh < 40:
            return "#00cc00"
        if speed_kmh < 100:
            return "#dddd00"
        return "#ff3300"

    # ---- renderer interface ----
    def setup(self, ax):
        ax.set_xlim(-20, 20)
        ax.set_ylim(-20, 20)
        ax.set_zlim(-1, 5)
        ax.set_xlabel("X", fontsize=7)
        ax.set_ylabel("Y", fontsize=7)
        ax.set_zlabel("Z", fontsize=7)
        ax.set_title("Vehicle", fontsize=9)

    def update(self, ax, state: dict):
        speed = state.get("speed_kmh", 0.0)
        steer_deg = state.get("steering_deg", 0.0)
        gear = state.get("gear", "P")
        soc = state.get("soc_pct", 100.0)
        odo = state.get("odometer_km", 0.0)

        # simple kinematics: advance position
        dt = 0.1  # ~10 FPS
        steer_rad = math.radians(steer_deg)
        v_ms = speed / 3.6
        self._heading += steer_rad * dt * 0.5
        self._pos_x += v_ms * dt * math.cos(self._heading)
        self._pos_y += v_ms * dt * math.sin(self._heading)

        color = self._speed_color(speed)
        cz = self._CAR_H / 2

        # car body
        self._box(ax, self._pos_x, self._pos_y, cz,
                  self._CAR_L, self._CAR_W, self._CAR_H,
                  self._heading, color)

        # front wheel indicators (rotated by steering)
        wl = 0.3
        ww = 0.1
        front_offsets = [(self._CAR_L * 0.35, self._CAR_W * 0.55),
                         (self._CAR_L * 0.35, -self._CAR_W * 0.55)]
        for ox, oy in front_offsets:
            wx, wy = self._rot_z(ox, oy, self._heading)
            self._box(ax, self._pos_x + wx, self._pos_y + wy, 0.15,
                      wl, ww, 0.15, self._heading + steer_rad, "#cccccc")

        # speed vector arrow
        if speed > 0.5:
            dx = math.cos(self._heading) * v_ms * 0.3
            dy = math.sin(self._heading) * v_ms * 0.3
            ax.quiver(self._pos_x, self._pos_y, cz,
                      dx, dy, 0,
                      color=color, arrow_length_ratio=0.25, linewidth=1.5)

        # trail
        self._trail.append((self._pos_x, self._pos_y, 0.0))
        if len(self._trail) > 300:
            self._trail = self._trail[-300:]
        if len(self._trail) > 1:
            xs = [p[0] for p in self._trail]
            ys = [p[1] for p in self._trail]
            zs = [p[2] for p in self._trail]
            ax.plot(xs, ys, zs, color="#555555", linewidth=0.6, alpha=0.5)

        # re-center view on vehicle
        ax.set_xlim(self._pos_x - 15, self._pos_x + 15)
        ax.set_ylim(self._pos_y - 15, self._pos_y + 15)

        ax.set_title(
            f"Vehicle  {speed:.0f} km/h  gear={gear}  SoC={soc:.0f}%  "
            f"odo={odo:.1f}km",
            fontsize=8,
        )


register_renderer("automotive", VehicleRenderer)
