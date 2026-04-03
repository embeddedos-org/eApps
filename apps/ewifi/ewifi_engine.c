// SPDX-License-Identifier: MIT
// eWiFi Engine — scanning, channel analysis, security assessment, handshake education

#include "ewifi.h"
#include <string.h>
#include <stdio.h>
#include <stdlib.h>

/* ---- String Helpers ---- */

const char *ewifi_security_str(ewifi_security_t s)
{
    static const char *names[] = {
        "Open", "WEP", "WPA", "WPA2-PSK", "WPA2-Enterprise",
        "WPA3-SAE", "WPA3-Enterprise"
    };
    return (s < EWIFI_SEC_COUNT) ? names[s] : "?";
}

const char *ewifi_standard_str(ewifi_standard_t s)
{
    static const char *names[] = {
        "802.11b", "802.11g", "802.11n (WiFi 4)",
        "802.11ac (WiFi 5)", "802.11ax (WiFi 6)", "802.11be (WiFi 7)"
    };
    return (s < EWIFI_STD_COUNT) ? names[s] : "?";
}

const char *ewifi_band_str(ewifi_band_t b)
{
    static const char *names[] = {"2.4 GHz", "5 GHz", "6 GHz"};
    return (b <= EWIFI_BAND_6G) ? names[b] : "?";
}

ewifi_signal_quality_t ewifi_signal_quality(int rssi)
{
    if (rssi > -50) return EWIFI_SIGNAL_EXCELLENT;
    if (rssi > -60) return EWIFI_SIGNAL_GOOD;
    if (rssi > -70) return EWIFI_SIGNAL_FAIR;
    if (rssi > -80) return EWIFI_SIGNAL_WEAK;
    return EWIFI_SIGNAL_VERY_WEAK;
}

const char *ewifi_signal_quality_str(ewifi_signal_quality_t q)
{
    static const char *names[] = {
        "Excellent", "Good", "Fair", "Weak", "Very Weak"
    };
    return (q <= EWIFI_SIGNAL_VERY_WEAK) ? names[q] : "?";
}

int ewifi_rssi_to_pct(int rssi)
{
    if (rssi >= -30) return 100;
    if (rssi <= -90) return 0;
    return (rssi + 90) * 100 / 60;
}

/* ================================================================
 *  SIMULATED NETWORK SCANNER
 *  In production: uses platform WiFi API (nl80211 / CoreLocation / WifiManager)
 * ================================================================ */

static ewifi_network_t g_networks[EWIFI_MAX_NETWORKS];
static int g_network_count = 0;

#define SCPY(d,s) strncpy(d,s,sizeof(d)-1)

