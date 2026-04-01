// SPDX-License-Identifier: MIT
#include "eapps/platform.h"
#include <stdio.h>
#include <stdlib.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

int eapps_clipboard_get(char *buf, int buf_len) {
    FILE *p = popen("xclip -selection clipboard -o 2>/dev/null", "r");
    if (!p) return -1;
    size_t n = fread(buf, 1, (size_t)(buf_len - 1), p);
    buf[n] = '\0';
    pclose(p);
    return (int)n;
}

int eapps_clipboard_set(const char *text) {
    FILE *p = popen("xclip -selection clipboard 2>/dev/null", "w");
    if (!p) return -1;
    fputs(text, p);
    pclose(p);
    return 0;
}

void eapps_sysinfo_hostname(char *buf, int buf_len) {
    gethostname(buf, (size_t)buf_len);
}

void eapps_sysinfo_os(char *buf, int buf_len) {
    snprintf(buf, (size_t)buf_len, "Linux");
}

int eapps_sysinfo_cpu_count(void) {
    return (int)sysconf(_SC_NPROCESSORS_ONLN);
}

uint64_t eapps_sysinfo_ram_total(void) {
    long pages = sysconf(_SC_PHYS_PAGES);
    long page_size = sysconf(_SC_PAGE_SIZE);
    return (uint64_t)pages * (uint64_t)page_size;
}

void eapps_keepawake_enable(void) { }
void eapps_keepawake_disable(void) { }

int eapps_process_launch(const char *cmd) {
    return system(cmd);
}

uint32_t eapps_tick_get_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint32_t)(ts.tv_sec * 1000 + ts.tv_nsec / 1000000);
}
