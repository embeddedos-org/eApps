// SPDX-License-Identifier: MIT
#include "evirustower.h"
#include <stdbool.h>
static bool evirustower_init(lv_obj_t *parent) { (void)parent; return true; }
static void evirustower_deinit(void) { }
static void evirustower_on_show(void) { }
static void evirustower_on_hide(void) { }
const eapps_app_info_t evirustower_info = {
    .id = "evirustower", .name = "eVirusTower", .icon = "vir",
    .description = "Antivirus scanner", .category = EAPPS_CAT_SECURITY, .version = "2.0.0",
};
const eapps_app_lifecycle_t evirustower_lifecycle = {
    .init = evirustower_init, .deinit = evirustower_deinit,
    .on_show = evirustower_on_show, .on_hide = evirustower_on_hide,
};