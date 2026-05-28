// SPDX-License-Identifier: MIT
// eNote — EoS LVGL Application
#include "enote.h"
#include <stdbool.h>
#include <string.h>

typedef struct {
    lv_obj_t *textarea;
    lv_obj_t *lbl_preview;
    lv_obj_t *lbl_wordcount;
    lv_timer_t *timer;
} enote_ctx_t;
static enote_ctx_t ctx;


static void enote_text_changed_cb(lv_event_t *e) {
    (void)e;
    const char *txt = lv_textarea_get_text(ctx.textarea);
    int words = 0; bool in_word = false;
    for (int i = 0; txt[i]; i++) {
        if (txt[i] == ' ' || txt[i] == '\n') in_word = false;
        else if (!in_word) { in_word = true; words++; }
    }
    lv_label_set_text_fmt(ctx.lbl_wordcount, "Words: %d", words);
}

static bool enote_init(lv_obj_t *parent) {

    ctx.textarea = lv_textarea_create(parent);
    lv_obj_set_size(ctx.textarea, 280, 180);
    lv_obj_align(ctx.textarea, LV_ALIGN_TOP_MID, 0, 8);
    lv_textarea_set_placeholder_text(ctx.textarea, "Start typing your note...");
    lv_obj_add_event_cb(ctx.textarea, enote_text_changed_cb, LV_EVENT_VALUE_CHANGED, NULL);
    ctx.lbl_wordcount = lv_label_create(parent);
    lv_obj_align(ctx.lbl_wordcount, LV_ALIGN_BOTTOM_LEFT, 8, -8);
    lv_label_set_text(ctx.lbl_wordcount, "Words: 0");
    ctx.lbl_preview = lv_label_create(parent);
    lv_obj_align(ctx.lbl_preview, LV_ALIGN_BOTTOM_RIGHT, -8, -8);
    lv_label_set_text(ctx.lbl_preview, "");
    return true;

}
static void enote_deinit(void) {
    if (ctx.timer) { lv_timer_del(ctx.timer); ctx.timer = NULL; }
}
static void enote_on_show(void) { }
static void enote_on_hide(void) { }
const eapps_app_info_t enote_info = {
    .id = "enote", .name = "eNote", .icon = "not",
    .description = "Note-taking with markdown preview", .category = EAPPS_CAT_PRODUCTIVITY, .version = "2.0.0",
};
const eapps_app_lifecycle_t enote_lifecycle = {
    .init = enote_init, .deinit = enote_deinit,
    .on_show = enote_on_show, .on_hide = enote_on_hide,
};
