// SPDX-License-Identifier: MIT
#include "eapps/platform.h"
#include "eapps/theme.h"
#include "eapps/registry.h"

int main(void) {
    /* eos_hal_init() */
    eapps_theme_init(false);
    eapps_registry_init();

    /* lv_init → lv_port_disp_eos_init → lv_port_indev_eos_init
     * → suite_init → eos_task_create(lvgl_task) */

    while (1) { /* lv_timer_handler(); eos_task_delay(5); */ }
    return 0;
}
