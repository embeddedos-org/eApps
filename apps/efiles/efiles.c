// SPDX-License-Identifier: MIT
#include "efiles.h"
#include <stdbool.h>
static bool efiles_init(lv_obj_t *parent) { (void)parent; return true; }
static void efiles_deinit(void) { }
static void efiles_on_show(void) { }
static void efiles_on_hide(void) { }
const eapps_app_info_t efiles_info = {
    .id = "efiles", .name = "eFiles", .icon = "dir",
    .description = "File browser and manager", .category = EAPPS_CAT_PRODUCTIVITY, .version = "2.0.0",
};
const eapps_app_lifecycle_t efiles_lifecycle = {
    .init = efiles_init, .deinit = efiles_deinit,
    .on_show = efiles_on_show, .on_hide = efiles_on_hide,
};