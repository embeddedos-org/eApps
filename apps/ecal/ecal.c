// SPDX-License-Identifier: MIT
#include "ecal.h"
#include <stdbool.h>
static bool ecal_init(lv_obj_t *parent) { (void)parent; return true; }
static void ecal_deinit(void) { }
static void ecal_on_show(void) { }
static void ecal_on_hide(void) { }
const eapps_app_info_t ecal_info = {
    .id = "ecal", .name = "eCalc", .icon = "calc",
    .description = "Scientific calculator", .category = EAPPS_CAT_PRODUCTIVITY, .version = "2.0.0",
};
const eapps_app_lifecycle_t ecal_lifecycle = {
    .init = ecal_init, .deinit = ecal_deinit,
    .on_show = ecal_on_show, .on_hide = ecal_on_hide,
};