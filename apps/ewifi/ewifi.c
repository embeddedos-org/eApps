// SPDX-License-Identifier: MIT
// eWiFi UI — LVGL interface for WiFi Analyzer & Security Education
#include "ewifi.h"
#include "eapps/theme.h"
#include "eapps/widgets.h"
#include "lvgl.h"
#include <stdbool.h>
#include <stdio.h>
#include <string.h>

static lv_color_t hc(uint32_t hex) {
    return lv_color_make((hex >> 16) & 0xFF, (hex >> 8) & 0xFF, hex & 0xFF);
}

/* ---- State ---- */
static lv_obj_t *s_root = NULL;
static lv_obj_t *s_status_lbl = NULL;
static lv_obj_t *s_content = NULL;
static lv_obj_t *s_nav_bar = NULL;

typedef enum { TAB_SCAN=0, TAB_CHANNELS, TAB_PASSWORDS, TAB_SECURITY } ewifi_tab_t;
static ewifi_tab_t s_active_tab = TAB_SCAN;

static ewifi_network_t s_networks[EWIFI_MAX_NETWORKS];
static int s_net_count = 0;
static int s_selected_net = 0;
static ewifi_vault_t s_vault;
static ewifi_auto_connect_t s_ac;

static void rebuild_content(void);

static void show_toast(const char *msg) {
    if (s_status_lbl) lv_label_set_text(s_status_lbl, msg);
}

/* ---- Signal Color ---- */
static uint32_t signal_color(int rssi) {
    if (rssi > -50) return 0x00E676;
    if (rssi > -60) return 0x66BB6A;
    if (rssi > -70) return 0xFFEB3B;
    if (rssi > -80) return 0xFF9800;
    return 0xF44336;
}

static uint32_t risk_color(ewifi_risk_level_t r) {
    switch (r) {
    case EWIFI_RISK_SECURE:  return 0x00E676;
    case EWIFI_RISK_LOW:     return 0x66BB6A;
    case EWIFI_RISK_MEDIUM:  return 0xFFEB3B;
    case EWIFI_RISK_HIGH:    return 0xFF9800;
    case EWIFI_RISK_CRITICAL: return 0xF44336;
    }
    return 0xFFFFFF;
}

/* ---- Helpers ---- */
static lv_obj_t *make_row(lv_obj_t *par) {
    lv_obj_t *r = lv_obj_create(par);
    lv_obj_set_size(r, LV_PCT(100), LV_SIZE_CONTENT);
    lv_obj_set_style_bg_opa(r, LV_OPA_TRANSP, 0);
    lv_obj_set_style_border_width(r, 0, 0);
    lv_obj_set_style_pad_all(r, 0, 0);
    lv_obj_set_style_pad_gap(r, 6, 0);
    lv_obj_set_flex_flow(r, LV_FLEX_FLOW_ROW);
    lv_obj_set_flex_align(r, LV_FLEX_ALIGN_START, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER);
    return r;
}

/* ---- Build Network List (Scan Tab) ---- */
static void net_click_cb(lv_event_t *e) {
    intptr_t idx = (intptr_t)lv_event_get_user_data(e);
    s_selected_net = (int)idx;

    /* Run 6-flag validation */
    ewifi_validation_t val;
    ewifi_validate_network(&s_networks[s_selected_net], s_networks, s_net_count, &val);

    char buf[128];
    if (val.safe_to_connect) {
        snprintf(buf, 128, "%s: SAFE [%d/100] — 0 red flags",
                 s_networks[s_selected_net].ssid, val.safety_score);
    } else {
        snprintf(buf, 128, "%s: UNSAFE [%d/100] — %d red flag(s)!",
                 s_networks[s_selected_net].ssid, val.safety_score,
                 val.flags_triggered);
    }
    show_toast(buf);
}

