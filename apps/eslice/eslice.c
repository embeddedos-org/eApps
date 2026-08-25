// SPDX-License-Identifier: MIT
// eSlice — EoS LVGL Application
#include "eslice.h"
#include <stdbool.h>
typedef struct {
    lv_obj_t *lbl_title;
    lv_obj_t *lbl_status;
    lv_timer_t *timer;
} eslice_ctx_t;
static eslice_ctx_t ctx;
static bool eslice_init(lv_obj_t *parent) {
    ctx.lbl_title = lv_label_create(parent);
    lv_obj_set_style_text_font(ctx.lbl_title, &lv_font_montserrat_24, 0);
    lv_obj_align(ctx.lbl_title, LV_ALIGN_TOP_MID, 0, 16);
    lv_label_set_text(ctx.lbl_title, "eSlice");
    ctx.lbl_status = lv_label_create(parent);
    lv_obj_align(ctx.lbl_status, LV_ALIGN_CENTER, 0, 0);
    lv_label_set_text(ctx.lbl_status, "Fruit slice game\nv2.0.0 — Ready");
    lv_obj_t *btn = lv_btn_create(parent);
    lv_obj_align(btn, LV_ALIGN_BOTTOM_MID, 0, -16);
    lv_obj_t *lbl = lv_label_create(btn);
    lv_label_set_text(lbl, "Open");
    ctx.timer = NULL;
    return true;
}
static void eslice_deinit(void) { }
static void eslice_on_show(void) { }
static void eslice_on_hide(void) { }
const eapps_app_info_t eslice_info = {
    .id = "eslice", .name = "eSlice", .icon = "slc",
    .description = "Fruit slice game", .category = EAPPS_CAT_GAMES, .version = "2.0.0",
};
const eapps_app_lifecycle_t eslice_lifecycle = {
    .init = eslice_init, .deinit = eslice_deinit,
    .on_show = eslice_on_show, .on_hide = eslice_on_hide,
};
