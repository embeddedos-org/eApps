// SPDX-License-Identifier: MIT
// eBuffer — EoS LVGL Application
#include "ebuffer.h"
#include <stdbool.h>
typedef struct {
    lv_obj_t *lbl_title;
    lv_obj_t *lbl_status;
    lv_timer_t *timer;
} ebuffer_ctx_t;
static ebuffer_ctx_t ctx;
static bool ebuffer_init(lv_obj_t *parent) {
    ctx.lbl_title = lv_label_create(parent);
    lv_obj_set_style_text_font(ctx.lbl_title, &lv_font_montserrat_24, 0);
    lv_obj_align(ctx.lbl_title, LV_ALIGN_TOP_MID, 0, 16);
    lv_label_set_text(ctx.lbl_title, "eBuffer");
    ctx.lbl_status = lv_label_create(parent);
    lv_obj_align(ctx.lbl_status, LV_ALIGN_CENTER, 0, 0);
    lv_label_set_text(ctx.lbl_status, "Clipboard manager\nv2.0.0 — Ready");
    lv_obj_t *btn = lv_btn_create(parent);
    lv_obj_align(btn, LV_ALIGN_BOTTOM_MID, 0, -16);
    lv_obj_t *lbl = lv_label_create(btn);
    lv_label_set_text(lbl, "Open");
    ctx.timer = NULL;
    return true;
}
static void ebuffer_deinit(void) { }
static void ebuffer_on_show(void) { }
static void ebuffer_on_hide(void) { }
const eapps_app_info_t ebuffer_info = {
    .id = "ebuffer", .name = "eBuffer", .icon = "buf",
    .description = "Clipboard manager", .category = EAPPS_CAT_SYSTEM, .version = "2.0.0",
};
const eapps_app_lifecycle_t ebuffer_lifecycle = {
    .init = ebuffer_init, .deinit = ebuffer_deinit,
    .on_show = ebuffer_on_show, .on_hide = ebuffer_on_hide,
};
