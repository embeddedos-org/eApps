# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
import time, threading
from typing import Callable, Optional, List

class UARTDevice:
    def __init__(self, name: str = 'uart0', base_addr: int = 0x40000000):
        self.name = name
        self.base = base_addr
        self.tx_buffer: list = []
        self.rx_buffer: list = []
        self.baud = 115200
        self.enabled = False
        self.on_tx: Optional[Callable] = None
        self.output_log: list = []

    def write_reg(self, offset: int, val: int):
        if offset == 0x00:  # TX data register
            ch = chr(val & 0x7F)
            self.tx_buffer.append(ch)
            self.output_log.append(ch)
            if self.on_tx:
                self.on_tx(ch)
        elif offset == 0x04:  # Control register
            self.enabled = bool(val & 1)
        elif offset == 0x08:  # Baud register
            self.baud = val

    def read_reg(self, offset: int) -> int:
        if offset == 0x00:  # RX data register
            return self.rx_buffer.pop(0) if self.rx_buffer else 0
        elif offset == 0x04:  # Status register
            status = 0
            if self.rx_buffer: status |= 1  # RX ready
            status |= 2  # TX ready
            if self.enabled: status |= 4
            return status
        return 0

    def inject_input(self, data: str):
        for ch in data:
            self.rx_buffer.append(ord(ch))

    def get_output(self) -> str:
        return ''.join(self.output_log)

    def io_handler(self, op: str, addr: int, val: int) -> int:
        offset = addr - self.base
        if 'read' in op:
            return self.read_reg(offset)
        else:
            self.write_reg(offset, val)
            return 0

class GPIODevice:
    def __init__(self, name: str = 'gpio0', base_addr: int = 0x40010000, pins: int = 32):
        self.name = name
        self.base = base_addr
        self.pin_count = pins
        self.direction = 0  # bitmask: 1=output
        self.output_val = 0
        self.input_val = 0
        self.irq_mask = 0
        self.irq_pending = 0

    def write_reg(self, offset: int, val: int):
        if offset == 0x00: self.direction = val
        elif offset == 0x04: self.output_val = val
        elif offset == 0x08: self.irq_mask = val
        elif offset == 0x0C: self.irq_pending &= ~val  # clear on write

    def read_reg(self, offset: int) -> int:
        if offset == 0x00: return self.direction
        elif offset == 0x04: return self.output_val
        elif offset == 0x08: return self.input_val
        elif offset == 0x0C: return self.irq_pending
        return 0

    def set_input(self, pin: int, value: bool):
        if value: self.input_val |= (1 << pin)
        else: self.input_val &= ~(1 << pin)
        if self.irq_mask & (1 << pin):
            self.irq_pending |= (1 << pin)

    def io_handler(self, op: str, addr: int, val: int) -> int:
        offset = addr - self.base
        if 'read' in op: return self.read_reg(offset)
        else: self.write_reg(offset, val); return 0

class TimerDevice:
    def __init__(self, name: str = 'timer0', base_addr: int = 0x40020000):
        self.name = name
        self.base = base_addr
        self.counter = 0
        self.reload_val = 0
        self.prescaler = 1
        self.enabled = False
        self.irq_enabled = False
        self.irq_pending = False
        self.on_irq: Optional[Callable] = None

    def write_reg(self, offset: int, val: int):
        if offset == 0x00: self.reload_val = val; self.counter = val
        elif offset == 0x04:
            self.enabled = bool(val & 1)
            self.irq_enabled = bool(val & 2)
        elif offset == 0x08: self.prescaler = max(1, val)
        elif offset == 0x0C: self.irq_pending = False

    def read_reg(self, offset: int) -> int:
        if offset == 0x00: return self.counter
        elif offset == 0x04: return (int(self.enabled) | (int(self.irq_enabled) << 1))
        elif offset == 0x08: return self.prescaler
        elif offset == 0x0C: return int(self.irq_pending)
        return 0

    def tick(self):
        if not self.enabled: return
        self.counter -= 1
        if self.counter <= 0:
            self.counter = self.reload_val
            if self.irq_enabled:
                self.irq_pending = True
                if self.on_irq: self.on_irq()

    def io_handler(self, op: str, addr: int, val: int) -> int:
        offset = addr - self.base
        if 'read' in op: return self.read_reg(offset)
        else: self.write_reg(offset, val); return 0

