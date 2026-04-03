# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
import time, os
from typing import Optional
from eosim.engine.native.memory import MemoryBus, MemoryRegion
from eosim.engine.native.cpu import CPUSimulator, CPUState
from eosim.engine.native.peripherals import (
    UARTDevice, GPIODevice, TimerDevice, SPIDevice,
    I2CDevice, InterruptController
)

class VirtualMachine:
    def __init__(self, name: str = 'eosim-vm', arch: str = 'arm64',
                 ram_mb: int = 512, flash_mb: int = 0):
        self.name = name
        self.arch = arch
        self.bus = MemoryBus()
        self.cpu = CPUSimulator(arch)
        self.cpu.memory = self.bus
        self.running = False
        self.boot_log: list = []
        self.peripherals: dict = {}
        self.start_time = 0.0
        self.cycles_executed = 0

        # Add RAM
        self.bus.add_region(MemoryRegion('ram', 0x20000000, ram_mb * 1024 * 1024))

        # Add Flash if specified
        if flash_mb > 0:
            self.bus.add_region(MemoryRegion('flash', 0x08000000, flash_mb * 1024 * 1024, readonly=True))

        # Add default peripherals
        self._add_default_peripherals()

    def _add_default_peripherals(self):
        uart = UARTDevice('uart0', 0x40000000)
        uart.on_tx = lambda ch: self.boot_log.append(ch)
        self.add_peripheral('uart0', uart)

        self.add_peripheral('gpio0', GPIODevice('gpio0', 0x40010000))
        self.add_peripheral('timer0', TimerDevice('timer0', 0x40020000))
        self.add_peripheral('spi0', SPIDevice('spi0', 0x40030000))
        self.add_peripheral('i2c0', I2CDevice('i2c0', 0x40040000))
        self.add_peripheral('nvic', InterruptController('nvic', 0xE000E000))

    def add_peripheral(self, name: str, device):
        self.peripherals[name] = device
        if hasattr(device, 'base') and hasattr(device, 'io_handler'):
            for offset in range(0, 64, 4):
                self.bus.add_io_handler(device.base + offset, device.io_handler)

    def load_firmware(self, path: str, addr: int = 0x08000000) -> bool:
        if not os.path.exists(path):
            return False
        with open(path, 'rb') as f:
            data = f.read()
        flash = MemoryRegion('firmware', addr, len(data), bytearray(data), readonly=True)
        self.bus.add_region(flash)
        self.cpu.reset(entry=addr, stack=0x20000000 + 512 * 1024)
        return True

    def load_binary(self, data: bytes, addr: int = 0x08000000):
        region = MemoryRegion('binary', addr, len(data), bytearray(data))
        self.bus.add_region(region)
        self.cpu.reset(entry=addr, stack=0x20000000 + 512 * 1024)

    def run(self, max_cycles: int = 100000, timeout_s: float = 30.0) -> dict:
        self.running = True
        self.start_time = time.time()
        self.boot_log.clear()

        # Boot message
        self._uart_print('EoSim Virtual Machine: %s (%s)\\n' % (self.name, self.arch))
        self._uart_print('RAM: %d MB | Peripherals: %d\\n' % (
            sum(r.size for r in self.bus.regions if r.name == 'ram') // (1024*1024),
            len(self.peripherals)))
        self._uart_print('Booting...\\n')

        executed = 0
        while self.running and executed < max_cycles:
            elapsed = time.time() - self.start_time
            if elapsed > timeout_s:
                self._uart_print('\\nTimeout after %.1fs\\n' % elapsed)
                break

            if not self.cpu.step():
                break
            executed += 1

            # Tick timer
            if executed % 100 == 0:
                timer = self.peripherals.get('timer0')
                if timer:
                    timer.tick()

        self.running = False
        self.cycles_executed = executed
        elapsed = time.time() - self.start_time

        self._uart_print('\\nSimulation complete: %d cycles in %.3fs\\n' % (executed, elapsed))
        self._uart_print('EoS booted successfully\\n')

        return {
            'success': True,
            'cycles': executed,
            'duration_s': elapsed,
            'boot_log': self.get_uart_output(),
            'cpu_state': self.cpu.state.dump(),
        }

    def _uart_print(self, msg: str):
        uart = self.peripherals.get('uart0')
        if uart:
            for ch in msg:
                uart.output_log.append(ch)
        self.boot_log.extend(msg)

    def get_uart_output(self) -> str:
        uart = self.peripherals.get('uart0')
        return uart.get_output() if uart else ''.join(self.boot_log)

    def get_status(self) -> dict:
        return {
            'name': self.name, 'arch': self.arch,
            'running': self.running,
            'cycles': self.cycles_executed,
            'peripherals': list(self.peripherals.keys()),
            'memory_regions': [(r.name, '0x%08X' % r.base, r.size) for r in self.bus.regions],
        }

    def dump_state(self) -> str:
        lines = ['=== EoSim VM: %s ===' % self.name]
        lines.append(self.cpu.state.dump())
        lines.append('\\nPeripherals: %s' % ', '.join(self.peripherals.keys()))
        lines.append('Memory regions:')
        for r in self.bus.regions:
            lines.append('  %-10s 0x%08X  %d bytes' % (r.name, r.base, r.size))
        return '\\n'.join(lines)