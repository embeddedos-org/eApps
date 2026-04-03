# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""3D renderer for satellites (domain: aerospace_sat)."""

import math

from eosim.gui.renderers import BaseRenderer, register_renderer


class SatelliteRenderer(BaseRenderer):
    DOMAIN = "aerospace_sat"
    DISPLAY_NAME = "Satellite"

    _EARTH_R = 1.0  # normalised radius
    _LAT_N = 12
    _LON_N = 24

    def __init__(self):
        self._earth_lines: list | None = None

    # ---- rotation helper ----
    @staticmethod
    def _rot_y(px, py, pz, a):
        c, s = math.cos(a), math.sin(a)
        return px * c + pz * s, py, -px * s + pz * c

    @staticmethod
    def _rot_z(px, py, pz, a):
        c, s = math.cos(a), math.sin(a)
        return px * c - py * s, px * s + py * c, pz

    @staticmethod
    def _rot_x(px, py, pz, a):
        c, s = math.cos(a), math.sin(a)
        return px, py * c - pz * s, py * s + pz * c

    def _build_earth(self):
        """Pre-compute Earth wireframe lines."""
        R = self._EARTH_R
        lines = []
        # latitude circles
        for i in range(self._LAT_N + 1):
            lat = -math.pi / 2 + math.pi * i / self._LAT_N
            r = R * math.cos(lat)
            z = R * math.sin(lat)
            pts = []
            for j in range(self._LON_N + 1):
                lon = 2 * math.pi * j / self._LON_N
                pts.append((r * math.cos(lon), r * math.sin(lon), z))
            lines.append(pts)
        # longitude lines
        for j in range(self._LON_N):
            lon = 2 * math.pi * j / self._LON_N
            pts = []
            for i in range(self._LAT_N + 1):
                lat = -math.pi / 2 + math.pi * i / self._LAT_N
                r = R * math.cos(lat)
                z = R * math.sin(lat)
                pts.append((r * math.cos(lon), r * math.sin(lon), z))
            lines.append(pts)
        return lines

    def _draw_cube(self, ax, cx, cy, cz, size, color):
        """Tiny cube as satellite body."""
        h = size / 2
        verts = [
            (cx - h, cy - h, cz - h), (cx + h, cy - h, cz - h),
            (cx + h, cy + h, cz - h), (cx - h, cy + h, cz - h),
            (cx - h, cy - h, cz + h), (cx + h, cy - h, cz + h),
            (cx + h, cy + h, cz + h), (cx - h, cy + h, cz + h),
        ]
        edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),
            (4, 5), (5, 6), (6, 7), (7, 4),
            (0, 4), (1, 5), (2, 6), (3, 7),
        ]
        for a, b in edges:
            ax.plot(
                [verts[a][0], verts[b][0]],
                [verts[a][1], verts[b][1]],
                [verts[a][2], verts[b][2]],
                color=color, linewidth=0.8,
            )

    # ---- renderer interface ----
    def setup(self, ax):
        lim = 3.0
        ax.set_xlim(-lim, lim)
        ax.set_ylim(-lim, lim)
        ax.set_zlim(-lim, lim)
        ax.set_xlabel("X", fontsize=7)
        ax.set_ylabel("Y", fontsize=7)
        ax.set_zlabel("Z", fontsize=7)
        ax.set_title("Satellite", fontsize=9)

    def update(self, ax, state: dict):
        orbit_alt = state.get("orbit_alt_km", 400.0)
        velocity = state.get("velocity_mps", 7700.0)
        attitude = state.get("attitude", [0.0, 0.0, 0.0])
        in_eclipse = state.get("in_eclipse", False)
        power = state.get("solar_power_w", 0.0)

        # normalise orbit radius
        sat_r = self._EARTH_R + orbit_alt / 6371.0

        # build / draw Earth
        if self._earth_lines is None:
            self._earth_lines = self._build_earth()

        earth_color = "#224488" if not in_eclipse else "#111133"
        for pts in self._earth_lines:
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            zs = [p[2] for p in pts]
            ax.plot(xs, ys, zs, color=earth_color, linewidth=0.3, alpha=0.6)

        # eclipse shading: darken the -X half
        if in_eclipse:
            for i in range(6):
                lat = -math.pi / 2 + math.pi * i / 6
                r = self._EARTH_R * math.cos(lat)
                z = self._EARTH_R * math.sin(lat)
                for j in range(12):
                    lon = math.pi + 2 * math.pi * j / 12
                    ax.scatter(
                        [r * math.cos(lon)], [r * math.sin(lon)], [z],
                        color="#000022", s=3, alpha=0.4, depthshade=False,
                    )

        # orbit ring
        ring_pts = 60
        ring_xs, ring_ys, ring_zs = [], [], []
        for i in range(ring_pts + 1):
            a = 2 * math.pi * i / ring_pts
            ring_xs.append(sat_r * math.cos(a))
            ring_ys.append(sat_r * math.sin(a))
            ring_zs.append(0.0)
        ax.plot(ring_xs, ring_ys, ring_zs, color="#445566", linewidth=0.5,
                alpha=0.4)

        # satellite position (use tick to animate around orbit)
        tick = state.get("tick", 0)
        orbit_angle = (tick * 0.02) % (2 * math.pi)
        sx = sat_r * math.cos(orbit_angle)
        sy = sat_r * math.sin(orbit_angle)
        sz = 0.0

        # satellite body cube
        sat_color = "#ffcc00" if not in_eclipse else "#887744"
        self._draw_cube(ax, sx, sy, sz, 0.08, sat_color)

        # solar panels (two rectangles extending from body)
        panel_len = 0.15
        att_yaw = math.radians(attitude[2]) if len(attitude) > 2 else 0.0
        for sign in (-1, 1):
            px = sx + sign * panel_len * math.cos(att_yaw + orbit_angle)
            py = sy + sign * panel_len * math.sin(att_yaw + orbit_angle)
            ax.plot([sx, px], [sy, py], [sz, sz],
                    color="#4488cc", linewidth=2.5)

        # velocity vector
        v_scale = 0.15
        vx = -math.sin(orbit_angle) * v_scale
        vy = math.cos(orbit_angle) * v_scale
        ax.quiver(sx, sy, sz, vx, vy, 0,
                  color="#ff6644", arrow_length_ratio=0.3, linewidth=1.0)

        # adjust view
        lim = sat_r + 0.5
        ax.set_xlim(-lim, lim)
        ax.set_ylim(-lim, lim)
        ax.set_zlim(-lim, lim)

        ax.set_title(
            f"Satellite  alt={orbit_alt:.0f}km  v={velocity:.0f}m/s  "
            f"{'ECLIPSE' if in_eclipse else 'SUN'}  {power:.0f}W",
            fontsize=8,
        )


register_renderer("aerospace_sat", SatelliteRenderer)
