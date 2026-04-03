# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""3D renderer for weather systems (domain: weather)."""
import math
import random
from eosim.gui.renderers import BaseRenderer, register_renderer


class WeatherRenderer(BaseRenderer):
    DOMAIN = "weather"
    DISPLAY_NAME = "Weather System"

    def __init__(self):
        super().__init__()
        self._particles = []

    def setup(self, ax):
        ax.set_xlim(-10, 10)
        ax.set_ylim(-10, 10)
        ax.set_zlim(0, 10)
        ax.set_xlabel("X", fontsize=7)
        ax.set_ylabel("Y", fontsize=7)
        ax.set_zlabel("Alt (km)", fontsize=7)
        ax.set_title("Weather System", fontsize=9)

    def _draw_wind_vectors(self, ax, speed, direction, count=8):
        dir_rad = math.radians(direction)
        dx = math.cos(dir_rad) * speed * 0.05
        dy = math.sin(dir_rad) * speed * 0.05
        for i in range(count):
            x = random.uniform(-8, 8)
            y = random.uniform(-8, 8)
            z = random.uniform(0.5, 3)
            ax.quiver(x, y, z, dx, dy, 0,
                      color="#88ccff", arrow_length_ratio=0.3,
                      linewidth=0.8, alpha=0.6)

    def _draw_clouds(self, ax, cover_pct, base_alt=5):
        n = int(cover_pct / 10)
        for _ in range(n):
            cx = random.uniform(-7, 7)
            cy = random.uniform(-7, 7)
            for _ in range(5):
                x = cx + random.gauss(0, 1.5)
                y = cy + random.gauss(0, 1.5)
                z = base_alt + random.gauss(0, 0.3)
                ax.scatter([x], [y], [z], color="#cccccc", s=40, alpha=0.4)

    def _draw_rain(self, ax, precip_rate):
        n = int(min(precip_rate * 5, 30))
        for _ in range(n):
            x = random.uniform(-8, 8)
            y = random.uniform(-8, 8)
            z_top = random.uniform(3, 5)
            ax.plot([x, x], [y, y], [z_top, z_top - 0.5],
                    color="#4488ff", linewidth=0.5, alpha=0.6)

    def update(self, ax, state: dict):
        temp = state.get("temperature_c", 20)
        humidity = state.get("humidity_pct", 55)
        pressure = state.get("pressure_hpa", 1013)
        wind_speed = state.get("wind_speed_mps", 5)
        wind_dir = state.get("wind_direction_deg", 180)
        precip = state.get("precipitation_mm_hr", 0)
        cloud_cover = state.get("cloud_cover_pct", 30)
        vis = state.get("visibility_km", 10)

        self._draw_wind_vectors(ax, wind_speed, wind_dir)
        self._draw_clouds(ax, cloud_cover)
        if precip > 0.1:
            self._draw_rain(ax, precip)

        ax.plot([-9, 9], [-9, -9], [0, 0], color="#446633", linewidth=2)
        ax.plot([-9, 9], [9, 9], [0, 0], color="#446633", linewidth=2)

        ax.set_title(
            f"Weather  {temp:.0f}°C  {humidity:.0f}%RH  "
            f"{pressure:.0f}hPa  Wind {wind_speed:.0f}m/s@{wind_dir:.0f}°  "
            f"Rain {precip:.1f}mm/h",
            fontsize=7)


register_renderer("weather", WeatherRenderer)
