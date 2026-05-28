// SPDX-License-Identifier: MIT
// Dice Roller — EoS LVGL Application
#include "dice.h"
#include <stdbool.h>
#include <string.h>

typedef struct {
    lv_obj_t *lbl_result;
    lv_obj_t *lbl_history;
    int history[10];
    int hist_len;
    uint64_t seed;
    lv_timer_t *timer;
} dice_ctx_t;
static dice_ctx_t ctx;


static void dice_roll_cb(lv_event_t *e) {
    (void)e;
    ctx.seed = ctx.seed * 6364136223846793005ULL + 1442695040888963407ULL;
    int val = (int)((ctx.seed >> 33) % 6) + 1;
    lv_label_set_text_fmt(ctx.lbl_result, "%d", val);
    if (ctx.hist_len < 10) ctx.history[ctx.hist_len++] = val;
    else { for (int i=0;i<9;i++) ctx.history[i]=ctx.history[i+1]; ctx.history[9]=val; }
    char buf[64] = "History: ";
    for (int i=0;i<ctx.hist_len;i++) { char tmp[4]; lv_snprintf(tmp,4,"%d ",ctx.history[i]); lv_strncat(buf,tmp,sizeof(buf)-strlen(buf)-1); }
    lv_label_set_text(ctx.lbl_history, buf);
}

static bool dice_init(lv_obj_t *parent) {

    ctx.hist_len = 0; ctx.seed = 42;
    lv_obj_t *btn = lv_btn_create(parent);
    lv_obj_align(btn, LV_ALIGN_CENTER, 0, -40);
    lv_obj_set_size(btn, 140, 56);
    lv_obj_t *lbl = lv_label_create(btn);
    lv_label_set_text(lbl, "Roll D6");
    lv_obj_add_event_cb(btn, dice_roll_cb, LV_EVENT_CLICKED, NULL);
    ctx.lbl_result = lv_label_create(parent);
    lv_obj_align(ctx.lbl_result, LV_ALIGN_CENTER, 0, 30);
    lv_obj_set_style_text_font(ctx.lbl_result, &lv_font_montserrat_48, 0);
    lv_label_set_text(ctx.lbl_result, "-");
    ctx.lbl_history = lv_label_create(parent);
    lv_obj_align(ctx.lbl_history, LV_ALIGN_CENTER, 0, 90);
    lv_label_set_text(ctx.lbl_history, "History: —");
    return true;

}
static void dice_deinit(void) {
    if (ctx.timer) { lv_timer_del(ctx.timer); ctx.timer = NULL; }
}
static void dice_on_show(void) { }
static void dice_on_hide(void) { }
const eapps_app_info_t dice_info = {
    .id = "dice", .name = "Dice Roller", .icon = "dic",
    .description = "Multi-dice roller with history", .category = EAPPS_CAT_GAMES, .version = "2.0.0",
};
const eapps_app_lifecycle_t dice_lifecycle = {
    .init = dice_init, .deinit = dice_deinit,
    .on_show = dice_on_show, .on_hide = dice_on_hide,
};
