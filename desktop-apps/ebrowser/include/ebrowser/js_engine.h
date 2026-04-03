// SPDX-License-Identifier: MIT
#ifndef eBrowser_JS_ENGINE_H
#define eBrowser_JS_ENGINE_H

#include <stdbool.h>
#include <stddef.h>
#include "eBrowser/dom.h"

#define EB_JS_MAX_TIMERS 32

typedef struct eb_js_ctx eb_js_ctx_t;

typedef struct {
    size_t memory_limit;
    int    max_execution_ms;
    bool   enable_console;
} eb_js_config_t;

typedef struct {
    int    id;
    int    interval_ms;
    bool   repeat;
    bool   active;
    int    elapsed_ms;
    char   callback_src[256];
} eb_js_timer_t;

struct eb_js_ctx {
    eb_js_config_t config;
    eb_dom_node_t *document;
    bool           initialized;
    eb_js_timer_t  timers[EB_JS_MAX_TIMERS];
    int            timer_count;
    int            next_timer_id;
    char           console_output[4096];
    size_t         console_len;
};

eb_js_config_t eb_js_config_default(void);
bool           eb_js_init(eb_js_ctx_t *ctx, const eb_js_config_t *config);
bool           eb_js_set_document(eb_js_ctx_t *ctx, eb_dom_node_t *doc);
bool           eb_js_eval(eb_js_ctx_t *ctx, const char *script, size_t len);
bool           eb_js_call_function(eb_js_ctx_t *ctx, const char *name);
int            eb_js_set_timeout(eb_js_ctx_t *ctx, const char *callback, int ms);
int            eb_js_set_interval(eb_js_ctx_t *ctx, const char *callback, int ms);
bool           eb_js_clear_timer(eb_js_ctx_t *ctx, int timer_id);
void           eb_js_tick(eb_js_ctx_t *ctx, int elapsed_ms);
const char    *eb_js_get_console_output(const eb_js_ctx_t *ctx);
void           eb_js_console_log(eb_js_ctx_t *ctx, const char *msg);
void           eb_js_deinit(eb_js_ctx_t *ctx);

#endif
