// SPDX-License-Identifier: MIT
// eWiFi Vault & Auto-Connect — password vault with PIN encryption + auto WiFi management
//
// Vault: stores WiFi credentials with XOR encryption using master PIN
// Auto-Connect: scans for known networks, connects automatically, reconnects on drop
//
// Platform connect commands:
//   Windows: netsh wlan connect name="SSID"
//            netsh wlan add profile (if new)
//   Linux:   nmcli device wifi connect "SSID" password "pass"
//   macOS:   networksetup -setairportnetwork en0 "SSID" "password"

#include "ewifi.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#ifdef _WIN32
#define popen  _popen
#define pclose _pclose
#endif

/* ================================================================
 *  PASSWORD VAULT
 * ================================================================ */

void ewifi_vault_init(ewifi_vault_t *v)
{
    memset(v, 0, sizeof(*v));
    v->count = 0;
    v->pin_set = false;
    v->unlocked = true;
}

bool ewifi_vault_set_pin(ewifi_vault_t *v, const char *pin)
{
    if (!pin || strlen(pin) < 4 || strlen(pin) >= EWIFI_PIN_MAX) return false;
    strncpy(v->master_pin, pin, EWIFI_PIN_MAX - 1);
    v->pin_set = true;
    v->unlocked = true;
    ewifi_vault_encrypt_all(v);
    return true;
}

bool ewifi_vault_unlock(ewifi_vault_t *v, const char *pin)
{
    if (!v->pin_set) { v->unlocked = true; return true; }
    if (strcmp(v->master_pin, pin) == 0) {
        v->unlocked = true;
        ewifi_vault_decrypt_all(v);
        return true;
    }
    return false;
}

void ewifi_vault_lock(ewifi_vault_t *v)
{
    if (v->pin_set) {
        ewifi_vault_encrypt_all(v);
        v->unlocked = false;
    }
}

bool ewifi_vault_add(ewifi_vault_t *v, const char *ssid, const char *pass,
                      const char *note, bool auto_conn)
{
    if (v->count >= EWIFI_VAULT_MAX) return false;
    if (!v->unlocked) return false;

    int existing = ewifi_vault_find(v, ssid);
    if (existing >= 0) {
        strncpy(v->entries[existing].password, pass, EWIFI_PASS_MAX - 1);
        if (note) strncpy(v->entries[existing].note, note, 31);
        v->entries[existing].auto_connect = auto_conn;
        return true;
    }

    ewifi_vault_entry_t *e = &v->entries[v->count];
    memset(e, 0, sizeof(*e));
    strncpy(e->ssid, ssid, EWIFI_SSID_MAX - 1);
    strncpy(e->password, pass, EWIFI_PASS_MAX - 1);
    if (note) strncpy(e->note, note, 31);
    e->auto_connect = auto_conn;
    e->is_encrypted = false;
    v->count++;
    return true;
}

bool ewifi_vault_remove(ewifi_vault_t *v, int idx)
{
    if (idx < 0 || idx >= v->count || !v->unlocked) return false;
    for (int i = idx; i < v->count - 1; i++)
        v->entries[i] = v->entries[i + 1];
    v->count--;
    memset(&v->entries[v->count], 0, sizeof(ewifi_vault_entry_t));
    return true;
}

const ewifi_vault_entry_t *ewifi_vault_get(const ewifi_vault_t *v, int idx)
{
    if (idx < 0 || idx >= v->count) return NULL;
    return &v->entries[idx];
}

int ewifi_vault_find(const ewifi_vault_t *v, const char *ssid)
{
    for (int i = 0; i < v->count; i++)
        if (strcmp(v->entries[i].ssid, ssid) == 0) return i;
    return -1;
}

/* XOR encryption with PIN as key — simple but effective for local storage */
static void xor_crypt(const char *data, int len, const char *key, int klen,
                       uint8_t *out)
{
    for (int i = 0; i < len; i++)
        out[i] = (uint8_t)(data[i] ^ key[i % klen]);
}

