// SPDX-License-Identifier: MIT
#include "eBrowser/layout.h"
#include <string.h>
#include <stdio.h>

void eb_layout_init(eb_layout_context_t *ctx, int vp_width, int vp_height) {
    if (!ctx) return;
    memset(ctx, 0, sizeof(eb_layout_context_t));
    ctx->viewport_width = vp_width;
    ctx->viewport_height = vp_height;
}

static eb_layout_box_t *alloc_box(eb_layout_context_t *ctx) {
    if (ctx->box_count >= EB_LAYOUT_MAX_BOXES) return NULL;
    eb_layout_box_t *box = &ctx->boxes[ctx->box_count++];
    memset(box, 0, sizeof(eb_layout_box_t));
    return box;
}

static eb_layout_box_t *build_tree(eb_layout_context_t *ctx, eb_dom_node_t *node,
                                     const eb_stylesheet_t *ss,
                                     const eb_computed_style_t *parent_style) {
    if (!node) return NULL;
    if (node->type == EB_NODE_COMMENT) return NULL;
    eb_layout_box_t *box = alloc_box(ctx);
    if (!box) return NULL;
    box->node = node;
    if (node->type == EB_NODE_ELEMENT || node->type == EB_NODE_DOCUMENT) {
        const char *id = eb_dom_get_attribute(node, "id");
        const char *cls = eb_dom_get_attribute(node, "class");
        if (parent_style) box->style = eb_css_resolve_style_inherited(ss, node->tag, id, cls, parent_style);
        else box->style = eb_css_resolve_style(ss, node->tag, id, cls);
        const char *inline_style = eb_dom_get_attribute(node, "style");
        if (inline_style) eb_css_apply_inline_style(&box->style, inline_style);
    } else {
        box->style = parent_style ? *parent_style : eb_css_default_style(NULL);
    }
    if (box->style.display == EB_DISPLAY_NONE) return NULL;
    for (int i = 0; i < node->child_count; i++) {
        eb_layout_box_t *child = build_tree(ctx, node->children[i], ss, &box->style);
        if (child && box->child_count < EB_DOM_MAX_CHILDREN) {
            box->children[box->child_count++] = child;
            child->parent = box;
        }
    }
    return box;
}

eb_layout_box_t *eb_layout_build(eb_layout_context_t *ctx, eb_dom_node_t *dom, const eb_stylesheet_t *ss) {
    if (!ctx || !dom) return NULL;
    return build_tree(ctx, dom, ss, NULL);
}

static void compute_box(eb_layout_box_t *box, int container_x, int container_y, int container_width, int *cursor_y);

static void compute_table(eb_layout_box_t *box, int container_width) {
    eb_computed_style_t *s = &box->style;
    int ix = box->x + s->padding.left, iy = box->y + s->padding.top;
    int cw = container_width - s->padding.left - s->padding.right;
    int max_cols = 0;
    for (int r = 0; r < box->child_count; r++) if (box->children[r] && box->children[r]->child_count > max_cols) max_cols = box->children[r]->child_count;
    if (max_cols <= 0) max_cols = 1;
    int col_w = cw / max_cols;
    int cy = iy;
    for (int r = 0; r < box->child_count; r++) {
        eb_layout_box_t *row = box->children[r];
        if (!row) continue;
        row->x = ix; row->y = cy; row->width = cw;
        int rh = 0;
        for (int c = 0; c < row->child_count; c++) {
            eb_layout_box_t *cell = row->children[c];
            if (!cell) continue;
            cell->x = ix + c * col_w + cell->style.padding.left;
            cell->y = cy + cell->style.padding.top;
            cell->width = col_w - cell->style.padding.left - cell->style.padding.right;
            cell->height = cell->style.font_size + 4 + cell->style.padding.top + cell->style.padding.bottom;
            int sc = cell->y;
            for (int j = 0; j < cell->child_count; j++) {
                if (!cell->children[j]) continue;
                cell->children[j]->x = cell->x; cell->children[j]->y = sc;
                cell->children[j]->width = cell->width; cell->children[j]->height = cell->children[j]->style.font_size + 4;
                sc += cell->children[j]->height;
            }
            int ch = sc - cell->y;
            if (ch > cell->height) cell->height = ch;
            cell->height += cell->style.padding.top + cell->style.padding.bottom;
            if (cell->height > rh) rh = cell->height;
        }
        row->height = rh; cy += rh;
    }
    if (s->height_auto) box->height = (cy - iy) + s->padding.top + s->padding.bottom;
}

