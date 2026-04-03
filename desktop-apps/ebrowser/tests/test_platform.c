// SPDX-License-Identifier: MIT
// Platform abstraction layer tests for eBrowser web browser
#include "eBrowser/platform.h"
#include <stdio.h>
#include <string.h>

static int s_pass = 0, s_fail = 0;
#define TEST(name) static void name(void)
#define RUN(name) do { printf("  %s... ", #name); name(); printf("PASS\n"); s_pass++; } while(0)
#define ASSERT(cond) do { if(!(cond)) { printf("FAIL: %s:%d: %s\n", __FILE__, __LINE__, #cond); s_fail++; return; } } while(0)

TEST(test_platform_detect) {
    eb_platform_type_t p = eb_platform_detect();
    ASSERT(p == EB_PLATFORM_LINUX || p == EB_PLATFORM_WINDOWS ||
           p == EB_PLATFORM_RTOS || p == EB_PLATFORM_WEB ||
           p == EB_PLATFORM_BAREMETAL || p == EB_PLATFORM_UNKNOWN);
}

TEST(test_platform_name_not_null) {
    const char *name = eb_platform_name();
    ASSERT(name != NULL);
    ASSERT(strlen(name) > 0);
}

TEST(test_platform_name_known) {
    const char *name = eb_platform_name();
    ASSERT(strcmp(name, "Linux") == 0 || strcmp(name, "Windows") == 0 ||
           strcmp(name, "RTOS") == 0 || strcmp(name, "Web") == 0 ||
           strcmp(name, "Bare-metal") == 0 || strcmp(name, "Unknown") == 0);
}

TEST(test_platform_alloc_free) {
    void *ptr = eb_platform_alloc(1024);
    ASSERT(ptr != NULL);
    memset(ptr, 0xAA, 1024);
    eb_platform_free(ptr);
}

TEST(test_platform_alloc_zero) {
    void *ptr = eb_platform_alloc(0);
    eb_platform_free(ptr);
}

TEST(test_platform_alloc_large) {
    void *ptr = eb_platform_alloc(1024 * 1024);
    ASSERT(ptr != NULL);
    eb_platform_free(ptr);
}

TEST(test_platform_free_null) {
    eb_platform_free(NULL);
}

TEST(test_platform_tick_ms) {
    uint32_t tick = eb_platform_tick_ms();
    (void)tick;
}

TEST(test_platform_file_exists_null) {
    ASSERT(eb_platform_file_exists(NULL) == false);
}

TEST(test_platform_file_exists_nonexistent) {
    ASSERT(eb_platform_file_exists("/nonexistent/path/file.txt") == false);
}

TEST(test_platform_read_file_null) {
    ASSERT(eb_platform_read_file(NULL, NULL, NULL) == -1);
    char *buf; size_t len;
    ASSERT(eb_platform_read_file(NULL, &buf, &len) == -1);
}

TEST(test_platform_read_file_nonexistent) {
    char *buf; size_t len;
    ASSERT(eb_platform_read_file("/nonexistent/file.txt", &buf, &len) == -1);
}

TEST(test_platform_available_memory) {
    size_t mem = eb_platform_available_memory();
    (void)mem;
}

int main(void) {
    printf("=== Platform Tests ===\n");
    RUN(test_platform_detect);
    RUN(test_platform_name_not_null);
    RUN(test_platform_name_known);
    RUN(test_platform_alloc_free);
    RUN(test_platform_alloc_zero);
    RUN(test_platform_alloc_large);
    RUN(test_platform_free_null);
    RUN(test_platform_tick_ms);
    RUN(test_platform_file_exists_null);
    RUN(test_platform_file_exists_nonexistent);
    RUN(test_platform_read_file_null);
    RUN(test_platform_read_file_nonexistent);
    RUN(test_platform_available_memory);
    printf("\nResults: %d passed, %d failed\n", s_pass, s_fail);
    return s_fail > 0 ? 1 : 0;
}
