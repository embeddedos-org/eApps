// SPDX-License-Identifier: MIT
#include <stdio.h>
#include <string.h>
#include "../core/common/include/eapps/registry.h"

#define EAPPS_ASSERT(cond, msg) do { \
    if (!(cond)) { fprintf(stderr, "FAIL: %s (%s:%d)\n", msg, __FILE__, __LINE__); failures++; } \
    else { passes++; } \
} while(0)

static int passes = 0, failures = 0;

static bool stub_init(lv_obj_t *p) { (void)p; return true; }
static void stub_deinit(void) {}

int main(void) {
    eapps_registry_init();
    EAPPS_ASSERT(eapps_registry_count() == 0, "empty registry");

    eapps_app_info_t info1 = { .id="test1", .name="Test App 1", .icon="t1",
                                .description="First test app", .category=EAPPS_CAT_PRODUCTIVITY, .version="1.0" };
    eapps_app_lifecycle_t lc1 = { .init=stub_init, .deinit=stub_deinit };
    EAPPS_ASSERT(eapps_registry_register(&info1, &lc1) == true, "register 1");
    EAPPS_ASSERT(eapps_registry_count() == 1, "count after register");

    eapps_app_info_t info2 = { .id="test2", .name="Game App", .icon="g1",
                                .description="A game", .category=EAPPS_CAT_GAMES, .version="1.0" };
    eapps_registry_register(&info2, &lc1);

    const eapps_registry_entry_t *e = eapps_registry_find("test1");
    EAPPS_ASSERT(e != NULL, "find test1");
    EAPPS_ASSERT(strcmp(e->info.name, "Test App 1") == 0, "find test1 name");

    EAPPS_ASSERT(eapps_registry_find("nonexistent") == NULL, "find missing");

    const eapps_registry_entry_t *results[10];
    int n = eapps_registry_search("test", results, 10);
    EAPPS_ASSERT(n == 1, "search test");

    n = eapps_registry_list_by_category(EAPPS_CAT_GAMES, results, 10);
    EAPPS_ASSERT(n == 1, "category games");

    const eapps_app_lifecycle_t *lc = eapps_registry_get_lifecycle("test1");
    EAPPS_ASSERT(lc != NULL && lc->init != NULL, "get lifecycle");

    eapps_registry_deinit();
    EAPPS_ASSERT(eapps_registry_count() == 0, "count after deinit");

    printf("test_registry: %d passed, %d failed\n", passes, failures);
    return failures > 0 ? 1 : 0;
}
