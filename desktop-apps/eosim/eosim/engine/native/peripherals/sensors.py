# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""Domain-specific sensor peripherals for EoSim simulation."""
import math
import random


class SensorBase:
    """Base class for all sensor peripherals with io_handler support."""

    def __init__(self, name: str, base_addr: int):
        self.name = name
        self.base = base_addr
        self.enabled = False
        self.sample_rate_hz = 100
        self._tick_count = 0

    def simulate_tick(self):
        self._tick_count += 1

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


class TemperatureSensor(SensorBase):
    """Temperature/humidity sensor (e.g., BME280, SHT31)."""

    def __init__(self, name: str = 'temp0', base_addr: int = 0x40100000,
                 min_c: float = -40, max_c: float = 125):
        super().__init__(name, base_addr)
        self.temperature = 22.0
        self.humidity = 45.0
        self.min_c = min_c
        self.max_c = max_c
        self._drift = 0.0

    def simulate_tick(self):
        super().simulate_tick()
        self._drift += random.gauss(0, 0.01)
        self._drift *= 0.99
        self.temperature = max(self.min_c, min(self.max_c, self.temperature + self._drift))
        self.humidity = max(0, min(100, self.humidity + random.gauss(0, 0.05)))

    def set_value(self, temp: float, humidity: float = -1):
        self.temperature = temp
        if humidity >= 0:
            self.humidity = humidity

    def read_reg(self, offset: int) -> int:
        if offset == 0x00:
            return int(self.temperature * 100) & 0xFFFFFFFF
        elif offset == 0x04:
            return int(self.humidity * 100) & 0xFFFFFFFF
        elif offset == 0x08:
            return int(self.enabled)
        return 0

    def write_reg(self, offset: int, val: int):
        if offset == 0x08:
            self.enabled = bool(val & 1)


class PressureSensor(SensorBase):
    """Barometric/hydraulic pressure sensor."""

    def __init__(self, name: str = 'baro0', base_addr: int = 0x40100100,
                 range_kpa: float = 110.0):
        super().__init__(name, base_addr)
        self.pressure_kpa = 101.325
        self.altitude_m = 0.0
        self.range_kpa = range_kpa

    def simulate_tick(self):
        super().simulate_tick()
        self.pressure_kpa += random.gauss(0, 0.005)
        self.altitude_m = 44330 * (1 - (self.pressure_kpa / 101.325) ** 0.1903)

    def set_value(self, pressure_kpa: float):
        self.pressure_kpa = pressure_kpa
        self.altitude_m = 44330 * (1 - (pressure_kpa / 101.325) ** 0.1903)

    def set_altitude(self, alt_m: float):
        self.altitude_m = alt_m
        self.pressure_kpa = 101.325 * (1 - alt_m / 44330) ** 5.255

    def read_reg(self, offset: int) -> int:
        if offset == 0x00:
            return int(self.pressure_kpa * 1000) & 0xFFFFFFFF
        elif offset == 0x04:
            return int(self.altitude_m * 100) & 0xFFFFFFFF
        return 0


class IMUSensor(SensorBase):
    """Inertial Measurement Unit — accelerometer + gyroscope + magnetometer."""

    def __init__(self, name: str = 'imu0', base_addr: int = 0x40100200, axes: int = 9):
        super().__init__(name, base_addr)
        self.axes = axes
        self.accel = [0.0, 0.0, 9.81]
        self.gyro = [0.0, 0.0, 0.0]
        self.mag = [0.25, 0.0, 0.45]

    def simulate_tick(self):
        super().simulate_tick()
        for i in range(3):
            self.accel[i] += random.gauss(0, 0.02)
            self.gyro[i] += random.gauss(0, 0.1)
            self.gyro[i] *= 0.98

    def set_accel(self, x: float, y: float, z: float):
        self.accel = [x, y, z]

    def set_gyro(self, x: float, y: float, z: float):
        self.gyro = [x, y, z]

    def set_mag(self, x: float, y: float, z: float):
        self.mag = [x, y, z]

    def read_reg(self, offset: int) -> int:
        idx = offset // 4
        if idx < 3:
            return int(self.accel[idx] * 1000) & 0xFFFFFFFF
        elif idx < 6:
            return int(self.gyro[idx - 3] * 1000) & 0xFFFFFFFF
        elif idx < 9:
            return int(self.mag[idx - 6] * 1000) & 0xFFFFFFFF
        return 0


