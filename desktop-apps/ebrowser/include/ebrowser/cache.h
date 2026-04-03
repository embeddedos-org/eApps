// SPDX-License-Identifier: MIT
#ifndef eBrowser_CACHE_H
#define eBrowser_CACHE_H

#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

#define EB_CACHE_MAX_ENTRIES 128
#define EB_CACHE_MAX_URL     512
#define EB_CACHE_MAX_ETAG    128

typedef struct {
    char     url[EB_CACHE_MAX_URL];
    char     etag[EB_CACHE_MAX_ETAG];
    uint8_t *data;
    size_t   data_len;
    uint64_t created_at;
    uint64_t expires_at;
    uint64_t last_accessed;
    bool     valid;
} eb_cache_entry_t;

typedef struct {
    eb_cache_entry_t entries[EB_CACHE_MAX_ENTRIES];
    int              entry_count;
    size_t           max_size_bytes;
    size_t           current_size;
} eb_cache_t;

void              eb_cache_init(eb_cache_t *cache, size_t max_size);
eb_cache_entry_t *eb_cache_get(eb_cache_t *cache, const char *url);
bool              eb_cache_put(eb_cache_t *cache, const char *url, const uint8_t *data,
                                size_t len, const char *etag, int max_age_sec);
bool              eb_cache_invalidate(eb_cache_t *cache, const char *url);
void              eb_cache_evict_lru(eb_cache_t *cache);
void              eb_cache_clear(eb_cache_t *cache);
size_t            eb_cache_size(const eb_cache_t *cache);

#endif
