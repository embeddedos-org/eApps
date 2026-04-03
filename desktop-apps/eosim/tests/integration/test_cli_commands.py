"""Integration tests — CLI commands via Click test runner."""
import pytest
from click.testing import CliRunner
from eosim.cli.main import cli


@pytest.fixture
def runner():
    return CliRunner()


class TestCLICommands:
    """Test CLI commands produce correct output without errors."""

    def test_cli_help(self, runner):
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "EoSim" in result.output

    def test_list_command(self, runner):
        result = runner.invoke(cli, ["list"])
        assert result.exit_code == 0

    def test_list_with_arch_filter(self, runner):
        result = runner.invoke(cli, ["list", "--arch", "arm"])
        assert result.exit_code == 0

    def test_stats_command(self, runner):
        result = runner.invoke(cli, ["stats"])
        assert result.exit_code == 0

    def test_search_command(self, runner):
        result = runner.invoke(cli, ["search", "stm32"])
        assert result.exit_code == 0

    def test_info_command(self, runner):
        result = runner.invoke(cli, ["info", "stm32f4"])
        assert result.exit_code == 0

    def test_validate_all_command(self, runner):
        result = runner.invoke(cli, ["validate", "--all"])
        assert result.exit_code == 0

    def test_doctor_command(self, runner):
        result = runner.invoke(cli, ["doctor"])
        assert result.exit_code == 0

    def test_domain_list_command(self, runner):
        result = runner.invoke(cli, ["domain", "list"])
        assert result.exit_code == 0

    def test_domain_info_command(self, runner):
        result = runner.invoke(cli, ["domain", "info", "automotive"])
        assert result.exit_code == 0

    def test_modeling_list_command(self, runner):
        result = runner.invoke(cli, ["modeling", "list"])
        assert result.exit_code == 0

    def test_modeling_info_command(self, runner):
        result = runner.invoke(cli, ["modeling", "info", "deterministic"])
        assert result.exit_code == 0

    def test_invalid_command(self, runner):
        result = runner.invoke(cli, ["nonexistent"])
        assert result.exit_code != 0
