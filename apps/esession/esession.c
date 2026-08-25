// SPDX-License-Identifier: MIT
// eSession — EoS LVGL Application
#include "esession.h"
#include <stdbool.h>
typedef struct {
    lv_obj_t *lbl_title;
    lv_obj_t *lbl_status;
    lv_timer_t *timer;
} esession_ctx_t;
static esession_ctx_t ctx;
static bool esession_init(lv_obj_t *parent) {
    ctx.lbl_title = lv_label_create(parent);
    lv_obj_set_style_text_font(ctx.lbl_title, &lv_font_montserrat_24, 0);
    lv_obj_align(ctx.lbl_title, LV_ALIGN_TOP_MID, 0, 16);
    lv_label_set_text(ctx.lbl_title, "eSession");
    ctx.lbl_status = lv_label_create(parent);
    lv_obj_align(ctx.lbl_status, LV_ALIGN_CENTER, 0, 0);
    lv_label_set_text(ctx.lbl_status, "Session manager\nv2.0.0 — Ready");
    lv_obj_t *btn = lv_btn_create(parent);
    lv_obj_align(btn, LV_ALIGN_BOTTOM_MID, 0, -16);
    lv_obj_t *lbl = lv_label_create(btn);
    lv_label_set_text(lbl, "Open");
    ctx.timer = NULL;
    return true;
}
static void esession_deinit(void) { }
static void esession_on_show(void) { }
static void esession_on_hide(void) { }
const eapps_app_info_t esession_info = {
    .id = "esession", .name = "eSession", .icon = "ssn",
    .description = "Session manager", .category = EAPPS_CAT_SYSTEM, .version = "2.0.0",
};
const eapps_app_lifecycle_t esession_lifecycle = {
    .init = esession_init, .deinit = esession_deinit,
    .on_show = esession_on_show, .on_hide = esession_on_hide,
};
