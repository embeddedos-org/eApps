# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""QEMU/target state bridge — reads registers/memory from GDB/QMP and
populates CPUState and MemoryBus models for GUI display.

Works with both QEMU GDB stub and OpenOCD GDB server.
"""
import threading
import time
from typing import Optional, Callable


class TargetStateBridge:
    """Bridges remote target state (via GDB) into EoSim's CPUState model.

    Polls the GDB server at a configurable interval and updates
    the CPUState object for GUI display.
    """

    def __init__(self, gdb_client=None, poll_interval: float = 0.1):
        self._gdb = gdb_client
        self._poll_interval = poll_interval
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._cpu_state = None
        self._on_update: Optional[Callable] = None
        self._last_regs = {}
        self._last_pc = 0

    def set_gdb_client(self, gdb_client):
        """Set or replace the GDB client."""
        self._gdb = gdb_client

    def set_cpu_state(self, cpu_state):
        """Set the CPUState object to populate."""
        self._cpu_state = cpu_state

    def set_on_update(self, callback: Callable):
        """Set callback invoked after each state update."""
        self._on_update = callback

    def read_registers(self) -> dict:
        """Read all registers from target. Returns dict of name→value."""
        if not self._gdb or not self._gdb.connected:
            return {}
        try:
            return self._gdb.read_all_registers()
        except Exception:
            return {}

    def read_memory(self, addr: int, length: int) -> bytes:
        """Read memory from target."""
        if not self._gdb or not self._gdb.connected:
            return b''
        try:
            return self._gdb.read_memory(addr, length)
        except Exception:
            return b''

    def update_cpu_state(self):
        """Read registers from target and populate CPUState."""
        regs = self.read_registers()
        if not regs or not self._cpu_state:
            return

        state = self._cpu_state
        arch = self._gdb.arch if self._gdb else 'arm'

        if arch in ('arm', 'arm32'):
            for i in range(16):
                key = f'r{i}'
                if key in regs and i < len(state.regs):
                    state.regs[i] = regs[key]
            state.pc = regs.get('r15', regs.get('pc', state.pc))
            state.sp = regs.get('r13', regs.get('sp', state.sp))
            state.lr = regs.get('r14', regs.get('lr', state.lr))
            state.cpsr = regs.get('cpsr', state.cpsr)
        else:
            for i in range(min(31, len(state.regs))):
                key = f'x{i}'
                if key in regs:
                    state.regs[i] = regs[key]
            state.pc = regs.get('pc', state.pc)
            state.sp = regs.get('sp', state.sp)
            state.cpsr = regs.get('cpsr', state.cpsr)

        self._last_regs = regs
        self._last_pc = state.pc

    def update_memory_bus(self, bus, addr: int = 0x20000000, length: int = 256):
        """Read memory from target and write into MemoryBus model."""
        data = self.read_memory(addr, length)
        if not data or not bus:
            return
        for i, byte in enumerate(data):
            try:
                bus.write8(addr + i, byte)
            except Exception:
                break

    def poll_once(self):
        """Perform a single poll cycle."""
        self.update_cpu_state()
        if self._on_update:
            try:
                self._on_update()
            except Exception:
                pass

    def start_polling(self):
        """Start background polling thread."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(
            target=self._poll_loop, daemon=True, name='state-bridge')
        self._thread.start()

    def stop_polling(self):
        """Stop background polling."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
            self._thread = None

    def _poll_loop(self):
        while self._running:
            self.poll_once()
            time.sleep(self._poll_interval)

    @property
    def last_registers(self) -> dict:
        return dict(self._last_regs)

    @property
    def last_pc(self) -> int:
        return self._last_pc
