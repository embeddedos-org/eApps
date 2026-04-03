# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""IoT / Smart Home simulator. Pure Python, cross-platform."""
import random


class IoTSimulator:
    PRODUCT_TYPE = 'iot'
    DISPLAY_NAME = 'IoT Device'

    SCENARIOS = {
        'sensor_cycle': {'interval': 30, 'description': 'Periodic sensor read and report'},
        'mqtt_publish': {'topic': 'sensor/data', 'description': 'Publish sensor data via MQTT'},
        'ble_pairing': {'description': 'BLE device pairing sequence'},
        'low_power_sleep': {'sleep_ms': 60000, 'description': 'Deep sleep between readings'},
        'ota_update': {'description': 'Over-the-air firmware update'},
        'multi_sensor': {'description': 'Aggregate multiple sensors and report'},
    }

    def __init__(self, vm):
        self.vm = vm
        self.tick_count = 0
        self.state = {}
        self.scenario = ''
        self._scenario_step = 0

    def setup(self):
        from eosim.engine.native.peripherals.sensors import TemperatureSensor, LightSensor, ADCChannel
        from eosim.engine.native.peripherals.actuators import RelayBank
        from eosim.engine.native.peripherals.wireless import WiFiModule, BLEModule
        from eosim.engine.native.peripherals.composites import BatteryManagement, RTCModule

        self.vm.add_peripheral('temp0', TemperatureSensor('temp0', 0x40100000))
        self.vm.add_peripheral('light0', LightSensor('light0', 0x40100500))
        self.vm.add_peripheral('adc0', ADCChannel('adc0', 0x40100600))
        self.vm.add_peripheral('relay0', RelayBank('relay0', 0x40200500, 4))
        self.vm.add_peripheral('wifi0', WiFiModule('wifi0', 0x40400000))
        self.vm.add_peripheral('ble0', BLEModule('ble0', 0x40400100))
        self.vm.add_peripheral('bms0', BatteryManagement('bms0', 0x40500000, 1, 2000))
        self.vm.add_peripheral('rtc0', RTCModule('rtc0', 0x40500400))

        self.state = {
            'temperature': 22, 'humidity': 45, 'light_lux': 500,
            'wifi_connected': False, 'ble_connected': False, 'soc_pct': 85,
            'sleep_mode': False, 'tx_count': 0, 'scenario': '',
        }

    def load_scenario(self, name: str):
        if name not in self.SCENARIOS:
            return
        self.scenario = name
        self._scenario_step = 0
        self.state['scenario'] = name

        wifi = self.vm.peripherals.get('wifi0')
        ble = self.vm.peripherals.get('ble0')

        if name in ('sensor_cycle', 'mqtt_publish', 'multi_sensor'):
            if wifi:
                wifi.connect()
                self.state['wifi_connected'] = True
        elif name == 'ble_pairing':
            if ble:
                ble.start_advertising()
        elif name == 'low_power_sleep':
            self.state['sleep_mode'] = True

    def tick(self):
        self.tick_count += 1
        if self.state.get('sleep_mode') and self.scenario == 'low_power_sleep':
            interval = self.SCENARIOS['low_power_sleep']['sleep_ms'] // 100
            if self.tick_count % max(1, interval) != 0:
                return
            self.state['sleep_mode'] = False

        for name, dev in self.vm.peripherals.items():
            if hasattr(dev, 'simulate_tick'):
                dev.simulate_tick()

        temp = self.vm.peripherals.get('temp0')
        light = self.vm.peripherals.get('light0')
        wifi = self.vm.peripherals.get('wifi0')
        ble = self.vm.peripherals.get('ble0')
        bms = self.vm.peripherals.get('bms0')

        if temp:
            self.state['temperature'] = round(temp.temperature, 1)
            self.state['humidity'] = round(temp.humidity, 1)
        if light:
            self.state['light_lux'] = round(light.lux, 0)
        if wifi:
            self.state['wifi_connected'] = wifi.connected
        if ble:
            self.state['ble_connected'] = ble.connected
        if bms:
            self.state['soc_pct'] = round(bms.soc_percent, 1)

        self._apply_scenario()
        self._scenario_step += 1

    def _apply_scenario(self):
        if not self.scenario:
            return
        if self.scenario == 'sensor_cycle':
            interval = self.SCENARIOS['sensor_cycle']['interval']
            if self._scenario_step % interval == 0:
                self.state['tx_count'] += 1
        elif self.scenario == 'mqtt_publish':
            if self._scenario_step % 10 == 0 and self.state.get('wifi_connected'):
                self.state['tx_count'] += 1
        elif self.scenario == 'ble_pairing':
            ble = self.vm.peripherals.get('ble0')
            if ble and self._scenario_step > 20 and not ble.connected:
                ble.connect_peer()
                self.state['ble_connected'] = True
        elif self.scenario == 'low_power_sleep':
            self.state['sleep_mode'] = True
        elif self.scenario == 'ota_update':
            pass
        elif self.scenario == 'multi_sensor':
            if self._scenario_step % 5 == 0:
                self.state['tx_count'] += 1

    def get_state(self) -> dict:
        return dict(self.state)

    def get_peripherals(self) -> dict:
        return dict(self.vm.peripherals)

    def get_status_text(self) -> str:
        return f"{self.DISPLAY_NAME} | TX {self.state.get('tx_count', 0)} | Tick {self.tick_count}"

    def reset(self):
        self.tick_count = 0
        self.state = {}
        self.scenario = ''
