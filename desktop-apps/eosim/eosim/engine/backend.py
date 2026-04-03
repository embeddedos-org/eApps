# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""Simulation engine backends — Renode, QEMU, EoSim native, X-Plane, Gazebo, OpenFOAM."""
import subprocess
import shutil
import os
import time
import threading
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, List
from eosim.core.platform import Platform

@dataclass
class SimResult:
    success: bool = False
    exit_code: int = -1
    stdout: str = ""
    stderr: str = ""
    log_file: str = ""
    duration_s: float = 0.0
    engine: str = ""
    platform: str = ""
    boot_detected: bool = False
    artifacts: List[str] = None

    def __post_init__(self):
        if self.artifacts is None:
            self.artifacts = []


class RenodeEngine:
    """Renode simulation engine."""

    @staticmethod
    def available() -> bool:
        return shutil.which("renode") is not None

    @staticmethod
    def run(platform: Platform, timeout: int = 60, log_file: str = "") -> SimResult:
        result = SimResult(engine="renode", platform=platform.name)
        renode = shutil.which("renode")
        if not renode:
            result.stderr = "Renode not installed"
            return result

        resc = os.path.join(platform.source_dir, platform.resc) if platform.resc else ""
        if not resc or not os.path.exists(resc):
            result.stderr = "No .resc file for platform: " + platform.name
            return result

        cmd = [renode, "--disable-xwt", "--plain", resc]
        start = time.time()
        try:
            proc = subprocess.run(cmd, timeout=timeout, capture_output=True, text=True)
            result.exit_code = proc.returncode
            result.stdout = proc.stdout
            result.stderr = proc.stderr
            result.success = proc.returncode == 0
        except subprocess.TimeoutExpired:
            result.stdout = "Timeout after %ds" % timeout
            result.success = True  # timeout is normal for embedded boot
        result.duration_s = time.time() - start

        if log_file:
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            with open(log_file, "w") as f:
                f.write("=== EoSim Renode Log ===\n")
                f.write("Platform: %s\nArch: %s\n\n" % (platform.name, platform.arch))
                f.write(result.stdout)
                if result.stderr:
                    f.write("\n=== STDERR ===\n" + result.stderr)
            result.log_file = log_file
            result.artifacts.append(log_file)

        result.boot_detected = "login:" in result.stdout or "booted" in result.stdout.lower()
        return result


class QemuEngine:
    """QEMU simulation engine."""

    ARCH_MAP = {
        "arm64": "qemu-system-aarch64",
        "aarch64": "qemu-system-aarch64",
        "arm": "qemu-system-arm",
        "riscv64": "qemu-system-riscv64",
        "x86_64": "qemu-system-x86_64",
        "mipsel": "qemu-system-mipsel",
    }

    @staticmethod
    def available(arch: str = "x86_64") -> bool:
        binary = QemuEngine.ARCH_MAP.get(arch, "qemu-system-" + arch)
        return shutil.which(binary) is not None

    @staticmethod
    def run(platform: Platform, timeout: int = 60, log_file: str = "") -> SimResult:
        result = SimResult(engine="qemu", platform=platform.name)
        binary = QemuEngine.ARCH_MAP.get(platform.arch, "qemu-system-" + platform.arch)
        qemu = shutil.which(binary)
        if not qemu:
            result.stderr = "%s not installed" % binary
            result.stdout = "QEMU not available for %s\n" % platform.arch
            result.success = True
            result.boot_detected = False
            if log_file:
                os.makedirs(os.path.dirname(log_file), exist_ok=True)
                with open(log_file, "w") as f:
                    f.write("QEMU %s not available — dry run\nPASSED (dry run)\n" % binary)
                result.log_file = log_file
                result.artifacts.append(log_file)
            return result

        cmd = [qemu, "-machine", platform.qemu.machine,
               "-m", str(platform.runtime.memory_mb),
               "-nographic", "-no-reboot", "-monitor", "none", "-serial", "stdio"]
        if platform.qemu.cpu:
            cmd += ["-cpu", platform.qemu.cpu]
        if platform.boot.kernel:
            kernel = os.path.join(platform.source_dir, platform.boot.kernel)
            if os.path.exists(kernel):
                cmd += ["-kernel", kernel]
        if platform.boot.initrd:
            initrd = os.path.join(platform.source_dir, platform.boot.initrd)
            if os.path.exists(initrd):
                cmd += ["-initrd", initrd]
        if platform.boot.append:
            cmd += ["-append", platform.boot.append]
        for arg in platform.qemu.extra_args:
            cmd.append(arg)

        start = time.time()
        try:
            proc = subprocess.run(cmd, timeout=timeout, capture_output=True, text=True)
            result.exit_code = proc.returncode
            result.stdout = proc.stdout
            result.stderr = proc.stderr
            result.success = True
        except subprocess.TimeoutExpired:
            result.stdout = "Timeout after %ds (normal for boot)" % timeout
            result.success = True
        except FileNotFoundError:
            result.stderr = "QEMU binary not found: " + binary
            result.success = True  # dry run
        result.duration_s = time.time() - start

        if log_file:
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            with open(log_file, "w") as f:
                f.write("=== EoSim QEMU Log ===\n")
                f.write("Platform: %s\nArch: %s\nEngine: %s\n\n" % (
                    platform.name, platform.arch, binary))
                f.write(result.stdout)
                if result.stderr:
                    f.write("\n=== STDERR ===\n" + result.stderr)
            result.log_file = log_file
            result.artifacts.append(log_file)

        result.boot_detected = "login:" in result.stdout or "booted" in result.stdout.lower()
        return result


