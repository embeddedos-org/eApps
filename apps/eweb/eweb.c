// SPDX-License-Identifier: MIT
#include "eweb.h"
#include <stdbool.h>
static bool eweb_init(lv_obj_t *parent) { (void)parent; return true; }
static void eweb_deinit(void) { }
static void eweb_on_show(void) { }
static void eweb_on_hide(void) { }
const eapps_app_info_t eweb_info = {
    .id = "eweb", .name = "eWeb", .icon = "web",
    .description = "Web browser", .category = EAPPS_CAT_WEB, .version = "2.0.0",
};
const eapps_app_lifecycle_t eweb_lifecycle = {
    .init = eweb_init, .deinit = eweb_deinit,
    .on_show = eweb_on_show, .on_hide = eweb_on_hide,
};