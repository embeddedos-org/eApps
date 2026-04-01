// SPDX-License-Identifier: MIT
#include "epdf.h"
#include <stdbool.h>
static bool epdf_init(lv_obj_t *parent) { (void)parent; return true; }
static void epdf_deinit(void) { }
static void epdf_on_show(void) { }
static void epdf_on_hide(void) { }
const eapps_app_info_t epdf_info = {
    .id = "epdf", .name = "ePDF", .icon = "pdf",
    .description = "PDF page viewer", .category = EAPPS_CAT_PRODUCTIVITY, .version = "2.0.0",
};
const eapps_app_lifecycle_t epdf_lifecycle = {
    .init = epdf_init, .deinit = epdf_deinit,
    .on_show = epdf_on_show, .on_hide = epdf_on_hide,
};