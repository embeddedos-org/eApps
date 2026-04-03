// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Meta Platforms, Inc. and affiliates.

#ifndef EAPPS_TV_LAYOUT_H
#define EAPPS_TV_LAYOUT_H

#include "lvgl.h"

#define TV_OVERSCAN_PCT     5
#define TV_FONT_MIN_SP      24
#define TV_FOCUS_RING_WIDTH  4
#define TV_FOCUS_COLOR       0x1E88E5
#define TV_CARD_WIDTH        280
#define TV_CARD_HEIGHT       200
#define TV_CARD_GAP          24

void eapps_tv_apply_overscan(lv_obj_t *parent);
void eapps_tv_focus_ring_add(lv_obj_t *obj);
lv_obj_t *eapps_tv_card_create(lv_obj_t *parent, const char *title, const char *icon, const char *desc);
lv_obj_t *eapps_tv_carousel_create(lv_obj_t *parent);

#endif /* EAPPS_TV_LAYOUT_H */
