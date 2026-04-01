// SPDX-License-Identifier: MIT
#ifndef EAPPS_APP_SUITE_H
#define EAPPS_APP_SUITE_H

#include "eapps/types.h"

bool suite_init(lv_obj_t *parent);
void suite_deinit(void);
void suite_register_all_apps(void);

#endif /* EAPPS_APP_SUITE_H */
