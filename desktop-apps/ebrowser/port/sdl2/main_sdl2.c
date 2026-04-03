// SPDX-License-Identifier: MIT
// eBrowser SDL2 Desktop Entry Point — real GUI window with LVGL rendering
#include "lvgl.h"
#include "eBrowser/browser.h"
#include <stdio.h>
#include <stdlib.h>
#include <SDL2/SDL.h>

#define WINDOW_WIDTH  800
#define WINDOW_HEIGHT 480

static SDL_Window   *s_window   = NULL;
static SDL_Renderer *s_renderer = NULL;
static SDL_Texture  *s_texture  = NULL;
static lv_display_t *s_display  = NULL;
static lv_indev_t   *s_mouse    = NULL;
static eb_browser_t  s_browser;
static volatile int   s_running = 1;

static uint8_t s_fb[WINDOW_WIDTH * WINDOW_HEIGHT * 4];
static int     s_mouse_pressed = 0;
static int     s_mouse_x = 0, s_mouse_y = 0;

static void flush_cb(lv_display_t *disp, const lv_area_t *area, uint8_t *px_map) {
    int32_t w = area->x2 - area->x1 + 1;
    int32_t h = area->y2 - area->y1 + 1;
    int32_t x, y;

    for (y = 0; y < h; y++) {
        for (x = 0; x < w; x++) {
            int src_idx = (y * w + x) * 2;
            uint16_t pixel = (uint16_t)((uint16_t)px_map[src_idx] | ((uint16_t)px_map[src_idx + 1] << 8));
            uint8_t r = (uint8_t)(((pixel >> 11) & 0x1F) << 3);
            uint8_t g = (uint8_t)(((pixel >> 5) & 0x3F) << 2);
            uint8_t b = (uint8_t)((pixel & 0x1F) << 3);

            int dst_idx = ((area->y1 + y) * WINDOW_WIDTH + (area->x1 + x)) * 4;
            s_fb[dst_idx + 0] = b;
            s_fb[dst_idx + 1] = g;
            s_fb[dst_idx + 2] = r;
            s_fb[dst_idx + 3] = 255;
        }
    }

    lv_display_flush_ready(disp);
}

static void mouse_read_cb(lv_indev_t *indev, lv_indev_data_t *data) {
    (void)indev;
    data->point.x = s_mouse_x;
    data->point.y = s_mouse_y;
    data->state = s_mouse_pressed ? LV_INDEV_STATE_PRESSED : LV_INDEV_STATE_RELEASED;
}

static uint32_t tick_cb(void) {
    return SDL_GetTicks();
}

int main(int argc, char *argv[]) {
    (void)argc; (void)argv;

    printf("[eBrowser] Starting eBrowser v0.1.0...\n");

    if (SDL_Init(SDL_INIT_VIDEO) != 0) {
        fprintf(stderr, "[eBrowser] SDL_Init failed: %s\n", SDL_GetError());
        return 1;
    }

    s_window = SDL_CreateWindow("eBrowser",
        SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
        WINDOW_WIDTH, WINDOW_HEIGHT, SDL_WINDOW_SHOWN);
    if (!s_window) {
        fprintf(stderr, "[eBrowser] SDL_CreateWindow failed: %s\n", SDL_GetError());
        SDL_Quit();
        return 1;
    }

    s_renderer = SDL_CreateRenderer(s_window, -1, SDL_RENDERER_ACCELERATED | SDL_RENDERER_PRESENTVSYNC);
    if (!s_renderer) {
        s_renderer = SDL_CreateRenderer(s_window, -1, SDL_RENDERER_SOFTWARE);
    }
    if (!s_renderer) {
        fprintf(stderr, "[eBrowser] SDL_CreateRenderer failed: %s\n", SDL_GetError());
        SDL_DestroyWindow(s_window);
        SDL_Quit();
        return 1;
    }

    s_texture = SDL_CreateTexture(s_renderer,
        SDL_PIXELFORMAT_ARGB8888, SDL_TEXTUREACCESS_STREAMING,
        WINDOW_WIDTH, WINDOW_HEIGHT);

    printf("[eBrowser] Initializing LVGL...\n");
    lv_init();
    lv_tick_set_cb(tick_cb);

    s_display = lv_display_create(WINDOW_WIDTH, WINDOW_HEIGHT);
    static uint8_t buf1[WINDOW_WIDTH * 10 * 2];
    lv_display_set_buffers(s_display, buf1, NULL, sizeof(buf1), LV_DISPLAY_RENDER_MODE_PARTIAL);
    lv_display_set_flush_cb(s_display, flush_cb);

    s_mouse = lv_indev_create();
    lv_indev_set_type(s_mouse, LV_INDEV_TYPE_POINTER);
    lv_indev_set_read_cb(s_mouse, mouse_read_cb);

    printf("[eBrowser] Creating browser UI...\n");
    lv_obj_t *scr = lv_screen_active();
    eb_browser_init(&s_browser, scr);

    if (argc > 1) {
        printf("[eBrowser] Navigating to %s\n", argv[1]);
        eb_browser_navigate(&s_browser, argv[1]);
    }

    printf("[eBrowser] Browser ready — 800x480 window\n");

    while (s_running) {
        SDL_Event ev;
        while (SDL_PollEvent(&ev)) {
            switch (ev.type) {
                case SDL_QUIT:
                    s_running = 0;
                    break;
                case SDL_MOUSEMOTION:
                    s_mouse_x = ev.motion.x;
                    s_mouse_y = ev.motion.y;
                    break;
                case SDL_MOUSEBUTTONDOWN:
                    s_mouse_pressed = 1;
                    s_mouse_x = ev.button.x;
                    s_mouse_y = ev.button.y;
                    break;
                case SDL_MOUSEBUTTONUP:
                    s_mouse_pressed = 0;
                    break;
                default:
                    break;
            }
        }

        lv_timer_handler();

        SDL_UpdateTexture(s_texture, NULL, s_fb, WINDOW_WIDTH * 4);
        SDL_RenderClear(s_renderer);
        SDL_RenderCopy(s_renderer, s_texture, NULL, NULL);
        SDL_RenderPresent(s_renderer);

        SDL_Delay(5);
    }

    printf("[eBrowser] Shutting down...\n");
    eb_browser_deinit(&s_browser);
    lv_deinit();

    SDL_DestroyTexture(s_texture);
    SDL_DestroyRenderer(s_renderer);
    SDL_DestroyWindow(s_window);
    SDL_Quit();

    return 0;
}
