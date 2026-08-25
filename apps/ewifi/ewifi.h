// SPDX-License-Identifier: MIT
// eWiFi — EoS LVGL Application

/**
 * @file ewifi.h
 * @brief Public API for the eWiFi app: scanning, channel analysis, security
 *        assessment, a credential vault, and auto-connect.
 *
 * Reconstructed from the three implementation files' own usage — the header had
 * been reduced to app-registration boilerplate, leaving ewifi_engine.c,
 * ewifi_passwords.c and ewifi_vault.c (46 KB together) uncompilable.
 *
 * @warning The vault is **obfuscation, not encryption**, and the OS credential
 *          readers shell out. Read the notes on ewifi_vault_t and
 *          ewifi_extract_saved_passwords() before relying on either.
 */

#pragma once

#include "lvgl.h"
#include "eapps_core.h"

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* ---- Capacity limits --------------------------------------------------- */

#define EWIFI_MAX_NETWORKS  32   /**< Scan result capacity.                */
#define EWIFI_MAX_CHANNELS  32   /**< 11 x 2.4 GHz + 9 x 5 GHz analysed.   */
#define EWIFI_MAX_SAVED     32   /**< OS credentials read in one call.     */
#define EWIFI_VAULT_MAX     32   /**< Vault entry slots.                   */
#define EWIFI_SSID_MAX      33   /**< 32-octet SSID plus NUL.              */
#define EWIFI_BSSID_LEN     18   /**< "AA:BB:CC:DD:EE:FF" plus NUL.        */
#define EWIFI_PASS_MAX      64   /**< 63-char WPA passphrase plus NUL.     */
#define EWIFI_PIN_MAX       16   /**< Vault PIN; minimum length is 4.      */
#define EWIFI_NOTE_MAX      32   /**< Vault note; engine strncpy's 31.     */
#define EWIFI_MAX_FINDINGS  12   /**< Assessment findings per network.     */
#define EWIFI_MAX_RECS      12   /**< Assessment recommendations.          */

/* ---- Security, standards, bands ---------------------------------------- */

/** Link-layer security. Order matches ewifi_security_str()'s name table. */
typedef enum {
    EWIFI_SEC_OPEN = 0,
    EWIFI_SEC_WEP,
    EWIFI_SEC_WPA,
    EWIFI_SEC_WPA2_PSK,
    EWIFI_SEC_WPA2_ENT,
    EWIFI_SEC_WPA3_SAE,
    EWIFI_SEC_WPA3_ENT,
    EWIFI_SEC_COUNT
} ewifi_security_t;

/**
 * PHY generation. Order is load-bearing: ewifi_assess_network() and
 * ewifi_is_network_safe() both compare against EWIFI_STD_G and EWIFI_STD_N
 * with < and <=, so these must stay in ascending capability order.
 */
typedef enum {
    EWIFI_STD_B = 0,
    EWIFI_STD_G,
    EWIFI_STD_N,
    EWIFI_STD_AC,
    EWIFI_STD_AX,
    EWIFI_STD_BE,
    EWIFI_STD_COUNT
} ewifi_standard_t;

/** Frequency band. ewifi_band_str() indexes its table with these. */
typedef enum {
    EWIFI_BAND_2G = 0,
    EWIFI_BAND_5G,
    EWIFI_BAND_6G
} ewifi_band_t;

/** Coarse signal bucket derived from RSSI. */
typedef enum {
    EWIFI_SIGNAL_EXCELLENT = 0,
    EWIFI_SIGNAL_GOOD,
    EWIFI_SIGNAL_FAIR,
    EWIFI_SIGNAL_WEAK,
    EWIFI_SIGNAL_VERY_WEAK
} ewifi_signal_quality_t;

/** Overall risk verdict from ewifi_assess_network(). */
typedef enum {
    EWIFI_RISK_SECURE = 0,
    EWIFI_RISK_LOW,
    EWIFI_RISK_MEDIUM,
    EWIFI_RISK_HIGH,
    EWIFI_RISK_CRITICAL
} ewifi_risk_t;

/* ---- Networks and channels --------------------------------------------- */

/** One access point as seen by a scan. */
typedef struct {
    char             ssid[EWIFI_SSID_MAX];
    char             bssid[EWIFI_BSSID_LEN];
    int              rssi;            /**< dBm, negative.                  */
    int              channel;
    int              frequency_mhz;
    ewifi_band_t     band;
    ewifi_security_t security;
    ewifi_standard_t standard;
    int              width_mhz;       /**< Channel width: 20/40/80/160.    */
    int              noise_dbm;
    int              snr;             /**< dB.                             */
    int              max_rate_kbps;   /**< Advertised PHY rate.            */
    bool             hidden;
} ewifi_network_t;