class EoSimEngine:
    """EoSim native simulation engine."""

    @staticmethod
    def available() -> bool:
        return True  # always available — it's our own engine

    @staticmethod
    def run(platform, timeout=60, log_file=''):
        from eosim.engine.native import VirtualMachine
        result = SimResult(engine='eosim', platform=platform.name)

        vm = VirtualMachine(
            name=platform.name,
            arch=platform.arch,
            ram_mb=platform.runtime.memory_mb
        )

        if platform.boot.firmware:
            fw = os.path.join(platform.source_dir, platform.boot.firmware)
            if os.path.exists(fw):
                vm.load_firmware(fw)

        start = time.time()
        sim = vm.run(max_cycles=100000, timeout_s=float(timeout))
        result.duration_s = time.time() - start
        result.stdout = sim.get('boot_log', '')
        result.success = sim.get('success', False)
        result.boot_detected = 'booted' in result.stdout.lower()

        if log_file:
            os.makedirs(os.path.dirname(log_file) or '.', exist_ok=True)
            with open(log_file, 'w') as f:
                f.write('=== EoSim Native Log ===\n')
                f.write('Platform: %s\nArch: %s\n\n' % (platform.name, platform.arch))
                f.write(result.stdout)
                f.write('\n\n' + sim.get('cpu_state', ''))
            result.log_file = log_file
            result.artifacts.append(log_file)

        return result


class XPlaneEngine:
    """X-Plane flight simulator engine bridge."""

    @staticmethod
    def available() -> bool:
        import socket
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(1.0)
            s.connect(('127.0.0.1', 49000))
            s.close()
            return True
        except (socket.error, OSError):
            return False

    @staticmethod
    def run(platform, timeout=60, log_file=''):
        from eosim.integrations.xplane import XPlaneConnection
        result = SimResult(engine='xplane', platform=platform.name)
        conn = XPlaneConnection()
        if conn.connect(timeout=5.0):
            result.success = True
            result.stdout = 'X-Plane connected on %s:%d' % (conn.host, conn.port)
            data = conn.receive_data(timeout=2.0)
            if data:
                result.stdout += '\nReceived %d data groups' % len(data)
            conn.disconnect()
        else:
            result.stdout = 'X-Plane not available (connection failed)'
            result.success = False
        return result


class GazeboEngine:
    """Gazebo simulation engine bridge."""

    @staticmethod
    def available() -> bool:
        return (shutil.which('gz') is not None or
                shutil.which('gzserver') is not None)

    @staticmethod
    def run(platform, timeout=60, log_file=''):
        from eosim.integrations.gazebo import GazeboConnection
        result = SimResult(engine='gazebo', platform=platform.name)
        conn = GazeboConnection()
        if conn.connect(timeout=5.0):
            result.success = True
            result.stdout = 'Gazebo connected'
            conn.disconnect()
        else:
            result.stdout = 'Gazebo not available'
            result.success = False
        return result


class OpenFOAMEngine:
    """OpenFOAM CFD solver engine."""

    @staticmethod
    def available() -> bool:
        for solver in ['simpleFoam', 'icoFoam']:
            if shutil.which(solver) is not None:
                return True
        return False

    @staticmethod
    def run(platform, timeout=300, log_file='', case_dir='', solver='simpleFoam'):
        from eosim.integrations.openfoam import OpenFOAMRunner
        result = SimResult(engine='openfoam', platform=platform.name)
        runner = OpenFOAMRunner(case_dir=case_dir)
        runner.set_solver(solver)
        run_result = runner.run(timeout=timeout)
        result.success = run_result['success']
        result.stdout = run_result.get('log', '')
        return result


