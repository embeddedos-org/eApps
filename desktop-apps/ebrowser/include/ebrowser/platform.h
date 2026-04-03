// SPDX-License-Identifier: MIT
#ifndef eBrowser_PLATFORM_H
#define eBrowser_PLATFORM_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef enum {
    EB_PLATFORM_LINUX,
    EB_PLATFORM_RTOS,
    EB_PLATFORM_BAREMETAL,
    EB_PLATFORM_WINDOWS,
    EB_PLATFORM_WEB,
    EB_PLATFORM_UNKNOWN
} eb_platform_type_t;

eb_platform_type_t eb_platform_detect(void);
const char        *eb_platform_name(void);
uint32_t           eb_platform_tick_ms(void);
void               eb_platform_sleep_ms(uint32_t ms);
void              *eb_platform_alloc(size_t size);
void               eb_platform_free(void *ptr);
size_t             eb_platform_available_memory(void);
bool               eb_platform_file_exists(const char *path);
int                eb_platform_read_file(const char *path, char **out_buf, size_t *out_len);

#endif /* eBrowser_PLATFORM_H */
