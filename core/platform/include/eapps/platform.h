// SPDX-License-Identifier: MIT
#ifndef EAPPS_PLATFORM_H
#define EAPPS_PLATFORM_H

#include <stdint.h>
#include <stdbool.h>

int  eapps_clipboard_get(char *buf, int buf_len);
int  eapps_clipboard_set(const char *text);

void eapps_sysinfo_hostname(char *buf, int buf_len);
void eapps_sysinfo_os(char *buf, int buf_len);
int  eapps_sysinfo_cpu_count(void);
uint64_t eapps_sysinfo_ram_total(void);

void eapps_keepawake_enable(void);
void eapps_keepawake_disable(void);

int  eapps_process_launch(const char *cmd);

uint32_t eapps_tick_get_ms(void);

#endif /* EAPPS_PLATFORM_H */
