// SPDX-License-Identifier: MIT
#include "suite.h"
#include "eapps/registry.h"
#include "eapps/theme.h"
#include "eapps/widgets.h"
#include "eapps/version.h"
#include "lvgl.h"
#include <string.h>
#include <stdbool.h>

/* Import all app infos and lifecycles */
#ifdef EAPPS_BUILD_PRODUCTIVITY
extern const eapps_app_info_t ecal_info;       extern const eapps_app_lifecycle_t ecal_lifecycle;
extern const eapps_app_info_t enote_info;      extern const eapps_app_lifecycle_t enote_lifecycle;
extern const eapps_app_info_t econverter_info; extern const eapps_app_lifecycle_t econverter_lifecycle;
extern const eapps_app_info_t ebuffer_info;    extern const eapps_app_lifecycle_t ebuffer_lifecycle;
extern const eapps_app_info_t efiles_info;     extern const eapps_app_lifecycle_t efiles_lifecycle;
extern const eapps_app_info_t ecleaner_info;   extern const eapps_app_lifecycle_t ecleaner_lifecycle;
extern const eapps_app_info_t eclock_info;     extern const eapps_app_lifecycle_t eclock_lifecycle;
extern const eapps_app_info_t etools_info;     extern const eapps_app_lifecycle_t etools_lifecycle;
extern const eapps_app_info_t etimer_info;     extern const eapps_app_lifecycle_t etimer_lifecycle;
extern const eapps_app_info_t epdf_info;       extern const eapps_app_lifecycle_t epdf_lifecycle;
extern const eapps_app_info_t ezip_info;       extern const eapps_app_lifecycle_t ezip_lifecycle;
extern const eapps_app_info_t eviewer_info;    extern const eapps_app_lifecycle_t eviewer_lifecycle;
extern const eapps_app_info_t esession_info;   extern const eapps_app_lifecycle_t esession_lifecycle;
#endif

#ifdef EAPPS_BUILD_MEDIA
extern const eapps_app_info_t emusic_info;   extern const eapps_app_lifecycle_t emusic_lifecycle;
extern const eapps_app_info_t evideo_info;   extern const eapps_app_lifecycle_t evideo_lifecycle;
extern const eapps_app_info_t egallery_info; extern const eapps_app_lifecycle_t egallery_lifecycle;
extern const eapps_app_info_t eplay_info;    extern const eapps_app_lifecycle_t eplay_lifecycle;
extern const eapps_app_info_t epaint_info;   extern const eapps_app_lifecycle_t epaint_lifecycle;
#endif

#ifdef EAPPS_BUILD_GAMES
extern const eapps_app_info_t snake_info;       extern const eapps_app_lifecycle_t snake_lifecycle;
extern const eapps_app_info_t tetris_info;      extern const eapps_app_lifecycle_t tetris_lifecycle;
extern const eapps_app_info_t minesweeper_info; extern const eapps_app_lifecycle_t minesweeper_lifecycle;
extern const eapps_app_info_t dice_info;        extern const eapps_app_lifecycle_t dice_lifecycle;
extern const eapps_app_info_t erunner_info;     extern const eapps_app_lifecycle_t erunner_lifecycle;
extern const eapps_app_info_t esurfer_info;     extern const eapps_app_lifecycle_t esurfer_lifecycle;
extern const eapps_app_info_t echess_info;      extern const eapps_app_lifecycle_t echess_lifecycle;
extern const eapps_app_info_t ebirds_info;      extern const eapps_app_lifecycle_t ebirds_lifecycle;
extern const eapps_app_info_t eslice_info;      extern const eapps_app_lifecycle_t eslice_lifecycle;
extern const eapps_app_info_t eblocks_info;     extern const eapps_app_lifecycle_t eblocks_lifecycle;
extern const eapps_app_info_t ecrush_info;      extern const eapps_app_lifecycle_t ecrush_lifecycle;
#endif

