// SPDX-License-Identifier: MIT
#include "esurfer.h"
#include <stdbool.h>
static bool esurfer_init(lv_obj_t *parent) { (void)parent; return true; }
static void esurfer_deinit(void) { }
static void esurfer_on_show(void) { }
static void esurfer_on_hide(void) { }
const eapps_app_info_t esurfer_info = {
    .id = "esurfer", .name = "eSurfer", .icon = "srf",
    .description = "Lane-based surfer game", .category = EAPPS_CAT_GAMES, .version = "2.0.0",
};
const eapps_app_lifecycle_t esurfer_lifecycle = {
    .init = esurfer_init, .deinit = esurfer_deinit,
    .on_show = esurfer_on_show, .on_hide = esurfer_on_hide,
};