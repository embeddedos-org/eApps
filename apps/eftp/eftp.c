// SPDX-License-Identifier: MIT
#include "eftp.h"
#include <stdbool.h>
static bool eftp_init(lv_obj_t *parent) { (void)parent; return true; }
static void eftp_deinit(void) { }
static void eftp_on_show(void) { }
static void eftp_on_hide(void) { }
const eapps_app_info_t eftp_info = {
    .id = "eftp", .name = "eFTP", .icon = "ftp",
    .description = "FTP file transfer client", .category = EAPPS_CAT_CONNECTIVITY, .version = "2.0.0",
};
const eapps_app_lifecycle_t eftp_lifecycle = {
    .init = eftp_init, .deinit = eftp_deinit,
    .on_show = eftp_on_show, .on_hide = eftp_on_hide,
};