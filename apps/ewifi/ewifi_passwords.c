// SPDX-License-Identifier: MIT
// eWiFi Password Extraction — reads saved WiFi credentials from your own OS
//
// Platform commands used:
//   Windows: netsh wlan show profile name="SSID" key=clear
//   Linux:   nmcli -s -g 802-11-wireless.ssid,802-11-wireless-security.psk connection show
//   macOS:   security find-generic-password -D "AirPort network password" -a "SSID" -w
//
// NOTE: Requires appropriate privileges on each platform:
//   Windows: Run as admin for key=clear to reveal passwords
//   Linux:   Root or NetworkManager policy allows access
//   macOS:   User must approve keychain access prompt

#include "ewifi.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#ifdef _WIN32
#include <windows.h>
#define popen  _popen
#define pclose _pclose
#endif

/* ---- Trim whitespace ---- */
static void trim(char *s)
{
    int len = (int)strlen(s);
    while (len > 0 && (s[len-1] == '\n' || s[len-1] == '\r' || s[len-1] == ' '))
        s[--len] = '\0';
    char *start = s;
    while (*start == ' ') start++;
    if (start != s) memmove(s, start, strlen(start) + 1);
}

/* ================================================================
 *  WINDOWS: netsh wlan show profiles / show profile key=clear
 * ================================================================ */
#ifdef _WIN32

static int extract_profiles_win(ewifi_saved_cred_t *out, int max)
{
    FILE *fp = popen("netsh wlan show profiles", "r");
    if (!fp) return 0;

    char line[256];
    int count = 0;
    while (fgets(line, sizeof(line), fp) && count < max) {
        /* Look for "All User Profile" or "User Profile" lines */
        char *marker = strstr(line, ": ");
        if (!marker) continue;
        if (!strstr(line, "Profile") && !strstr(line, "profile")) continue;

        marker += 2;
        trim(marker);
        if (strlen(marker) == 0) continue;

        memset(&out[count], 0, sizeof(ewifi_saved_cred_t));
        strncpy(out[count].ssid, marker, EWIFI_SSID_MAX - 1);
        out[count].password_found = false;
        count++;
    }
    pclose(fp);
    return count;
}

static bool extract_key_for_profile_win(const char *ssid, ewifi_saved_cred_t *cred)
{
    char cmd[256];
    snprintf(cmd, sizeof(cmd),
             "netsh wlan show profile name=\"%s\" key=clear", ssid);

    FILE *fp = popen(cmd, "r");
    if (!fp) return false;

    char line[256];
    memset(cred, 0, sizeof(*cred));
    strncpy(cred->ssid, ssid, EWIFI_SSID_MAX - 1);

    while (fgets(line, sizeof(line), fp)) {
        /* Key Content : password_here */
        if (strstr(line, "Key Content") || strstr(line, "key content") ||
            strstr(line, "Schl") /* German locale */) {
            char *val = strstr(line, ": ");
            if (val) {
                val += 2;
                trim(val);
                strncpy(cred->password, val, EWIFI_PASS_MAX - 1);
                cred->password_found = (strlen(cred->password) > 0);
            }
        }
        /* Authentication : WPA2-Personal */
        if (strstr(line, "Authentication") || strstr(line, "authentication")) {
            char *val = strstr(line, ": ");
            if (val) {
                val += 2;
                trim(val);
                strncpy(cred->auth_type, val, sizeof(cred->auth_type) - 1);
            }
        }
        /* Cipher / Security */
        if (strstr(line, "Cipher") || strstr(line, "cipher") ||
            strstr(line, "Security") || strstr(line, "security")) {
            char *val = strstr(line, ": ");
            if (val && strlen(cred->security) == 0) {
                val += 2;
                trim(val);
                strncpy(cred->security, val, sizeof(cred->security) - 1);
            }
        }
    }
    pclose(fp);
    return cred->password_found;
}