static void build_scan_tab(lv_obj_t *body) {
    const eapps_palette_t *p = eapps_theme_get_palette();

    char hdr[48];
    snprintf(hdr, 48, "%d networks found", s_net_count);
    lv_obj_t *h = lv_label_create(body);
    lv_label_set_text(h, hdr);
    lv_obj_set_style_text_color(h, hc(p->primary), 0);
    lv_obj_set_style_text_font(h, &lv_font_montserrat_14, 0);

    for (int i = 0; i < s_net_count; i++) {
        ewifi_network_t *n = &s_networks[i];
        int pct = ewifi_rssi_to_pct(n->rssi);

        lv_obj_t *card = eapps_card_create(body);
        lv_obj_set_style_pad_all(card, 8, 0);

        lv_obj_t *row1 = make_row(card);

        /* Signal bar */
        lv_obj_t *bar_bg = lv_obj_create(row1);
        lv_obj_set_size(bar_bg, 40, 12);
        lv_obj_set_style_bg_color(bar_bg, hc(p->surface), 0);
        lv_obj_set_style_bg_opa(bar_bg, LV_OPA_COVER, 0);
        lv_obj_set_style_radius(bar_bg, 4, 0);
        lv_obj_set_style_border_width(bar_bg, 0, 0);
        lv_obj_set_style_pad_all(bar_bg, 0, 0);

        lv_obj_t *bar_fg = lv_obj_create(bar_bg);
        int bar_w = (pct * 38) / 100;
        if (bar_w < 2) bar_w = 2;
        lv_obj_set_size(bar_fg, bar_w, 10);
        lv_obj_set_style_bg_color(bar_fg, hc(signal_color(n->rssi)), 0);
        lv_obj_set_style_bg_opa(bar_fg, LV_OPA_COVER, 0);
        lv_obj_set_style_radius(bar_fg, 3, 0);
        lv_obj_set_style_border_width(bar_fg, 0, 0);
        lv_obj_align(bar_fg, LV_ALIGN_LEFT_MID, 1, 0);

        /* SSID + details */
        lv_obj_t *ssid = lv_label_create(row1);
        char ssid_txt[64];
        snprintf(ssid_txt, 64, "%s%s", n->ssid, n->hidden ? " [H]" : "");
        lv_label_set_text(ssid, ssid_txt);
        lv_obj_set_style_text_color(ssid, hc(p->on_surface), 0);
        lv_obj_set_style_text_font(ssid, &lv_font_montserrat_12, 0);
        lv_obj_set_flex_grow(ssid, 1);

        /* RSSI */
        lv_obj_t *rssi_lbl = lv_label_create(row1);
        char rssi_txt[16];
        snprintf(rssi_txt, 16, "%d dBm", n->rssi);
        lv_label_set_text(rssi_lbl, rssi_txt);
        lv_obj_set_style_text_color(rssi_lbl, hc(signal_color(n->rssi)), 0);
        lv_obj_set_style_text_font(rssi_lbl, &lv_font_montserrat_12, 0);

        /* Row 2: details */
        lv_obj_t *row2 = make_row(card);
        lv_obj_t *det = lv_label_create(row2);
        char det_txt[96];
        snprintf(det_txt, 96, "%s | CH %d | %s | %s | %d MHz",
                 ewifi_security_str(n->security), n->channel,
                 ewifi_band_str(n->band), ewifi_standard_str(n->standard),
                 n->width_mhz);
        lv_label_set_text(det, det_txt);
        lv_obj_set_style_text_color(det, hc(p->on_surface), 0);
        lv_obj_set_style_text_opa(det, LV_OPA_60, 0);
        lv_obj_set_style_text_font(det, &lv_font_montserrat_12, 0);
        lv_label_set_long_mode(det, LV_LABEL_LONG_WRAP);
        lv_obj_set_width(det, LV_PCT(100));

        lv_obj_add_event_cb(card, net_click_cb, LV_EVENT_CLICKED, (void *)(intptr_t)i);
    }
}

/* ---- Build Channel Tab ---- */
static void build_channel_tab(lv_obj_t *body) {
    const eapps_palette_t *p = eapps_theme_get_palette();
    ewifi_channel_t channels[EWIFI_MAX_CHANNELS];
    int count = ewifi_channel_analysis(channels, EWIFI_MAX_CHANNELS);

    int best2g = ewifi_best_channel(EWIFI_BAND_2G);
    int best5g = ewifi_best_channel(EWIFI_BAND_5G);
    char rec[64];
    snprintf(rec, 64, "Best: 2.4GHz CH %d  |  5GHz CH %d", best2g, best5g);
    lv_obj_t *rec_lbl = lv_label_create(body);
    lv_label_set_text(rec_lbl, rec);
    lv_obj_set_style_text_color(rec_lbl, hc(0x00E676), 0);
    lv_obj_set_style_text_font(rec_lbl, &lv_font_montserrat_14, 0);

    /* 2.4 GHz section */
    lv_obj_t *card2g = eapps_card_create(body);
    lv_obj_t *t2g = lv_label_create(card2g);
    lv_label_set_text(t2g, LV_SYMBOL_WIFI "  2.4 GHz Channels");
    lv_obj_set_style_text_color(t2g, hc(p->primary), 0);
    lv_obj_set_style_text_font(t2g, &lv_font_montserrat_14, 0);

    lv_obj_t *chart_row = make_row(card2g);
    for (int i = 0; i < count; i++) {
        if (channels[i].band != EWIFI_BAND_2G) continue;
        lv_obj_t *col = lv_obj_create(chart_row);
        lv_obj_set_size(col, 22, 60);
        lv_obj_set_style_bg_opa(col, LV_OPA_TRANSP, 0);
        lv_obj_set_style_border_width(col, 0, 0);
        lv_obj_set_style_pad_all(col, 0, 0);
        lv_obj_set_flex_flow(col, LV_FLEX_FLOW_COLUMN);
        lv_obj_set_flex_align(col, LV_FLEX_ALIGN_END, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER);

        int bar_h = (channels[i].utilization_pct * 35) / 100;
        if (bar_h < 2) bar_h = 2;
        lv_obj_t *bar = lv_obj_create(col);
        lv_obj_set_size(bar, 16, bar_h);
        uint32_t bc = (channels[i].utilization_pct > 60) ? 0xF44336 :
                       (channels[i].utilization_pct > 30) ? 0xFFEB3B : 0x00E676;
        lv_obj_set_style_bg_color(bar, hc(bc), 0);
        lv_obj_set_style_bg_opa(bar, LV_OPA_COVER, 0);
        lv_obj_set_style_radius(bar, 3, 0);
        lv_obj_set_style_border_width(bar, 0, 0);

        lv_obj_t *ch_lbl = lv_label_create(col);
        char ch_txt[4];
        snprintf(ch_txt, 4, "%d", channels[i].number);
        lv_label_set_text(ch_lbl, ch_txt);
        lv_obj_set_style_text_font(ch_lbl, &lv_font_montserrat_12, 0);
        lv_obj_set_style_text_color(ch_lbl, hc(p->on_surface), 0);
    }

    /* 5 GHz section */
    lv_obj_t *card5g = eapps_card_create(body);
    lv_obj_t *t5g = lv_label_create(card5g);
    lv_label_set_text(t5g, LV_SYMBOL_WIFI "  5 GHz Channels");
    lv_obj_set_style_text_color(t5g, hc(p->primary), 0);
    lv_obj_set_style_text_font(t5g, &lv_font_montserrat_14, 0);

    lv_obj_t *list5g = eapps_list_create(card5g);
    for (int i = 0; i < count; i++) {
        if (channels[i].band != EWIFI_BAND_5G) continue;
        char key[16], val[32];
        snprintf(key, 16, "CH %d", channels[i].number);
        snprintf(val, 32, "%d nets | %d%%", channels[i].network_count,
                 channels[i].utilization_pct);
        eapps_list_item_create(list5g, NULL, key, val);
    }
}

