// SPDX-License-Identifier: MIT
// eConverter — EoS LVGL Application
#include "econverter.h"
#include <stdbool.h>
typedef struct {
    lv_obj_t *lbl_title;
    lv_obj_t *lbl_status;
    lv_timer_t *timer;
} econverter_ctx_t;
static econverter_ctx_t ctx;
static bool econverter_init(lv_obj_t *parent) {
    ctx.lbl_title = lv_label_create(parent);
    lv_obj_set_style_text_font(ctx.lbl_title, &lv_font_montserrat_24, 0);
    lv_obj_align(ctx.lbl_title, LV_ALIGN_TOP_MID, 0, 16);
    lv_label_set_text(ctx.lbl_title, "eConverter");
    ctx.lbl_status = lv_label_create(parent);
    lv_obj_align(ctx.lbl_status, LV_ALIGN_CENTER, 0, 0);
    lv_label_set_text(ctx.lbl_status, "Unit and currency converter\nv2.0.0 — Ready");
    lv_obj_t *btn = lv_btn_create(parent);
    lv_obj_align(btn, LV_ALIGN_BOTTOM_MID, 0, -16);
    lv_obj_t *lbl = lv_label_create(btn);
    lv_label_set_text(lbl, "Open");
    ctx.timer = NULL;
    return true;
}
static void econverter_deinit(void) { }
static void econverter_on_show(void) { }
static void econverter_on_hide(void) { }
const eapps_app_info_t econverter_info = {
    .id = "econverter", .name = "eConverter", .icon = "cvt",
    .description = "Unit and currency converter", .category = EAPPS_CAT_PRODUCTIVITY, .version = "2.0.0",
};
const eapps_app_lifecycle_t econverter_lifecycle = {
    .init = econverter_init, .deinit = econverter_deinit,
    .on_show = econverter_on_show, .on_hide = econverter_on_hide,
};
