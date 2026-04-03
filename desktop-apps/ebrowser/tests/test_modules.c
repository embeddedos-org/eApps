// SPDX-License-Identifier: MIT
#include "eBrowser/js_engine.h"
#include "eBrowser/cache.h"
#include "eBrowser/cookies.h"
#include "eBrowser/logger.h"
#include "eBrowser/metrics.h"
#include "eBrowser/plugin.h"
#include "eBrowser/permissions.h"
#include <stdio.h>
#include <string.h>

static int s_pass = 0, s_fail = 0;
#define TEST(name) static void name(void)
#define RUN(name) do { printf("  %s... ", #name); name(); printf("PASS\n"); s_pass++; } while(0)
#define ASSERT(cond) do { if(!(cond)) { printf("FAIL: %s:%d: %s\n", __FILE__, __LINE__, #cond); s_fail++; return; } } while(0)

TEST(test_js_init) {
    eb_js_ctx_t ctx;
    ASSERT(eb_js_init(&ctx, NULL));
    ASSERT(ctx.initialized);
    ASSERT(ctx.config.memory_limit == 4 * 1024 * 1024);
    eb_js_deinit(&ctx);
    ASSERT(!ctx.initialized);
}

TEST(test_js_console_log) {
    eb_js_ctx_t ctx;
    eb_js_init(&ctx, NULL);
    eb_js_console_log(&ctx, "hello");
    ASSERT(strstr(eb_js_get_console_output(&ctx), "hello") != NULL);
    eb_js_deinit(&ctx);
}

TEST(test_js_eval_console) {
    eb_js_ctx_t ctx;
    eb_js_init(&ctx, NULL);
    const char *script = "console.log(\"world\")";
    eb_js_eval(&ctx, script, strlen(script));
    ASSERT(strstr(eb_js_get_console_output(&ctx), "world") != NULL);
    eb_js_deinit(&ctx);
}

TEST(test_js_timers) {
    eb_js_ctx_t ctx;
    eb_js_init(&ctx, NULL);
    int id1 = eb_js_set_timeout(&ctx, "console.log(\"t1\")", 100);
    ASSERT(id1 > 0);
    int id2 = eb_js_set_interval(&ctx, "console.log(\"t2\")", 200);
    ASSERT(id2 > 0);
    ASSERT(eb_js_clear_timer(&ctx, id1));
    ASSERT(!eb_js_clear_timer(&ctx, 999));
    eb_js_deinit(&ctx);
}

TEST(test_cache_basic) {
    static eb_cache_t cache;
    eb_cache_init(&cache, 1024 * 1024);
    const uint8_t data[] = "hello cache";
    ASSERT(eb_cache_put(&cache, "http://example.com", data, sizeof(data), "etag1", 3600));
    eb_cache_entry_t *e = eb_cache_get(&cache, "http://example.com");
    ASSERT(e != NULL);
    ASSERT(e->data_len == sizeof(data));
    ASSERT(memcmp(e->data, data, sizeof(data)) == 0);
    ASSERT(eb_cache_get(&cache, "http://missing.com") == NULL);
    eb_cache_invalidate(&cache, "http://example.com");
    ASSERT(eb_cache_get(&cache, "http://example.com") == NULL);
    eb_cache_clear(&cache);
}

TEST(test_cookies_basic) {
    eb_cookie_jar_t jar;
    eb_cookie_jar_init(&jar);
    ASSERT(eb_cookie_jar_parse_set_cookie(&jar, "name=value; Path=/; Secure; HttpOnly", "example.com"));
    ASSERT(eb_cookie_jar_count(&jar) == 1);
    char buf[512];
    int n = eb_cookie_jar_get_for_url(&jar, "https://example.com/page", true, buf, sizeof(buf));
    ASSERT(n == 1);
    ASSERT(strstr(buf, "name=value") != NULL);
    n = eb_cookie_jar_get_for_url(&jar, "http://example.com/page", false, buf, sizeof(buf));
    ASSERT(n == 0);
    eb_cookie_jar_remove(&jar, "name", "example.com");
    ASSERT(eb_cookie_jar_count(&jar) == 0);
    eb_cookie_jar_clear(&jar);
}

TEST(test_cookies_set) {
    eb_cookie_jar_t jar;
    eb_cookie_jar_init(&jar);
    ASSERT(eb_cookie_jar_set(&jar, "session", "abc123", "test.com", "/api", 3600));
    ASSERT(eb_cookie_jar_count(&jar) == 1);
    eb_cookie_jar_clear(&jar);
}

static int s_log_count = 0;
static void test_log_cb(eb_log_level_t level, const char *module, const char *msg) {
    (void)level; (void)module; (void)msg; s_log_count++;
}

