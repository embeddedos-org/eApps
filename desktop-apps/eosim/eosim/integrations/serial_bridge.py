# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""Serial bridge — pyserial UART data bridge for hardware-in-the-loop.

Bridges real serial port data between physical hardware and
the EoSim UART terminal / VirtualMachine UART peripheral.
"""
import threading
import time
from typing import Optional, Callable, List

try:
    import serial
    import serial.tools.list_ports
    HAS_SERIAL = True
except ImportError:
    HAS_SERIAL = False


class SerialBridge:
    """Bridges a real serial port to EoSim's UART system.

    Reads from hardware serial, calls on_receive callback
    (feeds UART terminal).
    Writes from UART terminal → sends to hardware serial.
    """

    def __init__(self):
        self._port: Optional[object] = None
        self._read_thread: Optional[threading.Thread] = None
        self._running = False
        self._on_receive: Optional[Callable[[str], None]] = None
        self._port_name = ''
        self._baudrate = 115200

    @staticmethod
    def available() -> bool:
        return HAS_SERIAL

    @staticmethod
    def list_ports() -> List[dict]:
        """Enumerate available serial ports."""
        if not HAS_SERIAL:
            return []
        ports = []
        for p in serial.tools.list_ports.comports():
            ports.append({
                'device': p.device,
                'description': p.description,
                'hwid': p.hwid,
                'vid': p.vid,
                'pid': p.pid,
                'manufacturer': p.manufacturer or '',
            })
        return ports

    @staticmethod
    def detect_dev_boards() -> List[dict]:
        """Detect common development board serial adapters."""
        if not HAS_SERIAL:
            return []
        boards = []
        known = {
            (0x0483, 0x374B): 'ST-Link V2-1 (STM32)',
            (0x0483, 0x3748): 'ST-Link V2 (STM32)',
            (0x0483, 0x3752): 'ST-Link V3 (STM32)',
            (0x1366, 0x0105): 'J-Link (Segger)',
            (0x1366, 0x1015): 'J-Link (Segger)',
            (0x10C4, 0xEA60): 'CP2102 USB-UART',
            (0x0403, 0x6001): 'FTDI FT232R',
            (0x0403, 0x6010): 'FTDI FT2232',
            (0x2E8A, 0x0005): 'Raspberry Pi Pico',
            (0x239A, None): 'Adafruit (CircuitPython)',
        }
        for p in serial.tools.list_ports.comports():
            vid, pid = p.vid, p.pid
            if vid:
                name = known.get((vid, pid))
                if not name:
                    name = known.get((vid, None))
                if name:
                    boards.append({
                        'device': p.device,
                        'board': name,
                        'description': p.description,
                    })
        return boards

    def connect(self, port: str, baudrate: int = 115200, timeout: float = 1.0):
        """Open serial connection."""
        if not HAS_SERIAL:
            raise RuntimeError(
                "pyserial not installed. Run: pip install pyserial")
        self._port = serial.Serial(port, baudrate, timeout=timeout)
        self._port_name = port
        self._baudrate = baudrate

    def set_on_receive(self, callback: Callable[[str], None]):
        """Set callback for received data (feeds UART terminal)."""
        self._on_receive = callback

    def write(self, data: str):
        """Send data to the hardware serial port."""
        if self._port and self._port.is_open:
            self._port.write(data.encode('utf-8', errors='replace'))

    def write_bytes(self, data: bytes):
        """Send raw bytes to the hardware serial port."""
        if self._port and self._port.is_open:
            self._port.write(data)

    def start_reading(self):
        """Start background thread to read from serial port."""
        if self._running:
            return
        self._running = True
        self._read_thread = threading.Thread(
            target=self._read_loop, daemon=True, name='serial-bridge')
        self._read_thread.start()

    def stop_reading(self):
        """Stop background reading."""
        self._running = False
        if self._read_thread:
            self._read_thread.join(timeout=2.0)
            self._read_thread = None

    def _read_loop(self):
        while self._running and self._port and self._port.is_open:
            try:
                data = self._port.read(self._port.in_waiting or 1)
                if data and self._on_receive:
                    text = data.decode('utf-8', errors='replace')
                    self._on_receive(text)
            except Exception:
                time.sleep(0.01)

    def inject_into_vm(self, vm):
        """Bridge serial data into VirtualMachine's UART peripheral."""
        uart = vm.peripherals.get('uart0')
        if uart and hasattr(uart, 'inject_input'):
            self.set_on_receive(lambda text: uart.inject_input(text))

    @property
    def is_connected(self) -> bool:
        return self._port is not None and self._port.is_open

    @property
    def port_name(self) -> str:
        return self._port_name

    def disconnect(self):
        """Close serial connection."""
        self.stop_reading()
        if self._port:
            try:
                self._port.close()
            except Exception:
                pass
            self._port = None
