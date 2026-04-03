# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""QMP (QEMU Machine Protocol) client — JSON-over-socket control of QEMU VMs.

Protocol: https://www.qemu.org/docs/master/interop/qmp-spec.html
Supports TCP and Unix socket connections.
"""
import json
import socket
import threading
import time
from typing import Optional, Dict, Any, Callable, List


class QMPError(Exception):
    """QMP protocol or communication error."""


class QMPClient:
    """Client for QEMU Machine Protocol (QMP).

    Provides VM control (pause/resume/reset), device queries,
    and memory inspection via HMP passthrough.
    """

    def __init__(self):
        self._sock: Optional[socket.socket] = None
        self._connected = False
        self._event_thread: Optional[threading.Thread] = None
        self._event_handlers: Dict[str, List[Callable]] = {}
        self._lock = threading.Lock()
        self._recv_buffer = b''

    def connect_tcp(self, host: str = 'localhost', port: int = 4444, timeout: float = 5.0):
        """Connect to QMP via TCP."""
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.settimeout(timeout)
        self._sock.connect((host, port))
        self._negotiate()

    def connect_unix(self, path: str, timeout: float = 5.0):
        """Connect to QMP via Unix domain socket."""
        self._sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self._sock.settimeout(timeout)
        self._sock.connect(path)
        self._negotiate()

    def _negotiate(self):
        """Read QMP greeting and send qmp_capabilities."""
        greeting = self._recv_json()
        if 'QMP' not in greeting:
            raise QMPError(f"Invalid QMP greeting: {greeting}")
        resp = self.execute('qmp_capabilities')
        if 'error' in resp:
            raise QMPError(f"Capability negotiation failed: {resp}")
        self._connected = True

    def execute(self, command: str, arguments: Dict[str, Any] = None) -> dict:
        """Execute a QMP command and return the response."""
        msg = {'execute': command}
        if arguments:
            msg['arguments'] = arguments
        with self._lock:
            self._send_json(msg)
            return self._recv_response()

    def _send_json(self, obj):
        data = json.dumps(obj).encode('utf-8') + b'\r\n'
        self._sock.sendall(data)

    def _recv_json(self) -> dict:
        while True:
            if b'\n' in self._recv_buffer:
                line, self._recv_buffer = self._recv_buffer.split(b'\n', 1)
                line = line.strip()
                if line:
                    return json.loads(line)
            chunk = self._sock.recv(4096)
            if not chunk:
                raise QMPError("Connection closed")
            self._recv_buffer += chunk

    def _recv_response(self) -> dict:
        while True:
            msg = self._recv_json()
            if 'event' in msg:
                self._dispatch_event(msg)
                continue
            return msg

    # --- VM control commands ---

    def stop(self) -> dict:
        """Pause the VM."""
        return self.execute('stop')

    def cont(self) -> dict:
        """Resume the VM."""
        return self.execute('cont')

    def system_reset(self) -> dict:
        """Reset the VM."""
        return self.execute('system_reset')

    def system_powerdown(self) -> dict:
        """Graceful powerdown."""
        return self.execute('system_powerdown')

    def quit(self) -> dict:
        """Terminate QEMU."""
        return self.execute('quit')

    # --- Query commands ---

    def query_status(self) -> dict:
        """Get VM run state."""
        resp = self.execute('query-status')
        return resp.get('return', {})

    def query_cpus(self) -> list:
        """Get CPU info."""
        resp = self.execute('query-cpus-fast')
        return resp.get('return', [])

    def query_block(self) -> list:
        """Get block device info."""
        resp = self.execute('query-block')
        return resp.get('return', [])

    def query_chardev(self) -> list:
        """Get character device info."""
        resp = self.execute('query-chardev')
        return resp.get('return', [])

    # --- HMP passthrough for memory/register access ---

    def hmp_command(self, command: str) -> str:
        """Execute an HMP (Human Monitor Protocol) command."""
        resp = self.execute('human-monitor-command',
                           {'command-line': command})
        return resp.get('return', '')

    def read_memory(self, addr: int, size: int = 64, fmt: str = 'x') -> str:
        """Read physical memory using HMP xp command."""
        count = size // 4
        return self.hmp_command(f'xp /{count}{fmt} 0x{addr:x}')

    def read_registers(self) -> str:
        """Read CPU registers using HMP info registers."""
        return self.hmp_command('info registers')

    # --- Event handling ---

    def on_event(self, event_name: str, handler: Callable):
        """Register an event handler."""
        self._event_handlers.setdefault(event_name, []).append(handler)

    def _dispatch_event(self, event: dict):
        name = event.get('event', '')
        handlers = self._event_handlers.get(name, [])
        for h in handlers:
            try:
                h(event)
            except Exception:
                pass

    def start_event_listener(self):
        """Start background thread for async QEMU events."""
        if self._event_thread and self._event_thread.is_alive():
            return
        self._event_thread = threading.Thread(
            target=self._event_loop, daemon=True, name='qmp-events')
        self._event_thread.start()

    def _event_loop(self):
        while self._connected:
            try:
                msg = self._recv_json()
                if 'event' in msg:
                    self._dispatch_event(msg)
            except (socket.timeout, OSError):
                time.sleep(0.1)
            except Exception:
                break

    # --- Lifecycle ---

    @property
    def connected(self) -> bool:
        return self._connected

    def disconnect(self):
        """Close QMP connection."""
        self._connected = False
        if self._sock:
            try:
                self._sock.close()
            except Exception:
                pass
            self._sock = None
