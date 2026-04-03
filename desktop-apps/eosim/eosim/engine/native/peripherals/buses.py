# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""Domain-specific bus protocol peripherals for EoSim simulation."""
from typing import List, Dict, Optional
from collections import deque


class BusBase:
    """Base class for bus protocol peripherals."""

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


class CANBusController(BusBase):
    """CAN 2.0A/B bus controller for automotive."""

    def __init__(self, name: str = 'can0', base_addr: int = 0x40300000,
                 bitrate: int = 500000):
        super().__init__(name, base_addr)
        self.bitrate = bitrate
        self.tx_queue: deque = deque(maxlen=64)
        self.rx_queue: deque = deque(maxlen=64)
        self.filters: List[int] = []
        self.bus_off = False
        self.error_count = 0
        self.tx_count = 0
        self.rx_count = 0
        self.last_tx_id = 0
        self.last_rx_id = 0
        self.loopback = False

    def send_message(self, msg_id: int, data: bytes, extended: bool = False):
        msg = {'id': msg_id, 'data': data, 'extended': extended, 'dlc': len(data)}
        self.tx_queue.append(msg)
        self.tx_count += 1
        self.last_tx_id = msg_id
        if self.loopback:
            self.rx_queue.append(msg)
            self.rx_count += 1

    def receive_message(self) -> Optional[dict]:
        if self.rx_queue:
            msg = self.rx_queue.popleft()
            self.last_rx_id = msg['id']
            return msg
        return None

    def inject_message(self, msg_id: int, data: bytes):
        if not self.filters or msg_id in self.filters:
            msg = {'id': msg_id, 'data': data, 'extended': False, 'dlc': len(data)}
            self.rx_queue.append(msg)
            self.rx_count += 1

    def read_reg(self, offset: int) -> int:
        if offset == 0x00:
            return int(self.enabled) | (int(self.bus_off) << 1)
        elif offset == 0x04:
            return self.tx_count
        elif offset == 0x08:
            return self.rx_count
        elif offset == 0x0C:
            return len(self.rx_queue)
        elif offset == 0x10:
            return self.last_rx_id
        elif offset == 0x14:
            return self.error_count
        return 0

    def write_reg(self, offset: int, val: int):
        if offset == 0x00:
            self.enabled = bool(val & 1)
        elif offset == 0x04:
            self.bitrate = val
        elif offset == 0x10:
            self.send_message(val, b'\x00' * 8)


class LINBusController(BusBase):
    """LIN bus controller for automotive body electronics."""

    def __init__(self, name: str = 'lin0', base_addr: int = 0x40300100):
        super().__init__(name, base_addr)
        self.schedule_table: List[dict] = []
        self.frame_buffer: Dict[int, bytes] = {}
        self.current_frame_id = 0
        self.master_mode = True

    def send_frame(self, frame_id: int, data: bytes):
        self.frame_buffer[frame_id] = data
        self.current_frame_id = frame_id

    def read_reg(self, offset: int) -> int:
        if offset == 0x00:
            return self.current_frame_id
        elif offset == 0x04:
            return int(self.master_mode)
        return 0

    def write_reg(self, offset: int, val: int):
        if offset == 0x00:
            self.current_frame_id = val & 0x3F
        elif offset == 0x04:
            self.master_mode = bool(val & 1)


class ModbusController(BusBase):
    """Modbus RTU/TCP controller for industrial automation."""

    def __init__(self, name: str = 'modbus0', base_addr: int = 0x40300200,
                 mode: str = 'rtu'):
        super().__init__(name, base_addr)
        self.mode = mode
        self.slave_addr = 1
        self.registers: List[int] = [0] * 256
        self.coils: List[bool] = [False] * 256
        self.input_registers: List[int] = [0] * 256
        self.discrete_inputs: List[bool] = [False] * 256
        self.transaction_count = 0

    def read_holding(self, addr: int, count: int = 1) -> List[int]:
        return self.registers[addr:addr + count]

    def write_holding(self, addr: int, values: List[int]):
        for i, v in enumerate(values):
            if addr + i < len(self.registers):
                self.registers[addr + i] = v & 0xFFFF
        self.transaction_count += 1

    def read_coil(self, addr: int) -> bool:
        return self.coils[addr] if addr < len(self.coils) else False

    def write_coil(self, addr: int, val: bool):
        if addr < len(self.coils):
            self.coils[addr] = val
        self.transaction_count += 1

    def read_reg(self, offset: int) -> int:
        if offset == 0x00:
            return self.slave_addr
        elif offset == 0x04:
            return self.transaction_count
        return 0

    def write_reg(self, offset: int, val: int):
        if offset == 0x00:
            self.slave_addr = val & 0xFF


