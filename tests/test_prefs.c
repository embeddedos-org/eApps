// SPDX-License-Identifier: MIT
#include <stdio.h>
#include <string.h>
#include "../core/storage/include/eapps/prefs.h"

#define EAPPS_ASSERT(cond, msg) do { \
    if (!(cond)) { fprintf(stderr, "FAIL: %s (%s:%d)\n", msg, __FILE__, __LINE__); failures++; } \
    else { passes++; } \
} while(0)

static int passes = 0, failures = 0;

int main(void) {
    eapps_prefs_t *p = eapps_prefs_init("test_prefs");
    EAPPS_ASSERT(p != NULL, "prefs init");

    eapps_prefs_set_string(p, "name", "test_value");
    EAPPS_ASSERT(strcmp(eapps_prefs_get_string(p, "name", ""), "test_value") == 0, "set/get string");

    EAPPS_ASSERT(strcmp(eapps_prefs_get_string(p, "missing", "default"), "default") == 0, "default string");

    eapps_prefs_set_int(p, "score", 42);
    EAPPS_ASSERT(eapps_prefs_get_int(p, "score", 0) == 42, "set/get int");
    EAPPS_ASSERT(eapps_prefs_get_int(p, "missing_int", -1) == -1, "default int");

    eapps_prefs_set_bool(p, "enabled", true);
    EAPPS_ASSERT(eapps_prefs_get_bool(p, "enabled", false) == true, "set/get bool true");
    eapps_prefs_set_bool(p, "enabled", false);
    EAPPS_ASSERT(eapps_prefs_get_bool(p, "enabled", true) == false, "set/get bool false");

    EAPPS_ASSERT(eapps_prefs_save(p) == true, "save");
    eapps_prefs_deinit(p);

    /* Test persistence by re-loading */
    p = eapps_prefs_init("test_prefs");
    EAPPS_ASSERT(strcmp(eapps_prefs_get_string(p, "name", ""), "test_value") == 0, "persist string");
    EAPPS_ASSERT(eapps_prefs_get_int(p, "score", 0) == 42, "persist int");
    eapps_prefs_deinit(p);

    /* Cleanup test file */
    remove("test_prefs.ini");

    printf("test_prefs: %d passed, %d failed\n", passes, failures);
    return failures > 0 ? 1 : 0;
}
