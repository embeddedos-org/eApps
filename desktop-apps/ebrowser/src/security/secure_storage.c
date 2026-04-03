// SPDX-License-Identifier: MIT
#include "eBrowser/secure_storage.h"
#include "eBrowser/crypto.h"
#include <string.h>
#include <stdio.h>

eb_store_status_t eb_store_init(eb_secure_store_t *store, const char *filepath) {
    if (!store) return EB_STORE_ERR_INVALID;
    memset(store, 0, sizeof(eb_secure_store_t));
    store->magic = EB_STORE_MAGIC;
    store->locked = true;
    if (filepath) strncpy(store->filepath, filepath, 255);
    eb_crypto_random_bytes(store->key_salt, 16);
    return EB_STORE_OK;
}

eb_store_status_t eb_store_open(eb_secure_store_t *store, const char *password) {
    if (!store || !password) return EB_STORE_ERR_INVALID;
    if (store->magic != EB_STORE_MAGIC) return EB_STORE_ERR_CORRUPT;
    int rc = eb_crypto_pbkdf2_sha256(password, strlen(password),
                                      store->key_salt, 16, 10000,
                                      store->master_key, 32);
    if (rc != 0) return EB_STORE_ERR_CRYPTO;
    store->locked = false;
    return EB_STORE_OK;
}

eb_store_status_t eb_store_close(eb_secure_store_t *store) {
    if (!store) return EB_STORE_ERR_INVALID;
    eb_crypto_secure_zero(store->master_key, 32);
    store->locked = true;
    return EB_STORE_OK;
}

static int find_entry(const eb_secure_store_t *store, const char *key) {
    if (!store || !key) return -1;
    for (int i = 0; i < store->entry_count; i++) {
        if (strcmp(store->entries[i].key, key) == 0) return i;
    }
    return -1;
}

eb_store_status_t eb_store_put(eb_secure_store_t *store, const char *key,
                                const uint8_t *value, size_t value_len) {
    if (!store || !key || !value) return EB_STORE_ERR_INVALID;
    if (store->locked) return EB_STORE_ERR_LOCKED;
    if (value_len > EB_STORE_MAX_VALUE - 32) return EB_STORE_ERR_INVALID;

    int idx = find_entry(store, key);
    if (idx < 0) {
        if (store->entry_count >= EB_STORE_MAX_ENTRIES) return EB_STORE_ERR_FULL;
        idx = store->entry_count++;
    }

    eb_store_entry_t *entry = &store->entries[idx];
    strncpy(entry->key, key, EB_STORE_MAX_KEY - 1);

    eb_crypto_random_bytes(entry->iv, 16);

    size_t cipher_len = 0;
    int rc = eb_aes128_cbc_encrypt(store->master_key, entry->iv,
                                    value, value_len,
                                    entry->encrypted_value, &cipher_len);
    if (rc != 0) return EB_STORE_ERR_CRYPTO;
    entry->encrypted_len = cipher_len;

    eb_hmac_sha256(store->master_key, 16, entry->encrypted_value,
                    cipher_len, entry->tag);

    return EB_STORE_OK;
}

eb_store_status_t eb_store_get(eb_secure_store_t *store, const char *key,
                                uint8_t *value, size_t *value_len) {
    if (!store || !key || !value || !value_len) return EB_STORE_ERR_INVALID;
    if (store->locked) return EB_STORE_ERR_LOCKED;

    int idx = find_entry(store, key);
    if (idx < 0) return EB_STORE_ERR_NOT_FOUND;

    eb_store_entry_t *entry = &store->entries[idx];

    uint8_t computed_tag[32];
    eb_hmac_sha256(store->master_key, 16, entry->encrypted_value,
                    entry->encrypted_len, computed_tag);
    if (!eb_crypto_constant_time_compare(computed_tag, entry->tag, 32))
        return EB_STORE_ERR_CORRUPT;

    size_t plain_len = 0;
    int rc = eb_aes128_cbc_decrypt(store->master_key, entry->iv,
                                    entry->encrypted_value, entry->encrypted_len,
                                    value, &plain_len);
    if (rc != 0) return EB_STORE_ERR_CRYPTO;
    *value_len = plain_len;
    return EB_STORE_OK;
}

eb_store_status_t eb_store_delete(eb_secure_store_t *store, const char *key) {
    if (!store || !key) return EB_STORE_ERR_INVALID;
    if (store->locked) return EB_STORE_ERR_LOCKED;
    int idx = find_entry(store, key);
    if (idx < 0) return EB_STORE_ERR_NOT_FOUND;
    eb_crypto_secure_zero(&store->entries[idx], sizeof(eb_store_entry_t));
    for (int i = idx; i < store->entry_count - 1; i++)
        store->entries[i] = store->entries[i + 1];
    store->entry_count--;
    return EB_STORE_OK;
}

