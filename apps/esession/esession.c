// SPDX-License-Identifier: MIT
#include "esession.h"
#include <stdbool.h>
static bool esession_init(lv_obj_t *parent) { (void)parent; return true; }
static void esession_deinit(void) { }
static void esession_on_show(void) { }
static void esession_on_hide(void) { }
const eapps_app_info_t esession_info = {
    .id = "esession", .name = "eSession", .icon = "ses",
    .description = "Session manager", .category = EAPPS_CAT_PRODUCTIVITY, .version = "2.0.0",
};
const eapps_app_lifecycle_t esession_lifecycle = {
    .init = esession_init, .deinit = esession_deinit,
    .on_show = esession_on_show, .on_hide = esession_on_hide,
};