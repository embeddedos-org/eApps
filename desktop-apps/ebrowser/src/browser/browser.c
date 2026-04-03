// SPDX-License-Identifier: MIT
#include "eBrowser/browser.h"
#include "eBrowser/html_parser.h"
#include "eBrowser/css_parser.h"
#include "eBrowser/layout.h"
#include "eBrowser/render.h"
#include "eBrowser/http.h"
#include "eBrowser/url.h"
#include <string.h>
#include <stdio.h>

#define EB_HOME_URL    "about:home"
#define EB_DEFAULT_URL "https://example.com"

static const char *s_home_html =
    "<!DOCTYPE html>"
    "<html><head><title>eBrowser Home</title></head>"
    "<body style=\"background-color:#f0f4f8;margin:0;padding:40px;\">"
    "<div style=\"text-align:center;\">"
    "<h1 style=\"color:#2563eb;\">eBrowser</h1>"
    "<p style=\"color:#64748b;\">A lightweight web browser for embedded and IoT devices</p>"
    "<hr>"
    "<p style=\"font-size:14px;color:#94a3b8;\">Enter a URL in the address bar to get started</p>"
    "</div>"
    "</body></html>";

static void url_bar_event_cb(lv_event_t *e) {
    eb_browser_t *browser = (eb_browser_t *)lv_event_get_user_data(e);
    if (!browser) return;
    const char *url = lv_textarea_get_text(browser->url_bar);
    if (url && url[0]) eb_browser_navigate(browser, url);
}

static void back_btn_cb(lv_event_t *e) {
    eb_browser_t *b = (eb_browser_t *)lv_event_get_user_data(e);
    if (b) eb_browser_back(b);
}

static void forward_btn_cb(lv_event_t *e) {
    eb_browser_t *b = (eb_browser_t *)lv_event_get_user_data(e);
    if (b) eb_browser_forward(b);
}

static void reload_btn_cb(lv_event_t *e) {
    eb_browser_t *b = (eb_browser_t *)lv_event_get_user_data(e);
    if (b) eb_browser_reload(b);
}

static void home_btn_cb(lv_event_t *e) {
    eb_browser_t *b = (eb_browser_t *)lv_event_get_user_data(e);
    if (b) eb_browser_home(b);
}

static lv_obj_t *create_nav_button(lv_obj_t *parent, const char *symbol, lv_event_cb_t cb, void *user_data) {
    lv_obj_t *btn = lv_button_create(parent);
    lv_obj_set_size(btn, 36, 36);
    lv_obj_set_style_radius(btn, 4, LV_PART_MAIN);
    lv_obj_set_style_bg_color(btn, lv_color_make(229, 231, 235), LV_PART_MAIN);
    lv_obj_set_style_bg_opa(btn, LV_OPA_COVER, LV_PART_MAIN);
    lv_obj_add_event_cb(btn, cb, LV_EVENT_CLICKED, user_data);
    lv_obj_t *lbl = lv_label_create(btn);
    lv_label_set_text(lbl, symbol);
    lv_obj_center(lbl);
    return btn;
}

