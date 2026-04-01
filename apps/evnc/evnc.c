// SPDX-License-Identifier: MIT
#include "evnc.h"
#include <stdbool.h>
static bool evnc_init(lv_obj_t *parent) { (void)parent; return true; }
static void evnc_deinit(void) { }
static void evnc_on_show(void) { }
static void evnc_on_hide(void) { }
const eapps_app_info_t evnc_info = {
    .id = "evnc", .name = "eVNC", .icon = "vnc",
    .description = "VNC remote desktop client", .category = EAPPS_CAT_CONNECTIVITY, .version = "2.0.0",
};
const eapps_app_lifecycle_t evnc_lifecycle = {
    .init = evnc_init, .deinit = evnc_deinit,
    .on_show = evnc_on_show, .on_hide = evnc_on_hide,
};