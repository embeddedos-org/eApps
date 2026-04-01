// SPDX-License-Identifier: MIT
#ifndef EAPPS_WIDGETS_H
#define EAPPS_WIDGETS_H

#include "eapps/types.h"

lv_obj_t *eapps_card_create(lv_obj_t *parent);
lv_obj_t *eapps_button_create(lv_obj_t *parent, const char *text);
lv_obj_t *eapps_button_icon_create(lv_obj_t *parent, const char *icon, const char *text);
lv_obj_t *eapps_dialog_create(lv_obj_t *parent, const char *title, const char *message);
lv_obj_t *eapps_scaffold_create(lv_obj_t *parent, const char *title, bool has_bottom_nav);
lv_obj_t *eapps_search_bar_create(lv_obj_t *parent);
lv_obj_t *eapps_text_input_create(lv_obj_t *parent, const char *placeholder);
lv_obj_t *eapps_grid_create(lv_obj_t *parent, int cols);
lv_obj_t *eapps_list_create(lv_obj_t *parent);
lv_obj_t *eapps_list_item_create(lv_obj_t *list, const char *icon, const char *text, const char *sub);

#endif /* EAPPS_WIDGETS_H */