void ewifi_engine_init(void)
{
    memset(g_networks, 0, sizeof(g_networks));
    int i = 0;

    SCPY(g_networks[i].ssid, "HomeNetwork_5G");
    SCPY(g_networks[i].bssid, "A4:CF:12:D3:45:67");
    g_networks[i].rssi = -42;  g_networks[i].channel = 36;
    g_networks[i].frequency_mhz = 5180;  g_networks[i].band = EWIFI_BAND_5G;
    g_networks[i].security = EWIFI_SEC_WPA3_SAE;
    g_networks[i].standard = EWIFI_STD_AX;
    g_networks[i].width_mhz = 80;  g_networks[i].noise_dbm = -95;
    g_networks[i].snr = 53;  g_networks[i].max_rate_kbps = 1201000;
    i++;

    SCPY(g_networks[i].ssid, "HomeNetwork");
    SCPY(g_networks[i].bssid, "A4:CF:12:D3:45:68");
    g_networks[i].rssi = -48;  g_networks[i].channel = 6;
    g_networks[i].frequency_mhz = 2437;  g_networks[i].band = EWIFI_BAND_2G;
    g_networks[i].security = EWIFI_SEC_WPA2_PSK;
    g_networks[i].standard = EWIFI_STD_N;
    g_networks[i].width_mhz = 40;  g_networks[i].noise_dbm = -90;
    g_networks[i].snr = 42;  g_networks[i].max_rate_kbps = 300000;
    i++;

    SCPY(g_networks[i].ssid, "Neighbor_WiFi");
    SCPY(g_networks[i].bssid, "B8:27:EB:AA:BB:CC");
    g_networks[i].rssi = -65;  g_networks[i].channel = 1;
    g_networks[i].frequency_mhz = 2412;  g_networks[i].band = EWIFI_BAND_2G;
    g_networks[i].security = EWIFI_SEC_WPA2_PSK;
    g_networks[i].standard = EWIFI_STD_N;
    g_networks[i].width_mhz = 20;  g_networks[i].noise_dbm = -88;
    g_networks[i].snr = 23;  g_networks[i].max_rate_kbps = 150000;
    i++;

    SCPY(g_networks[i].ssid, "CoffeeShop_Free");
    SCPY(g_networks[i].bssid, "DC:A6:32:11:22:33");
    g_networks[i].rssi = -72;  g_networks[i].channel = 11;
    g_networks[i].frequency_mhz = 2462;  g_networks[i].band = EWIFI_BAND_2G;
    g_networks[i].security = EWIFI_SEC_OPEN;
    g_networks[i].standard = EWIFI_STD_G;
    g_networks[i].width_mhz = 20;  g_networks[i].noise_dbm = -85;
    g_networks[i].snr = 13;  g_networks[i].max_rate_kbps = 54000;
    i++;

    SCPY(g_networks[i].ssid, "Office_5G_AC");
    SCPY(g_networks[i].bssid, "00:1A:2B:3C:4D:5E");
    g_networks[i].rssi = -55;  g_networks[i].channel = 149;
    g_networks[i].frequency_mhz = 5745;  g_networks[i].band = EWIFI_BAND_5G;
    g_networks[i].security = EWIFI_SEC_WPA2_ENT;
    g_networks[i].standard = EWIFI_STD_AC;
    g_networks[i].width_mhz = 80;  g_networks[i].noise_dbm = -92;
    g_networks[i].snr = 37;  g_networks[i].max_rate_kbps = 867000;
    i++;

    SCPY(g_networks[i].ssid, "OldRouter");
    SCPY(g_networks[i].bssid, "44:55:66:77:88:99");
    g_networks[i].rssi = -78;  g_networks[i].channel = 6;
    g_networks[i].frequency_mhz = 2437;  g_networks[i].band = EWIFI_BAND_2G;
    g_networks[i].security = EWIFI_SEC_WEP;
    g_networks[i].standard = EWIFI_STD_B;
    g_networks[i].width_mhz = 20;  g_networks[i].noise_dbm = -82;
    g_networks[i].snr = 4;  g_networks[i].max_rate_kbps = 11000;
    i++;

    SCPY(g_networks[i].ssid, "WiFi7_Ultra");
    SCPY(g_networks[i].bssid, "EE:FF:00:11:22:33");
    g_networks[i].rssi = -38;  g_networks[i].channel = 5;
    g_networks[i].frequency_mhz = 5975;  g_networks[i].band = EWIFI_BAND_6G;
    g_networks[i].security = EWIFI_SEC_WPA3_SAE;
    g_networks[i].standard = EWIFI_STD_BE;
    g_networks[i].width_mhz = 320;  g_networks[i].noise_dbm = -100;
    g_networks[i].snr = 62;  g_networks[i].max_rate_kbps = 46000000;
    i++;

    g_networks[i].hidden = true;
    SCPY(g_networks[i].ssid, "(hidden)");
    SCPY(g_networks[i].bssid, "AA:BB:CC:DD:EE:FF");
    g_networks[i].rssi = -81;  g_networks[i].channel = 3;
    g_networks[i].frequency_mhz = 2422;  g_networks[i].band = EWIFI_BAND_2G;
    g_networks[i].security = EWIFI_SEC_WPA2_PSK;
    g_networks[i].standard = EWIFI_STD_N;
    g_networks[i].width_mhz = 20;  g_networks[i].noise_dbm = -86;
    g_networks[i].snr = 5;  g_networks[i].max_rate_kbps = 72000;
    i++;

    g_network_count = i;
}

int ewifi_scan(ewifi_network_t *out, int max)
{
    int count = (g_network_count < max) ? g_network_count : max;
    memcpy(out, g_networks, count * sizeof(ewifi_network_t));
    return count;
}

/* ================================================================
 *  CHANNEL ANALYSIS
 * ================================================================ */

