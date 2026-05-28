// SPDX-License-Identifier: MIT
// eCalendar — EoS LVGL Application
#include "ecal.h"
#include <stdbool.h>
#include <string.h>

typedef struct {
    int year, month, day;
    lv_obj_t *lbl_header;
    lv_obj_t *day_btns[42];
    lv_obj_t *lbl_events;
    lv_timer_t *timer;
} ecal_ctx_t;
static ecal_ctx_t ctx;
static const char *MONTHS[] = {"Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"};
static const int DAYS_IN_MONTH[] = {31,28,31,30,31,30,31,31,30,31,30,31};


static bool ecal_init(lv_obj_t *parent) {

    ctx.year = 2025; ctx.month = 5; ctx.day = 28;
    ctx.lbl_header = lv_label_create(parent);
    lv_obj_align(ctx.lbl_header, LV_ALIGN_TOP_MID, 0, 8);
    lv_label_set_text_fmt(ctx.lbl_header, "%s %d", MONTHS[ctx.month-1], ctx.year);
    lv_obj_t *grid = lv_obj_create(parent);
    lv_obj_set_size(grid, 280, 200);
    lv_obj_align(grid, LV_ALIGN_CENTER, 0, 0);
    lv_obj_set_layout(grid, LV_LAYOUT_GRID);
    for (int i = 0; i < 42; i++) {
        ctx.day_btns[i] = lv_btn_create(grid);
        lv_obj_set_size(ctx.day_btns[i], 36, 28);
        lv_obj_t *l = lv_label_create(ctx.day_btns[i]);
        int d = i - 2; /* May 2025 starts on Thu=4, offset 4 */
        if (d >= 1 && d <= 31) lv_label_set_text_fmt(l, "%d", d);
        else lv_label_set_text(l, "");
    }
    ctx.lbl_events = lv_label_create(parent);
    lv_obj_align(ctx.lbl_events, LV_ALIGN_BOTTOM_MID, 0, -8);
    lv_label_set_text(ctx.lbl_events, "No events today");
    return true;

}
static void ecal_deinit(void) {
    if (ctx.timer) { lv_timer_del(ctx.timer); ctx.timer = NULL; }
}
static void ecal_on_show(void) { }
static void ecal_on_hide(void) { }
const eapps_app_info_t ecal_info = {
    .id = "ecal", .name = "eCalendar", .icon = "cal",
    .description = "Calendar and event planner", .category = EAPPS_CAT_PRODUCTIVITY, .version = "2.0.0",
};
const eapps_app_lifecycle_t ecal_lifecycle = {
    .init = ecal_init, .deinit = ecal_deinit,
    .on_show = ecal_on_show, .on_hide = ecal_on_hide,
};
