# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
import random
from eosim.engine.native.peripherals.actuators import ActuatorBase


class VentilatorActuator(ActuatorBase):
    def __init__(self, name='vent0', base_addr=0x40220000):
        super().__init__(name, base_addr)
        self.tidal_volume_ml = 500
        self.target_volume_ml = 500
        self.respiratory_rate = 16
        self.peep_cmh2o = 5.0
        self.fio2_pct = 21.0
    def simulate_tick(self):
        self.tidal_volume_ml += (self.target_volume_ml - self.tidal_volume_ml) * 0.1
    def read_reg(self, offset):
        if offset == 0x00: return int(self.tidal_volume_ml) & 0xFFFFFFFF
        return 0
    def write_reg(self, offset, val):
        if offset == 0x00: self.target_volume_ml = max(100, min(1200, val))


class InfusionPump(ActuatorBase):
    def __init__(self, name='infusion0', base_addr=0x40220100):
        super().__init__(name, base_addr)
        self.flow_rate_ml_hr = 0.0
        self.target_rate_ml_hr = 0.0
        self.total_delivered_ml = 0.0
        self.occlusion = False
    def simulate_tick(self):
        if self.enabled and not self.occlusion:
            self.flow_rate_ml_hr += (self.target_rate_ml_hr - self.flow_rate_ml_hr) * 0.15
    def read_reg(self, offset):
        if offset == 0x00: return int(self.flow_rate_ml_hr * 100) & 0xFFFFFFFF
        return 0


class SurgicalTool(ActuatorBase):
    def __init__(self, name='surgical0', base_addr=0x40220200):
        super().__init__(name, base_addr)
        self.position = [0.0, 0.0, 0.0]
        self.target_position = [0.0, 0.0, 0.0]
        self.force_feedback_n = 0.0
        self.tool_active = False
    def simulate_tick(self):
        if self.tool_active:
            for i in range(3):
                self.position[i] += (self.target_position[i] - self.position[i]) * 0.2
    def read_reg(self, offset):
        idx = offset // 4
        if idx < 3: return int(self.position[idx] * 1000) & 0xFFFFFFFF
        return 0
