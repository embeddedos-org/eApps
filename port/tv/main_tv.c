// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Meta Platforms, Inc. and affiliates.

#include "lvgl.h"
#include <stdio.h>
#include <stdlib.h>

#define TV_DISP_HOR_RES 1920
#define TV_DISP_VER_RES 1080

extern void lv_port_disp_tv_init(void);
extern void lv_port_disp_tv_deinit(void);
extern void lv_port_indev_tv_init(void);
extern void lv_port_indev_tv_deinit(void);
extern void eapps_suite_init(void);

/**
 * Initialize the eApps TV port.
 */
void eapps_tv_init(void)
{
    lv_init();
    lv_port_disp_tv_init();
    lv_port_indev_tv_init();
    eapps_suite_init();
}

/**
 * Run one LVGL tick step.
 * @return milliseconds until the next call is needed.
 */
uint32_t eapps_tv_step(void)
{
    uint32_t ms = lv_timer_handler();
    return ms;
}

/**
 * Deinitialize the eApps TV port and free resources.
 */
void eapps_tv_deinit(void)
{
    lv_port_indev_tv_deinit();
    lv_port_disp_tv_deinit();
    lv_deinit();
}
