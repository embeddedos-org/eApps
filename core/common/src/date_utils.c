// SPDX-License-Identifier: MIT
#include "eapps/date_utils.h"
#include <stdio.h>
#include <string.h>

void eapps_date_format(time_t t, const char *fmt, char *buf, size_t buf_len) {
    if (!buf || buf_len == 0) return;
    struct tm *tm = localtime(&t);
    if (!tm || !fmt) { buf[0] = '\0'; return; }
    strftime(buf, buf_len, fmt, tm);
}

void eapps_time_ago(time_t t, char *buf, size_t buf_len) {
    if (!buf || buf_len == 0) return;
    time_t now = time(NULL);
    long diff = (long)(now - t);
    if (diff < 0) diff = 0;

    if (diff < 60)          snprintf(buf, buf_len, "just now");
    else if (diff < 3600)   snprintf(buf, buf_len, "%ld min ago", diff / 60);
    else if (diff < 86400)  snprintf(buf, buf_len, "%ld hr ago", diff / 3600);
    else if (diff < 604800) snprintf(buf, buf_len, "%ld days ago", diff / 86400);
    else                    eapps_date_format(t, "%b %d, %Y", buf, buf_len);
}

void eapps_format_duration(uint32_t seconds, char *buf, size_t buf_len) {
    if (!buf || buf_len == 0) return;
    uint32_t h = seconds / 3600;
    uint32_t m = (seconds % 3600) / 60;
    uint32_t s = seconds % 60;
    if (h > 0) snprintf(buf, buf_len, "%u:%02u:%02u", h, m, s);
    else       snprintf(buf, buf_len, "%u:%02u", m, s);
}
