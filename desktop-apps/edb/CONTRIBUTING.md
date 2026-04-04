# Contributing to eDB

Thank you for your interest in contributing to eDB! This document provides guidelines and instructions for contributing.

## Getting Started

1. **Fork the repository** and clone your fork locally.
2. **Set up the development environment:**

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

3. **Run the tests** to ensure everything works:

```bash
pytest
```

## Development Workflow

### Branching

- Create a feature branch from `main`: `git checkout -b feature/your-feature`
- Use descriptive branch names: `feature/`, `fix/`, `docs/`, `refactor/`

### Code Style

- We use **ruff** for linting and formatting
- We use **mypy** for type checking
- Run both before submitting:

```bash
ruff check src/ tests/
ruff format src/ tests/
mypy src/edb/
```

### Testing

- Write tests for all new functionality
- Place unit tests in `tests/unit/`
- Place integration tests in `tests/integration/`
- Maintain test coverage above 80%

```bash
pytest --cov=edb --cov-report=html
```

### Commit Messages

Use conventional commit format:

```
type(scope): description

feat(core): add TTL support to key-value store
fix(api): handle empty query body gracefully
docs(readme): update installation instructions
test(auth): add RBAC permission tests
```

## Pull Request Process

1. Ensure all tests pass and linting is clean
2. Update documentation if your changes affect the public API
3. Add a changelog entry in `CHANGELOG.md`
4. Request review from at least one maintainer
5. Squash commits before merging

## Reporting Issues

- Use GitHub Issues for bug reports and feature requests
- Include reproduction steps, expected behavior, and actual behavior
- Tag issues appropriately: `bug`, `enhancement`, `documentation`

## Architecture Overview

See [docs/architecture.md](docs/architecture.md) for the system design.

Key modules:
- `src/edb/core/` — Storage engines (relational, document, key-value)
- `src/edb/query/` — Query parsing and planning
- `src/edb/api/` — REST API (FastAPI)
- `src/edb/auth/` — Authentication and RBAC
- `src/edb/security/` — Encryption and audit logging
- `src/edb/ebot/` — AI/NLP query interface

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
