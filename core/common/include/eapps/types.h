// SPDX-License-Identifier: MIT
// Copyright (c) 2026 EoS Project

#ifndef EAPPS_TYPES_H
#define EAPPS_TYPES_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#define EAPPS_MAX_NAME        64
#define EAPPS_MAX_DESC        256
#define EAPPS_MAX_ICON        8
#define EAPPS_MAX_VERSION     16
#define EAPPS_MAX_APPS        64
#define EAPPS_MAX_SEARCH      128

typedef enum {
    EAPPS_CAT_PRODUCTIVITY,
    EAPPS_CAT_MEDIA,
    EAPPS_CAT_GAMES,
    EAPPS_CAT_CONNECTIVITY,
    EAPPS_CAT_SECURITY,
    EAPPS_CAT_WEB,
    EAPPS_CAT_COUNT
} eapps_category_t;

typedef enum {
    EAPPS_PLATFORM_DESKTOP,
    EAPPS_PLATFORM_EOS_TARGET,
    EAPPS_PLATFORM_WEB_TARGET,
    EAPPS_PLATFORM_COUNT
} eapps_platform_t;

typedef struct {
    const char *id;
    const char *name;
    const char *icon;
    const char *description;
    eapps_category_t category;
    const char *version;
} eapps_app_info_t;

typedef struct lv_obj_t lv_obj_t;

typedef struct {
    bool (*init)(lv_obj_t *parent);
    void (*deinit)(void);
    void (*on_show)(void);
    void (*on_hide)(void);
} eapps_app_lifecycle_t;

static inline const char *eapps_category_str(eapps_category_t cat) {
    switch (cat) {
        case EAPPS_CAT_PRODUCTIVITY: return "Productivity";
        case EAPPS_CAT_MEDIA:        return "Media";
        case EAPPS_CAT_GAMES:        return "Games";
        case EAPPS_CAT_CONNECTIVITY: return "Connectivity";
        case EAPPS_CAT_SECURITY:     return "Security";
        case EAPPS_CAT_WEB:          return "Web";
        default:                      return "Unknown";
    }
}

#endif /* EAPPS_TYPES_H */