#ifdef EAPPS_BUILD_CONNECTIVITY
extern const eapps_app_info_t eftp_info;    extern const eapps_app_lifecycle_t eftp_lifecycle;
extern const eapps_app_info_t eserial_info; extern const eapps_app_lifecycle_t eserial_lifecycle;
extern const eapps_app_info_t essh_info;    extern const eapps_app_lifecycle_t essh_lifecycle;
extern const eapps_app_info_t evnc_info;    extern const eapps_app_lifecycle_t evnc_lifecycle;
extern const eapps_app_info_t etunnel_info; extern const eapps_app_lifecycle_t etunnel_lifecycle;
extern const eapps_app_info_t echat_info;   extern const eapps_app_lifecycle_t echat_lifecycle;
extern const eapps_app_info_t eremote_info; extern const eapps_app_lifecycle_t eremote_lifecycle;
extern const eapps_app_info_t ewifi_info;   extern const eapps_app_lifecycle_t ewifi_lifecycle;
#endif

#ifdef EAPPS_BUILD_SECURITY
extern const eapps_app_info_t evpn_info;        extern const eapps_app_lifecycle_t evpn_lifecycle;
extern const eapps_app_info_t eguard_info;      extern const eapps_app_lifecycle_t eguard_lifecycle;
extern const eapps_app_info_t evirustower_info; extern const eapps_app_lifecycle_t evirustower_lifecycle;
#endif

#ifdef EAPPS_BUILD_WEB
extern const eapps_app_info_t eweb_info; extern const eapps_app_lifecycle_t eweb_lifecycle;
#endif

#define REG(app) eapps_registry_register(&app##_info, &app##_lifecycle)

void suite_register_all_apps(void) {
#ifdef EAPPS_BUILD_PRODUCTIVITY
    REG(ecal); REG(enote); REG(econverter); REG(ebuffer);
    REG(efiles); REG(ecleaner); REG(eclock); REG(etools);
    REG(etimer); REG(epdf); REG(ezip); REG(eviewer); REG(esession);
#endif
#ifdef EAPPS_BUILD_MEDIA
    REG(emusic); REG(evideo); REG(egallery); REG(eplay); REG(epaint);
#endif
#ifdef EAPPS_BUILD_GAMES
    REG(snake); REG(tetris); REG(minesweeper); REG(dice);
    REG(erunner); REG(esurfer); REG(echess); REG(ebirds);
    REG(eslice); REG(eblocks); REG(ecrush);
#endif
#ifdef EAPPS_BUILD_CONNECTIVITY
    REG(eftp); REG(eserial); REG(essh); REG(evnc); REG(etunnel); REG(echat); REG(eremote); REG(ewifi);
#endif
#ifdef EAPPS_BUILD_SECURITY
    REG(evpn); REG(eguard); REG(evirustower);
#endif
#ifdef EAPPS_BUILD_WEB
    REG(eweb);
#endif
}

/* ---- Launcher State ---- */

static lv_obj_t *s_main_screen  = NULL;
static lv_obj_t *s_grid_cont    = NULL;
static lv_obj_t *s_app_cont     = NULL;
static lv_obj_t *s_topbar       = NULL;
static lv_obj_t *s_cat_tabs     = NULL;
static const char *s_current_app_id = NULL;
static eapps_category_t s_active_cat = EAPPS_CAT_PRODUCTIVITY;

static lv_color_t hex_color(uint32_t hex)
{
    return lv_color_make((hex >> 16) & 0xFF, (hex >> 8) & 0xFF, hex & 0xFF);
}

/* ---- App Card ---- */

typedef struct {
    const char *app_id;
} app_card_data_t;

