// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Meta Platforms, Inc. and affiliates.

#include "eapps/tv_layout.h"

void eapps_tv_apply_overscan(lv_obj_t *parent)
{
    lv_coord_t hor = lv_obj_get_width(parent) * TV_OVERSCAN_PCT / 100;
    lv_coord_t ver = lv_obj_get_height(parent) * TV_OVERSCAN_PCT / 100;

    lv_obj_set_style_pad_left(parent, hor, LV_PART_MAIN);
    lv_obj_set_style_pad_right(parent, hor, LV_PART_MAIN);
    lv_obj_set_style_pad_top(parent, ver, LV_PART_MAIN);
    lv_obj_set_style_pad_bottom(parent, ver, LV_PART_MAIN);
}

void eapps_tv_focus_ring_add(lv_obj_t *obj)
{
    static lv_style_t style_focus;
    static bool style_inited = false;

    if (!style_inited) {
        lv_style_init(&style_focus);
        lv_style_set_outline_width(&style_focus, TV_FOCUS_RING_WIDTH);
        lv_style_set_outline_color(&style_focus, lv_color_hex(TV_FOCUS_COLOR));
        lv_style_set_outline_opa(&style_focus, LV_OPA_COVER);
        lv_style_set_outline_pad(&style_focus, 2);
        style_inited = true;
    }

    lv_obj_add_style(obj, &style_focus, LV_STATE_FOCUSED);
}

lv_obj_t *eapps_tv_card_create(lv_obj_t *parent, const char *title, const char *icon, const char *desc)
{
    lv_obj_t *card = lv_obj_create(parent);
    lv_obj_set_size(card, TV_CARD_WIDTH, TV_CARD_HEIGHT);
    lv_obj_set_flex_flow(card, LV_FLEX_FLOW_COLUMN);
    lv_obj_set_flex_align(card, LV_FLEX_ALIGN_START, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER);
    lv_obj_set_style_pad_all(card, 12, LV_PART_MAIN);
    lv_obj_set_style_radius(card, 12, LV_PART_MAIN);
    lv_obj_set_style_bg_opa(card, LV_OPA_COVER, LV_PART_MAIN);
    lv_obj_set_style_bg_color(card, lv_color_hex(0x2C2C2C), LV_PART_MAIN);

    lv_obj_t *lbl_icon = lv_label_create(card);
    lv_label_set_text(lbl_icon, icon);
    lv_obj_set_style_text_font(lbl_icon, lv_font_default(), LV_PART_MAIN);

    lv_obj_t *lbl_title = lv_label_create(card);
    lv_label_set_text(lbl_title, title);
    lv_obj_set_style_text_color(lbl_title, lv_color_white(), LV_PART_MAIN);

    lv_obj_t *lbl_desc = lv_label_create(card);
    lv_label_set_text(lbl_desc, desc);
    lv_label_set_long_mode(lbl_desc, LV_LABEL_LONG_WRAP);
    lv_obj_set_width(lbl_desc, TV_CARD_WIDTH - 24);
    lv_obj_set_style_text_color(lbl_desc, lv_color_hex(0xAAAAAA), LV_PART_MAIN);

    lv_obj_add_flag(card, LV_OBJ_FLAG_CLICKABLE);
    eapps_tv_focus_ring_add(card);

    return card;
}

lv_obj_t *eapps_tv_carousel_create(lv_obj_t *parent)
{
    lv_obj_t *row = lv_obj_create(parent);
    lv_obj_set_size(row, LV_PCT(100), LV_SIZE_CONTENT);
    lv_obj_set_flex_flow(row, LV_FLEX_FLOW_ROW);
    lv_obj_set_flex_align(row, LV_FLEX_ALIGN_START, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER);
    lv_obj_set_style_pad_column(row, TV_CARD_GAP, LV_PART_MAIN);
    lv_obj_set_scroll_dir(row, LV_DIR_HOR);
    lv_obj_set_scroll_snap_x(row, LV_SCROLL_SNAP_CENTER);
    lv_obj_set_style_bg_opa(row, LV_OPA_TRANSP, LV_PART_MAIN);
    lv_obj_clear_flag(row, LV_OBJ_FLAG_SCROLLABLE);
    lv_obj_add_flag(row, LV_OBJ_FLAG_SCROLL_ONE | LV_OBJ_FLAG_SCROLLABLE);

    return row;
}
