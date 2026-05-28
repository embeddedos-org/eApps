// SPDX-License-Identifier: MIT
// Snake — EoS LVGL Application
#include "snake.h"
#include <stdbool.h>
#include <string.h>

#define GRID_W 20
#define GRID_H 15
#define CELL_SZ 16
typedef struct { int x, y; } pt_t;
typedef struct {
    lv_obj_t *canvas;
    pt_t body[GRID_W * GRID_H];
    int len;
    pt_t dir;
    pt_t food;
    lv_timer_t *timer;
    int score;
    lv_obj_t *label_score;
    bool running;
} snake_ctx_t;
static snake_ctx_t ctx;


static void snake_tick(lv_timer_t *t) {
    (void)t;
    if (!ctx.running) return;
    pt_t head = {ctx.body[0].x + ctx.dir.x, ctx.body[0].y + ctx.dir.y};
    if (head.x < 0 || head.x >= GRID_W || head.y < 0 || head.y >= GRID_H) {
        ctx.running = false; return;
    }
    for (int i = 0; i < ctx.len; i++) {
        if (ctx.body[i].x == head.x && ctx.body[i].y == head.y) { ctx.running = false; return; }
    }
    bool ate = (head.x == ctx.food.x && head.y == ctx.food.y);
    if (!ate) ctx.len--;
    for (int i = ctx.len; i > 0; i--) ctx.body[i] = ctx.body[i-1];
    ctx.body[0] = head;
    if (ate) { ctx.score += 10; ctx.food.x = (ctx.food.x * 7 + 3) % GRID_W; ctx.food.y = (ctx.food.y * 5 + 2) % GRID_H; }
    lv_label_set_text_fmt(ctx.label_score, "Score: %d", ctx.score);
}

static bool snake_init(lv_obj_t *parent) {

    ctx.len = 3; ctx.score = 0; ctx.running = true;
    ctx.body[0] = (pt_t){10,7}; ctx.body[1] = (pt_t){9,7}; ctx.body[2] = (pt_t){8,7};
    ctx.dir = (pt_t){1,0}; ctx.food = (pt_t){15,7};
    ctx.canvas = lv_canvas_create(parent);
    lv_obj_set_size(ctx.canvas, GRID_W * CELL_SZ, GRID_H * CELL_SZ);
    lv_obj_align(ctx.canvas, LV_ALIGN_CENTER, 0, 20);
    ctx.label_score = lv_label_create(parent);
    lv_obj_align(ctx.label_score, LV_ALIGN_TOP_MID, 0, 8);
    lv_label_set_text(ctx.label_score, "Score: 0");
    ctx.timer = lv_timer_create(snake_tick, 150, NULL);
    return true;

}
static void snake_deinit(void) {
    if (ctx.timer) { lv_timer_del(ctx.timer); ctx.timer = NULL; }
}
static void snake_on_show(void) { }
static void snake_on_hide(void) { }
const eapps_app_info_t snake_info = {
    .id = "snake", .name = "Snake", .icon = "snk",
    .description = "Classic snake game", .category = EAPPS_CAT_GAMES, .version = "2.0.0",
};
const eapps_app_lifecycle_t snake_lifecycle = {
    .init = snake_init, .deinit = snake_deinit,
    .on_show = snake_on_show, .on_hide = snake_on_hide,
};
