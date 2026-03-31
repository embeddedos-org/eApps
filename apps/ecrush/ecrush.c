// SPDX-License-Identifier: MIT
#include "ecrush.h"
#include <stdbool.h>
static bool ecrush_init(lv_obj_t *parent) { (void)parent; return true; }
static void ecrush_deinit(void) { }
static void ecrush_on_show(void) { }
static void ecrush_on_hide(void) { }
const eapps_app_info_t ecrush_info = {
    .id = "ecrush", .name = "eCrush", .icon = "crh",
    .description = "Match-3 puzzle game", .category = EAPPS_CAT_GAMES, .version = "2.0.0",
};
const eapps_app_lifecycle_t ecrush_lifecycle = {
    .init = ecrush_init, .deinit = ecrush_deinit,
    .on_show = ecrush_on_show, .on_hide = ecrush_on_hide,
};