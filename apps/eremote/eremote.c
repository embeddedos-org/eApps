// SPDX-License-Identifier: MIT
// eRemote UI — LVGL interface for Universal Smart Remote
#include "eremote.h"
#include "eapps/theme.h"
#include "eapps/widgets.h"
#include "lvgl.h"
#include <stdbool.h>
#include <stdio.h>
#include <string.h>

/* ---- Helpers ---- */

static lv_color_t hc(uint32_t hex)
{
    return lv_color_make((hex >> 16) & 0xFF, (hex >> 8) & 0xFF, hex & 0xFF);
}

/* ---- State ---- */

#define VOL_MIN     0
#define VOL_MAX     100
#define CH_MIN      1
#define CH_MAX      999
#define TEMP_MIN    16
#define TEMP_MAX    30

static eremote_device_t s_devices[MAX_DEVICES];
static int              s_device_count = 0;
static int              s_active_idx   = 0;
static bool             s_media_playing = false;

static lv_obj_t *s_root         = NULL;
static lv_obj_t *s_device_row   = NULL;
static lv_obj_t *s_remote_panel = NULL;
static lv_obj_t *s_status_lbl   = NULL;
static lv_obj_t *s_vol_lbl      = NULL;
static lv_obj_t *s_ch_lbl       = NULL;
static lv_obj_t *s_power_btn    = NULL;
static lv_obj_t *s_temp_lbl     = NULL;
static lv_obj_t *s_nav_bar      = NULL;

/* Bottom navigation tab index */
typedef enum {
    TAB_REMOTE = 0,
    TAB_SCENES,
    TAB_SCHEDULE,
    TAB_SETTINGS,
} eremote_tab_t;

static eremote_tab_t s_active_tab = TAB_REMOTE;

/* ---- Default Devices ---- */

static void load_default_devices(void)
{
    memset(s_devices, 0, sizeof(s_devices));

    #define SCPY(d,s) strncpy(d,s,sizeof(d)-1)
    SCPY(s_devices[0].name, "Sony TV");
    SCPY(s_devices[0].brand, "Sony");
    SCPY(s_devices[0].model, "Bravia");
    s_devices[0].type = EREMOTE_DEV_TV;
    s_devices[0].conn = EREMOTE_CONN_IR | EREMOTE_CONN_WIFI;
    s_devices[0].op_mode = EREMOTE_MODE_DIRECT;
    s_devices[0].power_on = true;
    s_devices[0].volume = 25;
    s_devices[0].channel = 1;
    s_devices[0].temperature = 24;
    s_devices[0].two_way = true;

    SCPY(s_devices[1].name, "Soundbar");
    SCPY(s_devices[1].brand, "Samsung");
    SCPY(s_devices[1].model, "Soundbar HW-Q");
    s_devices[1].type = EREMOTE_DEV_SOUNDBAR;
    s_devices[1].conn = EREMOTE_CONN_BLE;
    s_devices[1].op_mode = EREMOTE_MODE_DIRECT;
    s_devices[1].volume = 40;
    s_devices[1].channel = 1;
    s_devices[1].temperature = 24;
    s_devices[1].two_way = true;

    SCPY(s_devices[2].name, "Apple TV");
    SCPY(s_devices[2].brand, "Apple");
    SCPY(s_devices[2].model, "Apple TV 4K");
    s_devices[2].type = EREMOTE_DEV_STREAMING;
    s_devices[2].conn = EREMOTE_CONN_BLE;
    s_devices[2].op_mode = EREMOTE_MODE_DIRECT;
    s_devices[2].power_on = true;
    s_devices[2].volume = 50;
    s_devices[2].channel = 1;
    s_devices[2].temperature = 24;
    s_devices[2].two_way = true;

    SCPY(s_devices[3].name, "AC Unit");
    SCPY(s_devices[3].brand, "Daikin");
    SCPY(s_devices[3].model, "FTK-Series");
    s_devices[3].type = EREMOTE_DEV_AC;
    s_devices[3].conn = EREMOTE_CONN_IR;
    s_devices[3].op_mode = EREMOTE_MODE_HUB;
    s_devices[3].temperature = 22;
    s_devices[3].fan_speed = 2;
    s_devices[3].channel = 1;
    #undef SCPY

    s_device_count = 4;
    s_active_idx = 0;
}

