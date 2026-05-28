// SPDX-License-Identifier: MIT
// eBirds — EoS LVGL Application
#include "ebirds.h"
#include <stdbool.h>
typedef struct {
    lv_obj_t *lbl_title;
    lv_obj_t *lbl_status;
    lv_timer_t *timer;
} ebirds_ctx_t;
static ebirds_ctx_t ctx;
static bool ebirds_init(lv_obj_t *parent) {
    ctx.lbl_title = lv_label_create(parent);
    lv_obj_set_style_text_font(ctx.lbl_title, &lv_font_montserrat_24, 0);
    lv_obj_align(ctx.lbl_title, LV_ALIGN_TOP_MID, 0, 16);
    lv_label_set_text(ctx.lbl_title, "eBirds");
    ctx.lbl_status = lv_label_create(parent);
    lv_obj_align(ctx.lbl_status, LV_ALIGN_CENTER, 0, 0);
    lv_label_set_text(ctx.lbl_status, "Flappy bird-style game\nv2.0.0 — Ready");
    lv_obj_t *btn = lv_btn_create(parent);
    lv_obj_align(btn, LV_ALIGN_BOTTOM_MID, 0, -16);
    lv_obj_t *lbl = lv_label_create(btn);
    lv_label_set_text(lbl, "Open");
    ctx.timer = NULL;
    return true;
}
static void ebirds_deinit(void) { }
static void ebirds_on_show(void) { }
static void ebirds_on_hide(void) { }
const eapps_app_info_t ebirds_info = {
    .id = "ebirds", .name = "eBirds", .icon = "bir",
    .description = "Flappy bird-style game", .category = EAPPS_CAT_GAMES, .version = "2.0.0",
};
const eapps_app_lifecycle_t ebirds_lifecycle = {
    .init = ebirds_init, .deinit = ebirds_deinit,
    .on_show = ebirds_on_show, .on_hide = ebirds_on_hide,
};
