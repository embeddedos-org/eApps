// SPDX-License-Identifier: MIT
#include "echess.h"
#include <stdbool.h>
static bool echess_init(lv_obj_t *parent) { (void)parent; return true; }
static void echess_deinit(void) { }
static void echess_on_show(void) { }
static void echess_on_hide(void) { }
const eapps_app_info_t echess_info = {
    .id = "echess", .name = "eChess", .icon = "chs",
    .description = "Chess with full move validation", .category = EAPPS_CAT_GAMES, .version = "2.0.0",
};
const eapps_app_lifecycle_t echess_lifecycle = {
    .init = echess_init, .deinit = echess_deinit,
    .on_show = echess_on_show, .on_hide = echess_on_hide,
};