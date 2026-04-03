# Contributing to eApps

Thank you for your interest in contributing to eApps! This document provides guidelines and instructions for contributing.

## Getting Started

1. **Fork the repository** and clone your fork locally.
2. **Set up the development environment:**

```bash
git clone https://github.com/embeddedos-org/eApps.git
cd eApps
git submodule update --init --recursive
cmake -B build -DEAPPS_PORT=sdl2 -DBUILD_TESTING=ON
cmake --build build
```

3. **Run the tests** to ensure everything works:

```bash
ctest --test-dir build --output-on-failure
```

## Development Workflow

### Branching

- Create a feature branch from `master`: `git checkout -b feature/your-feature`
- Use descriptive branch names: `feature/`, `fix/`, `docs/`, `refactor/`, `app/`

### Code Style

- We use **clang-format** and **clang-tidy** for code quality
- Run before submitting:

```bash
clang-format -i core/**/*.c core/**/*.h apps/**/*.c apps/**/*.h
cmake --build build --target cppcheck
```

### Testing

- Write tests for all new functionality
- Place unit tests in `tests/`
- Maintain test coverage above 70%

```bash
cmake -B build -DEAPPS_PORT=sdl2 -DBUILD_TESTING=ON
cmake --build build
ctest --test-dir build --output-on-failure
```

### Commit Messages

Use conventional commit format:

```
type(scope): description

feat(ecal): add scientific notation display
fix(snake): fix wall collision at boundary
docs(readme): update build instructions
test(core): add string_utils edge case tests
app(ezip): add TAR extraction support
```

## Pull Request Process

1. Ensure all tests pass and linting is clean
2. Update documentation if your changes affect the public API
3. Add a changelog entry in `CHANGELOG.md`
4. Run `cppcheck` and resolve warnings
5. Request review from at least one maintainer
6. Squash commits before merging

## Adding a New App

1. Create `apps/<name>/` with `CMakeLists.txt`, `<name>.c`, and `<name>.h`
2. Register the app in `core/common/src/registry.c`
3. Add `add_subdirectory(apps/<name>)` to the root `CMakeLists.txt`
4. Add a row to the app table in `README.md`
5. See [Adding Apps Guide](docs/adding-apps.md) for details

## Reporting Issues

- Use GitHub Issues for bug reports and feature requests
- Include reproduction steps, expected behavior, and actual behavior
- Tag issues appropriately: `bug`, `enhancement`, `documentation`, `app`

## Architecture Overview

See [docs/architecture.md](docs/architecture.md) for the system design.

Key modules:
- `core/common/` — Types, math, string, date, registry, expression parser
- `core/ui/` — LVGL theme, widgets, canvas, game engine
- `core/storage/` — Key-value preferences (file-backed)
- `core/network/` — HTTP client (POSIX/Win32/Web backends)
- `core/platform/` — Platform abstraction (Linux/Win32/EoS/Web)
- `apps/` — 38 application modules
- `port/` — Display + input drivers per platform

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
