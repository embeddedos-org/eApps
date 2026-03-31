// SPDX-License-Identifier: MIT
#include "eapps/theme.h"

static bool s_dark = false;

static const eapps_palette_t LIGHT_PALETTE = {
    .primary    = 0x1976D2,
    .on_primary = 0xFFFFFF,
    .surface    = 0xFFFFFF,
    .on_surface = 0x212121,
    .background = 0xF5F5F5,
    .card       = 0xFFFFFF,
    .border     = 0xE0E0E0,
    .error      = 0xD32F2F,
    .success    = 0x388E3C,
    .accent     = 0xFF9800,
};

static const eapps_palette_t DARK_PALETTE = {
    .primary    = 0x90CAF9,
    .on_primary = 0x000000,
    .surface    = 0x1E1E1E,
    .on_surface = 0xE0E0E0,
    .background = 0x121212,
    .card       = 0x2C2C2C,
    .border     = 0x444444,
    .error      = 0xEF9A9A,
    .success    = 0x81C784,
    .accent     = 0xFFB74D,
};

void eapps_theme_init(bool is_dark) {
    s_dark = is_dark;
}

void eapps_theme_toggle(void) {
    s_dark = !s_dark;
}

bool eapps_theme_is_dark(void) {
    return s_dark;
}

const eapps_palette_t *eapps_theme_get_palette(void) {
    return s_dark ? &DARK_PALETTE : &LIGHT_PALETTE;
}
