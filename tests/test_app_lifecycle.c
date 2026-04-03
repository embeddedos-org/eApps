// SPDX-License-Identifier: MIT
// Tests that all app info and lifecycle structs are properly populated.
#include "eapps_test.h"
#include "../core/common/include/eapps/types.h"

/* ================================================================
 * Extern declarations for all app infos and lifecycles.
 * Grouped by build category, matching the pattern in suite.c.
 * ================================================================ */

/* ---- Productivity (14 apps) ---- */
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
extern const eapps_app_info_t esettings_info;  extern const eapps_app_lifecycle_t esettings_lifecycle;
#endif

/* ---- Media (5 apps) ---- */
#ifdef EAPPS_BUILD_MEDIA
extern const eapps_app_info_t emusic_info;   extern const eapps_app_lifecycle_t emusic_lifecycle;
extern const eapps_app_info_t evideo_info;   extern const eapps_app_lifecycle_t evideo_lifecycle;
extern const eapps_app_info_t egallery_info; extern const eapps_app_lifecycle_t egallery_lifecycle;
extern const eapps_app_info_t eplay_info;    extern const eapps_app_lifecycle_t eplay_lifecycle;
extern const eapps_app_info_t epaint_info;   extern const eapps_app_lifecycle_t epaint_lifecycle;
#endif

/* ---- Games (11 apps) ---- */
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

/* ---- Connectivity (8 apps) ---- */
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

/* ---- Security (4 apps) ---- */
#ifdef EAPPS_BUILD_SECURITY
extern const eapps_app_info_t evpn_info;        extern const eapps_app_lifecycle_t evpn_lifecycle;
extern const eapps_app_info_t eguard_info;      extern const eapps_app_lifecycle_t eguard_lifecycle;
extern const eapps_app_info_t evirustower_info; extern const eapps_app_lifecycle_t evirustower_lifecycle;
extern const eapps_app_info_t ebot_info;        extern const eapps_app_lifecycle_t ebot_lifecycle;
#endif

/* ---- Web (1 app) ---- */
#ifdef EAPPS_BUILD_WEB
extern const eapps_app_info_t eweb_info; extern const eapps_app_lifecycle_t eweb_lifecycle;
#endif

/* ================================================================
 * Macro to verify a single app's info and lifecycle fields.
 * ================================================================ */

#define CHECK_APP(app) do { \
    ASSERT_NOT_NULL((app##_info).id,         #app " info.id is non-NULL"); \
    ASSERT_TRUE(strlen((app##_info).id) > 0, #app " info.id is non-empty"); \
    ASSERT_NOT_NULL((app##_info).name,         #app " info.name is non-NULL"); \
    ASSERT_TRUE(strlen((app##_info).name) > 0, #app " info.name is non-empty"); \
    ASSERT_NOT_NULL((app##_lifecycle).init,   #app " lifecycle.init is non-NULL"); \
    ASSERT_NOT_NULL((app##_lifecycle).deinit, #app " lifecycle.deinit is non-NULL"); \
} while(0)

/* ================================================================
 * Tests grouped by category
 * ================================================================ */

#ifdef EAPPS_BUILD_PRODUCTIVITY
static void test_productivity_apps(void) {
    TEST_SUITE("App Lifecycle — Productivity");
    CHECK_APP(ecal);
    CHECK_APP(enote);
    CHECK_APP(econverter);
    CHECK_APP(ebuffer);
    CHECK_APP(efiles);
    CHECK_APP(ecleaner);
    CHECK_APP(eclock);
    CHECK_APP(etools);
    CHECK_APP(etimer);
    CHECK_APP(epdf);
    CHECK_APP(ezip);
    CHECK_APP(eviewer);
    CHECK_APP(esession);
    CHECK_APP(esettings);
}
#endif

#ifdef EAPPS_BUILD_MEDIA
static void test_media_apps(void) {
    TEST_SUITE("App Lifecycle — Media");
    CHECK_APP(emusic);
    CHECK_APP(evideo);
    CHECK_APP(egallery);
    CHECK_APP(eplay);
    CHECK_APP(epaint);
}
#endif

#ifdef EAPPS_BUILD_GAMES
static void test_games_apps(void) {
    TEST_SUITE("App Lifecycle — Games");
    CHECK_APP(snake);
    CHECK_APP(tetris);
    CHECK_APP(minesweeper);
    CHECK_APP(dice);
    CHECK_APP(erunner);
    CHECK_APP(esurfer);
    CHECK_APP(echess);
    CHECK_APP(ebirds);
    CHECK_APP(eslice);
    CHECK_APP(eblocks);
    CHECK_APP(ecrush);
}
#endif

#ifdef EAPPS_BUILD_CONNECTIVITY
static void test_connectivity_apps(void) {
    TEST_SUITE("App Lifecycle — Connectivity");
    CHECK_APP(eftp);
    CHECK_APP(eserial);
    CHECK_APP(essh);
    CHECK_APP(evnc);
    CHECK_APP(etunnel);
    CHECK_APP(echat);
    CHECK_APP(eremote);
    CHECK_APP(ewifi);
}
#endif

#ifdef EAPPS_BUILD_SECURITY
static void test_security_apps(void) {
    TEST_SUITE("App Lifecycle — Security");
    CHECK_APP(evpn);
    CHECK_APP(eguard);
    CHECK_APP(evirustower);
    CHECK_APP(ebot);
}
#endif

#ifdef EAPPS_BUILD_WEB
static void test_web_apps(void) {
    TEST_SUITE("App Lifecycle — Web");
    CHECK_APP(eweb);
}
#endif

int main(void) {
#ifdef EAPPS_BUILD_PRODUCTIVITY
    test_productivity_apps();
#endif
#ifdef EAPPS_BUILD_MEDIA
    test_media_apps();
#endif
#ifdef EAPPS_BUILD_GAMES
    test_games_apps();
#endif
#ifdef EAPPS_BUILD_CONNECTIVITY
    test_connectivity_apps();
#endif
#ifdef EAPPS_BUILD_SECURITY
    test_security_apps();
#endif
#ifdef EAPPS_BUILD_WEB
    test_web_apps();
#endif

    TEST_EXIT();
}
