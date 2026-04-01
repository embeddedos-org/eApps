// SPDX-License-Identifier: MIT
#include "ecleaner.h"
#include <stdbool.h>
static bool ecleaner_init(lv_obj_t *parent) { (void)parent; return true; }
static void ecleaner_deinit(void) { }
static void ecleaner_on_show(void) { }
static void ecleaner_on_hide(void) { }
const eapps_app_info_t ecleaner_info = {
    .id = "ecleaner", .name = "eCleaner", .icon = "cln",
    .description = "System cleaner and optimizer", .category = EAPPS_CAT_PRODUCTIVITY, .version = "2.0.0",
};
const eapps_app_lifecycle_t ecleaner_lifecycle = {
    .init = ecleaner_init, .deinit = ecleaner_deinit,
    .on_show = ecleaner_on_show, .on_hide = ecleaner_on_hide,
};