/*
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2024 Meta Platforms, Inc. and affiliates.
 *
 * Android platform abstraction for eApps.
 */

#if defined(__ANDROID__)

#include <stdint.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <sys/system_properties.h>

int eapps_clipboard_get(char *buf, uint32_t buf_size)
{
    (void)buf;
    (void)buf_size;
    return -1;
}

int eapps_clipboard_set(const char *text)
{
    (void)text;
    return -1;
}

int eapps_sysinfo_hostname(char *buf, uint32_t buf_size)
{
    if(buf == NULL || buf_size == 0) return -1;

    char model[128] = {0};
    __system_property_get("ro.product.model", model);

    if(model[0] == '\0') {
        strncpy(buf, "Android", buf_size - 1);
    } else {
        strncpy(buf, model, buf_size - 1);
    }
    buf[buf_size - 1] = '\0';
    return 0;
}

const char *eapps_sysinfo_os(void)
{
    return "Android";
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
    if(pages <= 0 || page_size <= 0) return 0;
    return (uint64_t)pages * (uint64_t)page_size;
}

uint32_t eapps_tick_get_ms(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint32_t)(ts.tv_sec * 1000 + ts.tv_nsec / 1000000);
}

int eapps_keepawake_enable(void)
{
    return 0;
}

int eapps_keepawake_disable(void)
{
    return 0;
}

int eapps_process_launch(const char *cmd)
{
    (void)cmd;
    return -1;
}

#endif /* __ANDROID__ */
