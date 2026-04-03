# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
from dataclasses import dataclass, field
from typing import Optional, Callable

@dataclass
class CPUState:
    arch: str = 'arm64'
    regs: list = field(default_factory=lambda: [0] * 32)
    pc: int = 0
    sp: int = 0
    lr: int = 0
    cpsr: int = 0
    halted: bool = False
    cycles: int = 0
    irq_enabled: bool = True
    mode: str = 'supervisor'

    def reset(self, entry_point: int = 0, stack_top: int = 0x20000000):
        self.regs = [0] * 32
        self.pc = entry_point
        self.sp = stack_top
        self.lr = 0
        self.cpsr = 0
        self.halted = False
        self.cycles = 0
        self.mode = 'supervisor'

    def dump(self) -> str:
        lines = ['CPU State (%s):' % self.arch]
        lines.append('  PC: 0x%08X  SP: 0x%08X  LR: 0x%08X' % (self.pc, self.sp, self.lr))
        lines.append('  CPSR: 0x%08X  Mode: %s  Cycles: %d' % (self.cpsr, self.mode, self.cycles))
        for i in range(0, min(16, len(self.regs)), 4):
            lines.append('  R%-2d: 0x%08X  R%-2d: 0x%08X  R%-2d: 0x%08X  R%-2d: 0x%08X' % (
                i, self.regs[i], i+1, self.regs[i+1], i+2, self.regs[i+2], i+3, self.regs[i+3]))
        return '\n'.join(lines)

class CPUSimulator:
    def __init__(self, arch: str = 'arm64'):
        self.state = CPUState(arch=arch)
        self.memory = None  # set by VirtualMachine
        self.breakpoints: set = set()
        self.watchpoints: set = set()
        self.trace_log: list = []
        self.max_instructions: int = 1000000
        self.on_syscall: Optional[Callable] = None
        self.on_halt: Optional[Callable] = None

    def reset(self, entry: int = 0, stack: int = 0x20000000):
        self.state.reset(entry, stack)
        self.trace_log.clear()

    def step(self) -> bool:
        if self.state.halted:
            return False
        if self.state.pc in self.breakpoints:
            self.state.halted = True
            return False
        if self.memory:
            instr = self.memory.read32(self.state.pc)
            self._execute(instr)
        self.state.pc += 4
        self.state.cycles += 1
        if self.state.cycles >= self.max_instructions:
            self.state.halted = True
        return not self.state.halted

    def run(self, max_cycles: int = 0) -> int:
        limit = max_cycles if max_cycles > 0 else self.max_instructions
        executed = 0
        while not self.state.halted and executed < limit:
            if not self.step():
                break
            executed += 1
        return executed

    def _execute(self, instr: int):
        # Instruction decoder — handles common patterns
        if instr == 0:  # NOP or uninitialized
            pass
        elif instr == 0xE12FFF1E:  # BX LR (ARM return)
            self.state.pc = self.state.lr - 4
        elif instr == 0xEF000000:  # SVC 0 (syscall)
            if self.on_syscall:
                self.on_syscall(self.state)
        elif instr == 0xE7FFDEFE:  # UDF (halt/breakpoint)
            self.state.halted = True
            if self.on_halt: self.on_halt(self.state)
        elif (instr & 0xFF000000) == 0xEA000000:  # B (branch)
            offset = instr & 0x00FFFFFF
            if offset & 0x800000: offset |= 0xFF000000  # sign extend
            self.state.pc += (offset << 2)
        elif (instr & 0xFFF00000) == 0xE3A00000:  # MOV Rd, imm (ARM)
            rd = (instr >> 12) & 0xF
            imm = instr & 0xFF
            rot = ((instr >> 8) & 0xF) * 2
            val = ((imm >> rot) | (imm << (32 - rot))) & 0xFFFFFFFF if rot else imm
            self.state.regs[rd] = val
        elif (instr & 0xFE1F0000) == 0xE41F0000:  # LDR from memory
            rd = (instr >> 12) & 0xF
            addr = self.state.pc + 8 + (instr & 0xFFF)
            if self.memory:
                self.state.regs[rd] = self.memory.read32(addr)
        elif (instr & 0xFE1F0000) == 0xE40F0000:  # STR to memory
            rd = (instr >> 12) & 0xF
            addr = self.state.pc + 8 + (instr & 0xFFF)
            if self.memory:
                self.memory.write32(addr, self.state.regs[rd])
        # More instructions can be added for each architecture
        self.trace_log.append((self.state.pc, instr, self.state.cycles))