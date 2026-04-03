# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""Physiology domain sensors — heart model, lung model, blood pressure."""
import math
import random

from eosim.engine.native.peripherals.sensors import SensorBase


class HeartModel(SensorBase):
    def __init__(self, name='heart0', base_addr=0x40120000):
        super().__init__(name, base_addr)
        self.heart_rate_bpm = 72
        self.cardiac_output_lpm = 5.0
        self.stroke_volume_ml = 70
        self.ejection_fraction = 0.60

    def simulate_tick(self):
        super().simulate_tick()
        self.heart_rate_bpm += random.gauss(0, 0.3)
        self.heart_rate_bpm = max(30, min(220, self.heart_rate_bpm))
        self.stroke_volume_ml += random.gauss(0, 0.2)
        self.stroke_volume_ml = max(20, min(130, self.stroke_volume_ml))
        self.cardiac_output_lpm = self.heart_rate_bpm * self.stroke_volume_ml / 1000.0

    def set_heart_rate(self, bpm):
        self.heart_rate_bpm = max(30, min(220, bpm))

    def read_reg(self, offset):
        if offset == 0x00: return int(self.heart_rate_bpm) & 0xFFFFFFFF
        if offset == 0x04: return int(self.cardiac_output_lpm * 1000) & 0xFFFFFFFF
        return 0


class LungModel(SensorBase):
    def __init__(self, name='lung0', base_addr=0x40120100):
        super().__init__(name, base_addr)
        self.respiratory_rate = 16
        self.tidal_volume_ml = 500
        self.spo2_percent = 98.0
        self.minute_ventilation = 8.0

    def simulate_tick(self):
        super().simulate_tick()
        self.respiratory_rate += random.gauss(0, 0.1)
        self.respiratory_rate = max(4, min(40, self.respiratory_rate))
        self.spo2_percent += random.gauss(0, 0.1)
        self.spo2_percent = max(60, min(100, self.spo2_percent))
        self.minute_ventilation = self.respiratory_rate * self.tidal_volume_ml / 1000.0

    def set_spo2(self, spo2):
        self.spo2_percent = max(60, min(100, spo2))

    def read_reg(self, offset):
        if offset == 0x00: return int(self.respiratory_rate) & 0xFFFFFFFF
        if offset == 0x04: return int(self.tidal_volume_ml) & 0xFFFFFFFF
        if offset == 0x08: return int(self.spo2_percent * 100) & 0xFFFFFFFF
        return 0


class BloodPressureSensor(SensorBase):
    def __init__(self, name='bp0', base_addr=0x40120200):
        super().__init__(name, base_addr)
        self.systolic_mmhg = 120.0
        self.diastolic_mmhg = 80.0
        self.mean_arterial_pressure = 93.3

    def simulate_tick(self):
        super().simulate_tick()
        self.systolic_mmhg += random.gauss(0, 0.5)
        self.systolic_mmhg = max(60, min(250, self.systolic_mmhg))
        self.diastolic_mmhg += random.gauss(0, 0.3)
        self.diastolic_mmhg = max(30, min(150, self.diastolic_mmhg))
        self.mean_arterial_pressure = self.diastolic_mmhg + (self.systolic_mmhg - self.diastolic_mmhg) / 3.0

    def set_pressure(self, systolic, diastolic):
        self.systolic_mmhg = systolic
        self.diastolic_mmhg = diastolic

    def read_reg(self, offset):
        if offset == 0x00: return int(self.systolic_mmhg * 100) & 0xFFFFFFFF
        if offset == 0x04: return int(self.diastolic_mmhg * 100) & 0xFFFFFFFF
        if offset == 0x08: return int(self.mean_arterial_pressure * 100) & 0xFFFFFFFF
        return 0
