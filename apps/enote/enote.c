// SPDX-License-Identifier: MIT
#include "enote.h"
#include <stdbool.h>
static bool enote_init(lv_obj_t *parent) { (void)parent; return true; }
static void enote_deinit(void) { }
static void enote_on_show(void) { }
static void enote_on_hide(void) { }
const eapps_app_info_t enote_info = {
    .id = "enote", .name = "eNote", .icon = "note",
    .description = "Notepad with persistence", .category = EAPPS_CAT_PRODUCTIVITY, .version = "2.0.0",
};
const eapps_app_lifecycle_t enote_lifecycle = {
    .init = enote_init, .deinit = enote_deinit,
    .on_show = enote_on_show, .on_hide = enote_on_hide,
};