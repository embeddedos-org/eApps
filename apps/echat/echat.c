// SPDX-License-Identifier: MIT
#include "echat.h"
#include <stdbool.h>
static bool echat_init(lv_obj_t *parent) { (void)parent; return true; }
static void echat_deinit(void) { }
static void echat_on_show(void) { }
static void echat_on_hide(void) { }
const eapps_app_info_t echat_info = {
    .id = "echat", .name = "eChat", .icon = "chat",
    .description = "Chat messaging client", .category = EAPPS_CAT_CONNECTIVITY, .version = "2.0.0",
};
const eapps_app_lifecycle_t echat_lifecycle = {
    .init = echat_init, .deinit = echat_deinit,
    .on_show = echat_on_show, .on_hide = echat_on_hide,
};