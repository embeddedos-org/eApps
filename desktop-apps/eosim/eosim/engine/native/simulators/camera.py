# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""Home Camera simulator. Pure Python, cross-platform."""
import random


class HomeCameraSimulator:
    PRODUCT_TYPE = 'home_camera'
    DISPLAY_NAME = 'Home Camera'

    SCENARIOS = {
        'motion_detect': {'threshold': 0.6, 'description': 'Motion detection with alert cooldown'},
        'night_vision': {'description': 'Auto night vision based on ambient light'},
        'live_stream': {'fps': 30, 'description': 'Live video stream to cloud/app'},
        'cloud_upload': {'description': 'Upload recorded clips to cloud storage'},
        'pan_tilt': {'description': 'Pan-tilt motor control for camera positioning'},
        'two_way_audio': {'description': 'Two-way audio communication channel'},
    }

    def __init__(self, vm):
        self.vm = vm
        self.tick_count = 0
        self.state = {}
        self.scenario = ''
        self._scenario_step = 0
        self._motion_cooldown = 0

    def setup(self):
        from eosim.engine.native.peripherals.wireless import WiFiModule
        from eosim.engine.native.peripherals.sensors import TemperatureSensor, LightSensor
        from eosim.engine.native.peripherals.composites import RTCModule, BatteryManagement

        self.vm.add_peripheral('wifi0', WiFiModule('wifi0', 0x40400000))
        self.vm.add_peripheral('temp0', TemperatureSensor('temp0', 0x40100000))
        self.vm.add_peripheral('light0', LightSensor('light0', 0x40100500))
        self.vm.add_peripheral('rtc0', RTCModule('rtc0', 0x40500400))
        self.vm.add_peripheral('bms0', BatteryManagement('bms0', 0x40500000, 1, 4000))

        self.state = {
            'motion_detected': False, 'recording': False,
            'night_mode': False, 'pan_angle': 0, 'tilt_angle': 0,
            'stream_fps': 0, 'wifi_connected': False,
            'storage_used_mb': 0, 'alerts_count': 0,
            'ir_active': False, 'scenario': '',
        }

    def load_scenario(self, name: str):
        if name not in self.SCENARIOS:
            return
        self.scenario = name
        self._scenario_step = 0
        self.state['scenario'] = name

        wifi = self.vm.peripherals.get('wifi0')

        if name in ('motion_detect', 'live_stream', 'cloud_upload', 'two_way_audio'):
            if wifi:
                wifi.connect()
                self.state['wifi_connected'] = True
        elif name == 'night_vision':
            self.state['night_mode'] = True
            self.state['ir_active'] = True

    def tick(self):
        self.tick_count += 1

        for name, dev in self.vm.peripherals.items():
            if hasattr(dev, 'simulate_tick'):
                dev.simulate_tick()

        wifi = self.vm.peripherals.get('wifi0')
        light = self.vm.peripherals.get('light0')

        if wifi:
            self.state['wifi_connected'] = wifi.connected
        if light:
            lux = light.lux
            if lux < 10:
                self.state['night_mode'] = True
                self.state['ir_active'] = True
            else:
                self.state['night_mode'] = False
                self.state['ir_active'] = False

        if self.state.get('recording'):
            self.state['storage_used_mb'] = round(self.state['storage_used_mb'] + 0.5, 1)

        if self._motion_cooldown > 0:
            self._motion_cooldown -= 1

        self._apply_scenario()
        self._scenario_step += 1

    def _apply_scenario(self):
        if not self.scenario:
            return
        if self.scenario == 'motion_detect':
            threshold = self.SCENARIOS['motion_detect']['threshold']
            if self._motion_cooldown <= 0 and random.random() > threshold:
                self.state['motion_detected'] = True
                self.state['recording'] = True
                self.state['alerts_count'] += 1
                self._motion_cooldown = 30
            elif self._motion_cooldown <= 0:
                self.state['motion_detected'] = False
        elif self.scenario == 'night_vision':
            pass
        elif self.scenario == 'live_stream':
            fps = self.SCENARIOS['live_stream']['fps']
            self.state['stream_fps'] = fps
            self.state['recording'] = True
        elif self.scenario == 'cloud_upload':
            if self._scenario_step % 20 == 0 and self.state['storage_used_mb'] > 10:
                self.state['storage_used_mb'] = max(0, self.state['storage_used_mb'] - 10)
        elif self.scenario == 'pan_tilt':
            if self._scenario_step % 5 == 0:
                self.state['pan_angle'] = (self.state['pan_angle'] + 15) % 360
            if self._scenario_step % 8 == 0:
                self.state['tilt_angle'] = max(-45, min(45, self.state['tilt_angle'] + random.choice([-10, 10])))
        elif self.scenario == 'two_way_audio':
            if self._scenario_step == 5:
                self.state['recording'] = True

    def get_state(self) -> dict:
        return dict(self.state)

    def get_peripherals(self) -> dict:
        return dict(self.vm.peripherals)

    def get_status_text(self) -> str:
        alerts = self.state.get('alerts_count', 0)
        storage = self.state.get('storage_used_mb', 0)
        return f"{self.DISPLAY_NAME} | Alerts {alerts} | {storage}MB | Tick {self.tick_count}"

    def reset(self):
        self.tick_count = 0
        self.state = {}
        self.scenario = ''
        self._motion_cooldown = 0
