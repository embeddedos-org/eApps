// SPDX-License-Identifier: MIT
// eSettings — EoS LVGL Application
#include "esettings.h"
#include <stdbool.h>
typedef struct {
    lv_obj_t *lbl_title;
    lv_obj_t *lbl_status;
    lv_timer_t *timer;
} esettings_ctx_t;
static esettings_ctx_t ctx;
static bool esettings_init(lv_obj_t *parent) {
    ctx.lbl_title = lv_label_create(parent);
    lv_obj_set_style_text_font(ctx.lbl_title, &lv_font_montserrat_24, 0);
    lv_obj_align(ctx.lbl_title, LV_ALIGN_TOP_MID, 0, 16);
    lv_label_set_text(ctx.lbl_title, "eSettings");
    ctx.lbl_status = lv_label_create(parent);
    lv_obj_align(ctx.lbl_status, LV_ALIGN_CENTER, 0, 0);
    lv_label_set_text(ctx.lbl_status, "System settings\nv2.0.0 — Ready");
    lv_obj_t *btn = lv_btn_create(parent);
    lv_obj_align(btn, LV_ALIGN_BOTTOM_MID, 0, -16);
    lv_obj_t *lbl = lv_label_create(btn);
    lv_label_set_text(lbl, "Open");
    ctx.timer = NULL;
    return true;
}
static void esettings_deinit(void) { }
static void esettings_on_show(void) { }
static void esettings_on_hide(void) { }
const eapps_app_info_t esettings_info = {
    .id = "esettings", .name = "eSettings", .icon = "set",
    .description = "System settings", .category = EAPPS_CAT_SYSTEM, .version = "2.0.0",
};
const eapps_app_lifecycle_t esettings_lifecycle = {
    .init = esettings_init, .deinit = esettings_deinit,
    .on_show = esettings_on_show, .on_hide = esettings_on_hide,
};
