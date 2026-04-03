// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Meta Platforms, Inc. and affiliates.

#include "lvgl.h"
#include <stdlib.h>

#define IOS_DISP_HOR_RES 390
#define IOS_DISP_VER_RES 844
#define IOS_BUF_LINES    10

static lv_display_t *ios_display = NULL;
static uint8_t *buf1 = NULL;
static uint8_t *buf2 = NULL;

extern void eapps_ios_flush_pixels(int x, int y, int w, int h, const void *px_map);

static void disp_flush_cb(lv_display_t *disp, const lv_area_t *area, uint8_t *px_map)
{
    int x = area->x1;
    int y = area->y1;
    int w = lv_area_get_width(area);
    int h = lv_area_get_height(area);

    eapps_ios_flush_pixels(x, y, w, h, px_map);

    lv_display_flush_ready(disp);
}

void lv_port_disp_ios_init(void)
{
    uint32_t buf_size = IOS_DISP_HOR_RES * IOS_BUF_LINES * lv_color_format_get_size(LV_COLOR_FORMAT_NATIVE);

    buf1 = (uint8_t *)malloc(buf_size);
    buf2 = (uint8_t *)malloc(buf_size);

    ios_display = lv_display_create(IOS_DISP_HOR_RES, IOS_DISP_VER_RES);
    lv_display_set_flush_cb(ios_display, disp_flush_cb);
    lv_display_set_buffers(ios_display, buf1, buf2, buf_size, LV_DISPLAY_RENDER_MODE_PARTIAL);
}

void lv_port_disp_ios_deinit(void)
{
    if (ios_display) {
        lv_display_delete(ios_display);
        ios_display = NULL;
    }
    free(buf1);
    buf1 = NULL;
    free(buf2);
    buf2 = NULL;
}
