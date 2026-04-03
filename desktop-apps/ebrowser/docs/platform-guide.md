# Platform Guide

## Supported Platforms

| Platform | Toolchain | Entry Point | Notes |
|----------|-----------|-------------|-------|
| Desktop (Linux/macOS/Windows) | GCC / Clang / MSVC | `port/sdl2/main_sdl2.c` | SDL2 required |
| EoS Embedded | arm-none-eabi-gcc | `port/eos/main_eos.c` | Uses EoS HAL |
| Web (WASM) | Emscripten | `port/web/main_web.c` | Runs in browser |

## Building for Desktop (SDL2)

```bash
mkdir build && cd build
cmake ..
make
./eBrowser https://example.com
```

## Cross-Compiling for EoS

```bash
cmake -DCMAKE_TOOLCHAIN_FILE=../cmake/eos.cmake \
      -DEOS_TARGET_ARCH=arm ..
make
```

The EoS port provides three functions for integration:
- `eBrowser_eos_main()` — Initialize LVGL + browser
- `eBrowser_eos_tick()` — Call from your main loop
- `eBrowser_eos_deinit()` — Clean up

## Building for Web (Emscripten)

```bash
emcmake cmake -DCMAKE_TOOLCHAIN_FILE=../cmake/emscripten.cmake ..
emmake make
```

Output: `eBrowser_web.html`, `eBrowser_web.js`, `eBrowser_web.wasm`

## Platform Abstraction

All platform-specific code is isolated in `platform/platform.c` using preprocessor guards:

| API | Linux | Windows | EoS | Web |
|-----|-------|---------|-----|-----|
| `eb_platform_tick_ms()` | `clock_gettime` | `GetTickCount` | Stub | Stub |
| `eb_platform_sleep_ms()` | `usleep` | `Sleep` | Stub | Stub |
| `eb_platform_file_exists()` | `stat` | `GetFileAttributes` | Stub | Stub |
| Network | POSIX sockets | Winsock | Stub | Stub |

## Feature Flags

Disable features to reduce binary size:

```bash
cmake -DeBrowser_BUILD_JS=OFF \
      -DeBrowser_BUILD_NETWORK=OFF ..
```

## Memory Considerations

eBrowser is designed for constrained environments:
- DOM nodes: 64 children max, 16 attributes max
- Layout boxes: 512 max
- Tabs: 8 max
- History: 64 entries max
- All string buffers have fixed maximum sizes
