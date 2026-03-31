// SPDX-License-Identifier: MIT
#include "epaint.h"
#include <stdbool.h>
static bool epaint_init(lv_obj_t *parent) { (void)parent; return true; }
static void epaint_deinit(void) { }
static void epaint_on_show(void) { }
static void epaint_on_hide(void) { }
const eapps_app_info_t epaint_info = {
    .id = "epaint", .name = "ePaint", .icon = "pnt",
    .description = "Drawing canvas with tools", .category = EAPPS_CAT_MEDIA, .version = "2.0.0",
};
const eapps_app_lifecycle_t epaint_lifecycle = {
    .init = epaint_init, .deinit = epaint_deinit,
    .on_show = epaint_on_show, .on_hide = epaint_on_hide,
};