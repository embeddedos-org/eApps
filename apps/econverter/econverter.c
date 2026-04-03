// SPDX-License-Identifier: MIT
#include "econverter.h"
#include <stdbool.h>
static bool econverter_init(lv_obj_t *parent) { (void)parent; return true; }
static void econverter_deinit(void) { }
static void econverter_on_show(void) { }
static void econverter_on_hide(void) { }
const eapps_app_info_t econverter_info = {
    .id = "econverter", .name = "eConverter", .icon = "conv",
    .description = "Text and encoding converter", .category = EAPPS_CAT_PRODUCTIVITY, .version = "2.0.0",
};
const eapps_app_lifecycle_t econverter_lifecycle = {
    .init = econverter_init, .deinit = econverter_deinit,
    .on_show = econverter_on_show, .on_hide = econverter_on_hide,
};