// SPDX-License-Identifier: MIT
#include "eplay.h"
#include <stdbool.h>
static bool eplay_init(lv_obj_t *parent) { (void)parent; return true; }
static void eplay_deinit(void) { }
static void eplay_on_show(void) { }
static void eplay_on_hide(void) { }
const eapps_app_info_t eplay_info = {
    .id = "eplay", .name = "ePlay", .icon = "play",
    .description = "Media playlist player", .category = EAPPS_CAT_MEDIA, .version = "2.0.0",
};
const eapps_app_lifecycle_t eplay_lifecycle = {
    .init = eplay_init, .deinit = eplay_deinit,
    .on_show = eplay_on_show, .on_hide = eplay_on_hide,
};