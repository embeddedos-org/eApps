// SPDX-License-Identifier: MIT
#ifndef EAPPS_PREFS_H
#define EAPPS_PREFS_H

#include <stdbool.h>
#include <stdint.h>

typedef struct eapps_prefs eapps_prefs_t;

eapps_prefs_t *eapps_prefs_init(const char *app_id);
void           eapps_prefs_deinit(eapps_prefs_t *p);
const char    *eapps_prefs_get_string(eapps_prefs_t *p, const char *key, const char *def);
void           eapps_prefs_set_string(eapps_prefs_t *p, const char *key, const char *val);
int            eapps_prefs_get_int(eapps_prefs_t *p, const char *key, int def);
void           eapps_prefs_set_int(eapps_prefs_t *p, const char *key, int val);
bool           eapps_prefs_get_bool(eapps_prefs_t *p, const char *key, bool def);
void           eapps_prefs_set_bool(eapps_prefs_t *p, const char *key, bool val);
bool           eapps_prefs_save(eapps_prefs_t *p);

#endif /* EAPPS_PREFS_H */
