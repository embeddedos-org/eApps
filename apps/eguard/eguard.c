// SPDX-License-Identifier: MIT
#include "eguard.h"
#include <stdbool.h>
static bool eguard_init(lv_obj_t *parent) { (void)parent; return true; }
static void eguard_deinit(void) { }
static void eguard_on_show(void) { }
static void eguard_on_hide(void) { }
const eapps_app_info_t eguard_info = {
    .id = "eguard", .name = "eGuard", .icon = "grd",
    .description = "Screen keep-awake guard", .category = EAPPS_CAT_SECURITY, .version = "2.0.0",
};
const eapps_app_lifecycle_t eguard_lifecycle = {
    .init = eguard_init, .deinit = eguard_deinit,
    .on_show = eguard_on_show, .on_hide = eguard_on_hide,
};