static eremote_device_t *active_device(void)
{
    if (s_active_idx < 0 || s_active_idx >= s_device_count) return NULL;
    return &s_devices[s_active_idx];
}

/* ---- Toast Feedback ---- */

static void show_toast(const char *msg)
{
    if (s_status_lbl) lv_label_set_text(s_status_lbl, msg);
}

/* ---- Update Labels ---- */

static void refresh_labels(void)
{
    eremote_device_t *dev = active_device();
    if (!dev) return;

    if (s_vol_lbl) {
        char buf[16];
        snprintf(buf, sizeof(buf), "Vol: %d", dev->volume);
        lv_label_set_text(s_vol_lbl, buf);
    }
    if (s_ch_lbl) {
        char buf[16];
        snprintf(buf, sizeof(buf), "CH: %d", dev->channel);
        lv_label_set_text(s_ch_lbl, buf);
    }
    if (s_temp_lbl) {
        char buf[16];
        snprintf(buf, sizeof(buf), "%d" LV_SYMBOL_DEGREE_SIGN "C", dev->temperature);
        lv_label_set_text(s_temp_lbl, buf);
    }
    if (s_power_btn) {
        const eapps_palette_t *p = eapps_theme_get_palette();
        if (dev->power_on) {
            lv_obj_set_style_bg_color(s_power_btn, hc(0x00BFA5), 0);
            lv_obj_set_style_shadow_color(s_power_btn, hc(0x00BFA5), 0);
            lv_obj_set_style_shadow_width(s_power_btn, 12, 0);
            lv_obj_set_style_shadow_opa(s_power_btn, LV_OPA_40, 0);
        } else {
            lv_obj_set_style_bg_color(s_power_btn, hc(p->surface), 0);
            lv_obj_set_style_shadow_width(s_power_btn, 0, 0);
        }
    }
}

/* ---- Callbacks ---- */

static void power_cb(lv_event_t *e)
{
    (void)e;
    eremote_device_t *dev = active_device();
    if (!dev) return;
    dev->power_on = !dev->power_on;
    show_toast(dev->power_on ? "Power ON" : "Power OFF");
    refresh_labels();
}

static void vol_up_cb(lv_event_t *e)
{
    (void)e;
    eremote_device_t *dev = active_device();
    if (!dev) return;
    if (dev->volume < VOL_MAX) dev->volume++;
    show_toast("Volume +");
    refresh_labels();
}

static void vol_down_cb(lv_event_t *e)
{
    (void)e;
    eremote_device_t *dev = active_device();
    if (!dev) return;
    if (dev->volume > VOL_MIN) dev->volume--;
    show_toast("Volume -");
    refresh_labels();
}

static void ch_up_cb(lv_event_t *e)
{
    (void)e;
    eremote_device_t *dev = active_device();
    if (!dev) return;
    dev->channel = (dev->channel >= CH_MAX) ? CH_MIN : dev->channel + 1;
    show_toast("Channel +");
    refresh_labels();
}

static void ch_down_cb(lv_event_t *e)
{
    (void)e;
    eremote_device_t *dev = active_device();
    if (!dev) return;
    dev->channel = (dev->channel <= CH_MIN) ? CH_MAX : dev->channel - 1;
    show_toast("Channel -");
    refresh_labels();
}

static void dpad_cb(lv_event_t *e)
{
    const char *dir = (const char *)lv_event_get_user_data(e);
    char buf[32];
    snprintf(buf, sizeof(buf), "D-Pad: %s", dir ? dir : "?");
    show_toast(buf);
}

static void numpad_cb(lv_event_t *e)
{
    intptr_t digit = (intptr_t)lv_event_get_user_data(e);
    char buf[24];
    snprintf(buf, sizeof(buf), "Input: %d", (int)digit);
    show_toast(buf);
}

static void media_play_cb(lv_event_t *e)
{
    (void)e;
    s_media_playing = !s_media_playing;
    show_toast(s_media_playing ? "Play" : "Pause");
}

static void media_ff_cb(lv_event_t *e)    { (void)e; show_toast("Fast Forward"); }
static void media_rew_cb(lv_event_t *e)   { (void)e; show_toast("Rewind"); }
static void media_skip_cb(lv_event_t *e)  { (void)e; show_toast("Skip"); }
static void menu_cb(lv_event_t *e)        { (void)e; show_toast("Menu"); }
static void back_cb(lv_event_t *e)        { (void)e; show_toast("Back"); }

