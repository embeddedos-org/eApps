# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""Media Streaming Device simulator. Pure Python, cross-platform."""
import random


class MediaDeviceSimulator:
    PRODUCT_TYPE = 'media_device'
    DISPLAY_NAME = 'Media Streaming Device'

    SCENARIOS = {
        'channel_switch': {'channel': 1, 'description': 'Switch TV channel and rebuffer'},
        'stream_buffer': {'bitrate': 8000, 'description': 'Continuous stream buffering'},
        'hdmi_cec': {'description': 'HDMI-CEC device discovery and control'},
        'cast_discovery': {'description': 'Discover and pair cast peers on network'},
        'epg_load': {'description': 'Load electronic programme guide data'},
        'drm_handshake': {'description': 'DRM licence negotiation and key exchange'},
    }

    def __init__(self, vm):
        self.vm = vm
        self.tick_count = 0
        self.state = {}
        self.scenario = ''
        self._scenario_step = 0

    def setup(self):
        from eosim.engine.native.peripherals.wireless import WiFiModule, BLEModule
        from eosim.engine.native.peripherals.actuators import DisplayDriver
        from eosim.engine.native.peripherals.composites import RTCModule

        self.vm.add_peripheral('wifi0', WiFiModule('wifi0', 0x40400000))
        self.vm.add_peripheral('ble0', BLEModule('ble0', 0x40400100))
        self.vm.add_peripheral('display0', DisplayDriver('display0', 0x40200000))
        self.vm.add_peripheral('rtc0', RTCModule('rtc0', 0x40500400))

        self.state = {
            'channel': 1, 'stream_bitrate_kbps': 0, 'buffer_pct': 0,
            'hdmi_connected': False, 'wifi_connected': False,
            'cast_peers': 0, 'drm_active': False,
            'resolution': '1080p', 'audio_codec': 'AAC',
            'scenario': '',
        }

    def load_scenario(self, name: str):
        if name not in self.SCENARIOS:
            return
        self.scenario = name
        self._scenario_step = 0
        self.state['scenario'] = name

        wifi = self.vm.peripherals.get('wifi0')

        if name in ('channel_switch', 'stream_buffer', 'cast_discovery', 'epg_load'):
            if wifi:
                wifi.connect()
                self.state['wifi_connected'] = True
        elif name == 'hdmi_cec':
            self.state['hdmi_connected'] = True
        elif name == 'drm_handshake':
            if wifi:
                wifi.connect()
                self.state['wifi_connected'] = True
            self.state['drm_active'] = False

    def tick(self):
        self.tick_count += 1

        for name, dev in self.vm.peripherals.items():
            if hasattr(dev, 'simulate_tick'):
                dev.simulate_tick()

        wifi = self.vm.peripherals.get('wifi0')
        if wifi:
            self.state['wifi_connected'] = wifi.connected

        if self.state.get('wifi_connected') and self.state['buffer_pct'] < 100:
            self.state['buffer_pct'] = min(100, self.state['buffer_pct'] + random.randint(1, 3))

        if self.state['buffer_pct'] >= 100:
            self.state['stream_bitrate_kbps'] = 8000

        self._apply_scenario()
        self._scenario_step += 1

    def _apply_scenario(self):
        if not self.scenario:
            return
        if self.scenario == 'channel_switch':
            if self._scenario_step % 50 == 0:
                self.state['channel'] += 1
                self.state['buffer_pct'] = 0
                self.state['stream_bitrate_kbps'] = 0
        elif self.scenario == 'stream_buffer':
            pass
        elif self.scenario == 'hdmi_cec':
            if self._scenario_step == 10:
                self.state['hdmi_connected'] = True
        elif self.scenario == 'cast_discovery':
            if self._scenario_step % 15 == 0 and self.state['cast_peers'] < 5:
                self.state['cast_peers'] += 1
        elif self.scenario == 'epg_load':
            pass
        elif self.scenario == 'drm_handshake':
            if self._scenario_step > 20 and not self.state['drm_active']:
                self.state['drm_active'] = True

    def get_state(self) -> dict:
        return dict(self.state)

    def get_peripherals(self) -> dict:
        return dict(self.vm.peripherals)

    def get_status_text(self) -> str:
        ch = self.state.get('channel', 1)
        buf = self.state.get('buffer_pct', 0)
        return f"{self.DISPLAY_NAME} | CH {ch} | Buf {buf}% | Tick {self.tick_count}"

    def reset(self):
        self.tick_count = 0
        self.state = {}
        self.scenario = ''
