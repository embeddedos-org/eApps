// SPDX-License-Identifier: MIT
#include "minesweeper.h"
#include <stdbool.h>
static bool minesweeper_init(lv_obj_t *parent) { (void)parent; return true; }
static void minesweeper_deinit(void) { }
static void minesweeper_on_show(void) { }
static void minesweeper_on_hide(void) { }
const eapps_app_info_t minesweeper_info = {
    .id = "minesweeper", .name = "Minesweeper", .icon = "mns",
    .description = "Mine avoidance puzzle", .category = EAPPS_CAT_GAMES, .version = "2.0.0",
};
const eapps_app_lifecycle_t minesweeper_lifecycle = {
    .init = minesweeper_init, .deinit = minesweeper_deinit,
    .on_show = minesweeper_on_show, .on_hide = minesweeper_on_hide,
};