bool eb_browser_init(eb_browser_t *browser, lv_obj_t *parent) {
    if (!browser || !parent) return false;
    memset(browser, 0, sizeof(eb_browser_t));

    browser->root = lv_obj_create(parent);
    lv_obj_set_size(browser->root, LV_PCT(100), LV_PCT(100));
    lv_obj_set_flex_flow(browser->root, LV_FLEX_FLOW_COLUMN);
    lv_obj_set_style_pad_all(browser->root, 0, LV_PART_MAIN);
    lv_obj_set_style_pad_gap(browser->root, 0, LV_PART_MAIN);
    lv_obj_set_style_bg_color(browser->root, lv_color_make(255, 255, 255), LV_PART_MAIN);
    lv_obj_set_style_bg_opa(browser->root, LV_OPA_COVER, LV_PART_MAIN);

    browser->toolbar = lv_obj_create(browser->root);
    lv_obj_set_size(browser->toolbar, LV_PCT(100), 48);
    lv_obj_set_flex_flow(browser->toolbar, LV_FLEX_FLOW_ROW);
    lv_obj_set_flex_align(browser->toolbar, LV_FLEX_ALIGN_START, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER);
    lv_obj_set_style_pad_all(browser->toolbar, 4, LV_PART_MAIN);
    lv_obj_set_style_pad_gap(browser->toolbar, 4, LV_PART_MAIN);
    lv_obj_set_style_bg_color(browser->toolbar, lv_color_make(243, 244, 246), LV_PART_MAIN);
    lv_obj_set_style_bg_opa(browser->toolbar, LV_OPA_COVER, LV_PART_MAIN);
    lv_obj_set_style_border_width(browser->toolbar, 1, LV_PART_MAIN);
    lv_obj_set_style_border_side(browser->toolbar, LV_BORDER_SIDE_BOTTOM, LV_PART_MAIN);
    lv_obj_set_style_border_color(browser->toolbar, lv_color_make(209, 213, 219), LV_PART_MAIN);

    browser->back_btn    = create_nav_button(browser->toolbar, LV_SYMBOL_LEFT,    back_btn_cb,    browser);
    browser->forward_btn = create_nav_button(browser->toolbar, LV_SYMBOL_RIGHT,   forward_btn_cb, browser);
    browser->reload_btn  = create_nav_button(browser->toolbar, LV_SYMBOL_REFRESH, reload_btn_cb,  browser);
    browser->home_btn    = create_nav_button(browser->toolbar, LV_SYMBOL_HOME,    home_btn_cb,    browser);

    browser->url_bar = lv_textarea_create(browser->toolbar);
    lv_textarea_set_one_line(browser->url_bar, true);
    lv_textarea_set_placeholder_text(browser->url_bar, "Enter URL...");
    lv_obj_set_flex_grow(browser->url_bar, 1);
    lv_obj_set_height(browser->url_bar, 36);
    lv_obj_set_style_radius(browser->url_bar, 18, LV_PART_MAIN);
    lv_obj_set_style_bg_color(browser->url_bar, lv_color_white(), LV_PART_MAIN);
    lv_obj_set_style_border_width(browser->url_bar, 1, LV_PART_MAIN);
    lv_obj_set_style_border_color(browser->url_bar, lv_color_make(209, 213, 219), LV_PART_MAIN);
    lv_obj_add_event_cb(browser->url_bar, url_bar_event_cb, LV_EVENT_READY, browser);

    browser->tab_bar = lv_obj_create(browser->root);
    lv_obj_set_size(browser->tab_bar, LV_PCT(100), 32);
    lv_obj_set_flex_flow(browser->tab_bar, LV_FLEX_FLOW_ROW);
    lv_obj_set_style_pad_all(browser->tab_bar, 2, LV_PART_MAIN);
    lv_obj_set_style_pad_gap(browser->tab_bar, 2, LV_PART_MAIN);
    lv_obj_set_style_bg_color(browser->tab_bar, lv_color_make(249, 250, 251), LV_PART_MAIN);
    lv_obj_set_style_bg_opa(browser->tab_bar, LV_OPA_COVER, LV_PART_MAIN);
    lv_obj_set_style_border_width(browser->tab_bar, 1, LV_PART_MAIN);
    lv_obj_set_style_border_side(browser->tab_bar, LV_BORDER_SIDE_BOTTOM, LV_PART_MAIN);
    lv_obj_set_style_border_color(browser->tab_bar, lv_color_make(229, 231, 235), LV_PART_MAIN);

    browser->page_area = lv_obj_create(browser->root);
    lv_obj_set_size(browser->page_area, LV_PCT(100), LV_SIZE_CONTENT);
    lv_obj_set_flex_grow(browser->page_area, 1);
    lv_obj_set_style_pad_all(browser->page_area, 0, LV_PART_MAIN);
    lv_obj_set_style_bg_color(browser->page_area, lv_color_white(), LV_PART_MAIN);
    lv_obj_set_style_bg_opa(browser->page_area, LV_OPA_COVER, LV_PART_MAIN);

    browser->status_bar = lv_obj_create(browser->root);
    lv_obj_set_size(browser->status_bar, LV_PCT(100), 24);
    lv_obj_set_style_pad_hor(browser->status_bar, 8, LV_PART_MAIN);
    lv_obj_set_style_bg_color(browser->status_bar, lv_color_make(243, 244, 246), LV_PART_MAIN);
    lv_obj_set_style_bg_opa(browser->status_bar, LV_OPA_COVER, LV_PART_MAIN);
    lv_obj_set_style_border_width(browser->status_bar, 1, LV_PART_MAIN);
    lv_obj_set_style_border_side(browser->status_bar, LV_BORDER_SIDE_TOP, LV_PART_MAIN);
    lv_obj_set_style_border_color(browser->status_bar, lv_color_make(229, 231, 235), LV_PART_MAIN);

    browser->status_label = lv_label_create(browser->status_bar);
    lv_label_set_text(browser->status_label, "Ready");
    lv_obj_set_style_text_font(browser->status_label, &lv_font_montserrat_12, LV_PART_MAIN);
    lv_obj_set_style_text_color(browser->status_label, lv_color_make(107, 114, 128), LV_PART_MAIN);
    lv_obj_align(browser->status_label, LV_ALIGN_LEFT_MID, 0, 0);

    eb_browser_new_tab(browser);
    eb_browser_home(browser);

    return true;
}