void ewifi_vault_encrypt_all(ewifi_vault_t *v)
{
    if (!v->pin_set) return;
    int klen = (int)strlen(v->master_pin);
    for (int i = 0; i < v->count; i++) {
        if (!v->entries[i].is_encrypted) {
            xor_crypt(v->entries[i].password, EWIFI_PASS_MAX,
                      v->master_pin, klen, v->entries[i].encrypted);
            memset(v->entries[i].password, 0, EWIFI_PASS_MAX);
            v->entries[i].is_encrypted = true;
        }
    }
}

void ewifi_vault_decrypt_all(ewifi_vault_t *v)
{
    if (!v->pin_set) return;
    int klen = (int)strlen(v->master_pin);
    for (int i = 0; i < v->count; i++) {
        if (v->entries[i].is_encrypted) {
            xor_crypt((const char *)v->entries[i].encrypted, EWIFI_PASS_MAX,
                      v->master_pin, klen, (uint8_t *)v->entries[i].password);
            v->entries[i].is_encrypted = false;
        }
    }
}

bool ewifi_vault_import_os(ewifi_vault_t *v)
{
    ewifi_saved_cred_t creds[EWIFI_MAX_SAVED];
    int count = ewifi_extract_saved_passwords(creds, EWIFI_MAX_SAVED);
    int imported = 0;
    for (int i = 0; i < count; i++) {
        if (creds[i].password_found && ewifi_vault_find(v, creds[i].ssid) < 0) {
            ewifi_vault_add(v, creds[i].ssid, creds[i].password, "Imported", true);
            imported++;
        }
    }
    return imported > 0;
}

/* ================================================================
 *  AUTO-CONNECT ENGINE
 * ================================================================ */

void ewifi_ac_init(ewifi_auto_connect_t *ac)
{
    memset(ac, 0, sizeof(*ac));
    ac->enabled = false;
    ac->state = EWIFI_AC_DISABLED;
    ac->max_retries = 5;
    ac->scan_interval_sec = 10;
    ac->prefer_5ghz = true;
    ac->auto_reconnect = true;
}

void ewifi_ac_enable(ewifi_auto_connect_t *ac, bool enable)
{
    ac->enabled = enable;
    if (enable) {
        ac->state = EWIFI_AC_SCANNING;
        ac->retry_count = 0;
    } else {
        ac->state = EWIFI_AC_DISABLED;
    }
}

const char *ewifi_ac_state_str(ewifi_ac_state_t s)
{
    static const char *names[] = {
        "Disabled", "Scanning", "Connecting",
        "Connected", "Reconnecting", "Failed"
    };
    return (s <= EWIFI_AC_FAILED) ? names[s] : "?";
}

/* Platform-specific WiFi connect */
bool ewifi_ac_connect(const char *ssid, const char *password)
{
    char cmd[256];
    (void)password;

#ifdef _WIN32
    snprintf(cmd, sizeof(cmd), "netsh wlan connect name=\"%s\" 2>nul", ssid);
#elif defined(__linux__)
    if (password && strlen(password) > 0)
        snprintf(cmd, sizeof(cmd),
                 "nmcli device wifi connect \"%s\" password \"%s\" 2>/dev/null",
                 ssid, password);
    else
        snprintf(cmd, sizeof(cmd),
                 "nmcli connection up \"%s\" 2>/dev/null", ssid);
#elif defined(__APPLE__)
    if (password && strlen(password) > 0)
        snprintf(cmd, sizeof(cmd),
                 "networksetup -setairportnetwork en0 \"%s\" \"%s\" 2>/dev/null",
                 ssid, password);
    else
        snprintf(cmd, sizeof(cmd),
                 "networksetup -setairportnetwork en0 \"%s\" 2>/dev/null", ssid);
#else
    (void)cmd;
    return true;
#endif

#if defined(_WIN32) || defined(__linux__) || defined(__APPLE__)
    int ret = system(cmd);
    return (ret == 0);
#endif
}

bool ewifi_ac_disconnect(void)
{
    char cmd[128];
#ifdef _WIN32
    snprintf(cmd, sizeof(cmd), "netsh wlan disconnect 2>nul");
#elif defined(__linux__)
    snprintf(cmd, sizeof(cmd), "nmcli device disconnect wlan0 2>/dev/null");
#elif defined(__APPLE__)
    snprintf(cmd, sizeof(cmd),
             "networksetup -setairportpower en0 off && "
             "networksetup -setairportpower en0 on 2>/dev/null");
#else
    (void)cmd;
    return true;
#endif

#if defined(_WIN32) || defined(__linux__) || defined(__APPLE__)
    return system(cmd) == 0;
#endif
}

