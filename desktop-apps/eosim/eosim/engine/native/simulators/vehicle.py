# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""Vehicle / SDV simulator — software-defined vehicle (car/truck/EV/scooter).

Pure Python, cross-platform (Linux/Windows/macOS). No OS-specific dependencies.
"""
import math
import random
import struct


class VehicleSimulator:
    """Software-Defined Vehicle (SDV) / automotive simulator.

    Physics: speed, acceleration, braking, steering angle, wheel RPM.
    CAN message simulation: periodic ECU messages at correct intervals.
    Scenarios: highway cruise, city driving, emergency braking, lane change,
               parking, OTA update, cold start.
    """

    PRODUCT_TYPE = 'vehicle'
    DISPLAY_NAME = 'Vehicle / SDV'

    SCENARIOS = {
        'highway_cruise': {'target_speed_kmh': 110, 'steering': 0, 'description': 'Steady highway cruise at 110 km/h'},
        'city_driving': {'target_speed_kmh': 40, 'steering': 5, 'description': 'City driving with frequent stops'},
        'emergency_braking': {'target_speed_kmh': 0, 'brake_pct': 100, 'description': 'Full ABS braking from speed'},
        'lane_change': {'steering_sequence': [15, 0, -15, 0], 'description': 'Double lane change maneuver'},
        'parking': {'target_speed_kmh': 5, 'steering': 30, 'description': 'Low-speed parking maneuver'},
        'ota_update': {'target_speed_kmh': 0, 'description': 'Vehicle stationary during OTA update'},
        'cold_start': {'coolant_temp': -10, 'description': 'Engine cold start in winter'},
    }

    def __init__(self, vm):
        self.vm = vm
        self.tick_count = 0
        self.state = {}
        self.scenario = ''
        self._scenario_step = 0

    def setup(self):
        from eosim.engine.native.peripherals.sensors import IMUSensor, GPSModule, TemperatureSensor
        from eosim.engine.native.peripherals.actuators import (
            MotorController, SteeringActuator, ThrottleActuator, BrakeActuator)
        from eosim.engine.native.peripherals.buses import CANBusController, LINBusController
        from eosim.engine.native.peripherals.composites import BatteryManagement, WatchdogTimer

        self.vm.add_peripheral('imu0', IMUSensor('imu0', 0x40100200))
        self.vm.add_peripheral('gps0', GPSModule('gps0', 0x40100300))
        self.vm.add_peripheral('temp_coolant', TemperatureSensor('temp_coolant', 0x40100010, 0, 120))
        self.vm.add_peripheral('temp_ambient', TemperatureSensor('temp_ambient', 0x40100020, -40, 60))
        self.vm.add_peripheral('can0', CANBusController('can0', 0x40300000))
        self.vm.add_peripheral('lin0', LINBusController('lin0', 0x40300100))
        self.vm.add_peripheral('motor0', MotorController('motor0', 0x40200000))
        self.vm.add_peripheral('steering', SteeringActuator('steering', 0x40200800))
        self.vm.add_peripheral('throttle', ThrottleActuator('throttle', 0x40200900))
        self.vm.add_peripheral('brake', BrakeActuator('brake', 0x40200A00))
        self.vm.add_peripheral('bms0', BatteryManagement('bms0', 0x40500000, 96, 75000))
        self.vm.add_peripheral('wdt0', WatchdogTimer('wdt0', 0x40500200))

        self.state = {
            'speed_kmh': 0, 'rpm': 0, 'gear': 'P', 'steering_deg': 0,
            'throttle_pct': 0, 'brake_pct': 0, 'soc_pct': 85,
            'wheel_rpm': [0, 0, 0, 0], 'coolant_temp_c': 20,
            'odometer_km': 0, 'scenario': '',
        }

    def load_scenario(self, name: str):
        if name in self.SCENARIOS:
            self.scenario = name
            self._scenario_step = 0
            self.state['scenario'] = name
            cfg = self.SCENARIOS[name]
            if 'coolant_temp' in cfg:
                tc = self.vm.peripherals.get('temp_coolant')
                if tc:
                    tc.set_value(cfg['coolant_temp'])
                    self.state['coolant_temp_c'] = cfg['coolant_temp']

    def tick(self):
        self.tick_count += 1
        for name, dev in self.vm.peripherals.items():
            if hasattr(dev, 'simulate_tick'):
                dev.simulate_tick()

        throttle = self.vm.peripherals.get('throttle')
        brake = self.vm.peripherals.get('brake')
        motor = self.vm.peripherals.get('motor0')
        bms = self.vm.peripherals.get('bms0')
        gps = self.vm.peripherals.get('gps0')
        steering = self.vm.peripherals.get('steering')
        can = self.vm.peripherals.get('can0')
        imu = self.vm.peripherals.get('imu0')

        self._apply_scenario()

        accel = (throttle.position_pct if throttle else 0) * 0.5
        decel = (brake.pressure_pct if brake else 0) * 0.8
        drag = self.state['speed_kmh'] * 0.002
        speed = self.state.get('speed_kmh', 0)
        speed = max(0, speed + (accel - decel - drag) * 0.1)
        self.state['speed_kmh'] = round(speed, 1)
        self.state['rpm'] = int(speed * 50 + random.gauss(0, 20))
        self.state['throttle_pct'] = round(throttle.position_pct if throttle else 0, 1)
        self.state['brake_pct'] = round(brake.pressure_pct if brake else 0, 1)
        self.state['steering_deg'] = round(steering.angle_deg if steering else 0, 1)
        self.state['soc_pct'] = round(bms.soc_percent if bms else 0, 1)
        self.state['odometer_km'] += speed / 3600 * 0.01

        wheel_base_rpm = speed * 8.8
        for i in range(4):
            self.state['wheel_rpm'][i] = round(wheel_base_rpm + random.gauss(0, 2), 0)

        if speed < 1:
            self.state['gear'] = 'P'
        elif speed < 20:
            self.state['gear'] = '1'
        elif speed < 40:
            self.state['gear'] = '2'
        elif speed < 70:
            self.state['gear'] = '3'
        elif speed < 100:
            self.state['gear'] = '4'
        else:
            self.state['gear'] = '5'

        tc = self.vm.peripherals.get('temp_coolant')
        if tc:
            if speed > 0 and tc.temperature < 90:
                tc.temperature += 0.05
            self.state['coolant_temp_c'] = round(tc.temperature, 1)

        if gps:
            gps.speed_mps = speed / 3.6
            heading = steering.angle_deg * 0.1 if steering else 0
            gps.heading_deg = (gps.heading_deg + heading) % 360

        if imu:
            lat_g = math.sin(math.radians(steering.angle_deg * 0.1 if steering else 0)) * speed / 100
            imu.set_accel(accel * 0.01, lat_g, 9.81)

        if can:
            if self.tick_count % 1 == 0:
                can.inject_message(0x100, struct.pack('<HH', max(0, min(65535, int(speed * 100))), max(0, min(65535, self.state['rpm']))))
            if self.tick_count % 2 == 0:
                can.inject_message(0x200, struct.pack('<hH',
                    int(steering.angle_deg * 10 if steering else 0), 0))
            if self.tick_count % 5 == 0:
                can.inject_message(0x300, struct.pack('<HHHH',
                    *[max(0, min(65535, int(w))) for w in self.state['wheel_rpm']]))
            if self.tick_count % 10 == 0:
                can.inject_message(0x600, struct.pack('<HBB',
                    int(bms.soc_percent * 100 if bms else 0),
                    int(self.state['coolant_temp_c'] + 40), 0))

        if bms:
            bms.current_ma = speed * 100 + random.gauss(0, 50)

    def _apply_scenario(self):
        if not self.scenario:
            return
        cfg = self.SCENARIOS.get(self.scenario, {})
        throttle = self.vm.peripherals.get('throttle')
        brake = self.vm.peripherals.get('brake')
        steering = self.vm.peripherals.get('steering')

        if self.scenario == 'highway_cruise':
            if throttle:
                error = cfg['target_speed_kmh'] - self.state['speed_kmh']
                throttle.target_pct = max(0, min(100, 50 + error * 2))

        elif self.scenario == 'city_driving':
            cycle = self.tick_count % 200
            if cycle < 80:
                if throttle:
                    throttle.target_pct = 30
                if brake:
                    brake.target_pct = 0
            elif cycle < 120:
                if throttle:
                    throttle.target_pct = 0
                if brake:
                    brake.target_pct = 60
            else:
                if throttle:
                    throttle.target_pct = 0
                if brake:
                    brake.target_pct = 0

        elif self.scenario == 'emergency_braking':
            if throttle:
                throttle.target_pct = 0
            if brake:
                brake.target_pct = 100
                if self.state['speed_kmh'] > 10:
                    brake.abs_active = True
                else:
                    brake.abs_active = False

        elif self.scenario == 'lane_change':
            seq = cfg['steering_sequence']
            phase = (self.tick_count // 30) % len(seq)
            if steering:
                steering.target_angle = seq[phase]

        elif self.scenario == 'parking':
            if throttle:
                throttle.target_pct = 5
            if steering:
                steering.target_angle = cfg.get('steering', 30)

        elif self.scenario == 'ota_update':
            if throttle:
                throttle.target_pct = 0
            if brake:
                brake.target_pct = 0

        self._scenario_step += 1

    def get_state(self) -> dict:
        return dict(self.state)

    def get_peripherals(self) -> dict:
        return dict(self.vm.peripherals)

    def get_status_text(self) -> str:
        scn = f" [{self.scenario}]" if self.scenario else ""
        return f"{self.DISPLAY_NAME} | Tick {self.tick_count}{scn}"

    def reset(self):
        self.tick_count = 0
        self.state = {}
        self.scenario = ''
        self._scenario_step = 0
