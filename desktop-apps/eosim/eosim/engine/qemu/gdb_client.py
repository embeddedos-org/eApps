# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""GDB Remote Serial Protocol client — shared by QEMU and OpenOCD.

Implements the GDB RSP protocol for register/memory access, breakpoints,
and execution control. Works with any GDB server (QEMU -gdb, OpenOCD, etc.).
"""
import socket
import re
from typing import Optional, List, Dict


class GDBError(Exception):
    """GDB protocol or communication error."""


# ARM register layout (r0-r15 + cpsr)
ARM_REG_NAMES = [f'r{i}' for i in range(16)] + ['cpsr']
ARM_REG_SIZE = 4  # bytes per register

# AArch64 register layout (x0-x30 + sp + pc + cpsr)
AARCH64_REG_NAMES = [f'x{i}' for i in range(31)] + ['sp', 'pc', 'cpsr']
AARCH64_REG_SIZE = 8


class GDBRemoteClient:
    """GDB Remote Serial Protocol client for register/memory access and control.

    Protocol: https://sourceware.org/gdb/current/onlinedocs/gdb/Remote-Protocol.html
    Supports both QEMU GDB stub and OpenOCD GDB server.
    """

    def __init__(self, arch: str = 'arm'):
        self._sock: Optional[socket.socket] = None
        self._connected = False
        self._arch = arch
        self._reg_names = ARM_REG_NAMES if arch in ('arm', 'arm32') else AARCH64_REG_NAMES
        self._reg_size = ARM_REG_SIZE if arch in ('arm', 'arm32') else AARCH64_REG_SIZE
        self._no_ack_mode = False

    def connect(self, host: str = 'localhost', port: int = 1234, timeout: float = 5.0):
        """Connect to GDB server."""
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.settimeout(timeout)
        self._sock.connect((host, port))
        self._connected = True
        try:
            self._send_packet('QStartNoAckMode')
            resp = self._recv_packet()
            if resp == 'OK':
                self._no_ack_mode = True
        except Exception:
            pass

    # --- Packet framing ---

    @staticmethod
    def _checksum(data: str) -> int:
        return sum(ord(c) for c in data) & 0xFF

    def _send_packet(self, data: str):
        cs = self._checksum(data)
        packet = f'${data}#{cs:02x}'
        self._sock.sendall(packet.encode('ascii'))

    def _recv_packet(self) -> str:
        buf = b''
        while True:
            c = self._sock.recv(1)
            if not c:
                raise GDBError("Connection closed")
            if c == b'$':
                break
            if c == b'+':
                continue
        while True:
            c = self._sock.recv(1)
            if not c:
                raise GDBError("Connection closed")
            if c == b'#':
                self._sock.recv(2)  # checksum
                break
            buf += c
        if not self._no_ack_mode:
            self._sock.sendall(b'+')
        return buf.decode('ascii', errors='replace')

    def _command(self, cmd: str) -> str:
        self._send_packet(cmd)
        return self._recv_packet()

    # --- Register access ---

    def read_all_registers(self) -> Dict[str, int]:
        """Read all CPU registers. Returns dict of name→value."""
        resp = self._command('g')
        if not resp or resp.startswith('E'):
            raise GDBError(f"Register read failed: {resp}")
        regs = {}
        hex_per_reg = self._reg_size * 2
        for i, name in enumerate(self._reg_names):
            offset = i * hex_per_reg
            if offset + hex_per_reg > len(resp):
                break
            hex_val = resp[offset:offset + hex_per_reg]
            val = int.from_bytes(bytes.fromhex(hex_val), 'little')
            regs[name] = val
        return regs

    def read_register(self, index: int) -> int:
        """Read a single register by index."""
        resp = self._command(f'p{index:x}')
        if not resp or resp.startswith('E'):
            raise GDBError(f"Register read failed: {resp}")
        return int.from_bytes(bytes.fromhex(resp), 'little')

    def write_register(self, index: int, value: int):
        """Write a single register by index."""
        hex_val = value.to_bytes(self._reg_size, 'little').hex()
        resp = self._command(f'P{index:x}={hex_val}')
        if resp != 'OK':
            raise GDBError(f"Register write failed: {resp}")

    # --- Memory access ---

    def read_memory(self, addr: int, length: int) -> bytes:
        """Read memory at address. Returns bytes."""
        resp = self._command(f'm{addr:x},{length:x}')
        if not resp or resp.startswith('E'):
            raise GDBError(f"Memory read failed: {resp}")
        return bytes.fromhex(resp)

    def write_memory(self, addr: int, data: bytes):
        """Write memory at address."""
        hex_data = data.hex()
        resp = self._command(f'M{addr:x},{len(data):x}:{hex_data}')
        if resp != 'OK':
            raise GDBError(f"Memory write failed: {resp}")

    # --- Breakpoints ---

    def set_breakpoint(self, addr: int, kind: int = 4) -> bool:
        """Set a software breakpoint at addr."""
        resp = self._command(f'Z0,{addr:x},{kind:x}')
        return resp == 'OK'

    def clear_breakpoint(self, addr: int, kind: int = 4) -> bool:
        """Clear a software breakpoint at addr."""
        resp = self._command(f'z0,{addr:x},{kind:x}')
        return resp == 'OK'

    def set_watchpoint(self, addr: int, length: int = 4,
                       wp_type: str = 'write') -> bool:
        """Set a watchpoint. wp_type: 'write', 'read', or 'access'."""
        type_map = {'write': '2', 'read': '3', 'access': '4'}
        ztype = type_map.get(wp_type, '2')
        resp = self._command(f'Z{ztype},{addr:x},{length:x}')
        return resp == 'OK'

    def clear_watchpoint(self, addr: int, length: int = 4,
                         wp_type: str = 'write') -> bool:
        """Clear a watchpoint."""
        type_map = {'write': '2', 'read': '3', 'access': '4'}
        ztype = type_map.get(wp_type, '2')
        resp = self._command(f'z{ztype},{addr:x},{length:x}')
        return resp == 'OK'

    # --- Execution control ---

    def step(self) -> str:
        """Single-step one instruction. Returns stop reason."""
        return self._command('s')

    def continue_execution(self) -> str:
        """Continue execution. Blocks until target stops."""
        return self._command('c')

    def halt(self) -> str:
        """Interrupt a running target."""
        self._sock.sendall(b'\x03')
        return self._recv_packet()

    # --- Target info ---

    def get_thread_info(self) -> List[str]:
        """Get thread/CPU list."""
        threads = []
        resp = self._command('qfThreadInfo')
        while resp and resp != 'l':
            if resp.startswith('m'):
                threads.extend(resp[1:].split(','))
            resp = self._command('qsThreadInfo')
        return threads

    def get_target_description(self) -> str:
        """Read target description XML."""
        resp = self._command('qXfer:features:read:target.xml:0,ffff')
        if resp.startswith('l'):
            return resp[1:]
        elif resp.startswith('m'):
            data = resp[1:]
            while True:
                resp = self._command(
                    f'qXfer:features:read:target.xml:{len(data):x},ffff')
                if resp.startswith('l'):
                    data += resp[1:]
                    break
                elif resp.startswith('m'):
                    data += resp[1:]
                else:
                    break
            return data
        return ''

    def detach(self):
        """Detach from target."""
        try:
            self._command('D')
        except Exception:
            pass

    # --- Lifecycle ---

    @property
    def connected(self) -> bool:
        return self._connected

    @property
    def arch(self) -> str:
        return self._arch

    @property
    def register_names(self) -> List[str]:
        return list(self._reg_names)

    def disconnect(self):
        """Close GDB connection."""
        self._connected = False
        if self._sock:
            try:
                self.detach()
                self._sock.close()
            except Exception:
                pass
            self._sock = None
