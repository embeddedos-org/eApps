// SPDX-License-Identifier: MIT
#include "eBrowser/crypto.h"
#include <string.h>
#include <stdlib.h>
#include <stdio.h>

// --- SHA-256 Constants ---
static const uint32_t K[64] = {
    0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
    0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
    0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
    0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
    0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
    0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
    0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
    0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2
};

#define ROTR(x,n) (((x)>>(n))|((x)<<(32-(n))))
#define CH(x,y,z)  (((x)&(y))^(~(x)&(z)))
#define MAJ(x,y,z) (((x)&(y))^((x)&(z))^((y)&(z)))
#define EP0(x) (ROTR(x,2)^ROTR(x,13)^ROTR(x,22))
#define EP1(x) (ROTR(x,6)^ROTR(x,11)^ROTR(x,25))
#define SIG0(x) (ROTR(x,7)^ROTR(x,18)^((x)>>3))
#define SIG1(x) (ROTR(x,17)^ROTR(x,19)^((x)>>10))

static void sha256_transform(eb_sha256_ctx_t *ctx, const uint8_t block[64]) {
    uint32_t W[64], a,b,c,d,e,f,g,h,t1,t2;
    for (int i = 0; i < 16; i++)
        W[i] = ((uint32_t)block[i*4]<<24)|((uint32_t)block[i*4+1]<<16)|
               ((uint32_t)block[i*4+2]<<8)|block[i*4+3];
    for (int i = 16; i < 64; i++)
        W[i] = SIG1(W[i-2]) + W[i-7] + SIG0(W[i-15]) + W[i-16];
    a=ctx->state[0]; b=ctx->state[1]; c=ctx->state[2]; d=ctx->state[3];
    e=ctx->state[4]; f=ctx->state[5]; g=ctx->state[6]; h=ctx->state[7];
    for (int i = 0; i < 64; i++) {
        t1 = h + EP1(e) + CH(e,f,g) + K[i] + W[i];
        t2 = EP0(a) + MAJ(a,b,c);
        h=g; g=f; f=e; e=d+t1; d=c; c=b; b=a; a=t1+t2;
    }
    ctx->state[0]+=a; ctx->state[1]+=b; ctx->state[2]+=c; ctx->state[3]+=d;
    ctx->state[4]+=e; ctx->state[5]+=f; ctx->state[6]+=g; ctx->state[7]+=h;
}

void eb_sha256_init(eb_sha256_ctx_t *ctx) {
    if (!ctx) return;
    ctx->state[0]=0x6a09e667; ctx->state[1]=0xbb67ae85;
    ctx->state[2]=0x3c6ef372; ctx->state[3]=0xa54ff53a;
    ctx->state[4]=0x510e527f; ctx->state[5]=0x9b05688c;
    ctx->state[6]=0x1f83d9ab; ctx->state[7]=0x5be0cd19;
    ctx->bit_count = 0;
    ctx->buffer_len = 0;
}

void eb_sha256_update(eb_sha256_ctx_t *ctx, const uint8_t *data, size_t len) {
    if (!ctx || !data) return;
    for (size_t i = 0; i < len; i++) {
        ctx->buffer[ctx->buffer_len++] = data[i];
        if (ctx->buffer_len == 64) {
            sha256_transform(ctx, ctx->buffer);
            ctx->bit_count += 512;
            ctx->buffer_len = 0;
        }
    }
}

void eb_sha256_final(eb_sha256_ctx_t *ctx, uint8_t digest[EB_SHA256_DIGEST_SIZE]) {
    if (!ctx || !digest) return;
    ctx->bit_count += ctx->buffer_len * 8;
    ctx->buffer[ctx->buffer_len++] = 0x80;
    if (ctx->buffer_len > 56) {
        while (ctx->buffer_len < 64) ctx->buffer[ctx->buffer_len++] = 0;
        sha256_transform(ctx, ctx->buffer);
        ctx->buffer_len = 0;
    }
    while (ctx->buffer_len < 56) ctx->buffer[ctx->buffer_len++] = 0;
    for (int i = 7; i >= 0; i--)
        ctx->buffer[ctx->buffer_len++] = (uint8_t)(ctx->bit_count >> (i*8));
    sha256_transform(ctx, ctx->buffer);
    for (int i = 0; i < 8; i++) {
        digest[i*4]   = (uint8_t)(ctx->state[i]>>24);
        digest[i*4+1] = (uint8_t)(ctx->state[i]>>16);
        digest[i*4+2] = (uint8_t)(ctx->state[i]>>8);
        digest[i*4+3] = (uint8_t)(ctx->state[i]);
    }
}

