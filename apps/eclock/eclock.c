// SPDX-License-Identifier: MIT
#include "eclock.h"
#include <stdbool.h>
static bool eclock_init(lv_obj_t *parent) { (void)parent; return true; }
static void eclock_deinit(void) { }
static void eclock_on_show(void) { }
static void eclock_on_hide(void) { }
const eapps_app_info_t eclock_info = {
    .id = "eclock", .name = "eClock", .icon = "clk",
    .description = "Clock with stopwatch and timer", .category = EAPPS_CAT_PRODUCTIVITY, .version = "2.0.0",
};
const eapps_app_lifecycle_t eclock_lifecycle = {
    .init = eclock_init, .deinit = eclock_deinit,
    .on_show = eclock_on_show, .on_hide = eclock_on_hide,
};