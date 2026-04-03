# Contributing to EoSim

Thank you for your interest in contributing to EoSim! This document provides guidelines and instructions for contributing.

## Getting Started

1. **Fork the repository** and clone your fork locally.
2. **Set up the development environment:**

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[all]"
```

3. **Run the tests** to ensure everything works:

```bash
make test
```

## Development Workflow

### Branching

- Create a feature branch from `main`: `git checkout -b feature/your-feature`
- Use descriptive branch names: `feature/`, `fix/`, `docs/`, `refactor/`, `platform/`

### Code Style

- We use **ruff** for linting and formatting
- Run before submitting:

```bash
make lint
make format
```

### Testing

- Write tests for all new functionality
- Place unit tests in `tests/unit/`
- Place integration tests in `tests/integration/`
- Maintain test coverage above 70%

```bash
make test           # Run all tests
make test-unit      # Unit tests only
make coverage       # Tests with coverage report
```

### Commit Messages

Use conventional commit format:

```
type(scope): description

feat(engine): add SPI peripheral simulation
fix(cli): handle missing platform.yml gracefully
docs(readme): update installation instructions
test(core): add PlatformRegistry filter tests
platform(nrf52): add Nordic nRF52840 platform config
```

## Pull Request Process

1. Ensure all tests pass and linting is clean
2. Update documentation if your changes affect the public API
3. Add a changelog entry in `CHANGELOG.md`
4. Validate platform configs: `make validate`
5. Request review from at least one maintainer
6. Squash commits before merging

## Adding a New Platform

1. Create `platforms/<name>/platform.yml` (see [Platform Authoring Guide](docs/platform-authoring.md))
2. Create `platforms/<name>/tests.yml` with validation checks
3. Run `eosim validate platforms/<name>/platform.yml`
4. Add a row to the platform table in `README.md`
5. Add tests in `tests/unit/` if the platform has special behavior

## Reporting Issues

- Use GitHub Issues for bug reports and feature requests
- Include reproduction steps, expected behavior, and actual behavior
- Run `eosim doctor` and include the output
- Tag issues appropriately: `bug`, `enhancement`, `documentation`, `platform`

## Architecture Overview

See [docs/architecture.md](docs/architecture.md) for the system design.

Key modules:
- `eosim/core/` — Platform models, registry, schema validation, domains, modeling
- `eosim/engine/` — Simulation backends (EoSim native, Renode, QEMU, HIL)
- `eosim/cli/` — Click-based command-line interface
- `eosim/gui/` — Tkinter dashboard with 3D renderers
- `eosim/integrations/` — External tool bridges (X-Plane, Gazebo, OpenFOAM, OpenOCD)
- `platforms/` — Platform YAML configurations (52+)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
