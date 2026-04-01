// SPDX-License-Identifier: MIT
// SDL2 display driver — creates window and renders LVGL framebuffer

#include <stdint.h>
#include <stdbool.h>

#define EAPPS_SDL2_HOR_RES 800
#define EAPPS_SDL2_VER_RES 480

void lv_port_disp_sdl2_init(void);
