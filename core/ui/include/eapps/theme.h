// SPDX-License-Identifier: MIT
#ifndef EAPPS_THEME_H
#define EAPPS_THEME_H

#include <stdbool.h>
#include <stdint.h>

typedef struct {
    uint32_t primary;
    uint32_t on_primary;
    uint32_t surface;
    uint32_t on_surface;
    uint32_t background;
    uint32_t card;
    uint32_t border;
    uint32_t error;
    uint32_t success;
    uint32_t accent;
} eapps_palette_t;

void               eapps_theme_init(bool is_dark);
void               eapps_theme_toggle(void);
bool               eapps_theme_is_dark(void);
const eapps_palette_t *eapps_theme_get_palette(void);

#endif /* EAPPS_THEME_H */
