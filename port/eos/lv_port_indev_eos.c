// SPDX-License-Identifier: MIT
// Copyright (c) 2026 EoS Project

/**
 * @file lv_port_indev_eos.c
 * @brief LVGL input device port for EoS — bridges eos_touch_* HAL to LVGL
 */

#include "lvgl.h"
#include <eos/hal_extended.h>

static lv_indev_t *s_indev = NULL;

static void indev_read_cb(lv_indev_t *indev, lv_indev_data_t *data)
{
    (void)indev;

    eos_touch_point_t points[1];
    uint8_t count = 0;

    eos_touch_read(0, points, 1, &count);

    if (count > 0 && points[0].pressed) {
        data->point.x = points[0].x;
        data->point.y = points[0].y;
        data->state   = LV_INDEV_STATE_PRESSED;
    } else {
        data->state = LV_INDEV_STATE_RELEASED;
    }
}

void lv_port_indev_eos_init(void)
{
    eos_touch_config_t cfg = {
        .id         = 0,
        .type       = EOS_TOUCH_CAPACITIVE,
        .width      = 800,
        .height     = 480,
        .max_points = 1,
    };

    if (eos_touch_init(&cfg) != 0) return;

    s_indev = lv_indev_create();
    if (!s_indev) return;

    lv_indev_set_type(s_indev, LV_INDEV_TYPE_POINTER);
    lv_indev_set_read_cb(s_indev, indev_read_cb);
}

void lv_port_indev_eos_deinit(void)
{
    if (s_indev) {
        lv_indev_delete(s_indev);
        s_indev = NULL;
    }
    eos_touch_deinit(0);
}
