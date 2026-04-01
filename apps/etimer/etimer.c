// SPDX-License-Identifier: MIT
#include "etimer.h"
#include <stdbool.h>
static bool etimer_init(lv_obj_t *parent) { (void)parent; return true; }
static void etimer_deinit(void) { }
static void etimer_on_show(void) { }
static void etimer_on_hide(void) { }
const eapps_app_info_t etimer_info = {
    .id = "etimer", .name = "eTimer", .icon = "tmr",
    .description = "Countdown timer with presets", .category = EAPPS_CAT_PRODUCTIVITY, .version = "2.0.0",
};
const eapps_app_lifecycle_t etimer_lifecycle = {
    .init = etimer_init, .deinit = etimer_deinit,
    .on_show = etimer_on_show, .on_hide = etimer_on_hide,
};