// SPDX-License-Identifier: MIT
#include "eBrowser/logger.h"
#include <stdio.h>
#include <stdarg.h>
#include <string.h>

static eb_log_level_t s_level = EB_LOG_INFO;
static eb_log_callback_t s_callback = NULL;

void eb_log_init(void) { s_level = EB_LOG_INFO; s_callback = NULL; }
void eb_log_set_level(eb_log_level_t level) { s_level = level; }
eb_log_level_t eb_log_get_level(void) { return s_level; }
void eb_log_set_callback(eb_log_callback_t cb) { s_callback = cb; }

const char *eb_log_level_name(eb_log_level_t level) {
    switch (level) {
        case EB_LOG_TRACE: return "TRACE"; case EB_LOG_DEBUG: return "DEBUG";
        case EB_LOG_INFO:  return "INFO";  case EB_LOG_WARN:  return "WARN";
        case EB_LOG_ERROR: return "ERROR"; case EB_LOG_FATAL: return "FATAL";
        default: return "?";
    }
}

void eb_log_write(eb_log_level_t level, const char *module, const char *fmt, ...) {
    if (level < s_level) return;
    char buf[1024];
    va_list ap; va_start(ap, fmt); vsnprintf(buf, sizeof(buf), fmt, ap); va_end(ap);
    if (s_callback) { s_callback(level, module, buf); return; }
    fprintf(level >= EB_LOG_ERROR ? stderr : stdout, "[%s][%s] %s\n",
            eb_log_level_name(level), module ? module : "-", buf);
}
