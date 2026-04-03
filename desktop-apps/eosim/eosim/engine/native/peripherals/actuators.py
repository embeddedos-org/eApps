# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""Domain-specific actuator peripherals for EoSim simulation."""
import random


class ActuatorBase:
    """Base class for actuator peripherals with io_handler support."""

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


class MotorController(ActuatorBase):
    """DC/stepper/BLDC motor controller."""

    def __init__(self, name: str = 'motor0', base_addr: int = 0x40200000,
                 motor_type: str = 'dc'):
        super().__init__(name, base_addr)
        self.motor_type = motor_type
        self.speed_rpm = 0
        self.target_speed = 0
        self.position_deg = 0.0
        self.direction = 1
        self.current_ma = 0.0
        self.max_rpm = 5000

    def simulate_tick(self):
        if self.enabled:
            diff = self.target_speed - self.speed_rpm
            self.speed_rpm += int(diff * 0.1)
            self.position_deg += self.speed_rpm * self.direction * 0.006
            self.position_deg %= 360
            self.current_ma = abs(self.speed_rpm) * 0.5 + random.gauss(0, 5)
        else:
            self.speed_rpm = int(self.speed_rpm * 0.95)
            self.current_ma = max(0, self.current_ma - 10)

    def read_reg(self, offset: int) -> int:
        if offset == 0x00:
            return self.speed_rpm & 0xFFFFFFFF
        elif offset == 0x04:
            return int(self.position_deg * 100) & 0xFFFFFFFF
        elif offset == 0x08:
            return int(self.current_ma * 100) & 0xFFFFFFFF
        elif offset == 0x0C:
            return self.direction
        elif offset == 0x10:
            return int(self.enabled)
        return 0

    def write_reg(self, offset: int, val: int):
        if offset == 0x00:
            self.target_speed = min(val, self.max_rpm)
        elif offset == 0x0C:
            self.direction = 1 if val else -1
        elif offset == 0x10:
            self.enabled = bool(val & 1)


class ServoController(ActuatorBase):
    """Multi-channel servo controller (PWM-based)."""

    def __init__(self, name: str = 'servo0', base_addr: int = 0x40200100,
                 channels: int = 8):
        super().__init__(name, base_addr)
        self.channels = channels
        self.positions = [90.0] * channels
        self.targets = [90.0] * channels
        self.speed_limit = 60.0
        self.min_angle = 0.0
        self.max_angle = 180.0

    def simulate_tick(self):
        for i in range(self.channels):
            diff = self.targets[i] - self.positions[i]
            step = min(abs(diff), self.speed_limit * 0.01)
            if diff > 0:
                self.positions[i] += step
            elif diff < 0:
                self.positions[i] -= step

    def set_target(self, ch: int, angle: float):
        if 0 <= ch < self.channels:
            self.targets[ch] = max(self.min_angle, min(self.max_angle, angle))

    def read_reg(self, offset: int) -> int:
        ch = offset // 4
        if 0 <= ch < self.channels:
            return int(self.positions[ch] * 100) & 0xFFFFFFFF
        return 0

    def write_reg(self, offset: int, val: int):
        ch = offset // 8
        sub = offset % 8
        if 0 <= ch < self.channels:
            if sub == 0:
                self.targets[ch] = max(self.min_angle, min(self.max_angle, val / 100.0))


class ESCController(ActuatorBase):
    """Electronic Speed Controller for brushless motors (drone/multirotor)."""

    def __init__(self, name: str = 'esc0', base_addr: int = 0x40200200,
                 channels: int = 4):
        super().__init__(name, base_addr)
        self.channels = channels
        self.throttle = [0.0] * channels
        self.rpm = [0] * channels
        self.armed = False
        self.max_rpm = 12000

    def simulate_tick(self):
        for i in range(self.channels):
            if self.armed and self.enabled:
                target_rpm = int(self.throttle[i] / 100.0 * self.max_rpm)
                self.rpm[i] += int((target_rpm - self.rpm[i]) * 0.2)
            else:
                self.rpm[i] = int(self.rpm[i] * 0.9)

    def read_reg(self, offset: int) -> int:
        ch = offset // 8
        sub = offset % 8
        if 0 <= ch < self.channels:
            if sub == 0:
                return int(self.throttle[ch] * 100) & 0xFFFFFFFF
            elif sub == 4:
                return self.rpm[ch] & 0xFFFFFFFF
        elif offset == 0x30:
            return int(self.armed)
        return 0

    def write_reg(self, offset: int, val: int):
        ch = offset // 8
        sub = offset % 8
        if 0 <= ch < self.channels:
            if sub == 0:
                self.throttle[ch] = max(0, min(100, val / 100.0))
        elif offset == 0x30:
            self.armed = bool(val & 1)
        elif offset == 0x34:
            self.enabled = bool(val & 1)


