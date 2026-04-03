// SPDX-License-Identifier: MIT
#ifndef EAPPS_APP_EWIFI_H
#define EAPPS_APP_EWIFI_H
#include "eapps/types.h"
#include <stdint.h>
#include <stdbool.h>

/* ================================================================
 * eWiFi — WiFi Analyzer & Network Security Education Tool
 *
 * Features:
 *   - Network scanning & signal strength (RSSI) visualization
 *   - Channel utilization & interference analysis
 *   - Security protocol detection (Open/WEP/WPA2/WPA3)
 *   - 4-way handshake education (WPA2-PSK flow)
 *   - Network hardening recommendations
 *   - Encryption standards reference
 *   - Lab setup guide for safe learning
 * ================================================================ */

/* ---- Security Types ---- */

typedef enum {
    EWIFI_SEC_OPEN,
    EWIFI_SEC_WEP,
    EWIFI_SEC_WPA,
    EWIFI_SEC_WPA2_PSK,
    EWIFI_SEC_WPA2_ENT,
    EWIFI_SEC_WPA3_SAE,
    EWIFI_SEC_WPA3_ENT,
    EWIFI_SEC_COUNT,
} ewifi_security_t;

/* ---- WiFi Standard ---- */

typedef enum {
    EWIFI_STD_B,       /* 802.11b  — 2.4 GHz, 11 Mbps */
    EWIFI_STD_G,       /* 802.11g  — 2.4 GHz, 54 Mbps */
    EWIFI_STD_N,       /* 802.11n  — 2.4/5 GHz, 600 Mbps (WiFi 4) */
    EWIFI_STD_AC,      /* 802.11ac — 5 GHz, 6.9 Gbps (WiFi 5) */
    EWIFI_STD_AX,      /* 802.11ax — 2.4/5/6 GHz, 9.6 Gbps (WiFi 6) */
    EWIFI_STD_BE,      /* 802.11be — 2.4/5/6 GHz, 46 Gbps (WiFi 7) */
    EWIFI_STD_COUNT,
} ewifi_standard_t;

/* ---- Band ---- */

typedef enum {
    EWIFI_BAND_2G,
    EWIFI_BAND_5G,
    EWIFI_BAND_6G,
} ewifi_band_t;

/* ---- Scanned Network ---- */

#define EWIFI_MAX_NETWORKS 32
#define EWIFI_SSID_MAX     33
#define EWIFI_BSSID_LEN    18

typedef struct {
    char              ssid[EWIFI_SSID_MAX];
    char              bssid[EWIFI_BSSID_LEN];
    int               rssi;
    int               channel;
    int               frequency_mhz;
    ewifi_band_t      band;
    ewifi_security_t  security;
    ewifi_standard_t  standard;
    int               width_mhz;
    bool              hidden;
    int               noise_dbm;
    int               snr;
    uint32_t          max_rate_kbps;
} ewifi_network_t;

/* ---- Channel Info ---- */

#define EWIFI_MAX_CHANNELS 64

typedef struct {
    int  number;
    int  frequency_mhz;
    int  network_count;
    int  utilization_pct;
    int  noise_floor_dbm;
    bool dfs;
    ewifi_band_t band;
} ewifi_channel_t;

/* ---- Signal Quality ---- */

typedef enum {
    EWIFI_SIGNAL_EXCELLENT,  /* > -50 dBm */
    EWIFI_SIGNAL_GOOD,       /* -50 to -60 dBm */
    EWIFI_SIGNAL_FAIR,       /* -60 to -70 dBm */
    EWIFI_SIGNAL_WEAK,       /* -70 to -80 dBm */
    EWIFI_SIGNAL_VERY_WEAK,  /* < -80 dBm */
} ewifi_signal_quality_t;

/* ---- 4-Way Handshake Steps (Education) ---- */