static void temp_up_cb(lv_event_t *e)
{
    (void)e;
    eremote_device_t *dev = active_device();
    if (!dev) return;
    if (dev->temperature < TEMP_MAX) dev->temperature++;
    show_toast("Temp +");
    refresh_labels();
}

static void temp_down_cb(lv_event_t *e)
{
    (void)e;
    eremote_device_t *dev = active_device();
    if (!dev) return;
    if (dev->temperature > TEMP_MIN) dev->temperature--;
    show_toast("Temp -");
    refresh_labels();
}

/* ---- Connection Toggle ---- */

static void ir_toggle_cb(lv_event_t *e)
{
    lv_obj_t *sw = lv_event_get_target(e);
    eremote_device_t *dev = active_device();
    if (!dev) return;
    if (lv_obj_has_state(sw, LV_STATE_CHECKED))
        dev->conn |= EREMOTE_CONN_IR;
    else
        dev->conn &= (uint8_t)~EREMOTE_CONN_IR;
    show_toast((dev->conn & EREMOTE_CONN_IR) ? "IR enabled" : "IR disabled");
}

static void ble_toggle_cb(lv_event_t *e)
{
    lv_obj_t *sw = lv_event_get_target(e);
    eremote_device_t *dev = active_device();
    if (!dev) return;
    if (lv_obj_has_state(sw, LV_STATE_CHECKED))
        dev->conn |= EREMOTE_CONN_BLE;
    else
        dev->conn &= (uint8_t)~EREMOTE_CONN_BLE;
    show_toast((dev->conn & EREMOTE_CONN_BLE) ? "BLE enabled" : "BLE disabled");
}

/* ---- Device Card Selection ---- */

static void rebuild_remote_panel(void);

static void device_card_cb(lv_event_t *e)
{
    intptr_t idx = (intptr_t)lv_event_get_user_data(e);
    if (idx >= 0 && idx < s_device_count) {
        s_active_idx = (int)idx;
        show_toast(s_devices[s_active_idx].name);
        rebuild_remote_panel();
    }
}

static void add_device_cb(lv_event_t *e)
{
    (void)e;
    if (s_device_count >= MAX_DEVICES) {
        show_toast("Max devices reached");
        return;
    }
    memset(&s_devices[s_device_count], 0, sizeof(eremote_device_t));
    strncpy(s_devices[s_device_count].name, "New Device", 31);
    strncpy(s_devices[s_device_count].brand, "Unknown", 23);
    s_devices[s_device_count].type = EREMOTE_DEV_CUSTOM;
    s_devices[s_device_count].conn = EREMOTE_CONN_BLE;
    s_devices[s_device_count].op_mode = EREMOTE_MODE_DIRECT;
    s_devices[s_device_count].volume = 30;
    s_devices[s_device_count].channel = 1;
    s_devices[s_device_count].temperature = 24;
    s_device_count++;
    show_toast("Device added");
}

/* ---- UI Builder Helpers ---- */

static lv_obj_t *make_icon_btn(lv_obj_t *parent, const char *label,
                                int w, int h, uint32_t bg_color,
                                uint32_t text_color, lv_event_cb_t cb,
                                void *user_data)
{
    lv_obj_t *btn = lv_button_create(parent);
    lv_obj_set_size(btn, w, h);
    lv_obj_set_style_bg_color(btn, hc(bg_color), 0);
    lv_obj_set_style_bg_opa(btn, LV_OPA_COVER, 0);
    lv_obj_set_style_radius(btn, 8, 0);
    lv_obj_set_style_shadow_width(btn, 0, 0);

    lv_obj_t *lbl = lv_label_create(btn);
    lv_label_set_text(lbl, label);
    lv_obj_set_style_text_color(lbl, hc(text_color), 0);
    lv_obj_center(lbl);

    if (cb) lv_obj_add_event_cb(btn, cb, LV_EVENT_CLICKED, user_data);
    return btn;
}

static lv_obj_t *make_row(lv_obj_t *parent)
{
    lv_obj_t *row = lv_obj_create(parent);
    lv_obj_set_size(row, LV_PCT(100), LV_SIZE_CONTENT);
    lv_obj_set_style_bg_opa(row, LV_OPA_TRANSP, 0);
    lv_obj_set_style_border_width(row, 0, 0);
    lv_obj_set_style_pad_all(row, 0, 0);
    lv_obj_set_style_pad_gap(row, 6, 0);
    lv_obj_set_flex_flow(row, LV_FLEX_FLOW_ROW);
    lv_obj_set_flex_align(row, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER,
                          LV_FLEX_ALIGN_CENTER);
    return row;
}

