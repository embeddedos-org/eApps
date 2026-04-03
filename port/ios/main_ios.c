// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Meta Platforms, Inc. and affiliates.

#include "lvgl.h"
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

extern void lv_port_disp_ios_init(void);
extern void lv_port_disp_ios_deinit(void);
extern void lv_port_indev_ios_init(void);
extern void lv_port_indev_ios_deinit(void);
extern void eapps_suite_init(void);

/**
 * Initialize the eApps iOS port.
 * Called from Objective-C/Swift wrapper (CADisplayLink-based).
 */
void eapps_ios_init(void)
{
    lv_init();
    lv_port_disp_ios_init();
    lv_port_indev_ios_init();
    eapps_suite_init();
}

/**
 * Run one LVGL tick step.
 * Called from CADisplayLink callback.
 * @return milliseconds until the next call is needed.
 */
uint32_t eapps_ios_step(void)
{
    uint32_t ms = lv_timer_handler();
    return ms;
}

/**
 * Deinitialize the eApps iOS port and free resources.
 */
void eapps_ios_deinit(void)
{
    lv_port_indev_ios_deinit();
    lv_port_disp_ios_deinit();
    lv_deinit();
}
