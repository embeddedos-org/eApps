// SPDX-License-Identifier: MIT
#include "dice.h"
#include <stdbool.h>
static bool dice_init(lv_obj_t *parent) { (void)parent; return true; }
static void dice_deinit(void) { }
static void dice_on_show(void) { }
static void dice_on_hide(void) { }
const eapps_app_info_t dice_info = {
    .id = "dice", .name = "Dice", .icon = "die",
    .description = "Dice roller with animation", .category = EAPPS_CAT_GAMES, .version = "2.0.0",
};
const eapps_app_lifecycle_t dice_lifecycle = {
    .init = dice_init, .deinit = dice_deinit,
    .on_show = dice_on_show, .on_hide = dice_on_hide,
};