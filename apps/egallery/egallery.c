// SPDX-License-Identifier: MIT
#include "egallery.h"
#include <stdbool.h>
static bool egallery_init(lv_obj_t *parent) { (void)parent; return true; }
static void egallery_deinit(void) { }
static void egallery_on_show(void) { }
static void egallery_on_hide(void) { }
const eapps_app_info_t egallery_info = {
    .id = "egallery", .name = "eGallery", .icon = "gal",
    .description = "Image gallery viewer", .category = EAPPS_CAT_MEDIA, .version = "2.0.0",
};
const eapps_app_lifecycle_t egallery_lifecycle = {
    .init = egallery_init, .deinit = egallery_deinit,
    .on_show = egallery_on_show, .on_hide = egallery_on_hide,
};