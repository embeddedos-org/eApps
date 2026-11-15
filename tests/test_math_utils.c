// SPDX-License-Identifier: MIT
#include <stdio.h>
#include <string.h>
#include "../core/common/include/eapps/math_utils.h"

#define EAPPS_ASSERT(cond, msg) do { \
    if (!(cond)) { fprintf(stderr, "FAIL: %s (%s:%d)\n", msg, __FILE__, __LINE__); failures++; } \
    else { passes++; } \
} while(0)

static int passes = 0, failures = 0;

static void test_clamp(void) {
    EAPPS_ASSERT(eapps_clamp(5, 0, 10) == 5, "clamp mid");
    EAPPS_ASSERT(eapps_clamp(-1, 0, 10) == 0, "clamp low");
    EAPPS_ASSERT(eapps_clamp(15, 0, 10) == 10, "clamp high");
    EAPPS_ASSERT(eapps_clamp(0, 0, 10) == 0, "clamp boundary low");
    EAPPS_ASSERT(eapps_clamp(10, 0, 10) == 10, "clamp boundary high");
}

static void test_lerp(void) {
    EAPPS_ASSERT(eapps_lerp(0.0f, 10.0f, 0.0f) == 0.0f, "lerp 0");
    EAPPS_ASSERT(eapps_lerp(0.0f, 10.0f, 1.0f) == 10.0f, "lerp 1");
    EAPPS_ASSERT(eapps_lerp(0.0f, 10.0f, 0.5f) == 5.0f, "lerp 0.5");
}

static void test_format_file_size(void) {
    char buf[32];
    eapps_format_file_size(512, buf, sizeof(buf));
    EAPPS_ASSERT(strcmp(buf, "512 B") == 0, "512 bytes");

    eapps_format_file_size(1536, buf, sizeof(buf));
    EAPPS_ASSERT(strcmp(buf, "1.5 KB") == 0, "1.5 KB");

    eapps_format_file_size(1048576, buf, sizeof(buf));
    EAPPS_ASSERT(strcmp(buf, "1.0 MB") == 0, "1 MB");
}

/* A size that rounds up to 1024.0 of one unit is shown as 1.0 of the next. */
static void check_size(unsigned long long bytes, const char *want) {
    char buf[32], msg[96];
    eapps_format_file_size(bytes, buf, sizeof(buf));
    printf("  %llu bytes -> \"%s\"\n", bytes, buf);
    snprintf(msg, sizeof(msg), "%llu bytes: want \"%s\", got \"%s\"", bytes, want, buf);
    EAPPS_ASSERT(strcmp(buf, want) == 0, msg);
}

static void test_format_file_size_unit_rollover(void) {
    check_size(1023ULL, "1023 B");
    check_size(1048524ULL, "1023.9 KB");     /* 1023.949 KB stays in KB */
    check_size(1048525ULL, "1.0 MB");        /* 1023.950 KB rounds to 1024.0 */
    check_size(1048575ULL, "1.0 MB");        /* 1 MiB - 1 byte */
    check_size(1073741823ULL, "1.0 GB");     /* 1 GiB - 1 byte */
    check_size(1099511627775ULL, "1.0 TB");  /* 1 TiB - 1 byte */
}

int main(void) {
    test_clamp();
    test_lerp();
    test_format_file_size();
    test_format_file_size_unit_rollover();
    printf("test_math_utils: %d passed, %d failed\n", passes, failures);
    return failures > 0 ? 1 : 0;
}
