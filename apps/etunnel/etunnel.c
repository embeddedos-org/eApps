// SPDX-License-Identifier: MIT
// eTunnel — EoS LVGL Application
#include "etunnel.h"
#include <stdbool.h>
typedef struct {
    lv_obj_t *lbl_title;
    lv_obj_t *lbl_status;
    lv_timer_t *timer;
} etunnel_ctx_t;
static etunnel_ctx_t ctx;
static bool etunnel_init(lv_obj_t *parent) {
    ctx.lbl_title = lv_label_create(parent);
    lv_obj_set_style_text_font(ctx.lbl_title, &lv_font_montserrat_24, 0);
    lv_obj_align(ctx.lbl_title, LV_ALIGN_TOP_MID, 0, 16);
    lv_label_set_text(ctx.lbl_title, "eTunnel");
    ctx.lbl_status = lv_label_create(parent);
    lv_obj_align(ctx.lbl_status, LV_ALIGN_CENTER, 0, 0);
    lv_label_set_text(ctx.lbl_status, "VPN tunnel manager\nv2.0.0 — Ready");
    lv_obj_t *btn = lv_btn_create(parent);
    lv_obj_align(btn, LV_ALIGN_BOTTOM_MID, 0, -16);
    lv_obj_t *lbl = lv_label_create(btn);
    lv_label_set_text(lbl, "Open");
    ctx.timer = NULL;
    return true;
}
static void etunnel_deinit(void) { }
static void etunnel_on_show(void) { }
static void etunnel_on_hide(void) { }
const eapps_app_info_t etunnel_info = {
    .id = "etunnel", .name = "eTunnel", .icon = "tun",
    .description = "VPN tunnel manager", .category = EAPPS_CAT_NETWORK, .version = "2.0.0",
};
const eapps_app_lifecycle_t etunnel_lifecycle = {
    .init = etunnel_init, .deinit = etunnel_deinit,
    .on_show = etunnel_on_show, .on_hide = etunnel_on_hide,
};
