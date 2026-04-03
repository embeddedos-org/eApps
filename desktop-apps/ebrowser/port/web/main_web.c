// SPDX-License-Identifier: MIT
#include "lvgl.h"
#include "eBrowser/browser.h"

#ifdef eBrowser_PLATFORM_WEB
#include <emscripten.h>

static eb_browser_t s_browser;

static void main_loop(void) {
    lv_timer_handler();
}

int main(void) {
    lv_init();

    lv_obj_t *scr = lv_screen_active();
    eb_browser_init(&s_browser, scr);
    eb_browser_home(&s_browser);

    emscripten_set_main_loop(main_loop, 0, 1);

    eb_browser_deinit(&s_browser);
    lv_deinit();
    return 0;
}
#endif
