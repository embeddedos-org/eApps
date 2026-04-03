# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""Energy / Power system simulator. Pure Python, cross-platform."""
import math, random


class EnergySimulator:
    PRODUCT_TYPE = 'energy'
    DISPLAY_NAME = 'Energy System'
    SCENARIOS = {
        'mppt_tracking': {'description': 'Solar MPPT peak power tracking'},
        'grid_sync': {'target_freq': 60.0, 'description': 'Sync inverter to grid'},
        'charge_discharge': {'description': 'Battery charge/discharge cycle'},
        'islanding': {'description': 'Grid disconnect, island mode'},
        'load_shedding': {'max_load_w': 2000, 'description': 'Shed non-critical loads'},
    }

    def __init__(self, vm):
        self.vm = vm; self.tick_count = 0; self.state = {}
        self.scenario = ''; self._scenario_step = 0

    def setup(self):
        from eosim.engine.native.peripherals.sensors import ADCChannel, TemperatureSensor, CurrentSensor
        from eosim.engine.native.peripherals.actuators import RelayBank
        from eosim.engine.native.peripherals.buses import ModbusController
        from eosim.engine.native.peripherals.composites import BatteryManagement, RTCModule
        self.vm.add_peripheral('solar_adc', ADCChannel('solar_adc', 0x40100600, 4))
        self.vm.add_peripheral('current0', CurrentSensor('current0', 0x40100700))
        self.vm.add_peripheral('temp0', TemperatureSensor('temp0', 0x40100000, -20, 80))
        self.vm.add_peripheral('relay0', RelayBank('relay0', 0x40200500))
        self.vm.add_peripheral('modbus0', ModbusController('modbus0', 0x40300200))
        self.vm.add_peripheral('bms0', BatteryManagement('bms0', 0x40500000, 16, 100000))
        self.vm.add_peripheral('rtc0', RTCModule('rtc0', 0x40500400))
        self.state = {'solar_power_w': 0, 'grid_power_w': 0, 'load_power_w': 500,
                      'battery_soc': 60, 'grid_frequency_hz': 60.0, 'mode': 'GRID_TIE',
                      'mppt_voltage': 0, 'island_mode': False, 'scenario': ''}

    def load_scenario(self, name):
        if name not in self.SCENARIOS: return
        self.scenario = name; self._scenario_step = 0; self.state['scenario'] = name
        if name == 'islanding': self.state['island_mode'] = True; self.state['mode'] = 'ISLAND'
        elif name == 'load_shedding': self.state['load_power_w'] = 3000

    def tick(self):
        self.tick_count += 1
        for n, d in self.vm.peripherals.items():
            if hasattr(d, 'simulate_tick'): d.simulate_tick()
        hour = (self.tick_count % 2400) / 100
        solar = max(0, 3000 * math.sin(math.pi * (hour - 6) / 12)) if 6 <= hour <= 18 else 0
        solar += random.gauss(0, 50)
        self.state['solar_power_w'] = round(max(0, solar))
        self.state['grid_frequency_hz'] = 60.0 + random.gauss(0, 0.02)
        if self.scenario == 'mppt_tracking': self.state['mppt_voltage'] = round(solar * 0.12 + random.gauss(0, 0.5), 1)
        elif self.scenario == 'islanding': self.state['grid_power_w'] = 0; self.state['mode'] = 'ISLAND'
        elif self.scenario == 'load_shedding':
            relay = self.vm.peripherals.get('relay0')
            if self.state['load_power_w'] > 2000 and relay: relay.states[7] = False; self.state['load_power_w'] = 2000
        elif self.scenario == 'charge_discharge':
            bms = self.vm.peripherals.get('bms0')
            if bms: bms.charging = (self._scenario_step % 400) < 200
        bms = self.vm.peripherals.get('bms0')
        modbus = self.vm.peripherals.get('modbus0')
        if bms:
            surplus = solar - self.state['load_power_w']
            bms.charging = surplus > 0; bms.current_ma = abs(surplus) * 0.2
            self.state['battery_soc'] = round(bms.soc_percent, 1)
        if modbus:
            modbus.registers[0] = int(self.state['solar_power_w'])
            modbus.registers[1] = int(self.state['battery_soc'] * 10)
        self._scenario_step += 1

    def get_state(self): return dict(self.state)
    def get_peripherals(self): return dict(self.vm.peripherals)
    def get_status_text(self): return f"{self.DISPLAY_NAME} | {self.state.get('mode','GRID_TIE')} | SOC {self.state.get('battery_soc',0)}% | Tick {self.tick_count}"
    def reset(self): self.tick_count = 0; self.state = {}; self.scenario = ''
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""Energy / Power system simulator. Pure Python, cross-platform."""
import math
import random


class EnergySimulator:
    PRODUCT_TYPE = 'energy'
    DISPLAY_NAME = 'Energy System'

    SCENARIOS = {
        'mppt_tracking': {'description': 'Solar MPPT algorithm tracking peak power'},
        'grid_sync': {'target_freq': 60.0, 'description': 'Synchronize inverter to grid frequency'},
        'charge_discharge': {'description': 'Battery charge/discharge cycle'},
        'islanding': {'description': 'Grid disconnect, operate in island mode'},
        'load_shedding': {'max_load_w': 2000, 'description': 'Shed non-critical loads'},
    }

    def __init__(self, vm):
        self.vm = vm
        self.tick_count = 0
        self.state = {}
        self.scenario = ''
        self._scenario_step = 0

    def setup(self):
        from eosim.engine.native.peripherals.sensors import ADCChannel, TemperatureSensor, CurrentSensor
        from eosim.engine.native.peripherals.actuators import RelayBank
        from eosim.engine.native.peripherals.buses import ModbusController
        from eosim.engine.native.peripherals.composites import BatteryManagement, RTCModule

        self.vm.add_peripheral('solar_adc', ADCChannel('solar_adc', 0x40100600, 4))
        self.vm.add_peripheral('current0', CurrentSensor('current0', 0x40100700))
        self.vm.add_peripheral('temp0', TemperatureSensor('temp0', 0x40100000, -20, 80))
        self.vm.add_peripheral('relay0', RelayBank('relay0', 0x40200500))
        self.vm.add_peripheral('modbus0', ModbusController('modbus0', 0x40300200))
        self.vm.add_peripheral('bms0', BatteryManagement('bms0', 0x40500000, 16, 100000))
        self.vm.add_peripheral('rtc0', RTCModule('rtc0', 0x40500400))

        self.state = {
            'solar_power_w': 0, 'grid_power_w': 0, 'load_power_w': 500,
            'battery_soc': 60, 'grid_frequency_hz': 60.0, 'mode': 'GRID_TIE',
            'mppt_voltage': 0, 'island_mode': False, 'scenario': '',
        }

    def load_scenario(self, name: str):
        if name not in self.SCENARIOS:
            return
        self.scenario = name
        self._scenario_step = 0
        self.state['scenario'] = name

        if name == 'islanding':
            self.state['island_mode'] = True
            self.state['mode'] = 'ISLAND'
        elif name == 'load_shedding':
            self.state['load_power_w'] = 3000

    def tick(self):
        self.tick_count += 1
        for name, dev in self.vm.peripherals.items():
            if hasattr(dev, 'simulate_tick'):
                dev.simulate_tick()

        hour_sim = (self.tick_count % 2400) / 100
        solar = max(0, 3000 * math.sin(math.pi * (hour_sim - 6) / 12)) if 6 <= hour_sim <= 18 else 0
        solar += random.gauss(0, 50)
        self.state['solar_power_w'] = round(max(0, solar), 0)
        self.state['grid_frequency_hz'] = 60.0 + random.gauss(0, 0.02)

        self._apply_scenario()

        bms = self.vm.peripherals.get('bms0')
        solar_adc = self.vm.peripherals.get('solar_adc')
        current = self.vm.peripherals.get('current0')
        modbus = self.vm.peripherals.get('modbus0')

        if solar_adc:
            solar_adc.set_voltage(0, int(solar * 0.1))

        if bms:
            surplus = solar - self.state['load_power_w']
            if surplus > 0:
                bms.charging = True
                bms.current_ma = surplus * 0.2
            else:
                bms.charging = False
                bms.current_ma = abs(surplus) * 0.2
            self.state['battery_soc'] = round(bms.soc_percent, 1)

        if current:
            current.set_value(abs(solar - self.state['load_power_w']) * 0.01, 240000)

        if modbus:
            modbus.registers[0] = int(self.state['solar_power_w'])
            modbus.registers[1] = int(self.state['battery_soc'] * 10)
            modbus.registers[2] = int(self.state['load_power_w'])

        self._scenario_step += 1

    def _apply_scenario(self):
        if not self.scenario:
            return
        if self.scenario == 'mppt_tracking':
            solar = self.state['solar_power_w']
            self.state['mppt_voltage'] = round(solar * 0.12 + random.gauss(0, 0.5), 1)

        elif self.scenario == 'grid_sync':
            target = self.SCENARIOS['grid_sync']['target_freq']
            self.state['grid_frequency_hz'] = target + random.gauss(0, 0.01)

        elif self.scenario == 'charge_discharge':
            cycle = self._scenario_step % 400
            bms = self.vm.peripherals.get('bms0')
            if bms:
                bms.charging = cycle < 200

        elif self.scenario == 'islanding':
            self.state['grid_power_w'] = 0
            self.state['mode'] = 'ISLAND'

        elif self.scenario == 'load_shedding':
            max_load = self.SCENARIOS['load_shedding']['max_load_w']
            relay = self.vm.peripherals.get('relay0')
            if self.state['load_power_w'] > max_load and relay:
                relay.states[7] = False
                relay.states[6] = False
                self.state['load_power_w'] = max_load

    def get_state(self) -> dict:
        return dict(self.state)

    def get_peripherals(self) -> dict:
        return dict(self.vm.peripherals)

    def get_status_text(self) -> str:
        mode = self.state.get('mode', 'GRID_TIE')
        soc = self.state.get('battery_soc', 0)
        return f"{self.DISPLAY_NAME} | {mode} | SOC {soc}% | Tick {self.tick_count}"

    def reset(self):
        self.tick_count = 0
        self.state = {}
        self.scenario = ''