class EthernetMAC(BusBase):
    """Ethernet MAC controller."""

    def __init__(self, name: str = 'eth0', base_addr: int = 0x40300300):
        super().__init__(name, base_addr)
        self.mac_addr = [0x02, 0x00, 0x00, 0x00, 0x00, 0x01]
        self.link_up = True
        self.speed_mbps = 100
        self.tx_packets = 0
        self.rx_packets = 0
        self.tx_bytes = 0
        self.rx_bytes = 0
        self.ip_addr = '192.168.1.100'
        self.tx_buffer: deque = deque(maxlen=64)
        self.rx_buffer: deque = deque(maxlen=64)

    def send_packet(self, data: bytes):
        self.tx_buffer.append(data)
        self.tx_packets += 1
        self.tx_bytes += len(data)

    def inject_packet(self, data: bytes):
        self.rx_buffer.append(data)
        self.rx_packets += 1
        self.rx_bytes += len(data)

    def read_reg(self, offset: int) -> int:
        if offset == 0x00:
            return int(self.link_up) | (int(self.enabled) << 1)
        elif offset == 0x04:
            return self.speed_mbps
        elif offset == 0x08:
            return self.tx_packets
        elif offset == 0x0C:
            return self.rx_packets
        return 0

    def write_reg(self, offset: int, val: int):
        if offset == 0x00:
            self.enabled = bool(val & 1)


class ARINC429(BusBase):
    """ARINC 429 avionics data bus."""

    def __init__(self, name: str = 'arinc0', base_addr: int = 0x40300400):
        super().__init__(name, base_addr)
        self.tx_labels: deque = deque(maxlen=256)
        self.rx_labels: deque = deque(maxlen=256)
        self.speed = 'high'
        self.tx_count = 0
        self.rx_count = 0

    def send_word(self, label: int, sdi: int, data: int, ssm: int):
        word = ((label & 0xFF) | ((sdi & 0x3) << 8) |
                ((data & 0x7FFFF) << 10) | ((ssm & 0x3) << 29))
        self.tx_labels.append(word)
        self.tx_count += 1

    def inject_word(self, word: int):
        self.rx_labels.append(word)
        self.rx_count += 1

    def read_reg(self, offset: int) -> int:
        if offset == 0x00:
            return int(self.enabled)
        elif offset == 0x04:
            return self.tx_count
        elif offset == 0x08:
            return self.rx_count
        elif offset == 0x0C:
            return len(self.rx_labels)
        elif offset == 0x10:
            if self.rx_labels:
                return self.rx_labels.popleft()
        return 0

    def write_reg(self, offset: int, val: int):
        if offset == 0x00:
            self.enabled = bool(val & 1)
        elif offset == 0x10:
            self.tx_labels.append(val)
            self.tx_count += 1


class MIL1553Bus(BusBase):
    """MIL-STD-1553 military data bus."""

    def __init__(self, name: str = 'mil1553_0', base_addr: int = 0x40300500):
        super().__init__(name, base_addr)
        self.rt_address = 1
        self.messages: deque = deque(maxlen=64)
        self.mode = 'rt'
        self.tx_count = 0
        self.rx_count = 0
        self.bus_a_active = True

    def send_command(self, rt_addr: int, subaddr: int, data: list):
        msg = {'rt': rt_addr, 'sa': subaddr, 'data': data, 'word_count': len(data)}
        self.messages.append(msg)
        self.tx_count += 1

    def read_reg(self, offset: int) -> int:
        if offset == 0x00:
            return self.rt_address
        elif offset == 0x04:
            return self.tx_count
        elif offset == 0x08:
            return self.rx_count
        elif offset == 0x0C:
            return int(self.bus_a_active)
        return 0

    def write_reg(self, offset: int, val: int):
        if offset == 0x00:
            self.rt_address = val & 0x1F
        elif offset == 0x0C:
            self.bus_a_active = bool(val & 1)
