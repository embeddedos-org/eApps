# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""Wearable device simulator. Pure Python, cross-platform."""
import math
import random


class WearableSimulator:
    PRODUCT_TYPE = 'wearable'
    DISPLAY_NAME = 'Wearable Device'

    SCENARIOS = {
        'step_counting': {'steps_per_min': 120, 'description': 'Walking step detection'},
        'heart_rate_monitor': {'description': 'Continuous HR monitoring'},
        'sleep_tracking': {'description': 'Sleep stage detection (light/deep/REM)'},
        'notification': {'description': 'Phone notification with haptic alert'},
        'workout_detection': {'type': 'running', 'description': 'Auto-detect running workout'},
    }

    def __init__(self, vm):
        self.vm = vm
        self.tick_count = 0
        self.state = {}
        self.scenario = ''
        self._scenario_step = 0
        self._step_acc = 0.0

    def setup(self):
        from eosim.engine.native.peripherals.sensors import IMUSensor, PulseOximeter, TemperatureSensor
        from eosim.engine.native.peripherals.actuators import DisplayDriver, HapticDriver
        from eosim.engine.native.peripherals.wireless import BLEModule
        from eosim.engine.native.peripherals.composites import BatteryManagement

        self.vm.add_peripheral('imu0', IMUSensor('imu0', 0x40100200))
        self.vm.add_peripheral('spo2_0', PulseOximeter('spo2_0', 0x40100900))
        self.vm.add_peripheral('temp0', TemperatureSensor('temp0', 0x40100000, 20, 42))
        self.vm.add_peripheral('display0', DisplayDriver('display0', 0x40200600, 240, 240))
        self.vm.add_peripheral('haptic0', HapticDriver('haptic0', 0x40200700))
        self.vm.add_peripheral('ble0', BLEModule('ble0', 0x40400100))
        self.vm.add_peripheral('bms0', BatteryManagement('bms0', 0x40500000, 1, 300))

        self.state = {
            'heart_rate': 72, 'spo2': 98, 'steps': 0, 'calories': 0,
            'skin_temp': 33.5, 'ble_connected': False, 'soc_pct': 80,
            'sleep_stage': '', 'workout_active': False, 'workout_type': '',
            'distance_m': 0, 'scenario': '',
        }

    def load_scenario(self, name: str):
        if name not in self.SCENARIOS:
            return
        self.scenario = name
        self._scenario_step = 0
        self.state['scenario'] = name

        imu = self.vm.peripherals.get('imu0')

        if name == 'step_counting' or name == 'workout_detection':
            if imu:
                imu.set_accel(0, 0, 12.0)

        elif name == 'sleep_tracking':
            self.state['sleep_stage'] = 'light'
            spo2 = self.vm.peripherals.get('spo2_0')
            if spo2:
                spo2.set_value(97, 60)

        elif name == 'notification':
            haptic = self.vm.peripherals.get('haptic0')
            if haptic:
                haptic.intensity = 200
                haptic.duration_ms = 500
                haptic._remaining_ms = 500

        elif name == 'workout_detection':
            self.state['workout_active'] = True
            self.state['workout_type'] = self.SCENARIOS[name].get('type', 'running')

    def tick(self):
        self.tick_count += 1
        for name, dev in self.vm.peripherals.items():
            if hasattr(dev, 'simulate_tick'):
                dev.simulate_tick()

        imu = self.vm.peripherals.get('imu0')
        spo2 = self.vm.peripherals.get('spo2_0')
        bms = self.vm.peripherals.get('bms0')
        ble = self.vm.peripherals.get('ble0')
        temp = self.vm.peripherals.get('temp0')

        if imu:
            mag = math.sqrt(sum(a * a for a in imu.accel))
            if mag > 11:
                self._step_acc += 0.3
                if self._step_acc >= 1.0:
                    self.state['steps'] += 1
                    self._step_acc -= 1.0
                    self.state['calories'] += 0.04
                    self.state['distance_m'] += 0.75

        if spo2:
            self.state['heart_rate'] = spo2.pulse_rate
            self.state['spo2'] = round(spo2.spo2_percent, 1)
        if bms:
            self.state['soc_pct'] = round(bms.soc_percent, 1)
        if ble:
            self.state['ble_connected'] = ble.connected
        if temp:
            self.state['skin_temp'] = round(temp.temperature, 1)

        self._apply_scenario()
        self._scenario_step += 1

    def _apply_scenario(self):
        if not self.scenario:
            return

        imu = self.vm.peripherals.get('imu0')

        if self.scenario == 'step_counting':
            if imu:
                swing = 3.0 * math.sin(self._scenario_step * 0.5)
                imu.set_accel(swing, random.gauss(0, 0.5), 9.81 + abs(swing))

        elif self.scenario == 'heart_rate_monitor':
            pass

        elif self.scenario == 'sleep_tracking':
            cycle = self._scenario_step % 360
            if cycle < 120:
                self.state['sleep_stage'] = 'light'
            elif cycle < 200:
                self.state['sleep_stage'] = 'deep'
            elif cycle < 280:
                self.state['sleep_stage'] = 'REM'
            else:
                self.state['sleep_stage'] = 'light'

            spo2 = self.vm.peripherals.get('spo2_0')
            if spo2:
                hr = 55 if self.state['sleep_stage'] == 'deep' else 65
                spo2.set_value(97, hr)

        elif self.scenario == 'notification':
            pass

        elif self.scenario == 'workout_detection':
            if imu:
                t = self._scenario_step * 0.3
                swing = 5.0 * math.sin(t)
                imu.set_accel(swing, random.gauss(0, 1), 9.81 + abs(swing) * 0.5)

            spo2 = self.vm.peripherals.get('spo2_0')
            if spo2 and self._scenario_step > 50:
                spo2.set_value(96, min(180, 100 + self._scenario_step // 10))

    def get_state(self) -> dict:
        return dict(self.state)

    def get_peripherals(self) -> dict:
        return dict(self.vm.peripherals)

    def get_status_text(self) -> str:
        hr = self.state.get('heart_rate', 0)
        steps = self.state.get('steps', 0)
        return f"{self.DISPLAY_NAME} | HR {hr} | {steps} steps | Tick {self.tick_count}"

    def reset(self):
        self.tick_count = 0
        self.state = {}
        self.scenario = ''
        self._step_acc = 0.0
