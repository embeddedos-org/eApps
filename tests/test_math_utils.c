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

int main(void) {
    test_clamp();
    test_lerp();
    test_format_file_size();
    printf("test_math_utils: %d passed, %d failed\n", passes, failures);
    return failures > 0 ? 1 : 0;
}
