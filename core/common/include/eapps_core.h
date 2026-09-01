/* SPDX-License-Identifier: MIT
 * Copyright (c) 2026 EoS Project
 *
 * eapps_core.h - umbrella header for eApps application modules.
 *
 * 46 files under apps/ include "eapps_core.h", but the header was never
 * committed - it appears in no commit in this repository's history. Every app
 * target added by the root CMakeLists.txt therefore failed to compile:
 *
 *   apps/ecal/ecal.h:5:10: fatal error: eapps_core.h: No such file or directory
 *
 * Nothing here is invented. Each declaration the apps rely on already existed in
 * a per-module header; this file only aggregates them, so the contract is
 * whatever those headers say:
 *
 *   eapps_app_info_t, eapps_app_lifecycle_t   <- eapps/types.h
 *   eapps_registry_*                          <- eapps/registry.h
 *   eapps_scaffold_create, eapps_card_create,
 *   eapps_list_create, eapps_list_item_create  <- eapps/widgets.h
 *   eapps_palette_t, eapps_theme_get_palette   <- eapps/theme.h
 *
 * Apps that additionally use the canvas, game-engine, TV-layout, or the string,
 * math, date, and expression utilities should include those headers directly
 * rather than have this one pull in the whole tree.
 */

#ifndef EAPPS_CORE_H
#define EAPPS_CORE_H

#include "eapps/types.h"
#include "eapps/registry.h"
#include "eapps/theme.h"
#include "eapps/widgets.h"

#endif /* EAPPS_CORE_H */
