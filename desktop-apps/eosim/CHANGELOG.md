# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `.gitignore` with Python, IDE, and EoSim-specific patterns
- `Makefile` with standardized targets (test, lint, format, coverage, build, clean, docker)
- `CONTRIBUTING.md` with development workflow, code style, and PR process
- `CODE_OF_CONDUCT.md` (Contributor Covenant v2.1)
- GitHub Actions CI workflow (`ci.yml`) — Python 3.9-3.12 matrix, lint, test, coverage
- GitHub Actions nightly regression workflow (`nightly.yml`)
- GitHub Actions release workflow (`release.yml`) — PyPI publishing
- GitHub issue templates (bug report, feature request)
- GitHub pull request template with checklist
- `Dockerfile` with multi-stage build and QEMU pre-installed
- `docker-compose.yml` for containerized simulation
- `tests/conftest.py` with shared fixtures (sample platforms, registries, SimResults)
- Integration tests: platform pipeline, CLI commands, scenario runner
- Example READMEs for `examples/` and `examples/cluster-demo/`

### Changed
- Enhanced `pyproject.toml` with URLs, classifiers, authors, tool configs (pytest, coverage, ruff)
- Consolidated `pytest.ini` into `pyproject.toml` `[tool.pytest.ini_options]`
- Expanded `SECURITY.md` with supported versions, scope, and disclosure process

### Fixed
- `docs/architecture.md` — replaced corrupted PowerShell artifacts with proper Markdown

### Documentation
- `docs/getting-started.md` — step-by-step installation and first simulation tutorial
- `docs/api-reference.md` — complete Python API documentation with examples
- `docs/platform-authoring.md` — guide for creating new platform configurations
- `docs/hil-guide.md` — hardware-in-the-loop setup, wiring, and troubleshooting
- `docs/cli-reference.md` — full CLI command tree with options and examples

### Removed
- `pytest.ini` (consolidated into `pyproject.toml`)

## [0.1.0] - 2026-03-31

### Added
- Initial release of eosim
- Custom EoSim native simulation engine (zero external dependencies)
- Engine priority: EoSim native > Renode > dry-run
- Renode engine backend
- 41 platform configurations across 12 architectures
- CPU, memory, and 6 peripheral simulators (UART, GPIO, Timer, SPI, I2C, NVIC)
- pip-installable package with CLI (`eosim` command)
- GUI simulator with Tkinter-based 3D product renderers
- QEMU integration with QMP, GDB, ELF loader, and state bridge
- Hardware-in-the-loop (HIL) session management
- Complete CI/CD pipeline with nightly, weekly, EoSim sanity, and simulation test runs
- Full cross-platform support (Linux, Windows, macOS)
- ISO/IEC standards compliance documentation
- MIT license

[Unreleased]: https://github.com/embeddedos-org/eosim/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/embeddedos-org/eosim/releases/tag/v0.1.0
