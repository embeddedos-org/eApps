// SPDX-License-Identifier: MIT
#include "epaint.h"
#include "eapps/theme.h"
#include "eapps/widgets.h"
#include "lvgl.h"
#include <stdbool.h>

static lv_obj_t *s_canvas = NULL;
static lv_obj_t *s_color_indicator = NULL;
static lv_color_t s_pen_color;
static int s_pen_size = 4;
static bool s_eraser = false;

static lv_color_t hc(uint32_t hex)
{
    return lv_color_make((hex >> 16) & 0xFF, (hex >> 8) & 0xFF, hex & 0xFF);
}

static void canvas_draw_cb(lv_event_t *e)
{
    lv_obj_t *canvas = lv_event_get_target(e);
    lv_indev_t *indev = lv_indev_active();
    if (!indev) return;

    lv_point_t pt;
    lv_indev_get_point(indev, &pt);

    lv_coord_t x = pt.x - lv_obj_get_x(canvas);
    lv_coord_t y = pt.y - lv_obj_get_y(canvas);

    lv_layer_t *layer = lv_canvas_get_layer(canvas);
    if (!layer) return;

    lv_draw_rect_dsc_t rect_dsc;
    lv_draw_rect_dsc_init(&rect_dsc);
    rect_dsc.bg_color = s_eraser ? hc(0x1E1E1E) : s_pen_color;
    rect_dsc.bg_opa = LV_OPA_COVER;
    rect_dsc.radius = s_pen_size;

    lv_area_t area = {
        .x1 = x - s_pen_size / 2,
        .y1 = y - s_pen_size / 2,
        .x2 = x + s_pen_size / 2,
        .y2 = y + s_pen_size / 2,
    };
    lv_draw_rect(layer, &rect_dsc, &area);
    lv_canvas_finish_layer(canvas, layer);
}

static void color_btn_cb(lv_event_t *e)
{
    uint32_t color = (uint32_t)(intptr_t)lv_event_get_user_data(e);
    s_pen_color = hc(color);
    s_eraser = false;
    if (s_color_indicator) {
        lv_obj_set_style_bg_color(s_color_indicator, s_pen_color, 0);
    }
}

static void eraser_cb(lv_event_t *e)
{
    (void)e;
    s_eraser = true;
}

static void clear_cb(lv_event_t *e)
{
    (void)e;
    if (s_canvas) {
        lv_canvas_fill_bg(s_canvas, hc(0x1E1E1E), LV_OPA_COVER);
    }
}

static void size_cb(lv_event_t *e)
{
    int sz = (int)(intptr_t)lv_event_get_user_data(e);
    s_pen_size = sz;
}

