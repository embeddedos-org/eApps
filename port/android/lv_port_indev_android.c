/*
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2024 Meta Platforms, Inc. and affiliates.
 *
 * Android touch input driver for LVGL.
 */

#include "lvgl.h"
#include <android/input.h>

static lv_indev_t *s_indev   = NULL;
static int32_t     s_last_x  = 0;
static int32_t     s_last_y  = 0;
static bool        s_pressed = false;

static void indev_read_cb(lv_indev_t *indev, lv_indev_data_t *data)
{
    (void)indev;

    data->point.x = s_last_x;
    data->point.y = s_last_y;
    data->state = s_pressed ? LV_INDEV_STATE_PRESSED : LV_INDEV_STATE_RELEASED;
}

void lv_port_indev_android_process_event(AInputEvent *event)
{
    if(AInputEvent_getType(event) != AINPUT_EVENT_TYPE_MOTION) {
        return;
    }

    int32_t action = AMotionEvent_getAction(event) & AMOTION_EVENT_ACTION_MASK;

    s_last_x = (int32_t)AMotionEvent_getX(event, 0);
    s_last_y = (int32_t)AMotionEvent_getY(event, 0);

    switch(action) {
        case AMOTION_EVENT_ACTION_DOWN:
        case AMOTION_EVENT_ACTION_MOVE:
            s_pressed = true;
            break;
        case AMOTION_EVENT_ACTION_UP:
        case AMOTION_EVENT_ACTION_CANCEL:
            s_pressed = false;
            break;
        default:
            break;
    }
}

void lv_port_indev_android_init(void)
{
    s_indev = lv_indev_create();
    lv_indev_set_type(s_indev, LV_INDEV_TYPE_POINTER);
    lv_indev_set_read_cb(s_indev, indev_read_cb);
}

void lv_port_indev_android_deinit(void)
{
    if(s_indev) {
        lv_indev_delete(s_indev);
        s_indev = NULL;
    }

    s_last_x  = 0;
    s_last_y  = 0;
    s_pressed = false;
}