/* ---- Build Device Cards Row ---- */

static void build_device_row(lv_obj_t *parent)
{
    const eapps_palette_t *p = eapps_theme_get_palette();

    s_device_row = lv_obj_create(parent);
    lv_obj_set_size(s_device_row, LV_PCT(100), 70);
    lv_obj_set_style_bg_opa(s_device_row, LV_OPA_TRANSP, 0);
    lv_obj_set_style_border_width(s_device_row, 0, 0);
    lv_obj_set_style_pad_all(s_device_row, 4, 0);
    lv_obj_set_style_pad_gap(s_device_row, 8, 0);
    lv_obj_set_flex_flow(s_device_row, LV_FLEX_FLOW_ROW);
    lv_obj_set_flex_align(s_device_row, LV_FLEX_ALIGN_START,
                          LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER);
    lv_obj_add_flag(s_device_row, LV_OBJ_FLAG_SCROLLABLE);

    for (int i = 0; i < s_device_count; i++) {
        bool is_active = (i == s_active_idx);

        lv_obj_t *card = lv_obj_create(s_device_row);
        lv_obj_set_size(card, 100, 56);
        lv_obj_set_style_bg_color(card, is_active ? hc(p->primary) : hc(p->card), 0);
        lv_obj_set_style_bg_opa(card, LV_OPA_COVER, 0);
        lv_obj_set_style_radius(card, 10, 0);
        lv_obj_set_style_border_color(card, hc(p->border), 0);
        lv_obj_set_style_border_width(card, is_active ? 2 : 1, 0);
        lv_obj_set_style_pad_all(card, 6, 0);
        lv_obj_set_flex_flow(card, LV_FLEX_FLOW_COLUMN);
        lv_obj_set_flex_align(card, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER,
                              LV_FLEX_ALIGN_CENTER);

        lv_obj_t *name = lv_label_create(card);
        lv_label_set_text(name, s_devices[i].name);
        lv_obj_set_style_text_color(name,
            is_active ? hc(p->on_primary) : hc(p->on_surface), 0);
        lv_obj_set_style_text_font(name, &lv_font_montserrat_12, 0);

        lv_obj_t *brand = lv_label_create(card);
        lv_label_set_text(brand, s_devices[i].brand);
        lv_obj_set_style_text_color(brand,
            is_active ? hc(p->on_primary) : hc(p->on_surface), 0);
        lv_obj_set_style_text_opa(brand, LV_OPA_60, 0);
        lv_obj_set_style_text_font(brand, &lv_font_montserrat_12, 0);

        lv_obj_add_event_cb(card, device_card_cb, LV_EVENT_CLICKED,
                            (void *)(intptr_t)i);
    }

    /* "+ Add Device" card */
    lv_obj_t *add_card = lv_obj_create(s_device_row);
    lv_obj_set_size(add_card, 56, 56);
    lv_obj_set_style_bg_color(add_card, hc(p->surface), 0);
    lv_obj_set_style_bg_opa(add_card, LV_OPA_COVER, 0);
    lv_obj_set_style_radius(add_card, 10, 0);
    lv_obj_set_style_border_color(add_card, hc(p->border), 0);
    lv_obj_set_style_border_width(add_card, 1, 0);
    lv_obj_set_style_border_opa(add_card, LV_OPA_50, 0);

    lv_obj_t *plus = lv_label_create(add_card);
    lv_label_set_text(plus, LV_SYMBOL_PLUS);
    lv_obj_set_style_text_color(plus, hc(p->primary), 0);
    lv_obj_set_style_text_font(plus, &lv_font_montserrat_16, 0);
    lv_obj_center(plus);

    lv_obj_add_event_cb(add_card, add_device_cb, LV_EVENT_CLICKED, NULL);
}

/* ---- Build Connection Row ---- */

