// SPDX-License-Identifier: MIT
#include "eapps/prefs.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_ENTRIES 64
#define MAX_KEY_LEN 64
#define MAX_VAL_LEN 256

typedef struct {
    char key[MAX_KEY_LEN];
    char value[MAX_VAL_LEN];
} pref_entry_t;

struct eapps_prefs {
    char         app_id[64];
    char         filepath[256];
    pref_entry_t entries[MAX_ENTRIES];
    int          count;
};

static pref_entry_t *find_entry(eapps_prefs_t *p, const char *key) {
    for (int i = 0; i < p->count; i++) {
        if (strcmp(p->entries[i].key, key) == 0) return &p->entries[i];
    }
    return NULL;
}

eapps_prefs_t *eapps_prefs_init(const char *app_id) {
    eapps_prefs_t *p = (eapps_prefs_t *)calloc(1, sizeof(eapps_prefs_t));
    if (!p) return NULL;
    snprintf(p->app_id, sizeof(p->app_id), "%s", app_id);
    snprintf(p->filepath, sizeof(p->filepath), "%s.ini", app_id);

    FILE *f = fopen(p->filepath, "r");
    if (f) {
        char line[MAX_KEY_LEN + MAX_VAL_LEN + 4];
        while (fgets(line, sizeof(line), f) && p->count < MAX_ENTRIES) {
            char *eq = strchr(line, '=');
            if (!eq) continue;
            *eq = '\0';
            char *val = eq + 1;
            size_t vlen = strlen(val);
            if (vlen > 0 && val[vlen - 1] == '\n') val[vlen - 1] = '\0';
            snprintf(p->entries[p->count].key, MAX_KEY_LEN, "%s", line);
            snprintf(p->entries[p->count].value, MAX_VAL_LEN, "%s", val);
            p->count++;
        }
        fclose(f);
    }
    return p;
}

void eapps_prefs_deinit(eapps_prefs_t *p) {
    if (p) { eapps_prefs_save(p); free(p); }
}

const char *eapps_prefs_get_string(eapps_prefs_t *p, const char *key, const char *def) {
    if (!p || !key) return def;
    pref_entry_t *e = find_entry(p, key);
    return e ? e->value : def;
}

void eapps_prefs_set_string(eapps_prefs_t *p, const char *key, const char *val) {
    if (!p || !key || !val) return;
    pref_entry_t *e = find_entry(p, key);
    if (e) { snprintf(e->value, MAX_VAL_LEN, "%s", val); return; }
    if (p->count >= MAX_ENTRIES) return;
    snprintf(p->entries[p->count].key, MAX_KEY_LEN, "%s", key);
    snprintf(p->entries[p->count].value, MAX_VAL_LEN, "%s", val);
    p->count++;
}

int eapps_prefs_get_int(eapps_prefs_t *p, const char *key, int def) {
    const char *s = eapps_prefs_get_string(p, key, NULL);
    return s ? atoi(s) : def;
}

void eapps_prefs_set_int(eapps_prefs_t *p, const char *key, int val) {
    char buf[32];
    snprintf(buf, sizeof(buf), "%d", val);
    eapps_prefs_set_string(p, key, buf);
}

bool eapps_prefs_get_bool(eapps_prefs_t *p, const char *key, bool def) {
    const char *s = eapps_prefs_get_string(p, key, NULL);
    if (!s) return def;
    return strcmp(s, "true") == 0 || strcmp(s, "1") == 0;
}

void eapps_prefs_set_bool(eapps_prefs_t *p, const char *key, bool val) {
    eapps_prefs_set_string(p, key, val ? "true" : "false");
}

bool eapps_prefs_save(eapps_prefs_t *p) {
    if (!p) return false;
    FILE *f = fopen(p->filepath, "w");
    if (!f) return false;
    for (int i = 0; i < p->count; i++)
        fprintf(f, "%s=%s\n", p->entries[i].key, p->entries[i].value);
    fclose(f);
    return true;
}
