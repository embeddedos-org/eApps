# Adding a New App

## Step-by-Step Guide

### 1. Create App Directory

```
apps/<app_id>/
├── <app_id>.h         # Header with extern info/lifecycle
├── <app_id>.c         # Implementation
└── CMakeLists.txt     # Build config
```

### 2. Header File Template

```c
#ifndef EAPPS_APP_<APP_ID>_H
#define EAPPS_APP_<APP_ID>_H
#include "eapps/types.h"
extern const eapps_app_info_t <app_id>_info;
extern const eapps_app_lifecycle_t <app_id>_lifecycle;
#endif
```

### 3. Source File Template

```c
#include "<app_id>.h"
#include <stdbool.h>

static bool <app_id>_init(lv_obj_t *parent) {
    // Create your LVGL UI here using parent as the container
    // Use eapps_card_create(), eapps_button_create(), etc.
    return true;
}

static void <app_id>_deinit(void) {
    // Cleanup resources
}

static void <app_id>_on_show(void) { }
static void <app_id>_on_hide(void) { }

const eapps_app_info_t <app_id>_info = {
    .id = "<app_id>",
    .name = "App Name",
    .icon = "icon",
    .description = "Short description",
    .category = EAPPS_CAT_PRODUCTIVITY,  // or MEDIA, GAMES, etc.
    .version = "2.0.0",
};

const eapps_app_lifecycle_t <app_id>_lifecycle = {
    .init = <app_id>_init,
    .deinit = <app_id>_deinit,
    .on_show = <app_id>_on_show,
    .on_hide = <app_id>_on_hide,
};
```

### 4. CMakeLists.txt

```cmake
add_library(<app_id> STATIC <app_id>.c)
target_include_directories(<app_id> PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
target_link_libraries(<app_id> PUBLIC eapps_ui)
```

### 5. Register in Suite

Add extern declarations and `REG(<app_id>)` call in `apps/suite/suite.c`.

### 6. Add to Root CMakeLists.txt

Add `add_subdirectory(apps/<app_id>)` under the appropriate category flag.

### 7. Link in Suite CMakeLists.txt

Add `<app_id>` to the appropriate `SUITE_LINK_LIBS` list in `apps/suite/CMakeLists.txt`.