static void build_connection_row(lv_obj_t *parent)
{
    const eapps_palette_t *p = eapps_theme_get_palette();
    eremote_device_t *dev = active_device();
    if (!dev) return;

    lv_obj_t *row = make_row(parent);
    lv_obj_set_style_pad_hor(row, 8, 0);

    lv_obj_t *ir_lbl = lv_label_create(row);
    lv_label_set_text(ir_lbl, "IR");
    lv_obj_set_style_text_color(ir_lbl, hc(p->on_surface), 0);

    lv_obj_t *ir_sw = lv_switch_create(row);
    lv_obj_set_size(ir_sw, 40, 22);
    if (dev->conn & EREMOTE_CONN_IR) lv_obj_add_state(ir_sw, LV_STATE_CHECKED);
    lv_obj_add_event_cb(ir_sw, ir_toggle_cb, LV_EVENT_VALUE_CHANGED, NULL);

    lv_obj_t *spacer = lv_obj_create(row);
    lv_obj_set_size(spacer, 20, 1);
    lv_obj_set_style_bg_opa(spacer, LV_OPA_TRANSP, 0);
    lv_obj_set_style_border_width(spacer, 0, 0);

    lv_obj_t *ble_lbl = lv_label_create(row);
    lv_label_set_text(ble_lbl, LV_SYMBOL_BLUETOOTH " BLE");
    lv_obj_set_style_text_color(ble_lbl, hc(p->on_surface), 0);

    lv_obj_t *ble_sw = lv_switch_create(row);
    lv_obj_set_size(ble_sw, 40, 22);
    if (dev->conn & EREMOTE_CONN_BLE) lv_obj_add_state(ble_sw, LV_STATE_CHECKED);
    lv_obj_add_event_cb(ble_sw, ble_toggle_cb, LV_EVENT_VALUE_CHANGED, NULL);
}

/* ---- Build D-Pad ---- */

static void build_dpad(lv_obj_t *parent, uint32_t btn_bg, uint32_t btn_fg)
{
    static const char *dirs[] = {"Up", "Down", "Left", "Right", "OK"};

    /* Row 1: Up */
    lv_obj_t *r1 = make_row(parent);
    make_icon_btn(r1, LV_SYMBOL_UP, 48, 40, btn_bg, btn_fg, dpad_cb, (void *)dirs[0]);

    /* Row 2: Left, OK, Right */
    lv_obj_t *r2 = make_row(parent);
    make_icon_btn(r2, LV_SYMBOL_LEFT, 48, 40, btn_bg, btn_fg, dpad_cb, (void *)dirs[2]);
    make_icon_btn(r2, "OK", 56, 40, 0x00BFA5, 0xFFFFFF, dpad_cb, (void *)dirs[4]);
    make_icon_btn(r2, LV_SYMBOL_RIGHT, 48, 40, btn_bg, btn_fg, dpad_cb, (void *)dirs[3]);

    /* Row 3: Down */
    lv_obj_t *r3 = make_row(parent);
    make_icon_btn(r3, LV_SYMBOL_DOWN, 48, 40, btn_bg, btn_fg, dpad_cb, (void *)dirs[1]);
}

/* ---- Build Volume & Channel Controls ---- */

static void build_vol_ch(lv_obj_t *parent, uint32_t btn_bg, uint32_t btn_fg)
{
    const eapps_palette_t *p = eapps_theme_get_palette();

    lv_obj_t *row = make_row(parent);

    /* Volume */
    make_icon_btn(row, LV_SYMBOL_VOLUME_MID " -", 52, 36, btn_bg, btn_fg, vol_down_cb, NULL);
    s_vol_lbl = lv_label_create(row);
    lv_label_set_text(s_vol_lbl, "Vol: 0");
    lv_obj_set_style_text_color(s_vol_lbl, hc(p->on_surface), 0);
    lv_obj_set_style_min_width(s_vol_lbl, 60, 0);
    lv_obj_set_style_text_align(s_vol_lbl, LV_TEXT_ALIGN_CENTER, 0);
    make_icon_btn(row, LV_SYMBOL_VOLUME_MAX " +", 52, 36, btn_bg, btn_fg, vol_up_cb, NULL);

    /* Spacer */
    lv_obj_t *sp = lv_obj_create(row);
    lv_obj_set_size(sp, 12, 1);
    lv_obj_set_style_bg_opa(sp, LV_OPA_TRANSP, 0);
    lv_obj_set_style_border_width(sp, 0, 0);

    /* Channel */
    make_icon_btn(row, "CH-", 44, 36, btn_bg, btn_fg, ch_down_cb, NULL);
    s_ch_lbl = lv_label_create(row);
    lv_label_set_text(s_ch_lbl, "CH: 1");
    lv_obj_set_style_text_color(s_ch_lbl, hc(p->on_surface), 0);
    lv_obj_set_style_min_width(s_ch_lbl, 56, 0);
    lv_obj_set_style_text_align(s_ch_lbl, LV_TEXT_ALIGN_CENTER, 0);
    make_icon_btn(row, "CH+", 44, 36, btn_bg, btn_fg, ch_up_cb, NULL);
}