/** Occupancy of a single channel, from ewifi_channel_analysis(). */
typedef struct {
    int          number;
    int          frequency_mhz;
    ewifi_band_t band;
    bool         dfs;               /**< Radar-detection channel.          */
    int          noise_floor_dbm;
    int          network_count;
    int          utilization_pct;   /**< Clamped to 100.                   */
} ewifi_channel_t;

/* ---- Security assessment ----------------------------------------------- */

/** Result of ewifi_assess_network(). Strings are static literals. */
typedef struct {
    int          score;             /**< Starts at 100, penalties applied. */
    ewifi_risk_t risk;
    const char  *findings[EWIFI_MAX_FINDINGS];
    int          finding_count;
    const char  *recommendations[EWIFI_MAX_RECS];
    int          rec_count;
} ewifi_assessment_t;

/* ---- Threat validation ------------------------------------------------- */

/**
 * Threat classes checked by ewifi_validate_network().
 *
 * These are array indices into ewifi_validation_t::flags, assigned positionally
 * in the implementation, so the order is part of the contract.
 */
typedef enum {
    EWIFI_FLAG_OPEN_HONEYPOT = 0,
    EWIFI_FLAG_CAPTIVE_PORTAL,
    EWIFI_FLAG_EVIL_TWIN,
    EWIFI_FLAG_WEP_INSECURE,
    EWIFI_FLAG_ROGUE_AP,
    EWIFI_FLAG_MITM_RISK,
    EWIFI_FLAG_COUNT
} ewifi_flag_id_t;

/** One threat flag: always named, populated only when triggered. */
typedef struct {
    const char *name;
    const char *detail;
    const char *action;
    bool        triggered;
} ewifi_flag_t;

/** Result of ewifi_validate_network(). */
typedef struct {
    int          safety_score;      /**< Starts at 100, penalties applied. */
    bool         safe_to_connect;
    ewifi_flag_t flags[EWIFI_FLAG_COUNT];
    int          flags_triggered;
} ewifi_validation_t;

/* ---- Speed and ranking ------------------------------------------------- */

/** Throughput and latency sample. */
typedef struct {
    float download_mbps;
    float upload_mbps;
    float latency_ms;
    float jitter_ms;
} ewifi_speed_result_t;

/** One row of ewifi_speed_rank_all(), sorted by overall_score descending. */
typedef struct {
    char  ssid[EWIFI_SSID_MAX];
    int   rssi;
    bool  is_safe;
    int   security_score;
    float download_mbps;
    float upload_mbps;
    float latency_ms;
    float overall_score;
} ewifi_net_ranking_t;

/* ---- 4-way handshake reference ----------------------------------------- */

/** Stage of the WPA2 4-way handshake, used by the explanatory UI. */
typedef enum {
    EWIFI_HS_IDLE = 0,
    EWIFI_HS_MSG1_ANONCE,
    EWIFI_HS_MSG2_SNONCE,
    EWIFI_HS_MSG3_GTK,
    EWIFI_HS_MSG4_ACK,
    EWIFI_HS_COMPLETE
} ewifi_handshake_step_t;

/** Static description of one handshake stage. */
typedef struct {
    ewifi_handshake_step_t step;
    const char            *title;
    const char            *description;
} ewifi_handshake_info_t;

/* ---- OS-stored credentials --------------------------------------------- */

/**
 * One credential read back from the host OS's own network manager.
 *
 * @warning These structures hold a plaintext passphrase. Zero them with
 *          memset() once finished; do not log or render `password`.
 */
typedef struct {
    char             ssid[EWIFI_SSID_MAX];
    char             password[EWIFI_PASS_MAX];
    char             auth_type[24];      /**< e.g. "wpa-psk", from the OS. */
    ewifi_security_t security;
    bool             password_found;
} ewifi_saved_cred_t;

/* ---- Credential vault -------------------------------------------------- */

/** One vault record. Either `password` or `encrypted` is live, never both. */
typedef struct {
    char    ssid[EWIFI_SSID_MAX];
    char    password[EWIFI_PASS_MAX];   /**< Cleared once obfuscated.      */
    uint8_t encrypted[EWIFI_PASS_MAX];  /**< XOR output; see warning.      */
    char    note[EWIFI_NOTE_MAX];
    bool    auto_connect;
    bool    is_encrypted;
} ewifi_vault_entry_t;

