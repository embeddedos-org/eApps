// SPDX-License-Identifier: MIT
#include "esettings.h"
#include "eapps/theme.h"
#include "eapps/widgets.h"
#include "lvgl.h"
#include <stdbool.h>

static lv_color_t hc(uint32_t hex)
{
    return lv_color_make((hex >> 16) & 0xFF, (hex >> 8) & 0xFF, hex & 0xFF);
}

static void theme_toggle_cb(lv_event_t *e)
{
    (void)e;
    eapps_theme_toggle();
}

static void brightness_cb(lv_event_t *e)
{
    lv_obj_t *slider = lv_event_get_target(e);
    int val = (int)lv_slider_get_value(slider);
    (void)val;
}

static bool esettings_init(lv_obj_t *parent)
{
    const eapps_palette_t *p = eapps_theme_get_palette();

    lv_obj_t *scaf = eapps_scaffold_create(parent, "Settings", false);
    lv_obj_t *body = lv_obj_get_child(scaf, 1);
    lv_obj_set_flex_flow(body, LV_FLEX_FLOW_COLUMN);
    lv_obj_set_style_pad_all(body, 12, 0);
    lv_obj_set_style_pad_gap(body, 8, 0);

    /* Display section */
    lv_obj_t *disp_card = eapps_card_create(body);
    lv_obj_t *disp_title = lv_label_create(disp_card);
    lv_label_set_text(disp_title, LV_SYMBOL_IMAGE "  Display");
    lv_obj_set_style_text_color(disp_title, hc(p->primary), 0);
    lv_obj_set_style_text_font(disp_title, &lv_font_montserrat_14, 0);

    /* Brightness slider */
    lv_obj_t *br_row = lv_obj_create(disp_card);
    lv_obj_set_size(br_row, LV_PCT(100), 40);
    lv_obj_set_style_bg_opa(br_row, LV_OPA_TRANSP, 0);
    lv_obj_set_style_border_width(br_row, 0, 0);
    lv_obj_set_style_pad_all(br_row, 0, 0);
    lv_obj_set_flex_flow(br_row, LV_FLEX_FLOW_ROW);
    lv_obj_set_flex_align(br_row, LV_FLEX_ALIGN_START, LV_FLEX_ALIGN_CENTER,
                          LV_FLEX_ALIGN_CENTER);

    lv_obj_t *br_lbl = lv_label_create(br_row);
    lv_label_set_text(br_lbl, "Brightness");
    lv_obj_set_style_text_color(br_lbl, hc(p->on_surface), 0);
    lv_obj_set_style_min_width(br_lbl, 100, 0);

    lv_obj_t *slider = lv_slider_create(br_row);
    lv_obj_set_width(slider, 180);
    lv_slider_set_range(slider, 0, 100);
    lv_slider_set_value(slider, 80, LV_ANIM_OFF);
    lv_obj_add_event_cb(slider, brightness_cb, LV_EVENT_VALUE_CHANGED, NULL);

    /* Theme toggle */
    lv_obj_t *theme_row = lv_obj_create(disp_card);
    lv_obj_set_size(theme_row, LV_PCT(100), 40);
    lv_obj_set_style_bg_opa(theme_row, LV_OPA_TRANSP, 0);
    lv_obj_set_style_border_width(theme_row, 0, 0);
    lv_obj_set_style_pad_all(theme_row, 0, 0);
    lv_obj_set_flex_flow(theme_row, LV_FLEX_FLOW_ROW);
    lv_obj_set_flex_align(theme_row, LV_FLEX_ALIGN_SPACE_BETWEEN,
                          LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER);

    lv_obj_t *theme_lbl = lv_label_create(theme_row);
    lv_label_set_text(theme_lbl, "Dark Theme");
    lv_obj_set_style_text_color(theme_lbl, hc(p->on_surface), 0);

    lv_obj_t *sw = lv_switch_create(theme_row);
    if (eapps_theme_is_dark()) lv_obj_add_state(sw, LV_STATE_CHECKED);
    lv_obj_add_event_cb(sw, theme_toggle_cb, LV_EVENT_VALUE_CHANGED, NULL);

    /* System info section */
    lv_obj_t *sys_card = eapps_card_create(body);
    lv_obj_t *sys_title = lv_label_create(sys_card);
    lv_label_set_text(sys_title, LV_SYMBOL_SETTINGS "  System Info");
    lv_obj_set_style_text_color(sys_title, hc(p->primary), 0);
    lv_obj_set_style_text_font(sys_title, &lv_font_montserrat_14, 0);

    lv_obj_t *info_list = eapps_list_create(sys_card);
    eapps_list_item_create(info_list, NULL, "OS", "EoS v1.0.0");
    eapps_list_item_create(info_list, NULL, "Display", "800x480 RGB565");
    eapps_list_item_create(info_list, NULL, "Product", "Desktop");
    eapps_list_item_create(info_list, NULL, "Backend", "SDL2 / Linux FB");

    /* Network section */
    lv_obj_t *net_card = eapps_card_create(body);
    lv_obj_t *net_title = lv_label_create(net_card);
    lv_label_set_text(net_title, LV_SYMBOL_WIFI "  Network");
    lv_obj_set_style_text_color(net_title, hc(p->primary), 0);
    lv_obj_set_style_text_font(net_title, &lv_font_montserrat_14, 0);

    lv_obj_t *net_list = eapps_list_create(net_card);
    eapps_list_item_create(net_list, NULL, "WiFi", "Connected");
    eapps_list_item_create(net_list, NULL, "Bluetooth", "Off");
    eapps_list_item_create(net_list, NULL, "IP Address", "192.168.1.100");

    /* About section */
    lv_obj_t *about_card = eapps_card_create(body);
    lv_obj_t *about_title = lv_label_create(about_card);
    lv_label_set_text(about_title, "About EoS");
    lv_obj_set_style_text_color(about_title, hc(p->primary), 0);
    lv_obj_set_style_text_font(about_title, &lv_font_montserrat_14, 0);

    lv_obj_t *about_text = lv_label_create(about_card);
    lv_label_set_text(about_text,
        "EoS (EmbeddedOS) is an open-source embedded operating\n"
        "system framework. Built with LVGL for display.\n\n"
        "https://embeddedos-org.github.io");
    lv_label_set_long_mode(about_text, LV_LABEL_LONG_WRAP);
    lv_obj_set_width(about_text, LV_PCT(100));
    lv_obj_set_style_text_color(about_text, hc(p->on_surface), 0);

    return true;
}

static void esettings_deinit(void) {}
static void esettings_on_show(void) {}
static void esettings_on_hide(void) {}

const eapps_app_info_t esettings_info = {
    .id = "esettings", .name = "Settings", .icon = LV_SYMBOL_SETTINGS,
    .description = "System settings and configuration",
    .category = EAPPS_CAT_PRODUCTIVITY, .version = "1.0.0",
};
const eapps_app_lifecycle_t esettings_lifecycle = {
    .init = esettings_init, .deinit = esettings_deinit,
    .on_show = esettings_on_show, .on_hide = esettings_on_hide,
};
