// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Meta Platforms, Inc. and affiliates.

#if defined(EAPPS_PLATFORM_TV)

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <stdint.h>

#ifdef _SC_NPROCESSORS_ONLN
#include <unistd.h>
#endif

int eapps_clipboard_get(char *buf, int buf_len)
{
    (void)buf;
    (void)buf_len;
    return -1;
}

int eapps_clipboard_set(const char *text)
{
    (void)text;
    return -1;
}

const char *eapps_sysinfo_hostname(void)
{
    return "Smart TV";
}

const char *eapps_sysinfo_os(void)
{
    return "TV OS";
}

int eapps_sysinfo_cpu_count(void)
{
#ifdef _SC_NPROCESSORS_ONLN
    long n = sysconf(_SC_NPROCESSORS_ONLN);
    return (n > 0) ? (int)n : 4;
#else
    return 4;
#endif
}

uint64_t eapps_sysinfo_ram_total(void)
{
    /* Default to 2 GB for typical smart TV hardware */
    return (uint64_t)2 * 1024 * 1024 * 1024;
}

uint32_t eapps_tick_get_ms(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint32_t)(ts.tv_sec * 1000 + ts.tv_nsec / 1000000);
}

int eapps_keepawake_enable(void)
{
    /* Stub: TV is typically always awake */
    return 0;
}

int eapps_keepawake_disable(void)
{
    /* Stub */
    return 0;
}

int eapps_process_launch(const char *cmd)
{
    (void)cmd;
    /* Stub: TV platforms generally do not support arbitrary process launching */
    return -1;
}

#endif /* EAPPS_PLATFORM_TV */
