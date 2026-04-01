// SPDX-License-Identifier: MIT
// Copyright (c) 2026 EoS Project

/**
 * @file main_sdl2.c
 * @brief SDL2 simulator main entry point — initializes SDL2 backend, LVGL,
 *        display/input ports, and runs the eApps suite main loop.
 */

#include "lvgl.h"
#include <eos/hal_extended.h>
#include <SDL2/SDL.h>
#include <stdio.h>

extern void lv_port_disp_sdl2_init(void);
extern void lv_port_disp_sdl2_deinit(void);
extern void lv_port_indev_sdl2_init(void);
extern void lv_port_indev_sdl2_deinit(void);

extern int eos_backend_sdl2_register(void);

extern void eapps_suite_init(void);

static volatile bool s_running = true;

int main(int argc, char *argv[])
{
    (void)argc; (void)argv;

    printf("[SDL2] Registering SDL2 backend...\n");
    if (eos_backend_sdl2_register() != 0) {
        fprintf(stderr, "[SDL2] Failed to register SDL2 backend\n");
        return 1;
    }

    printf("[SDL2] Initializing LVGL...\n");
    lv_init();

    printf("[SDL2] Initializing display port (800x480)...\n");
    lv_port_disp_sdl2_init();

    printf("[SDL2] Initializing input port...\n");
    lv_port_indev_sdl2_init();

    printf("[SDL2] Starting eApps suite...\n");
    eapps_suite_init();

    printf("[SDL2] Entering main loop...\n");
    while (s_running) {
        uint32_t time_till_next = lv_timer_handler();

        SDL_Event ev;
        while (SDL_PollEvent(&ev)) {
            if (ev.type == SDL_QUIT) {
                s_running = false;
            }
        }

        SDL_Delay(time_till_next > 0 ? time_till_next : 5);
    }

    printf("[SDL2] Shutting down...\n");
    lv_port_indev_sdl2_deinit();
    lv_port_disp_sdl2_deinit();
    lv_deinit();
    SDL_Quit();

    return 0;
}
