// SPDX-License-Identifier: MIT
#ifndef eBrowser_LAYOUT_H
#define eBrowser_LAYOUT_H

#include "eBrowser/dom.h"
#include "eBrowser/css_parser.h"

#define EB_LAYOUT_MAX_BOXES 512

typedef struct eb_layout_box eb_layout_box_t;

struct eb_layout_box {
    int                  x, y, width, height;
    eb_computed_style_t  style;
    eb_dom_node_t       *node;
    eb_layout_box_t     *parent;
    eb_layout_box_t     *children[EB_DOM_MAX_CHILDREN];
    int                  child_count;
};

typedef struct {
    eb_layout_box_t boxes[EB_LAYOUT_MAX_BOXES];
    int             box_count;
    int             viewport_width;
    int             viewport_height;
} eb_layout_context_t;

void             eb_layout_init(eb_layout_context_t *ctx, int vp_width, int vp_height);
eb_layout_box_t *eb_layout_build(eb_layout_context_t *ctx, eb_dom_node_t *dom,
                                  const eb_stylesheet_t *ss);
void             eb_layout_compute(eb_layout_context_t *ctx, eb_layout_box_t *root);
void             eb_layout_print(const eb_layout_box_t *box, int depth);

#endif /* eBrowser_LAYOUT_H */
