// SPDX-License-Identifier: MIT
#ifndef eBrowser_CRYPTO_H
#define eBrowser_CRYPTO_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#define EB_SHA256_DIGEST_SIZE   32
#define EB_SHA256_BLOCK_SIZE    64
#define EB_AES128_KEY_SIZE      16
#define EB_AES128_BLOCK_SIZE    16
#define EB_AES128_IV_SIZE       16
#define EB_HMAC_SHA256_SIZE     32

// --- SHA-256 ---

typedef struct {
    uint32_t state[8];
    uint64_t bit_count;
    uint8_t  buffer[EB_SHA256_BLOCK_SIZE];
    size_t   buffer_len;
} eb_sha256_ctx_t;

void eb_sha256_init(eb_sha256_ctx_t *ctx);
void eb_sha256_update(eb_sha256_ctx_t *ctx, const uint8_t *data, size_t len);
void eb_sha256_final(eb_sha256_ctx_t *ctx, uint8_t digest[EB_SHA256_DIGEST_SIZE]);
void eb_sha256(const uint8_t *data, size_t len, uint8_t digest[EB_SHA256_DIGEST_SIZE]);

// --- HMAC-SHA256 ---

typedef struct {
    eb_sha256_ctx_t inner;
    eb_sha256_ctx_t outer;
    uint8_t         key_pad[EB_SHA256_BLOCK_SIZE];
} eb_hmac_sha256_ctx_t;

void eb_hmac_sha256_init(eb_hmac_sha256_ctx_t *ctx, const uint8_t *key, size_t key_len);
void eb_hmac_sha256_update(eb_hmac_sha256_ctx_t *ctx, const uint8_t *data, size_t len);
void eb_hmac_sha256_final(eb_hmac_sha256_ctx_t *ctx, uint8_t mac[EB_HMAC_SHA256_SIZE]);
void eb_hmac_sha256(const uint8_t *key, size_t key_len,
                     const uint8_t *data, size_t data_len,
                     uint8_t mac[EB_HMAC_SHA256_SIZE]);

// --- AES-128 ---

typedef struct {
    uint32_t round_keys[44];
} eb_aes128_ctx_t;

void eb_aes128_init(eb_aes128_ctx_t *ctx, const uint8_t key[EB_AES128_KEY_SIZE]);
void eb_aes128_encrypt_block(const eb_aes128_ctx_t *ctx,
                              const uint8_t in[EB_AES128_BLOCK_SIZE],
                              uint8_t out[EB_AES128_BLOCK_SIZE]);
void eb_aes128_decrypt_block(const eb_aes128_ctx_t *ctx,
                              const uint8_t in[EB_AES128_BLOCK_SIZE],
                              uint8_t out[EB_AES128_BLOCK_SIZE]);

int  eb_aes128_cbc_encrypt(const uint8_t key[EB_AES128_KEY_SIZE],
                            const uint8_t iv[EB_AES128_IV_SIZE],
                            const uint8_t *plaintext, size_t plain_len,
                            uint8_t *ciphertext, size_t *cipher_len);
int  eb_aes128_cbc_decrypt(const uint8_t key[EB_AES128_KEY_SIZE],
                            const uint8_t iv[EB_AES128_IV_SIZE],
                            const uint8_t *ciphertext, size_t cipher_len,
                            uint8_t *plaintext, size_t *plain_len);

// --- Utilities ---

int  eb_crypto_random_bytes(uint8_t *buf, size_t len);
bool eb_crypto_constant_time_compare(const uint8_t *a, const uint8_t *b, size_t len);
void eb_crypto_secure_zero(void *ptr, size_t len);
void eb_crypto_hex_encode(const uint8_t *data, size_t len, char *hex_out);
int  eb_crypto_hex_decode(const char *hex, uint8_t *out, size_t out_max);
int  eb_crypto_base64_encode(const uint8_t *data, size_t len, char *out, size_t out_max);
int  eb_crypto_base64_decode(const char *b64, uint8_t *out, size_t out_max);

// --- Key Derivation ---

int  eb_crypto_pbkdf2_sha256(const char *password, size_t pass_len,
                              const uint8_t *salt, size_t salt_len,
                              int iterations,
                              uint8_t *derived_key, size_t key_len);

#endif /* eBrowser_CRYPTO_H */
