// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Meta Platforms, Inc. and affiliates.

#if defined(__APPLE__) && defined(EAPPS_PLATFORM_IOS)

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

int eapps_clipboard_get(char *buf, int buf_len)
{
    (void)buf;
    (void)buf_len;
    /* Requires Objective-C UIPasteboard bridge */
    return -1;
}

int eapps_clipboard_set(const char *text)
{
    (void)text;
    /* Requires Objective-C UIPasteboard bridge */
    return -1;
}

const char *eapps_sysinfo_hostname(void)
{
    return "iPhone";
}

const char *eapps_sysinfo_os(void)
{
    return "iOS";
}

int eapps_sysinfo_cpu_count(void)
{
    long n = sysconf(_SC_NPROCESSORS_ONLN);
    return (n > 0) ? (int)n : 1;
}

uint64_t eapps_sysinfo_ram_total(void)
{
    long pages = sysconf(_SC_PHYS_PAGES);
    long page_size = sysconf(_SC_PAGE_SIZE);
    if (pages > 0 && page_size > 0) {
        return (uint64_t)pages * (uint64_t)page_size;
    }
    return 0;
}

uint32_t eapps_tick_get_ms(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint32_t)(ts.tv_sec * 1000 + ts.tv_nsec / 1000000);
}

int eapps_keepawake_enable(void)
{
    /* Stub: would need UIApplication.idleTimerDisabled via Obj-C bridge */
    return -1;
}

int eapps_keepawake_disable(void)
{
    /* Stub */
    return -1;
}

int eapps_process_launch(const char *cmd)
{
    (void)cmd;
    /* Stub: iOS does not support arbitrary process launching */
    return -1;
}

#endif /* __APPLE__ && EAPPS_PLATFORM_IOS */