/**
 * Credential vault.
 *
 * @warning `encrypted` is **obfuscation, not encryption**, and this struct is
 *          why: xor_crypt() uses `master_pin` as a repeating XOR keystream and
 *          `master_pin` is stored here in cleartext, beside the ciphertext it
 *          protects. Anyone who can read the vault can read the key. The XOR
 *          is also applied over the full EWIFI_PASS_MAX buffer, so the
 *          zero padding after a short passphrase leaks the keystream directly.
 *          Treat a persisted vault as plaintext. Making this real needs a KDF
 *          over the PIN, an AEAD, and a PIN that is verified rather than
 *          stored — a design change, not a patch.
 */
typedef struct {
    ewifi_vault_entry_t entries[EWIFI_VAULT_MAX];
    int                 count;
    char                master_pin[EWIFI_PIN_MAX];
    bool                pin_set;
    bool                unlocked;
} ewifi_vault_t;

/* ---- Auto-connect ------------------------------------------------------ */

/** Auto-connect state machine. Order matches ewifi_ac_state_str(). */
typedef enum {
    EWIFI_AC_DISABLED = 0,
    EWIFI_AC_SCANNING,
    EWIFI_AC_CONNECTING,
    EWIFI_AC_CONNECTED,
    EWIFI_AC_RECONNECTING,
    EWIFI_AC_FAILED
} ewifi_ac_state_t;

/** Auto-connect configuration and live state. */
typedef struct {
    bool             enabled;
    ewifi_ac_state_t state;
    char             connected_ssid[EWIFI_SSID_MAX];
    int              retry_count;
    int              max_retries;
    int              scan_interval_sec;
    bool             prefer_5ghz;
    bool             auto_reconnect;
    bool             smart_free_wifi;    /**< Opt in to open networks.     */
    bool             speed_auto_switch;  /**< Hop to the fastest known AP. */
} ewifi_auto_connect_t;

/* ======================================================================== */
/*  Engine API                                                              */
/* ======================================================================== */

/** @return Static name for @p s, or "?" if out of range. */
const char *ewifi_security_str(ewifi_security_t s);
/** @return Static name for @p s, or "?" if out of range. */
const char *ewifi_standard_str(ewifi_standard_t s);
/** @return Static name for @p b, or "?" if out of range. */
const char *ewifi_band_str(ewifi_band_t b);

/**
 * @brief Bucket an RSSI reading.
 * @param rssi Signal strength in dBm.
 * @return The matching quality bucket.
 */
ewifi_signal_quality_t ewifi_signal_quality(int rssi);

/** @return Static name for @p q, or "?" if out of range. */
const char *ewifi_signal_quality_str(ewifi_signal_quality_t q);

/**
 * @brief Map RSSI onto a 0-100 scale.
 * @param rssi Signal strength in dBm.
 * @return 100 at -30 dBm or better, 0 at -90 dBm or worse, linear between.
 */
int ewifi_rssi_to_pct(int rssi);

/** @brief Populate the scanner's network table. Call before ewifi_scan(). */
void ewifi_engine_init(void);

/**
 * @brief Copy scan results out.
 * @param out Destination array, at least @p max entries.
 * @param max Capacity of @p out.
 * @return Number of networks written.
 */
int ewifi_scan(ewifi_network_t *out, int max);

/**
 * @brief Compute per-channel occupancy for 2.4 GHz and 5 GHz.
 * @param out Destination array, at least @p max entries.
 * @param max Capacity of @p out; EWIFI_MAX_CHANNELS is always sufficient.
 * @return Number of channels written.
 */
int ewifi_channel_analysis(ewifi_channel_t *out, int max);

/**
 * @brief Least-utilised non-DFS channel in a band.
 * @param band Band to search.
 * @return Channel number, or -1 if the band has no candidate.
 */
int ewifi_best_channel(ewifi_band_t band);

/**
 * @brief Score a network's security posture.
 * @param net Network to assess.
 * @param out Receives findings, recommendations, score and risk.
 *
 * @code
 * ewifi_assessment_t a;
 * ewifi_assess_network(&net, &a);
 * printf("%d (%s)\n", a.score, a.risk == EWIFI_RISK_SECURE ? "secure" : "review");
 * @endcode
 */
void ewifi_assess_network(const ewifi_network_t *net, ewifi_assessment_t *out);

/**
 * @param step Stage to describe.
 * @return Static description, or NULL if @p step is unknown.
 */
const ewifi_handshake_info_t *ewifi_handshake_get_step(ewifi_handshake_step_t step);

/** @return Number of documented handshake stages. */
int ewifi_handshake_step_count(void);

