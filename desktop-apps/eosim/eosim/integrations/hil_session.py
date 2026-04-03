# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""HIL session orchestrator — composes OpenOCD, GDB, serial bridge.

Provides a unified API for starting a hardware-in-the-loop session
that connects to a real development board.
"""


class HILSession:
    """Hardware-in-the-loop session orchestrating OpenOCD + GDB + serial.

    Composes OpenOCDManager, GDBRemoteClient, SerialBridge, and
    TargetStateBridge into a single session lifecycle.
    """

    def __init__(self):
        self._openocd = None
        self._gdb = None
        self._serial = None
        self._bridge = None
        self._config = {}
        self._connected = False

    def start(self, adapter: str = 'stlink', target: str = 'stm32f4',
              serial_port: str = '', baudrate: int = 115200,
              gdb_port: int = 3333, arch: str = 'arm'):
        """Start a full HIL session: OpenOCD → GDB → serial → state bridge."""
        from eosim.integrations.openocd import OpenOCDManager
        from eosim.engine.qemu.gdb_client import GDBRemoteClient
        from eosim.integrations.serial_bridge import SerialBridge
        from eosim.engine.qemu.state_bridge import TargetStateBridge

        self._config = {
            'adapter': adapter, 'target': target,
            'serial_port': serial_port, 'baudrate': baudrate,
            'gdb_port': gdb_port, 'arch': arch,
        }

        self._openocd = OpenOCDManager()
        self._openocd.launch(adapter=adapter, target=target, gdb_port=gdb_port)

        self._gdb = GDBRemoteClient(arch=arch)
        self._gdb.connect(port=gdb_port)

        self._bridge = TargetStateBridge(gdb_client=self._gdb)

        if serial_port:
            self._serial = SerialBridge()
            self._serial.connect(serial_port, baudrate)
            self._serial.start_reading()

        self._connected = True

    def flash(self, firmware_path: str) -> bool:
        """Flash firmware to the target."""
        if not self._openocd:
            return False
        return self._openocd.flash(firmware_path)

    def halt(self):
        """Halt the target CPU."""
        if self._openocd:
            self._openocd.halt()

    def resume(self):
        """Resume target execution."""
        if self._openocd:
            self._openocd.resume()

    def reset(self):
        """Reset the target."""
        if self._openocd:
            self._openocd.reset()

    def read_registers(self) -> dict:
        """Read CPU registers via GDB."""
        if self._bridge:
            return self._bridge.read_registers()
        return {}

    def read_memory(self, addr: int, length: int) -> bytes:
        """Read target memory via GDB."""
        if self._bridge:
            return self._bridge.read_memory(addr, length)
        return b''

    def set_serial_callback(self, callback):
        """Set callback for serial data received from hardware."""
        if self._serial:
            self._serial.set_on_receive(callback)

    def send_serial(self, data: str):
        """Send data to hardware via serial."""
        if self._serial:
            self._serial.write(data)

    def get_state(self) -> dict:
        """Get combined HIL session state."""
        state = dict(self._config)
        state['connected'] = self._connected
        if self._openocd:
            state['openocd'] = self._openocd.get_status()
        if self._gdb:
            state['gdb_connected'] = self._gdb.connected
            state['registers'] = (
                self._bridge.last_registers if self._bridge else {})
        if self._serial:
            state['serial_connected'] = self._serial.is_connected
        return state

    @property
    def gdb_client(self):
        return self._gdb

    @property
    def state_bridge(self):
        return self._bridge

    @property
    def serial_bridge(self):
        return self._serial

    @property
    def openocd(self):
        return self._openocd

    @property
    def connected(self) -> bool:
        return self._connected

    def stop(self):
        """Stop the HIL session and clean up all resources."""
        self._connected = False
        if self._bridge:
            self._bridge.stop_polling()
        if self._serial:
            self._serial.disconnect()
        if self._gdb:
            self._gdb.disconnect()
        if self._openocd:
            self._openocd.stop()
        self._openocd = None
        self._gdb = None
        self._serial = None
        self._bridge = None
