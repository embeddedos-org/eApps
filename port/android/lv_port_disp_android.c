/*
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2024 Meta Platforms, Inc. and affiliates.
 *
 * Android display driver for LVGL.
 */

#include "lvgl.h"
#include <android/native_window.h>
#include <stdlib.h>

#define ANDROID_DISP_HOR_RES 800
#define ANDROID_DISP_VER_RES 480
#define ANDROID_BUF_LINES    10

static lv_display_t *s_display = NULL;
static lv_color_t   *s_buf1   = NULL;
static lv_color_t   *s_buf2   = NULL;
static ANativeWindow *s_window = NULL;

static void disp_flush_cb(lv_display_t *disp, const lv_area_t *area, uint8_t *px_map)
{
    if(s_window == NULL) {
        lv_display_flush_ready(disp);
        return;
    }

    ANativeWindow_Buffer buffer;
    if(ANativeWindow_lock(s_window, &buffer, NULL) < 0) {
        lv_display_flush_ready(disp);
        return;
    }

    lv_color_t *src = (lv_color_t *)px_map;
    int32_t w = lv_area_get_width(area);
    int32_t h = lv_area_get_height(area);

    for(int32_t y = 0; y < h; y++) {
        lv_color_t *dst = (lv_color_t *)((uint8_t *)buffer.bits +
                          (area->y1 + y) * buffer.stride * sizeof(lv_color_t));
        dst += area->x1;
        memcpy(dst, src, w * sizeof(lv_color_t));
        src += w;
    }

    ANativeWindow_unlockAndPost(s_window);
    lv_display_flush_ready(disp);
}

void lv_port_disp_android_init(void)
{
    uint32_t buf_size = ANDROID_DISP_HOR_RES * ANDROID_BUF_LINES;

    s_buf1 = (lv_color_t *)malloc(buf_size * sizeof(lv_color_t));
    s_buf2 = (lv_color_t *)malloc(buf_size * sizeof(lv_color_t));

    s_display = lv_display_create(ANDROID_DISP_HOR_RES, ANDROID_DISP_VER_RES);
    lv_display_set_buffers(s_display, s_buf1, s_buf2,
                           buf_size * sizeof(lv_color_t),
                           LV_DISPLAY_RENDER_MODE_PARTIAL);
    lv_display_set_flush_cb(s_display, disp_flush_cb);
}

void lv_port_disp_android_deinit(void)
{
    if(s_display) {
        lv_display_delete(s_display);
        s_display = NULL;
    }

    if(s_buf1) {
        free(s_buf1);
        s_buf1 = NULL;
    }

    if(s_buf2) {
        free(s_buf2);
        s_buf2 = NULL;
    }

    s_window = NULL;
}

void lv_port_disp_android_set_window(ANativeWindow *window)
{
    s_window = window;
    if(s_window) {
        ANativeWindow_setBuffersGeometry(s_window,
                                         ANDROID_DISP_HOR_RES,
                                         ANDROID_DISP_VER_RES,
                                         WINDOW_FORMAT_RGBX_8888);
    }
}
