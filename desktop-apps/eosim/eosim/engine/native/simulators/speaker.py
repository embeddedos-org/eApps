# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""Smart Speaker simulator. Pure Python, cross-platform."""
import random


class SmartSpeakerSimulator:
    PRODUCT_TYPE = 'smart_speaker'
    DISPLAY_NAME = 'Smart Speaker'

    SCENARIOS = {
        'wake_word': {'description': 'Wake word detection and listening mode'},
        'voice_command': {'description': 'Process voice command after wake word'},
        'audio_playback': {'description': 'Stream and play audio content'},
        'ble_setup': {'description': 'BLE provisioning and WiFi setup flow'},
        'multi_room_sync': {'group_size': 3, 'description': 'Synchronise playback across speakers'},
        'alarm_trigger': {'description': 'Alarm/timer trigger and dismiss'},
    }

    def __init__(self, vm):
        self.vm = vm
        self.tick_count = 0
        self.state = {}
        self.scenario = ''
        self._scenario_step = 0

    def setup(self):
        from eosim.engine.native.peripherals.wireless import WiFiModule, BLEModule
        from eosim.engine.native.peripherals.sensors import TemperatureSensor
        from eosim.engine.native.peripherals.composites import BatteryManagement

        self.vm.add_peripheral('wifi0', WiFiModule('wifi0', 0x40400000))
        self.vm.add_peripheral('ble0', BLEModule('ble0', 0x40400100))
        self.vm.add_peripheral('temp0', TemperatureSensor('temp0', 0x40100000))
        self.vm.add_peripheral('bms0', BatteryManagement('bms0', 0x40500000, 1, 3000))

        self.state = {
            'wake_word_detected': False, 'listening': False,
            'volume_pct': 50, 'playing': False,
            'wifi_connected': False, 'ble_connected': False,
            'mic_active': True, 'speaker_group_size': 1,
            'command_count': 0, 'scenario': '',
        }

    def load_scenario(self, name: str):
        if name not in self.SCENARIOS:
            return
        self.scenario = name
        self._scenario_step = 0
        self.state['scenario'] = name

        wifi = self.vm.peripherals.get('wifi0')
        ble = self.vm.peripherals.get('ble0')

        if name in ('wake_word', 'voice_command', 'audio_playback', 'multi_room_sync', 'alarm_trigger'):
            if wifi:
                wifi.connect()
                self.state['wifi_connected'] = True
        elif name == 'ble_setup':
            if ble:
                ble.start_advertising()

    def tick(self):
        self.tick_count += 1

        for name, dev in self.vm.peripherals.items():
            if hasattr(dev, 'simulate_tick'):
                dev.simulate_tick()

        wifi = self.vm.peripherals.get('wifi0')
        ble = self.vm.peripherals.get('ble0')

        if wifi:
            self.state['wifi_connected'] = wifi.connected
        if ble:
            self.state['ble_connected'] = ble.connected

        self._apply_scenario()
        self._scenario_step += 1

    def _apply_scenario(self):
        if not self.scenario:
            return
        if self.scenario == 'wake_word':
            if self._scenario_step == 5:
                self.state['wake_word_detected'] = True
                self.state['listening'] = True
            if self._scenario_step == 25:
                self.state['listening'] = False
                self.state['wake_word_detected'] = False
        elif self.scenario == 'voice_command':
            if self._scenario_step == 5:
                self.state['wake_word_detected'] = True
                self.state['listening'] = True
            if self._scenario_step == 15:
                self.state['listening'] = False
                self.state['command_count'] += 1
            if self._scenario_step == 20:
                self.state['playing'] = True
        elif self.scenario == 'audio_playback':
            if self._scenario_step == 3:
                self.state['playing'] = True
        elif self.scenario == 'ble_setup':
            ble = self.vm.peripherals.get('ble0')
            if ble and self._scenario_step > 20 and not ble.connected:
                ble.connect_peer()
                self.state['ble_connected'] = True
        elif self.scenario == 'multi_room_sync':
            group = self.SCENARIOS['multi_room_sync']['group_size']
            if self._scenario_step % 10 == 0 and self.state['speaker_group_size'] < group:
                self.state['speaker_group_size'] += 1
            if self._scenario_step > 15:
                self.state['playing'] = True
        elif self.scenario == 'alarm_trigger':
            if self._scenario_step == 10:
                self.state['playing'] = True
                self.state['volume_pct'] = 100

    def get_state(self) -> dict:
        return dict(self.state)

    def get_peripherals(self) -> dict:
        return dict(self.vm.peripherals)

    def get_status_text(self) -> str:
        vol = self.state.get('volume_pct', 50)
        cmds = self.state.get('command_count', 0)
        return f"{self.DISPLAY_NAME} | Vol {vol}% | Cmds {cmds} | Tick {self.tick_count}"

    def reset(self):
        self.tick_count = 0
        self.state = {}
        self.scenario = ''