static bool epaint_init(lv_obj_t *parent)
{
    const eapps_palette_t *p = eapps_theme_get_palette();
    s_pen_color = hc(p->primary);
    s_eraser = false;
    s_pen_size = 4;

    lv_obj_t *scaf = eapps_scaffold_create(parent, "ePaint", false);
    lv_obj_t *body = lv_obj_get_child(scaf, 1);
    lv_obj_set_flex_flow(body, LV_FLEX_FLOW_COLUMN);
    lv_obj_set_style_pad_all(body, 4, 0);

    /* Toolbar */
    lv_obj_t *toolbar = lv_obj_create(body);
    lv_obj_set_size(toolbar, LV_PCT(100), 40);
    lv_obj_set_style_bg_color(toolbar, hc(p->surface), 0);
    lv_obj_set_style_bg_opa(toolbar, LV_OPA_COVER, 0);
    lv_obj_set_style_border_width(toolbar, 0, 0);
    lv_obj_set_style_radius(toolbar, 8, 0);
    lv_obj_set_style_pad_all(toolbar, 4, 0);
    lv_obj_set_style_pad_gap(toolbar, 4, 0);
    lv_obj_set_flex_flow(toolbar, LV_FLEX_FLOW_ROW);
    lv_obj_set_flex_align(toolbar, LV_FLEX_ALIGN_START, LV_FLEX_ALIGN_CENTER,
                          LV_FLEX_ALIGN_CENTER);

    static const uint32_t colors[] = {
        0xFF0000, 0x00FF00, 0x0000FF, 0xFFFF00,
        0xFF00FF, 0x00FFFF, 0xFFFFFF, 0xFF8800
    };
    for (int i = 0; i < 8; i++) {
        lv_obj_t *cb = lv_button_create(toolbar);
        lv_obj_set_size(cb, 28, 28);
        lv_obj_set_style_bg_color(cb, hc(colors[i]), 0);
        lv_obj_set_style_bg_opa(cb, LV_OPA_COVER, 0);
        lv_obj_set_style_radius(cb, 14, 0);
        lv_obj_set_style_shadow_width(cb, 0, 0);
        lv_obj_add_event_cb(cb, color_btn_cb, LV_EVENT_CLICKED,
                            (void *)(intptr_t)colors[i]);
    }

    s_color_indicator = lv_obj_create(toolbar);
    lv_obj_set_size(s_color_indicator, 28, 28);
    lv_obj_set_style_bg_color(s_color_indicator, s_pen_color, 0);
    lv_obj_set_style_bg_opa(s_color_indicator, LV_OPA_COVER, 0);
    lv_obj_set_style_radius(s_color_indicator, 4, 0);
    lv_obj_set_style_border_color(s_color_indicator, hc(p->on_surface), 0);
    lv_obj_set_style_border_width(s_color_indicator, 2, 0);

    lv_obj_t *eraser_btn = eapps_button_create(toolbar, "Eraser");
    lv_obj_set_height(eraser_btn, 28);
    lv_obj_add_event_cb(eraser_btn, eraser_cb, LV_EVENT_CLICKED, NULL);

    lv_obj_t *clear_btn = eapps_button_create(toolbar, "Clear");
    lv_obj_set_height(clear_btn, 28);
    lv_obj_add_event_cb(clear_btn, clear_cb, LV_EVENT_CLICKED, NULL);

    static const int sizes[] = {2, 4, 8, 16};
    static const char *size_names[] = {"S", "M", "L", "XL"};
    for (int i = 0; i < 4; i++) {
        lv_obj_t *sb = lv_button_create(toolbar);
        lv_obj_set_size(sb, 28, 28);
        lv_obj_set_style_radius(sb, 4, 0);
        lv_obj_t *sl = lv_label_create(sb);
        lv_label_set_text(sl, size_names[i]);
        lv_obj_center(sl);
        lv_obj_add_event_cb(sb, size_cb, LV_EVENT_CLICKED,
                            (void *)(intptr_t)sizes[i]);
    }

    /* Canvas */
    static lv_color_t canvas_buf[480 * 320];
    s_canvas = lv_canvas_create(body);
    lv_canvas_set_buffer(s_canvas, canvas_buf, 480, 320, LV_COLOR_FORMAT_NATIVE);
    lv_canvas_fill_bg(s_canvas, hc(0x1E1E1E), LV_OPA_COVER);
    lv_obj_set_style_border_color(s_canvas, hc(p->border), 0);
    lv_obj_set_style_border_width(s_canvas, 1, 0);
    lv_obj_add_event_cb(s_canvas, canvas_draw_cb, LV_EVENT_PRESSING, NULL);

    return true;
}

static void epaint_deinit(void)
{
    s_canvas = NULL;
    s_color_indicator = NULL;
}

static void epaint_on_show(void) {}
static void epaint_on_hide(void) {}

const eapps_app_info_t epaint_info = {
    .id = "epaint", .name = "ePaint", .icon = LV_SYMBOL_EDIT,
    .description = "Drawing canvas with tools",
    .category = EAPPS_CAT_MEDIA, .version = "2.0.0",
};
const eapps_app_lifecycle_t epaint_lifecycle = {
    .init = epaint_init, .deinit = epaint_deinit,
    .on_show = epaint_on_show, .on_hide = epaint_on_hide,
};