/* ---- Build Security Tab ---- */
static void build_security_tab(lv_obj_t *body) {
    const eapps_palette_t *p = eapps_theme_get_palette();

    if (s_net_count == 0) return;
    ewifi_network_t *net = &s_networks[s_selected_net];

    ewifi_assessment_t assess;
    ewifi_assess_network(net, &assess);

    /* Header card */
    lv_obj_t *hdr_card = eapps_card_create(body);
    lv_obj_t *net_name = lv_label_create(hdr_card);
    char ntxt[64];
    snprintf(ntxt, 64, "%s  —  Score: %d/100", net->ssid, assess.score);
    lv_label_set_text(net_name, ntxt);
    lv_obj_set_style_text_color(net_name, hc(risk_color(assess.risk)), 0);
    lv_obj_set_style_text_font(net_name, &lv_font_montserrat_14, 0);

    static const char *risk_names[] = {"CRITICAL","HIGH","MEDIUM","LOW","SECURE"};
    lv_obj_t *risk_lbl = lv_label_create(hdr_card);
    char risk_txt[32];
    snprintf(risk_txt, 32, "Risk Level: %s", risk_names[assess.risk]);
    lv_label_set_text(risk_lbl, risk_txt);
    lv_obj_set_style_text_color(risk_lbl, hc(risk_color(assess.risk)), 0);

    /* 6 Red Flags Validation Report */
    ewifi_validation_t val;
    ewifi_validate_network(net, s_networks, s_net_count, &val);

    lv_obj_t *flags_card = eapps_card_create(body);
    lv_obj_set_style_pad_all(flags_card, 10, 0);
    lv_obj_t *flags_title = lv_label_create(flags_card);
    char ft[48];
    snprintf(ft, 48, "Pre-Connect Scan: %d/6 flags [%d/100]",
             val.flags_triggered, val.safety_score);
    lv_label_set_text(flags_title, ft);
    lv_obj_set_style_text_color(flags_title,
        val.safe_to_connect ? hc(0x00E676) : hc(0xF44336), 0);
    lv_obj_set_style_text_font(flags_title, &lv_font_montserrat_14, 0);

    for (int f = 0; f < EWIFI_FLAG_COUNT; f++) {
        lv_obj_t *fr = make_row(flags_card);
        lv_obj_t *fi = lv_label_create(fr);
        lv_label_set_text(fi, val.flags[f].triggered ? LV_SYMBOL_CLOSE : LV_SYMBOL_OK);
        lv_obj_set_style_text_color(fi,
            val.flags[f].triggered ? hc(0xF44336) : hc(0x00E676), 0);

        lv_obj_t *fn = lv_label_create(fr);
        lv_label_set_text(fn, val.flags[f].name);
        lv_obj_set_style_text_color(fn, hc(p->on_surface), 0);
        lv_obj_set_style_text_font(fn, &lv_font_montserrat_12, 0);

        if (val.flags[f].triggered && val.flags[f].detail) {
            lv_obj_t *fd = lv_label_create(flags_card);
            lv_label_set_text(fd, val.flags[f].detail);
            lv_label_set_long_mode(fd, LV_LABEL_LONG_WRAP);
            lv_obj_set_width(fd, LV_PCT(100));
            lv_obj_set_style_text_color(fd, hc(0xFF9800), 0);
            lv_obj_set_style_text_font(fd, &lv_font_montserrat_12, 0);

            if (val.flags[f].action) {
                lv_obj_t *fa = lv_label_create(flags_card);
                lv_label_set_text(fa, val.flags[f].action);
                lv_label_set_long_mode(fa, LV_LABEL_LONG_WRAP);
                lv_obj_set_width(fa, LV_PCT(100));
                lv_obj_set_style_text_color(fa, hc(0xF44336), 0);
                lv_obj_set_style_text_font(fa, &lv_font_montserrat_12, 0);
            }
        }
    }

    /* Findings */
    lv_obj_t *find_card = eapps_card_create(body);
    lv_obj_t *find_title = lv_label_create(find_card);
    lv_label_set_text(find_title, "Findings");
    lv_obj_set_style_text_color(find_title, hc(p->primary), 0);
    lv_obj_set_style_text_font(find_title, &lv_font_montserrat_14, 0);

    for (int i = 0; i < assess.finding_count; i++) {
        lv_obj_t *f = lv_label_create(find_card);
        char ftxt[128];
        snprintf(ftxt, 128, "  %s", assess.findings[i]);
        lv_label_set_text(f, ftxt);
        lv_label_set_long_mode(f, LV_LABEL_LONG_WRAP);
        lv_obj_set_width(f, LV_PCT(100));
        lv_obj_set_style_text_color(f, hc(p->on_surface), 0);
        lv_obj_set_style_text_font(f, &lv_font_montserrat_12, 0);
    }

    /* Recommendations */
    lv_obj_t *rec_card = eapps_card_create(body);
    lv_obj_t *rec_title = lv_label_create(rec_card);
    lv_label_set_text(rec_title, "Recommendations");
    lv_obj_set_style_text_color(rec_title, hc(0x00E676), 0);
    lv_obj_set_style_text_font(rec_title, &lv_font_montserrat_14, 0);

    for (int i = 0; i < assess.rec_count; i++) {
        lv_obj_t *r = lv_label_create(rec_card);
        char rtxt[128];
        snprintf(rtxt, 128, "  %s", assess.recommendations[i]);
        lv_label_set_text(r, rtxt);
        lv_label_set_long_mode(r, LV_LABEL_LONG_WRAP);
        lv_obj_set_width(r, LV_PCT(100));
        lv_obj_set_style_text_color(r, hc(p->on_surface), 0);
        lv_obj_set_style_text_font(r, &lv_font_montserrat_12, 0);
    }

    /* Hardening checklist */
    lv_obj_t *hard_card = eapps_card_create(body);
    lv_obj_t *hard_title = lv_label_create(hard_card);
    lv_label_set_text(hard_title, "Network Hardening Checklist");
    lv_obj_set_style_text_color(hard_title, hc(p->primary), 0);
    lv_obj_set_style_text_font(hard_title, &lv_font_montserrat_14, 0);

    static const char *checklist[] = {
        "Use WPA3-SAE if router supports it",
        "Random passphrase 15+ characters",
        "Disable WPS (Wi-Fi Protected Setup)",
        "Keep router firmware updated",
        "Use guest network for IoT devices",
        "Enable MAC address filtering",
        "Change default admin credentials",
        "Disable remote management",
    };
    for (int i = 0; i < 8; i++) {
        lv_obj_t *cl = lv_label_create(hard_card);
        char ctxt[96];
        snprintf(ctxt, 96, LV_SYMBOL_OK "  %s", checklist[i]);
        lv_label_set_text(cl, ctxt);
        lv_label_set_long_mode(cl, LV_LABEL_LONG_WRAP);
        lv_obj_set_width(cl, LV_PCT(100));
        lv_obj_set_style_text_color(cl, hc(p->on_surface), 0);
        lv_obj_set_style_text_font(cl, &lv_font_montserrat_12, 0);
    }
}