class GPSModule(SensorBase):
    """GPS/GNSS receiver module."""

    def __init__(self, name: str = 'gps0', base_addr: int = 0x40100300):
        super().__init__(name, base_addr)
        self.latitude = 37.3861
        self.longitude = -122.0839
        self.altitude = 10.0
        self.speed_mps = 0.0
        self.heading_deg = 0.0
        self.satellites = 8
        self.fix = True
        self.hdop = 1.2

    def simulate_tick(self):
        super().simulate_tick()
        if self.speed_mps > 0:
            dlat = self.speed_mps * math.cos(math.radians(self.heading_deg)) / 111320
            dlon = self.speed_mps * math.sin(math.radians(self.heading_deg)) / (
                111320 * math.cos(math.radians(self.latitude)))
            self.latitude += dlat * 0.01
            self.longitude += dlon * 0.01
        self.latitude += random.gauss(0, 0.000001)
        self.longitude += random.gauss(0, 0.000001)

    def set_position(self, lat: float, lon: float, alt: float = 0):
        self.latitude = lat
        self.longitude = lon
        self.altitude = alt

    def read_reg(self, offset: int) -> int:
        if offset == 0x00:
            return int(self.latitude * 1e7) & 0xFFFFFFFF
        elif offset == 0x04:
            return int(self.longitude * 1e7) & 0xFFFFFFFF
        elif offset == 0x08:
            return int(self.altitude * 100) & 0xFFFFFFFF
        elif offset == 0x0C:
            return int(self.speed_mps * 100) & 0xFFFFFFFF
        elif offset == 0x10:
            return int(self.heading_deg * 100) & 0xFFFFFFFF
        elif offset == 0x14:
            return self.satellites
        elif offset == 0x18:
            return int(self.fix)
        return 0


class ProximitySensor(SensorBase):
    """Proximity/distance sensor (ultrasonic, IR, or LiDAR)."""

    def __init__(self, name: str = 'prox0', base_addr: int = 0x40100400,
                 max_range_cm: int = 400):
        super().__init__(name, base_addr)
        self.distance_cm = max_range_cm
        self.max_range_cm = max_range_cm
        self.detected = False
        self.sensor_type = 'ultrasonic'

    def simulate_tick(self):
        super().simulate_tick()
        self.distance_cm += random.gauss(0, 0.5)
        self.distance_cm = max(2, min(self.max_range_cm, self.distance_cm))
        self.detected = self.distance_cm < self.max_range_cm * 0.8

    def set_value(self, distance_cm: float):
        self.distance_cm = distance_cm
        self.detected = distance_cm < self.max_range_cm * 0.8

    def read_reg(self, offset: int) -> int:
        if offset == 0x00:
            return int(self.distance_cm * 10) & 0xFFFFFFFF
        elif offset == 0x04:
            return int(self.detected)
        return 0


class LightSensor(SensorBase):
    """Ambient light sensor (lux + IR)."""

    def __init__(self, name: str = 'light0', base_addr: int = 0x40100500):
        super().__init__(name, base_addr)
        self.lux = 500.0
        self.ir_level = 100.0

    def simulate_tick(self):
        super().simulate_tick()
        self.lux += random.gauss(0, 2)
        self.lux = max(0, self.lux)

    def set_value(self, lux: float):
        self.lux = lux

    def read_reg(self, offset: int) -> int:
        if offset == 0x00:
            return int(self.lux * 100) & 0xFFFFFFFF
        elif offset == 0x04:
            return int(self.ir_level * 100) & 0xFFFFFFFF
        return 0


class ADCChannel(SensorBase):
    """Multi-channel analog-to-digital converter."""

    def __init__(self, name: str = 'adc0', base_addr: int = 0x40100600,
                 channels: int = 8, resolution: int = 12):
        super().__init__(name, base_addr)
        self.channels = channels
        self.resolution = resolution
        self.values = [0] * channels
        self.reference_mv = 3300
        self.max_val = (1 << resolution) - 1

    def set_channel(self, ch: int, raw_value: int):
        if 0 <= ch < self.channels:
            self.values[ch] = max(0, min(self.max_val, raw_value))

    def set_voltage(self, ch: int, mv: float):
        if 0 <= ch < self.channels:
            self.values[ch] = int(mv / self.reference_mv * self.max_val)

    def read_reg(self, offset: int) -> int:
        ch = offset // 4
        if 0 <= ch < self.channels:
            return self.values[ch]
        return 0


