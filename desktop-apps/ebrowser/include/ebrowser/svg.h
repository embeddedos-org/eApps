// SPDX-License-Identifier: MIT
#ifndef eBrowser_SVG_H
#define eBrowser_SVG_H

#include <stdint.h>
#include <stdbool.h>
#include "eBrowser/css_parser.h"

#define EB_SVG_MAX_SHAPES   128
#define EB_SVG_MAX_POINTS   256

typedef enum {
    EB_SVG_RECT,
    EB_SVG_CIRCLE,
    EB_SVG_ELLIPSE,
    EB_SVG_LINE,
    EB_SVG_POLYLINE,
    EB_SVG_POLYGON,
    EB_SVG_PATH
} eb_svg_shape_type_t;

typedef struct {
    int x, y;
} eb_svg_point_t;

typedef struct {
    eb_svg_shape_type_t type;
    eb_color_t          fill;
    eb_color_t          stroke;
    int                 stroke_width;
    bool                has_fill;
    bool                has_stroke;

    union {
        struct { int x, y, width, height, rx, ry; } rect;
        struct { int cx, cy, r; } circle;
        struct { int cx, cy, rx, ry; } ellipse;
        struct { int x1, y1, x2, y2; } line;
        struct { eb_svg_point_t points[EB_SVG_MAX_POINTS]; int count; } poly;
        struct { eb_svg_point_t points[EB_SVG_MAX_POINTS]; int count; } path;
    } data;
} eb_svg_shape_t;

typedef struct {
    int              viewbox_x, viewbox_y;
    int              viewbox_width, viewbox_height;
    int              width, height;
    eb_svg_shape_t   shapes[EB_SVG_MAX_SHAPES];
    int              shape_count;
} eb_svg_element_t;

bool eb_svg_parse(eb_svg_element_t *svg, const char *content, size_t len);

#endif
// SPDX-License-Identifier: MIT
#ifndef eBrowser_SVG_H
#define eBrowser_SVG_H

#include <stdint.h>
#include <stdbool.h>
#include "eBrowser/css_parser.h"

#define EB_SVG_MAX_SHAPES   128
#define EB_SVG_MAX_POINTS   256

typedef enum {
    EB_SVG_RECT,
    EB_SVG_CIRCLE,
    EB_SVG_ELLIPSE,
    EB_SVG_LINE,
    EB_SVG_POLYLINE,
    EB_SVG_POLYGON,
    EB_SVG_PATH
} eb_svg_shape_type_t;

typedef struct {
    int x, y;
} eb_svg_point_t;

typedef struct {
    eb_svg_shape_type_t type;
    eb_color_t          fill;
    eb_color_t          stroke;
    int                 stroke_width;
    bool                has_fill;
    bool                has_stroke;

    union {
        struct { int x, y, width, height, rx, ry; } rect;
        struct { int cx, cy, r; } circle;
        struct { int cx, cy, rx, ry; } ellipse;
        struct { int x1, y1, x2, y2; } line;
        struct { eb_svg_point_t points[EB_SVG_MAX_POINTS]; int count; } poly;
        struct { eb_svg_point_t points[EB_SVG_MAX_POINTS]; int count; } path;
    } data;
} eb_svg_shape_t;

typedef struct {
    int              viewbox_x, viewbox_y;
    int              viewbox_width, viewbox_height;
    int              width, height;
    eb_svg_shape_t   shapes[EB_SVG_MAX_SHAPES];
    int              shape_count;
} eb_svg_element_t;

bool eb_svg_parse(eb_svg_element_t *svg, const char *content, size_t len);

#endif /* eBrowser_SVG_H */
