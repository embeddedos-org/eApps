// SPDX-License-Identifier: MIT
#include "eserial.h"
#include <stdbool.h>
static bool eserial_init(lv_obj_t *parent) { (void)parent; return true; }
static void eserial_deinit(void) { }
static void eserial_on_show(void) { }
static void eserial_on_hide(void) { }
const eapps_app_info_t eserial_info = {
    .id = "eserial", .name = "eSerial", .icon = "ser",
    .description = "Serial port terminal", .category = EAPPS_CAT_CONNECTIVITY, .version = "2.0.0",
};
const eapps_app_lifecycle_t eserial_lifecycle = {
    .init = eserial_init, .deinit = eserial_deinit,
    .on_show = eserial_on_show, .on_hide = eserial_on_hide,
};