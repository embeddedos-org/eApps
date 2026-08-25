// SPDX-License-Identifier: MIT
// Minesweeper — EoS LVGL Application
#include "minesweeper.h"
#include <stdbool.h>
#include <string.h>

#define MS_W 9
#define MS_H 9
#define MS_MINES 10
typedef struct {
    uint8_t board[MS_H][MS_W]; /* bit0=mine bit1=revealed bit2=flagged */
    int revealed, flags;
    lv_obj_t *btns[MS_H][MS_W];
    lv_obj_t *lbl_status;
    bool game_over;
    lv_timer_t *timer;
} ms_ctx_t;
static ms_ctx_t ctx;


static bool minesweeper_init(lv_obj_t *parent) {

    memset(&ctx, 0, sizeof(ctx));
    /* place mines */
    int placed = 0;
    uint32_t seed = 12345;
    while (placed < MS_MINES) {
        seed = seed * 1103515245 + 12345;
        int r = (seed >> 16) % MS_H;
        seed = seed * 1103515245 + 12345;
        int c = (seed >> 16) % MS_W;
        if (!(ctx.board[r][c] & 1)) { ctx.board[r][c] |= 1; placed++; }
    }
    lv_obj_t *grid = lv_obj_create(parent);
    lv_obj_set_size(grid, MS_W * 32 + 8, MS_H * 32 + 8);
    lv_obj_align(grid, LV_ALIGN_CENTER, 0, 20);
    lv_obj_set_layout(grid, LV_LAYOUT_GRID);
    for (int r = 0; r < MS_H; r++) for (int c = 0; c < MS_W; c++) {
        ctx.btns[r][c] = lv_btn_create(grid);
        lv_obj_set_size(ctx.btns[r][c], 28, 28);
    }
    ctx.lbl_status = lv_label_create(parent);
    lv_obj_align(ctx.lbl_status, LV_ALIGN_TOP_MID, 0, 8);
    lv_label_set_text(ctx.lbl_status, "Minesweeper — Click to reveal");
    return true;

}
static void minesweeper_deinit(void) {
    if (ctx.timer) { lv_timer_del(ctx.timer); ctx.timer = NULL; }
}
static void minesweeper_on_show(void) { }
static void minesweeper_on_hide(void) { }
const eapps_app_info_t minesweeper_info = {
    .id = "minesweeper", .name = "Minesweeper", .icon = "msw",
    .description = "Classic minesweeper", .category = EAPPS_CAT_GAMES, .version = "2.0.0",
};
const eapps_app_lifecycle_t minesweeper_lifecycle = {
    .init = minesweeper_init, .deinit = minesweeper_deinit,
    .on_show = minesweeper_on_show, .on_hide = minesweeper_on_hide,
};
