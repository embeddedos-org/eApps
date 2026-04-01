// SPDX-License-Identifier: MIT
#include "evpn.h"
#include <stdbool.h>
static bool evpn_init(lv_obj_t *parent) { (void)parent; return true; }
static void evpn_deinit(void) { }
static void evpn_on_show(void) { }
static void evpn_on_hide(void) { }
const eapps_app_info_t evpn_info = {
    .id = "evpn", .name = "eVPN", .icon = "vpn",
    .description = "VPN client with server selection", .category = EAPPS_CAT_SECURITY, .version = "2.0.0",
};
const eapps_app_lifecycle_t evpn_lifecycle = {
    .init = evpn_init, .deinit = evpn_deinit,
    .on_show = evpn_on_show, .on_hide = evpn_on_hide,
};