int ewifi_channel_analysis(ewifi_channel_t *out, int max)
{
    static const int ch2g[] = {1,2,3,4,5,6,7,8,9,10,11};
    static const int freq2g[] = {2412,2417,2422,2427,2432,2437,2442,2447,2452,2457,2462};
    int count = 0;

    for (int c = 0; c < 11 && count < max; c++) {
        out[count].number = ch2g[c];
        out[count].frequency_mhz = freq2g[c];
        out[count].band = EWIFI_BAND_2G;
        out[count].dfs = false;
        out[count].noise_floor_dbm = -90;
        out[count].network_count = 0;
        out[count].utilization_pct = 0;

        for (int n = 0; n < g_network_count; n++) {
            if (g_networks[n].band == EWIFI_BAND_2G) {
                int d = abs(g_networks[n].channel - ch2g[c]);
                if (d <= 2) {
                    out[count].network_count++;
                    out[count].utilization_pct += 15;
                }
            }
        }
        if (out[count].utilization_pct > 100) out[count].utilization_pct = 100;
        count++;
    }

    static const int ch5g[] = {36,40,44,48,149,153,157,161,165};
    static const int freq5g[] = {5180,5200,5220,5240,5745,5765,5785,5805,5825};
    for (int c = 0; c < 9 && count < max; c++) {
        out[count].number = ch5g[c];
        out[count].frequency_mhz = freq5g[c];
        out[count].band = EWIFI_BAND_5G;
        out[count].dfs = (ch5g[c] >= 52 && ch5g[c] <= 144);
        out[count].noise_floor_dbm = -95;
        out[count].network_count = 0;
        out[count].utilization_pct = 0;

        for (int n = 0; n < g_network_count; n++) {
            if (g_networks[n].band == EWIFI_BAND_5G &&
                g_networks[n].channel == ch5g[c]) {
                out[count].network_count++;
                out[count].utilization_pct += 20;
            }
        }
        count++;
    }
    return count;
}

int ewifi_best_channel(ewifi_band_t band)
{
    ewifi_channel_t channels[EWIFI_MAX_CHANNELS];
    int count = ewifi_channel_analysis(channels, EWIFI_MAX_CHANNELS);
    int best = -1, min_util = 999;

    for (int i = 0; i < count; i++) {
        if (channels[i].band == band && !channels[i].dfs &&
            channels[i].utilization_pct < min_util) {
            min_util = channels[i].utilization_pct;
            best = channels[i].number;
        }
    }
    return best;
}

/* ================================================================
 *  SECURITY ASSESSMENT
 * ================================================================ */

void ewifi_assess_network(const ewifi_network_t *net, ewifi_assessment_t *out)
{
    memset(out, 0, sizeof(*out));
    out->score = 100;

    if (net->security == EWIFI_SEC_OPEN) {
        out->score -= 50;
        out->findings[out->finding_count++] = "No encryption — traffic is plaintext";
        out->recommendations[out->rec_count++] = "Enable WPA2-PSK or WPA3-SAE immediately";
    }
    if (net->security == EWIFI_SEC_WEP) {
        out->score -= 40;
        out->findings[out->finding_count++] = "WEP is broken — crackable in seconds";
        out->recommendations[out->rec_count++] = "Upgrade to WPA2 or WPA3";
    }
    if (net->security == EWIFI_SEC_WPA) {
        out->score -= 20;
        out->findings[out->finding_count++] = "WPA (TKIP) has known vulnerabilities";
        out->recommendations[out->rec_count++] = "Upgrade to WPA2-AES or WPA3";
    }
    if (net->security == EWIFI_SEC_WPA2_PSK) {
        out->score -= 5;
        out->findings[out->finding_count++] = "WPA2-PSK: strong if password is 15+ chars";
        out->recommendations[out->rec_count++] = "Use random passphrase 15+ characters";
    }
    if (net->security == EWIFI_SEC_WPA3_SAE || net->security == EWIFI_SEC_WPA3_ENT) {
        out->findings[out->finding_count++] = "WPA3 — strongest available encryption";
    }
    if (net->hidden) {
        out->score -= 3;
        out->findings[out->finding_count++] = "Hidden SSID provides no real security";
        out->recommendations[out->rec_count++] = "Hidden SSIDs are easily discovered";
    }
    if (net->standard <= EWIFI_STD_G) {
        out->score -= 10;
        out->findings[out->finding_count++] = "Legacy WiFi standard (802.11b/g)";
        out->recommendations[out->rec_count++] = "Upgrade router to WiFi 5 or 6";
    }

    out->recommendations[out->rec_count++] = "Disable WPS on router";
    out->recommendations[out->rec_count++] = "Keep firmware updated";

    if (out->score >= 90) out->risk = EWIFI_RISK_SECURE;
    else if (out->score >= 75) out->risk = EWIFI_RISK_LOW;
    else if (out->score >= 50) out->risk = EWIFI_RISK_MEDIUM;
    else if (out->score >= 25) out->risk = EWIFI_RISK_HIGH;
    else out->risk = EWIFI_RISK_CRITICAL;
}