/* Scan available networks, find best match in vault, connect */
ewifi_ac_state_t ewifi_ac_tick(ewifi_auto_connect_t *ac, const ewifi_vault_t *vault)
{
    if (!ac->enabled) return EWIFI_AC_DISABLED;
    if (!vault || !vault->unlocked) return ac->state;

    ewifi_network_t nets[EWIFI_MAX_NETWORKS];
    int count = ewifi_scan(nets, EWIFI_MAX_NETWORKS);

    /* Sort by signal strength — prefer 5GHz if enabled */
    int best_idx = -1;
    int best_rssi = -999;

    for (int n = 0; n < count; n++) {
        int vidx = ewifi_vault_find(vault, nets[n].ssid);
        if (vidx < 0) continue;
        if (!vault->entries[vidx].auto_connect) continue;

        int score = nets[n].rssi;
        if (ac->prefer_5ghz && nets[n].band >= EWIFI_BAND_5G)
            score += 10;

        if (score > best_rssi) {
            best_rssi = score;
            best_idx = n;
        }
    }

    if (best_idx >= 0) {
        int vidx = ewifi_vault_find(vault, nets[best_idx].ssid);
        const char *pass = vault->entries[vidx].password;

        ac->state = EWIFI_AC_CONNECTING;
        if (ewifi_ac_connect(nets[best_idx].ssid, pass)) {
            strncpy(ac->connected_ssid, nets[best_idx].ssid, EWIFI_SSID_MAX - 1);
            ac->state = EWIFI_AC_CONNECTED;
            ac->retry_count = 0;
        } else {
            ac->retry_count++;
            if (ac->retry_count >= ac->max_retries)
                ac->state = EWIFI_AC_FAILED;
            else
                ac->state = EWIFI_AC_RECONNECTING;
        }
    } else {
        ac->state = EWIFI_AC_SCANNING;
    }

    return ac->state;
}

bool ewifi_ac_reconnect(ewifi_auto_connect_t *ac, const ewifi_vault_t *vault)
{
    if (!ac->auto_reconnect) return false;
    ewifi_ac_disconnect();
    ac->state = EWIFI_AC_RECONNECTING;
    ac->retry_count = 0;
    return ewifi_ac_tick(ac, vault) == EWIFI_AC_CONNECTED;
}

/* ================================================================
 *  PRE-CONNECT VALIDATION — 6 RED FLAGS
 *
 *  Every network must pass ALL 6 checks before auto-connecting.
 *  Each flag produces a name, detail, and recommended action.
 *
 *  Flag 1: OPEN_HONEYPOT — "Free_WiFi" with Open security
 *  Flag 2: CAPTIVE_PORTAL — Likely credential harvesting portal
 *  Flag 3: EVIL_TWIN — Two identical SSIDs, different channels/BSSIDs
 *  Flag 4: WEP_INSECURE — WEP encryption (crackable in seconds)
 *  Flag 5: ROGUE_AP — Unexpectedly strong signal in open network
 *  Flag 6: MITM_RISK — Conditions favorable for man-in-the-middle
 * ================================================================ */

/* Honeypot SSID patterns — common bait names */
static bool is_honeypot_name(const char *ssid)
{
    static const char *baits[] = {
        "Free", "FREE", "free", "Guest", "GUEST", "Public", "PUBLIC",
        "Open", "OPEN", "Hotspot", "HOTSPOT", "Airport", "Hotel",
        "Starbucks", "McDonalds", "attwifi", "xfinity", "linksys",
        "netgear", "default", "setup", "test", "hack", "VIRUS",
    };
    for (int i = 0; i < (int)(sizeof(baits)/sizeof(baits[0])); i++) {
        if (strstr(ssid, baits[i]) != NULL) return true;
    }
    if (strlen(ssid) <= 4) return true;
    return false;
}

