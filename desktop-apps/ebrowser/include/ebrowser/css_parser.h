// SPDX-License-Identifier: MIT
#ifndef eBrowser_CSS_PARSER_H
#define eBrowser_CSS_PARSER_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#define EB_CSS_MAX_SELECTOR   128
#define EB_CSS_MAX_PROPERTIES 32
#define EB_CSS_MAX_VALUE      128
#define EB_CSS_MAX_RULES      64
#define EB_CSS_MAX_TAG_LEN    32

typedef enum {
    EB_DISPLAY_BLOCK,
    EB_DISPLAY_INLINE,
    EB_DISPLAY_INLINE_BLOCK,
    EB_DISPLAY_NONE,
    EB_DISPLAY_FLEX,
    EB_DISPLAY_TABLE,
    EB_DISPLAY_TABLE_ROW,
    EB_DISPLAY_TABLE_CELL,
    EB_DISPLAY_LIST_ITEM
} eb_display_t;

typedef enum {
    EB_POSITION_STATIC,
    EB_POSITION_RELATIVE,
    EB_POSITION_ABSOLUTE,
    EB_POSITION_FIXED
} eb_position_t;

typedef enum {
    EB_FLOAT_NONE,
    EB_FLOAT_LEFT,
    EB_FLOAT_RIGHT
} eb_float_t;

typedef enum {
    EB_OVERFLOW_VISIBLE,
    EB_OVERFLOW_HIDDEN,
    EB_OVERFLOW_SCROLL,
    EB_OVERFLOW_AUTO
} eb_overflow_t;

typedef enum {
    EB_FONT_WEIGHT_NORMAL,
    EB_FONT_WEIGHT_BOLD
} eb_font_weight_t;

typedef enum {
    EB_FONT_STYLE_NORMAL,
    EB_FONT_STYLE_ITALIC
} eb_font_style_t;

typedef enum {
    EB_TEXT_ALIGN_LEFT,
    EB_TEXT_ALIGN_CENTER,
    EB_TEXT_ALIGN_RIGHT,
    EB_TEXT_ALIGN_JUSTIFY
} eb_text_align_t;

typedef enum {
    EB_TEXT_DECORATION_NONE,
    EB_TEXT_DECORATION_UNDERLINE,
    EB_TEXT_DECORATION_LINE_THROUGH,
    EB_TEXT_DECORATION_OVERLINE
} eb_text_decoration_t;

typedef enum {
    EB_TEXT_TRANSFORM_NONE,
    EB_TEXT_TRANSFORM_UPPERCASE,
    EB_TEXT_TRANSFORM_LOWERCASE,
    EB_TEXT_TRANSFORM_CAPITALIZE
} eb_text_transform_t;

typedef enum {
    EB_LIST_STYLE_NONE,
    EB_LIST_STYLE_DISC,
    EB_LIST_STYLE_CIRCLE,
    EB_LIST_STYLE_SQUARE,
    EB_LIST_STYLE_DECIMAL
} eb_list_style_t;

typedef enum {
    EB_FLEX_DIRECTION_ROW,
    EB_FLEX_DIRECTION_COLUMN,
    EB_FLEX_DIRECTION_ROW_REVERSE,
    EB_FLEX_DIRECTION_COLUMN_REVERSE
} eb_flex_direction_t;

typedef enum {
    EB_JUSTIFY_FLEX_START,
    EB_JUSTIFY_FLEX_END,
    EB_JUSTIFY_CENTER,
    EB_JUSTIFY_SPACE_BETWEEN,
    EB_JUSTIFY_SPACE_AROUND
} eb_justify_content_t;

typedef enum {
    EB_ALIGN_STRETCH,
    EB_ALIGN_FLEX_START,
    EB_ALIGN_FLEX_END,
    EB_ALIGN_CENTER,
    EB_ALIGN_BASELINE
} eb_align_items_t;

typedef struct {
    uint8_t r, g, b, a;
} eb_color_t;

typedef struct {
    int top, right, bottom, left;
} eb_edges_t;

typedef struct {
    eb_color_t          color;
    eb_color_t          background_color;
    eb_display_t        display;
    eb_position_t       position;
    eb_float_t          css_float;
    eb_overflow_t       overflow;
    int                 font_size;
    eb_font_weight_t    font_weight;
    eb_font_style_t     font_style;
    eb_text_align_t     text_align;
    eb_text_decoration_t text_decoration;
    eb_text_transform_t text_transform;
    eb_list_style_t     list_style;
    eb_edges_t          margin;
    eb_edges_t          padding;
    int                 width;
    int                 height;
    bool                width_auto;
    bool                height_auto;
    int                 border_width;
    eb_color_t          border_color;
    int                 border_radius;
    int                 z_index;
    int                 opacity;
    int                 line_height;
    eb_flex_direction_t flex_direction;
    eb_justify_content_t justify_content;
    eb_align_items_t    align_items;
    int                 flex_grow;
    int                 gap;
} eb_computed_style_t;

typedef struct {
    char name[EB_CSS_MAX_VALUE];
    char value[EB_CSS_MAX_VALUE];
} eb_css_property_t;

typedef struct {
    char              selector[EB_CSS_MAX_SELECTOR];
    eb_css_property_t properties[EB_CSS_MAX_PROPERTIES];
    int               prop_count;
    int               specificity;
} eb_css_rule_t;

typedef struct {
    eb_css_rule_t rules[EB_CSS_MAX_RULES];
    int           rule_count;
} eb_stylesheet_t;

void              eb_css_init_stylesheet(eb_stylesheet_t *ss);
bool              eb_css_parse(eb_stylesheet_t *ss, const char *css, size_t len);
eb_computed_style_t eb_css_default_style(const char *tag);
eb_color_t        eb_css_parse_color(const char *str);
int               eb_css_parse_length(const char *str);
int               eb_css_compute_specificity(const char *selector);
eb_computed_style_t eb_css_resolve_style(const eb_stylesheet_t *ss, const char *tag,
                                          const char *id, const char *class_name);
eb_computed_style_t eb_css_resolve_style_inherited(const eb_stylesheet_t *ss,
                                                    const char *tag, const char *id,
                                                    const char *class_name,
                                                    const eb_computed_style_t *parent_style);
void              eb_css_apply_inline_style(eb_computed_style_t *style, const char *inline_css);

#endif
