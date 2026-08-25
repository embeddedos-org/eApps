// SPDX-License-Identifier: MIT
// eGuard — EoS LVGL Application
#include "eguard.h"
#include <stdbool.h>
#include <string.h>

typedef struct {
    bool guard_active;
    uint32_t interval_sec;
    uint32_t elapsed_sec;
    lv_obj_t *lbl_status;
    lv_obj_t *lbl_timer;
    lv_obj_t *btn_toggle;
    lv_obj_t *lbl_interval;
    lv_timer_t *tick_timer;
} eguard_state_t;

static eguard_state_t s;

static void eguard_update_ui(void) {
    if (s.lbl_status)
        lv_label_set_text(s.lbl_status, s.guard_active ? LV_SYMBOL_OK " GUARDING" : LV_SYMBOL_PAUSE " PAUSED");
    if (s.btn_toggle) {
        lv_obj_t *lbl = lv_obj_get_child(s.btn_toggle, 0);
        if (lbl) lv_label_set_text(lbl, s.guard_active ? LV_SYMBOL_STOP " Stop" : LV_SYMBOL_PLAY " Start");
    }
    if (s.lbl_interval) {
        char buf[32];
        lv_snprintf(buf, sizeof(buf), "Interval: %us", s.interval_sec);
        lv_label_set_text(s.lbl_interval, buf);
    }
}

static void eguard_tick_cb(lv_timer_t *t) {
    (void)t;
    if (!s.guard_active) return;
    s.elapsed_sec++;
    if (s.lbl_timer) {
        char buf[32];
        uint32_t h = s.elapsed_sec / 3600;
        uint32_t m = (s.elapsed_sec % 3600) / 60;
        uint32_t sec = s.elapsed_sec % 60;
        lv_snprintf(buf, sizeof(buf), "%02u:%02u:%02u", h, m, sec);
        lv_label_set_text(s.lbl_timer, buf);
    }
}

static void eguard_toggle_cb(lv_event_t *e) {
    (void)e;
    s.guard_active = !s.guard_active;
    if (!s.guard_active) s.elapsed_sec = 0;
    if (s.lbl_timer) lv_label_set_text(s.lbl_timer, "00:00:00");
    eguard_update_ui();
}

static void eguard_interval_cb(lv_event_t *e) {
    lv_obj_t *dd = lv_event_get_target(e);
    uint16_t sel = lv_dropdown_get_selected(dd);
    static const uint32_t intervals[] = {30, 60, 120, 300};
    if (sel < 4) s.interval_sec = intervals[sel];
    eguard_update_ui();
}

static bool eguard_init(lv_obj_t *parent) {
    memset(&s, 0, sizeof(s));
    s.interval_sec = 60;

    lv_obj_t *title = lv_label_create(parent);
    lv_label_set_text(title, "eGuard — Session Keep-Alive");
    lv_obj_set_style_text_font(title, &lv_font_montserrat_16, 0);
    lv_obj_align(title, LV_ALIGN_TOP_MID, 0, 10);

    s.lbl_status = lv_label_create(parent);
    lv_obj_set_style_text_font(s.lbl_status, &lv_font_montserrat_14, 0);
    lv_obj_align(s.lbl_status, LV_ALIGN_CENTER, 0, -40);

    s.lbl_timer = lv_label_create(parent);
    lv_label_set_text(s.lbl_timer, "00:00:00");
    lv_obj_set_style_text_font(s.lbl_timer, &lv_font_montserrat_24, 0);
    lv_obj_align(s.lbl_timer, LV_ALIGN_CENTER, 0, -10);

    s.btn_toggle = lv_btn_create(parent);
    lv_obj_set_size(s.btn_toggle, 120, 40);
    lv_obj_align(s.btn_toggle, LV_ALIGN_CENTER, 0, 30);
    lv_obj_add_event_cb(s.btn_toggle, eguard_toggle_cb, LV_EVENT_CLICKED, NULL);
    lv_obj_t *btn_lbl = lv_label_create(s.btn_toggle);
    lv_obj_center(btn_lbl);

    /* Interval dropdown */
    lv_obj_t *dd = lv_dropdown_create(parent);
    lv_dropdown_set_options(dd, "30s\n60s\n120s\n300s");
    lv_dropdown_set_selected(dd, 1);
    lv_obj_set_width(dd, 100);
    lv_obj_align(dd, LV_ALIGN_CENTER, 0, 80);
    lv_obj_add_event_cb(dd, eguard_interval_cb, LV_EVENT_VALUE_CHANGED, NULL);

    s.lbl_interval = lv_label_create(parent);
    lv_obj_align(s.lbl_interval, LV_ALIGN_CENTER, 0, 110);

    s.tick_timer = lv_timer_create(eguard_tick_cb, 1000, NULL);

    eguard_update_ui();
    return true;
}

static void eguard_deinit(void) {
    if (s.tick_timer) lv_timer_del(s.tick_timer);
    memset(&s, 0, sizeof(s));
}

static void eguard_on_show(void) { }
static void eguard_on_hide(void) { }

const eapps_app_info_t eguard_info = {
    .id = "eguard", .name = "eGuard", .icon = "grd",
    .description = "Session keep-alive guard — prevents sleep, lock & idle",
    .category = EAPPS_CAT_SECURITY, .version = "3.0.0",
};
const eapps_app_lifecycle_t eguard_lifecycle = {
    .init = eguard_init, .deinit = eguard_deinit,
    .on_show = eguard_on_show, .on_hide = eguard_on_hide,
};