/* ---- Auto-Connect Callbacks ---- */
static void ac_toggle_cb(lv_event_t *e) {
    lv_obj_t *sw = lv_event_get_target(e);
    bool on = lv_obj_has_state(sw, LV_STATE_CHECKED);
    ewifi_ac_enable(&s_ac, on);
    if (on) {
        ewifi_ac_tick(&s_ac, &s_vault);
        char buf[64];
        snprintf(buf, 64, "Auto-Connect: %s", ewifi_ac_state_str(s_ac.state));
        show_toast(buf);
    } else {
        show_toast("Auto-Connect disabled");
    }
}

static void ac_reconnect_cb(lv_event_t *e) {
    (void)e;
    ewifi_ac_reconnect(&s_ac, &s_vault);
    char buf[64];
    snprintf(buf, 64, "Reconnect: %s → %s",
             s_ac.connected_ssid[0] ? s_ac.connected_ssid : "none",
             ewifi_ac_state_str(s_ac.state));
    show_toast(buf);
}

static void ac_prefer5g_cb(lv_event_t *e) {
    lv_obj_t *sw = lv_event_get_target(e);
    s_ac.prefer_5ghz = lv_obj_has_state(sw, LV_STATE_CHECKED);
    show_toast(s_ac.prefer_5ghz ? "Prefer 5 GHz ON" : "Prefer 5 GHz OFF");
}

static void ac_autorecon_cb(lv_event_t *e) {
    lv_obj_t *sw = lv_event_get_target(e);
    s_ac.auto_reconnect = lv_obj_has_state(sw, LV_STATE_CHECKED);
    show_toast(s_ac.auto_reconnect ? "Auto-Reconnect ON" : "Auto-Reconnect OFF");
}

static void ac_smartfree_cb(lv_event_t *e) {
    lv_obj_t *sw = lv_event_get_target(e);
    s_ac.smart_free_wifi = lv_obj_has_state(sw, LV_STATE_CHECKED);
    if (s_ac.smart_free_wifi) {
        int r = ewifi_smart_free_connect(&s_ac);
        char buf[64];
        snprintf(buf, 64, "Smart Free WiFi: %s",
                 r ? s_ac.connected_ssid : "no safe network found");
        show_toast(buf);
    } else {
        show_toast("Smart Free WiFi OFF");
    }
}

static void ac_speedswitch_cb(lv_event_t *e) {
    lv_obj_t *sw = lv_event_get_target(e);
    s_ac.speed_auto_switch = lv_obj_has_state(sw, LV_STATE_CHECKED);
    if (s_ac.speed_auto_switch) {
        bool ok = ewifi_switch_to_fastest(&s_ac, &s_vault);
        char buf[64];
        snprintf(buf, 64, "Speed Switch: %s",
                 ok ? s_ac.connected_ssid : "failed");
        show_toast(buf);
        rebuild_content();
    } else {
        show_toast("Speed Auto-Switch OFF");
    }
}

