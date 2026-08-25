// SPDX-License-Identifier: MIT
// ePaint — EoS LVGL Application
#include "epaint.h"
#include <stdbool.h>
typedef struct {
    lv_obj_t *lbl_title;
    lv_obj_t *lbl_status;
    lv_timer_t *timer;
} epaint_ctx_t;
static epaint_ctx_t ctx;
static bool epaint_init(lv_obj_t *parent) {
    ctx.lbl_title = lv_label_create(parent);
    lv_obj_set_style_text_font(ctx.lbl_title, &lv_font_montserrat_24, 0);
    lv_obj_align(ctx.lbl_title, LV_ALIGN_TOP_MID, 0, 16);
    lv_label_set_text(ctx.lbl_title, "ePaint");
    ctx.lbl_status = lv_label_create(parent);
    lv_obj_align(ctx.lbl_status, LV_ALIGN_CENTER, 0, 0);
    lv_label_set_text(ctx.lbl_status, "Drawing and painting\nv2.0.0 — Ready");
    lv_obj_t *btn = lv_btn_create(parent);
    lv_obj_align(btn, LV_ALIGN_BOTTOM_MID, 0, -16);
    lv_obj_t *lbl = lv_label_create(btn);
    lv_label_set_text(lbl, "Open");
    ctx.timer = NULL;
    return true;
}
static void epaint_deinit(void) { }
static void epaint_on_show(void) { }
static void epaint_on_hide(void) { }
const eapps_app_info_t epaint_info = {
    .id = "epaint", .name = "ePaint", .icon = "pnt",
    .description = "Drawing and painting", .category = EAPPS_CAT_MEDIA, .version = "2.0.0",
};
const eapps_app_lifecycle_t epaint_lifecycle = {
    .init = epaint_init, .deinit = epaint_deinit,
    .on_show = epaint_on_show, .on_hide = epaint_on_hide,
};
