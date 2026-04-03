// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Meta Platforms, Inc. and affiliates.

#include "lvgl.h"
#include <stdbool.h>
#include <stdint.h>

static lv_indev_t *tv_indev = NULL;
static uint32_t last_key = 0;
static bool key_pressed = false;

/**
 * Map a platform key code to an LVGL key.
 */
static uint32_t map_key_to_lv(uint32_t key)
{
    switch (key) {
        case 0x01: return LV_KEY_UP;
        case 0x02: return LV_KEY_DOWN;
        case 0x03: return LV_KEY_LEFT;
        case 0x04: return LV_KEY_RIGHT;
        case 0x05: return LV_KEY_ENTER;
        case 0x06: return LV_KEY_ESC;
        default:   return 0;
    }
}

static void indev_read_cb(lv_indev_t *indev, lv_indev_data_t *data)
{
    (void)indev;

    uint32_t lv_key = map_key_to_lv(last_key);
    if (lv_key != 0) {
        data->key = lv_key;
    }

    data->state = key_pressed ? LV_INDEV_STATE_PRESSED : LV_INDEV_STATE_RELEASED;
}

/**
 * Process a remote control key event.
 * Called from the platform-specific remote/D-pad handler.
 *
 * Key codes:
 *   0x01 = Up, 0x02 = Down, 0x03 = Left, 0x04 = Right,
 *   0x05 = Enter/OK, 0x06 = Back/ESC
 */
void eapps_tv_process_key(uint32_t key, bool pressed)
{
    last_key = key;
    key_pressed = pressed;
}

void lv_port_indev_tv_init(void)
{
    tv_indev = lv_indev_create();
    lv_indev_set_type(tv_indev, LV_INDEV_TYPE_KEYPAD);
    lv_indev_set_read_cb(tv_indev, indev_read_cb);
}

void lv_port_indev_tv_deinit(void)
{
    if (tv_indev) {
        lv_indev_delete(tv_indev);
        tv_indev = NULL;
    }
    last_key = 0;
    key_pressed = false;
}
