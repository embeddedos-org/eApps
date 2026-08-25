// SPDX-License-Identifier: MIT
// eCrush — EoS LVGL Application
#include "ecrush.h"
#include <stdbool.h>
typedef struct {
    lv_obj_t *lbl_title;
    lv_obj_t *lbl_status;
    lv_timer_t *timer;
} ecrush_ctx_t;
static ecrush_ctx_t ctx;
static bool ecrush_init(lv_obj_t *parent) {
    ctx.lbl_title = lv_label_create(parent);
    lv_obj_set_style_text_font(ctx.lbl_title, &lv_font_montserrat_24, 0);
    lv_obj_align(ctx.lbl_title, LV_ALIGN_TOP_MID, 0, 16);
    lv_label_set_text(ctx.lbl_title, "eCrush");
    ctx.lbl_status = lv_label_create(parent);
    lv_obj_align(ctx.lbl_status, LV_ALIGN_CENTER, 0, 0);
    lv_label_set_text(ctx.lbl_status, "Match-3 puzzle game\nv2.0.0 — Ready");
    lv_obj_t *btn = lv_btn_create(parent);
    lv_obj_align(btn, LV_ALIGN_BOTTOM_MID, 0, -16);
    lv_obj_t *lbl = lv_label_create(btn);
    lv_label_set_text(lbl, "Open");
    ctx.timer = NULL;
    return true;
}
static void ecrush_deinit(void) { }
static void ecrush_on_show(void) { }
static void ecrush_on_hide(void) { }
const eapps_app_info_t ecrush_info = {
    .id = "ecrush", .name = "eCrush", .icon = "crs",
    .description = "Match-3 puzzle game", .category = EAPPS_CAT_GAMES, .version = "2.0.0",
};
const eapps_app_lifecycle_t ecrush_lifecycle = {
    .init = ecrush_init, .deinit = ecrush_deinit,
    .on_show = ecrush_on_show, .on_hide = ecrush_on_hide,
};
