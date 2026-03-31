// SPDX-License-Identifier: MIT
#include "eapps/canvas.h"
#include <stdlib.h>
#include <string.h>

struct eapps_canvas {
    eapps_draw_tool_t   tool;
    uint32_t            color;
    uint8_t             width;
    eapps_draw_stroke_t strokes[EAPPS_CANVAS_MAX_STROKES];
    int                 stroke_count;
    int                 undo_pos;
    int                 canvas_w;
    int                 canvas_h;
};

eapps_canvas_t *eapps_canvas_create(lv_obj_t *parent, int w, int h) {
    (void)parent;
    eapps_canvas_t *c = (eapps_canvas_t *)calloc(1, sizeof(eapps_canvas_t));
    if (!c) return NULL;
    c->tool = EAPPS_DRAW_PEN;
    c->color = 0x000000;
    c->width = 3;
    c->canvas_w = w;
    c->canvas_h = h;
    return c;
}

void eapps_canvas_destroy(eapps_canvas_t *c) {
    free(c);
}

void eapps_canvas_set_tool(eapps_canvas_t *c, eapps_draw_tool_t tool) {
    if (c) c->tool = tool;
}

void eapps_canvas_set_color(eapps_canvas_t *c, uint32_t color) {
    if (c) c->color = color;
}

void eapps_canvas_set_width(eapps_canvas_t *c, uint8_t width) {
    if (c) c->width = width;
}

void eapps_canvas_undo(eapps_canvas_t *c) {
    if (c && c->undo_pos > 0) c->undo_pos--;
}

void eapps_canvas_redo(eapps_canvas_t *c) {
    if (c && c->undo_pos < c->stroke_count) c->undo_pos++;
}

void eapps_canvas_clear(eapps_canvas_t *c) {
    if (!c) return;
    c->stroke_count = 0;
    c->undo_pos = 0;
}