class CurrentSensor(SensorBase):
    """Current/voltage/power measurement sensor (e.g., INA219)."""

    def __init__(self, name: str = 'ina0', base_addr: int = 0x40100700):
        super().__init__(name, base_addr)
        self.current_ma = 0.0
        self.voltage_mv = 3300.0
        self.power_mw = 0.0
        self.shunt_uv = 0

    def simulate_tick(self):
        super().simulate_tick()
        self.power_mw = self.current_ma * self.voltage_mv / 1000.0
        self.current_ma += random.gauss(0, 0.5)
        self.current_ma = max(0, self.current_ma)

    def set_value(self, current_ma: float, voltage_mv: float):
        self.current_ma = current_ma
        self.voltage_mv = voltage_mv
        self.power_mw = current_ma * voltage_mv / 1000.0

    def read_reg(self, offset: int) -> int:
        if offset == 0x00:
            return int(self.current_ma * 100) & 0xFFFFFFFF
        elif offset == 0x04:
            return int(self.voltage_mv) & 0xFFFFFFFF
        elif offset == 0x08:
            return int(self.power_mw * 100) & 0xFFFFFFFF
        return 0


class ECGSensor(SensorBase):
    """Electrocardiogram sensor for medical devices."""

    def __init__(self, name: str = 'ecg0', base_addr: int = 0x40100800):
        super().__init__(name, base_addr)
        self.heart_rate_bpm = 72
        self.waveform = [0.0] * 256
        self.leads = 3
        self.signal_quality = 95
        self._phase = 0.0

    def simulate_tick(self):
        super().simulate_tick()
        freq = self.heart_rate_bpm / 60.0
        self._phase += freq * 0.01
        if self._phase > 1.0:
            self._phase -= 1.0
        p = self._phase
        if p < 0.1:
            val = 0.1 * math.sin(p / 0.1 * math.pi)
        elif p < 0.15:
            val = 0.0
        elif p < 0.2:
            val = -0.1 * math.sin((p - 0.15) / 0.05 * math.pi)
        elif p < 0.25:
            val = 1.0 * math.sin((p - 0.2) / 0.05 * math.pi)
        elif p < 0.3:
            val = -0.2 * math.sin((p - 0.25) / 0.05 * math.pi)
        elif p < 0.5:
            val = 0.15 * math.sin((p - 0.3) / 0.2 * math.pi)
        else:
            val = 0.0
        val += random.gauss(0, 0.01)
        self.waveform.pop(0)
        self.waveform.append(val)

    def set_heart_rate(self, bpm: int):
        self.heart_rate_bpm = max(30, min(250, bpm))

    def read_reg(self, offset: int) -> int:
        if offset == 0x00:
            return self.heart_rate_bpm
        elif offset == 0x04:
            return int(self.waveform[-1] * 1000) & 0xFFFFFFFF
        elif offset == 0x08:
            return self.signal_quality
        elif offset == 0x0C:
            return self.leads
        return 0


class PulseOximeter(SensorBase):
    """SpO2 / pulse oximeter sensor."""

    def __init__(self, name: str = 'spo2_0', base_addr: int = 0x40100900):
        super().__init__(name, base_addr)
        self.spo2_percent = 98.0
        self.pulse_rate = 72
        self.signal_quality = 90
        self.perfusion_index = 5.0

    def simulate_tick(self):
        super().simulate_tick()
        self.spo2_percent += random.gauss(0, 0.1)
        self.spo2_percent = max(70, min(100, self.spo2_percent))
        self.pulse_rate += random.gauss(0, 0.3)
        self.pulse_rate = max(40, min(200, int(self.pulse_rate)))

    def set_value(self, spo2: float, pulse: int = -1):
        self.spo2_percent = spo2
        if pulse > 0:
            self.pulse_rate = pulse

    def read_reg(self, offset: int) -> int:
        if offset == 0x00:
            return int(self.spo2_percent * 100) & 0xFFFFFFFF
        elif offset == 0x04:
            return self.pulse_rate
        elif offset == 0x08:
            return self.signal_quality
        return 0
