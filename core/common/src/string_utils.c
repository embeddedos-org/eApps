// SPDX-License-Identifier: MIT
#include "eapps/string_utils.h"
#include <string.h>
#include <ctype.h>
#include <stdio.h>

void eapps_str_truncate(const char *src, char *dst, size_t max_len) {
    if (!src || !dst || max_len == 0) return;
    size_t len = strlen(src);
    if (len <= max_len) {
        memcpy(dst, src, len + 1);
    } else {
        if (max_len > 3) {
            memcpy(dst, src, max_len - 3);
            dst[max_len - 3] = '.';
            dst[max_len - 2] = '.';
            dst[max_len - 1] = '.';
            dst[max_len] = '\0';
        } else {
            memcpy(dst, src, max_len);
            dst[max_len] = '\0';
        }
    }
}

void eapps_hexdump(const uint8_t *data, size_t len, char *out, size_t out_len) {
    if (!data || !out || out_len == 0) return;
    size_t pos = 0;
    for (size_t i = 0; i < len && pos + 3 < out_len; i++) {
        pos += (size_t)snprintf(out + pos, out_len - pos, "%02X ", data[i]);
    }
    if (pos > 0) out[pos - 1] = '\0';
    else out[0] = '\0';
}

static const char b64_table[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";

int eapps_base64_encode(const uint8_t *src, size_t src_len, char *dst, size_t dst_len) {
    size_t needed = 4 * ((src_len + 2) / 3) + 1;
    if (!src || !dst || dst_len < needed) return -1;
    size_t j = 0;
    for (size_t i = 0; i < src_len; i += 3) {
        uint32_t v = (uint32_t)src[i] << 16;
        if (i + 1 < src_len) v |= (uint32_t)src[i + 1] << 8;
        if (i + 2 < src_len) v |= (uint32_t)src[i + 2];
        dst[j++] = b64_table[(v >> 18) & 0x3F];
        dst[j++] = b64_table[(v >> 12) & 0x3F];
        dst[j++] = (i + 1 < src_len) ? b64_table[(v >> 6) & 0x3F] : '=';
        dst[j++] = (i + 2 < src_len) ? b64_table[v & 0x3F] : '=';
    }
    dst[j] = '\0';
    return (int)j;
}

static int b64_val(char c) {
    if (c >= 'A' && c <= 'Z') return c - 'A';
    if (c >= 'a' && c <= 'z') return c - 'a' + 26;
    if (c >= '0' && c <= '9') return c - '0' + 52;
    if (c == '+') return 62;
    if (c == '/') return 63;
    return -1;
}

int eapps_base64_decode(const char *src, uint8_t *dst, size_t dst_len) {
    if (!src || !dst) return -1;
    size_t slen = strlen(src);
    if (slen % 4 != 0) return -1;
    size_t out = 0;
    for (size_t i = 0; i < slen; i += 4) {
        int a = b64_val(src[i]), b = b64_val(src[i + 1]);
        int c = (src[i + 2] != '=') ? b64_val(src[i + 2]) : 0;
        int d = (src[i + 3] != '=') ? b64_val(src[i + 3]) : 0;
        if (a < 0 || b < 0) return -1;
        uint32_t v = ((uint32_t)a << 18) | ((uint32_t)b << 12) | ((uint32_t)c << 6) | (uint32_t)d;
        if (out < dst_len) dst[out++] = (uint8_t)(v >> 16);
        if (src[i + 2] != '=' && out < dst_len) dst[out++] = (uint8_t)(v >> 8);
        if (src[i + 3] != '=' && out < dst_len) dst[out++] = (uint8_t)(v);
    }
    return (int)out;
}

void eapps_str_to_lower(char *str) {
    if (!str) return;
    for (; *str; str++) *str = (char)tolower((unsigned char)*str);
}

void eapps_str_to_upper(char *str) {
    if (!str) return;
    for (; *str; str++) *str = (char)toupper((unsigned char)*str);
}

bool eapps_str_contains_ci(const char *haystack, const char *needle) {
    if (!haystack || !needle) return false;
    size_t hlen = strlen(haystack), nlen = strlen(needle);
    if (nlen > hlen) return false;
    for (size_t i = 0; i <= hlen - nlen; i++) {
        bool match = true;
        for (size_t j = 0; j < nlen; j++) {
            if (tolower((unsigned char)haystack[i + j]) != tolower((unsigned char)needle[j])) {
                match = false;
                break;
            }
        }
        if (match) return true;
    }
    return false;
}
