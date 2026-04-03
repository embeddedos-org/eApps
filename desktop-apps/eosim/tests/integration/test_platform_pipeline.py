"""Integration tests — full platform pipeline: YAML → Platform → Engine → SimResult → Checks."""
import os
import pytest
import yaml
from pathlib import Path

from eosim.core.platform import Platform, discover_platforms
from eosim.core.registry import PlatformRegistry
from eosim.core.schema import validate_platform
from eosim.engine.backend import EoSimEngine, SimResult, get_engine
from eosim.tests.runner import run_checks, load_checks


class TestPlatformPipeline:
    """End-to-end: YAML config → Platform loading → validation → engine selection."""

    def test_load_and_validate_platform(self, sample_platform_dir):
        """Load a platform from YAML and validate it."""
        cfg_path = str(sample_platform_dir / "platform.yml")
        platform = Platform.from_yaml(cfg_path)

        assert platform.name == "test-board"
        assert platform.arch == "arm"
        assert platform.engine == "eosim"

        with open(cfg_path) as f:
            data = yaml.safe_load(f)
        errors = validate_platform(data)
        assert errors == [], f"Validation errors: {errors}"

    def test_discover_and_registry(self, multi_platform_dir):
        """Discover platforms from directory and build a registry."""
        platforms = discover_platforms(str(multi_platform_dir))
        assert len(platforms) == 3

        registry = PlatformRegistry.from_dict(platforms)
        assert registry.count() == 3

        arm_platforms = registry.filter(arch="arm")
        assert len(arm_platforms) == 1
        assert arm_platforms[0].name == "arm-mcu"

    def test_engine_selection(self, sample_platform):
        """Verify engine selection for a platform."""
        engine = get_engine(sample_platform)
        assert engine is not None
        assert EoSimEngine.available()

    def test_native_engine_run(self, sample_platform):
        """Run the EoSim native engine and get a SimResult."""
        result = EoSimEngine.run(sample_platform, timeout=10)
        assert isinstance(result, SimResult)
        assert result.engine == "eosim"
        assert result.platform == sample_platform.name

    def test_checks_against_result(self, successful_sim_result):
        """Run test checks against a successful SimResult."""
        checks = [
            {"type": "serial_contains", "value": "Booting EoS"},
            {"type": "exit_code", "value": "0"},
            {"type": "timeout", "seconds": 60},
            {"type": "boot_success"},
        ]
        results = run_checks(successful_sim_result, checks)
        assert len(results) == 4
        assert all(r.passed for r in results), (
            f"Failed checks: {[r.name for r in results if not r.passed]}"
        )

    def test_checks_detect_failures(self, failed_sim_result):
        """Verify checks correctly detect failures."""
        checks = [
            {"type": "serial_contains", "value": "Ready"},
            {"type": "exit_code", "value": "0"},
            {"type": "boot_success"},
        ]
        results = run_checks(failed_sim_result, checks)
        assert not all(r.passed for r in results)

    def test_load_checks_from_yaml(self, sample_platform_dir):
        """Load test checks from a tests.yml file."""
        checks = load_checks(str(sample_platform_dir))
        assert len(checks) == 3
        assert checks[0]["type"] == "serial_contains"


class TestPlatformValidation:
    """Validate platform configs in the real platforms/ directory."""

    def test_validate_all_real_platforms(self):
        """Validate all platform.yml files in the platforms/ directory."""
        platforms_dir = Path(__file__).parent.parent.parent / "platforms"
        if not platforms_dir.exists():
            pytest.skip("platforms/ directory not found")

        errors = {}
        for sub in sorted(platforms_dir.iterdir()):
            cfg = sub / "platform.yml"
            if cfg.exists():
                with open(cfg) as f:
                    data = yaml.safe_load(f) or {}
                errs = validate_platform(data)
                if errs:
                    errors[sub.name] = errs

        assert errors == {}, f"Platform validation errors: {errors}"

    def test_discover_real_platforms(self):
        """Verify discover_platforms can load the real platforms/ directory."""
        platforms_dir = Path(__file__).parent.parent.parent / "platforms"
        if not platforms_dir.exists():
            pytest.skip("platforms/ directory not found")

        platforms = discover_platforms(str(platforms_dir))
        assert len(platforms) > 0, "No platforms discovered"