void eb_sha256(const uint8_t *data, size_t len, uint8_t digest[EB_SHA256_DIGEST_SIZE]) {
    eb_sha256_ctx_t ctx;
    eb_sha256_init(&ctx);
    eb_sha256_update(&ctx, data, len);
    eb_sha256_final(&ctx, digest);
}

// --- HMAC-SHA256 ---

void eb_hmac_sha256_init(eb_hmac_sha256_ctx_t *ctx, const uint8_t *key, size_t key_len) {
    if (!ctx || !key) return;
    uint8_t key_block[EB_SHA256_BLOCK_SIZE];
    memset(key_block, 0, sizeof(key_block));
    if (key_len > EB_SHA256_BLOCK_SIZE) {
        eb_sha256(key, key_len, key_block);
    } else {
        memcpy(key_block, key, key_len);
    }
    uint8_t ipad[EB_SHA256_BLOCK_SIZE], opad[EB_SHA256_BLOCK_SIZE];
    for (int i = 0; i < EB_SHA256_BLOCK_SIZE; i++) {
        ipad[i] = key_block[i] ^ 0x36;
        opad[i] = key_block[i] ^ 0x5c;
    }
    memcpy(ctx->key_pad, opad, EB_SHA256_BLOCK_SIZE);
    eb_sha256_init(&ctx->inner);
    eb_sha256_update(&ctx->inner, ipad, EB_SHA256_BLOCK_SIZE);
    eb_crypto_secure_zero(key_block, sizeof(key_block));
    eb_crypto_secure_zero(ipad, sizeof(ipad));
}

void eb_hmac_sha256_update(eb_hmac_sha256_ctx_t *ctx, const uint8_t *data, size_t len) {
    if (!ctx) return;
    eb_sha256_update(&ctx->inner, data, len);
}

void eb_hmac_sha256_final(eb_hmac_sha256_ctx_t *ctx, uint8_t mac[EB_HMAC_SHA256_SIZE]) {
    if (!ctx || !mac) return;
    uint8_t inner_hash[EB_SHA256_DIGEST_SIZE];
    eb_sha256_final(&ctx->inner, inner_hash);
    eb_sha256_init(&ctx->outer);
    eb_sha256_update(&ctx->outer, ctx->key_pad, EB_SHA256_BLOCK_SIZE);
    eb_sha256_update(&ctx->outer, inner_hash, EB_SHA256_DIGEST_SIZE);
    eb_sha256_final(&ctx->outer, mac);
    eb_crypto_secure_zero(inner_hash, sizeof(inner_hash));
}

void eb_hmac_sha256(const uint8_t *key, size_t key_len,
                     const uint8_t *data, size_t data_len,
                     uint8_t mac[EB_HMAC_SHA256_SIZE]) {
    eb_hmac_sha256_ctx_t ctx;
    eb_hmac_sha256_init(&ctx, key, key_len);
    eb_hmac_sha256_update(&ctx, data, data_len);
    eb_hmac_sha256_final(&ctx, mac);
    eb_crypto_secure_zero(&ctx, sizeof(ctx));
}

// --- AES-128 ---

