// SPDX-License-Identifier: MIT
// eRunner — EoS LVGL Application
#include "erunner.h"
#include <stdbool.h>
typedef struct {
    lv_obj_t *lbl_title;
    lv_obj_t *lbl_status;
    lv_timer_t *timer;
} erunner_ctx_t;
static erunner_ctx_t ctx;
static bool erunner_init(lv_obj_t *parent) {
    ctx.lbl_title = lv_label_create(parent);
    lv_obj_set_style_text_font(ctx.lbl_title, &lv_font_montserrat_24, 0);
    lv_obj_align(ctx.lbl_title, LV_ALIGN_TOP_MID, 0, 16);
    lv_label_set_text(ctx.lbl_title, "eRunner");
    ctx.lbl_status = lv_label_create(parent);
    lv_obj_align(ctx.lbl_status, LV_ALIGN_CENTER, 0, 0);
    lv_label_set_text(ctx.lbl_status, "App launcher\nv2.0.0 — Ready");
    lv_obj_t *btn = lv_btn_create(parent);
    lv_obj_align(btn, LV_ALIGN_BOTTOM_MID, 0, -16);
    lv_obj_t *lbl = lv_label_create(btn);
    lv_label_set_text(lbl, "Open");
    ctx.timer = NULL;
    return true;
}
static void erunner_deinit(void) { }
static void erunner_on_show(void) { }
static void erunner_on_hide(void) { }
const eapps_app_info_t erunner_info = {
    .id = "erunner", .name = "eRunner", .icon = "run",
    .description = "App launcher", .category = EAPPS_CAT_SYSTEM, .version = "2.0.0",
};
const eapps_app_lifecycle_t erunner_lifecycle = {
    .init = erunner_init, .deinit = erunner_deinit,
    .on_show = erunner_on_show, .on_hide = erunner_on_hide,
};
