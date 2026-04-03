# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
import random
from eosim.engine.native.peripherals.actuators import ActuatorBase


class AeroActuator(ActuatorBase):
    def __init__(self, name='aero_act0', base_addr=0x40210000):
        super().__init__(name, base_addr)
        self.flap_angle_deg = 0.0
        self.target_flap_deg = 0.0
        self.slat_position_pct = 0.0
        self.aileron_deg = 0.0
        self.target_aileron_deg = 0.0
    def simulate_tick(self):
        self.flap_angle_deg += (self.target_flap_deg - self.flap_angle_deg) * 0.15
        self.aileron_deg += (self.target_aileron_deg - self.aileron_deg) * 0.2
    def read_reg(self, offset):
        if offset == 0x00: return int(self.flap_angle_deg * 100) & 0xFFFFFFFF
        return 0
    def write_reg(self, offset, val):
        if offset == 0x00: self.target_flap_deg = max(-45, min(45, val / 100.0))


class TunnelFanController(ActuatorBase):
    def __init__(self, name='fan0', base_addr=0x40210100):
        super().__init__(name, base_addr)
        self.fan_speed_rpm = 0
        self.target_speed_rpm = 0
        self.flow_velocity_mps = 0.0
        self.power_kw = 0.0
    def simulate_tick(self):
        self.fan_speed_rpm += int((self.target_speed_rpm - self.fan_speed_rpm) * 0.08)
        self.flow_velocity_mps = self.fan_speed_rpm * 0.01
    def read_reg(self, offset):
        if offset == 0x00: return self.fan_speed_rpm & 0xFFFFFFFF
        return 0
    def write_reg(self, offset, val):
        if offset == 0x00: self.target_speed_rpm = max(0, min(20000, val))
