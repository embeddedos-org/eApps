"""Integration tests — YAML scenario loading and validation."""
import pytest
import yaml
from pathlib import Path

from eosim.engine.backend import SimResult
from eosim.tests.runner import run_checks


class TestScenarioRunner:
    """Test that YAML scenario files are valid and can drive checks."""

    @pytest.fixture
    def scenarios_dir(self):
        d = Path(__file__).parent.parent / "scenarios"
        if not d.exists():
            pytest.skip("tests/scenarios/ directory not found")
        return d

    def test_full_boot_scenario_loads(self, scenarios_dir):
        """Verify full_boot.yml is valid YAML with expected structure."""
        path = scenarios_dir / "full_boot.yml"
        if not path.exists():
            pytest.skip("full_boot.yml not found")

        with open(path) as f:
            data = yaml.safe_load(f)

        assert data is not None
        assert "steps" in data or "checks" in data

    def test_rtos_boot_scenario_loads(self, scenarios_dir):
        """Verify rtos_boot.yml is valid YAML with expected structure."""
        path = scenarios_dir / "rtos_boot.yml"
        if not path.exists():
            pytest.skip("rtos_boot.yml not found")

        with open(path) as f:
            data = yaml.safe_load(f)

        assert data is not None
        assert "steps" in data or "checks" in data

    def test_checks_from_scenario(self, scenarios_dir):
        """Extract checks from a scenario and run against a mock SimResult."""
        path = scenarios_dir / "rtos_boot.yml"
        if not path.exists():
            pytest.skip("rtos_boot.yml not found")

        with open(path) as f:
            data = yaml.safe_load(f) or {}

        checks = data.get("checks", [])
        if not checks:
            steps = data.get("steps", [])
            for step in steps:
                if "check" in step:
                    checks.append(step["check"])

        sim_result = SimResult(
            success=True,
            exit_code=0,
            stdout="Booting EoS RTOS...\nScheduler started.\nReady.\nlogin:",
            engine="eosim",
            platform="test",
            boot_detected=True,
            duration_s=1.0,
        )

        if checks:
            results = run_checks(sim_result, checks)
            assert len(results) > 0

    def test_all_scenario_files_are_valid_yaml(self, scenarios_dir):
        """Every .yml file in scenarios/ must parse as valid YAML."""
        for yml_file in scenarios_dir.glob("*.yml"):
            with open(yml_file) as f:
                data = yaml.safe_load(f)
            assert data is not None, f"{yml_file.name} is empty or invalid"
