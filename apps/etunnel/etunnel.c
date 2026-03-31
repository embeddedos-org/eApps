// SPDX-License-Identifier: MIT
#include "etunnel.h"
#include <stdbool.h>
static bool etunnel_init(lv_obj_t *parent) { (void)parent; return true; }
static void etunnel_deinit(void) { }
static void etunnel_on_show(void) { }
static void etunnel_on_hide(void) { }
const eapps_app_info_t etunnel_info = {
    .id = "etunnel", .name = "eTunnel", .icon = "tun",
    .description = "SSH tunnel manager", .category = EAPPS_CAT_CONNECTIVITY, .version = "2.0.0",
};
const eapps_app_lifecycle_t etunnel_lifecycle = {
    .init = etunnel_init, .deinit = etunnel_deinit,
    .on_show = etunnel_on_show, .on_hide = etunnel_on_hide,
};