TEST(test_logger) {
    eb_log_init();
    ASSERT(eb_log_get_level() == EB_LOG_INFO);
    eb_log_set_level(EB_LOG_DEBUG);
    ASSERT(eb_log_get_level() == EB_LOG_DEBUG);
    ASSERT(strcmp(eb_log_level_name(EB_LOG_ERROR), "ERROR") == 0);
    s_log_count = 0;
    eb_log_set_callback(test_log_cb);
    eb_log_write(EB_LOG_INFO, "TEST", "hello %d", 42);
    ASSERT(s_log_count == 1);
    eb_log_write(EB_LOG_TRACE, "TEST", "filtered");
    ASSERT(s_log_count == 1);
    eb_log_set_callback(NULL);
}

TEST(test_metrics) {
    eb_metrics_t m;
    eb_metrics_init(&m);
    ASSERT(m.parse_time_us == 0);
    eb_metrics_record_parse(&m, 100);
    eb_metrics_record_layout(&m, 200);
    eb_metrics_record_render(&m, 300);
    eb_metrics_tick_frame(&m);
    ASSERT(m.parse_time_us == 100);
    ASSERT(m.layout_time_us == 200);
    ASSERT(m.render_time_us == 300);
    ASSERT(m.frame_count == 1);
    eb_metrics_reset(&m);
    ASSERT(m.frame_count == 0);
}

static bool test_plugin_init_called = false;
static bool test_plugin_init_fn(void *ud) { (void)ud; test_plugin_init_called = true; return true; }
static bool test_plugin_hook_fn(eb_plugin_hook_t hook, const eb_plugin_event_t *ev, void *ud) { (void)hook; (void)ev; (void)ud; return true; }

TEST(test_plugin_system) {
    eb_plugin_manager_t mgr;
    eb_plugin_manager_init(&mgr);
    eb_plugin_t p;
    memset(&p, 0, sizeof(p));
    strncpy(p.name, "test_plugin", EB_PLUGIN_MAX_NAME - 1);
    strncpy(p.version, "1.0", 15);
    p.priority = 10;
    p.init = test_plugin_init_fn;
    p.on_event = test_plugin_hook_fn;
    p.hooks[EB_HOOK_ON_PAGE_LOAD] = true;
    test_plugin_init_called = false;
    ASSERT(eb_plugin_register(&mgr, &p));
    ASSERT(test_plugin_init_called);
    ASSERT(mgr.count == 1);
    ASSERT(!eb_plugin_register(&mgr, &p));
    ASSERT(eb_plugin_find(&mgr, "test_plugin") != NULL);
    ASSERT(eb_plugin_find(&mgr, "nonexistent") == NULL);
    eb_plugin_event_t ev;
    memset(&ev, 0, sizeof(ev));
    ev.url = "http://test.com";
    ASSERT(eb_plugin_dispatch(&mgr, EB_HOOK_ON_PAGE_LOAD, &ev) == 1);
    ASSERT(eb_plugin_dispatch(&mgr, EB_HOOK_ON_RENDER, &ev) == 0);
    ASSERT(eb_plugin_disable(&mgr, "test_plugin"));
    ASSERT(eb_plugin_dispatch(&mgr, EB_HOOK_ON_PAGE_LOAD, &ev) == 0);
    ASSERT(eb_plugin_enable(&mgr, "test_plugin"));
    ASSERT(eb_plugin_unregister(&mgr, "test_plugin"));
    ASSERT(mgr.count == 0);
    eb_plugin_manager_shutdown(&mgr);
}

TEST(test_permissions) {
    eb_permission_ctx_t ctx;
    eb_permissions_init(&ctx, "https://example.com");
    ASSERT(eb_permissions_query(&ctx, EB_PERM_STORAGE) == EB_PERM_STATE_GRANTED);
    ASSERT(eb_permissions_query(&ctx, EB_PERM_CAMERA) == EB_PERM_STATE_DENIED);
    ASSERT(!eb_permissions_request(&ctx, EB_PERM_CAMERA));
    ASSERT(strcmp(eb_permission_name(EB_PERM_CAMERA), "camera") == 0);
    ASSERT(strcmp(eb_permission_name(EB_PERM_GEOLOCATION), "geolocation") == 0);
    eb_permissions_revoke(&ctx, EB_PERM_STORAGE);
    ASSERT(eb_permissions_query(&ctx, EB_PERM_STORAGE) == EB_PERM_STATE_DENIED);
}

int main(void) {
    printf("=== Phase 2-7 Module Tests ===\n");
    RUN(test_js_init);
    RUN(test_js_console_log);
    RUN(test_js_eval_console);
    RUN(test_js_timers);
    RUN(test_cache_basic);
    RUN(test_cookies_basic);
    RUN(test_cookies_set);
    RUN(test_logger);
    RUN(test_metrics);
    RUN(test_plugin_system);
    RUN(test_permissions);
    printf("\nResults: %d passed, %d failed\n", s_pass, s_fail);
    return s_fail > 0 ? 1 : 0;
}