bool eb_store_exists(const eb_secure_store_t *store, const char *key) {
    return find_entry(store, key) >= 0;
}

int eb_store_count(const eb_secure_store_t *store) {
    return store ? store->entry_count : 0;
}

eb_store_status_t eb_store_put_string(eb_secure_store_t *store, const char *key, const char *value) {
    if (!value) return EB_STORE_ERR_INVALID;
    return eb_store_put(store, key, (const uint8_t *)value, strlen(value));
}

eb_store_status_t eb_store_get_string(eb_secure_store_t *store, const char *key,
                                       char *value, size_t max_len) {
    if (!value || max_len == 0) return EB_STORE_ERR_INVALID;
    uint8_t buf[EB_STORE_MAX_VALUE];
    size_t len = 0;
    eb_store_status_t rc = eb_store_get(store, key, buf, &len);
    if (rc != EB_STORE_OK) return rc;
    if (len >= max_len) len = max_len - 1;
    memcpy(value, buf, len);
    value[len] = '\0';
    eb_crypto_secure_zero(buf, sizeof(buf));
    return EB_STORE_OK;
}

eb_store_status_t eb_store_clear(eb_secure_store_t *store) {
    if (!store) return EB_STORE_ERR_INVALID;
    if (store->locked) return EB_STORE_ERR_LOCKED;
    eb_crypto_secure_zero(store->entries, sizeof(store->entries));
    store->entry_count = 0;
    return EB_STORE_OK;
}

eb_store_status_t eb_store_remove_expired(eb_secure_store_t *store, uint64_t now) {
    if (!store) return EB_STORE_ERR_INVALID;
    if (store->locked) return EB_STORE_ERR_LOCKED;
    int i = 0;
    while (i < store->entry_count) {
        if (store->entries[i].expires_at > 0 && store->entries[i].expires_at < now) {
            eb_crypto_secure_zero(&store->entries[i], sizeof(eb_store_entry_t));
            for (int j = i; j < store->entry_count - 1; j++)
                store->entries[j] = store->entries[j + 1];
            store->entry_count--;
        } else {
            i++;
        }
    }
    return EB_STORE_OK;
}

eb_store_status_t eb_store_save(eb_secure_store_t *store) {
    if (!store || store->filepath[0] == '\0') return EB_STORE_ERR_IO;
    FILE *f = fopen(store->filepath, "wb");
    if (!f) return EB_STORE_ERR_IO;
    fwrite(&store->magic, sizeof(uint32_t), 1, f);
    fwrite(store->key_salt, 16, 1, f);
    fwrite(&store->entry_count, sizeof(int), 1, f);
    fwrite(store->entries, sizeof(eb_store_entry_t), (size_t)store->entry_count, f);
    fclose(f);
    return EB_STORE_OK;
}

eb_store_status_t eb_store_load(eb_secure_store_t *store) {
    if (!store || store->filepath[0] == '\0') return EB_STORE_ERR_IO;
    FILE *f = fopen(store->filepath, "rb");
    if (!f) return EB_STORE_ERR_IO;
    uint32_t magic;
    if (fread(&magic, sizeof(uint32_t), 1, f) != 1 || magic != EB_STORE_MAGIC) {
        fclose(f); return EB_STORE_ERR_CORRUPT;
    }
    store->magic = magic;
    fread(store->key_salt, 16, 1, f);
    fread(&store->entry_count, sizeof(int), 1, f);
    if (store->entry_count > EB_STORE_MAX_ENTRIES) {
        fclose(f); return EB_STORE_ERR_CORRUPT;
    }
    fread(store->entries, sizeof(eb_store_entry_t), (size_t)store->entry_count, f);
    fclose(f);
    store->locked = true;
    return EB_STORE_OK;
}

const char *eb_store_status_string(eb_store_status_t status) {
    switch (status) {
        case EB_STORE_OK:          return "OK";
        case EB_STORE_ERR_FULL:    return "Storage full";
        case EB_STORE_ERR_NOT_FOUND: return "Key not found";
        case EB_STORE_ERR_CRYPTO:  return "Crypto error";
        case EB_STORE_ERR_IO:      return "I/O error";
        case EB_STORE_ERR_CORRUPT: return "Data corrupt";
        case EB_STORE_ERR_LOCKED:  return "Store locked";
        case EB_STORE_ERR_INVALID: return "Invalid argument";
        default:                    return "Unknown error";
    }
}
