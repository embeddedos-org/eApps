// SPDX-License-Identifier: MIT
#include "eapps/platform.h"
#include "eapps/theme.h"
#include "eapps/registry.h"

void main_loop(void) { /* lv_timer_handler(); */ }

int main(void) {
    eapps_theme_init(false);
    eapps_registry_init();
    /* emscripten_set_main_loop(main_loop, 0, 1); */
    return 0;
}
