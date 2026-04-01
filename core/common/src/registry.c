// SPDX-License-Identifier: MIT
#include "eapps/registry.h"
#include <string.h>
#include <ctype.h>

static eapps_registry_entry_t s_entries[EAPPS_MAX_APPS];
static int s_count = 0;

void eapps_registry_init(void) {
    s_count = 0;
    memset(s_entries, 0, sizeof(s_entries));
}

void eapps_registry_deinit(void) {
    s_count = 0;
}

bool eapps_registry_register(const eapps_app_info_t *info, const eapps_app_lifecycle_t *lc) {
    if (!info || !lc || s_count >= EAPPS_MAX_APPS) return false;
    s_entries[s_count].info = *info;
    s_entries[s_count].lifecycle = *lc;
    s_count++;
    return true;
}

const eapps_registry_entry_t *eapps_registry_find(const char *id) {
    if (!id) return NULL;
    for (int i = 0; i < s_count; i++) {
        if (strcmp(s_entries[i].info.id, id) == 0) return &s_entries[i];
    }
    return NULL;
}

static bool ci_contains(const char *haystack, const char *needle) {
    if (!haystack || !needle) return false;
    size_t hlen = strlen(haystack), nlen = strlen(needle);
    if (nlen > hlen) return false;
    for (size_t i = 0; i <= hlen - nlen; i++) {
        bool match = true;
        for (size_t j = 0; j < nlen; j++) {
            if (tolower((unsigned char)haystack[i + j]) != tolower((unsigned char)needle[j])) {
                match = false;
                break;
            }
        }
        if (match) return true;
    }
    return false;
}

int eapps_registry_search(const char *query, const eapps_registry_entry_t **out, int max) {
    if (!query || !out || max <= 0) return 0;
    int found = 0;
    for (int i = 0; i < s_count && found < max; i++) {
        if (ci_contains(s_entries[i].info.name, query) ||
            ci_contains(s_entries[i].info.description, query) ||
            ci_contains(s_entries[i].info.id, query)) {
            out[found++] = &s_entries[i];
        }
    }
    return found;
}

int eapps_registry_list_by_category(eapps_category_t cat, const eapps_registry_entry_t **out, int max) {
    if (!out || max <= 0) return 0;
    int found = 0;
    for (int i = 0; i < s_count && found < max; i++) {
        if (s_entries[i].info.category == cat) {
            out[found++] = &s_entries[i];
        }
    }
    return found;
}

const eapps_app_lifecycle_t *eapps_registry_get_lifecycle(const char *id) {
    const eapps_registry_entry_t *e = eapps_registry_find(id);
    return e ? &e->lifecycle : NULL;
}

int eapps_registry_count(void) {
    return s_count;
}

const eapps_registry_entry_t *eapps_registry_get_all(int *count) {
    if (count) *count = s_count;
    return s_entries;
}
