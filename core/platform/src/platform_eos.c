// SPDX-License-Identifier: MIT
#include "eapps/platform.h"
#include <string.h>

int  eapps_clipboard_get(char *buf, int buf_len) { (void)buf; (void)buf_len; return -1; }
int  eapps_clipboard_set(const char *text) { (void)text; return -1; }
void eapps_sysinfo_hostname(char *buf, int buf_len) { snprintf(buf, buf_len, "eos-device"); }
void eapps_sysinfo_os(char *buf, int buf_len) { snprintf(buf, buf_len, "EoS"); }
int  eapps_sysinfo_cpu_count(void) { return 1; }
uint64_t eapps_sysinfo_ram_total(void) { return 256 * 1024 * 1024ULL; }
void eapps_keepawake_enable(void) { /* eos_hal_display_backlight(255) */ }
void eapps_keepawake_disable(void) { }
int  eapps_process_launch(const char *cmd) { (void)cmd; return -1; }

static uint32_t s_tick = 0;
uint32_t eapps_tick_get_ms(void) { return s_tick++; }
