// SPDX-License-Identifier: MIT
// eClock — EoS LVGL Application
#include "eclock.h"
#include <stdbool.h>
#include <string.h>

typedef struct {
    lv_obj_t *label_time;
    lv_obj_t *label_date;
    lv_obj_t *btn_stopwatch;
    lv_obj_t *label_sw;
    lv_timer_t *timer;
    uint32_t sw_ms;
    bool sw_running;
} eclock_ctx_t;
static eclock_ctx_t ctx;


static void eclock_timer_cb(lv_timer_t *t) {
    (void)t;
    if (ctx.sw_running) {
        ctx.sw_ms += 100;
        uint32_t m = ctx.sw_ms / 60000;
        uint32_t s = (ctx.sw_ms % 60000) / 1000;
        uint32_t ms = ctx.sw_ms % 1000;
        lv_label_set_text_fmt(ctx.label_sw, "%02lu:%02lu.%03lu", m, s, ms);
    }
}

static bool eclock_init(lv_obj_t *parent) {

    ctx.sw_ms = 0; ctx.sw_running = false;
    ctx.label_time = lv_label_create(parent);
    lv_obj_set_style_text_font(ctx.label_time, &lv_font_montserrat_48, 0);
    lv_obj_align(ctx.label_time, LV_ALIGN_CENTER, 0, -60);
    lv_label_set_text(ctx.label_time, "00:00:00");
    ctx.label_date = lv_label_create(parent);
    lv_obj_align(ctx.label_date, LV_ALIGN_CENTER, 0, -10);
    lv_label_set_text(ctx.label_date, "Wed, 28 May 2025");
    ctx.btn_stopwatch = lv_btn_create(parent);
    lv_obj_align(ctx.btn_stopwatch, LV_ALIGN_CENTER, 0, 60);
    lv_obj_t *lbl = lv_label_create(ctx.btn_stopwatch);
    lv_label_set_text(lbl, "Start Stopwatch");
    ctx.label_sw = lv_label_create(parent);
    lv_obj_align(ctx.label_sw, LV_ALIGN_CENTER, 0, 110);
    lv_label_set_text(ctx.label_sw, "00:00.000");
    ctx.timer = lv_timer_create(eclock_timer_cb, 100, NULL);
    return true;

}
static void eclock_deinit(void) {
    if (ctx.timer) { lv_timer_del(ctx.timer); ctx.timer = NULL; }
}
static void eclock_on_show(void) { }
static void eclock_on_hide(void) { }
const eapps_app_info_t eclock_info = {
    .id = "eclock", .name = "eClock", .icon = "clk",
    .description = "Clock with stopwatch and timer", .category = EAPPS_CAT_PRODUCTIVITY, .version = "2.0.0",
};
const eapps_app_lifecycle_t eclock_lifecycle = {
    .init = eclock_init, .deinit = eclock_deinit,
    .on_show = eclock_on_show, .on_hide = eclock_on_hide,
};
