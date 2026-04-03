// SPDX-License-Identifier: MIT
#include "lvgl.h"
#include "eBrowser/browser.h"

static eb_browser_t s_browser;

void eBrowser_eos_main(void) {
    lv_init();

    lv_obj_t *scr = lv_screen_active();
    eb_browser_init(&s_browser, scr);
    eb_browser_home(&s_browser);
}

void eBrowser_eos_tick(void) {
    lv_timer_handler();
}

void eBrowser_eos_deinit(void) {
    eb_browser_deinit(&s_browser);
    lv_deinit();
}