class ValveController(ActuatorBase):
    """Valve controller (on/off or proportional)."""

    def __init__(self, name: str = 'valve0', base_addr: int = 0x40200300,
                 channels: int = 4):
        super().__init__(name, base_addr)
        self.channels = channels
        self.positions = [0.0] * channels
        self.types = ['on_off'] * channels

    def read_reg(self, offset: int) -> int:
        ch = offset // 4
        if 0 <= ch < self.channels:
            return int(self.positions[ch] * 100) & 0xFFFFFFFF
        return 0

    def write_reg(self, offset: int, val: int):
        ch = offset // 4
        if 0 <= ch < self.channels:
            if self.types[ch] == 'on_off':
                self.positions[ch] = 100.0 if val else 0.0
            else:
                self.positions[ch] = max(0, min(100, val / 100.0))


class PumpController(ActuatorBase):
    """Pump controller (infusion, hydraulic, etc.)."""

    def __init__(self, name: str = 'pump0', base_addr: int = 0x40200400):
        super().__init__(name, base_addr)
        self.flow_rate_ml_min = 0.0
        self.target_flow = 0.0
        self.pressure_kpa = 0.0
        self.total_delivered_ml = 0.0
        self.occlusion = False

    def simulate_tick(self):
        if self.enabled and not self.occlusion:
            diff = self.target_flow - self.flow_rate_ml_min
            self.flow_rate_ml_min += diff * 0.1
            self.total_delivered_ml += self.flow_rate_ml_min / 6000
            self.pressure_kpa = self.flow_rate_ml_min * 0.5
        elif self.occlusion:
            self.flow_rate_ml_min = 0
            self.pressure_kpa = 200.0

    def read_reg(self, offset: int) -> int:
        if offset == 0x00:
            return int(self.flow_rate_ml_min * 100) & 0xFFFFFFFF
        elif offset == 0x04:
            return int(self.pressure_kpa * 100) & 0xFFFFFFFF
        elif offset == 0x08:
            return int(self.total_delivered_ml * 100) & 0xFFFFFFFF
        elif offset == 0x0C:
            return int(self.occlusion)
        return 0

    def write_reg(self, offset: int, val: int):
        if offset == 0x00:
            self.target_flow = val / 100.0
        elif offset == 0x04:
            self.enabled = bool(val & 1)


class RelayBank(ActuatorBase):
    """Multi-channel relay controller."""

    def __init__(self, name: str = 'relay0', base_addr: int = 0x40200500,
                 channels: int = 8):
        super().__init__(name, base_addr)
        self.channels = channels
        self.states = [False] * channels
        self.cycle_counts = [0] * channels

    def read_reg(self, offset: int) -> int:
        if offset == 0x00:
            val = 0
            for i in range(self.channels):
                if self.states[i]:
                    val |= (1 << i)
            return val
        return 0

    def write_reg(self, offset: int, val: int):
        if offset == 0x00:
            for i in range(self.channels):
                new_state = bool(val & (1 << i))
                if new_state != self.states[i]:
                    self.cycle_counts[i] += 1
                self.states[i] = new_state