int ewifi_extract_saved_passwords(ewifi_saved_cred_t *out, int max)
{
    int count = extract_profiles_win(out, max);
    for (int i = 0; i < count; i++) {
        ewifi_saved_cred_t detailed;
        if (extract_key_for_profile_win(out[i].ssid, &detailed)) {
            out[i] = detailed;
        }
    }
    return count;
}

bool ewifi_extract_password_for_ssid(const char *ssid, ewifi_saved_cred_t *out)
{
    return extract_key_for_profile_win(ssid, out);
}

/* ================================================================
 *  LINUX: nmcli connection show
 * ================================================================ */
#elif defined(__linux__)

int ewifi_extract_saved_passwords(ewifi_saved_cred_t *out, int max)
{
    /* nmcli -t -f NAME,TYPE connection show --active */
    FILE *fp = popen("nmcli -t -f NAME,TYPE connection show 2>/dev/null", "r");
    if (!fp) return 0;

    char line[256];
    int count = 0;
    while (fgets(line, sizeof(line), fp) && count < max) {
        trim(line);
        /* Format: SSID:802-11-wireless */
        if (!strstr(line, "wireless")) continue;
        char *colon = strchr(line, ':');
        if (colon) *colon = '\0';

        memset(&out[count], 0, sizeof(ewifi_saved_cred_t));
        strncpy(out[count].ssid, line, EWIFI_SSID_MAX - 1);

        /* Get password: nmcli -s -g 802-11-wireless-security.psk connection show "SSID" */
        char cmd[256];
        snprintf(cmd, sizeof(cmd),
                 "nmcli -s -g 802-11-wireless-security.psk connection show \"%s\" 2>/dev/null",
                 out[count].ssid);
        FILE *fp2 = popen(cmd, "r");
        if (fp2) {
            char pass[EWIFI_PASS_MAX] = {0};
            if (fgets(pass, sizeof(pass), fp2)) {
                trim(pass);
                if (strlen(pass) > 0) {
                    strncpy(out[count].password, pass, EWIFI_PASS_MAX - 1);
                    out[count].password_found = true;
                }
            }
            pclose(fp2);
        }

        /* Get auth type */
        snprintf(cmd, sizeof(cmd),
                 "nmcli -g 802-11-wireless-security.key-mgmt connection show \"%s\" 2>/dev/null",
                 out[count].ssid);
        FILE *fp3 = popen(cmd, "r");
        if (fp3) {
            char auth[24] = {0};
            if (fgets(auth, sizeof(auth), fp3)) {
                trim(auth);
                strncpy(out[count].auth_type, auth, sizeof(out[count].auth_type) - 1);
            }
            pclose(fp3);
        }

        count++;
    }
    pclose(fp);
    return count;
}

bool ewifi_extract_password_for_ssid(const char *ssid, ewifi_saved_cred_t *out)
{
    memset(out, 0, sizeof(*out));
    strncpy(out->ssid, ssid, EWIFI_SSID_MAX - 1);

    char cmd[256];
    snprintf(cmd, sizeof(cmd),
             "nmcli -s -g 802-11-wireless-security.psk connection show \"%s\" 2>/dev/null",
             ssid);
    FILE *fp = popen(cmd, "r");
    if (!fp) return false;

    char pass[EWIFI_PASS_MAX] = {0};
    if (fgets(pass, sizeof(pass), fp)) {
        trim(pass);
        if (strlen(pass) > 0) {
            strncpy(out->password, pass, EWIFI_PASS_MAX - 1);
            out->password_found = true;
        }
    }
    pclose(fp);
    return out->password_found;
}

/* ================================================================
 *  macOS: security find-generic-password
 * ================================================================ */
#elif defined(__APPLE__)

