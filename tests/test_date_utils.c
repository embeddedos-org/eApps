// SPDX-License-Identifier: MIT
#include <stdio.h>
#include <string.h>
#include "../core/common/include/eapps/date_utils.h"

#define EAPPS_ASSERT(cond, msg) do { \
    if (!(cond)) { fprintf(stderr, "FAIL: %s (%s:%d)\n", msg, __FILE__, __LINE__); failures++; } \
    else { passes++; } \
} while(0)

static int passes = 0, failures = 0;

static void test_format_duration(void) {
    char buf[32];
    eapps_format_duration(90, buf, sizeof(buf));
    EAPPS_ASSERT(strcmp(buf, "1:30") == 0, "90s = 1:30");

    eapps_format_duration(3661, buf, sizeof(buf));
    EAPPS_ASSERT(strcmp(buf, "1:01:01") == 0, "3661s = 1:01:01");

    eapps_format_duration(0, buf, sizeof(buf));
    EAPPS_ASSERT(strcmp(buf, "0:00") == 0, "0s = 0:00");
}

static void test_time_ago(void) {
    char buf[64];
    time_t now = time(NULL);

    eapps_time_ago(now, buf, sizeof(buf));
    EAPPS_ASSERT(strcmp(buf, "just now") == 0, "just now");

    eapps_time_ago(now - 120, buf, sizeof(buf));
    EAPPS_ASSERT(strcmp(buf, "2 min ago") == 0, "2 min ago");

    eapps_time_ago(now - 7200, buf, sizeof(buf));
    EAPPS_ASSERT(strcmp(buf, "2 hr ago") == 0, "2 hr ago");
}

int main(void) {
    test_format_duration();
    test_time_ago();
    printf("test_date_utils: %d passed, %d failed\n", passes, failures);
    return failures > 0 ? 1 : 0;
}