static void speed_test_all_cb(lv_event_t *e) {
    (void)e;
    ewifi_net_ranking_t rankings[EWIFI_MAX_NETWORKS];
    int count = ewifi_speed_rank_all(rankings, EWIFI_MAX_NETWORKS);
    if (count > 0) {
        char buf[96];
        snprintf(buf, 96, "Fastest: %s (%.0f Mbps, %.0fms) Score: %.0f",
                 rankings[0].ssid, rankings[0].download_mbps,
                 rankings[0].latency_ms, rankings[0].overall_score);
        show_toast(buf);
    } else {
        show_toast("No networks to test");
    }
    rebuild_content();
}

static void vault_import_cb(lv_event_t *e) {
    (void)e;
    if (ewifi_vault_import_os(&s_vault)) {
        char buf[32];
        snprintf(buf, 32, "Vault: %d entries", s_vault.count);
        show_toast(buf);
        rebuild_content();
    } else {
        show_toast("No new passwords to import");
    }
}

/* ---- Build Passwords Tab ---- */
static void build_passwords_tab(lv_obj_t *body) {
    const eapps_palette_t *p = eapps_theme_get_palette();

    lv_obj_t *title = lv_label_create(body);
    lv_label_set_text(title, LV_SYMBOL_EYE_OPEN "  Saved WiFi Passwords");
    lv_obj_set_style_text_color(title, hc(p->primary), 0);
    lv_obj_set_style_text_font(title, &lv_font_montserrat_14, 0);

    lv_obj_t *note = lv_label_create(body);
    lv_label_set_text(note, "Extracts passwords from your own OS storage.\n"
                            "Windows: netsh | Linux: nmcli | macOS: keychain");
    lv_label_set_long_mode(note, LV_LABEL_LONG_WRAP);
    lv_obj_set_width(note, LV_PCT(100));
    lv_obj_set_style_text_color(note, hc(p->on_surface), 0);
    lv_obj_set_style_text_opa(note, LV_OPA_60, 0);
    lv_obj_set_style_text_font(note, &lv_font_montserrat_12, 0);

    ewifi_saved_cred_t creds[EWIFI_MAX_SAVED];
    int count = ewifi_extract_saved_passwords(creds, EWIFI_MAX_SAVED);

    if (count == 0) {
        lv_obj_t *empty = lv_label_create(body);
        lv_label_set_text(empty, "No saved networks found.\n"
                                  "Run as admin for full access.");
        lv_obj_set_style_text_color(empty, hc(0xFF9800), 0);
        return;
    }

    char hdr[32];
    snprintf(hdr, 32, "%d saved networks", count);
    lv_obj_t *h = lv_label_create(body);
    lv_label_set_text(h, hdr);
    lv_obj_set_style_text_color(h, hc(0x00E676), 0);

    for (int i = 0; i < count; i++) {
        lv_obj_t *card = eapps_card_create(body);
        lv_obj_set_style_pad_all(card, 10, 0);

        /* SSID + auth type */
        lv_obj_t *row1 = make_row(card);
        lv_obj_t *ssid = lv_label_create(row1);
        lv_label_set_text(ssid, creds[i].ssid);
        lv_obj_set_style_text_color(ssid, hc(p->on_surface), 0);
        lv_obj_set_style_text_font(ssid, &lv_font_montserrat_14, 0);
        lv_obj_set_flex_grow(ssid, 1);

        lv_obj_t *auth = lv_label_create(row1);
        lv_label_set_text(auth, creds[i].auth_type);
        lv_obj_set_style_text_color(auth, hc(p->primary), 0);
        lv_obj_set_style_text_font(auth, &lv_font_montserrat_12, 0);

        /* Password */
        lv_obj_t *pass_row = make_row(card);
        lv_obj_t *key_icon = lv_label_create(pass_row);
        if (creds[i].password_found) {
            lv_label_set_text(key_icon, LV_SYMBOL_OK);
            lv_obj_set_style_text_color(key_icon, hc(0x00E676), 0);
        } else {
            lv_label_set_text(key_icon, LV_SYMBOL_CLOSE);
            lv_obj_set_style_text_color(key_icon, hc(0xF44336), 0);
        }

        lv_obj_t *pass = lv_label_create(pass_row);
        if (creds[i].password_found) {
            lv_label_set_text(pass, creds[i].password);
            lv_obj_set_style_text_color(pass, hc(0x00E676), 0);
        } else {
            lv_label_set_text(pass, "(not available — run as admin)");
            lv_obj_set_style_text_color(pass, hc(p->on_surface), 0);
            lv_obj_set_style_text_opa(pass, LV_OPA_40, 0);
        }
        lv_obj_set_style_text_font(pass, &lv_font_montserrat_12, 0);

        /* Security info */
        if (strlen(creds[i].security) > 0) {
            lv_obj_t *sec = lv_label_create(card);
            char stxt[48];
            snprintf(stxt, 48, "Cipher: %s", creds[i].security);
            lv_label_set_text(sec, stxt);
            lv_obj_set_style_text_color(sec, hc(p->on_surface), 0);
            lv_obj_set_style_text_opa(sec, LV_OPA_50, 0);
            lv_obj_set_style_text_font(sec, &lv_font_montserrat_12, 0);
        }
    }

    /* Import from OS button */
    lv_obj_t *imp_row = make_row(body);
    lv_obj_t *imp_btn = lv_button_create(imp_row);
    lv_obj_set_size(imp_btn, LV_SIZE_CONTENT, 36);
    lv_obj_set_style_bg_color(imp_btn, hc(p->primary), 0);
    lv_obj_set_style_radius(imp_btn, 8, 0);
    lv_obj_t *imp_lbl = lv_label_create(imp_btn);
    lv_label_set_text(imp_lbl, LV_SYMBOL_DOWNLOAD " Import from OS");
    lv_obj_set_style_text_color(imp_lbl, hc(p->on_primary), 0);
    lv_obj_center(imp_lbl);
    lv_obj_add_event_cb(imp_btn, vault_import_cb, LV_EVENT_CLICKED, NULL);

    /* ---- Auto-Connect Section ---- */
    lv_obj_t *ac_card = eapps_card_create(body);
    lv_obj_set_style_pad_all(ac_card, 10, 0);

    lv_obj_t *ac_title = lv_label_create(ac_card);
    lv_label_set_text(ac_title, LV_SYMBOL_REFRESH "  Auto-Connect");
    lv_obj_set_style_text_color(ac_title, hc(p->primary), 0);
    lv_obj_set_style_text_font(ac_title, &lv_font_montserrat_14, 0);

    /* Status */
    lv_obj_t *ac_status_row = make_row(ac_card);
    lv_obj_t *ac_st = lv_label_create(ac_status_row);
    char st_buf[64];
    snprintf(st_buf, 64, "Status: %s", ewifi_ac_state_str(s_ac.state));
    lv_label_set_text(ac_st, st_buf);
    lv_obj_set_style_text_color(ac_st, hc(p->on_surface), 0);
    if (s_ac.connected_ssid[0]) {
        lv_obj_t *ac_conn = lv_label_create(ac_status_row);
        char conn_buf[48];
        snprintf(conn_buf, 48, " → %s", s_ac.connected_ssid);
        lv_label_set_text(ac_conn, conn_buf);
        lv_obj_set_style_text_color(ac_conn, hc(0x00E676), 0);
    }

    /* Enable toggle */
    lv_obj_t *en_row = make_row(ac_card);
    lv_obj_set_flex_align(en_row, LV_FLEX_ALIGN_SPACE_BETWEEN,
                          LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER);
    lv_obj_t *en_lbl = lv_label_create(en_row);
    lv_label_set_text(en_lbl, "Enable Auto-Connect");
    lv_obj_set_style_text_color(en_lbl, hc(p->on_surface), 0);
    lv_obj_t *en_sw = lv_switch_create(en_row);
    lv_obj_set_size(en_sw, 44, 24);
    if (s_ac.enabled) lv_obj_add_state(en_sw, LV_STATE_CHECKED);
    lv_obj_add_event_cb(en_sw, ac_toggle_cb, LV_EVENT_VALUE_CHANGED, NULL);

    /* Prefer 5 GHz */
    lv_obj_t *p5_row = make_row(ac_card);
    lv_obj_set_flex_align(p5_row, LV_FLEX_ALIGN_SPACE_BETWEEN,
                          LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER);
    lv_obj_t *p5_lbl = lv_label_create(p5_row);
    lv_label_set_text(p5_lbl, "Prefer 5 GHz");
    lv_obj_set_style_text_color(p5_lbl, hc(p->on_surface), 0);
    lv_obj_t *p5_sw = lv_switch_create(p5_row);
    lv_obj_set_size(p5_sw, 44, 24);
    if (s_ac.prefer_5ghz) lv_obj_add_state(p5_sw, LV_STATE_CHECKED);
    lv_obj_add_event_cb(p5_sw, ac_prefer5g_cb, LV_EVENT_VALUE_CHANGED, NULL);

    /* Auto-Reconnect */
    lv_obj_t *ar_row = make_row(ac_card);
    lv_obj_set_flex_align(ar_row, LV_FLEX_ALIGN_SPACE_BETWEEN,
                          LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER);
    lv_obj_t *ar_lbl = lv_label_create(ar_row);
    lv_label_set_text(ar_lbl, "Auto-Reconnect on Drop");
    lv_obj_set_style_text_color(ar_lbl, hc(p->on_surface), 0);
    lv_obj_t *ar_sw = lv_switch_create(ar_row);
    lv_obj_set_size(ar_sw, 44, 24);
    if (s_ac.auto_reconnect) lv_obj_add_state(ar_sw, LV_STATE_CHECKED);
    lv_obj_add_event_cb(ar_sw, ac_autorecon_cb, LV_EVENT_VALUE_CHANGED, NULL);

    /* Smart Free WiFi */
    lv_obj_t *sf_row = make_row(ac_card);
    lv_obj_set_flex_align(sf_row, LV_FLEX_ALIGN_SPACE_BETWEEN,
                          LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER);
    lv_obj_t *sf_lbl = lv_label_create(sf_row);
    lv_label_set_text(sf_lbl, LV_SYMBOL_WIFI " Smart Free WiFi");
    lv_obj_set_style_text_color(sf_lbl, hc(p->on_surface), 0);
    lv_obj_t *sf_sw = lv_switch_create(sf_row);
    lv_obj_set_size(sf_sw, 44, 24);
    if (s_ac.smart_free_wifi) lv_obj_add_state(sf_sw, LV_STATE_CHECKED);
    lv_obj_add_event_cb(sf_sw, ac_smartfree_cb, LV_EVENT_VALUE_CHANGED, NULL);

    lv_obj_t *sf_note = lv_label_create(ac_card);
    lv_label_set_text(sf_note, "Auto-connects to free WiFi only if safe:\n"
                               "no evil twins, WPA2+, good signal, no WEP");
    lv_label_set_long_mode(sf_note, LV_LABEL_LONG_WRAP);
    lv_obj_set_width(sf_note, LV_PCT(100));
    lv_obj_set_style_text_color(sf_note, hc(p->on_surface), 0);
    lv_obj_set_style_text_opa(sf_note, LV_OPA_40, 0);
    lv_obj_set_style_text_font(sf_note, &lv_font_montserrat_12, 0);

    /* Speed Auto-Switch */
    lv_obj_t *ss_row = make_row(ac_card);
    lv_obj_set_flex_align(ss_row, LV_FLEX_ALIGN_SPACE_BETWEEN,
                          LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER);
    lv_obj_t *ss_lbl = lv_label_create(ss_row);
    lv_label_set_text(ss_lbl, LV_SYMBOL_CHARGE " Speed Auto-Switch");
    lv_obj_set_style_text_color(ss_lbl, hc(p->on_surface), 0);
    lv_obj_t *ss_sw = lv_switch_create(ss_row);
    lv_obj_set_size(ss_sw, 44, 24);
    if (s_ac.speed_auto_switch) lv_obj_add_state(ss_sw, LV_STATE_CHECKED);
    lv_obj_add_event_cb(ss_sw, ac_speedswitch_cb, LV_EVENT_VALUE_CHANGED, NULL);

    lv_obj_t *ss_note = lv_label_create(ac_card);
    lv_label_set_text(ss_note, "Tests all WiFi speeds, auto-switches to fastest.\n"
                               "Score = download×0.5 + latency×0.3 + signal×0.2");
    lv_label_set_long_mode(ss_note, LV_LABEL_LONG_WRAP);
    lv_obj_set_width(ss_note, LV_PCT(100));
    lv_obj_set_style_text_color(ss_note, hc(p->on_surface), 0);
    lv_obj_set_style_text_opa(ss_note, LV_OPA_40, 0);
    lv_obj_set_style_text_font(ss_note, &lv_font_montserrat_12, 0);

    /* Test All Speeds button */
    lv_obj_t *ts_row = make_row(ac_card);
    lv_obj_t *ts_btn = lv_button_create(ts_row);
    lv_obj_set_size(ts_btn, LV_SIZE_CONTENT, 36);
    lv_obj_set_style_bg_color(ts_btn, hc(0x00BFA5), 0);
    lv_obj_set_style_radius(ts_btn, 8, 0);
    lv_obj_t *ts_lbl = lv_label_create(ts_btn);
    lv_label_set_text(ts_lbl, LV_SYMBOL_CHARGE " Test All & Switch to Fastest");
    lv_obj_set_style_text_color(ts_lbl, hc(0xFFFFFF), 0);
    lv_obj_center(ts_lbl);
    lv_obj_add_event_cb(ts_btn, speed_test_all_cb, LV_EVENT_CLICKED, NULL);

    /* Speed Rankings (if available) */
    ewifi_net_ranking_t ranks[EWIFI_MAX_NETWORKS];
    int rank_count = ewifi_speed_rank_all(ranks, EWIFI_MAX_NETWORKS);
    if (rank_count > 0) {
        lv_obj_t *rank_title = lv_label_create(ac_card);
        lv_label_set_text(rank_title, "Speed Rankings:");
        lv_obj_set_style_text_color(rank_title, hc(p->primary), 0);
        lv_obj_set_style_text_font(rank_title, &lv_font_montserrat_12, 0);

        for (int r = 0; r < rank_count && r < 5; r++) {
            lv_obj_t *rr = make_row(ac_card);
            lv_obj_t *rl = lv_label_create(rr);
            char rbuf[96];
            snprintf(rbuf, 96, "#%d %s%s — %.0f Mbps, %.0fms  [%.0f]",
                     r + 1, ranks[r].ssid,
                     ranks[r].is_safe ? " " LV_SYMBOL_OK : " " LV_SYMBOL_CLOSE,
                     ranks[r].download_mbps, ranks[r].latency_ms,
                     ranks[r].overall_score);
            lv_label_set_text(rl, rbuf);
            lv_label_set_long_mode(rl, LV_LABEL_LONG_WRAP);
            lv_obj_set_width(rl, LV_PCT(100));
            lv_obj_set_style_text_color(rl,
                ranks[r].is_safe ? hc(0x00E676) : hc(0xFF9800), 0);
            lv_obj_set_style_text_font(rl, &lv_font_montserrat_12, 0);
        }
    }

    /* Reconnect Now button */
    lv_obj_t *rc_row = make_row(ac_card);
    lv_obj_t *rc_btn = lv_button_create(rc_row);
    lv_obj_set_size(rc_btn, LV_SIZE_CONTENT, 36);
    lv_obj_set_style_bg_color(rc_btn, hc(0xFF9800), 0);
    lv_obj_set_style_radius(rc_btn, 8, 0);
    lv_obj_t *rc_lbl = lv_label_create(rc_btn);
    lv_label_set_text(rc_lbl, LV_SYMBOL_REFRESH " Disconnect & Reconnect");
    lv_obj_set_style_text_color(rc_lbl, hc(0xFFFFFF), 0);
    lv_obj_center(rc_lbl);
    lv_obj_add_event_cb(rc_btn, ac_reconnect_cb, LV_EVENT_CLICKED, NULL);

    /* Vault count */
    lv_obj_t *vault_info = lv_label_create(ac_card);
    char vbuf[48];
    snprintf(vbuf, 48, "Vault: %d saved | Retries: %d/%d",
             s_vault.count, s_ac.retry_count, s_ac.max_retries);
    lv_label_set_text(vault_info, vbuf);
    lv_obj_set_style_text_color(vault_info, hc(p->on_surface), 0);
    lv_obj_set_style_text_opa(vault_info, LV_OPA_50, 0);
    lv_obj_set_style_text_font(vault_info, &lv_font_montserrat_12, 0);
}