/** @return A simulated throughput sample. Performs no network I/O. */
ewifi_speed_result_t ewifi_speed_test_simulate(void);

/* ======================================================================== */
/*  Shell argument safety                                                   */
/* ======================================================================== */

/**
 * @brief Quote an untrusted string for safe use as one POSIX shell word.
 * @param in     String to quote; NULL is rejected.
 * @param out    Receives the quoted form, including surrounding quotes.
 * @param out_sz Size of @p out in bytes.
 * @return true on success; false if @p out is too small, or @p in contains a
 *         newline or carriage return, which cannot be carried safely.
 *
 * Wraps @p in in single quotes and rewrites any embedded single quote, so every
 * other byte is preserved exactly. Needed because SSIDs are attacker-controlled
 * and reach system()/popen().
 *
 * @code
 * char q[128];
 * if (ewifi_shell_quote_posix(ssid, q, sizeof(q))) {
 *     snprintf(cmd, sizeof(cmd), "nmcli connection up %s 2>/dev/null", q);
 * }
 * @endcode
 */
bool ewifi_shell_quote_posix(const char *in, char *out, size_t out_sz);

/**
 * @brief Decide whether a string is safe to place in a cmd.exe command line.
 * @param in String to check.
 * @return true only for a non-empty string of alphanumerics, space, dot,
 *         underscore or hyphen.
 *
 * Fails closed on an allowlist rather than escaping, because cmd.exe expands
 * %VAR% inside double quotes and its escaping rules interact with the called
 * program's own argv parsing. Rejects some legitimate SSIDs by design.
 */
bool ewifi_shell_arg_is_safe_win(const char *in);

/* ======================================================================== */
/*  OS credential readers                                                   */
/* ======================================================================== */

/**
 * @brief Read the host's own saved Wi-Fi credentials.
 * @param out Destination array, at least @p max entries.
 * @param max Capacity of @p out.
 * @return Number of credentials written.
 *
 * Reads the current user's stored profiles through the platform network
 * manager — `nmcli` on Linux, `netsh wlan` on Windows, `security` on macOS —
 * so it returns only what the invoking user is already entitled to read, and
 * may return 0 without elevation.
 *
 * @warning Fills plaintext passphrases. memset() the array when done.
 */
int ewifi_extract_saved_passwords(ewifi_saved_cred_t *out, int max);

/**
 * @brief Read one saved credential by SSID.
 * @param ssid SSID to look up.
 * @param out  Receives the credential.
 * @return true if a passphrase was recovered.
 *
 * @warning @p ssid reaches a shell command. SSIDs are attacker-controlled —
 *          any nearby party can broadcast one — so it is rejected unless it
 *          contains only characters safe to pass through a shell.
 */
bool ewifi_extract_password_for_ssid(const char *ssid, ewifi_saved_cred_t *out);

/* ======================================================================== */
/*  Vault API                                                               */
/* ======================================================================== */

/** @brief Reset a vault to empty, PIN unset, unlocked. */
void ewifi_vault_init(ewifi_vault_t *v);

/**
 * @brief Set the master PIN and obfuscate stored entries.
 * @param v   Vault.
 * @param pin PIN, at least 4 and under EWIFI_PIN_MAX characters.
 * @return false if @p pin is NULL or out of range.
 */
bool ewifi_vault_set_pin(ewifi_vault_t *v, const char *pin);

/**
 * @brief Unlock a vault and deobfuscate its entries.
 * @param v   Vault.
 * @param pin PIN to check.
 * @return true when unlocked; true immediately if no PIN is set.
 */
bool ewifi_vault_unlock(ewifi_vault_t *v, const char *pin);

/** @brief Re-obfuscate and mark locked. A no-op when no PIN is set. */
void ewifi_vault_lock(ewifi_vault_t *v);

/**
 * @brief Add or update an entry.
 * @param v         Vault; must be unlocked.
 * @param ssid      Network name, used as the key.
 * @param pass      Passphrase.
 * @param note      Optional free-text note; may be NULL.
 * @param auto_conn Whether auto-connect may use this entry.
 * @return false if the vault is locked or full.
 */
bool ewifi_vault_add(ewifi_vault_t *v, const char *ssid, const char *pass,
                     const char *note, bool auto_conn);

/**
 * @brief Remove an entry, closing the gap.
 * @param v   Vault; must be unlocked.
 * @param idx Zero-based index.
 * @return false if @p idx is out of range or the vault is locked.
 */
bool ewifi_vault_remove(ewifi_vault_t *v, int idx);

/**
 * @param v   Vault.
 * @param idx Zero-based index.
 * @return The entry, or NULL if @p idx is out of range.
 */