void eb_browser_deinit(eb_browser_t *browser) {
    if (!browser) return;
    if (browser->root) lv_obj_delete(browser->root);
    memset(browser, 0, sizeof(eb_browser_t));
}

static void render_html(eb_browser_t *browser, const char *html, size_t len) {
    if (!browser || !html || len == 0) return;

    lv_obj_clean(browser->page_area);

    eb_dom_node_t *dom = eb_html_parse(html, len);
    if (!dom) {
        eb_browser_set_status(browser, "Error: Failed to parse HTML");
        return;
    }

    eb_stylesheet_t ss;
    eb_css_init_stylesheet(&ss);

    eb_dom_node_t *style_node = eb_dom_find_by_tag(dom, "style");
    if (style_node && style_node->child_count > 0 &&
        style_node->children[0]->type == EB_NODE_TEXT) {
        eb_css_parse(&ss, style_node->children[0]->text, strlen(style_node->children[0]->text));
    }

    eb_layout_context_t layout_ctx;
    int page_w = 780;
    int page_h = 400;
    eb_layout_init(&layout_ctx, page_w, page_h);

    eb_dom_node_t *body = eb_dom_find_by_tag(dom, "body");
    if (!body) body = dom;

    eb_layout_box_t *root_box = eb_layout_build(&layout_ctx, body, &ss);
    if (root_box) {
        eb_layout_compute(&layout_ctx, root_box);

        eb_render_target_t rt;
        eb_render_init(&rt, browser->page_area, page_w, page_h);
        eb_color_t bg = {255, 255, 255, 255};
        eb_render_clear(&rt, bg);
        eb_render_paint(&rt, root_box);
    }

    eb_dom_node_t *title_node = eb_dom_find_by_tag(dom, "title");
    if (title_node && title_node->child_count > 0 &&
        title_node->children[0]->type == EB_NODE_TEXT) {
        strncpy(browser->tabs[browser->active_tab].title,
                title_node->children[0]->text, 255);
    }

    eb_dom_destroy(dom);
    eb_browser_set_status(browser, "Done");
}

