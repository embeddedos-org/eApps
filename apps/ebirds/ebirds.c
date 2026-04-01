// SPDX-License-Identifier: MIT
#include "ebirds.h"
#include <stdbool.h>
static bool ebirds_init(lv_obj_t *parent) { (void)parent; return true; }
static void ebirds_deinit(void) { }
static void ebirds_on_show(void) { }
static void ebirds_on_hide(void) { }
const eapps_app_info_t ebirds_info = {
    .id = "ebirds", .name = "eBirds", .icon = "brd",
    .description = "Slingshot physics game", .category = EAPPS_CAT_GAMES, .version = "2.0.0",
};
const eapps_app_lifecycle_t ebirds_lifecycle = {
    .init = ebirds_init, .deinit = ebirds_deinit,
    .on_show = ebirds_on_show, .on_hide = ebirds_on_hide,
};