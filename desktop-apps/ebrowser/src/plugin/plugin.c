// SPDX-License-Identifier: MIT
#include "eBrowser/plugin.h"

void eb_plugin_manager_init(eb_plugin_manager_t *mgr) {
    if (mgr) memset(mgr, 0, sizeof(eb_plugin_manager_t));
}

bool eb_plugin_register(eb_plugin_manager_t *mgr, const eb_plugin_t *plugin) {
    if (!mgr || !plugin || mgr->count >= EB_PLUGIN_MAX_PLUGINS) return false;
    if (eb_plugin_find(mgr, plugin->name)) return false;
    mgr->plugins[mgr->count] = *plugin;
    mgr->plugins[mgr->count].enabled = true;
    if (plugin->init) plugin->init(mgr->plugins[mgr->count].user_data);
    mgr->count++;
    return true;
}

bool eb_plugin_unregister(eb_plugin_manager_t *mgr, const char *name) {
    if (!mgr || !name) return false;
    for (int i = 0; i < mgr->count; i++) {
        if (strcmp(mgr->plugins[i].name, name) == 0) {
            if (mgr->plugins[i].shutdown) mgr->plugins[i].shutdown(mgr->plugins[i].user_data);
            for (int j = i; j < mgr->count - 1; j++) mgr->plugins[j] = mgr->plugins[j + 1];
            mgr->count--;
            return true;
        }
    }
    return false;
}

bool eb_plugin_enable(eb_plugin_manager_t *mgr, const char *name) {
    eb_plugin_t *p = eb_plugin_find(mgr, name);
    if (!p) return false;
    p->enabled = true;
    return true;
}

bool eb_plugin_disable(eb_plugin_manager_t *mgr, const char *name) {
    eb_plugin_t *p = eb_plugin_find(mgr, name);
    if (!p) return false;
    p->enabled = false;
    return true;
}

int eb_plugin_dispatch(eb_plugin_manager_t *mgr, eb_plugin_hook_t hook, const eb_plugin_event_t *event) {
    if (!mgr || hook < 0 || hook >= EB_HOOK_COUNT) return 0;
    int handled = 0;
    for (int i = 0; i < mgr->count; i++) {
        eb_plugin_t *p = &mgr->plugins[i];
        if (!p->enabled || !p->hooks[hook] || !p->on_event) continue;
        if (p->on_event(hook, event, p->user_data)) handled++;
    }
    return handled;
}

eb_plugin_t *eb_plugin_find(eb_plugin_manager_t *mgr, const char *name) {
    if (!mgr || !name) return NULL;
    for (int i = 0; i < mgr->count; i++) {
        if (strcmp(mgr->plugins[i].name, name) == 0) return &mgr->plugins[i];
    }
    return NULL;
}

void eb_plugin_manager_shutdown(eb_plugin_manager_t *mgr) {
    if (!mgr) return;
    for (int i = 0; i < mgr->count; i++) {
        if (mgr->plugins[i].shutdown) mgr->plugins[i].shutdown(mgr->plugins[i].user_data);
    }
    mgr->count = 0;
}
