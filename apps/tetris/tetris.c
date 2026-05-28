// SPDX-License-Identifier: MIT
// Tetris — EoS LVGL Application
#include "tetris.h"
#include <stdbool.h>
#include <string.h>

#define TET_W 10
#define TET_H 20
#define TET_CELL 16
typedef struct {
    uint8_t board[TET_H][TET_W];
    int score, lines, level;
    int px, py, piece, rot;
    lv_timer_t *timer;
    lv_obj_t *canvas;
    lv_obj_t *lbl_score;
    bool running;
} tetris_ctx_t;
static tetris_ctx_t ctx;
static const uint8_t PIECES[7][4][4] = {
    {{1,1,1,1},{0,0,0,0},{0,0,0,0},{0,0,0,0}}, /* I */
    {{1,1},{1,1},{0,0},{0,0}},                   /* O */
    {{0,1,0},{1,1,1},{0,0,0},{0,0,0}},           /* T */
    {{0,1,1},{1,1,0},{0,0,0},{0,0,0}},           /* S */
    {{1,1,0},{0,1,1},{0,0,0},{0,0,0}},           /* Z */
    {{1,0,0},{1,1,1},{0,0,0},{0,0,0}},           /* J */
    {{0,0,1},{1,1,1},{0,0,0},{0,0,0}},           /* L */
};


static void tetris_tick(lv_timer_t *t) {
    (void)t;
    if (!ctx.running) return;
    ctx.py++;
    /* simple gravity — no full collision for brevity */
    if (ctx.py >= TET_H - 1) {
        ctx.py = 0; ctx.px = 4;
        ctx.piece = (ctx.piece + 1) % 7;
        ctx.score += 10;
    }
    lv_label_set_text_fmt(ctx.lbl_score, "Score:\n%d\nLines:\n%d", ctx.score, ctx.lines);
}

static bool tetris_init(lv_obj_t *parent) {

    memset(&ctx, 0, sizeof(ctx));
    ctx.running = true; ctx.level = 1;
    ctx.px = 4; ctx.py = 0; ctx.piece = 0;
    ctx.canvas = lv_canvas_create(parent);
    lv_obj_set_size(ctx.canvas, TET_W * TET_CELL, TET_H * TET_CELL);
    lv_obj_align(ctx.canvas, LV_ALIGN_CENTER, -40, 0);
    ctx.lbl_score = lv_label_create(parent);
    lv_obj_align(ctx.lbl_score, LV_ALIGN_CENTER, 60, -40);
    lv_label_set_text(ctx.lbl_score, "Score:\n0\nLines:\n0");
    ctx.timer = lv_timer_create(tetris_tick, 500, NULL);
    return true;

}
static void tetris_deinit(void) {
    if (ctx.timer) { lv_timer_del(ctx.timer); ctx.timer = NULL; }
}
static void tetris_on_show(void) { }
static void tetris_on_hide(void) { }
const eapps_app_info_t tetris_info = {
    .id = "tetris", .name = "Tetris", .icon = "ttr",
    .description = "Classic Tetris block game", .category = EAPPS_CAT_GAMES, .version = "2.0.0",
};
const eapps_app_lifecycle_t tetris_lifecycle = {
    .init = tetris_init, .deinit = tetris_deinit,
    .on_show = tetris_on_show, .on_hide = tetris_on_hide,
};
