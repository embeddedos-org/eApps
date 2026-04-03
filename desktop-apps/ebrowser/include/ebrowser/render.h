// SPDX-License-Identifier: MIT
#ifndef eBrowser_RENDER_H
#define eBrowser_RENDER_H

#include "eBrowser/layout.h"
#include "lvgl.h"

typedef struct {
    lv_obj_t           *canvas;
    lv_color_t         *buf;
    int                 width;
    int                 height;
} eb_render_target_t;

void eb_render_init(eb_render_target_t *rt, lv_obj_t *parent, int w, int h);
void eb_render_clear(eb_render_target_t *rt, eb_color_t bg);
void eb_render_paint(eb_render_target_t *rt, const eb_layout_box_t *root);
void eb_render_deinit(eb_render_target_t *rt);

#endif /* eBrowser_RENDER_H */
