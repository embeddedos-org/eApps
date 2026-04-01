// SPDX-License-Identifier: MIT
// Copyright (c) 2026 EoS Project

/**
 * @file lv_port_disp_sdl2.c
 * @brief LVGL display port for SDL2 simulator
 */

#include "lvgl.h"
#include <eos/hal_extended.h>
#include <stdlib.h>

#define SDL2_DISP_HOR_RES 800
#define SDL2_DISP_VER_RES 480
#define SDL2_BUF_LINES    10

static lv_display_t *s_display = NULL;
static uint8_t *s_buf1 = NULL;
static uint8_t *s_buf2 = NULL;

static void disp_flush_cb(lv_display_t *disp, const lv_area_t *area,
                           uint8_t *px_map)
{
    uint16_t x = (uint16_t)area->x1;
    uint16_t y = (uint16_t)area->y1;
    uint16_t w = (uint16_t)(area->x2 - area->x1 + 1);
    uint16_t h = (uint16_t)(area->y2 - area->y1 + 1);

    eos_display_draw_bitmap(0, x, y, w, h, px_map);

    if (lv_display_flush_is_last(disp)) {
        eos_display_flush(0);
    }

    lv_display_flush_ready(disp);
}

void lv_port_disp_sdl2_init(void)
{
    eos_display_config_t cfg = {
        .id         = 0,
        .width      = SDL2_DISP_HOR_RES,
        .height     = SDL2_DISP_VER_RES,
        .color_mode = EOS_DISPLAY_COLOR_RGB565,
    };

    if (eos_display_init(&cfg) != 0) return;

    uint32_t buf_size = (uint32_t)SDL2_DISP_HOR_RES * SDL2_BUF_LINES *
                        sizeof(lv_color_t);

    s_buf1 = (uint8_t *)malloc(buf_size);
    s_buf2 = (uint8_t *)malloc(buf_size);
    if (!s_buf1 || !s_buf2) return;

    s_display = lv_display_create(SDL2_DISP_HOR_RES, SDL2_DISP_VER_RES);
    if (!s_display) return;

    lv_display_set_flush_cb(s_display, disp_flush_cb);
    lv_display_set_buffers(s_display, s_buf1, s_buf2, buf_size,
                           LV_DISPLAY_RENDER_MODE_PARTIAL);
}

void lv_port_disp_sdl2_deinit(void)
{
    if (s_display) {
        lv_display_delete(s_display);
        s_display = NULL;
    }
    free(s_buf1); s_buf1 = NULL;
    free(s_buf2); s_buf2 = NULL;
    eos_display_deinit(0);
}