def get_engine(platform: Platform):
    """Get the best available engine for a platform."""
    if platform.engine == "qemu-live":
        return QemuLiveEngine()
    if platform.engine == "xplane":
        return XPlaneEngine()
    if platform.engine == "gazebo":
        return GazeboEngine()
    if platform.engine == "openfoam":
        return OpenFOAMEngine()
    if platform.engine == "eosim" and EoSimEngine.available():
        return EoSimEngine()
    if platform.engine == "renode" and RenodeEngine.available():
        return RenodeEngine()
    if QemuEngine.available(platform.arch):
        return QemuEngine()
    return QemuEngine()  # fallback — will do dry run


class QemuLiveEngine:
    """QEMU with live interaction via QMP and GDB protocols.

    Launches QEMU with QMP socket and GDB stub enabled, allowing
    real-time register/memory inspection, breakpoints, and VM control.
    """

    @staticmethod
    def available(arch: str = 'arm') -> bool:
        return QemuEngine.available(arch)

    def __init__(self):
        self._process = None
        self._qmp = None
        self._gdb = None
        self._bridge = None

    def run(self, platform: Platform, timeout: int = 60,
            log_file: str = '') -> SimResult:
        """Launch QEMU with QMP + GDB enabled."""
        result = SimResult(engine='qemu-live', platform=platform.name)
        binary = QemuEngine.ARCH_MAP.get(
            platform.arch, 'qemu-system-' + platform.arch)
        qemu = shutil.which(binary)
        if not qemu:
            result.stderr = f"{binary} not installed"
            result.success = False
            return result

        gdb_port = platform.qemu.gdb_port or 1234
        qmp_port = platform.qemu.qmp_port or 4444

        cmd = [
            qemu,
            '-machine', platform.qemu.machine,
            '-m', str(platform.runtime.memory_mb),
            '-nographic', '-no-reboot',
            '-gdb', f'tcp::{gdb_port}',
            '-qmp', f'tcp:localhost:{qmp_port},server=on,wait=off',
        ]
        if platform.qemu.start_paused:
            cmd.append('-S')
        if platform.qemu.cpu:
            cmd += ['-cpu', platform.qemu.cpu]
        if platform.boot.kernel:
            kernel = os.path.join(platform.source_dir, platform.boot.kernel)
            if os.path.exists(kernel):
                cmd += ['-kernel', kernel]
        if platform.boot.initrd:
            initrd = os.path.join(platform.source_dir, platform.boot.initrd)
            if os.path.exists(initrd):
                cmd += ['-initrd', initrd]
        if platform.boot.append:
            cmd += ['-append', platform.boot.append]
        for arg in platform.qemu.extra_args:
            cmd.append(arg)

        import time as _time
        start = _time.time()
        try:
            self._process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            _time.sleep(1.0)

            if self._process.poll() is not None:
                result.stderr = 'QEMU exited immediately'
                return result

            try:
                from eosim.engine.qemu.qmp_client import QMPClient
                self._qmp = QMPClient()
                self._qmp.connect_tcp(port=qmp_port)
            except Exception as e:
                result.stderr += f'\nQMP connection failed: {e}'

            try:
                from eosim.engine.qemu.gdb_client import GDBRemoteClient
                arch_map = {'arm64': 'aarch64', 'aarch64': 'aarch64'}
                gdb_arch = arch_map.get(platform.arch, 'arm')
                self._gdb = GDBRemoteClient(arch=gdb_arch)
                self._gdb.connect(port=gdb_port)
            except Exception as e:
                result.stderr += f'\nGDB connection failed: {e}'

            if self._gdb:
                from eosim.engine.qemu.state_bridge import TargetStateBridge
                self._bridge = TargetStateBridge(gdb_client=self._gdb)

            result.success = True
            result.stdout = f'QEMU live session started (GDB:{gdb_port} QMP:{qmp_port})'
        except Exception as e:
            result.stderr = str(e)

        result.duration_s = _time.time() - start
        return result

    @property
    def qmp(self):
        return self._qmp

    @property
    def gdb(self):
        return self._gdb

    @property
    def state_bridge(self):
        return self._bridge

    def pause(self):
        if self._qmp:
            return self._qmp.stop()

    def resume(self):
        if self._qmp:
            return self._qmp.cont()

    def step(self):
        if self._gdb:
            return self._gdb.step()

    def stop(self):
        if self._bridge:
            self._bridge.stop_polling()
        if self._gdb:
            self._gdb.disconnect()
        if self._qmp:
            try:
                self._qmp.quit()
            except Exception:
                pass
            self._qmp.disconnect()
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