static void compute_flex(eb_layout_box_t *box, int container_width) {
    eb_computed_style_t *s = &box->style;
    int ix = box->x + s->padding.left, iy = box->y + s->padding.top;
    int cw = container_width - s->padding.left - s->padding.right;
    bool is_col = (s->flex_direction == EB_FLEX_DIRECTION_COLUMN || s->flex_direction == EB_FLEX_DIRECTION_COLUMN_REVERSE);
    int total_fixed = 0, total_grow = 0;
    for (int i = 0; i < box->child_count; i++) {
        eb_layout_box_t *ch = box->children[i]; if (!ch) continue;
        if (!is_col) { int w = ch->style.width_auto ? (ch->style.font_size * 8) : ch->style.width; total_fixed += w + ch->style.margin.left + ch->style.margin.right; if (i > 0) total_fixed += s->gap; }
        total_grow += ch->style.flex_grow > 0 ? ch->style.flex_grow : 0;
    }
    int rem = is_col ? 0 : (cw - total_fixed); if (rem < 0) rem = 0;
    int cx = ix, cy = iy;
    if (!is_col && s->justify_content == EB_JUSTIFY_CENTER) cx = ix + rem / 2;
    else if (!is_col && s->justify_content == EB_JUSTIFY_FLEX_END) cx = ix + rem;
    int max_cross = 0;
    for (int i = 0; i < box->child_count; i++) {
        eb_layout_box_t *ch = box->children[i]; if (!ch) continue;
        int w = ch->style.width_auto ? (ch->style.font_size * 8) : ch->style.width;
        if (ch->style.flex_grow > 0 && total_grow > 0 && !is_col) w += (rem * ch->style.flex_grow) / total_grow;
        int h = ch->style.height_auto ? (ch->style.font_size + 4) : ch->style.height;
        if (is_col) {
            ch->x = cx + ch->style.margin.left; ch->y = cy + ch->style.margin.top;
            ch->width = cw - ch->style.margin.left - ch->style.margin.right; ch->height = h;
            int sc = ch->y; for (int j = 0; j < ch->child_count; j++) compute_box(ch->children[j], ch->x, ch->y, ch->width, &sc);
            if (sc > ch->y + ch->height) ch->height = sc - ch->y;
            cy = ch->y + ch->height + ch->style.margin.bottom + s->gap;
        } else {
            ch->x = cx + ch->style.margin.left; ch->y = cy + ch->style.margin.top;
            ch->width = w; ch->height = h;
            int sc = ch->y; for (int j = 0; j < ch->child_count; j++) compute_box(ch->children[j], ch->x, ch->y, ch->width, &sc);
            if (sc > ch->y + ch->height) ch->height = sc - ch->y;
            cx = ch->x + ch->width + ch->style.margin.right + s->gap;
            int cross = ch->height + ch->style.margin.top + ch->style.margin.bottom;
            if (cross > max_cross) max_cross = cross;
        }
    }
    if (s->height_auto) { int h = is_col ? (cy - iy) : max_cross; box->height = h + s->padding.top + s->padding.bottom; }
}

static void compute_box(eb_layout_box_t *box, int container_x, int container_y, int container_width, int *cursor_y) {
    if (!box) return;
    eb_computed_style_t *s = &box->style;
    int cw = container_width - s->margin.left - s->margin.right - s->padding.left - s->padding.right;
    if (!s->width_auto) cw = s->width;
    box->x = container_x + s->margin.left;
    box->y = *cursor_y + s->margin.top;
    box->width = cw + s->padding.left + s->padding.right;
    if (s->display == EB_DISPLAY_TABLE) {
        box->height = s->height_auto ? 0 : s->height + s->padding.top + s->padding.bottom;
        compute_table(box, box->width);
        *cursor_y = box->y + box->height + s->margin.bottom; return;
    }
    if (s->display == EB_DISPLAY_FLEX) {
        box->height = s->height_auto ? s->padding.top + s->padding.bottom : s->height + s->padding.top + s->padding.bottom;
        compute_flex(box, box->width);
        *cursor_y = box->y + box->height + s->margin.bottom; return;
    }
    int ix = box->x + s->padding.left, iy = box->y + s->padding.top;
    int child_cursor = iy, line_x = ix, line_height = 0;
    for (int i = 0; i < box->child_count; i++) {
        eb_layout_box_t *child = box->children[i]; if (!child) continue;
        if (child->style.display == EB_DISPLAY_BLOCK || child->style.display == EB_DISPLAY_LIST_ITEM ||
            child->style.display == EB_DISPLAY_TABLE || child->style.display == EB_DISPLAY_FLEX) {
            if (line_x != ix) { child_cursor += line_height; line_x = ix; line_height = 0; }
            compute_box(child, ix, iy, cw, &child_cursor);
            child_cursor = child->y + child->height + child->style.margin.bottom;
        } else {
            int ew = child->style.font_size * 8;
            if (child->node && child->node->type == EB_NODE_TEXT) ew = (int)strlen(child->node->text) * (child->style.font_size / 2);
            if (line_x + ew > ix + cw && line_x != ix) { child_cursor += line_height; line_x = ix; line_height = 0; }
            child->x = line_x; child->y = child_cursor; child->width = ew; child->height = child->style.font_size + 4;
            int sc = child->y;
            for (int j = 0; j < child->child_count; j++) compute_box(child->children[j], child->x, child->y, ew, &sc);
            if (sc > child->y + child->height) child->height = sc - child->y;
            line_x += child->width;
            if (child->height > line_height) line_height = child->height;
        }
    }
    if (line_x != ix) child_cursor += line_height;
    int ch = child_cursor - (box->y + s->padding.top); if (ch < 0) ch = 0;
    box->height = s->height_auto ? ch + s->padding.top + s->padding.bottom : s->height + s->padding.top + s->padding.bottom;
    *cursor_y = box->y + box->height + s->margin.bottom;
}

void eb_layout_compute(eb_layout_context_t *ctx, eb_layout_box_t *root) {
    if (!ctx || !root) return;
    int cursor_y = 0;
    compute_box(root, 0, 0, ctx->viewport_width, &cursor_y);
}

void eb_layout_print(const eb_layout_box_t *box, int depth) {
    if (!box) return;
    for (int i = 0; i < depth; i++) printf("  ");
    printf("[%s] x=%d y=%d w=%d h=%d\n", box->node ? box->node->tag : "?", box->x, box->y, box->width, box->height);
    for (int i = 0; i < box->child_count; i++) eb_layout_print(box->children[i], depth + 1);
}
