# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""Wireless communication peripherals for EoSim simulation."""
import random
from collections import deque


class WirelessBase:
    """Base class for wireless peripherals."""

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


class WiFiModule(WirelessBase):
    """WiFi 802.11 module."""

    def __init__(self, name: str = 'wifi0', base_addr: int = 0x40400000):
        super().__init__(name, base_addr)
        self.ssid = 'EoSim-Network'
        self.connected = False
        self.rssi = -55
        self.ip_addr = '192.168.1.100'
        self.tx_packets = 0
        self.rx_packets = 0
        self.channel = 6
        self.security = 'WPA2'

    def connect(self, ssid: str = ''):
        self.ssid = ssid or self.ssid
        self.connected = True
        self.rssi = -45 + random.randint(-15, 5)

    def disconnect(self):
        self.connected = False
        self.rssi = 0

    def simulate_tick(self):
        if self.connected:
            self.rssi += random.gauss(0, 1)
            self.rssi = max(-90, min(-20, int(self.rssi)))

    def read_reg(self, offset: int) -> int:
        if offset == 0x00:
            return int(self.connected) | (int(self.enabled) << 1)
        elif offset == 0x04:
            return self.rssi & 0xFFFFFFFF
        elif offset == 0x08:
            return self.tx_packets
        elif offset == 0x0C:
            return self.rx_packets
        return 0

    def write_reg(self, offset: int, val: int):
        if offset == 0x00:
            self.enabled = bool(val & 2)
            if val & 1:
                self.connect()
            elif not (val & 1) and self.connected:
                self.disconnect()


class BLEModule(WirelessBase):
    """Bluetooth Low Energy module."""

    def __init__(self, name: str = 'ble0', base_addr: int = 0x40400100):
        super().__init__(name, base_addr)
        self.advertising = False
        self.connected = False
        self.rssi = -60
        self.peer_addr = ''
        self.services: list = []
        self.characteristics: dict = {}
        self.tx_packets = 0
        self.rx_packets = 0
        self.mtu = 23

    def start_advertising(self):
        self.advertising = True

    def connect_peer(self, addr: str = 'AA:BB:CC:DD:EE:FF'):
        self.connected = True
        self.advertising = False
        self.peer_addr = addr
        self.rssi = -50 + random.randint(-15, 5)

    def simulate_tick(self):
        if self.connected:
            self.rssi += random.gauss(0, 0.5)
            self.rssi = max(-90, min(-20, int(self.rssi)))

    def read_reg(self, offset: int) -> int:
        if offset == 0x00:
            return (int(self.advertising) |
                    (int(self.connected) << 1) |
                    (int(self.enabled) << 2))
        elif offset == 0x04:
            return self.rssi & 0xFFFFFFFF
        elif offset == 0x08:
            return self.tx_packets
        elif offset == 0x0C:
            return self.rx_packets
        return 0

    def write_reg(self, offset: int, val: int):
        if offset == 0x00:
            self.enabled = bool(val & 4)
            if val & 1:
                self.start_advertising()


class LoRaModule(WirelessBase):
    """LoRa/LoRaWAN module for IoT."""

    def __init__(self, name: str = 'lora0', base_addr: int = 0x40400200):
        super().__init__(name, base_addr)
        self.joined = False
        self.dev_eui = '00:11:22:33:44:55:66:77'
        self.spreading_factor = 7
        self.tx_power = 14
        self.frequency_mhz = 915.0
        self.packets_sent = 0
        self.packets_received = 0
        self.rssi = -100
        self.snr = 10.0

    def join_network(self):
        self.joined = True
        self.rssi = -90 + random.randint(-10, 20)

    def send_packet(self, data: bytes):
        self.packets_sent += 1

    def simulate_tick(self):
        if self.joined:
            self.rssi += random.gauss(0, 0.5)
            self.rssi = max(-130, min(-30, int(self.rssi)))

    def read_reg(self, offset: int) -> int:
        if offset == 0x00:
            return int(self.joined) | (int(self.enabled) << 1)
        elif offset == 0x04:
            return self.spreading_factor
        elif offset == 0x08:
            return self.packets_sent
        elif offset == 0x0C:
            return self.rssi & 0xFFFFFFFF
        return 0

    def write_reg(self, offset: int, val: int):
        if offset == 0x00:
            self.enabled = bool(val & 2)
            if val & 1:
                self.join_network()
        elif offset == 0x04:
            self.spreading_factor = max(7, min(12, val))


class ZigbeeModule(WirelessBase):
    """Zigbee/Thread module for smart home."""

    def __init__(self, name: str = 'zigbee0', base_addr: int = 0x40400300):
        super().__init__(name, base_addr)
        self.pan_id = 0x1234
        self.network_joined = False
        self.short_addr = 0xFFFE
        self.channel = 15
        self.tx_packets = 0
        self.rx_packets = 0

    def join_network(self, pan_id: int = 0):
        if pan_id:
            self.pan_id = pan_id
        self.network_joined = True
        self.short_addr = random.randint(0x0001, 0xFFF0)

    def read_reg(self, offset: int) -> int:
        if offset == 0x00:
            return int(self.network_joined) | (int(self.enabled) << 1)
        elif offset == 0x04:
            return self.pan_id
        elif offset == 0x08:
            return self.short_addr
        elif offset == 0x0C:
            return self.channel
        return 0

    def write_reg(self, offset: int, val: int):
        if offset == 0x00:
            self.enabled = bool(val & 2)
            if val & 1:
                self.join_network()
        elif offset == 0x0C:
            self.channel = max(11, min(26, val))


class RFTransceiver(WirelessBase):
    """Generic RF transceiver for telecom/defense."""

    def __init__(self, name: str = 'rf0', base_addr: int = 0x40400400):
        super().__init__(name, base_addr)
        self.frequency_mhz = 2400.0
        self.tx_power_dbm = 20
        self.modulation = 'QPSK'
        self.bandwidth_khz = 200
        self.rssi = -80
        self.tx_packets = 0
        self.rx_packets = 0

    def simulate_tick(self):
        if self.enabled:
            self.rssi += random.gauss(0, 0.3)
            self.rssi = max(-120, min(-10, int(self.rssi)))

    def read_reg(self, offset: int) -> int:
        if offset == 0x00:
            return int(self.enabled)
        elif offset == 0x04:
            return int(self.frequency_mhz * 100) & 0xFFFFFFFF
        elif offset == 0x08:
            return self.tx_power_dbm
        elif offset == 0x0C:
            return self.rssi & 0xFFFFFFFF
        return 0

    def write_reg(self, offset: int, val: int):
        if offset == 0x00:
            self.enabled = bool(val & 1)
        elif offset == 0x04:
            self.frequency_mhz = val / 100.0
        elif offset == 0x08:
            self.tx_power_dbm = max(-20, min(30, val))
