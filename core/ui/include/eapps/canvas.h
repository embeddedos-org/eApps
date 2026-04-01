// SPDX-License-Identifier: MIT
#ifndef EAPPS_CANVAS_H
#define EAPPS_CANVAS_H

#include "eapps/types.h"
#include <stdint.h>

#define EAPPS_CANVAS_MAX_STROKES 256
#define EAPPS_CANVAS_MAX_POINTS  512

typedef enum {
    EAPPS_DRAW_PEN,
    EAPPS_DRAW_LINE,
    EAPPS_DRAW_RECT,
    EAPPS_DRAW_CIRCLE,
    EAPPS_DRAW_ERASER,
    EAPPS_DRAW_TOOL_COUNT
} eapps_draw_tool_t;

typedef struct {
    int16_t x, y;
} eapps_point_t;

typedef struct {
    eapps_draw_tool_t tool;
    uint32_t          color;
    uint8_t           width;
    eapps_point_t     points[EAPPS_CANVAS_MAX_POINTS];
    int               point_count;
} eapps_draw_stroke_t;

typedef struct eapps_canvas eapps_canvas_t;

eapps_canvas_t *eapps_canvas_create(lv_obj_t *parent, int w, int h);
void            eapps_canvas_destroy(eapps_canvas_t *c);
void            eapps_canvas_set_tool(eapps_canvas_t *c, eapps_draw_tool_t tool);
void            eapps_canvas_set_color(eapps_canvas_t *c, uint32_t color);
void            eapps_canvas_set_width(eapps_canvas_t *c, uint8_t width);
void            eapps_canvas_undo(eapps_canvas_t *c);
void            eapps_canvas_redo(eapps_canvas_t *c);
void            eapps_canvas_clear(eapps_canvas_t *c);

#endif /* EAPPS_CANVAS_H */