static const uint8_t sbox[256] = {
    0x63,0x7c,0x77,0x7b,0xf2,0x6b,0x6f,0xc5,0x30,0x01,0x67,0x2b,0xfe,0xd7,0xab,0x76,
    0xca,0x82,0xc9,0x7d,0xfa,0x59,0x47,0xf0,0xad,0xd4,0xa2,0xaf,0x9c,0xa4,0x72,0xc0,
    0xb7,0xfd,0x93,0x26,0x36,0x3f,0xf7,0xcc,0x34,0xa5,0xe5,0xf1,0x71,0xd8,0x31,0x15,
    0x04,0xc7,0x23,0xc3,0x18,0x96,0x05,0x9a,0x07,0x12,0x80,0xe2,0xeb,0x27,0xb2,0x75,
    0x09,0x83,0x2c,0x1a,0x1b,0x6e,0x5a,0xa0,0x52,0x3b,0xd6,0xb3,0x29,0xe3,0x2f,0x84,
    0x53,0xd1,0x00,0xed,0x20,0xfc,0xb1,0x5b,0x6a,0xcb,0xbe,0x39,0x4a,0x4c,0x58,0xcf,
    0xd0,0xef,0xaa,0xfb,0x43,0x4d,0x33,0x85,0x45,0xf9,0x02,0x7f,0x50,0x3c,0x9f,0xa8,
    0x51,0xa3,0x40,0x8f,0x92,0x9d,0x38,0xf5,0xbc,0xb6,0xda,0x21,0x10,0xff,0xf3,0xd2,
    0xcd,0x0c,0x13,0xec,0x5f,0x97,0x44,0x17,0xc4,0xa7,0x7e,0x3d,0x64,0x5d,0x19,0x73,
    0x60,0x81,0x4f,0xdc,0x22,0x2a,0x90,0x88,0x46,0xee,0xb8,0x14,0xde,0x5e,0x0b,0xdb,
    0xe0,0x32,0x3a,0x0a,0x49,0x06,0x24,0x5c,0xc2,0xd3,0xac,0x62,0x91,0x95,0xe4,0x79,
    0xe7,0xc8,0x37,0x6d,0x8d,0xd5,0x4e,0xa9,0x6c,0x56,0xf4,0xea,0x65,0x7a,0xae,0x08,
    0xba,0x78,0x25,0x2e,0x1c,0xa6,0xb4,0xc6,0xe8,0xdd,0x74,0x1f,0x4b,0xbd,0x8b,0x8a,
    0x70,0x3e,0xb5,0x66,0x48,0x03,0xf6,0x0e,0x61,0x35,0x57,0xb9,0x86,0xc1,0x1d,0x9e,
    0xe1,0xf8,0x98,0x11,0x69,0xd9,0x8e,0x94,0x9b,0x1e,0x87,0xe9,0xce,0x55,0x28,0xdf,
    0x8c,0xa1,0x89,0x0d,0xbf,0xe6,0x42,0x68,0x41,0x99,0x2d,0x0f,0xb0,0x54,0xbb,0x16
};

static const uint8_t rsbox[256] = {
    0x52,0x09,0x6a,0xd5,0x30,0x36,0xa5,0x38,0xbf,0x40,0xa3,0x9e,0x81,0xf3,0xd7,0xfb,
    0x7c,0xe3,0x39,0x82,0x9b,0x2f,0xff,0x87,0x34,0x8e,0x43,0x44,0xc4,0xde,0xe9,0xcb,
    0x54,0x7b,0x94,0x32,0xa6,0xc2,0x23,0x3d,0xee,0x4c,0x95,0x0b,0x42,0xfa,0xc3,0x4e,
    0x08,0x2e,0xa1,0x66,0x28,0xd9,0x24,0xb2,0x76,0x5b,0xa2,0x49,0x6d,0x8b,0xd1,0x25,
    0x72,0xf8,0xf6,0x64,0x86,0x68,0x98,0x16,0xd4,0xa4,0x5c,0xcc,0x5d,0x65,0xb6,0x92,
    0x6c,0x70,0x48,0x50,0xfd,0xed,0xb9,0xda,0x5e,0x15,0x46,0x57,0xa7,0x8d,0x9d,0x84,
    0x90,0xd8,0xab,0x00,0x8c,0xbc,0xd3,0x0a,0xf7,0xe4,0x58,0x05,0xb8,0xb3,0x45,0x06,
    0xd0,0x2c,0x1e,0x8f,0xca,0x3f,0x0f,0x02,0xc1,0xaf,0xbd,0x03,0x01,0x13,0x8a,0x6b,
    0x3a,0x91,0x11,0x41,0x4f,0x67,0xdc,0xea,0x97,0xf2,0xcf,0xce,0xf0,0xb4,0xe6,0x73,
    0x96,0xac,0x74,0x22,0xe7,0xad,0x35,0x85,0xe2,0xf9,0x37,0xe8,0x1c,0x75,0xdf,0x6e,
    0x47,0xf1,0x1a,0x71,0x1d,0x29,0xc5,0x89,0x6f,0xb7,0x62,0x0e,0xaa,0x18,0xbe,0x1b,
    0xfc,0x56,0x3e,0x4b,0xc6,0xd2,0x79,0x20,0x9a,0xdb,0xc0,0xfe,0x78,0xcd,0x5a,0xf4,
    0x1f,0xdd,0xa8,0x33,0x88,0x07,0xc7,0x31,0xb1,0x12,0x10,0x59,0x27,0x80,0xec,0x5f,
    0x60,0x51,0x7f,0xa9,0x19,0xb5,0x4a,0x0d,0x2d,0xe5,0x7a,0x9f,0x93,0xc9,0x9c,0xef,
    0xa0,0xe0,0x3b,0x4d,0xae,0x2a,0xf5,0xb0,0xc8,0xeb,0xbb,0x3c,0x83,0x53,0x99,0x61,
    0x17,0x2b,0x04,0x7e,0xba,0x77,0xd6,0x26,0xe1,0x69,0x14,0x63,0x55,0x21,0x0c,0x7d
};