/* ---- Build Number Pad ---- */

static void build_numpad(lv_obj_t *parent, uint32_t btn_bg, uint32_t btn_fg)
{
    for (int row_start = 1; row_start <= 9; row_start += 3) {
        lv_obj_t *r = make_row(parent);
        for (int d = row_start; d < row_start + 3; d++) {
            char txt[4];
            snprintf(txt, sizeof(txt), "%d", d);
            make_icon_btn(r, txt, 44, 36, btn_bg, btn_fg, numpad_cb,
                          (void *)(intptr_t)d);
        }
    }
    /* 0, Menu, Back */
    lv_obj_t *r4 = make_row(parent);
    make_icon_btn(r4, "0", 44, 36, btn_bg, btn_fg, numpad_cb, (void *)(intptr_t)0);
    make_icon_btn(r4, "Menu", 52, 36, btn_bg, btn_fg, menu_cb, NULL);
    make_icon_btn(r4, LV_SYMBOL_LEFT " Back", 60, 36, btn_bg, btn_fg, back_cb, NULL);
}

/* ---- Build Media Controls ---- */

static void build_media(lv_obj_t *parent, uint32_t btn_bg, uint32_t btn_fg)
{
    lv_obj_t *row = make_row(parent);
    make_icon_btn(row, LV_SYMBOL_PREV, 40, 36, btn_bg, btn_fg, media_rew_cb, NULL);
    make_icon_btn(row, LV_SYMBOL_PLAY " / " LV_SYMBOL_PAUSE, 72, 36,
                  0x00BFA5, 0xFFFFFF, media_play_cb, NULL);
    make_icon_btn(row, LV_SYMBOL_NEXT, 40, 36, btn_bg, btn_fg, media_ff_cb, NULL);
    make_icon_btn(row, "Skip", 48, 36, btn_bg, btn_fg, media_skip_cb, NULL);
}

/* ---- Build AC Controls ---- */

static void build_ac_controls(lv_obj_t *parent, uint32_t btn_bg, uint32_t btn_fg)
{
    const eapps_palette_t *p = eapps_theme_get_palette();

    lv_obj_t *temp_card = eapps_card_create(parent);
    lv_obj_t *temp_title = lv_label_create(temp_card);
    lv_label_set_text(temp_title, "Temperature");
    lv_obj_set_style_text_color(temp_title, hc(p->primary), 0);
    lv_obj_set_style_text_font(temp_title, &lv_font_montserrat_14, 0);

    lv_obj_t *row = make_row(temp_card);
    make_icon_btn(row, "-", 48, 44, btn_bg, btn_fg, temp_down_cb, NULL);

    s_temp_lbl = lv_label_create(row);
    lv_label_set_text(s_temp_lbl, "24" LV_SYMBOL_DEGREE_SIGN "C");
    lv_obj_set_style_text_color(s_temp_lbl, hc(p->on_surface), 0);
    lv_obj_set_style_text_font(s_temp_lbl, &lv_font_montserrat_16, 0);
    lv_obj_set_style_min_width(s_temp_lbl, 72, 0);
    lv_obj_set_style_text_align(s_temp_lbl, LV_TEXT_ALIGN_CENTER, 0);

    make_icon_btn(row, "+", 48, 44, btn_bg, btn_fg, temp_up_cb, NULL);
}

/* ---- Rebuild Remote Panel ---- */

