// SPDX-License-Identifier: MIT
#include "eblocks.h"
#include <stdbool.h>
static bool eblocks_init(lv_obj_t *parent) { (void)parent; return true; }
static void eblocks_deinit(void) { }
static void eblocks_on_show(void) { }
static void eblocks_on_hide(void) { }
const eapps_app_info_t eblocks_info = {
    .id = "eblocks", .name = "eBlocks", .icon = "blk",
    .description = "Block puzzle game", .category = EAPPS_CAT_GAMES, .version = "2.0.0",
};
const eapps_app_lifecycle_t eblocks_lifecycle = {
    .init = eblocks_init, .deinit = eblocks_deinit,
    .on_show = eblocks_on_show, .on_hide = eblocks_on_hide,
};