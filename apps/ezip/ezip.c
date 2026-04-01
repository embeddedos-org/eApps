// SPDX-License-Identifier: MIT
#include "ezip.h"
#include <stdbool.h>
static bool ezip_init(lv_obj_t *parent) { (void)parent; return true; }
static void ezip_deinit(void) { }
static void ezip_on_show(void) { }
static void ezip_on_hide(void) { }
const eapps_app_info_t ezip_info = {
    .id = "ezip", .name = "eZip", .icon = "zip",
    .description = "Archive create and extract", .category = EAPPS_CAT_PRODUCTIVITY, .version = "2.0.0",
};
const eapps_app_lifecycle_t ezip_lifecycle = {
    .init = ezip_init, .deinit = ezip_deinit,
    .on_show = ezip_on_show, .on_hide = ezip_on_hide,
};