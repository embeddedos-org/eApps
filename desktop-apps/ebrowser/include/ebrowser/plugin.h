// SPDX-License-Identifier: MIT
#ifndef eBrowser_PLUGIN_H
#define eBrowser_PLUGIN_H

#include <stdbool.h>
#include <stddef.h>
#include <string.h>

#define EB_PLUGIN_MAX_PLUGINS 16
#define EB_PLUGIN_MAX_NAME    64

typedef enum {
    EB_HOOK_ON_PAGE_LOAD,
    EB_HOOK_ON_PAGE_UNLOAD,
    EB_HOOK_ON_REQUEST,
    EB_HOOK_ON_RESPONSE,
    EB_HOOK_ON_DOM_READY,
    EB_HOOK_ON_RENDER,
    EB_HOOK_ON_INPUT,
    EB_HOOK_COUNT
} eb_plugin_hook_t;

typedef struct {
    const char *url;
    const char *method;
    int         status_code;
    const char *body;
    size_t      body_len;
} eb_plugin_event_t;

typedef bool (*eb_plugin_init_fn)(void *user_data);
typedef void (*eb_plugin_shutdown_fn)(void *user_data);
typedef bool (*eb_plugin_hook_fn)(eb_plugin_hook_t hook, const eb_plugin_event_t *event, void *user_data);

typedef struct {
    char               name[EB_PLUGIN_MAX_NAME];
    char               version[16];
    int                priority;
    eb_plugin_init_fn  init;
    eb_plugin_shutdown_fn shutdown;
    eb_plugin_hook_fn  on_event;
    void              *user_data;
    bool               enabled;
    bool               hooks[EB_HOOK_COUNT];
} eb_plugin_t;

typedef struct {
    eb_plugin_t plugins[EB_PLUGIN_MAX_PLUGINS];
    int         count;
} eb_plugin_manager_t;

void eb_plugin_manager_init(eb_plugin_manager_t *mgr);
bool eb_plugin_register(eb_plugin_manager_t *mgr, const eb_plugin_t *plugin);
bool eb_plugin_unregister(eb_plugin_manager_t *mgr, const char *name);
bool eb_plugin_enable(eb_plugin_manager_t *mgr, const char *name);
bool eb_plugin_disable(eb_plugin_manager_t *mgr, const char *name);
int  eb_plugin_dispatch(eb_plugin_manager_t *mgr, eb_plugin_hook_t hook, const eb_plugin_event_t *event);
eb_plugin_t *eb_plugin_find(eb_plugin_manager_t *mgr, const char *name);
void eb_plugin_manager_shutdown(eb_plugin_manager_t *mgr);

#endif
