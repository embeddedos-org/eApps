# Porting Guide

## Adding a New Platform Target

To add support for a new platform (e.g., a new RTOS or embedded board):

### 1. Create Port Directory

```
port/<platform_name>/
├── lv_port_disp_<name>.c    # LVGL display driver
├── lv_port_indev_<name>.c   # LVGL input device driver
└── main_<name>.c            # Entry point
```

### 2. Implement Display Driver

Your display driver must provide a flush callback for LVGL:

```c
void lv_port_disp_<name>_init(void) {
    // 1. Initialize your display hardware
    // 2. Create LVGL display with lv_display_create()
    // 3. Set resolution and flush callback
    // 4. Allocate draw buffers
}
```

### 3. Implement Input Driver

Map your platform's input (touch, buttons, mouse) to LVGL:

```c
void lv_port_indev_<name>_init(void) {
    // 1. Initialize input hardware
    // 2. Create LVGL indev with lv_indev_create()
    // 3. Set read callback
}
```

### 4. Implement Platform Abstraction

Create `core/platform/src/platform_<name>.c` implementing all functions from `platform.h`:
- `eapps_tick_get_ms()` — Required for LVGL tick
- `eapps_clipboard_get/set()` — Optional
- `eapps_sysinfo_*()` — Optional
- `eapps_keepawake_*()` — Optional

### 5. Create CMake Toolchain

Add `cmake/<name>.cmake` with cross-compiler settings.

### 6. Update CMakeLists

Add platform detection in root `CMakeLists.txt` and selection in `port/CMakeLists.txt`.

### 7. Build & Test

```bash
cmake -B build-<name> -DCMAKE_TOOLCHAIN_FILE=cmake/<name>.cmake
cmake --build build-<name>
```
