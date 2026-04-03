# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- SECURITY.md with vulnerability disclosure policy and severity classification
- CONTRIBUTING.md with development guidelines and PR process
- CODE_OF_CONDUCT.md (Contributor Covenant v2.1)
- GitHub issue templates (bug report, feature request) and PR template
- Logging framework (`core/common/include/eapps/log.h`, `core/common/src/log.c`)
- Unit tests: test_http, test_platform, test_canvas, test_theme, test_widgets, test_log
- Integration tests: registry lifecycle, app category isolation
- Fuzz harnesses: expression parser, HTTP response parser, base64
- SBOM generation (CycloneDX v1.5) via CMake module
- OSSF Scorecard workflow for supply-chain security scoring
- CodeQL SAST scanning on push/PR
- Dependabot for GitHub Actions and git submodules
- Security roadmap, threat model, and audit checklist documentation
- `.clang-format` and `.clang-tidy` for code quality enforcement
- `.editorconfig` for consistent formatting across editors
- `CODEOWNERS` for automated review assignment

### Changed
- CI workflow: added clang-tidy step, coverage reporting, pinned actions to SHA
- Nightly workflow: added ASan/UBSan and Valgrind steps
- Weekly workflow: added full static analysis and dependency audit
- Release workflow: added SBOM generation step
- `cmake/eos.cmake`: added `-frandom-seed` for reproducible builds
- `cmake/linux.cmake`: added `SOURCE_DATE_EPOCH` support

### Fixed
- Version badge in README now shows 2.0.0 (was 0.1.0)

## [2.0.0] - 2026-04-01

### Added
- 38 applications across productivity, media, games, connectivity, and security categories
- Cross-platform support: Linux, Windows, macOS, EoS (embedded), Web (WASM)
- Core libraries: common, ui, storage, network, platform
- LVGL v9.1 UI framework integration
- CI/CD pipeline with nightly, weekly, and release workflows
- EoSim platform simulation testing
- 7 unit tests covering core modules
- cppcheck static analysis integration

### Changed
- Project version bumped from 0.1.0 to 2.0.0

## [0.1.0] - 2026-03-31

### Added
- Initial release of eApps
- Complete CI/CD pipeline with nightly, weekly, and QEMU sanity runs
- Full cross-platform support (Linux, Windows, macOS)
- ISO/IEC standards compliance documentation
- MIT license

[Unreleased]: https://github.com/embeddedos-org/eApps/compare/v2.0.0...HEAD
[2.0.0]: https://github.com/embeddedos-org/eApps/compare/v0.1.0...v2.0.0
[0.1.0]: https://github.com/embeddedos-org/eApps/releases/tag/v0.1.0
