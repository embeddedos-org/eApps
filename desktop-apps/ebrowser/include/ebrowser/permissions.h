// SPDX-License-Identifier: MIT
#ifndef eBrowser_PERMISSIONS_H
#define eBrowser_PERMISSIONS_H

#include <stdbool.h>

typedef enum {
    EB_PERM_CAMERA,
    EB_PERM_MICROPHONE,
    EB_PERM_GEOLOCATION,
    EB_PERM_NOTIFICATIONS,
    EB_PERM_CLIPBOARD,
    EB_PERM_STORAGE,
    EB_PERM_COUNT
} eb_permission_t;

typedef enum {
    EB_PERM_STATE_PROMPT,
    EB_PERM_STATE_GRANTED,
    EB_PERM_STATE_DENIED
} eb_permission_state_t;

typedef struct {
    eb_permission_state_t states[EB_PERM_COUNT];
    char origin[256];
} eb_permission_ctx_t;

void                 eb_permissions_init(eb_permission_ctx_t *ctx, const char *origin);
eb_permission_state_t eb_permissions_query(const eb_permission_ctx_t *ctx, eb_permission_t perm);
bool                 eb_permissions_request(eb_permission_ctx_t *ctx, eb_permission_t perm);
void                 eb_permissions_revoke(eb_permission_ctx_t *ctx, eb_permission_t perm);
const char          *eb_permission_name(eb_permission_t perm);

#endif