static const uint8_t rcon[11] = {0x8d,0x01,0x02,0x04,0x08,0x10,0x20,0x40,0x80,0x1b,0x36};

static uint8_t xtime(uint8_t x) { return (uint8_t)((x<<1) ^ (((x>>7)&1)*0x1b)); }

void eb_aes128_init(eb_aes128_ctx_t *ctx, const uint8_t key[EB_AES128_KEY_SIZE]) {
    if (!ctx || !key) return;
    for (int i = 0; i < 4; i++)
        ctx->round_keys[i] = ((uint32_t)key[4*i]<<24)|((uint32_t)key[4*i+1]<<16)|
                              ((uint32_t)key[4*i+2]<<8)|key[4*i+3];
    for (int i = 4; i < 44; i++) {
        uint32_t t = ctx->round_keys[i-1];
        if (i % 4 == 0) {
            t = ((uint32_t)sbox[(t>>16)&0xff]<<24)|((uint32_t)sbox[(t>>8)&0xff]<<16)|
                ((uint32_t)sbox[t&0xff]<<8)|sbox[(t>>24)&0xff];
            t ^= (uint32_t)rcon[i/4] << 24;
        }
        ctx->round_keys[i] = ctx->round_keys[i-4] ^ t;
    }
}

void eb_aes128_encrypt_block(const eb_aes128_ctx_t *ctx,
                              const uint8_t in[16], uint8_t out[16]) {
    if (!ctx || !in || !out) return;
    uint8_t state[4][4];
    for (int i = 0; i < 4; i++)
        for (int j = 0; j < 4; j++)
            state[j][i] = in[i*4+j];

    for (int i = 0; i < 4; i++)
        for (int j = 0; j < 4; j++)
            state[j][i] ^= (uint8_t)(ctx->round_keys[i] >> (24-8*j));

    for (int round = 1; round <= 10; round++) {
        for (int i = 0; i < 4; i++)
            for (int j = 0; j < 4; j++)
                state[i][j] = sbox[state[i][j]];

        uint8_t tmp;
        tmp=state[1][0]; state[1][0]=state[1][1]; state[1][1]=state[1][2]; state[1][2]=state[1][3]; state[1][3]=tmp;
        tmp=state[2][0]; state[2][0]=state[2][2]; state[2][2]=tmp; tmp=state[2][1]; state[2][1]=state[2][3]; state[2][3]=tmp;
        tmp=state[3][3]; state[3][3]=state[3][2]; state[3][2]=state[3][1]; state[3][1]=state[3][0]; state[3][0]=tmp;

        if (round < 10) {
            for (int i = 0; i < 4; i++) {
                uint8_t a=state[0][i],b=state[1][i],c=state[2][i],d=state[3][i];
                state[0][i] = xtime(a)^xtime(b)^b^c^d;
                state[1][i] = a^xtime(b)^xtime(c)^c^d;
                state[2][i] = a^b^xtime(c)^xtime(d)^d;
                state[3][i] = xtime(a)^a^b^c^xtime(d);
            }
        }

        for (int i = 0; i < 4; i++)
            for (int j = 0; j < 4; j++)
                state[j][i] ^= (uint8_t)(ctx->round_keys[round*4+i] >> (24-8*j));
    }

    for (int i = 0; i < 4; i++)
        for (int j = 0; j < 4; j++)
            out[i*4+j] = state[j][i];
}

