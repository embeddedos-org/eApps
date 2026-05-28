// SPDX-License-Identifier: MIT
// eVNC — EoS LVGL Application
#include "evnc.h"
#include <stdbool.h>
typedef struct {
    lv_obj_t *lbl_title;
    lv_obj_t *lbl_status;
    lv_timer_t *timer;
} evnc_ctx_t;
static evnc_ctx_t ctx;
static bool evnc_init(lv_obj_t *parent) {
    ctx.lbl_title = lv_label_create(parent);
    lv_obj_set_style_text_font(ctx.lbl_title, &lv_font_montserrat_24, 0);
    lv_obj_align(ctx.lbl_title, LV_ALIGN_TOP_MID, 0, 16);
    lv_label_set_text(ctx.lbl_title, "eVNC");
    ctx.lbl_status = lv_label_create(parent);
    lv_obj_align(ctx.lbl_status, LV_ALIGN_CENTER, 0, 0);
    lv_label_set_text(ctx.lbl_status, "VNC remote viewer\nv2.0.0 — Ready");
    lv_obj_t *btn = lv_btn_create(parent);
    lv_obj_align(btn, LV_ALIGN_BOTTOM_MID, 0, -16);
    lv_obj_t *lbl = lv_label_create(btn);
    lv_label_set_text(lbl, "Open");
    ctx.timer = NULL;
    return true;
}
static void evnc_deinit(void) { }
static void evnc_on_show(void) { }
static void evnc_on_hide(void) { }
const eapps_app_info_t evnc_info = {
    .id = "evnc", .name = "eVNC", .icon = "vnc",
    .description = "VNC remote viewer", .category = EAPPS_CAT_NETWORK, .version = "2.0.0",
};
const eapps_app_lifecycle_t evnc_lifecycle = {
    .init = evnc_init, .deinit = evnc_deinit,
    .on_show = evnc_on_show, .on_hide = evnc_on_hide,
};