typedef enum {
    EWIFI_HS_IDLE,
    EWIFI_HS_MSG1_ANONCE,
    EWIFI_HS_MSG2_SNONCE,
    EWIFI_HS_MSG3_GTK,
    EWIFI_HS_MSG4_ACK,
    EWIFI_HS_COMPLETE,
} ewifi_handshake_step_t;

typedef struct {
    ewifi_handshake_step_t step;
    const char            *description;
    const char            *detail;
} ewifi_handshake_info_t;

/* ---- Security Assessment ---- */

typedef enum {
    EWIFI_RISK_CRITICAL,
    EWIFI_RISK_HIGH,
    EWIFI_RISK_MEDIUM,
    EWIFI_RISK_LOW,
    EWIFI_RISK_SECURE,
} ewifi_risk_level_t;

#define EWIFI_MAX_RECOMMENDATIONS 8

typedef struct {
    ewifi_risk_level_t risk;
    int                score;
    const char        *findings[EWIFI_MAX_RECOMMENDATIONS];
    int                finding_count;
    const char        *recommendations[EWIFI_MAX_RECOMMENDATIONS];
    int                rec_count;
} ewifi_assessment_t;

/* ---- Speed Test Result ---- */

typedef struct {
    float  download_mbps;
    float  upload_mbps;
    float  latency_ms;
    float  jitter_ms;
} ewifi_speed_result_t;

/* ---- Saved WiFi Credentials ---- */

#define EWIFI_PASS_MAX 64
#define EWIFI_MAX_SAVED 32

typedef struct {
    char ssid[EWIFI_SSID_MAX];
    char password[EWIFI_PASS_MAX];
    char security[24];
    char auth_type[24];
    bool password_found;
} ewifi_saved_cred_t;

/* ---- Password Vault ---- */

#define EWIFI_VAULT_MAX  32
#define EWIFI_PIN_MAX    16

typedef struct {
    char    ssid[EWIFI_SSID_MAX];
    char    password[EWIFI_PASS_MAX];
    char    note[32];
    bool    auto_connect;
    uint8_t encrypted[EWIFI_PASS_MAX];
    bool    is_encrypted;
} ewifi_vault_entry_t;

typedef struct {
    ewifi_vault_entry_t entries[EWIFI_VAULT_MAX];
    int                 count;
    char                master_pin[EWIFI_PIN_MAX];
    bool                pin_set;
    bool                unlocked;
} ewifi_vault_t;

/* ---- Auto-Connect State ---- */

typedef enum {
    EWIFI_AC_DISABLED,
    EWIFI_AC_SCANNING,
    EWIFI_AC_CONNECTING,
    EWIFI_AC_CONNECTED,
    EWIFI_AC_RECONNECTING,
    EWIFI_AC_FAILED,
} ewifi_ac_state_t;

typedef struct {
    bool             enabled;
    ewifi_ac_state_t state;
    char             connected_ssid[EWIFI_SSID_MAX];
    int              retry_count;
    int              max_retries;
    int              scan_interval_sec;
    bool             prefer_5ghz;
    bool             auto_reconnect;
    bool             smart_free_wifi;
    bool             speed_auto_switch;
} ewifi_auto_connect_t;

/* ---- Pre-Connect Validation (6 Red Flags) ---- */

#define EWIFI_FLAG_COUNT 6

typedef enum {
    EWIFI_FLAG_OPEN_HONEYPOT   = 0,
    EWIFI_FLAG_CAPTIVE_PORTAL  = 1,
    EWIFI_FLAG_EVIL_TWIN       = 2,
    EWIFI_FLAG_WEP_INSECURE    = 3,
    EWIFI_FLAG_ROGUE_AP        = 4,
    EWIFI_FLAG_MITM_RISK       = 5,
} ewifi_red_flag_t;

typedef struct {
    bool        triggered;
    const char *name;
    const char *detail;
    const char *action;
} ewifi_flag_result_t;

typedef struct {
    ewifi_flag_result_t flags[EWIFI_FLAG_COUNT];
    int                 flags_triggered;
    bool                safe_to_connect;
    int                 safety_score;
} ewifi_validation_t;

