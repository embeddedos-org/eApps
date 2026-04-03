# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
import struct
from dataclasses import dataclass, field
from typing import Dict, Optional, Callable

@dataclass
class MemoryRegion:
    name: str
    base: int
    size: int
    data: bytearray = field(default_factory=bytearray)
    readonly: bool = False
    handler: Optional[Callable] = None

    def __post_init__(self):
        if not self.data:
            self.data = bytearray(self.size)

    def contains(self, addr: int) -> bool:
        return self.base <= addr < self.base + self.size

    def read8(self, addr: int) -> int:
        off = addr - self.base
        if 0 <= off < self.size:
            return self.data[off]
        return 0

    def read32(self, addr: int) -> int:
        off = addr - self.base
        if 0 <= off + 3 < self.size:
            return struct.unpack_from('<I', self.data, off)[0]
        return 0

    def write8(self, addr: int, val: int):
        if self.readonly: return
        off = addr - self.base
        if 0 <= off < self.size:
            self.data[off] = val & 0xFF

    def write32(self, addr: int, val: int):
        if self.readonly: return
        off = addr - self.base
        if 0 <= off + 3 < self.size:
            struct.pack_into('<I', self.data, off, val & 0xFFFFFFFF)

class MemoryBus:
    def __init__(self):
        self.regions: list = []
        self.io_handlers: Dict[int, Callable] = {}

    def add_region(self, region: MemoryRegion):
        self.regions.append(region)
        self.regions.sort(key=lambda r: r.base)

    def add_io_handler(self, addr: int, handler: Callable):
        self.io_handlers[addr] = handler

    def _find_region(self, addr: int) -> Optional[MemoryRegion]:
        for r in self.regions:
            if r.contains(addr):
                return r
        return None

    def read8(self, addr: int) -> int:
        if addr in self.io_handlers:
            return self.io_handlers[addr]('read8', addr, 0)
        r = self._find_region(addr)
        return r.read8(addr) if r else 0

    def read32(self, addr: int) -> int:
        base = addr & ~3
        if base in self.io_handlers:
            return self.io_handlers[base]('read32', addr, 0)
        r = self._find_region(addr)
        return r.read32(addr) if r else 0

    def write8(self, addr: int, val: int):
        if addr in self.io_handlers:
            self.io_handlers[addr]('write8', addr, val)
            return
        r = self._find_region(addr)
        if r: r.write8(addr, val)

    def write32(self, addr: int, val: int):
        base = addr & ~3
        if base in self.io_handlers:
            self.io_handlers[base]('write32', addr, val)
            return
        r = self._find_region(addr)
        if r: r.write32(addr, val)

    def load_binary(self, addr: int, data: bytes):
        for i, b in enumerate(data):
            self.write8(addr + i, b)

    def dump(self, addr: int, size: int) -> str:
        lines = []
        for off in range(0, size, 16):
            hexs = ' '.join('%02x' % self.read8(addr + off + i) for i in range(min(16, size - off)))
            lines.append('%08x: %s' % (addr + off, hexs))
        return '\n'.join(lines)