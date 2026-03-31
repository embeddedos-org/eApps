// SPDX-License-Identifier: MIT
#include "erunner.h"
#include <stdbool.h>
static bool erunner_init(lv_obj_t *parent) { (void)parent; return true; }
static void erunner_deinit(void) { }
static void erunner_on_show(void) { }
static void erunner_on_hide(void) { }
const eapps_app_info_t erunner_info = {
    .id = "erunner", .name = "eRunner", .icon = "run",
    .description = "Endless runner game", .category = EAPPS_CAT_GAMES, .version = "2.0.0",
};
const eapps_app_lifecycle_t erunner_lifecycle = {
    .init = erunner_init, .deinit = erunner_deinit,
    .on_show = erunner_on_show, .on_hide = erunner_on_hide,
};