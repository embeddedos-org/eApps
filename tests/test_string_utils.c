// SPDX-License-Identifier: MIT
#include <stdio.h>
#include <string.h>
#include "../core/common/include/eapps/string_utils.h"

#define EAPPS_ASSERT(cond, msg) do { \
    if (!(cond)) { fprintf(stderr, "FAIL: %s (%s:%d)\n", msg, __FILE__, __LINE__); failures++; } \
    else { passes++; } \
} while(0)

static int passes = 0, failures = 0;

static void test_truncate(void) {
    char buf[16];
    eapps_str_truncate("Hello", buf, 10);
    EAPPS_ASSERT(strcmp(buf, "Hello") == 0, "no truncation");

    eapps_str_truncate("Hello World This Is Long", buf, 10);
    EAPPS_ASSERT(strcmp(buf, "Hello W...") == 0, "truncated");
}

static void test_base64(void) {
    const uint8_t data[] = "Hello";
    char encoded[32];
    uint8_t decoded[32];

    int elen = eapps_base64_encode(data, 5, encoded, sizeof(encoded));
    EAPPS_ASSERT(elen > 0, "b64 encode");
    EAPPS_ASSERT(strcmp(encoded, "SGVsbG8=") == 0, "b64 encode value");

    int dlen = eapps_base64_decode(encoded, decoded, sizeof(decoded));
    EAPPS_ASSERT(dlen == 5, "b64 decode len");
    EAPPS_ASSERT(memcmp(decoded, "Hello", 5) == 0, "b64 roundtrip");
}

static void test_case_insensitive(void) {
    EAPPS_ASSERT(eapps_str_contains_ci("Hello World", "hello") == true, "ci search found");
    EAPPS_ASSERT(eapps_str_contains_ci("Hello World", "xyz") == false, "ci search not found");
}

static void test_to_lower_upper(void) {
    char buf[16] = "Hello";
    eapps_str_to_lower(buf);
    EAPPS_ASSERT(strcmp(buf, "hello") == 0, "to_lower");

    eapps_str_to_upper(buf);
    EAPPS_ASSERT(strcmp(buf, "HELLO") == 0, "to_upper");
}

int main(void) {
    test_truncate();
    test_base64();
    test_case_insensitive();
    test_to_lower_upper();
    printf("test_string_utils: %d passed, %d failed\n", passes, failures);
    return failures > 0 ? 1 : 0;
}
