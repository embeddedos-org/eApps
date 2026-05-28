// SPDX-License-Identifier: MIT
// eTrack — EoS LVGL Application
#include "etrack.h"
#include <stdbool.h>
typedef struct {
    lv_obj_t *lbl_title;
    lv_obj_t *lbl_status;
    lv_timer_t *timer;
} etrack_ctx_t;
static etrack_ctx_t ctx;
static bool etrack_init(lv_obj_t *parent) {
    ctx.lbl_title = lv_label_create(parent);
    lv_obj_set_style_text_font(ctx.lbl_title, &lv_font_montserrat_24, 0);
    lv_obj_align(ctx.lbl_title, LV_ALIGN_TOP_MID, 0, 16);
    lv_label_set_text(ctx.lbl_title, "eTrack");
    ctx.lbl_status = lv_label_create(parent);
    lv_obj_align(ctx.lbl_status, LV_ALIGN_CENTER, 0, 0);
    lv_label_set_text(ctx.lbl_status, "Task and time tracker\nv2.0.0 — Ready");
    lv_obj_t *btn = lv_btn_create(parent);
    lv_obj_align(btn, LV_ALIGN_BOTTOM_MID, 0, -16);
    lv_obj_t *lbl = lv_label_create(btn);
    lv_label_set_text(lbl, "Open");
    ctx.timer = NULL;
    return true;
}
static void etrack_deinit(void) { }
static void etrack_on_show(void) { }
static void etrack_on_hide(void) { }
const eapps_app_info_t etrack_info = {
    .id = "etrack", .name = "eTrack", .icon = "trk",
    .description = "Task and time tracker", .category = EAPPS_CAT_PRODUCTIVITY, .version = "2.0.0",
};
const eapps_app_lifecycle_t etrack_lifecycle = {
    .init = etrack_init, .deinit = etrack_deinit,
    .on_show = etrack_on_show, .on_hide = etrack_on_hide,
};
