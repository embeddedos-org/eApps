# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""Weather domain sensors — weather station, anemometer, radar."""
import math
import random

from eosim.engine.native.peripherals.sensors import SensorBase


class WeatherStation(SensorBase):
    def __init__(self, name='wxstation0', base_addr=0x40140000):
        super().__init__(name, base_addr)
        self.temperature_c = 20.0
        self.humidity_pct = 55.0
        self.pressure_hpa = 1013.25
        self.precipitation_mm_hr = 0.0
        self.visibility_km = 10.0
        self.cloud_cover_pct = 30.0

    def simulate_tick(self):
        super().simulate_tick()
        self.temperature_c += random.gauss(0, 0.02)
        self.humidity_pct = max(0, min(100, self.humidity_pct + random.gauss(0, 0.1)))
        self.pressure_hpa += random.gauss(0, 0.01)
        self.cloud_cover_pct = max(0, min(100, self.cloud_cover_pct + random.gauss(0, 0.2)))

    def set_conditions(self, temp_c, humidity, pressure_hpa):
        self.temperature_c = temp_c
        self.humidity_pct = max(0, min(100, humidity))
        self.pressure_hpa = pressure_hpa

    def read_reg(self, offset):
        if offset == 0x00: return int(self.temperature_c * 100) & 0xFFFFFFFF
        if offset == 0x04: return int(self.humidity_pct * 100) & 0xFFFFFFFF
        if offset == 0x08: return int(self.pressure_hpa * 100) & 0xFFFFFFFF
        return 0


class Anemometer(SensorBase):
    def __init__(self, name='anemometer0', base_addr=0x40140100):
        super().__init__(name, base_addr)
        self.wind_speed_mps = 5.0
        self.wind_direction_deg = 180.0
        self.gust_speed_mps = 7.0

    def simulate_tick(self):
        super().simulate_tick()
        self.wind_speed_mps = max(0, min(100, self.wind_speed_mps + random.gauss(0, 0.2)))
        self.wind_direction_deg = (self.wind_direction_deg + random.gauss(0, 2)) % 360
        self.gust_speed_mps = self.wind_speed_mps * (1 + abs(random.gauss(0, 0.3)))

    def set_wind(self, speed_mps, direction_deg):
        self.wind_speed_mps = max(0, speed_mps)
        self.wind_direction_deg = direction_deg % 360

    def read_reg(self, offset):
        if offset == 0x00: return int(self.wind_speed_mps * 1000) & 0xFFFFFFFF
        if offset == 0x04: return int(self.wind_direction_deg * 100) & 0xFFFFFFFF
        return 0


class RadarSensor(SensorBase):
    def __init__(self, name='radar0', base_addr=0x40140200):
        super().__init__(name, base_addr)
        self.reflectivity_dbz = 0.0
        self.precip_type = 0
        self.echo_top_km = 0.0

    def simulate_tick(self):
        super().simulate_tick()
        self.reflectivity_dbz = max(-30, min(75, self.reflectivity_dbz + random.gauss(0, 0.5)))

    def set_reflectivity(self, dbz):
        self.reflectivity_dbz = dbz

    def read_reg(self, offset):
        if offset == 0x00: return int(self.reflectivity_dbz * 100) & 0xFFFFFFFF
        if offset == 0x04: return self.precip_type & 0xFFFFFFFF
        return 0