void eb_aes128_decrypt_block(const eb_aes128_ctx_t *ctx,
                              const uint8_t in[16], uint8_t out[16]) {
    if (!ctx || !in || !out) return;
    uint8_t state[4][4];
    for (int i = 0; i < 4; i++)
        for (int j = 0; j < 4; j++)
            state[j][i] = in[i*4+j];

    for (int i = 0; i < 4; i++)
        for (int j = 0; j < 4; j++)
            state[j][i] ^= (uint8_t)(ctx->round_keys[40+i] >> (24-8*j));

    for (int round = 9; round >= 0; round--) {
        uint8_t tmp;
        tmp=state[1][3]; state[1][3]=state[1][2]; state[1][2]=state[1][1]; state[1][1]=state[1][0]; state[1][0]=tmp;
        tmp=state[2][0]; state[2][0]=state[2][2]; state[2][2]=tmp; tmp=state[2][1]; state[2][1]=state[2][3]; state[2][3]=tmp;
        tmp=state[3][0]; state[3][0]=state[3][1]; state[3][1]=state[3][2]; state[3][2]=state[3][3]; state[3][3]=tmp;

        for (int i = 0; i < 4; i++)
            for (int j = 0; j < 4; j++)
                state[i][j] = rsbox[state[i][j]];

        for (int i = 0; i < 4; i++)
            for (int j = 0; j < 4; j++)
                state[j][i] ^= (uint8_t)(ctx->round_keys[round*4+i] >> (24-8*j));

        if (round > 0) {
            for (int i = 0; i < 4; i++) {
                uint8_t a=state[0][i],b=state[1][i],c=state[2][i],d=state[3][i];
                uint8_t x9=xtime(xtime(xtime(a)))^a, xb=xtime(xtime(xtime(a))^a)^a;
                uint8_t xd=xtime(xtime(xtime(a)^a))^a, xe=xtime(xtime(xtime(a)^a)^a);
                (void)x9; (void)xb; (void)xd; (void)xe;
                uint8_t a9=xtime(xtime(xtime(a)))^a,ab=xtime(xtime(xtime(a))^a)^a,ad=xtime(xtime(xtime(a)^a))^a,ae=xtime(xtime(xtime(a)^a)^a);
                uint8_t b9=xtime(xtime(xtime(b)))^b,bb=xtime(xtime(xtime(b))^b)^b,bd=xtime(xtime(xtime(b)^b))^b,be=xtime(xtime(xtime(b)^b)^b);
                uint8_t c9=xtime(xtime(xtime(c)))^c,cb=xtime(xtime(xtime(c))^c)^c,cd_=xtime(xtime(xtime(c)^c))^c,ce=xtime(xtime(xtime(c)^c)^c);
                uint8_t d9=xtime(xtime(xtime(d)))^d,db=xtime(xtime(xtime(d))^d)^d,dd_=xtime(xtime(xtime(d)^d))^d,de=xtime(xtime(xtime(d)^d)^d);
                state[0][i]=ae^bb^cd_^d9;
                state[1][i]=a9^be^cb^dd_;
                state[2][i]=ad^b9^ce^db;
                state[3][i]=ab^bd^c9^de;
            }
        }
    }

    for (int i = 0; i < 4; i++)
        for (int j = 0; j < 4; j++)
            out[i*4+j] = state[j][i];
}

int eb_aes128_cbc_encrypt(const uint8_t key[16], const uint8_t iv[16],
                           const uint8_t *plaintext, size_t plain_len,
                           uint8_t *ciphertext, size_t *cipher_len) {
    if (!key || !iv || !plaintext || !ciphertext || !cipher_len) return -1;
    size_t pad = 16 - (plain_len % 16);
    *cipher_len = plain_len + pad;
    eb_aes128_ctx_t ctx;
    eb_aes128_init(&ctx, key);
    uint8_t prev[16];
    memcpy(prev, iv, 16);
    size_t offset = 0;
    while (offset < *cipher_len) {
        uint8_t block[16];
        for (int i = 0; i < 16; i++) {
            size_t idx = offset + (size_t)i;
            block[i] = (idx < plain_len) ? plaintext[idx] : (uint8_t)pad;
            block[i] ^= prev[i];
        }
        eb_aes128_encrypt_block(&ctx, block, ciphertext + offset);
        memcpy(prev, ciphertext + offset, 16);
        offset += 16;
    }
    eb_crypto_secure_zero(&ctx, sizeof(ctx));
    return 0;
}

