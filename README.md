# 📱 eApps — Cross-Platform Embedded Applications

[![CI](https://github.com/embeddedos-org/eApps/actions/workflows/ci.yml/badge.svg)](https://github.com/embeddedos-org/eApps/actions/workflows/ci.yml)
[![Nightly](https://github.com/embeddedos-org/eApps/actions/workflows/nightly.yml/badge.svg)](https://github.com/embeddedos-org/eApps/actions/workflows/nightly.yml)
[![Release](https://github.com/embeddedos-org/eApps/actions/workflows/release-suite.yml/badge.svg)](https://github.com/embeddedos-org/eApps/actions/workflows/release-suite.yml)
[![Version](https://img.shields.io/badge/version-0.1.0-blue)]()

**38 apps. One C codebase. Every platform.**

eApps is a pure C + LVGL monorepo delivering productivity tools, media apps, games, and system utilities across **Windows**, **Linux**, **macOS**, **EoS**, and **Web (Emscripten/WASM)** — from a single portable codebase.

---

## ⚡ Quick Start

| | |
git clone https://github.com/embeddedos-org/eApps.git
cd eApps
| **UI Framework** | LVGL v9.x |
# Desktop build (SDL2 backend)
cmake -B build -DEAPPS_PORT=sdl2
cmake --build build
./build/eapps_suite
| **Binary Size** | 500KB–5MB per standalone app |
# Build with tests
cmake -B build -DEAPPS_PORT=sdl2 -DEAPPS_BUILD_TESTS=ON
cmake --build build
ctest --test-dir build
## Quick Start
# Web build (Emscripten → WASM)
cmake -B build-web -DCMAKE_TOOLCHAIN_FILE=cmake/emscripten.cmake
cmake --build build-web

# EoS build (embedded target)
cmake -B build-eos -DCMAKE_TOOLCHAIN_FILE=cmake/eos.cmake
cmake --build build-eos
# Desktop build (Linux/macOS)
cmake -B build -DBUILD_TESTING=ON
---
./build/apps/suite/eapps_suite
## 📱 Apps (38 total)


# Run tests
cd build && ctest --output-on-failure

# Windows (MSVC)
cmake -B build
cmake --build build --config Release

# EoS cross-compile
---
cmake --build build-eos
## 🏗 Architecture
cmake -B build -DEAPPS_BUILD_STANDALONE=ON
```
eApps/
├── core/                     # Shared C libraries
│   ├── common/               #   Types, math, string, date, registry, expr parser
│   ├── ui/                   #   LVGL theme, widgets, canvas, game engine
│   ├── storage/              #   Key-value preferences (file-backed)
│   ├── network/              #   HTTP client (POSIX/Win32/Web backends)
│   └── platform/             #   Platform abstraction (Linux/Win32/EoS/Web)
├── apps/                     # 38 application modules
│   ├── suite/                #   Suite launcher (all-in-one)
│   ├── ecalc/                #   Calculator
│   ├── enote/                #   Text editor
│   ├── snake/                #   Snake game
│   └── ...                   #   + 34 more
├── port/                     # Display + input drivers per platform
│   ├── sdl2/                 #   SDL2 backend (Windows/Linux/macOS)
│   ├── eos/                  #   EoS framebuffer backend
│   └── web/                  #   Emscripten/WASM backend
├── extern/                   # Third-party (LVGL, lv_conf.h)
├── cmake/                    # Toolchain files
│   ├── emscripten.cmake      #   WebAssembly cross-compile
│   ├── eos.cmake             #   EoS embedded target
│   ├── linux.cmake           #   Linux native
│   └── windows.cmake         #   Windows native
├── tests/                    # Unit tests (C)
└── docs/                     # Documentation
```
./build/apps/ecal/ecal_standalone
---
| Flag | Description |
## 🎯 Platform Support
| `EAPPS_BUILD_PRODUCTIVITY` | ecal, enote, econverter, ebuffer, efiles, ecleaner, eclock, etools, etimer, epdf, ezip, eviewer, esession |
| Platform | Port | Backend | Output |
|----------|------|---------|--------|
| Windows | `sdl2` | SDL2 + OpenGL | `.exe` |
| Linux | `sdl2` | SDL2 + X11/Wayland | ELF binary |
| macOS | `sdl2` | SDL2 + Metal | `.app` |
| EoS (embedded) | `eos` | Framebuffer / display HAL | Firmware image |
| Web (any browser) | `web` | Emscripten → WASM | HTML + WASM |

---

## 🔧 Core Modules

| Module | Headers | Description |
|--------|---------|-------------|
| **common** | `eapps/types.h`, `version.h`, `math_utils.h`, `string_utils.h`, `date_utils.h`, `registry.h`, `expr_parser.h` | Shared types, math, string manipulation, date formatting, app registry, expression parser |
| **ui** | `eapps/theme.h`, `widgets.h`, `canvas.h`, `game_engine.h` | LVGL theme (dark/light), reusable widgets, 2D drawing canvas, game rendering engine |
| **storage** | `eapps/prefs.h` | Key-value preferences with file-backed persistence |
| **network** | `eapps/http.h` | HTTP client with platform backends (POSIX sockets, WinHTTP, Emscripten fetch) |
| **platform** | `eapps/platform.h` | Platform abstraction (paths, clipboard, locale, file I/O, process management) |

---

## 🧪 Tests

| `EAPPS_BUILD_MEDIA` | emusic, evideo, egallery, eplay, epaint |
cmake -B build -DEAPPS_PORT=sdl2 -DEAPPS_BUILD_TESTS=ON
cmake --build build
ctest --test-dir build --output-on-failure
| `EAPPS_BUILD_STANDALONE` | Per-app standalone executables (OFF by default) |

| Test | Covers |
|------|--------|
| `test_math_utils` | Math helpers, clamp, lerp, remap |
| `test_string_utils` | String trim, split, join, format |
| `test_date_utils` | Date formatting, parsing, relative time |
| `test_expr_parser` | Expression evaluation (calculator backend) |
| `test_registry` | App registration, lookup, enumeration |
| `test_prefs` | Preferences save/load/delete |
| `test_game_engine` | Game loop, sprite, collision detection |
# Games only
---
```
## 🚀 CI/CD

| Workflow | Schedule | Coverage |
|----------|----------|----------|
| **CI** | Every push/PR | Build matrix (Linux × Windows × macOS) + tests |
| **Nightly** | 2:00 AM UTC daily | Full build + test + regression report |
| **Weekly** | Monday 6:00 AM UTC | Comprehensive build + dependency audit |
| **EoSim Sanity** | 4:00 AM UTC daily | EoSim install + simulation validation |
| **Simulation Test** | 3:00 AM UTC daily | QEMU/EoSim platform simulation |
| **Release** | Tag `v*.*.*` | Build → test → package → GitHub Release |

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [Architecture](docs/architecture.md) | Module structure, build system, platform layers |
| [Adding Apps](docs/adding-apps.md) | Step-by-step guide to add a new app |
| [Porting Guide](docs/porting-guide.md) | How to port to a new platform |

---

## Related Projects

| Project | Repository | Purpose |
|---|---|---|
| **eos** | [embeddedos-org/eos](https://github.com/embeddedos-org/eos) | Embedded OS — provides HAL for display/input |
| **eosim** | [embeddedos-org/eosim](https://github.com/embeddedos-org/eosim) | Simulator — test apps in simulated environments |
| **ebuild** | [embeddedos-org/ebuild](https://github.com/embeddedos-org/ebuild) | Build system — SDK generator, packaging |
| **EoStudio** | [embeddedos-org/EoStudio](https://github.com/embeddedos-org/EoStudio) | Design suite with LLM integration |


## Project Structure

```
## 📜 License
├── CMakeLists.txt          # Root build configuration
├── cmake/                  # Toolchain files (eos, linux, windows, emscripten)
├── extern/                 # LVGL submodule + lv_conf.h
├── core/
│   ├── common/             # Types, registry, math/string/date utils, expr parser
│   ├── ui/                 # Theme, widgets, canvas, game engine
│   ├── storage/            # File-backed preferences
│   ├── network/            # HTTP abstraction (posix/win32/web backends)
│   └── platform/           # Clipboard, sysinfo, tick (per-platform impls)
├── port/
│   ├── sdl2/               # Desktop display/input drivers + main
│   ├── eos/                # EoS HAL drivers + main
│   └── web/                # Emscripten drivers + main
├── apps/
│   ├── ecal/               # Calculator (expr parser + btnmatrix)
│   ├── snake/              # Snake game (game engine)
│   ├── echess/             # Chess (full move validation)
│   ├── suite/              # Suite launcher (app grid + categories)
│   └── ...                 # 35 more apps
├── tests/                  # CTest unit tests
└── docs/                   # Architecture, porting guide, adding apps
```

## Platform Support

| Platform | Display | Input | Status |
|----------|---------|-------|--------|
| Linux (SDL2) | SDL2 window | Mouse + keyboard | ✅ Ready |
| Windows (SDL2) | SDL2 window | Mouse + keyboard | ✅ Ready |
| macOS (SDL2) | SDL2 window | Mouse + keyboard | ✅ Ready |
| EoS | HAL framebuffer | HAL touch | 🔧 Port stubs |
| Web | HTML5 canvas | Browser events | 🔧 Port stubs |

## License

MIT — see [LICENSE](LICENSE)