/* ---- Tab Rebuild ---- */
static void rebuild_content(void) {
    if (!s_root) return;
    if (s_content) { lv_obj_delete(s_content); s_content = NULL; }

    lv_obj_t *body = lv_obj_get_child(s_root, 1);
    if (!body) return;

    s_content = lv_obj_create(body);
    lv_obj_set_size(s_content, LV_PCT(100), LV_SIZE_CONTENT);
    lv_obj_set_flex_grow(s_content, 1);
    lv_obj_set_style_bg_opa(s_content, LV_OPA_TRANSP, 0);
    lv_obj_set_style_border_width(s_content, 0, 0);
    lv_obj_set_style_pad_all(s_content, 4, 0);
    lv_obj_set_style_pad_gap(s_content, 6, 0);
    lv_obj_set_flex_flow(s_content, LV_FLEX_FLOW_COLUMN);
    lv_obj_add_flag(s_content, LV_OBJ_FLAG_SCROLLABLE);

    switch (s_active_tab) {
    case TAB_SCAN:      build_scan_tab(s_content); break;
    case TAB_CHANNELS:  build_channel_tab(s_content); break;
    case TAB_PASSWORDS: build_passwords_tab(s_content); break;
    case TAB_SECURITY:  build_security_tab(s_content); break;
    }
}