int eb_aes128_cbc_decrypt(const uint8_t key[16], const uint8_t iv[16],
                           const uint8_t *ciphertext, size_t cipher_len,
                           uint8_t *plaintext, size_t *plain_len) {
    if (!key || !iv || !ciphertext || !plaintext || !plain_len) return -1;
    if (cipher_len == 0 || cipher_len % 16 != 0) return -1;
    eb_aes128_ctx_t ctx;
    eb_aes128_init(&ctx, key);
    const uint8_t *prev = iv;
    for (size_t offset = 0; offset < cipher_len; offset += 16) {
        uint8_t block[16];
        eb_aes128_decrypt_block(&ctx, ciphertext + offset, block);
        for (int i = 0; i < 16; i++)
            plaintext[offset + (size_t)i] = block[i] ^ prev[i];
        prev = ciphertext + offset;
    }
    uint8_t pad = plaintext[cipher_len - 1];
    if (pad < 1 || pad > 16) { eb_crypto_secure_zero(&ctx, sizeof(ctx)); return -1; }
    for (uint8_t i = 0; i < pad; i++) {
        if (plaintext[cipher_len - 1 - i] != pad) { eb_crypto_secure_zero(&ctx, sizeof(ctx)); return -1; }
    }
    *plain_len = cipher_len - pad;
    eb_crypto_secure_zero(&ctx, sizeof(ctx));
    return 0;
}

// --- Utilities ---

int eb_crypto_random_bytes(uint8_t *buf, size_t len) {
    if (!buf) return -1;
#if defined(_WIN32)
    for (size_t i = 0; i < len; i++) buf[i] = (uint8_t)(rand() & 0xFF);
#elif defined(__linux__) || defined(__APPLE__)
    FILE *f = fopen("/dev/urandom", "rb");
    if (!f) { for (size_t i = 0; i < len; i++) buf[i] = (uint8_t)(rand() & 0xFF); return 0; }
    size_t r = fread(buf, 1, len, f);
    fclose(f);
    if (r != len) return -1;
#else
    for (size_t i = 0; i < len; i++) buf[i] = (uint8_t)(rand() & 0xFF);
#endif
    return 0;
}

bool eb_crypto_constant_time_compare(const uint8_t *a, const uint8_t *b, size_t len) {
    if (!a || !b) return false;
    volatile uint8_t diff = 0;
    for (size_t i = 0; i < len; i++) diff |= a[i] ^ b[i];
    return diff == 0;
}

void eb_crypto_secure_zero(void *ptr, size_t len) {
    if (!ptr) return;
    volatile uint8_t *p = (volatile uint8_t *)ptr;
    while (len--) *p++ = 0;
}

void eb_crypto_hex_encode(const uint8_t *data, size_t len, char *hex_out) {
    if (!data || !hex_out) return;
    static const char hex[] = "0123456789abcdef";
    for (size_t i = 0; i < len; i++) {
        hex_out[i*2]   = hex[(data[i] >> 4) & 0xF];
        hex_out[i*2+1] = hex[data[i] & 0xF];
    }
    hex_out[len*2] = '\0';
}

int eb_crypto_hex_decode(const char *hex, uint8_t *out, size_t out_max) {
    if (!hex || !out) return -1;
    size_t hex_len = strlen(hex);
    if (hex_len % 2 != 0 || hex_len / 2 > out_max) return -1;
    for (size_t i = 0; i < hex_len / 2; i++) {
        uint8_t hi, lo;
        char c = hex[i*2];
        if (c >= '0' && c <= '9') hi = (uint8_t)(c - '0');
        else if (c >= 'a' && c <= 'f') hi = (uint8_t)(c - 'a' + 10);
        else if (c >= 'A' && c <= 'F') hi = (uint8_t)(c - 'A' + 10);
        else return -1;
        c = hex[i*2+1];
        if (c >= '0' && c <= '9') lo = (uint8_t)(c - '0');
        else if (c >= 'a' && c <= 'f') lo = (uint8_t)(c - 'a' + 10);
        else if (c >= 'A' && c <= 'F') lo = (uint8_t)(c - 'A' + 10);
        else return -1;
        out[i] = (hi << 4) | lo;
    }
    return (int)(hex_len / 2);
}