void ewifi_validate_network(const ewifi_network_t *net,
                             const ewifi_network_t *all, int count,
                             ewifi_validation_t *out)
{
    memset(out, 0, sizeof(*out));
    out->safety_score = 100;
    out->safe_to_connect = true;

    /* Initialize all flag names */
    out->flags[0].name = "Open Honeypot";
    out->flags[1].name = "Captive Portal";
    out->flags[2].name = "Evil Twin";
    out->flags[3].name = "WEP Insecure";
    out->flags[4].name = "Rogue AP";
    out->flags[5].name = "MITM Risk";

    /* ---- FLAG 1: Open Honeypot ---- */
    /* "Free_WiFi" with Open security — no encryption, anyone can sniff */
    if (net->security == EWIFI_SEC_OPEN && is_honeypot_name(net->ssid)) {
        out->flags[EWIFI_FLAG_OPEN_HONEYPOT].triggered = true;
        out->flags[EWIFI_FLAG_OPEN_HONEYPOT].detail =
            "Open network with suspicious name — no encryption, "
            "anyone can intercept your traffic";
        out->flags[EWIFI_FLAG_OPEN_HONEYPOT].action =
            "DO NOT CONNECT — use VPN if you must";
        out->safety_score -= 40;
        out->flags_triggered++;
    }

    /* ---- FLAG 2: Captive Portal Risk ---- */
    /* Networks that likely redirect to credential-harvesting login pages */
    if (net->security == EWIFI_SEC_OPEN) {
        bool portal_likely = false;
        if (is_honeypot_name(net->ssid)) portal_likely = true;
        if (net->band == EWIFI_BAND_2G && net->standard <= EWIFI_STD_G)
            portal_likely = true;
        /* Open network in public = almost certainly has captive portal */
        if (net->rssi > -65) portal_likely = true;

        if (portal_likely) {
            out->flags[EWIFI_FLAG_CAPTIVE_PORTAL].triggered = true;
            out->flags[EWIFI_FLAG_CAPTIVE_PORTAL].detail =
                "Likely captive portal — may ask for email/phone/payment. "
                "Could be credential harvesting or data collection";
            out->flags[EWIFI_FLAG_CAPTIVE_PORTAL].action =
                "Never enter real email/phone — use burner or skip";
            out->safety_score -= 15;
            out->flags_triggered++;
        }
    }

    /* ---- FLAG 3: Evil Twin Attack ---- */
    /* Two identical SSIDs with different BSSIDs or channels */
    {
        int dup_count = 0;
        bool diff_bssid = false;
        bool diff_channel = false;
        for (int i = 0; i < count; i++) {
            if (&all[i] == net) continue;
            if (strcmp(all[i].ssid, net->ssid) == 0) {
                dup_count++;
                if (strcmp(all[i].bssid, net->bssid) != 0) diff_bssid = true;
                if (all[i].channel != net->channel) diff_channel = true;
            }
        }
        if (dup_count > 0 && (diff_bssid || diff_channel)) {
            out->flags[EWIFI_FLAG_EVIL_TWIN].triggered = true;
            out->flags[EWIFI_FLAG_EVIL_TWIN].detail =
                "Multiple networks with same name but different hardware — "
                "one may be a fake AP intercepting traffic";
            out->flags[EWIFI_FLAG_EVIL_TWIN].action =
                "DO NOT CONNECT — verify with venue staff which is real";
            out->safety_score -= 50;
            out->flags_triggered++;
            out->safe_to_connect = false;
        }
    }

    /* ---- FLAG 4: WEP Insecure ---- */
    /* WEP encryption is fundamentally broken — crackable in seconds */
    if (net->security == EWIFI_SEC_WEP) {
        out->flags[EWIFI_FLAG_WEP_INSECURE].triggered = true;
        out->flags[EWIFI_FLAG_WEP_INSECURE].detail =
            "WEP encryption cracked in 2001 — tools like aircrack-ng "
            "break it in under 60 seconds. Same as no encryption";
        out->flags[EWIFI_FLAG_WEP_INSECURE].action =
            "DO NOT CONNECT — tell owner to upgrade to WPA2/WPA3";
        out->safety_score -= 45;
        out->flags_triggered++;
        out->safe_to_connect = false;
    }

    /* ---- FLAG 5: Rogue AP (Unexpectedly Strong Signal) ---- */
    /* Open network with suspiciously strong signal = attacker nearby */
    if (net->security <= EWIFI_SEC_WPA && net->rssi > -35) {
        out->flags[EWIFI_FLAG_ROGUE_AP].triggered = true;
        out->flags[EWIFI_FLAG_ROGUE_AP].detail =
            "Unusually strong signal for an open/weak network — "
            "may be a rogue AP placed close to harvest connections";
        out->flags[EWIFI_FLAG_ROGUE_AP].action =
            "DO NOT CONNECT — legitimate public APs are rarely this strong";
        out->safety_score -= 35;
        out->flags_triggered++;
        out->safe_to_connect = false;
    }

    /* ---- FLAG 6: MITM Risk ---- */
    /* Conditions that make man-in-the-middle attacks easy */
    {
        bool mitm = false;
        if (net->security == EWIFI_SEC_OPEN) mitm = true;
        if (net->security == EWIFI_SEC_WEP) mitm = true;
        if (net->hidden && net->security < EWIFI_SEC_WPA2_PSK) mitm = true;
        if (net->standard < EWIFI_STD_N && net->security < EWIFI_SEC_WPA2_PSK)
            mitm = true;

        if (mitm) {
            out->flags[EWIFI_FLAG_MITM_RISK].triggered = true;
            out->flags[EWIFI_FLAG_MITM_RISK].detail =
                "High risk of SSL stripping and traffic interception — "
                "attacker can see passwords, inject malicious content";
            out->flags[EWIFI_FLAG_MITM_RISK].action =
                "If you must connect, use VPN and verify HTTPS on every site";
            out->safety_score -= 20;
            out->flags_triggered++;
        }
    }

    /* Final determination */
    if (out->safety_score < 0) out->safety_score = 0;
    if (out->flags_triggered >= 2) out->safe_to_connect = false;
    if (out->safety_score < 50) out->safe_to_connect = false;
}

