// SPDX-License-Identifier: MIT
// Copyright (c) 2026 EoS Project

#ifndef EAPPS_REGISTRY_H
#define EAPPS_REGISTRY_H

#include "eapps/types.h"

typedef struct {
    eapps_app_info_t      info;
    eapps_app_lifecycle_t lifecycle;
} eapps_registry_entry_t;

void   eapps_registry_init(void);
void   eapps_registry_deinit(void);
bool   eapps_registry_register(const eapps_app_info_t *info, const eapps_app_lifecycle_t *lc);
const  eapps_registry_entry_t *eapps_registry_find(const char *id);
int    eapps_registry_search(const char *query, const eapps_registry_entry_t **out, int max);
int    eapps_registry_list_by_category(eapps_category_t cat, const eapps_registry_entry_t **out, int max);
const  eapps_app_lifecycle_t *eapps_registry_get_lifecycle(const char *id);
int    eapps_registry_count(void);
const  eapps_registry_entry_t *eapps_registry_get_all(int *count);

#endif /* EAPPS_REGISTRY_H */
