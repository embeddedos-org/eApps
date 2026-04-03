# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""3D renderer for fixed-wing aircraft (domain: aerospace)."""

import math

from eosim.gui.renderers import BaseRenderer, register_renderer


class AircraftRenderer(BaseRenderer):
    DOMAIN = "aerospace"
    DISPLAY_NAME = "Aircraft"

    def __init__(self):
        self._trail: list = []
        self._dist = 0.0

    # ---- rotation helpers ----
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

    def _rotate(self, px, py, pz, roll, pitch, heading):
        px, py, pz = self._rot_x(px, py, pz, roll)
        px, py, pz = self._rot_y(px, py, pz, pitch)
        px, py, pz = self._rot_z(px, py, pz, heading)
        return px, py, pz

    def _draw_line(self, ax, pts, roll, pitch, heading, ox, oy, oz, color,
                   lw=1.2):
        xs, ys, zs = [], [], []
        for p in pts:
            rx, ry, rz = self._rotate(p[0], p[1], p[2], roll, pitch, heading)
            xs.append(ox + rx)
            ys.append(oy + ry)
            zs.append(oz + rz)
        ax.plot(xs, ys, zs, color=color, linewidth=lw)

    # ---- renderer interface ----
    def setup(self, ax):
        ax.set_xlim(-5, 5)
        ax.set_ylim(-5, 5)
        ax.set_zlim(0, 40000)
        ax.set_xlabel("X (nm)", fontsize=7)
        ax.set_ylabel("Y (nm)", fontsize=7)
        ax.set_zlabel("Alt (ft)", fontsize=7)
        ax.set_title("Aircraft", fontsize=9)

    def update(self, ax, state: dict):
        alt = state.get("altitude_ft", 0.0)
        spd = state.get("airspeed_kts", 0.0)
        hdg = math.radians(state.get("heading_deg", 0.0))
        roll = math.radians(state.get("roll_deg", 0.0))
        pitch = math.radians(state.get("pitch_deg", 0.0))
        vs = state.get("vs_fpm", 0.0)
        gear_dn = state.get("gear_down", False)
        flaps = state.get("flaps_deg", 0.0)
        phase = state.get("flight_phase", "CRUISE")

        # advance position
        dt = 0.1
        self._dist += spd * dt * 0.0001
        ox = self._dist * math.cos(hdg)
        oy = self._dist * math.sin(hdg)
        oz = alt

        body_color = "#44bbff"

        # fuselage (nose to tail)
        fuselage = [(1.0, 0, 0), (-1.0, 0, 0)]
        self._draw_line(ax, fuselage, roll, pitch, hdg, ox, oy, oz,
                        body_color, 2)

        # wings
        wings = [(0.1, -1.2, 0), (0.1, 1.2, 0)]
        self._draw_line(ax, wings, roll, pitch, hdg, ox, oy, oz,
                        body_color, 2)

        # horizontal tail
        htail = [(-0.9, -0.4, 0), (-0.9, 0.4, 0)]
        self._draw_line(ax, htail, roll, pitch, hdg, ox, oy, oz,
                        body_color, 1.5)

        # vertical tail
        vtail = [(-0.9, 0, 0), (-0.9, 0, 0.4)]
        self._draw_line(ax, vtail, roll, pitch, hdg, ox, oy, oz,
                        body_color, 1.5)

        # flaps — extend wing trailing edges downward
        if flaps > 0:
            flap_a = math.radians(flaps) * 0.3
            for side in (-0.8, 0.8):
                flap_pts = [
                    (-0.1, side, 0),
                    (-0.1 - 0.2 * math.cos(flap_a), side,
                     -0.2 * math.sin(flap_a)),
                ]
                self._draw_line(ax, flap_pts, roll, pitch, hdg, ox, oy, oz,
                                "#ffaa00", 1.0)

        # landing gear
        if gear_dn:
            gear_pts = [
                (0.5, 0, 0, 0.5, 0, -0.3),
                (-0.5, -0.3, 0, -0.5, -0.3, -0.3),
                (-0.5, 0.3, 0, -0.5, 0.3, -0.3),
            ]
            for x1, y1, z1, x2, y2, z2 in gear_pts:
                self._draw_line(ax, [(x1, y1, z1), (x2, y2, z2)],
                                roll, pitch, hdg, ox, oy, oz, "#aaaaaa", 1.0)

        # flight path trail
        self._trail.append((ox, oy, oz))
        if len(self._trail) > 300:
            self._trail = self._trail[-300:]
        if len(self._trail) > 1:
            xs = [p[0] for p in self._trail]
            ys = [p[1] for p in self._trail]
            zs = [p[2] for p in self._trail]
            ax.plot(xs, ys, zs, color="#666666", linewidth=0.5, alpha=0.5)

        # re-center view
        margin = 3
        ax.set_xlim(ox - margin, ox + margin)
        ax.set_ylim(oy - margin, oy + margin)
        ax.set_zlim(max(0, alt - 5000), alt + 5000)

        ax.set_title(
            f"Aircraft  {phase}  {spd:.0f}kts  FL{alt / 100:.0f}  "
            f"VS{vs:+.0f}",
            fontsize=8,
        )


register_renderer("aerospace", AircraftRenderer)