/* ---- Bottom Nav ---- */
static void nav_cb(lv_event_t *e) {
    intptr_t t = (intptr_t)lv_event_get_user_data(e);
    s_active_tab = (ewifi_tab_t)t;
    rebuild_content();
}

static void build_nav(lv_obj_t *parent) {
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

    static const char *icons[] = {LV_SYMBOL_WIFI, LV_SYMBOL_CHARGE, LV_SYMBOL_EYE_OPEN, LV_SYMBOL_SETTINGS};
    static const char *labels[] = {"Scan", "Channels", "Passwords", "Security"};

    for (int i = 0; i < 4; i++) {
        bool active = (i == (int)s_active_tab);
        lv_obj_t *btn = lv_button_create(s_nav_bar);
        lv_obj_set_size(btn, LV_SIZE_CONTENT, 40);
        lv_obj_set_style_bg_opa(btn, LV_OPA_TRANSP, 0);
        lv_obj_set_style_shadow_width(btn, 0, 0);
        lv_obj_set_style_pad_hor(btn, 8, 0);
        lv_obj_set_flex_flow(btn, LV_FLEX_FLOW_COLUMN);
        lv_obj_set_flex_align(btn, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER);

        lv_obj_t *ico = lv_label_create(btn);
        lv_label_set_text(ico, icons[i]);
        lv_obj_set_style_text_color(ico, active ? hc(p->primary) : hc(p->on_surface), 0);

        lv_obj_t *lbl = lv_label_create(btn);
        lv_label_set_text(lbl, labels[i]);
        lv_obj_set_style_text_font(lbl, &lv_font_montserrat_12, 0);
        lv_obj_set_style_text_color(lbl, active ? hc(p->primary) : hc(p->on_surface), 0);
        lv_obj_set_style_text_opa(lbl, active ? LV_OPA_COVER : LV_OPA_60, 0);

        lv_obj_add_event_cb(btn, nav_cb, LV_EVENT_CLICKED, (void *)(intptr_t)i);
    }
}

