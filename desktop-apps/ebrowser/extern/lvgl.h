/* Minimal LVGL stub for CI builds without the LVGL submodule */
#ifndef LVGL_H
#define LVGL_H
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
typedef struct { uint16_t full; } lv_color_t;
typedef int32_t lv_coord_t;
static inline lv_color_t lv_color_make(uint8_t r, uint8_t g, uint8_t b) { lv_color_t c; c.full = (uint16_t)(((r>>3)<<11)|((g>>2)<<5)|(b>>3)); return c; }
static inline lv_color_t lv_color_black(void) { lv_color_t c = {0}; return c; }
static inline lv_color_t lv_color_white(void) { lv_color_t c; c.full = 0xFFFF; return c; }
typedef struct lv_obj_t lv_obj_t;
typedef struct lv_event_t lv_event_t;
typedef struct lv_indev_t lv_indev_t;
typedef struct lv_timer_t lv_timer_t;
typedef struct lv_display_t lv_display_t;
typedef struct lv_indev_data_t lv_indev_data_t;
typedef struct lv_layer_t lv_layer_t;
typedef struct { int32_t x1, y1, x2, y2; } lv_area_t;
typedef struct { int32_t x, y; } lv_point_t;
typedef void (*lv_timer_cb_t)(lv_timer_t *);
typedef void (*lv_event_cb_t)(lv_event_t *);
enum { LV_OPA_TRANSP=0, LV_OPA_COVER=255, LV_OPA_50=127 };
enum { LV_FLEX_FLOW_ROW=0, LV_FLEX_FLOW_COLUMN=1, LV_FLEX_FLOW_ROW_WRAP=2 };
enum { LV_FLEX_ALIGN_START=0, LV_FLEX_ALIGN_CENTER=1, LV_FLEX_ALIGN_END=2, LV_FLEX_ALIGN_SPACE_BETWEEN=3, LV_FLEX_ALIGN_SPACE_EVENLY=4 };
enum { LV_TEXT_ALIGN_CENTER=1, LV_TEXT_ALIGN_LEFT=2 };
enum { LV_LABEL_LONG_WRAP=0, LV_LABEL_LONG_DOT=1, LV_LABEL_LONG_SCROLL=2 };
enum { LV_EVENT_CLICKED=0, LV_EVENT_VALUE_CHANGED=1, LV_EVENT_PRESSING=2, LV_EVENT_READY=3 };
enum { LV_OBJ_FLAG_HIDDEN=1, LV_OBJ_FLAG_SCROLLABLE=2, LV_OBJ_FLAG_CLICKABLE=4 };
enum { LV_BORDER_SIDE_TOP=1, LV_BORDER_SIDE_BOTTOM=2 };
enum { LV_ALIGN_TOP_MID=0, LV_ALIGN_CENTER=1, LV_ALIGN_LEFT_MID=2, LV_ALIGN_RIGHT_MID=3, LV_ALIGN_BOTTOM_MID=4, LV_ALIGN_TOP_LEFT=5 };
enum { LV_PART_MAIN=0, LV_PART_INDICATOR=1, LV_PART_KNOB=2 };
enum { LV_INDEV_TYPE_POINTER=0, LV_INDEV_TYPE_KEYPAD=1 };
enum { LV_INDEV_STATE_PRESSED=0, LV_INDEV_STATE_RELEASED=1 };
enum { LV_ANIM_OFF=0, LV_ANIM_ON=1 };
enum { LV_STATE_CHECKED=1 };
enum { LV_DISPLAY_RENDER_MODE_PARTIAL=0 };
enum { LV_COLOR_FORMAT_NATIVE=0 };
#define LV_SIZE_CONTENT 0
#define LV_PCT(x) (-(x))
typedef struct { int dummy; } lv_font_t;
static const lv_font_t lv_font_montserrat_12 = {0};
static const lv_font_t lv_font_montserrat_14 = {0};
static const lv_font_t lv_font_montserrat_16 = {0};
static const lv_font_t lv_font_montserrat_20 = {0};
static const lv_font_t lv_font_montserrat_28 = {0};
typedef struct { lv_color_t bg_color; uint8_t bg_opa; int radius; } lv_draw_rect_dsc_t;
typedef struct { lv_color_t color; const lv_font_t *font; int align; } lv_draw_label_dsc_t;
#define LV_SYMBOL_LEFT "<"
#define LV_SYMBOL_RIGHT ">"
#define LV_SYMBOL_REFRESH "R"
#define LV_SYMBOL_HOME "H"
#define LV_SYMBOL_PLUS "+"
#define LV_SYMBOL_CLOSE "X"
#define LV_SYMBOL_SEARCH "S"
#define LV_SYMBOL_SETTINGS "G"
static inline lv_obj_t *lv_obj_create(lv_obj_t *p) { (void)p; return (lv_obj_t*)1; }
static inline lv_obj_t *lv_button_create(lv_obj_t *p) { (void)p; return (lv_obj_t*)1; }
static inline lv_obj_t *lv_label_create(lv_obj_t *p) { (void)p; return (lv_obj_t*)1; }
static inline lv_obj_t *lv_textarea_create(lv_obj_t *p) { (void)p; return (lv_obj_t*)1; }
static inline lv_obj_t *lv_canvas_create(lv_obj_t *p) { (void)p; return (lv_obj_t*)1; }
static inline void lv_obj_set_size(lv_obj_t *o, int w, int h) { (void)o;(void)w;(void)h; }
static inline void lv_obj_set_width(lv_obj_t *o, int w) { (void)o;(void)w; }
static inline void lv_obj_set_height(lv_obj_t *o, int h) { (void)o;(void)h; }
static inline void lv_obj_set_pos(lv_obj_t *o, int x, int y) { (void)o;(void)x;(void)y; }
static inline void lv_obj_center(lv_obj_t *o) { (void)o; }
static inline void lv_obj_align(lv_obj_t *o, int a, int x, int y) { (void)o;(void)a;(void)x;(void)y; }
static inline void lv_obj_set_flex_flow(lv_obj_t *o, int f) { (void)o;(void)f; }
static inline void lv_obj_set_flex_align(lv_obj_t *o, int m, int c, int t) { (void)o;(void)m;(void)c;(void)t; }
static inline void lv_obj_set_flex_grow(lv_obj_t *o, int g) { (void)o;(void)g; }
static inline void lv_obj_add_flag(lv_obj_t *o, int f) { (void)o;(void)f; }
static inline void lv_obj_clear_flag(lv_obj_t *o, int f) { (void)o;(void)f; }
static inline void lv_obj_add_state(lv_obj_t *o, int s) { (void)o;(void)s; }
static inline void lv_obj_add_event_cb(lv_obj_t *o, lv_event_cb_t cb, int e, void *d) { (void)o;(void)cb;(void)e;(void)d; }
static inline void lv_obj_clean(lv_obj_t *o) { (void)o; }
static inline void lv_obj_delete(lv_obj_t *o) { (void)o; }
static inline void lv_obj_remove_style(lv_obj_t *o, void *s, int p) { (void)o;(void)s;(void)p; }
static inline lv_obj_t *lv_obj_get_child(lv_obj_t *o, int i) { (void)o;(void)i; return (lv_obj_t*)1; }
static inline int lv_obj_get_child_count(lv_obj_t *o) { (void)o; return 0; }
static inline int lv_obj_get_width(lv_obj_t *o) { (void)o; return 0; }
static inline int lv_obj_get_height(lv_obj_t *o) { (void)o; return 0; }
static inline void lv_obj_set_style_bg_color(lv_obj_t *o, lv_color_t c, int s) { (void)o;(void)c;(void)s; }
static inline void lv_obj_set_style_bg_opa(lv_obj_t *o, int a, int s) { (void)o;(void)a;(void)s; }
static inline void lv_obj_set_style_radius(lv_obj_t *o, int r, int s) { (void)o;(void)r;(void)s; }
static inline void lv_obj_set_style_border_color(lv_obj_t *o, lv_color_t c, int s) { (void)o;(void)c;(void)s; }
static inline void lv_obj_set_style_border_width(lv_obj_t *o, int w, int s) { (void)o;(void)w;(void)s; }
static inline void lv_obj_set_style_border_side(lv_obj_t *o, int s, int p) { (void)o;(void)s;(void)p; }
static inline void lv_obj_set_style_pad_all(lv_obj_t *o, int p, int s) { (void)o;(void)p;(void)s; }
static inline void lv_obj_set_style_pad_hor(lv_obj_t *o, int p, int s) { (void)o;(void)p;(void)s; }
static inline void lv_obj_set_style_pad_ver(lv_obj_t *o, int p, int s) { (void)o;(void)p;(void)s; }
static inline void lv_obj_set_style_pad_gap(lv_obj_t *o, int g, int s) { (void)o;(void)g;(void)s; }
static inline void lv_obj_set_style_text_color(lv_obj_t *o, lv_color_t c, int s) { (void)o;(void)c;(void)s; }
static inline void lv_obj_set_style_text_font(lv_obj_t *o, const lv_font_t *f, int s) { (void)o;(void)f;(void)s; }
static inline void lv_obj_set_style_text_align(lv_obj_t *o, int a, int s) { (void)o;(void)a;(void)s; }
static inline void lv_obj_set_style_min_width(lv_obj_t *o, int w, int s) { (void)o;(void)w;(void)s; }
static inline void lv_label_set_text(lv_obj_t *o, const char *t) { (void)o;(void)t; }
static inline void lv_label_set_text_fmt(lv_obj_t *o, const char *f, ...) { (void)o;(void)f; }
static inline void lv_label_set_long_mode(lv_obj_t *o, int m) { (void)o;(void)m; }
static inline const char *lv_label_get_text(lv_obj_t *o) { (void)o; return ""; }
static inline void lv_textarea_set_one_line(lv_obj_t *o, bool b) { (void)o;(void)b; }
static inline void lv_textarea_set_placeholder_text(lv_obj_t *o, const char *t) { (void)o;(void)t; }
static inline void lv_textarea_set_text(lv_obj_t *o, const char *t) { (void)o;(void)t; }
static inline const char *lv_textarea_get_text(lv_obj_t *o) { (void)o; return ""; }
static inline void lv_canvas_set_buffer(lv_obj_t *o, void *b, int w, int h, int f) { (void)o;(void)b;(void)w;(void)h;(void)f; }
static inline void lv_canvas_fill_bg(lv_obj_t *o, lv_color_t c, int a) { (void)o;(void)c;(void)a; }
static inline lv_layer_t *lv_canvas_init_layer(lv_obj_t *o) { (void)o; return NULL; }
static inline void lv_canvas_finish_layer(lv_obj_t *o, lv_layer_t *l) { (void)o;(void)l; }
static inline void lv_draw_rect_dsc_init(lv_draw_rect_dsc_t *d) { if(d){d->bg_opa=0;d->radius=0;} }
static inline void lv_draw_rect(lv_layer_t *l, lv_draw_rect_dsc_t *d, lv_area_t *a) { (void)l;(void)d;(void)a; }
static inline void lv_draw_label_dsc_init(lv_draw_label_dsc_t *d) { (void)d; }
static inline void lv_draw_label(lv_layer_t *l, lv_draw_label_dsc_t *d, lv_area_t *a) { (void)l;(void)d;(void)a; }
static inline void *lv_event_get_user_data(lv_event_t *e) { (void)e; return NULL; }
static inline lv_obj_t *lv_event_get_target(lv_event_t *e) { (void)e; return (lv_obj_t*)1; }
static inline lv_timer_t *lv_timer_create(lv_timer_cb_t cb, uint32_t p, void *d) { (void)cb;(void)p;(void)d; return NULL; }
static inline void lv_timer_delete(lv_timer_t *t) { (void)t; }
static inline uint32_t lv_tick_get(void) { return 0; }
static inline lv_display_t *lv_display_create(int w, int h) { (void)w;(void)h; return NULL; }
static inline void lv_display_set_flush_cb(lv_display_t *d, void *cb) { (void)d;(void)cb; }
static inline void lv_display_set_buffers(lv_display_t *d, void *b1, void *b2, uint32_t s, int m) { (void)d;(void)b1;(void)b2;(void)s;(void)m; }
static inline bool lv_display_flush_is_last(lv_display_t *d) { (void)d; return true; }
static inline void lv_display_flush_ready(lv_display_t *d) { (void)d; }
static inline lv_indev_t *lv_indev_create(void) { return NULL; }
static inline void lv_indev_set_type(lv_indev_t *i, int t) { (void)i;(void)t; }
static inline void lv_indev_set_read_cb(lv_indev_t *i, void *cb) { (void)i;(void)cb; }
static inline lv_obj_t *lv_screen_active(void) { return (lv_obj_t*)1; }
static inline void lv_init(void) {}
static inline void lv_deinit(void) {}
static inline void lv_tick_set_cb(void *cb) { (void)cb; }
static inline uint32_t lv_timer_handler(void) { return 5; }
#endif
