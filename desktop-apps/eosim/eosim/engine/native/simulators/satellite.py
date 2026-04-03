# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""Satellite / CubeSat simulator. Pure Python, cross-platform."""
import random


class SatelliteSimulator:
    PRODUCT_TYPE = 'satellite'
    DISPLAY_NAME = 'CubeSat / Satellite'
    MODES = ['SAFE', 'DETUMBLE', 'SUN_POINTING', 'NOMINAL', 'COMMS', 'ECLIPSE']
    SCENARIOS = {
        'deployment': {'description': 'Post-deploy detumble'},
        'detumble': {'description': 'Reduce angular rates'},
        'sun_pointing': {'description': 'Orient panels to sun'},
        'ground_pass': {'description': 'Downlink during ground pass'},
        'eclipse_power': {'description': 'Eclipse power management'},
        'safe_mode': {'description': 'Enter safe mode'},
    }

    def __init__(self, vm):
        self.vm = vm; self.tick_count = 0; self.state = {}
        self.scenario = ''; self._scenario_step = 0

    def setup(self):
        from eosim.engine.native.peripherals.sensors import IMUSensor, GPSModule, ADCChannel
        from eosim.engine.native.peripherals.actuators import MotorController
        from eosim.engine.native.peripherals.wireless import RFTransceiver
        from eosim.engine.native.peripherals.composites import BatteryManagement, CryptoEngine, WatchdogTimer
        self.vm.add_peripheral('imu0', IMUSensor('imu0', 0x40100200, 9))
        self.vm.add_peripheral('gps0', GPSModule('gps0', 0x40100300))
        self.vm.add_peripheral('solar_adc', ADCChannel('solar_adc', 0x40100600, 4))
        self.vm.add_peripheral('reaction_wheel', MotorController('reaction_wheel', 0x40200000))
        self.vm.add_peripheral('rf0', RFTransceiver('rf0', 0x40400400))
        self.vm.add_peripheral('bms0', BatteryManagement('bms0', 0x40500000, 4, 2600))
        self.vm.add_peripheral('crypto0', CryptoEngine('crypto0', 0x40500300))
        self.vm.add_peripheral('wdt0', WatchdogTimer('wdt0', 0x40500200))
        self.state = {'orbit_alt_km': 550, 'angular_rate': [5, 3, 2], 'in_eclipse': False,
                      'solar_power_w': 5.0, 'soc_pct': 90, 'ground_contact': False,
                      'mode': 'DETUMBLE', 'data_downlinked_kb': 0, 'scenario': ''}

    def load_scenario(self, name):
        if name not in self.SCENARIOS: return
        self.scenario = name; self._scenario_step = 0; self.state['scenario'] = name
        if name == 'deployment': self.state['mode'] = 'DETUMBLE'; self.state['angular_rate'] = [8, 6, 4]
        elif name == 'detumble': self.state['mode'] = 'DETUMBLE'
        elif name == 'sun_pointing': self.state['mode'] = 'SUN_POINTING'
        elif name == 'ground_pass': self.state['mode'] = 'COMMS'; self.state['ground_contact'] = True
        elif name == 'eclipse_power': self.state['mode'] = 'ECLIPSE'; self.state['in_eclipse'] = True
        elif name == 'safe_mode': self.state['mode'] = 'SAFE'

    def tick(self):
        self.tick_count += 1
        for n, d in self.vm.peripherals.items():
            if hasattr(d, 'simulate_tick'): d.simulate_tick()
        bms = self.vm.peripherals.get('bms0'); imu = self.vm.peripherals.get('imu0')
        wheel = self.vm.peripherals.get('reaction_wheel')
        period = self.tick_count % 5400
        self.state['in_eclipse'] = period > 3600
        power = 0 if self.state['in_eclipse'] else 5.0 + random.gauss(0, 0.2)
        self.state['solar_power_w'] = round(max(0, power), 2)
        self.state['ground_contact'] = (period % 1800) < 600
        mode = self.state['mode']
        if mode == 'DETUMBLE':
            for i in range(3): self.state['angular_rate'][i] *= 0.98
            if all(abs(r) < 0.5 for r in self.state['angular_rate']): self.state['mode'] = 'NOMINAL'
            if wheel: wheel.enabled = True; wheel.target_speed = 100
        elif mode == 'COMMS':
            if self.state['ground_contact']: self.state['data_downlinked_kb'] += 10
            else: self.state['mode'] = 'NOMINAL'
        elif mode == 'ECLIPSE':
            if not self.state['in_eclipse']: self.state['mode'] = 'NOMINAL'
        elif mode == 'SAFE':
            if wheel: wheel.enabled = False
            if bms and bms.soc_percent > 50: self.state['mode'] = 'NOMINAL'
        if bms: bms.current_ma = 800 if self.state['in_eclipse'] else 300; self.state['soc_pct'] = round(bms.soc_percent, 1)
        if imu: imu.set_gyro(*self.state['angular_rate'])
        self._scenario_step += 1

    def get_state(self): return dict(self.state)
    def get_peripherals(self): return dict(self.vm.peripherals)
    def get_status_text(self):
        ecl = ' [ECLIPSE]' if self.state.get('in_eclipse') else ''
        return f"{self.DISPLAY_NAME} | {self.state.get('mode','SAFE')}{ecl} | Tick {self.tick_count}"
    def reset(self): self.tick_count = 0; self.state = {}; self.scenario = ''
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""Satellite / CubeSat simulator. Pure Python, cross-platform."""
import math
import random


class SatelliteSimulator:
    PRODUCT_TYPE = 'satellite'
    DISPLAY_NAME = 'CubeSat / Satellite'

    MODES = ['SAFE', 'DETUMBLE', 'SUN_POINTING', 'NOMINAL', 'COMMS', 'ECLIPSE']

    SCENARIOS = {
        'deployment': {'description': 'Post-deploy antenna release and detumble'},
        'detumble': {'description': 'Reduce angular rates after separation'},
        'sun_pointing': {'description': 'Orient solar panels toward sun'},
        'ground_pass': {'description': 'Downlink data during ground station pass'},
        'eclipse_power': {'description': 'Manage power budget during eclipse'},
        'safe_mode': {'description': 'Enter safe mode on anomaly'},
    }

    def __init__(self, vm):
        self.vm = vm
        self.tick_count = 0
        self.state = {}
        self.scenario = ''
        self._scenario_step = 0

    def setup(self):
        from eosim.engine.native.peripherals.sensors import IMUSensor, GPSModule, ADCChannel
        from eosim.engine.native.peripherals.actuators import MotorController
        from eosim.engine.native.peripherals.wireless import RFTransceiver
        from eosim.engine.native.peripherals.composites import BatteryManagement, CryptoEngine, WatchdogTimer

        self.vm.add_peripheral('imu0', IMUSensor('imu0', 0x40100200, 9))
        self.vm.add_peripheral('gps0', GPSModule('gps0', 0x40100300))
        self.vm.add_peripheral('solar_adc', ADCChannel('solar_adc', 0x40100600, 4))
        self.vm.add_peripheral('reaction_wheel', MotorController('reaction_wheel', 0x40200000))
        self.vm.add_peripheral('rf0', RFTransceiver('rf0', 0x40400400))
        self.vm.add_peripheral('bms0', BatteryManagement('bms0', 0x40500000, 4, 2600))
        self.vm.add_peripheral('crypto0', CryptoEngine('crypto0', 0x40500300))
        self.vm.add_peripheral('wdt0', WatchdogTimer('wdt0', 0x40500200))

        self.state = {
            'orbit_alt_km': 550, 'velocity_mps': 7600,
            'attitude': [0.0, 0.0, 0.0], 'angular_rate': [5.0, 3.0, 2.0],
            'in_eclipse': False, 'solar_power_w': 5.0, 'soc_pct': 90,
            'ground_contact': False, 'mode': 'DETUMBLE',
            'data_downlinked_kb': 0, 'scenario': '',
        }

    def load_scenario(self, name: str):
        if name not in self.SCENARIOS:
            return
        self.scenario = name
        self._scenario_step = 0
        self.state['scenario'] = name

        if name == 'deployment':
            self.state['mode'] = 'DETUMBLE'
            self.state['angular_rate'] = [8.0, 6.0, 4.0]
        elif name == 'detumble':
            self.state['mode'] = 'DETUMBLE'
        elif name == 'sun_pointing':
            self.state['mode'] = 'SUN_POINTING'
        elif name == 'ground_pass':
            self.state['mode'] = 'COMMS'
            self.state['ground_contact'] = True
            rf = self.vm.peripherals.get('rf0')
            if rf:
                rf.enabled = True
        elif name == 'eclipse_power':
            self.state['mode'] = 'ECLIPSE'
            self.state['in_eclipse'] = True
        elif name == 'safe_mode':
            self.state['mode'] = 'SAFE'

    def tick(self):
        self.tick_count += 1
        for name, dev in self.vm.peripherals.items():
            if hasattr(dev, 'simulate_tick'):
                dev.simulate_tick()

        bms = self.vm.peripherals.get('bms0')
        solar = self.vm.peripherals.get('solar_adc')
        imu = self.vm.peripherals.get('imu0')
        wheel = self.vm.peripherals.get('reaction_wheel')

        orbit_period = self.tick_count % 5400
        self.state['in_eclipse'] = orbit_period > 3600
        power = 0 if self.state['in_eclipse'] else 5.0 + random.gauss(0, 0.2)
        self.state['solar_power_w'] = round(max(0, power), 2)
        if solar:
            solar.set_voltage(0, int(power * 200))

        self.state['ground_contact'] = (orbit_period % 1800) < 600

        mode = self.state['mode']
        if mode == 'DETUMBLE':
            for i in range(3):
                self.state['angular_rate'][i] *= 0.98
                self.state['attitude'][i] += self.state['angular_rate'][i] * 0.01
            if all(abs(r) < 0.5 for r in self.state['angular_rate']):
                self.state['mode'] = 'NOMINAL'
            if wheel:
                wheel.enabled = True
                wheel.target_speed = 100

        elif mode == 'SUN_POINTING':
            sun_angle = (self.tick_count * 0.066) % 360
            for i in range(3):
                self.state['attitude'][i] += (sun_angle * 0.001 - self.state['attitude'][i]) * 0.05

        elif mode == 'COMMS':
            if self.state['ground_contact']:
                self.state['data_downlinked_kb'] += 10
            else:
                self.state['mode'] = 'NOMINAL'

        elif mode == 'ECLIPSE':
            if not self.state['in_eclipse']:
                self.state['mode'] = 'NOMINAL'

        elif mode == 'SAFE':
            if wheel:
                wheel.enabled = False
            if bms and bms.soc_percent > 50:
                self.state['mode'] = 'NOMINAL'

        if bms:
            bms.current_ma = 800 if self.state['in_eclipse'] else 300
            self.state['soc_pct'] = round(bms.soc_percent, 1)

        if imu:
            imu.set_gyro(*self.state['angular_rate'])

        self._scenario_step += 1

    def get_state(self) -> dict:
        return dict(self.state)

    def get_peripherals(self) -> dict:
        return dict(self.vm.peripherals)

    def get_status_text(self) -> str:
        mode = self.state.get('mode', 'SAFE')
        ecl = ' [ECLIPSE]' if self.state.get('in_eclipse') else ''
        return f"{self.DISPLAY_NAME} | {mode}{ecl} | Tick {self.tick_count}"

    def reset(self):
        self.tick_count = 0
        self.state = {}
        self.scenario = ''