class DisplayDriver(ActuatorBase):
    """OLED/LCD display driver with framebuffer."""

    def __init__(self, name: str = 'disp0', base_addr: int = 0x40200600,
                 width: int = 128, height: int = 64):
        super().__init__(name, base_addr)
        self.width = width
        self.height = height
        self.framebuffer = bytearray(width * height // 8)
        self.contrast = 255
        self.cursor_x = 0
        self.cursor_y = 0

    def read_reg(self, offset: int) -> int:
        if offset == 0x00:
            return self.width
        elif offset == 0x04:
            return self.height
        elif offset == 0x08:
            return self.contrast
        elif offset == 0x0C:
            return int(self.enabled)
        return 0

    def write_reg(self, offset: int, val: int):
        if offset == 0x08:
            self.contrast = val & 0xFF
        elif offset == 0x0C:
            self.enabled = bool(val & 1)
        elif offset == 0x10:
            idx = val & 0xFFFF
            if idx < len(self.framebuffer):
                self.framebuffer[idx] = (val >> 16) & 0xFF


class HapticDriver(ActuatorBase):
    """Haptic feedback motor driver."""

    def __init__(self, name: str = 'haptic0', base_addr: int = 0x40200700):
        super().__init__(name, base_addr)
        self.intensity = 0
        self.pattern = 0
        self.duration_ms = 0
        self._remaining_ms = 0

    def simulate_tick(self):
        if self._remaining_ms > 0:
            self._remaining_ms -= 10
            if self._remaining_ms <= 0:
                self.intensity = 0

    def read_reg(self, offset: int) -> int:
        if offset == 0x00:
            return self.intensity
        elif offset == 0x04:
            return self._remaining_ms
        return 0

    def write_reg(self, offset: int, val: int):
        if offset == 0x00:
            self.intensity = val & 0xFF
        elif offset == 0x04:
            self.pattern = val & 0xFF
        elif offset == 0x08:
            self.duration_ms = val
            self._remaining_ms = val


class SteeringActuator(ActuatorBase):
    """Electric Power Steering actuator."""

    def __init__(self, name: str = 'steer0', base_addr: int = 0x40200800):
        super().__init__(name, base_addr)
        self.angle_deg = 0.0
        self.target_angle = 0.0
        self.torque_nm = 0.0
        self.eps_enabled = True
        self.max_angle = 540.0

    def simulate_tick(self):
        diff = self.target_angle - self.angle_deg
        step = min(abs(diff), 5.0)
        if diff > 0:
            self.angle_deg += step
        elif diff < 0:
            self.angle_deg -= step
        self.torque_nm = diff * 0.1

    def read_reg(self, offset: int) -> int:
        if offset == 0x00:
            return int(self.angle_deg * 100) & 0xFFFFFFFF
        elif offset == 0x04:
            return int(self.torque_nm * 100) & 0xFFFFFFFF
        return 0

    def write_reg(self, offset: int, val: int):
        if offset == 0x00:
            angle = val / 100.0
            self.target_angle = max(-self.max_angle, min(self.max_angle, angle))


class ThrottleActuator(ActuatorBase):
    """Throttle/accelerator actuator."""

    def __init__(self, name: str = 'throttle0', base_addr: int = 0x40200900):
        super().__init__(name, base_addr)
        self.position_pct = 0.0
        self.target_pct = 0.0
        self.mode = 'manual'

    def simulate_tick(self):
        diff = self.target_pct - self.position_pct
        self.position_pct += diff * 0.2

    def read_reg(self, offset: int) -> int:
        if offset == 0x00:
            return int(self.position_pct * 100) & 0xFFFFFFFF
        return 0

    def write_reg(self, offset: int, val: int):
        if offset == 0x00:
            self.target_pct = max(0, min(100, val / 100.0))
        elif offset == 0x04:
            self.mode = 'cruise' if val else 'manual'


class BrakeActuator(ActuatorBase):
    """Brake actuator with ABS support."""

    def __init__(self, name: str = 'brake0', base_addr: int = 0x40200A00):
        super().__init__(name, base_addr)
        self.pressure_pct = 0.0
        self.target_pct = 0.0
        self.abs_active = False
        self.channels = [0.0, 0.0, 0.0, 0.0]

    def simulate_tick(self):
        diff = self.target_pct - self.pressure_pct
        self.pressure_pct += diff * 0.3
        for i in range(4):
            self.channels[i] = self.pressure_pct

    def read_reg(self, offset: int) -> int:
        if offset == 0x00:
            return int(self.pressure_pct * 100) & 0xFFFFFFFF
        elif offset == 0x04:
            return int(self.abs_active)
        return 0

    def write_reg(self, offset: int, val: int):
        if offset == 0x00:
            self.target_pct = max(0, min(100, val / 100.0))
