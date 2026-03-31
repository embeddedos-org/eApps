// SPDX-License-Identifier: MIT
#include "evideo.h"
#include <stdbool.h>
static bool evideo_init(lv_obj_t *parent) { (void)parent; return true; }
static void evideo_deinit(void) { }
static void evideo_on_show(void) { }
static void evideo_on_hide(void) { }
const eapps_app_info_t evideo_info = {
    .id = "evideo", .name = "eVideo", .icon = "vid",
    .description = "Video player with seek", .category = EAPPS_CAT_MEDIA, .version = "2.0.0",
};
const eapps_app_lifecycle_t evideo_lifecycle = {
    .init = evideo_init, .deinit = evideo_deinit,
    .on_show = evideo_on_show, .on_hide = evideo_on_hide,
};