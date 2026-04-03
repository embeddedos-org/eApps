// SPDX-License-Identifier: MIT
#include "eapps/platform.h"
#include <stdio.h>
#include <string.h>

int  eapps_clipboard_get(char *buf, int buf_len) { (void)buf; (void)buf_len; return -1; }
int  eapps_clipboard_set(const char *text) { (void)text; return -1; }
void eapps_sysinfo_hostname(char *buf, int buf_len) { snprintf(buf, (size_t)buf_len, "web-browser"); }
void eapps_sysinfo_os(char *buf, int buf_len) { snprintf(buf, (size_t)buf_len, "Web"); }
int  eapps_sysinfo_cpu_count(void) { return 1; }
uint64_t eapps_sysinfo_ram_total(void) { return 0; }
void eapps_keepawake_enable(void) { }
void eapps_keepawake_disable(void) { }
int  eapps_process_launch(const char *cmd) { (void)cmd; return -1; }

uint32_t eapps_tick_get_ms(void) { return 0; /* emscripten_get_now() */ }
