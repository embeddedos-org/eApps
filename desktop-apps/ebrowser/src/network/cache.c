// SPDX-License-Identifier: MIT
#include "eBrowser/cache.h"
#include <stdlib.h>
#include <string.h>
#include <time.h>

void eb_cache_init(eb_cache_t *cache, size_t max_size) {
    if (!cache) return;
    memset(cache, 0, sizeof(eb_cache_t));
    cache->max_size_bytes = max_size > 0 ? max_size : 10 * 1024 * 1024;
}

eb_cache_entry_t *eb_cache_get(eb_cache_t *cache, const char *url) {
    if (!cache || !url) return NULL;
    uint64_t now = (uint64_t)time(NULL);
    for (int i = 0; i < cache->entry_count; i++) {
        if (cache->entries[i].valid && strcmp(cache->entries[i].url, url) == 0) {
            if (cache->entries[i].expires_at > 0 && now > cache->entries[i].expires_at) {
                cache->entries[i].valid = false;
                if (cache->entries[i].data) { free(cache->entries[i].data); cache->entries[i].data = NULL; }
                cache->current_size -= cache->entries[i].data_len;
                return NULL;
            }
            cache->entries[i].last_accessed = now;
            return &cache->entries[i];
        }
    }
    return NULL;
}

bool eb_cache_put(eb_cache_t *cache, const char *url, const uint8_t *data, size_t len, const char *etag, int max_age_sec) {
    if (!cache || !url || !data || len == 0) return false;
    while (cache->current_size + len > cache->max_size_bytes && cache->entry_count > 0) eb_cache_evict_lru(cache);
    if (cache->current_size + len > cache->max_size_bytes) return false;
    eb_cache_entry_t *entry = NULL;
    for (int i = 0; i < cache->entry_count; i++) {
        if (cache->entries[i].valid && strcmp(cache->entries[i].url, url) == 0) {
            if (cache->entries[i].data) { cache->current_size -= cache->entries[i].data_len; free(cache->entries[i].data); }
            entry = &cache->entries[i]; break;
        }
    }
    if (!entry) {
        if (cache->entry_count >= EB_CACHE_MAX_ENTRIES) eb_cache_evict_lru(cache);
        if (cache->entry_count >= EB_CACHE_MAX_ENTRIES) return false;
        entry = &cache->entries[cache->entry_count++];
    }
    strncpy(entry->url, url, EB_CACHE_MAX_URL - 1);
    if (etag) strncpy(entry->etag, etag, EB_CACHE_MAX_ETAG - 1);
    entry->data = (uint8_t *)malloc(len);
    if (!entry->data) return false;
    memcpy(entry->data, data, len);
    entry->data_len = len;
    entry->created_at = (uint64_t)time(NULL);
    entry->last_accessed = entry->created_at;
    entry->expires_at = max_age_sec > 0 ? entry->created_at + (uint64_t)max_age_sec : 0;
    entry->valid = true;
    cache->current_size += len;
    return true;
}

bool eb_cache_invalidate(eb_cache_t *cache, const char *url) {
    if (!cache || !url) return false;
    for (int i = 0; i < cache->entry_count; i++) {
        if (cache->entries[i].valid && strcmp(cache->entries[i].url, url) == 0) {
            cache->entries[i].valid = false;
            if (cache->entries[i].data) { cache->current_size -= cache->entries[i].data_len; free(cache->entries[i].data); cache->entries[i].data = NULL; }
            return true;
        }
    }
    return false;
}

void eb_cache_evict_lru(eb_cache_t *cache) {
    if (!cache || cache->entry_count == 0) return;
    int oldest = -1; uint64_t oldest_time = UINT64_MAX;
    for (int i = 0; i < cache->entry_count; i++) {
        if (cache->entries[i].valid && cache->entries[i].last_accessed < oldest_time) { oldest = i; oldest_time = cache->entries[i].last_accessed; }
    }
    if (oldest >= 0) {
        cache->entries[oldest].valid = false;
        if (cache->entries[oldest].data) { cache->current_size -= cache->entries[oldest].data_len; free(cache->entries[oldest].data); cache->entries[oldest].data = NULL; }
    }
}

void eb_cache_clear(eb_cache_t *cache) {
    if (!cache) return;
    for (int i = 0; i < cache->entry_count; i++) { if (cache->entries[i].data) free(cache->entries[i].data); }
    memset(cache->entries, 0, sizeof(cache->entries));
    cache->entry_count = 0; cache->current_size = 0;
}

size_t eb_cache_size(const eb_cache_t *cache) { return cache ? cache->current_size : 0; }
