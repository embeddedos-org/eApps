# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""OpenOCD manager — launch and manage OpenOCD subprocess for HIL.

Manages OpenOCD lifecycle, adapter/target configuration, firmware flashing,
and target control via TCL commands or GDB bridge.
"""
import os
import shutil
import subprocess
import time
from typing import Optional, List


ADAPTER_CONFIGS = {
    'stlink': 'interface/stlink.cfg',
    'stlink-v2': 'interface/stlink-v2.cfg',
    'stlink-v3': 'interface/stlink-v2-1.cfg',
    'jlink': 'interface/jlink.cfg',
    'cmsis-dap': 'interface/cmsis-dap.cfg',
    'ftdi': 'interface/ftdi/olimex-arm-usb-ocd-h.cfg',
}

TARGET_CONFIGS = {
    'stm32f4': 'target/stm32f4x.cfg',
    'stm32f7': 'target/stm32f7x.cfg',
    'stm32h7': 'target/stm32h7x.cfg',
    'stm32l4': 'target/stm32l4x.cfg',
    'nrf52': 'target/nrf52.cfg',
    'nrf5340': 'target/nrf5340.cfg',
    'nrf9160': 'target/nrf9160.cfg',
    'esp32': 'target/esp32.cfg',
    'samd21': 'target/atsame5x.cfg',
    'psoc6': 'target/psoc6.cfg',
    'rp2040': 'target/rp2040.cfg',
    'lpc55': 'target/lpc55xx.cfg',
    'imx8m': 'target/imx8m.cfg',
    'k64f': 'target/klx.cfg',
}


class OpenOCDError(Exception):
    """OpenOCD launch or communication error."""


class OpenOCDManager:
    """Manages OpenOCD subprocess for hardware-in-the-loop debugging.

    Launches OpenOCD with the correct adapter and target config,
    provides firmware flashing, target halt/resume, and GDB port info.
    """

    def __init__(self):
        self._process: Optional[subprocess.Popen] = None
        self._gdb_port: int = 3333
        self._tcl_port: int = 6666
        self._telnet_port: int = 4444
        self._adapter: str = ''
        self._target: str = ''
        self._openocd_path: str = ''

    @staticmethod
    def find_openocd() -> str:
        """Find OpenOCD binary on the system."""
        path = shutil.which('openocd')
        if path:
            return path
        common_paths = [
            '/usr/local/bin/openocd',
            '/usr/bin/openocd',
            'C:\\Program Files\\OpenOCD\\bin\\openocd.exe',
            'C:\\OpenOCD\\bin\\openocd.exe',
        ]
        for p in common_paths:
            if os.path.isfile(p):
                return p
        return ''

    @staticmethod
    def available() -> bool:
        """Check if OpenOCD is available."""
        return bool(OpenOCDManager.find_openocd())

    def launch(self, adapter: str = 'stlink', target: str = 'stm32f4',
               gdb_port: int = 3333, extra_args: List[str] = None) -> bool:
        """Launch OpenOCD with the specified adapter and target config."""
        openocd = self.find_openocd()
        if not openocd:
            raise OpenOCDError(
                "OpenOCD not found. Install from https://openocd.org/")

        adapter_cfg = ADAPTER_CONFIGS.get(adapter, adapter)
        target_cfg = TARGET_CONFIGS.get(target, target)
        self._adapter = adapter
        self._target = target
        self._gdb_port = gdb_port
        self._openocd_path = openocd

        cmd = [
            openocd,
            '-f', adapter_cfg,
            '-f', target_cfg,
            '-c', f'gdb_port {gdb_port}',
            '-c', f'tcl_port {self._tcl_port}',
            '-c', f'telnet_port {self._telnet_port}',
        ]
        if extra_args:
            cmd.extend(extra_args)

        try:
            self._process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True,
            )
            time.sleep(1.5)
            if self._process.poll() is not None:
                stderr = (
                    self._process.stderr.read()
                    if self._process.stderr else '')
                raise OpenOCDError(
                    f"OpenOCD exited immediately: {stderr[:500]}")
            return True
        except FileNotFoundError:
            raise OpenOCDError(f"OpenOCD binary not found: {openocd}")

    def flash(self, firmware_path: str, verify: bool = True) -> bool:
        """Flash firmware to the target via OpenOCD."""
        if not os.path.isfile(firmware_path):
            raise OpenOCDError(f"Firmware file not found: {firmware_path}")
        # verify_image step omitted for now
        tcl_cmd = (
            f'program {firmware_path} verify reset exit'
            if verify else
            f'program {firmware_path} reset exit'
        )
        openocd = self._openocd_path or self.find_openocd()
        adapter_cfg = ADAPTER_CONFIGS.get(self._adapter, self._adapter)
        target_cfg = TARGET_CONFIGS.get(self._target, self._target)
        cmd = [
            openocd, '-f', adapter_cfg, '-f', target_cfg,
            '-c', 'init', '-c', tcl_cmd,
        ]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60)
        return result.returncode == 0

    def halt(self) -> bool:
        """Halt the target CPU."""
        return self._tcl_command('halt')

    def resume(self) -> bool:
        """Resume target execution."""
        return self._tcl_command('resume')

    def reset(self) -> bool:
        """Reset the target."""
        return self._tcl_command('reset run')

    def reset_halt(self) -> bool:
        """Reset and halt the target."""
        return self._tcl_command('reset halt')

    def _tcl_command(self, command: str) -> bool:
        """Send a TCL command to OpenOCD via the TCL port."""
        import socket
        try:
            addr = ('localhost', self._tcl_port)
            with socket.create_connection(addr, timeout=5) as s:
                s.sendall((command + '\x1a').encode())
                _ = s.recv(4096).decode(errors='replace')
                return True
        except Exception:
            return False

    @property
    def gdb_port(self) -> int:
        return self._gdb_port

    @property
    def is_running(self) -> bool:
        return self._process is not None and self._process.poll() is None

    def get_status(self) -> dict:
        return {
            'running': self.is_running,
            'adapter': self._adapter,
            'target': self._target,
            'gdb_port': self._gdb_port,
            'pid': self._process.pid if self._process else None,
        }

    def stop(self):
        """Terminate OpenOCD subprocess."""
        if self._process:
            try:
                self._process.terminate()
                self._process.wait(timeout=5)
            except Exception:
                try:
                    self._process.kill()
                except Exception:
                    pass
            self._process = None
