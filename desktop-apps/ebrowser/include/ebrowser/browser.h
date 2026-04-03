// SPDX-License-Identifier: MIT
#ifndef eBrowser_BROWSER_H
#define eBrowser_BROWSER_H

#include "lvgl.h"
#include <stdbool.h>

#define EB_BROWSER_MAX_TABS    8
#define EB_BROWSER_MAX_HISTORY 64
#define EB_BROWSER_MAX_URL     2048

typedef struct {
    char    url[EB_BROWSER_MAX_URL];
    char    title[256];
    bool    loading;
    int     scroll_y;
} eb_tab_t;

typedef struct {
    lv_obj_t   *root;
    lv_obj_t   *toolbar;
    lv_obj_t   *back_btn;
    lv_obj_t   *forward_btn;
    lv_obj_t   *reload_btn;
    lv_obj_t   *home_btn;
    lv_obj_t   *url_bar;
    lv_obj_t   *tab_bar;
    lv_obj_t   *page_area;
    lv_obj_t   *status_bar;
    lv_obj_t   *status_label;
    eb_tab_t    tabs[EB_BROWSER_MAX_TABS];
    int         tab_count;
    int         active_tab;
    char        history[EB_BROWSER_MAX_HISTORY][EB_BROWSER_MAX_URL];
    int         history_count;
    int         history_pos;
} eb_browser_t;

bool eb_browser_init(eb_browser_t *browser, lv_obj_t *parent);
void eb_browser_deinit(eb_browser_t *browser);
void eb_browser_navigate(eb_browser_t *browser, const char *url);
void eb_browser_back(eb_browser_t *browser);
void eb_browser_forward(eb_browser_t *browser);
void eb_browser_reload(eb_browser_t *browser);
void eb_browser_home(eb_browser_t *browser);
int  eb_browser_new_tab(eb_browser_t *browser);
void eb_browser_close_tab(eb_browser_t *browser, int index);
void eb_browser_switch_tab(eb_browser_t *browser, int index);
void eb_browser_set_status(eb_browser_t *browser, const char *text);

#endif /* eBrowser_BROWSER_H */