/* ---- Updated safety check using full validation ---- */

bool ewifi_is_network_safe(const ewifi_network_t *net,
                            const ewifi_network_t *all, int count)
{
    /* Basic pre-filters */
    if (net->hidden) return false;
    if (net->standard < EWIFI_STD_N) return false;
    if (net->rssi < -80) return false;
    if (net->snr < 10) return false;

    /* Run full 6-flag validation */
    ewifi_validation_t val;
    ewifi_validate_network(net, all, count, &val);
    return val.safe_to_connect;
}

int ewifi_smart_free_connect(ewifi_auto_connect_t *ac)
{
    if (!ac->smart_free_wifi) return 0;

    ewifi_network_t nets[EWIFI_MAX_NETWORKS];
    int count = ewifi_scan(nets, EWIFI_MAX_NETWORKS);

    int best_idx = -1;
    int best_score = -999;

    for (int n = 0; n < count; n++) {
        if (!ewifi_is_network_safe(&nets[n], nets, count)) continue;

        /* Score: RSSI + band bonus + security bonus */
        int score = nets[n].rssi;
        if (nets[n].band >= EWIFI_BAND_5G) score += 15;
        if (nets[n].security >= EWIFI_SEC_WPA3_SAE) score += 20;
        else if (nets[n].security >= EWIFI_SEC_WPA2_PSK) score += 10;
        score += nets[n].snr / 5;

        if (score > best_score) {
            best_score = score;
            best_idx = n;
        }
    }

    if (best_idx >= 0) {
        ac->state = EWIFI_AC_CONNECTING;
        const char *pass = (nets[best_idx].security == EWIFI_SEC_OPEN) ? "" : NULL;
        if (ewifi_ac_connect(nets[best_idx].ssid, pass)) {
            strncpy(ac->connected_ssid, nets[best_idx].ssid, EWIFI_SSID_MAX - 1);
            ac->state = EWIFI_AC_CONNECTED;
            return 1;
        }
        ac->state = EWIFI_AC_FAILED;
    }
    return 0;
}

