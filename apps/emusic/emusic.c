// SPDX-License-Identifier: MIT
#include "emusic.h"
#include <stdbool.h>
static bool emusic_init(lv_obj_t *parent) { (void)parent; return true; }
static void emusic_deinit(void) { }
static void emusic_on_show(void) { }
static void emusic_on_hide(void) { }
const eapps_app_info_t emusic_info = {
    .id = "emusic", .name = "eMusic", .icon = "mus",
    .description = "Music player with playlists", .category = EAPPS_CAT_MEDIA, .version = "2.0.0",
};
const eapps_app_lifecycle_t emusic_lifecycle = {
    .init = emusic_init, .deinit = emusic_deinit,
    .on_show = emusic_on_show, .on_hide = emusic_on_hide,
};