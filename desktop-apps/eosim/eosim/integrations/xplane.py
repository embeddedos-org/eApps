# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""X-Plane flight simulator integration — UDP dataref bridge."""
import socket
import struct
from typing import Optional, Dict


class XPlaneConnection:
    """Connect to X-Plane via UDP for dataref get/set and position control.

    X-Plane exposes data on UDP port 49000 by default.
    """

    DEFAULT_HOST = '127.0.0.1'
    DEFAULT_PORT = 49000

    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT):
        self.host = host
        self.port = port
        self._sock: Optional[socket.socket] = None
        self.connected = False
        self._datarefs: Dict[str, float] = {}

    def connect(self, timeout: float = 5.0) -> bool:
        try:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._sock.settimeout(timeout)
            self._sock.connect((self.host, self.port))
            self.connected = True
            return True
        except (socket.error, OSError):
            self.connected = False
            return False

    def disconnect(self):
        if self._sock:
            try:
                self._sock.close()
            except Exception:
                pass
        self._sock = None
        self.connected = False

    def get_dataref(self, path: str) -> Optional[float]:
        return self._datarefs.get(path)

    def set_dataref(self, path: str, value: float):
        if not self.connected or not self._sock:
            return
        try:
            msg = b'DREF\x00'
            msg += struct.pack('<f', value)
            msg += path.encode('ascii').ljust(500, b'\x00')
            self._sock.send(msg)
            self._datarefs[path] = value
        except (socket.error, OSError):
            pass

    def set_position(self, lat: float, lon: float, alt_m: float,
                     pitch: float = 0, roll: float = 0, heading: float = 0):
        if not self.connected or not self._sock:
            return
        try:
            msg = b'POSI\x00'
            msg += struct.pack('<i', 0)  # aircraft index
            msg += struct.pack('<dddffff', lat, lon, alt_m,
                               pitch, roll, heading, 0)
            self._sock.send(msg)
        except (socket.error, OSError):
            pass

    def receive_data(self, timeout: float = 0.1) -> dict:
        if not self._sock:
            return {}
        try:
            self._sock.settimeout(timeout)
            data, _ = self._sock.recvfrom(4096)
            if data[:4] == b'DATA':
                result = {}
                offset = 5
                while offset + 36 <= len(data):
                    idx = struct.unpack_from('<i', data, offset)[0]
                    values = struct.unpack_from('<8f', data, offset + 4)
                    result[idx] = values
                    offset += 36
                return result
        except (socket.timeout, socket.error, OSError):
            pass
        return {}

    def get_status(self) -> dict:
        return {
            'connected': self.connected,
            'host': self.host,
            'port': self.port,
            'datarefs_cached': len(self._datarefs),
        }