int ewifi_extract_saved_passwords(ewifi_saved_cred_t *out, int max)
{
    /* List preferred networks via networksetup */
    FILE *fp = popen(
        "networksetup -listpreferredwirelessnetworks en0 2>/dev/null | tail -n +2", "r");
    if (!fp) return 0;

    char line[256];
    int count = 0;
    while (fgets(line, sizeof(line), fp) && count < max) {
        trim(line);
        if (strlen(line) == 0) continue;

        memset(&out[count], 0, sizeof(ewifi_saved_cred_t));
        strncpy(out[count].ssid, line, EWIFI_SSID_MAX - 1);

        /* Try to get password from keychain */
        char cmd[256];
        snprintf(cmd, sizeof(cmd),
                 "security find-generic-password "
                 "-D \"AirPort network password\" -a \"%s\" -w 2>/dev/null",
                 out[count].ssid);
        FILE *fp2 = popen(cmd, "r");
        if (fp2) {
            char pass[EWIFI_PASS_MAX] = {0};
            if (fgets(pass, sizeof(pass), fp2)) {
                trim(pass);
                if (strlen(pass) > 0 && strstr(pass, "could not be found") == NULL) {
                    strncpy(out[count].password, pass, EWIFI_PASS_MAX - 1);
                    out[count].password_found = true;
                }
            }
            pclose(fp2);
        }

        strncpy(out[count].auth_type, "WPA/WPA2", sizeof(out[count].auth_type) - 1);
        count++;
    }
    pclose(fp);
    return count;
}

bool ewifi_extract_password_for_ssid(const char *ssid, ewifi_saved_cred_t *out)
{
    memset(out, 0, sizeof(*out));
    strncpy(out->ssid, ssid, EWIFI_SSID_MAX - 1);

    char cmd[256];
    snprintf(cmd, sizeof(cmd),
             "security find-generic-password "
             "-D \"AirPort network password\" -a \"%s\" -w 2>/dev/null",
             ssid);
    FILE *fp = popen(cmd, "r");
    if (!fp) return false;

    char pass[EWIFI_PASS_MAX] = {0};
    if (fgets(pass, sizeof(pass), fp)) {
        trim(pass);
        if (strlen(pass) > 0 && strstr(pass, "could not be found") == NULL) {
            strncpy(out->password, pass, EWIFI_PASS_MAX - 1);
            out->password_found = true;
        }
    }
    pclose(fp);
    return out->password_found;
}

/* ================================================================
 *  FALLBACK: Simulated data for embedded / unsupported platforms
 * ================================================================ */
#else

int ewifi_extract_saved_passwords(ewifi_saved_cred_t *out, int max)
{
    if (max < 3) return 0;
    memset(out, 0, 3 * sizeof(ewifi_saved_cred_t));

    strncpy(out[0].ssid, "HomeNetwork_5G", EWIFI_SSID_MAX - 1);
    strncpy(out[0].password, "MyStr0ng!WiFi#2026", EWIFI_PASS_MAX - 1);
    strncpy(out[0].auth_type, "WPA3-SAE", 23);
    out[0].password_found = true;

    strncpy(out[1].ssid, "HomeNetwork", EWIFI_SSID_MAX - 1);
    strncpy(out[1].password, "SimplePass123", EWIFI_PASS_MAX - 1);
    strncpy(out[1].auth_type, "WPA2-PSK", 23);
    out[1].password_found = true;

    strncpy(out[2].ssid, "Office_5G_AC", EWIFI_SSID_MAX - 1);
    strncpy(out[2].auth_type, "WPA2-Enterprise", 23);
    out[2].password_found = false;

    return 3;
}

bool ewifi_extract_password_for_ssid(const char *ssid, ewifi_saved_cred_t *out)
{
    ewifi_saved_cred_t all[3];
    int count = ewifi_extract_saved_passwords(all, 3);
    for (int i = 0; i < count; i++) {
        if (strcmp(all[i].ssid, ssid) == 0) {
            *out = all[i];
            return out->password_found;
        }
    }
    return false;
}

#endif