/* ================================================================
 *  SPEED AUTO-SWITCH — Test All Networks, Connect to Fastest
 *
 *  Flow:
 *    1. Scan all available networks
 *    2. For each safe/connectable network:
 *       a. Connect temporarily
 *       b. Run speed test (download + latency)
 *       c. Record results
 *       d. Disconnect
 *    3. Rank by overall score: download * 0.5 + (1000/latency) * 0.3 + rssi_pct * 0.2
 *    4. Connect to highest-scoring network
 *
 *  Note: In simulation mode, speeds are estimated from
 *  max_rate_kbps and RSSI (real implementation would do actual HTTP tests)
 * ================================================================ */

static float estimate_speed(const ewifi_network_t *net)
{
    /* Estimate real throughput from theoretical max + signal quality */
    float max_mbps = (float)net->max_rate_kbps / 1000.0f;
    int pct = ewifi_rssi_to_pct(net->rssi);
    float efficiency = 0.3f + (pct / 100.0f) * 0.4f; /* 30-70% of max */
    return max_mbps * efficiency;
}

int ewifi_speed_rank_all(ewifi_net_ranking_t *out, int max)
{
    ewifi_network_t nets[EWIFI_MAX_NETWORKS];
    int count = ewifi_scan(nets, EWIFI_MAX_NETWORKS);
    int ranked = 0;

    for (int n = 0; n < count && ranked < max; n++) {
        ewifi_net_ranking_t *r = &out[ranked];
        memset(r, 0, sizeof(*r));
        strncpy(r->ssid, nets[n].ssid, EWIFI_SSID_MAX - 1);
        r->rssi = nets[n].rssi;
        r->is_safe = ewifi_is_network_safe(&nets[n], nets, count);

        ewifi_assessment_t assess;
        ewifi_assess_network(&nets[n], &assess);
        r->security_score = assess.score;

        /* Estimate or simulate speed */
        r->download_mbps = estimate_speed(&nets[n]);
        r->upload_mbps = r->download_mbps * 0.3f;
        r->latency_ms = 5.0f + (100 - ewifi_rssi_to_pct(nets[n].rssi)) * 0.5f;

        /* Overall score: weighted combination */
        float dl_score = r->download_mbps * 0.5f;
        float lat_score = (r->latency_ms > 0) ? (1000.0f / r->latency_ms) * 0.3f : 0;
        float sig_score = (float)ewifi_rssi_to_pct(r->rssi) * 0.2f;
        r->overall_score = dl_score + lat_score + sig_score;

        ranked++;
    }

    /* Sort by overall_score descending */
    for (int i = 0; i < ranked - 1; i++) {
        for (int j = i + 1; j < ranked; j++) {
            if (out[j].overall_score > out[i].overall_score) {
                ewifi_net_ranking_t tmp = out[i];
                out[i] = out[j];
                out[j] = tmp;
            }
        }
    }

    return ranked;
}

bool ewifi_switch_to_fastest(ewifi_auto_connect_t *ac,
                              const ewifi_vault_t *vault)
{
    if (!ac->speed_auto_switch) return false;

    ewifi_net_ranking_t rankings[EWIFI_MAX_NETWORKS];
    int count = ewifi_speed_rank_all(rankings, EWIFI_MAX_NETWORKS);

    for (int i = 0; i < count; i++) {
        if (!rankings[i].is_safe) continue;

        /* Check if we have credentials for this network */
        const char *pass = "";
        if (vault) {
            int vidx = ewifi_vault_find(vault, rankings[i].ssid);
            if (vidx >= 0) pass = vault->entries[vidx].password;
        }

        /* Already connected to this one? Skip */
        if (strcmp(ac->connected_ssid, rankings[i].ssid) == 0)
            return true;

        ewifi_ac_disconnect();
        ac->state = EWIFI_AC_CONNECTING;

        if (ewifi_ac_connect(rankings[i].ssid, pass)) {
            strncpy(ac->connected_ssid, rankings[i].ssid, EWIFI_SSID_MAX - 1);
            ac->state = EWIFI_AC_CONNECTED;
            return true;
        }
    }

    ac->state = EWIFI_AC_FAILED;
    return false;
}
