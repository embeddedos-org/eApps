// SPDX-License-Identifier: MIT
#include "tetris.h"
#include <stdbool.h>
static bool tetris_init(lv_obj_t *parent) { (void)parent; return true; }
static void tetris_deinit(void) { }
static void tetris_on_show(void) { }
static void tetris_on_hide(void) { }
const eapps_app_info_t tetris_info = {
    .id = "tetris", .name = "Tetris", .icon = "tet",
    .description = "Block stacking game", .category = EAPPS_CAT_GAMES, .version = "2.0.0",
};
const eapps_app_lifecycle_t tetris_lifecycle = {
    .init = tetris_init, .deinit = tetris_deinit,
    .on_show = tetris_on_show, .on_hide = tetris_on_hide,
};