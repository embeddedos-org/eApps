# eBrowser Architecture

## Overview

eBrowser is a lightweight web browser engine for embedded and IoT devices. It follows a layered architecture that separates concerns and allows individual components to be replaced or configured for different hardware targets.

## Architecture Diagram

```
┌─────────────────────────────────────────────┐
│               Browser UI                     │
│   (address bar, tabs, navigation, status)    │
├─────────────────────────────────────────────┤
│    Core Engine (HTML / CSS / Layout / JS)    │
├──────────────┬──────────────┬───────────────┤
│  Rendering   │   Network    │    Input      │
│  Backend     │   Stack      │    Layer      │
├──────────────┴──────────────┴───────────────┤
│       Platform Abstraction Layer (PAL)      │
├─────────────────────────────────────────────┤
│          OS / Hardware / Drivers             │
└─────────────────────────────────────────────┘
```

## Modules

### Core Engine (`src/engine/`)

| Component | File | Description |
|-----------|------|-------------|
| DOM | `dom.c` | Document Object Model tree — element, text, comment nodes with attributes |
| HTML Parser | `html_parser.c` | Tokenizer + tree-building parser supporting HTML5 void elements, attributes, comments |
| CSS Parser | `css_parser.c` | Stylesheet parser with selector matching, 15+ CSS properties, named colors |
| Layout Engine | `layout.c` | Block/inline layout algorithm computing box positions from styled DOM |

### Rendering Backend (`src/render/`)

Paints layout boxes to an LVGL canvas. Supports:
- Background color fills
- Text rendering
- Border painting
- Recursive box tree traversal

### Network Stack (`src/network/`)

| Component | File | Description |
|-----------|------|-------------|
| URL Parser | `url.c` | Parses scheme, host, port, path, query, fragment; supports relative URL resolution |
| HTTP Client | `http.c` | HTTP/1.1 GET/POST with POSIX sockets, Winsock, and stub backends |

### Input Layer (`src/input/`)

Callback-based input system supporting pointer, keyboard, and touch events.

### Platform Abstraction Layer (`platform/`)

Provides OS-portable APIs for:
- Monotonic clock (`eb_platform_tick_ms`)
- Sleep (`eb_platform_sleep_ms`)
- Memory allocation
- File I/O
- Platform detection

### Browser UI (`src/browser/`)

Full browser chrome with:
- Navigation buttons (back, forward, reload, home)
- URL address bar with submit-on-enter
- Tab bar supporting up to 8 tabs
- Page rendering area
- Status bar
- History navigation (back/forward)
- Built-in home page (`about:home`)

### Port Layer (`port/`)

Platform-specific entry points:
- **SDL2** (`port/sdl2/`) — Desktop simulator with SDL2 event loop
- **EoS** (`port/eos/`) — Embedded OS integration (init/tick/deinit)
- **Web** (`port/web/`) — Emscripten/WASM with `emscripten_set_main_loop`

## Build System

CMake-based with feature flags:
- `eBrowser_BUILD_ENGINE` — Core HTML/CSS/Layout
- `eBrowser_BUILD_RENDER` — LVGL rendering
- `eBrowser_BUILD_NETWORK` — HTTP client
- `eBrowser_BUILD_INPUT` — Input abstraction
- `eBrowser_BUILD_BROWSER` — Browser UI
- `eBrowser_BUILD_JS` — Optional JS engine (future)
- `eBrowser_BUILD_STANDALONE` — Standalone executable

## Data Flow

```
URL → HTTP GET → HTML bytes → Tokenizer → Parser → DOM tree
                                                      ↓
                                CSS Parser → Stylesheet
                                                      ↓
                                Style Resolution → Styled DOM
                                                      ↓
                                Layout Engine → Box tree (x,y,w,h)
                                                      ↓
                                Renderer → LVGL Canvas → Display
```
