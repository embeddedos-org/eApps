# eApps Architecture

## Layer Diagram

```
┌─────────────────────────────────────────────────┐
│                  Suite Launcher                  │
│          (apps/suite/ — app grid + tabs)          │
├─────────────────────────────────────────────────┤
│                   38 Apps                        │
│  Productivity │ Media │ Games │ Connectivity │...│
├─────────────────────────────────────────────────┤
│                 Core Libraries                   │
│  eapps_ui    │ eapps_common │ eapps_storage     │
│  eapps_network │ eapps_platform                 │
├─────────────────────────────────────────────────┤
│                   LVGL v9.x                      │
│          (UI framework — extern/lvgl/)           │
├─────────────────────────────────────────────────┤
│                  Port Layer                      │
│     SDL2 (Desktop) │ EoS (Embedded) │ Web       │
├─────────────────────────────────────────────────┤
│              Platform / Hardware                 │
│  Linux/Win/macOS │ EoS HAL │ Emscripten/Browser │
└─────────────────────────────────────────────────┘
```

## Data Flow

1. **Startup:** `main_<platform>.c` → `lv_init()` → `eapps_theme_init()` → `eapps_registry_init()` → `suite_init()`
2. **App Launch:** User taps card → `eapps_registry_get_lifecycle(id)` → `lifecycle->init(container)` → app creates LVGL widgets
3. **App Exit:** Back button → `lifecycle->deinit()` → delete container → return to suite grid
4. **Input:** Platform indev driver → LVGL event system → app event handlers
5. **Rendering:** LVGL → `lv_timer_handler()` → flush callback → platform display driver

## Memory Budget

- **LVGL heap:** 64KB (configurable via `LV_MEM_SIZE` in `lv_conf.h`)
- **App static data:** ~1–5KB per app
- **Game objects:** 128 max × ~40 bytes = ~5KB
- **Canvas strokes:** 256 max × ~1KB = ~256KB (ePaint only)
- **Total RAM target:** < 512KB for embedded; unlimited for desktop/web

## Build Targets

| Platform | Toolchain | Binary Size | Notes |
|----------|-----------|-------------|-------|
| Desktop  | GCC/Clang/MSVC + SDL2 | 2–5MB | Full suite |
| EoS      | arm-none-eabi-gcc | 500KB–2MB | Cross-compiled |
| Web      | Emscripten | 1–3MB WASM | Browser canvas |
| Standalone | Any | 500KB–1MB each | Per-app binary |
