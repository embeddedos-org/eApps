# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""Weather domain actuators — weather modification actuator."""
import random

from eosim.engine.native.peripherals.actuators import ActuatorBase


class WeatherActuator(ActuatorBase):
    """Weather control actuator — seeding, heating, pressure injection."""

    def __init__(self, name: str = 'wx_act0', base_addr: int = 0x40240000):
        super().__init__(name, base_addr)
        self.seed_rate_g_hr = 0.0
        self.target_seed_rate = 0.0
        self.heater_power_kw = 0.0
        self.pressure_injection_pa = 0.0
        self.mode = 'idle'

    def simulate_tick(self):
        diff = self.target_seed_rate - self.seed_rate_g_hr
        self.seed_rate_g_hr += diff * 0.1

    def read_reg(self, offset: int) -> int:
        if offset == 0x00:
            return int(self.seed_rate_g_hr * 100) & 0xFFFFFFFF
        elif offset == 0x04:
            return int(self.heater_power_kw * 100) & 0xFFFFFFFF
        elif offset == 0x08:
            return int(self.pressure_injection_pa * 100) & 0xFFFFFFFF
        return 0

    def write_reg(self, offset: int, val: int):
        if offset == 0x00:
            self.target_seed_rate = max(0, val / 100.0)
        elif offset == 0x04:
            self.heater_power_kw = max(0, val / 100.0)
        elif offset == 0x08:
            self.pressure_injection_pa = val / 100.0
