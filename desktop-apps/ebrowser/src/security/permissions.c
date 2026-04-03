// SPDX-License-Identifier: MIT
#include "eBrowser/permissions.h"
#include <string.h>

void eb_permissions_init(eb_permission_ctx_t *ctx, const char *origin) {
    if (!ctx) return;
    memset(ctx, 0, sizeof(eb_permission_ctx_t));
    for (int i = 0; i < EB_PERM_COUNT; i++) ctx->states[i] = EB_PERM_STATE_DENIED;
    ctx->states[EB_PERM_STORAGE] = EB_PERM_STATE_GRANTED;
    if (origin) strncpy(ctx->origin, origin, sizeof(ctx->origin) - 1);
}

eb_permission_state_t eb_permissions_query(const eb_permission_ctx_t *ctx, eb_permission_t perm) {
    if (!ctx || perm < 0 || perm >= EB_PERM_COUNT) return EB_PERM_STATE_DENIED;
    return ctx->states[perm];
}

bool eb_permissions_request(eb_permission_ctx_t *ctx, eb_permission_t perm) {
    if (!ctx || perm < 0 || perm >= EB_PERM_COUNT) return false;
    if (ctx->states[perm] == EB_PERM_STATE_GRANTED) return true;
    ctx->states[perm] = EB_PERM_STATE_DENIED;
    return false;
}

void eb_permissions_revoke(eb_permission_ctx_t *ctx, eb_permission_t perm) {
    if (!ctx || perm < 0 || perm >= EB_PERM_COUNT) return;
    ctx->states[perm] = EB_PERM_STATE_DENIED;
}

const char *eb_permission_name(eb_permission_t perm) {
    switch (perm) {
        case EB_PERM_CAMERA: return "camera";
        case EB_PERM_MICROPHONE: return "microphone";
        case EB_PERM_GEOLOCATION: return "geolocation";
        case EB_PERM_NOTIFICATIONS: return "notifications";
        case EB_PERM_CLIPBOARD: return "clipboard";
        case EB_PERM_STORAGE: return "storage";
        default: return "unknown";
    }
}
