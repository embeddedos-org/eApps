// SPDX-License-Identifier: MIT
#include "eBrowser/render.h"
#include <stdlib.h>
#include <string.h>

void eb_render_init(eb_render_target_t *rt, lv_obj_t *parent, int w, int h) {
    if (!rt) return;
    rt->width = w;
    rt->height = h;
    rt->buf = (lv_color_t *)calloc((size_t)w * h, sizeof(lv_color_t));
    rt->canvas = lv_canvas_create(parent);
    lv_canvas_set_buffer(rt->canvas, rt->buf, w, h, LV_COLOR_FORMAT_NATIVE);
    lv_obj_set_size(rt->canvas, w, h);
}

void eb_render_clear(eb_render_target_t *rt, eb_color_t bg) {
    if (!rt || !rt->canvas) return;
    lv_color_t c = lv_color_make(bg.r, bg.g, bg.b);
    lv_canvas_fill_bg(rt->canvas, c, LV_OPA_COVER);
}

static void paint_box(eb_render_target_t *rt, const eb_layout_box_t *box) {
    if (!rt || !box) return;

    if (box->style.background_color.a > 0) {
        lv_layer_t layer;
        lv_canvas_init_layer(rt->canvas, &layer);
        lv_draw_rect_dsc_t rect_dsc;
        lv_draw_rect_dsc_init(&rect_dsc);
        rect_dsc.bg_color = lv_color_make(box->style.background_color.r,
                                           box->style.background_color.g,
                                           box->style.background_color.b);
        rect_dsc.bg_opa = box->style.background_color.a;
        rect_dsc.radius = 0;
        lv_area_t area = {box->x, box->y, box->x + box->width, box->y + box->height};
        lv_draw_rect(&layer, &rect_dsc, &area);
        lv_canvas_finish_layer(rt->canvas, &layer);
    }

    if (box->node && box->node->type == EB_NODE_TEXT && box->node->text[0]) {
        lv_layer_t layer;
        lv_canvas_init_layer(rt->canvas, &layer);
        lv_draw_label_dsc_t label_dsc;
        lv_draw_label_dsc_init(&label_dsc);
        label_dsc.color = lv_color_make(box->style.color.r, box->style.color.g, box->style.color.b);
        label_dsc.text = box->node->text;
        lv_area_t area = {box->x, box->y, box->x + box->width, box->y + box->height};
        lv_draw_label(&layer, &label_dsc, &area);
        lv_canvas_finish_layer(rt->canvas, &layer);
    }

    if (box->style.border_width > 0 && box->style.border_color.a > 0) {
        lv_layer_t layer;
        lv_canvas_init_layer(rt->canvas, &layer);
        lv_draw_rect_dsc_t border_dsc;
        lv_draw_rect_dsc_init(&border_dsc);
        border_dsc.bg_color = lv_color_make(box->style.border_color.r,
                                             box->style.border_color.g,
                                             box->style.border_color.b);
        border_dsc.bg_opa = LV_OPA_COVER;
        int bw = box->style.border_width;
        lv_area_t top = {box->x, box->y, box->x + box->width, box->y + bw};
        lv_draw_rect(&layer, &border_dsc, &top);
        lv_area_t bottom = {box->x, box->y + box->height - bw, box->x + box->width, box->y + box->height};
        lv_draw_rect(&layer, &border_dsc, &bottom);
        lv_area_t left_side = {box->x, box->y, box->x + bw, box->y + box->height};
        lv_draw_rect(&layer, &border_dsc, &left_side);
        lv_area_t right_side = {box->x + box->width - bw, box->y, box->x + box->width, box->y + box->height};
        lv_draw_rect(&layer, &border_dsc, &right_side);
        lv_canvas_finish_layer(rt->canvas, &layer);
    }

    for (int i = 0; i < box->child_count; i++) {
        paint_box(rt, box->children[i]);
    }
}

void eb_render_paint(eb_render_target_t *rt, const eb_layout_box_t *root) {
    paint_box(rt, root);
}

void eb_render_deinit(eb_render_target_t *rt) {
    if (!rt) return;
    if (rt->canvas) lv_obj_delete(rt->canvas);
    free(rt->buf);
    rt->canvas = NULL;
    rt->buf = NULL;
}