void eb_browser_navigate(eb_browser_t *browser, const char *url) {
    if (!browser || !url) return;

    strncpy(browser->tabs[browser->active_tab].url, url, EB_BROWSER_MAX_URL - 1);
    lv_textarea_set_text(browser->url_bar, url);

    if (browser->history_pos < browser->history_count - 1) {
        browser->history_count = browser->history_pos + 1;
    }
    if (browser->history_count < EB_BROWSER_MAX_HISTORY) {
        strncpy(browser->history[browser->history_count], url, EB_BROWSER_MAX_URL - 1);
        browser->history_pos = browser->history_count;
        browser->history_count++;
    }

    if (strcmp(url, EB_HOME_URL) == 0 || strcmp(url, "about:home") == 0) {
        eb_browser_set_status(browser, "Loading home page...");
        render_html(browser, s_home_html, strlen(s_home_html));
        return;
    }

    char status[256];
    snprintf(status, sizeof(status), "Loading %s...", url);
    eb_browser_set_status(browser, status);

    browser->tabs[browser->active_tab].loading = true;

    eb_http_response_t resp;
    if (eb_http_get(url, &resp) == 0 && resp.body) {
        render_html(browser, resp.body, resp.body_len);
        snprintf(status, sizeof(status), "HTTP %d — %zu bytes", resp.status_code, resp.body_len);
        eb_browser_set_status(browser, status);
        eb_http_response_free(&resp);
    } else {
        lv_obj_clean(browser->page_area);
        lv_obj_t *err_label = lv_label_create(browser->page_area);
        lv_label_set_text(err_label, "Failed to load page.\n\nCheck the URL and try again.");
        lv_obj_set_style_text_color(err_label, lv_color_make(185, 28, 28), LV_PART_MAIN);
        lv_obj_center(err_label);
        eb_browser_set_status(browser, "Error: Could not connect");
        eb_http_response_free(&resp);
    }

    browser->tabs[browser->active_tab].loading = false;
}

void eb_browser_back(eb_browser_t *browser) {
    if (!browser || browser->history_pos <= 0) return;
    browser->history_pos--;
    eb_browser_navigate(browser, browser->history[browser->history_pos]);
}

void eb_browser_forward(eb_browser_t *browser) {
    if (!browser || browser->history_pos >= browser->history_count - 1) return;
    browser->history_pos++;
    eb_browser_navigate(browser, browser->history[browser->history_pos]);
}

void eb_browser_reload(eb_browser_t *browser) {
    if (!browser) return;
    const char *url = browser->tabs[browser->active_tab].url;
    if (url[0]) eb_browser_navigate(browser, url);
}

void eb_browser_home(eb_browser_t *browser) {
    if (!browser) return;
    eb_browser_navigate(browser, EB_HOME_URL);
}

int eb_browser_new_tab(eb_browser_t *browser) {
    if (!browser || browser->tab_count >= EB_BROWSER_MAX_TABS) return -1;
    int idx = browser->tab_count++;
    memset(&browser->tabs[idx], 0, sizeof(eb_tab_t));
    strncpy(browser->tabs[idx].title, "New Tab", 255);
    browser->active_tab = idx;
    return idx;
}

void eb_browser_close_tab(eb_browser_t *browser, int index) {
    if (!browser || index < 0 || index >= browser->tab_count) return;
    if (browser->tab_count <= 1) return;
    for (int i = index; i < browser->tab_count - 1; i++) {
        browser->tabs[i] = browser->tabs[i + 1];
    }
    browser->tab_count--;
    if (browser->active_tab >= browser->tab_count) {
        browser->active_tab = browser->tab_count - 1;
    }
}

void eb_browser_switch_tab(eb_browser_t *browser, int index) {
    if (!browser || index < 0 || index >= browser->tab_count) return;
    browser->active_tab = index;
    lv_textarea_set_text(browser->url_bar, browser->tabs[index].url);
}

void eb_browser_set_status(eb_browser_t *browser, const char *text) {
    if (!browser || !browser->status_label) return;
    lv_label_set_text(browser->status_label, text ? text : "");
}
