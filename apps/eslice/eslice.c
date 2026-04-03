// SPDX-License-Identifier: MIT
#include "eslice.h"
#include <stdbool.h>
static bool eslice_init(lv_obj_t *parent) { (void)parent; return true; }
static void eslice_deinit(void) { }
static void eslice_on_show(void) { }
static void eslice_on_hide(void) { }
const eapps_app_info_t eslice_info = {
    .id = "eslice", .name = "eSlice", .icon = "slc",
    .description = "Fruit slicing game", .category = EAPPS_CAT_GAMES, .version = "2.0.0",
};
const eapps_app_lifecycle_t eslice_lifecycle = {
    .init = eslice_init, .deinit = eslice_deinit,
    .on_show = eslice_on_show, .on_hide = eslice_on_hide,
};