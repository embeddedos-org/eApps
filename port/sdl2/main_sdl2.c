// SPDX-License-Identifier: MIT
#include "eapps/platform.h"
#include "eapps/theme.h"
#include "eapps/registry.h"
#include <stdio.h>

int main(int argc, char **argv) {
    (void)argc; (void)argv;

    eapps_theme_init(false);
    eapps_registry_init();

    printf("eApps Suite (SDL2 Desktop)\n");
    printf("LVGL + SDL2 main loop — placeholder\n");

    /* TODO: SDL_Init → lv_init → lv_port_disp_sdl2_init → lv_port_indev_sdl2_init
     *       → suite_init → main loop (lv_timer_handler + SDL_Delay) */

    eapps_registry_deinit();
    return 0;
}
