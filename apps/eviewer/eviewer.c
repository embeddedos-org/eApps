// SPDX-License-Identifier: MIT
#include "eviewer.h"
#include <stdbool.h>
static bool eviewer_init(lv_obj_t *parent) { (void)parent; return true; }
static void eviewer_deinit(void) { }
static void eviewer_on_show(void) { }
static void eviewer_on_hide(void) { }
const eapps_app_info_t eviewer_info = {
    .id = "eviewer", .name = "eViewer", .icon = "eye",
    .description = "File content viewer", .category = EAPPS_CAT_PRODUCTIVITY, .version = "2.0.0",
};
const eapps_app_lifecycle_t eviewer_lifecycle = {
    .init = eviewer_init, .deinit = eviewer_deinit,
    .on_show = eviewer_on_show, .on_hide = eviewer_on_hide,
};