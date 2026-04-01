// SPDX-License-Identifier: MIT
#include "etools.h"
#include <stdbool.h>
static bool etools_init(lv_obj_t *parent) { (void)parent; return true; }
static void etools_deinit(void) { }
static void etools_on_show(void) { }
static void etools_on_hide(void) { }
const eapps_app_info_t etools_info = {
    .id = "etools", .name = "eTools", .icon = "tool",
    .description = "Unit converter compass level", .category = EAPPS_CAT_PRODUCTIVITY, .version = "2.0.0",
};
const eapps_app_lifecycle_t etools_lifecycle = {
    .init = etools_init, .deinit = etools_deinit,
    .on_show = etools_on_show, .on_hide = etools_on_hide,
};