static void app_card_click_cb(lv_event_t *e)
{
    const app_card_data_t *d = (const app_card_data_t *)lv_event_get_user_data(e);
    if (!d || !d->app_id) return;

    const eapps_app_lifecycle_t *lc = eapps_registry_get_lifecycle(d->app_id);
    if (!lc || !lc->init) return;

    s_current_app_id = d->app_id;

    if (s_grid_cont) lv_obj_add_flag(s_grid_cont, LV_OBJ_FLAG_HIDDEN);
    if (s_cat_tabs)  lv_obj_add_flag(s_cat_tabs, LV_OBJ_FLAG_HIDDEN);

    s_app_cont = lv_obj_create(s_main_screen);
    lv_obj_set_size(s_app_cont, LV_PCT(100), LV_PCT(100));
    lv_obj_set_style_bg_opa(s_app_cont, LV_OPA_TRANSP, 0);
    lv_obj_set_style_border_width(s_app_cont, 0, 0);
    lv_obj_set_style_pad_all(s_app_cont, 0, 0);

    lc->init(s_app_cont);
    if (lc->on_show) lc->on_show();

    const eapps_registry_entry_t *entry = eapps_registry_find(d->app_id);
    if (entry && s_topbar) {
        lv_obj_t *title = lv_obj_get_child(s_topbar, 1);
        if (title) lv_label_set_text(title, entry->info.name);
    }
}

static void create_app_card(lv_obj_t *grid, const eapps_registry_entry_t *e)
{
    const eapps_palette_t *p = eapps_theme_get_palette();

    lv_obj_t *card = lv_obj_create(grid);
    lv_obj_set_size(card, 110, 100);
    lv_obj_set_style_bg_color(card, hex_color(p->card), 0);
    lv_obj_set_style_bg_opa(card, LV_OPA_COVER, 0);
    lv_obj_set_style_radius(card, 12, 0);
    lv_obj_set_style_border_color(card, hex_color(p->border), 0);
    lv_obj_set_style_border_width(card, 1, 0);
    lv_obj_set_style_pad_all(card, 8, 0);
    lv_obj_set_flex_flow(card, LV_FLEX_FLOW_COLUMN);
    lv_obj_set_flex_align(card, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER,
                          LV_FLEX_ALIGN_CENTER);
    lv_obj_set_style_shadow_width(card, 4, 0);
    lv_obj_set_style_shadow_opa(card, LV_OPA_10, 0);

    lv_obj_t *icon_bg = lv_obj_create(card);
    lv_obj_set_size(icon_bg, 40, 40);
    lv_obj_set_style_bg_color(icon_bg, hex_color(p->primary), 0);
    lv_obj_set_style_bg_opa(icon_bg, LV_OPA_20, 0);
    lv_obj_set_style_radius(icon_bg, 10, 0);
    lv_obj_set_style_border_width(icon_bg, 0, 0);

    lv_obj_t *ico = lv_label_create(icon_bg);
    lv_label_set_text(ico, e->info.icon ? e->info.icon : "?");
    lv_obj_set_style_text_color(ico, hex_color(p->primary), 0);
    lv_obj_center(ico);

    lv_obj_t *name = lv_label_create(card);
    lv_label_set_text(name, e->info.name);
    lv_label_set_long_mode(name, LV_LABEL_LONG_DOT);
    lv_obj_set_width(name, 90);
    lv_obj_set_style_text_align(name, LV_TEXT_ALIGN_CENTER, 0);
    lv_obj_set_style_text_color(name, hex_color(p->on_surface), 0);
    lv_obj_set_style_text_font(name, &lv_font_montserrat_12, 0);

    static app_card_data_t card_data[EAPPS_MAX_APPS];
    static int card_idx = 0;
    if (card_idx < EAPPS_MAX_APPS) {
        card_data[card_idx].app_id = e->info.id;
        lv_obj_add_event_cb(card, app_card_click_cb, LV_EVENT_CLICKED,
                            &card_data[card_idx]);
        card_idx++;
    }
}

/* ---- Category Tabs ---- */

static void rebuild_grid(void);

static void cat_tab_click_cb(lv_event_t *e)
{
    eapps_category_t cat = (eapps_category_t)(intptr_t)lv_event_get_user_data(e);
    s_active_cat = cat;
    rebuild_grid();
}

