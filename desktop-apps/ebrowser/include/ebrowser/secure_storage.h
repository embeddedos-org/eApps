// SPDX-License-Identifier: MIT
#ifndef eBrowser_SECURE_STORAGE_H
#define eBrowser_SECURE_STORAGE_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#define EB_STORE_MAX_KEY     128
#define EB_STORE_MAX_VALUE   4096
#define EB_STORE_MAX_ENTRIES 256
#define EB_STORE_MAGIC       0xEB5EC00E

typedef enum {
    EB_STORE_OK = 0,
    EB_STORE_ERR_FULL,
    EB_STORE_ERR_NOT_FOUND,
    EB_STORE_ERR_CRYPTO,
    EB_STORE_ERR_IO,
    EB_STORE_ERR_CORRUPT,
    EB_STORE_ERR_LOCKED,
    EB_STORE_ERR_INVALID
} eb_store_status_t;

typedef struct {
    char    key[EB_STORE_MAX_KEY];
    uint8_t encrypted_value[EB_STORE_MAX_VALUE];
    size_t  encrypted_len;
    uint8_t iv[16];
    uint8_t tag[32];
    uint64_t created_at;
    uint64_t expires_at;
} eb_store_entry_t;

typedef struct {
    uint32_t          magic;
    uint8_t           master_key[32];
    uint8_t           key_salt[16];
    eb_store_entry_t  entries[EB_STORE_MAX_ENTRIES];
    int               entry_count;
    bool              locked;
    char              filepath[256];
} eb_secure_store_t;

eb_store_status_t eb_store_init(eb_secure_store_t *store, const char *filepath);
eb_store_status_t eb_store_open(eb_secure_store_t *store, const char *password);
eb_store_status_t eb_store_close(eb_secure_store_t *store);

eb_store_status_t eb_store_put(eb_secure_store_t *store, const char *key,
                                const uint8_t *value, size_t value_len);
eb_store_status_t eb_store_get(eb_secure_store_t *store, const char *key,
                                uint8_t *value, size_t *value_len);
eb_store_status_t eb_store_delete(eb_secure_store_t *store, const char *key);
bool              eb_store_exists(const eb_secure_store_t *store, const char *key);
int               eb_store_count(const eb_secure_store_t *store);

eb_store_status_t eb_store_put_string(eb_secure_store_t *store, const char *key, const char *value);
eb_store_status_t eb_store_get_string(eb_secure_store_t *store, const char *key,
                                       char *value, size_t max_len);

eb_store_status_t eb_store_save(eb_secure_store_t *store);
eb_store_status_t eb_store_load(eb_secure_store_t *store);
eb_store_status_t eb_store_clear(eb_secure_store_t *store);
eb_store_status_t eb_store_remove_expired(eb_secure_store_t *store, uint64_t now);

const char       *eb_store_status_string(eb_store_status_t status);

#endif /* eBrowser_SECURE_STORAGE_H */
