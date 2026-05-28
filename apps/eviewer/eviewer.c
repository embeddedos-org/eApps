// SPDX-License-Identifier: MIT
// eViewer — EoS LVGL Application
#include "eviewer.h"
#include <stdbool.h>
typedef struct {
    lv_obj_t *lbl_title;
    lv_obj_t *lbl_status;
    lv_timer_t *timer;
} eviewer_ctx_t;
static eviewer_ctx_t ctx;
static bool eviewer_init(lv_obj_t *parent) {
    ctx.lbl_title = lv_label_create(parent);
    lv_obj_set_style_text_font(ctx.lbl_title, &lv_font_montserrat_24, 0);
    lv_obj_align(ctx.lbl_title, LV_ALIGN_TOP_MID, 0, 16);
    lv_label_set_text(ctx.lbl_title, "eViewer");
    ctx.lbl_status = lv_label_create(parent);
    lv_obj_align(ctx.lbl_status, LV_ALIGN_CENTER, 0, 0);
    lv_label_set_text(ctx.lbl_status, "Document viewer\nv2.0.0 — Ready");
    lv_obj_t *btn = lv_btn_create(parent);
    lv_obj_align(btn, LV_ALIGN_BOTTOM_MID, 0, -16);
    lv_obj_t *lbl = lv_label_create(btn);
    lv_label_set_text(lbl, "Open");
    ctx.timer = NULL;
    return true;
}
static void eviewer_deinit(void) { }
static void eviewer_on_show(void) { }
static void eviewer_on_hide(void) { }
const eapps_app_info_t eviewer_info = {
    .id = "eviewer", .name = "eViewer", .icon = "vwr",
    .description = "Document viewer", .category = EAPPS_CAT_MEDIA, .version = "2.0.0",
};
const eapps_app_lifecycle_t eviewer_lifecycle = {
    .init = eviewer_init, .deinit = eviewer_deinit,
    .on_show = eviewer_on_show, .on_hide = eviewer_on_hide,
};
