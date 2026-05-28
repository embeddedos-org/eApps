// SPDX-License-Identifier: MIT
// eVPN — EoS LVGL Application
#include "evpn.h"
#include <stdbool.h>
typedef struct {
    lv_obj_t *lbl_title;
    lv_obj_t *lbl_status;
    lv_timer_t *timer;
} evpn_ctx_t;
static evpn_ctx_t ctx;
static bool evpn_init(lv_obj_t *parent) {
    ctx.lbl_title = lv_label_create(parent);
    lv_obj_set_style_text_font(ctx.lbl_title, &lv_font_montserrat_24, 0);
    lv_obj_align(ctx.lbl_title, LV_ALIGN_TOP_MID, 0, 16);
    lv_label_set_text(ctx.lbl_title, "eVPN");
    ctx.lbl_status = lv_label_create(parent);
    lv_obj_align(ctx.lbl_status, LV_ALIGN_CENTER, 0, 0);
    lv_label_set_text(ctx.lbl_status, "VPN client\nv2.0.0 — Ready");
    lv_obj_t *btn = lv_btn_create(parent);
    lv_obj_align(btn, LV_ALIGN_BOTTOM_MID, 0, -16);
    lv_obj_t *lbl = lv_label_create(btn);
    lv_label_set_text(lbl, "Open");
    ctx.timer = NULL;
    return true;
}
static void evpn_deinit(void) { }
static void evpn_on_show(void) { }
static void evpn_on_hide(void) { }
const eapps_app_info_t evpn_info = {
    .id = "evpn", .name = "eVPN", .icon = "vpn",
    .description = "VPN client", .category = EAPPS_CAT_NETWORK, .version = "2.0.0",
};
const eapps_app_lifecycle_t evpn_lifecycle = {
    .init = evpn_init, .deinit = evpn_deinit,
    .on_show = evpn_on_show, .on_hide = evpn_on_hide,
};
