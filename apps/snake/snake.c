// SPDX-License-Identifier: MIT
#include "snake.h"
#include <stdbool.h>
static bool snake_init(lv_obj_t *parent) { (void)parent; return true; }
static void snake_deinit(void) { }
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