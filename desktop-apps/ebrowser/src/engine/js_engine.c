// SPDX-License-Identifier: MIT
#include "eBrowser/js_engine.h"
#include <string.h>
#include <stdio.h>

eb_js_config_t eb_js_config_default(void) {
    eb_js_config_t c = {0};
    c.memory_limit = 4 * 1024 * 1024;
    c.max_execution_ms = 5000;
    c.enable_console = true;
    return c;
}

bool eb_js_init(eb_js_ctx_t *ctx, const eb_js_config_t *config) {
    if (!ctx) return false;
    memset(ctx, 0, sizeof(eb_js_ctx_t));
    ctx->config = config ? *config : eb_js_config_default();
    ctx->initialized = true;
    ctx->next_timer_id = 1;
    return true;
}

bool eb_js_set_document(eb_js_ctx_t *ctx, eb_dom_node_t *doc) {
    if (!ctx || !ctx->initialized) return false;
    ctx->document = doc;
    return true;
}

bool eb_js_eval(eb_js_ctx_t *ctx, const char *script, size_t len) {
    if (!ctx || !ctx->initialized || !script || len == 0) return false;
    if (ctx->config.enable_console) {
        if (strstr(script, "console.log") != NULL) {
            const char *start = strstr(script, "console.log(");
            if (start) {
                start += 12;
                const char *end = strchr(start, ')');
                if (end && end > start) {
                    const char *q1 = strchr(start, '"');
                    const char *q2 = q1 ? strchr(q1 + 1, '"') : NULL;
                    if (!q1) { q1 = strchr(start, '\''); q2 = q1 ? strchr(q1 + 1, '\'') : NULL; }
                    if (q1 && q2 && q2 > q1 + 1) {
                        size_t msg_len = (size_t)(q2 - q1 - 1);
                        if (ctx->console_len + msg_len + 2 < sizeof(ctx->console_output)) {
                            memcpy(ctx->console_output + ctx->console_len, q1 + 1, msg_len);
                            ctx->console_len += msg_len;
                            ctx->console_output[ctx->console_len++] = '\n';
                            ctx->console_output[ctx->console_len] = '\0';
                        }
                    }
                }
            }
        }
    }
    return true;
}

bool eb_js_call_function(eb_js_ctx_t *ctx, const char *name) {
    if (!ctx || !ctx->initialized || !name) return false;
    return true;
}

int eb_js_set_timeout(eb_js_ctx_t *ctx, const char *callback, int ms) {
    if (!ctx || !ctx->initialized || !callback || ctx->timer_count >= EB_JS_MAX_TIMERS) return -1;
    eb_js_timer_t *t = &ctx->timers[ctx->timer_count++];
    t->id = ctx->next_timer_id++;
    t->interval_ms = ms;
    t->repeat = false;
    t->active = true;
    t->elapsed_ms = 0;
    strncpy(t->callback_src, callback, sizeof(t->callback_src) - 1);
    return t->id;
}

int eb_js_set_interval(eb_js_ctx_t *ctx, const char *callback, int ms) {
    if (!ctx || !ctx->initialized || !callback || ctx->timer_count >= EB_JS_MAX_TIMERS) return -1;
    eb_js_timer_t *t = &ctx->timers[ctx->timer_count++];
    t->id = ctx->next_timer_id++;
    t->interval_ms = ms;
    t->repeat = true;
    t->active = true;
    t->elapsed_ms = 0;
    strncpy(t->callback_src, callback, sizeof(t->callback_src) - 1);
    return t->id;
}

bool eb_js_clear_timer(eb_js_ctx_t *ctx, int timer_id) {
    if (!ctx) return false;
    for (int i = 0; i < ctx->timer_count; i++) {
        if (ctx->timers[i].id == timer_id) { ctx->timers[i].active = false; return true; }
    }
    return false;
}

void eb_js_tick(eb_js_ctx_t *ctx, int elapsed_ms) {
    if (!ctx || !ctx->initialized) return;
    for (int i = 0; i < ctx->timer_count; i++) {
        eb_js_timer_t *t = &ctx->timers[i];
        if (!t->active) continue;
        t->elapsed_ms += elapsed_ms;
        if (t->elapsed_ms >= t->interval_ms) {
            eb_js_eval(ctx, t->callback_src, strlen(t->callback_src));
            if (t->repeat) t->elapsed_ms = 0;
            else t->active = false;
        }
    }
}

const char *eb_js_get_console_output(const eb_js_ctx_t *ctx) {
    if (!ctx) return "";
    return ctx->console_output;
}

void eb_js_console_log(eb_js_ctx_t *ctx, const char *msg) {
    if (!ctx || !msg) return;
    size_t len = strlen(msg);
    if (ctx->console_len + len + 2 < sizeof(ctx->console_output)) {
        memcpy(ctx->console_output + ctx->console_len, msg, len);
        ctx->console_len += len;
        ctx->console_output[ctx->console_len++] = '\n';
        ctx->console_output[ctx->console_len] = '\0';
    }
}

void eb_js_deinit(eb_js_ctx_t *ctx) {
    if (!ctx) return;
    ctx->initialized = false;
    ctx->document = NULL;
}