/* ================================================================
 *  4-WAY HANDSHAKE EDUCATION
 *
 *  WPA2-PSK authentication flow:
 *    1. AP → Client:  ANonce (AP's random number)
 *    2. Client → AP:  SNonce + MIC (client derives PTK from PMK+nonces)
 *    3. AP → Client:  GTK + MIC (AP verifies client, sends group key)
 *    4. Client → AP:  ACK (client confirms installation)
 *
 *  Key derivation:
 *    PMK = PBKDF2(passphrase, SSID, 4096, 256)  — intentionally slow
 *    PTK = PRF(PMK, ANonce, SNonce, MAC_AP, MAC_Client)
 *    PTK splits into: KCK(128) + KEK(128) + TK(128) + MIC key
 * ================================================================ */

static const ewifi_handshake_info_t g_handshake[] = {
    {EWIFI_HS_IDLE, "Pre-Authentication",
     "Client and AP share a Pre-Shared Key (PSK). The PMK is derived:\n"
     "PMK = PBKDF2-SHA1(passphrase, SSID, 4096 iterations, 256 bits)\n"
     "This is intentionally slow to resist brute-force attacks."},
    {EWIFI_HS_MSG1_ANONCE, "Message 1: AP sends ANonce",
     "AP generates a random ANonce and sends it to the client.\n"
     "The client now has all inputs to derive the PTK:\n"
     "PTK = PRF-512(PMK, ANonce, SNonce, MAC_AP, MAC_Client)"},
    {EWIFI_HS_MSG2_SNONCE, "Message 2: Client sends SNonce + MIC",
     "Client generates its own SNonce, derives the PTK, and sends\n"
     "SNonce + MIC (Message Integrity Code) to prove it knows the PMK.\n"
     "AP can now also derive the same PTK and verify the MIC."},
    {EWIFI_HS_MSG3_GTK, "Message 3: AP sends GTK (encrypted)",
     "AP confirms the client is authentic by verifying the MIC.\n"
     "AP sends the Group Temporal Key (GTK) encrypted with KEK.\n"
     "GTK is used for broadcast/multicast traffic."},
    {EWIFI_HS_MSG4_ACK, "Message 4: Client sends ACK",
     "Client confirms GTK installation. Both sides now have:\n"
     "- PTK for unicast encryption (AES-CCMP)\n"
     "- GTK for broadcast/multicast\n"
     "Secure session established."},
    {EWIFI_HS_COMPLETE, "Handshake Complete",
     "All traffic is now encrypted with AES-CCMP (WPA2) or\n"
     "AES-GCMP-256 (WPA3). Session keys are unique per connection.\n"
     "Why strong passwords matter: PBKDF2 with 4096 iterations means\n"
     "each guess takes ~4096x longer, but short passwords still fall."},
};

const ewifi_handshake_info_t *ewifi_handshake_get_step(ewifi_handshake_step_t step)
{
    for (int i = 0; i < (int)(sizeof(g_handshake)/sizeof(g_handshake[0])); i++)
        if (g_handshake[i].step == step) return &g_handshake[i];
    return NULL;
}

int ewifi_handshake_step_count(void) {
    return (int)(sizeof(g_handshake) / sizeof(g_handshake[0]));
}

/* ================================================================
 *  SPEED TEST (Simulated)
 * ================================================================ */

ewifi_speed_result_t ewifi_speed_test_simulate(void)
{
    ewifi_speed_result_t r;
    r.download_mbps = 245.7f;
    r.upload_mbps = 42.3f;
    r.latency_ms = 12.5f;
    r.jitter_ms = 2.1f;
    return r;
}