static lv_obj_t *create_cat_tabs(lv_obj_t *parent)
{
    const eapps_palette_t *p = eapps_theme_get_palette();
    static const char *cat_names[] = {
        "All", "Productivity", "Media", "Games", "Connect", "Security"
    };

    lv_obj_t *bar = lv_obj_create(parent);
    lv_obj_set_size(bar, LV_PCT(100), 36);
    lv_obj_set_style_bg_opa(bar, LV_OPA_TRANSP, 0);
    lv_obj_set_style_border_width(bar, 0, 0);
    lv_obj_set_style_pad_all(bar, 0, 0);
    lv_obj_set_style_pad_gap(bar, 4, 0);
    lv_obj_set_flex_flow(bar, LV_FLEX_FLOW_ROW);
    lv_obj_set_flex_align(bar, LV_FLEX_ALIGN_START, LV_FLEX_ALIGN_CENTER,
                          LV_FLEX_ALIGN_CENTER);

    for (int i = 0; i < (int)EAPPS_CAT_COUNT + 1; i++) {
        lv_obj_t *btn = lv_button_create(bar);
        lv_obj_set_size(btn, LV_SIZE_CONTENT, 30);
        lv_obj_set_style_pad_hor(btn, 12, 0);
        lv_obj_set_style_radius(btn, 15, 0);

        bool is_all = (i == 0);
        bool active = is_all ? (s_active_cat == 0)
                             : ((int)s_active_cat == i - 1);
        (void)active;

        lv_obj_set_style_bg_color(btn, hex_color(p->primary), 0);
        lv_obj_set_style_bg_opa(btn, (i == 0) ? LV_OPA_COVER : LV_OPA_20, 0);

        lv_obj_t *lbl = lv_label_create(btn);
        lv_label_set_text(lbl, cat_names[i]);
        lv_obj_set_style_text_color(lbl,
            (i == 0) ? hex_color(p->on_primary) : hex_color(p->primary), 0);
        lv_obj_set_style_text_font(lbl, &lv_font_montserrat_12, 0);

        intptr_t cat_val = (i == 0) ? 0 : (i - 1);
        lv_obj_add_event_cb(btn, cat_tab_click_cb, LV_EVENT_CLICKED,
                            (void *)cat_val);
    }

    return bar;
}

/* ---- Back Button ---- */

static void back_click_cb(lv_event_t *e)
{
    (void)e;
    if (!s_current_app_id) return;

    const eapps_app_lifecycle_t *lc =
        eapps_registry_get_lifecycle(s_current_app_id);
    if (lc) {
        if (lc->on_hide) lc->on_hide();
        if (lc->deinit) lc->deinit();
    }

    if (s_app_cont) {
        lv_obj_delete(s_app_cont);
        s_app_cont = NULL;
    }

    s_current_app_id = NULL;

    if (s_grid_cont) lv_obj_clear_flag(s_grid_cont, LV_OBJ_FLAG_HIDDEN);
    if (s_cat_tabs)  lv_obj_clear_flag(s_cat_tabs, LV_OBJ_FLAG_HIDDEN);

    if (s_topbar) {
        lv_obj_t *title = lv_obj_get_child(s_topbar, 1);
        if (title) lv_label_set_text(title, "EoS Apps");
    }
}

/* ---- Grid Rebuild ---- */

static void rebuild_grid(void)
{
    if (!s_grid_cont) return;
    lv_obj_clean(s_grid_cont);

    int count = 0;
    const eapps_registry_entry_t *all = eapps_registry_get_all(&count);
    if (!all) return;

    for (int i = 0; i < count; i++) {
        create_app_card(s_grid_cont, &all[i]);
    }
}

/* ---- Suite Init (Home Screen) ---- */

