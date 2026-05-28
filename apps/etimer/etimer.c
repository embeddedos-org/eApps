// SPDX-License-Identifier: MIT
// eTimer — EoS LVGL Application
#include "etimer.h"
#include <stdbool.h>
#include <string.h>

typedef struct {
    lv_obj_t *lbl_time;
    lv_obj_t *btn_start;
    lv_timer_t *timer;
    uint32_t remaining_ms;
    bool running;
} etimer_ctx_t;
static etimer_ctx_t ctx;


static void etimer_tick(lv_timer_t *t) {
    (void)t;
    if (ctx.remaining_ms <= 1000) {
        ctx.remaining_ms = 0; ctx.running = false;
        lv_timer_pause(ctx.timer);
        lv_label_set_text(ctx.lbl_time, "00:00");
        return;
    }
    ctx.remaining_ms -= 1000;
    uint32_t m = ctx.remaining_ms / 60000;
    uint32_t s = (ctx.remaining_ms % 60000) / 1000;
    lv_label_set_text_fmt(ctx.lbl_time, "%02lu:%02lu", m, s);
}
static void etimer_btn_cb(lv_event_t *e) {
    (void)e;
    ctx.running = !ctx.running;
    if (ctx.running) { lv_timer_resume(ctx.timer); lv_label_set_text(lv_obj_get_child(ctx.btn_start,0), "Pause"); }
    else { lv_timer_pause(ctx.timer); lv_label_set_text(lv_obj_get_child(ctx.btn_start,0), "Resume"); }
}

static bool etimer_init(lv_obj_t *parent) {

    ctx.remaining_ms = 5 * 60 * 1000; ctx.running = false;
    ctx.lbl_time = lv_label_create(parent);
    lv_obj_set_style_text_font(ctx.lbl_time, &lv_font_montserrat_48, 0);
    lv_obj_align(ctx.lbl_time, LV_ALIGN_CENTER, 0, -40);
    lv_label_set_text(ctx.lbl_time, "05:00");
    ctx.btn_start = lv_btn_create(parent);
    lv_obj_align(ctx.btn_start, LV_ALIGN_CENTER, 0, 40);
    lv_obj_t *lbl = lv_label_create(ctx.btn_start);
    lv_label_set_text(lbl, "Start");
    lv_obj_add_event_cb(ctx.btn_start, etimer_btn_cb, LV_EVENT_CLICKED, NULL);
    ctx.timer = lv_timer_create(etimer_tick, 1000, NULL);
    lv_timer_pause(ctx.timer);
    return true;

}
static void etimer_deinit(void) {
    if (ctx.timer) { lv_timer_del(ctx.timer); ctx.timer = NULL; }
}
static void etimer_on_show(void) { }
static void etimer_on_hide(void) { }
const eapps_app_info_t etimer_info = {
    .id = "etimer", .name = "eTimer", .icon = "tmr",
    .description = "Countdown timer with presets", .category = EAPPS_CAT_PRODUCTIVITY, .version = "2.0.0",
};
const eapps_app_lifecycle_t etimer_lifecycle = {
    .init = etimer_init, .deinit = etimer_deinit,
    .on_show = etimer_on_show, .on_hide = etimer_on_hide,
};
