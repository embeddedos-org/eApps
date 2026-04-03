// SPDX-License-Identifier: MIT
#ifndef eBrowser_LOGGER_H
#define eBrowser_LOGGER_H

#include <stdbool.h>
#include <stddef.h>

typedef enum {
    EB_LOG_TRACE,
    EB_LOG_DEBUG,
    EB_LOG_INFO,
    EB_LOG_WARN,
    EB_LOG_ERROR,
    EB_LOG_FATAL
} eb_log_level_t;

typedef void (*eb_log_callback_t)(eb_log_level_t level, const char *module, const char *msg);

void           eb_log_init(void);
void           eb_log_set_level(eb_log_level_t level);
eb_log_level_t eb_log_get_level(void);
void           eb_log_set_callback(eb_log_callback_t cb);
void           eb_log_write(eb_log_level_t level, const char *module, const char *fmt, ...);
const char    *eb_log_level_name(eb_log_level_t level);

#define EB_LOG_T(mod, ...) eb_log_write(EB_LOG_TRACE, mod, __VA_ARGS__)
#define EB_LOG_D(mod, ...) eb_log_write(EB_LOG_DEBUG, mod, __VA_ARGS__)
#define EB_LOG_I(mod, ...) eb_log_write(EB_LOG_INFO,  mod, __VA_ARGS__)
#define EB_LOG_W(mod, ...) eb_log_write(EB_LOG_WARN,  mod, __VA_ARGS__)
#define EB_LOG_E(mod, ...) eb_log_write(EB_LOG_ERROR, mod, __VA_ARGS__)
#define EB_LOG_F(mod, ...) eb_log_write(EB_LOG_FATAL, mod, __VA_ARGS__)

#endif
