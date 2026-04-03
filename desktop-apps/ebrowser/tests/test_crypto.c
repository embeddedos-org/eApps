// SPDX-License-Identifier: MIT
// Crypto module tests for eBrowser web browser
#include "eBrowser/crypto.h"
#include <stdio.h>
#include <string.h>

static int s_pass = 0, s_fail = 0;
#define TEST(name) static void name(void)
#define RUN(name) do { printf("  %s... ", #name); name(); printf("PASS\n"); s_pass++; } while(0)
#define ASSERT(cond) do { if(!(cond)) { printf("FAIL: %s:%d: %s\n", __FILE__, __LINE__, #cond); s_fail++; return; } } while(0)

TEST(test_sha256_empty) {
    uint8_t digest[32];
    eb_sha256((const uint8_t *)"", 0, digest);
    char hex[65];
    eb_crypto_hex_encode(digest, 32, hex);
    ASSERT(strcmp(hex, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855") == 0);
}

TEST(test_sha256_abc) {
    uint8_t digest[32];
    eb_sha256((const uint8_t *)"abc", 3, digest);
    char hex[65];
    eb_crypto_hex_encode(digest, 32, hex);
    ASSERT(strcmp(hex, "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad") == 0);
}

TEST(test_sha256_long) {
    const char *msg = "abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq";
    uint8_t digest[32];
    eb_sha256((const uint8_t *)msg, strlen(msg), digest);
    char hex[65];
    eb_crypto_hex_encode(digest, 32, hex);
    ASSERT(strcmp(hex, "248d6a61d20638b8e5c026930c3e6039a33ce45964ff2167f6ecedd419db06c1") == 0);
}

TEST(test_sha256_incremental) {
    eb_sha256_ctx_t ctx;
    eb_sha256_init(&ctx);
    eb_sha256_update(&ctx, (const uint8_t *)"a", 1);
    eb_sha256_update(&ctx, (const uint8_t *)"b", 1);
    eb_sha256_update(&ctx, (const uint8_t *)"c", 1);
    uint8_t digest[32];
    eb_sha256_final(&ctx, digest);
    uint8_t expected[32];
    eb_sha256((const uint8_t *)"abc", 3, expected);
    ASSERT(eb_crypto_constant_time_compare(digest, expected, 32));
}

TEST(test_hmac_sha256) {
    uint8_t key[] = {0x0b,0x0b,0x0b,0x0b,0x0b,0x0b,0x0b,0x0b,0x0b,0x0b,
                     0x0b,0x0b,0x0b,0x0b,0x0b,0x0b,0x0b,0x0b,0x0b,0x0b};
    uint8_t mac[32];
    eb_hmac_sha256(key, 20, (const uint8_t *)"Hi There", 8, mac);
    char hex[65];
    eb_crypto_hex_encode(mac, 32, hex);
    ASSERT(strcmp(hex, "b0344c61d8db38535ca8afceaf0bf12b881dc200c9833da726e9376c2e32cff7") == 0);
}

TEST(test_hmac_sha256_incremental) {
    uint8_t key[] = "secret";
    eb_hmac_sha256_ctx_t ctx;
    eb_hmac_sha256_init(&ctx, key, 6);
    eb_hmac_sha256_update(&ctx, (const uint8_t *)"hello ", 6);
    eb_hmac_sha256_update(&ctx, (const uint8_t *)"world", 5);
    uint8_t mac1[32];
    eb_hmac_sha256_final(&ctx, mac1);
    uint8_t mac2[32];
    eb_hmac_sha256(key, 6, (const uint8_t *)"hello world", 11, mac2);
    ASSERT(eb_crypto_constant_time_compare(mac1, mac2, 32));
}

TEST(test_aes128_encrypt_decrypt_block) {
    uint8_t key[16] = {0x2b,0x7e,0x15,0x16,0x28,0xae,0xd2,0xa6,0xab,0xf7,0x15,0x88,0x09,0xcf,0x4f,0x3c};
    uint8_t plain[16] = {0x32,0x43,0xf6,0xa8,0x88,0x5a,0x30,0x8d,0x31,0x31,0x98,0xa2,0xe0,0x37,0x07,0x34};
    uint8_t cipher[16], decrypted[16];
    eb_aes128_ctx_t ctx;
    eb_aes128_init(&ctx, key);
    eb_aes128_encrypt_block(&ctx, plain, cipher);
    ASSERT(!eb_crypto_constant_time_compare(plain, cipher, 16));
    eb_aes128_decrypt_block(&ctx, cipher, decrypted);
    ASSERT(eb_crypto_constant_time_compare(plain, decrypted, 16));
}

TEST(test_aes128_cbc_roundtrip) {
    uint8_t key[16] = {1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16};
    uint8_t iv[16] = {0};
    const char *msg = "Hello, World! This is a CBC test.";
    size_t msg_len = strlen(msg);
    uint8_t cipher[64], plain[64];
    size_t cipher_len = 0, plain_len = 0;
    ASSERT(eb_aes128_cbc_encrypt(key, iv, (const uint8_t *)msg, msg_len, cipher, &cipher_len) == 0);
    ASSERT(cipher_len >= msg_len);
    ASSERT(cipher_len % 16 == 0);
    ASSERT(eb_aes128_cbc_decrypt(key, iv, cipher, cipher_len, plain, &plain_len) == 0);
    ASSERT(plain_len == msg_len);
    ASSERT(memcmp(plain, msg, msg_len) == 0);
}

TEST(test_aes128_cbc_short_message) {
    uint8_t key[16] = {0}, iv[16] = {0};
    uint8_t cipher[32], plain[32];
    size_t cipher_len, plain_len;
    ASSERT(eb_aes128_cbc_encrypt(key, iv, (const uint8_t *)"Hi", 2, cipher, &cipher_len) == 0);
    ASSERT(cipher_len == 16);
    ASSERT(eb_aes128_cbc_decrypt(key, iv, cipher, cipher_len, plain, &plain_len) == 0);
    ASSERT(plain_len == 2);
    ASSERT(memcmp(plain, "Hi", 2) == 0);
}

TEST(test_constant_time_compare) {
    uint8_t a[] = {1,2,3,4,5};
    uint8_t b[] = {1,2,3,4,5};
    uint8_t c[] = {1,2,3,4,6};
    ASSERT(eb_crypto_constant_time_compare(a, b, 5) == true);
    ASSERT(eb_crypto_constant_time_compare(a, c, 5) == false);
    ASSERT(eb_crypto_constant_time_compare(NULL, b, 5) == false);
}

TEST(test_secure_zero) {
    uint8_t buf[32];
    memset(buf, 0xFF, sizeof(buf));
    eb_crypto_secure_zero(buf, sizeof(buf));
    for (int i = 0; i < 32; i++) ASSERT(buf[i] == 0);
}

TEST(test_hex_encode) {
    uint8_t data[] = {0xDE, 0xAD, 0xBE, 0xEF};
    char hex[9];
    eb_crypto_hex_encode(data, 4, hex);
    ASSERT(strcmp(hex, "deadbeef") == 0);
}

TEST(test_hex_decode) {
    uint8_t out[4];
    ASSERT(eb_crypto_hex_decode("deadbeef", out, 4) == 4);
    ASSERT(out[0] == 0xDE && out[1] == 0xAD && out[2] == 0xBE && out[3] == 0xEF);
}

TEST(test_hex_roundtrip) {
    uint8_t original[] = {0x01,0x23,0x45,0x67,0x89,0xAB,0xCD,0xEF};
    char hex[17];
    eb_crypto_hex_encode(original, 8, hex);
    uint8_t decoded[8];
    ASSERT(eb_crypto_hex_decode(hex, decoded, 8) == 8);
    ASSERT(memcmp(original, decoded, 8) == 0);
}

TEST(test_base64_encode) {
    char out[32];
    ASSERT(eb_crypto_base64_encode((const uint8_t *)"Hello", 5, out, sizeof(out)) > 0);
    ASSERT(strcmp(out, "SGVsbG8=") == 0);
}

TEST(test_base64_decode) {
    uint8_t out[32];
    int len = eb_crypto_base64_decode("SGVsbG8=", out, sizeof(out));
    ASSERT(len == 5);
    ASSERT(memcmp(out, "Hello", 5) == 0);
}

TEST(test_base64_roundtrip) {
    const uint8_t data[] = "The quick brown fox jumps over the lazy dog";
    char encoded[128];
    ASSERT(eb_crypto_base64_encode(data, strlen((char *)data), encoded, sizeof(encoded)) > 0);
    uint8_t decoded[128];
    int len = eb_crypto_base64_decode(encoded, decoded, sizeof(decoded));
    ASSERT(len == (int)strlen((char *)data));
    ASSERT(memcmp(decoded, data, (size_t)len) == 0);
}

TEST(test_random_bytes) {
    uint8_t buf1[32], buf2[32];
    ASSERT(eb_crypto_random_bytes(buf1, 32) == 0);
    ASSERT(eb_crypto_random_bytes(buf2, 32) == 0);
}

TEST(test_pbkdf2) {
    uint8_t derived[32];
    uint8_t salt[] = "salt";
    ASSERT(eb_crypto_pbkdf2_sha256("password", 8, salt, 4, 1, derived, 32) == 0);
    bool all_zero = true;
    for (int i = 0; i < 32; i++) if (derived[i] != 0) all_zero = false;
    ASSERT(!all_zero);
}

TEST(test_pbkdf2_deterministic) {
    uint8_t d1[32], d2[32];
    uint8_t salt[] = "fixed-salt";
    eb_crypto_pbkdf2_sha256("mypass", 6, salt, 10, 100, d1, 32);
    eb_crypto_pbkdf2_sha256("mypass", 6, salt, 10, 100, d2, 32);
    ASSERT(eb_crypto_constant_time_compare(d1, d2, 32));
}

int main(void) {
    printf("=== Crypto Tests ===\n");
    RUN(test_sha256_empty);
    RUN(test_sha256_abc);
    RUN(test_sha256_long);
    RUN(test_sha256_incremental);
    RUN(test_hmac_sha256);
    RUN(test_hmac_sha256_incremental);
    RUN(test_aes128_encrypt_decrypt_block);
    RUN(test_aes128_cbc_roundtrip);
    RUN(test_aes128_cbc_short_message);
    RUN(test_constant_time_compare);
    RUN(test_secure_zero);
    RUN(test_hex_encode);
    RUN(test_hex_decode);
    RUN(test_hex_roundtrip);
    RUN(test_base64_encode);
    RUN(test_base64_decode);
    RUN(test_base64_roundtrip);
    RUN(test_random_bytes);
    RUN(test_pbkdf2);
    RUN(test_pbkdf2_deterministic);
    printf("\nResults: %d passed, %d failed\n", s_pass, s_fail);
    return s_fail > 0 ? 1 : 0;
}