static void rebuild_remote_panel(void)
{
    if (!s_root) return;
    const eapps_palette_t *p = eapps_theme_get_palette();
    eremote_device_t *dev = active_device();
    if (!dev) return;

    /* Tear down existing UI */
    if (s_device_row)   { lv_obj_delete(s_device_row);   s_device_row = NULL; }
    if (s_remote_panel) { lv_obj_delete(s_remote_panel);  s_remote_panel = NULL; }
    s_vol_lbl = NULL;
    s_ch_lbl  = NULL;
    s_temp_lbl = NULL;
    s_power_btn = NULL;

    lv_obj_t *body = lv_obj_get_child(s_root, 1);
    if (!body) return;

    uint32_t btn_bg = p->surface;
    uint32_t btn_fg = p->on_surface;

    /* Device cards */
    build_device_row(body);

    /* Remote panel (scrollable) */
    s_remote_panel = lv_obj_create(body);
    lv_obj_set_size(s_remote_panel, LV_PCT(100), LV_SIZE_CONTENT);
    lv_obj_set_flex_grow(s_remote_panel, 1);
    lv_obj_set_style_bg_opa(s_remote_panel, LV_OPA_TRANSP, 0);
    lv_obj_set_style_border_width(s_remote_panel, 0, 0);
    lv_obj_set_style_pad_all(s_remote_panel, 4, 0);
    lv_obj_set_style_pad_gap(s_remote_panel, 6, 0);
    lv_obj_set_flex_flow(s_remote_panel, LV_FLEX_FLOW_COLUMN);
    lv_obj_set_flex_align(s_remote_panel, LV_FLEX_ALIGN_START,
                          LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER);
    lv_obj_add_flag(s_remote_panel, LV_OBJ_FLAG_SCROLLABLE);

    /* Connection toggles */
    build_connection_row(s_remote_panel);

    /* Power button */
    lv_obj_t *pwr_row = make_row(s_remote_panel);
    s_power_btn = make_icon_btn(pwr_row, LV_SYMBOL_POWER, 56, 44,
                                p->surface, p->on_surface, power_cb, NULL);
    lv_obj_set_style_radius(s_power_btn, 22, 0);

    /* Adaptive layout based on device type */
    switch (dev->type) {
    case EREMOTE_DEV_TV:
        build_dpad(s_remote_panel, btn_bg, btn_fg);
        build_vol_ch(s_remote_panel, btn_bg, btn_fg);
        build_numpad(s_remote_panel, btn_bg, btn_fg);
        build_media(s_remote_panel, btn_bg, btn_fg);
        break;
    case EREMOTE_DEV_SOUNDBAR:
        build_vol_ch(s_remote_panel, btn_bg, btn_fg);
        build_media(s_remote_panel, btn_bg, btn_fg);
        break;
    case EREMOTE_DEV_STREAMING:
        build_dpad(s_remote_panel, btn_bg, btn_fg);
        build_media(s_remote_panel, btn_bg, btn_fg);
        build_vol_ch(s_remote_panel, btn_bg, btn_fg);
        break;
    case EREMOTE_DEV_AC:
        build_ac_controls(s_remote_panel, btn_bg, btn_fg);
        break;
    case EREMOTE_DEV_CUSTOM:
        build_dpad(s_remote_panel, btn_bg, btn_fg);
        build_vol_ch(s_remote_panel, btn_bg, btn_fg);
        build_media(s_remote_panel, btn_bg, btn_fg);
        break;
    }

    refresh_labels();
}

/* ---- Build Bottom Navigation Bar ---- */

static void nav_tab_cb(lv_event_t *e)
{
    intptr_t tab = (intptr_t)lv_event_get_user_data(e);
    s_active_tab = (eremote_tab_t)tab;

    static const char *tab_names[] = {"Remote", "Scenes", "Schedule", "Settings"};
    if (tab >= TAB_SCENES && tab <= TAB_SETTINGS) {
        show_toast(tab_names[tab]);
    }
}