/* ---- Speed Test Ranking (per network) ---- */

typedef struct {
    char   ssid[EWIFI_SSID_MAX];
    int    rssi;
    float  download_mbps;
    float  upload_mbps;
    float  latency_ms;
    int    security_score;
    bool   is_safe;
    float  overall_score;
} ewifi_net_ranking_t;

/* ---- Engine API ---- */

void ewifi_engine_init(void);
int  ewifi_scan(ewifi_network_t *out, int max);
ewifi_signal_quality_t ewifi_signal_quality(int rssi);
const char *ewifi_signal_quality_str(ewifi_signal_quality_t q);
const char *ewifi_security_str(ewifi_security_t s);
const char *ewifi_standard_str(ewifi_standard_t s);
const char *ewifi_band_str(ewifi_band_t b);
int  ewifi_channel_analysis(ewifi_channel_t *out, int max);
int  ewifi_best_channel(ewifi_band_t band);
void ewifi_assess_network(const ewifi_network_t *net, ewifi_assessment_t *out);
const ewifi_handshake_info_t *ewifi_handshake_get_step(ewifi_handshake_step_t step);
int  ewifi_handshake_step_count(void);
ewifi_speed_result_t ewifi_speed_test_simulate(void);
int  ewifi_rssi_to_pct(int rssi);

/* Password extraction */
int  ewifi_extract_saved_passwords(ewifi_saved_cred_t *out, int max);
bool ewifi_extract_password_for_ssid(const char *ssid, ewifi_saved_cred_t *out);

/* Password Vault */
void ewifi_vault_init(ewifi_vault_t *v);
bool ewifi_vault_set_pin(ewifi_vault_t *v, const char *pin);
bool ewifi_vault_unlock(ewifi_vault_t *v, const char *pin);
void ewifi_vault_lock(ewifi_vault_t *v);
bool ewifi_vault_add(ewifi_vault_t *v, const char *ssid, const char *pass,
                      const char *note, bool auto_conn);
bool ewifi_vault_remove(ewifi_vault_t *v, int idx);
const ewifi_vault_entry_t *ewifi_vault_get(const ewifi_vault_t *v, int idx);
int  ewifi_vault_find(const ewifi_vault_t *v, const char *ssid);
void ewifi_vault_encrypt_all(ewifi_vault_t *v);
void ewifi_vault_decrypt_all(ewifi_vault_t *v);
bool ewifi_vault_import_os(ewifi_vault_t *v);

/* Auto-Connect */
void ewifi_ac_init(ewifi_auto_connect_t *ac);
void ewifi_ac_enable(ewifi_auto_connect_t *ac, bool enable);
ewifi_ac_state_t ewifi_ac_tick(ewifi_auto_connect_t *ac, const ewifi_vault_t *vault);
bool ewifi_ac_connect(const char *ssid, const char *password);
bool ewifi_ac_disconnect(void);
bool ewifi_ac_reconnect(ewifi_auto_connect_t *ac, const ewifi_vault_t *vault);
const char *ewifi_ac_state_str(ewifi_ac_state_t s);

/* Smart Free WiFi — auto-connect to safe open networks */
bool ewifi_is_network_safe(const ewifi_network_t *net,
                            const ewifi_network_t *all, int count);
int  ewifi_smart_free_connect(ewifi_auto_connect_t *ac);
void ewifi_validate_network(const ewifi_network_t *net,
                             const ewifi_network_t *all, int count,
                             ewifi_validation_t *out);

/* Speed Auto-Switch — test all, connect to fastest */
int  ewifi_speed_rank_all(ewifi_net_ranking_t *out, int max);
bool ewifi_switch_to_fastest(ewifi_auto_connect_t *ac,
                              const ewifi_vault_t *vault);

/* ---- App Registration ---- */

extern const eapps_app_info_t      ewifi_info;
extern const eapps_app_lifecycle_t ewifi_lifecycle;

#endif
