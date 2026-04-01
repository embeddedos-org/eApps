// SPDX-License-Identifier: MIT
#include "essh.h"
#include <stdbool.h>
static bool essh_init(lv_obj_t *parent) { (void)parent; return true; }
static void essh_deinit(void) { }
static void essh_on_show(void) { }
static void essh_on_hide(void) { }
const eapps_app_info_t essh_info = {
    .id = "essh", .name = "eSSH", .icon = "ssh",
    .description = "SSH terminal client", .category = EAPPS_CAT_CONNECTIVITY, .version = "2.0.0",
};
const eapps_app_lifecycle_t essh_lifecycle = {
    .init = essh_init, .deinit = essh_deinit,
    .on_show = essh_on_show, .on_hide = essh_on_hide,
};