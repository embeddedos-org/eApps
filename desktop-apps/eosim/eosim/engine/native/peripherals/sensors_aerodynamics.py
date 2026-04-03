# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""Aerodynamics domain sensors — wind tunnel, airflow, pitot tube, force balance."""
import math
import random

from eosim.engine.native.peripherals.sensors import SensorBase


class WindTunnelSensor(SensorBase):
    def __init__(self, name='wind_tunnel0', base_addr=0x40110000):
        super().__init__(name, base_addr)
        self.airspeed_mps = 0.0
        self.mach_number = 0.0
        self.dynamic_pressure_pa = 0.0
        self.temperature_k = 288.15
        self.tunnel_active = False

    def simulate_tick(self):
        super().simulate_tick()
        if self.tunnel_active:
            self.airspeed_mps += random.gauss(0, 0.05)
            self.airspeed_mps = max(0, self.airspeed_mps)
            speed_of_sound = 20.05 * math.sqrt(self.temperature_k)
            self.mach_number = self.airspeed_mps / speed_of_sound if speed_of_sound > 0 else 0
            rho = 1.225 * (self.temperature_k / 288.15)
            self.dynamic_pressure_pa = 0.5 * rho * self.airspeed_mps ** 2

    def set_airspeed(self, mps):
        self.airspeed_mps = max(0, mps)
        self.tunnel_active = True

    def read_reg(self, offset):
        if offset == 0x00: return int(self.airspeed_mps * 1000) & 0xFFFFFFFF
        if offset == 0x04: return int(self.mach_number * 10000) & 0xFFFFFFFF
        if offset == 0x08: return int(self.dynamic_pressure_pa * 100) & 0xFFFFFFFF
        return 0


class AirflowSensor(SensorBase):
    def __init__(self, name='airflow0', base_addr=0x40110100):
        super().__init__(name, base_addr)
        self.velocity = [0.0, 0.0, 0.0]
        self.turbulence_intensity = 0.0
        self.reynolds_number = 0.0

    def simulate_tick(self):
        super().simulate_tick()
        for i in range(3):
            self.velocity[i] += random.gauss(0, 0.02)
        speed = math.sqrt(sum(v * v for v in self.velocity))
        self.turbulence_intensity = abs(random.gauss(0, 0.05))
        self.reynolds_number = speed * 1.0 / 1.46e-5

    def set_velocity(self, vx, vy, vz):
        self.velocity = [vx, vy, vz]

    def read_reg(self, offset):
        idx = offset // 4
        if idx < 3: return int(self.velocity[idx] * 1000) & 0xFFFFFFFF
        if idx == 3: return int(self.turbulence_intensity * 10000) & 0xFFFFFFFF
        return 0


class PitotTube(SensorBase):
    def __init__(self, name='pitot0', base_addr=0x40110200):
        super().__init__(name, base_addr)
        self.total_pressure_pa = 101325.0
        self.static_pressure_pa = 101325.0
        self.indicated_airspeed_mps = 0.0

    def simulate_tick(self):
        super().simulate_tick()
        self.total_pressure_pa += random.gauss(0, 1.0)
        self.static_pressure_pa += random.gauss(0, 0.5)
        dp = max(0, self.total_pressure_pa - self.static_pressure_pa)
        self.indicated_airspeed_mps = math.sqrt(2 * dp / 1.225) if dp > 0 else 0

    def set_pressures(self, total_pa, static_pa):
        self.total_pressure_pa = total_pa
        self.static_pressure_pa = static_pa

    def read_reg(self, offset):
        if offset == 0x00: return int(self.total_pressure_pa * 100) & 0xFFFFFFFF
        if offset == 0x04: return int(self.static_pressure_pa * 100) & 0xFFFFFFFF
        if offset == 0x08: return int(self.indicated_airspeed_mps * 1000) & 0xFFFFFFFF
        return 0


class ForceBalance(SensorBase):
    def __init__(self, name='balance0', base_addr=0x40110300):
        super().__init__(name, base_addr)
        self.lift_n = 0.0
        self.drag_n = 0.0
        self.side_force_n = 0.0

    def simulate_tick(self):
        super().simulate_tick()
        self.lift_n += random.gauss(0, 0.1)
        self.drag_n += random.gauss(0, 0.05)

    def set_forces(self, lift, drag, side=0.0):
        self.lift_n = lift
        self.drag_n = drag
        self.side_force_n = side

    def read_reg(self, offset):
        if offset == 0x00: return int(self.lift_n * 1000) & 0xFFFFFFFF
        if offset == 0x04: return int(self.drag_n * 1000) & 0xFFFFFFFF
        if offset == 0x08: return int(self.side_force_n * 1000) & 0xFFFFFFFF
        return 0
