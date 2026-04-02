# 📱 eApps — Cross-Platform Embedded Applications

[![CI](https://github.com/embeddedos-org/eApps/actions/workflows/ci.yml/badge.svg)](https://github.com/embeddedos-org/eApps/actions/workflows/ci.yml)
[![Nightly](https://github.com/embeddedos-org/eApps/actions/workflows/nightly.yml/badge.svg)](https://github.com/embeddedos-org/eApps/actions/workflows/nightly.yml)
[![Release](https://github.com/embeddedos-org/eApps/actions/workflows/release-suite.yml/badge.svg)](https://github.com/embeddedos-org/eApps/actions/workflows/release-suite.yml)
[![Version](https://img.shields.io/badge/version-0.1.0-blue)]()

**38 apps. One C codebase. Every platform.**

eApps is a pure C + LVGL monorepo delivering productivity tools, media apps, games, and system utilities across **Windows**, **Linux**, **macOS**, **EoS**, and **Web (Emscripten/WASM)** — from a single portable codebase.

---

## ⚡ Quick Start

```bash
git clone https://github.com/embeddedos-org/eApps.git
cd eApps

# Desktop build (SDL2 backend)
cmake -B build -DEAPPS_PORT=sdl2
cmake --build build
./build/eapps_suite

# Build with tests
cmake -B build -DEAPPS_PORT=sdl2 -DBUILD_TESTING=ON
cmake --build build
ctest --test-dir build --output-on-failure

# Web build (Emscripten → WASM)
cmake -B build-web -DCMAKE_TOOLCHAIN_FILE=cmake/emscripten.cmake
cmake --build build-web

# EoS build (embedded target)
cmake -B build-eos -DCMAKE_TOOLCHAIN_FILE=cmake/eos.cmake
cmake --build build-eos

# Windows (MSVC)
cmake -B build
cmake --build build --config Release

# Build standalone per-app executables
cmake -B build -DEAPPS_BUILD_STANDALONE=ON
cmake --build build
./build/apps/ecal/ecal_standalone
```

---

## 📱 Apps (38 total)

### Productivity (13)

| App | Description |
|-----|-------------|
| **eNote** | Text editor with syntax highlighting, tabs, search/replace |
| **eCalc** | Scientific calculator with expression parser and unit conversion |
| **eCal** | Calendar and scheduler with events and reminders |
| **eFiles** | File manager with tree view, copy/move/delete |
| **eConverter** | Unit converter (length, weight, temp, voltage, hex/dec/bin) |
| **eBuffer** | Clipboard manager with history and pinned items |
| **eClock** | World clock, alarm, stopwatch, timer |
| **eCleaner** | Storage analyzer and temp file cleaner |
| **eTools** | System info, process list, memory viewer, hex editor |
| **ePaint** | Drawing editor with brushes, layers, shapes |
| **ePDF** | PDF viewer with page nav, zoom, text search |
| **eZip** | Archive manager (ZIP, TAR, GZ, BZ2) |
| **eViewer** | Image viewer with thumbnails and slideshow |

### Media (5)

| App | Description |
|-----|-------------|
| **eMusic** | Audio player with playlist and equalizer |
| **eVideo** | Video player with HW decoding and subtitles |
| **eGallery** | Image gallery with slideshow and EXIF |
| **ePlay** | Unified media center hub |
| **eTimer** | Countdown timer and stopwatch |

### Games (11)

| App | Description |
|-----|-------------|
| **Snake** | Classic snake with speed progression |
| **Tetris** | Falling blocks with rotation and line clear |
| **Minesweeper** | Mine-clearing with 3 difficulty grids |
| **Dice** | Dice roller with custom sides and stats |
| **eChess** | Chess with AI opponent (minimax) |
| **eRunner** | Endless runner with obstacles and power-ups |
| **eCrush** | Match-3 puzzle with combos and levels |
| **eBirds** | Physics launcher with destructible environments |
| **eBlocks** | Block-breaker with paddle and power-ups |
| **eSlice** | Swipe-to-slice with fruits and combos |
| **eVirusTower** | Tower defense with virus waves and upgrades |

### Connectivity (7)

| App | Description |
|-----|-------------|
| **eChat** | Messaging with EIPC transport and encryption |
| **eSSH** | SSH terminal with tabs and key auth |
| **eVNC** | VNC remote desktop viewer |
| **eWeb** | Web browser with HTML rendering |
| **eSerial** | Serial monitor with hex view and logging |
| **eVPN** | VPN client (WireGuard/OpenVPN) |
| **eTunnel** | SSH tunneling with SOCKS proxy |

### Security & System (2)

| App | Description |
|-----|-------------|
| **eGuard** | Firewall with rule editor and connection monitor |
| **Suite** | App launcher hub with search and categories |

---

## 🎯 Platform Support

| Platform | Port | Backend | Output |
|----------|------|---------|--------|
| Windows | `sdl2` | SDL2 + OpenGL | `.exe` |
| Linux | `sdl2` | SDL2 + X11/Wayland | ELF binary |
| macOS | `sdl2` | SDL2 + Metal | `.app` |
| EoS (embedded) | `eos` | Framebuffer / display HAL | Firmware image |
| Web (any browser) | `web` | Emscripten → WASM | HTML + WASM |

---

## 🏗 Architecture

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
│   ├── ecal/                 #   Calculator
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

## 🔨 Build Flags

| Flag | Description |
|------|-------------|
| `EAPPS_PORT` | Target port: `sdl2`, `eos`, `web` |
| `BUILD_TESTING` | Enable unit tests (standard CMake variable) |
| `EAPPS_BUILD_STANDALONE` | Per-app standalone executables (OFF by default) |
| `EAPPS_BUILD_PRODUCTIVITY` | ecal, enote, econverter, ebuffer, efiles, ecleaner, eclock, etools, etimer, epdf, ezip, eviewer, esession |
| `EAPPS_BUILD_MEDIA` | emusic, evideo, egallery, eplay, epaint |
| `EAPPS_BUILD_GAMES` | snake, tetris, minesweeper, dice, echess, erunner, ecrush, ebirds, eblocks, eslice, evirustower |

---

## 🧪 Tests

```bash
cmake -B build -DEAPPS_PORT=sdl2 -DBUILD_TESTING=ON
cmake --build build
ctest --test-dir build --output-on-failure
```

| Test | Covers |
|------|--------|
| `test_math_utils` | Math helpers, clamp, lerp, remap |
| `test_string_utils` | String trim, split, join, format |
| `test_date_utils` | Date formatting, parsing, relative time |
| `test_expr_parser` | Expression evaluation (calculator backend) |
| `test_registry` | App registration, lookup, enumeration |
| `test_prefs` | Preferences save/load/delete |
| `test_game_engine` | Game loop, sprite, collision detection |

---

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
| [Platform Guide](docs/platform-guide.md) | Platform-specific build and deployment notes |

---

## Related Projects

| Project | Repository | Purpose |
|---|---|---|
| **eos** | [embeddedos-org/eos](https://github.com/embeddedos-org/eos) | Embedded OS — provides HAL for display/input |
| **eboot** | [embeddedos-org/eboot](https://github.com/embeddedos-org/eboot) | Bootloader — secure boot, A/B slots |
| **ebuild** | [embeddedos-org/ebuild](https://github.com/embeddedos-org/ebuild) | Build system — SDK generator, packaging |
| **eipc** | [embeddedos-org/eipc](https://github.com/embeddedos-org/eipc) | IPC framework — Go + C SDK, HMAC auth |
| **eai** | [embeddedos-org/eai](https://github.com/embeddedos-org/eai) | AI layer — LLM inference, agent loop |
| **eni** | [embeddedos-org/eni](https://github.com/embeddedos-org/eni) | Neural interface — BCI, Neuralink adapter |
| **eosim** | [embeddedos-org/eosim](https://github.com/embeddedos-org/eosim) | Multi-architecture simulator |
| **EoStudio** | [embeddedos-org/EoStudio](https://github.com/embeddedos-org/EoStudio) | Design suite with LLM integration |

## Standards Compliance

This project is part of the EoS ecosystem and aligns with international standards including ISO/IEC/IEEE 15288:2023, ISO/IEC 12207, ISO/IEC/IEEE 42010, ISO/IEC 25000, ISO/IEC 25010, ISO/IEC 27001, ISO/IEC 15408, IEC 61508, ISO 26262, DO-178C, FIPS 140-3, POSIX (IEEE 1003), WCAG 2.1, and more. See the [EoS Compliance Documentation](https://github.com/embeddedos-org/.github/tree/master/docs/compliance) for full details including NTIA SBOM, SPDX, CycloneDX, and OpenChain compliance.

## 📜 License

MIT License — see [LICENSE](LICENSE) for details.
