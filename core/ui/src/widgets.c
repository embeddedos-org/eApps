// SPDX-License-Identifier: MIT
#include "eapps/widgets.h"

lv_obj_t *eapps_card_create(lv_obj_t *parent) {
    (void)parent;
    return NULL; /* LVGL integration: lv_obj_create + style */
}

lv_obj_t *eapps_button_create(lv_obj_t *parent, const char *text) {
    (void)parent; (void)text;
    return NULL;
}

lv_obj_t *eapps_button_icon_create(lv_obj_t *parent, const char *icon, const char *text) {
    (void)parent; (void)icon; (void)text;
    return NULL;
}

lv_obj_t *eapps_dialog_create(lv_obj_t *parent, const char *title, const char *message) {
    (void)parent; (void)title; (void)message;
    return NULL;
}

lv_obj_t *eapps_scaffold_create(lv_obj_t *parent, const char *title, bool has_bottom_nav) {
    (void)parent; (void)title; (void)has_bottom_nav;
    return NULL;
}

lv_obj_t *eapps_search_bar_create(lv_obj_t *parent) {
    (void)parent;
    return NULL;
}

lv_obj_t *eapps_text_input_create(lv_obj_t *parent, const char *placeholder) {
    (void)parent; (void)placeholder;
    return NULL;
}

lv_obj_t *eapps_grid_create(lv_obj_t *parent, int cols) {
    (void)parent; (void)cols;
    return NULL;
}

lv_obj_t *eapps_list_create(lv_obj_t *parent) {
    (void)parent;
    return NULL;
}

lv_obj_t *eapps_list_item_create(lv_obj_t *list, const char *icon, const char *text, const char *sub) {
    (void)list; (void)icon; (void)text; (void)sub;
    return NULL;
}
