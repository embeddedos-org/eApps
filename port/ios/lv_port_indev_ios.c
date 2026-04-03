// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Meta Platforms, Inc. and affiliates.

#include "lvgl.h"
#include <stdbool.h>

static lv_indev_t *ios_indev = NULL;
static int touch_x = 0;
static int touch_y = 0;
static bool touch_pressed = false;

static void indev_read_cb(lv_indev_t *indev, lv_indev_data_t *data)
{
    (void)indev;

    data->point.x = touch_x;
    data->point.y = touch_y;
    data->state = touch_pressed ? LV_INDEV_STATE_PRESSED : LV_INDEV_STATE_RELEASED;
}

/**
 * Process a touch event from UIKit.
 * Called from the native iOS touch handler.
 */
void eapps_ios_process_touch(int x, int y, bool pressed)
{
    touch_x = x;
    touch_y = y;
    touch_pressed = pressed;
}

void lv_port_indev_ios_init(void)
{
    ios_indev = lv_indev_create();
    lv_indev_set_type(ios_indev, LV_INDEV_TYPE_POINTER);
    lv_indev_set_read_cb(ios_indev, indev_read_cb);
}

void lv_port_indev_ios_deinit(void)
{
    if (ios_indev) {
        lv_indev_delete(ios_indev);
        ios_indev = NULL;
    }
    touch_x = 0;
    touch_y = 0;
    touch_pressed = false;
}