bool suite_init(lv_obj_t *parent)
{
    const eapps_palette_t *p = eapps_theme_get_palette();
    eapps_theme_init(true);

    suite_register_all_apps();

    s_main_screen = lv_obj_create(parent);
    lv_obj_set_size(s_main_screen, LV_PCT(100), LV_PCT(100));
    lv_obj_set_style_bg_color(s_main_screen, hex_color(p->background), 0);
    lv_obj_set_style_bg_opa(s_main_screen, LV_OPA_COVER, 0);
    lv_obj_set_style_border_width(s_main_screen, 0, 0);
    lv_obj_set_style_radius(s_main_screen, 0, 0);
    lv_obj_set_style_pad_all(s_main_screen, 0, 0);
    lv_obj_set_flex_flow(s_main_screen, LV_FLEX_FLOW_COLUMN);

    /* Top bar */
    s_topbar = lv_obj_create(s_main_screen);
    lv_obj_set_size(s_topbar, LV_PCT(100), 48);
    lv_obj_set_style_bg_color(s_topbar, hex_color(p->primary), 0);
    lv_obj_set_style_bg_opa(s_topbar, LV_OPA_COVER, 0);
    lv_obj_set_style_radius(s_topbar, 0, 0);
    lv_obj_set_style_border_width(s_topbar, 0, 0);
    lv_obj_set_style_pad_hor(s_topbar, 12, 0);
    lv_obj_set_flex_flow(s_topbar, LV_FLEX_FLOW_ROW);
    lv_obj_set_flex_align(s_topbar, LV_FLEX_ALIGN_START, LV_FLEX_ALIGN_CENTER,
                          LV_FLEX_ALIGN_CENTER);

    lv_obj_t *back_btn = lv_button_create(s_topbar);
    lv_obj_set_size(back_btn, 36, 36);
    lv_obj_set_style_bg_opa(back_btn, LV_OPA_TRANSP, 0);
    lv_obj_set_style_shadow_width(back_btn, 0, 0);
    lv_obj_t *back_lbl = lv_label_create(back_btn);
    lv_label_set_text(back_lbl, LV_SYMBOL_LEFT);
    lv_obj_set_style_text_color(back_lbl, hex_color(p->on_primary), 0);
    lv_obj_center(back_lbl);
    lv_obj_add_event_cb(back_btn, back_click_cb, LV_EVENT_CLICKED, NULL);

    lv_obj_t *title = lv_label_create(s_topbar);
    lv_label_set_text(title, "EoS Apps");
    lv_obj_set_style_text_color(title, hex_color(p->on_primary), 0);
    lv_obj_set_style_text_font(title, &lv_font_montserrat_16, 0);

    /* Search bar */
    lv_obj_t *search_row = lv_obj_create(s_main_screen);
    lv_obj_set_size(search_row, LV_PCT(100), 52);
    lv_obj_set_style_bg_opa(search_row, LV_OPA_TRANSP, 0);
    lv_obj_set_style_border_width(search_row, 0, 0);
    lv_obj_set_style_pad_all(search_row, 6, 0);
    eapps_search_bar_create(search_row);

    /* Category tabs */
    s_cat_tabs = create_cat_tabs(s_main_screen);

    /* App grid (scrollable) */
    s_grid_cont = eapps_grid_create(s_main_screen, 4);
    lv_obj_set_flex_grow(s_grid_cont, 1);
    lv_obj_set_size(s_grid_cont, LV_PCT(100), LV_SIZE_CONTENT);
    lv_obj_add_flag(s_grid_cont, LV_OBJ_FLAG_SCROLLABLE);

    rebuild_grid();

    return true;
}

void suite_deinit(void)
{
    if (s_current_app_id) {
        const eapps_app_lifecycle_t *lc =
            eapps_registry_get_lifecycle(s_current_app_id);
        if (lc && lc->deinit) lc->deinit();
    }
    s_current_app_id = NULL;
    s_main_screen = NULL;
    s_grid_cont   = NULL;
    s_app_cont    = NULL;
    s_topbar      = NULL;
    s_cat_tabs    = NULL;
}