/* ---- Lifecycle ---- */
static bool ewifi_init(lv_obj_t *parent) {
    const eapps_palette_t *p = eapps_theme_get_palette();

    ewifi_engine_init();
    ewifi_vault_init(&s_vault);
    ewifi_ac_init(&s_ac);
    ewifi_vault_import_os(&s_vault);
    s_net_count = ewifi_scan(s_networks, EWIFI_MAX_NETWORKS);
    s_active_tab = TAB_SCAN;
    s_selected_net = 0;

    s_root = eapps_scaffold_create(parent, "eWiFi", false);
    lv_obj_t *body = lv_obj_get_child(s_root, 1);
    lv_obj_set_flex_flow(body, LV_FLEX_FLOW_COLUMN);
    lv_obj_set_style_pad_all(body, 4, 0);
    lv_obj_set_style_pad_gap(body, 4, 0);

    s_status_lbl = lv_label_create(body);
    lv_label_set_text(s_status_lbl, "WiFi Analyzer ready");
    lv_obj_set_style_text_color(s_status_lbl, hc(p->primary), 0);
    lv_obj_set_style_text_font(s_status_lbl, &lv_font_montserrat_12, 0);
    lv_obj_set_width(s_status_lbl, LV_PCT(100));
    lv_obj_set_style_text_align(s_status_lbl, LV_TEXT_ALIGN_CENTER, 0);

    rebuild_content();
    build_nav(body);
    return true;
}

static void ewifi_deinit(void) {
    s_root = NULL; s_status_lbl = NULL; s_content = NULL; s_nav_bar = NULL;
    s_net_count = 0; s_selected_net = 0;
}
static void ewifi_on_show(void) {}
static void ewifi_on_hide(void) {}

const eapps_app_info_t ewifi_info = {
    .id = "ewifi", .name = "eWiFi", .icon = LV_SYMBOL_WIFI,
    .description = "WiFi analyzer & network security education",
    .category = EAPPS_CAT_CONNECTIVITY, .version = "1.0.0",
};
const eapps_app_lifecycle_t ewifi_lifecycle = {
    .init = ewifi_init, .deinit = ewifi_deinit,
    .on_show = ewifi_on_show, .on_hide = ewifi_on_hide,
};
