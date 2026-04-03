# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""Composite / domain-specific peripherals for EoSim simulation."""
import random
import time


class CompositeBase:
    """Base class for composite peripherals."""

    def __init__(self, name: str, base_addr: int):
        self.name = name
        self.base = base_addr
        self.enabled = False

    def simulate_tick(self):
        pass

    def io_handler(self, op: str, addr: int, val: int) -> int:
        offset = addr - self.base
        if 'read' in op:
            return self.read_reg(offset)
        else:
            self.write_reg(offset, val)
            return 0

    def read_reg(self, offset: int) -> int:
        return 0

    def write_reg(self, offset: int, val: int):
        pass


class BatteryManagement(CompositeBase):
    """Battery management system (BMS)."""

    def __init__(self, name: str = 'bms0', base_addr: int = 0x40500000,
                 cell_count: int = 4, capacity_mah: int = 5000):
        super().__init__(name, base_addr)
        self.cell_count = cell_count
        self.capacity_mah = capacity_mah
        self.voltage_mv = 3700 * cell_count
        self.current_ma = 0.0
        self.soc_percent = 85.0
        self.temperature_c = 25.0
        self.charging = False
        self.health_percent = 100
        self.cell_voltages = [3700] * cell_count
        self.low_voltage_alarm = False
        self.over_temp_alarm = False

    def simulate_tick(self):
        if self.current_ma > 0 and not self.charging:
            self.soc_percent -= self.current_ma / self.capacity_mah * 0.001
        elif self.charging and self.soc_percent < 100:
            self.soc_percent += 0.01
        self.soc_percent = max(0, min(100, self.soc_percent))
        self.voltage_mv = int(3000 + (self.soc_percent / 100.0) * 1200) * self.cell_count
        self.temperature_c += random.gauss(0, 0.1)
        self.temperature_c = max(-10, min(60, self.temperature_c))
        self.low_voltage_alarm = self.soc_percent < 15
        self.over_temp_alarm = self.temperature_c > 50
        for i in range(self.cell_count):
            self.cell_voltages[i] = self.voltage_mv // self.cell_count + random.randint(-20, 20)

    def read_reg(self, offset: int) -> int:
        if offset == 0x00:
            return self.voltage_mv
        elif offset == 0x04:
            return int(self.current_ma * 100) & 0xFFFFFFFF
        elif offset == 0x08:
            return int(self.soc_percent * 100) & 0xFFFFFFFF
        elif offset == 0x0C:
            return int(self.temperature_c * 100) & 0xFFFFFFFF
        elif offset == 0x10:
            return int(self.charging)
        elif offset == 0x14:
            return (int(self.low_voltage_alarm) | (int(self.over_temp_alarm) << 1))
        return 0

    def write_reg(self, offset: int, val: int):
        if offset == 0x10:
            self.charging = bool(val & 1)
        elif offset == 0x04:
            self.current_ma = val / 100.0


class PowerSupply(CompositeBase):
    """Multi-rail power supply."""

    def __init__(self, name: str = 'psu0', base_addr: int = 0x40500100):
        super().__init__(name, base_addr)
        self.input_voltage_mv = 12000
        self.rails = {'3v3': 3300, '5v': 5000, '1v8': 1800}
        self.efficiency_pct = 92.0
        self.load_pct = 0.0
        self.power_good = True

    def read_reg(self, offset: int) -> int:
        if offset == 0x00:
            return self.input_voltage_mv
        elif offset == 0x04:
            return int(self.efficiency_pct * 100) & 0xFFFFFFFF
        elif offset == 0x08:
            return int(self.power_good)
        return 0


class WatchdogTimer(CompositeBase):
    """Hardware watchdog timer for safety-critical systems."""

    def __init__(self, name: str = 'wdt0', base_addr: int = 0x40500200,
                 timeout_ms: int = 1000):
        super().__init__(name, base_addr)
        self.timeout_ms = timeout_ms
        self.counter = timeout_ms
        self.reset_triggered = False
        self.reset_count = 0
        self.window_mode = False
        self.window_start_ms = 250

    def simulate_tick(self):
        if self.enabled:
            self.counter -= 10
            if self.counter <= 0:
                self.reset_triggered = True
                self.reset_count += 1
                self.counter = self.timeout_ms

    def kick(self):
        if self.window_mode and self.counter > (self.timeout_ms - self.window_start_ms):
            self.reset_triggered = True
            self.reset_count += 1
        else:
            self.counter = self.timeout_ms
            self.reset_triggered = False

    def read_reg(self, offset: int) -> int:
        if offset == 0x00:
            return self.counter
        elif offset == 0x04:
            return self.timeout_ms
        elif offset == 0x08:
            return int(self.reset_triggered)
        elif offset == 0x0C:
            return self.reset_count
        return 0

    def write_reg(self, offset: int, val: int):
        if offset == 0x00:
            self.kick()
        elif offset == 0x04:
            self.timeout_ms = max(100, val)
            self.counter = self.timeout_ms
        elif offset == 0x08:
            self.enabled = bool(val & 1)


class CryptoEngine(CompositeBase):
    """Hardware cryptographic engine."""

    def __init__(self, name: str = 'crypto0', base_addr: int = 0x40500300):
        super().__init__(name, base_addr)
        self.algorithm = 'AES-256'
        self.key_size = 256
        self.busy = False
        self.operations_done = 0
        self.hash_ready = False
        self.hash_value = 0

    def encrypt(self, data: bytes) -> bytes:
        self.busy = True
        self.operations_done += 1
        result = bytes([b ^ 0xA5 for b in data])
        self.busy = False
        return result

    def decrypt(self, data: bytes) -> bytes:
        self.busy = True
        self.operations_done += 1
        result = bytes([b ^ 0xA5 for b in data])
        self.busy = False
        return result

    def compute_hash(self, data: bytes):
        self.hash_value = hash(data) & 0xFFFFFFFF
        self.hash_ready = True
        self.operations_done += 1

    def read_reg(self, offset: int) -> int:
        if offset == 0x00:
            return int(self.busy) | (int(self.hash_ready) << 1)
        elif offset == 0x04:
            return self.operations_done
        elif offset == 0x08:
            return self.hash_value
        elif offset == 0x0C:
            return self.key_size
        return 0


class RTCModule(CompositeBase):
    """Real-time clock module."""

    def __init__(self, name: str = 'rtc0', base_addr: int = 0x40500400):
        super().__init__(name, base_addr)
        self.unix_time = int(time.time())
        self.alarm_time = 0
        self.alarm_enabled = False
        self.alarm_triggered = False
        self.calibration = 0
        self.battery_ok = True

    def simulate_tick(self):
        if self.enabled:
            self.unix_time += 1
            if self.alarm_enabled and self.unix_time >= self.alarm_time:
                self.alarm_triggered = True

    def read_reg(self, offset: int) -> int:
        if offset == 0x00:
            return self.unix_time & 0xFFFFFFFF
        elif offset == 0x04:
            return self.alarm_time & 0xFFFFFFFF
        elif offset == 0x08:
            return (int(self.alarm_enabled) |
                    (int(self.alarm_triggered) << 1) |
                    (int(self.battery_ok) << 2))
        return 0

    def write_reg(self, offset: int, val: int):
        if offset == 0x00:
            self.unix_time = val
        elif offset == 0x04:
            self.alarm_time = val
        elif offset == 0x08:
            self.alarm_enabled = bool(val & 1)
            if val & 2:
                self.alarm_triggered = False
            self.enabled = bool(val & 4)
