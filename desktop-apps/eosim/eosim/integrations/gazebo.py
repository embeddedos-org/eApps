# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""Gazebo simulation integration — model spawn, state, force control."""
import subprocess
import shutil
from typing import Optional, Dict


class GazeboConnection:
    """Connect to Gazebo simulator via its Transport API / CLI.

    Supports Gazebo Garden+ (gz) and classic Gazebo (gzserver).
    """

    def __init__(self, host: str = '127.0.0.1', port: int = 11345):
        self.host = host
        self.port = port
        self.connected = False
        self._process: Optional[subprocess.Popen] = None
        self._models: Dict[str, dict] = {}

    @staticmethod
    def available() -> bool:
        return shutil.which('gz') is not None or shutil.which(
            'gzserver') is not None

    def connect(self, timeout: float = 10.0) -> bool:
        if not self.available():
            return False
        try:
            result = subprocess.run(
                ['gz', 'topic', '-l'],
                capture_output=True, text=True, timeout=5)
            self.connected = result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            try:
                result = subprocess.run(
                    ['gzserver', '--version'],
                    capture_output=True, text=True,
                    timeout=5)
                self.connected = result.returncode == 0
            except (subprocess.SubprocessError, FileNotFoundError):
                self.connected = False
        return self.connected

    def disconnect(self):
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
        self.connected = False

    def spawn_model(self, name: str, sdf_path: str,
                    x: float = 0, y: float = 0, z: float = 0) -> bool:
        try:
            cmd = ['gz', 'model', '--spawn-file', sdf_path,
                   '--model-name', name,
                   '-x', str(x), '-y', str(y), '-z', str(z)]
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self._models[name] = {'x': x, 'y': y, 'z': z, 'sdf': sdf_path}
                return True
        except (subprocess.SubprocessError, FileNotFoundError):
            pass
        return False

    def get_model_state(self, name: str) -> dict:
        try:
            cmd = ['gz', 'model', '-m', name, '-p']
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return {'name': name, 'pose': result.stdout.strip()}
        except (subprocess.SubprocessError, FileNotFoundError):
            pass
        return self._models.get(name, {})

    def apply_force(self, model: str, fx: float, fy: float, fz: float):
        pass  # requires Gazebo Transport API bindings

    def step(self, steps: int = 1):
        try:
            cmd = ['gz', 'world', '-s', '-r', str(steps)]
            subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        except (subprocess.SubprocessError, FileNotFoundError):
            pass

    def get_status(self) -> dict:
        return {
            'connected': self.connected,
            'host': self.host,
            'port': self.port,
            'models': list(self._models.keys()),
            'available': self.available(),
        }
