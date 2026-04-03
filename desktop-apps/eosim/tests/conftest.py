"""Shared test fixtures for EoSim test suite."""
import os
import pytest
import yaml
from pathlib import Path
from unittest.mock import MagicMock

from eosim.core.platform import Platform, BootConfig, RuntimeConfig, QemuConfig
from eosim.core.registry import PlatformRegistry
from eosim.engine.backend import SimResult


@pytest.fixture
def sample_platform_yaml():
    """Return a valid platform YAML dict."""
    return {
        "name": "test-board",
        "display_name": "Test Board",
        "arch": "arm",
        "engine": "eosim",
        "vendor": "TestVendor",
        "soc": "TEST1234",
        "class": "mcu",
        "domain": "industrial",
        "modeling": "deterministic",
        "runtime": {
            "memory_mb": 128,
            "headless": True,
            "uart": "sysbus.uart0",
            "timeout_s": 30,
        },
    }


@pytest.fixture
def sample_platform_dir(tmp_path, sample_platform_yaml):
    """Create a temporary platform directory with platform.yml and tests.yml."""
    plat_dir = tmp_path / "test-board"
    plat_dir.mkdir()

    with open(plat_dir / "platform.yml", "w") as f:
        yaml.dump(sample_platform_yaml, f)

    tests_data = {
        "checks": [
            {"type": "serial_contains", "value": "Booting"},
            {"type": "exit_code", "value": "0"},
            {"type": "timeout", "seconds": 30},
        ]
    }
    with open(plat_dir / "tests.yml", "w") as f:
        yaml.dump(tests_data, f)

    return plat_dir


@pytest.fixture
def sample_platform(sample_platform_dir):
    """Load a Platform from the sample platform dir."""
    return Platform.from_yaml(str(sample_platform_dir / "platform.yml"))


@pytest.fixture
def multi_platform_dir(tmp_path):
    """Create a directory with multiple platform configs for registry testing."""
    platforms = [
        {"name": "arm-mcu", "arch": "arm", "engine": "eosim", "vendor": "ST",
         "class": "mcu", "domain": "industrial"},
        {"name": "arm64-sbc", "arch": "arm64", "engine": "renode", "vendor": "Raspberry Pi",
         "class": "sbc", "domain": "consumer"},
        {"name": "riscv-dev", "arch": "riscv64", "engine": "qemu", "vendor": "SiFive",
         "class": "devboard", "domain": "iot"},
    ]
    for p in platforms:
        d = tmp_path / p["name"]
        d.mkdir()
        with open(d / "platform.yml", "w") as f:
            yaml.dump(p, f)
    return tmp_path


@pytest.fixture
def platform_registry(multi_platform_dir):
    """Create a PlatformRegistry with multiple platforms."""
    return PlatformRegistry(str(multi_platform_dir))


@pytest.fixture
def successful_sim_result():
    """A SimResult representing a successful simulation."""
    return SimResult(
        success=True,
        exit_code=0,
        stdout="Booting EoS v0.1.0...\nInitializing UART...\nReady.\nlogin:",
        stderr="",
        log_file="",
        duration_s=2.5,
        engine="eosim",
        platform="test-board",
        boot_detected=True,
    )


@pytest.fixture
def failed_sim_result():
    """A SimResult representing a failed simulation."""
    return SimResult(
        success=False,
        exit_code=1,
        stdout="Booting EoS v0.1.0...\nKernel panic!",
        stderr="FATAL: memory corruption",
        log_file="",
        duration_s=0.5,
        engine="eosim",
        platform="test-board",
        boot_detected=False,
    )
