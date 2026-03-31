// SPDX-License-Identifier: MIT
#include "suite.h"
#include "eapps/registry.h"
#include "eapps/theme.h"
#include "eapps/widgets.h"
#include "eapps/version.h"
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
    REG(eftp); REG(eserial); REG(essh); REG(evnc); REG(etunnel); REG(echat);
#endif
#ifdef EAPPS_BUILD_SECURITY
    REG(evpn); REG(eguard); REG(evirustower);
#endif
#ifdef EAPPS_BUILD_WEB
    REG(eweb);
#endif
}

static const char *s_current_app_id = NULL;

static void on_app_card_click(const char *app_id) {
    const eapps_app_lifecycle_t *lc = eapps_registry_get_lifecycle(app_id);
    if (!lc || !lc->init) return;
    s_current_app_id = app_id;
    /* TODO: create container, call lc->init(container), hide grid */
}

static void on_back_click(void) {
    if (!s_current_app_id) return;
    const eapps_app_lifecycle_t *lc = eapps_registry_get_lifecycle(s_current_app_id);
    if (lc && lc->deinit) lc->deinit();
    s_current_app_id = NULL;
    /* TODO: delete container, show grid */
}

bool suite_init(lv_obj_t *parent) {
    (void)parent;
    (void)on_app_card_click;
    (void)on_back_click;

    suite_register_all_apps();
    /* TODO: create top bar, search bar, category tabs, app grid */
    return true;
}

void suite_deinit(void) {
    s_current_app_id = NULL;
}