static const char b64_table[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";

int eb_crypto_base64_encode(const uint8_t *data, size_t len, char *out, size_t out_max) {
    if (!data || !out) return -1;
    size_t out_len = 4 * ((len + 2) / 3);
    if (out_len + 1 > out_max) return -1;
    size_t j = 0;
    for (size_t i = 0; i < len; i += 3) {
        uint32_t n = (uint32_t)data[i] << 16;
        if (i+1 < len) n |= (uint32_t)data[i+1] << 8;
        if (i+2 < len) n |= data[i+2];
        out[j++] = b64_table[(n>>18)&0x3F];
        out[j++] = b64_table[(n>>12)&0x3F];
        out[j++] = (i+1 < len) ? b64_table[(n>>6)&0x3F] : '=';
        out[j++] = (i+2 < len) ? b64_table[n&0x3F] : '=';
    }
    out[j] = '\0';
    return (int)j;
}

int eb_crypto_base64_decode(const char *b64, uint8_t *out, size_t out_max) {
    if (!b64 || !out) return -1;
    size_t len = strlen(b64);
    if (len % 4 != 0) return -1;
    size_t out_len = len / 4 * 3;
    if (b64[len-1] == '=') out_len--;
    if (b64[len-2] == '=') out_len--;
    if (out_len > out_max) return -1;
    size_t j = 0;
    for (size_t i = 0; i < len; i += 4) {
        uint32_t n = 0;
        for (int k = 0; k < 4; k++) {
            char c = b64[i+k];
            uint8_t v;
            if (c >= 'A' && c <= 'Z') v = (uint8_t)(c - 'A');
            else if (c >= 'a' && c <= 'z') v = (uint8_t)(c - 'a' + 26);
            else if (c >= '0' && c <= '9') v = (uint8_t)(c - '0' + 52);
            else if (c == '+') v = 62;
            else if (c == '/') v = 63;
            else v = 0;
            n = (n << 6) | v;
        }
        if (j < out_len) out[j++] = (uint8_t)(n >> 16);
        if (j < out_len) out[j++] = (uint8_t)(n >> 8);
        if (j < out_len) out[j++] = (uint8_t)n;
    }
    return (int)out_len;
}

// --- Key Derivation (PBKDF2-SHA256) ---

int eb_crypto_pbkdf2_sha256(const char *password, size_t pass_len,
                              const uint8_t *salt, size_t salt_len,
                              int iterations,
                              uint8_t *derived_key, size_t key_len) {
    if (!password || !salt || !derived_key || iterations < 1) return -1;
    size_t blocks = (key_len + EB_HMAC_SHA256_SIZE - 1) / EB_HMAC_SHA256_SIZE;
    for (size_t block = 1; block <= blocks; block++) {
        uint8_t u[EB_HMAC_SHA256_SIZE], t[EB_HMAC_SHA256_SIZE];
        uint8_t salt_block[1024];
        if (salt_len + 4 > sizeof(salt_block)) return -1;
        memcpy(salt_block, salt, salt_len);
        salt_block[salt_len]   = (uint8_t)(block >> 24);
        salt_block[salt_len+1] = (uint8_t)(block >> 16);
        salt_block[salt_len+2] = (uint8_t)(block >> 8);
        salt_block[salt_len+3] = (uint8_t)(block);
        eb_hmac_sha256((const uint8_t *)password, pass_len, salt_block, salt_len + 4, u);
        memcpy(t, u, EB_HMAC_SHA256_SIZE);
        for (int iter = 1; iter < iterations; iter++) {
            eb_hmac_sha256((const uint8_t *)password, pass_len, u, EB_HMAC_SHA256_SIZE, u);
            for (int j = 0; j < EB_HMAC_SHA256_SIZE; j++) t[j] ^= u[j];
        }
        size_t offset = (block - 1) * EB_HMAC_SHA256_SIZE;
        size_t copy_len = key_len - offset;
        if (copy_len > EB_HMAC_SHA256_SIZE) copy_len = EB_HMAC_SHA256_SIZE;
        memcpy(derived_key + offset, t, copy_len);
    }
    return 0;
}