static void build_nav_bar(lv_obj_t *parent)
{
    const eapps_palette_t *p = eapps_theme_get_palette();

    s_nav_bar = lv_obj_create(parent);
    lv_obj_set_size(s_nav_bar, LV_PCT(100), 48);
    lv_obj_set_style_bg_color(s_nav_bar, hc(p->card), 0);
    lv_obj_set_style_bg_opa(s_nav_bar, LV_OPA_COVER, 0);
    lv_obj_set_style_border_width(s_nav_bar, 0, 0);
    lv_obj_set_style_radius(s_nav_bar, 0, 0);
    lv_obj_set_style_pad_all(s_nav_bar, 0, 0);
    lv_obj_set_flex_flow(s_nav_bar, LV_FLEX_FLOW_ROW);
    lv_obj_set_flex_align(s_nav_bar, LV_FLEX_ALIGN_SPACE_EVENLY,
                          LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER);

    static const char *icons[] = {
        LV_SYMBOL_HOME, LV_SYMBOL_LIST, LV_SYMBOL_BELL, LV_SYMBOL_SETTINGS
    };
    static const char *labels[] = {"Remote", "Scenes", "Schedule", "Settings"};

    for (int i = 0; i < 4; i++) {
        bool active = (i == (int)s_active_tab);

        lv_obj_t *btn = lv_button_create(s_nav_bar);
        lv_obj_set_size(btn, LV_SIZE_CONTENT, 40);
        lv_obj_set_style_bg_opa(btn, LV_OPA_TRANSP, 0);
        lv_obj_set_style_shadow_width(btn, 0, 0);
        lv_obj_set_style_pad_hor(btn, 10, 0);
        lv_obj_set_flex_flow(btn, LV_FLEX_FLOW_COLUMN);
        lv_obj_set_flex_align(btn, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER,
                              LV_FLEX_ALIGN_CENTER);

        lv_obj_t *ico = lv_label_create(btn);
        lv_label_set_text(ico, icons[i]);
        lv_obj_set_style_text_color(ico,
            active ? hc(p->primary) : hc(p->on_surface), 0);

        lv_obj_t *lbl = lv_label_create(btn);
        lv_label_set_text(lbl, labels[i]);
        lv_obj_set_style_text_font(lbl, &lv_font_montserrat_12, 0);
        lv_obj_set_style_text_color(lbl,
            active ? hc(p->primary) : hc(p->on_surface), 0);
        lv_obj_set_style_text_opa(lbl, active ? LV_OPA_COVER : LV_OPA_60, 0);

        lv_obj_add_event_cb(btn, nav_tab_cb, LV_EVENT_CLICKED,
                            (void *)(intptr_t)i);
    }
}

/* ---- Lifecycle ---- */

static bool eremote_init(lv_obj_t *parent)
{
    const eapps_palette_t *p = eapps_theme_get_palette();

    /* Initialize engine subsystems */
    eremote_ir_db_init();
    eremote_scenes_init();
    eremote_schedules_init();

    load_default_devices();
    s_media_playing = false;
    s_active_tab = TAB_REMOTE;

    s_root = eapps_scaffold_create(parent, "eRemote", false);
    lv_obj_t *body = lv_obj_get_child(s_root, 1);
    lv_obj_set_flex_flow(body, LV_FLEX_FLOW_COLUMN);
    lv_obj_set_style_pad_all(body, 4, 0);
    lv_obj_set_style_pad_gap(body, 4, 0);

    /* Status / toast bar */
    s_status_lbl = lv_label_create(body);
    lv_label_set_text(s_status_lbl, "Select a device");
    lv_obj_set_style_text_color(s_status_lbl, hc(p->primary), 0);
    lv_obj_set_style_text_font(s_status_lbl, &lv_font_montserrat_12, 0);
    lv_obj_set_style_text_align(s_status_lbl, LV_TEXT_ALIGN_CENTER, 0);
    lv_obj_set_width(s_status_lbl, LV_PCT(100));

    rebuild_remote_panel();

    /* Bottom navigation */
    build_nav_bar(body);

    return true;
}

static void eremote_deinit(void)
{
    s_root         = NULL;
    s_device_row   = NULL;
    s_remote_panel = NULL;
    s_status_lbl   = NULL;
    s_vol_lbl      = NULL;
    s_ch_lbl       = NULL;
    s_power_btn    = NULL;
    s_temp_lbl     = NULL;
    s_nav_bar      = NULL;
    s_device_count = 0;
    s_active_idx   = 0;
}

static void eremote_on_show(void) {}
static void eremote_on_hide(void) {}

const eapps_app_info_t eremote_info = {
    .id = "eremote",
    .name = "eRemote",
    .icon = LV_SYMBOL_WIFI,
    .description = "Universal smart remote — BLE & IR",
    .category = EAPPS_CAT_CONNECTIVITY,
    .version = "1.0.0",
};

const eapps_app_lifecycle_t eremote_lifecycle = {
    .init = eremote_init,
    .deinit = eremote_deinit,
    .on_show = eremote_on_show,
    .on_hide = eremote_on_hide,
};