class SPIDevice:
    def __init__(self, name: str = 'spi0', base_addr: int = 0x40030000):
        self.name = name
        self.base = base_addr
        self.tx_data = 0
        self.rx_data = 0
        self.clock_div = 1
        self.enabled = False
        self.transfer_complete = False
        self.slave_select = 0xFF

    def write_reg(self, offset: int, val: int):
        if offset == 0x00: self.tx_data = val; self.transfer_complete = True; self.rx_data = val ^ 0xFF
        elif offset == 0x04: self.enabled = bool(val & 1)
        elif offset == 0x08: self.clock_div = max(1, val)
        elif offset == 0x0C: self.slave_select = val

    def read_reg(self, offset: int) -> int:
        if offset == 0x00: self.transfer_complete = False; return self.rx_data
        elif offset == 0x04: return int(self.enabled) | (int(self.transfer_complete) << 1)
        return 0

    def io_handler(self, op: str, addr: int, val: int) -> int:
        offset = addr - self.base
        if 'read' in op: return self.read_reg(offset)
        else: self.write_reg(offset, val); return 0

class I2CDevice:
    def __init__(self, name: str = 'i2c0', base_addr: int = 0x40040000):
        self.name = name
        self.base = base_addr
        self.slave_addr = 0
        self.tx_data = 0
        self.rx_data = 0
        self.status = 0
        self.enabled = False
        self.slaves: dict = {}

    def add_slave(self, addr: int, handler: Callable):
        self.slaves[addr] = handler

    def write_reg(self, offset: int, val: int):
        if offset == 0x00: self.slave_addr = val & 0x7F
        elif offset == 0x04:
            self.tx_data = val
            if self.slave_addr in self.slaves:
                self.rx_data = self.slaves[self.slave_addr](val)
                self.status = 1  # ACK
            else:
                self.status = 2  # NACK
        elif offset == 0x08: self.enabled = bool(val & 1)

    def read_reg(self, offset: int) -> int:
        if offset == 0x00: return self.slave_addr
        elif offset == 0x04: return self.rx_data
        elif offset == 0x08: return self.status
        return 0

    def io_handler(self, op: str, addr: int, val: int) -> int:
        offset = addr - self.base
        if 'read' in op: return self.read_reg(offset)
        else: self.write_reg(offset, val); return 0

class InterruptController:
    def __init__(self, name: str = 'nvic', base_addr: int = 0xE000E000, irq_count: int = 64):
        self.name = name
        self.base = base_addr
        self.irq_count = irq_count
        self.enabled = [False] * irq_count
        self.pending = [False] * irq_count
        self.priority = [0] * irq_count
        self.handlers: dict = {}

    def enable_irq(self, irq: int):
        if 0 <= irq < self.irq_count: self.enabled[irq] = True

    def disable_irq(self, irq: int):
        if 0 <= irq < self.irq_count: self.enabled[irq] = False

    def trigger(self, irq: int):
        if 0 <= irq < self.irq_count and self.enabled[irq]:
            self.pending[irq] = True

    def acknowledge(self, irq: int):
        if 0 <= irq < self.irq_count: self.pending[irq] = False

    def get_highest_pending(self) -> int:
        best = -1
        best_prio = 256
        for i in range(self.irq_count):
            if self.pending[i] and self.enabled[i] and self.priority[i] < best_prio:
                best = i
                best_prio = self.priority[i]
        return best