const ewifi_vault_entry_t *ewifi_vault_get(const ewifi_vault_t *v, int idx);

/**
 * @param v    Vault.
 * @param ssid SSID to find.
 * @return Index of the match, or -1 if absent.
 */
int ewifi_vault_find(const ewifi_vault_t *v, const char *ssid);

/**
 * @brief Obfuscate every cleartext entry.
 *
 * A no-op when no PIN is set: the PIN *is* the keystream, so there is nothing
 * to obfuscate with. See the ewifi_vault_t warning for why this is not
 * encryption.
 */
void ewifi_vault_encrypt_all(ewifi_vault_t *v);

/**
 * @brief Deobfuscate every obfuscated entry.
 *
 * A no-op when no PIN is set. See the ewifi_vault_t warning.
 */
void ewifi_vault_decrypt_all(ewifi_vault_t *v);

/**
 * @brief Import the host's saved credentials into the vault.
 * @param v Vault; must be unlocked.
 * @return true if at least one credential was imported.
 */
bool ewifi_vault_import_os(ewifi_vault_t *v);

/* ======================================================================== */
/*  Auto-connect API                                                        */
/* ======================================================================== */

/** @brief Reset to defaults: disabled, 5 retries, 10 s scan, prefer 5 GHz. */
void ewifi_ac_init(ewifi_auto_connect_t *ac);

/** @brief Enable or disable auto-connect, resetting the retry counter. */
void ewifi_ac_enable(ewifi_auto_connect_t *ac, bool enable);

/** @return Static name for @p s, or "?" if out of range. */
const char *ewifi_ac_state_str(ewifi_ac_state_t s);

/**
 * @brief Ask the platform to join a network.
 * @param ssid     Network to join.
 * @param password Passphrase; may be NULL for an open network.
 * @return true if the platform command reported success.
 *
 * @warning @p ssid and @p password reach a shell command and are rejected
 *          unless shell-safe. See ewifi_extract_password_for_ssid().
 */
bool ewifi_ac_connect(const char *ssid, const char *password);

/** @brief Ask the platform to disconnect. @return true on success. */
bool ewifi_ac_disconnect(void);

/**
 * @brief Advance the auto-connect state machine one step.
 * @param ac    Auto-connect state.
 * @param vault Credential source; must be unlocked to make progress.
 * @return The state after this tick.
 */
ewifi_ac_state_t ewifi_ac_tick(ewifi_auto_connect_t *ac,
                               const ewifi_vault_t *vault);

/**
 * @brief Retry the last connection after a drop.
 * @return true if a reconnect was attempted.
 */
bool ewifi_ac_reconnect(ewifi_auto_connect_t *ac, const ewifi_vault_t *vault);

/* ======================================================================== */
/*  Threat validation and ranking                                           */
/* ======================================================================== */

/**
 * @brief Check one network for the six threat classes in ewifi_flag_id_t.
 * @param net   Network under test.
 * @param all   Full scan result, needed to spot evil twins.
 * @param count Entries in @p all.
 * @param out   Receives per-flag verdicts and an overall safety score.
 */
void ewifi_validate_network(const ewifi_network_t *net,
                            const ewifi_network_t *all, int count,
                            ewifi_validation_t *out);

/**
 * @brief Quick safety verdict.
 * @param net   Network under test.
 * @param all   Full scan result.
 * @param count Entries in @p all.
 * @return true only if the network clears every threat check and the
 *         signal-quality floor.
 */
bool ewifi_is_network_safe(const ewifi_network_t *net,
                           const ewifi_network_t *all, int count);

/**
 * @brief Join the best open network, if opted in.
 * @param ac Auto-connect state; requires `smart_free_wifi`.
 * @return Number of connection attempts made.
 */
int ewifi_smart_free_connect(ewifi_auto_connect_t *ac);

/**
 * @brief Rank visible networks by estimated throughput, latency and signal.
 * @param out Destination array, at least @p max entries.
 * @param max Capacity of @p out.
 * @return Number of rows written, sorted by overall_score descending.
 */
int ewifi_speed_rank_all(ewifi_net_ranking_t *out, int max);

/**
 * @brief Switch to the highest-ranked known network, if opted in.
 * @return true if a switch was attempted.
 */
bool ewifi_switch_to_fastest(ewifi_auto_connect_t *ac,
                             const ewifi_vault_t *vault);

/* ---- App registration -------------------------------------------------- */

extern const eapps_app_info_t      ewifi_info;
extern const eapps_app_lifecycle_t ewifi_lifecycle;
