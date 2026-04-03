// SPDX-License-Identifier: MIT
#ifndef eBrowser_TLS_H
#define eBrowser_TLS_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#define EB_TLS_MAX_CERT_CHAIN   8
#define EB_TLS_MAX_HOSTNAME     256
#define EB_TLS_SESSION_ID_LEN   32
#define EB_TLS_MASTER_SECRET_LEN 48
#define EB_TLS_MAX_RECORD_SIZE  16384

typedef enum {
    EB_TLS_1_2 = 0x0303,
    EB_TLS_1_3 = 0x0304
} eb_tls_version_t;

typedef enum {
    EB_CIPHER_AES_128_CBC_SHA256   = 0x003C,
    EB_CIPHER_AES_256_CBC_SHA256   = 0x003D,
    EB_CIPHER_AES_128_GCM_SHA256   = 0x009C,
    EB_CIPHER_AES_256_GCM_SHA384   = 0x009D
} eb_cipher_suite_t;

typedef enum {
    EB_TLS_STATE_IDLE,
    EB_TLS_STATE_CLIENT_HELLO,
    EB_TLS_STATE_SERVER_HELLO,
    EB_TLS_STATE_CERTIFICATE,
    EB_TLS_STATE_KEY_EXCHANGE,
    EB_TLS_STATE_FINISHED,
    EB_TLS_STATE_ESTABLISHED,
    EB_TLS_STATE_ERROR,
    EB_TLS_STATE_CLOSED
} eb_tls_state_t;

typedef enum {
    EB_CERT_OK = 0,
    EB_CERT_EXPIRED,
    EB_CERT_NOT_YET_VALID,
    EB_CERT_HOSTNAME_MISMATCH,
    EB_CERT_UNTRUSTED_CA,
    EB_CERT_SELF_SIGNED,
    EB_CERT_REVOKED,
    EB_CERT_INVALID_SIGNATURE,
    EB_CERT_CHAIN_TOO_LONG
} eb_cert_status_t;

typedef struct {
    char     subject[256];
    char     issuer[256];
    char     common_name[256];
    char     serial[64];
    uint64_t not_before;
    uint64_t not_after;
    bool     is_ca;
    uint8_t  fingerprint_sha256[32];
    const uint8_t *raw_data;
    size_t   raw_len;
} eb_certificate_t;

typedef struct {
    eb_certificate_t certs[EB_TLS_MAX_CERT_CHAIN];
    int              cert_count;
    eb_cert_status_t status;
} eb_cert_chain_t;

typedef struct {
    uint8_t  session_id[EB_TLS_SESSION_ID_LEN];
    uint8_t  master_secret[EB_TLS_MASTER_SECRET_LEN];
    uint64_t created_at;
    uint64_t expires_at;
    char     hostname[EB_TLS_MAX_HOSTNAME];
    bool     valid;
} eb_tls_session_t;

typedef struct {
    eb_tls_version_t   version;
    eb_tls_state_t     state;
    eb_cipher_suite_t  cipher_suite;
    eb_cert_chain_t    peer_certs;
    eb_tls_session_t   session;
    char               hostname[EB_TLS_MAX_HOSTNAME];
    bool               verify_peer;
    bool               verify_hostname;
    uint8_t            client_random[32];
    uint8_t            server_random[32];
} eb_tls_ctx_t;

typedef struct {
    eb_tls_version_t  min_version;
    eb_tls_version_t  max_version;
    bool              verify_peer;
    bool              verify_hostname;
    const char       *ca_cert_path;
    eb_cipher_suite_t preferred_ciphers[8];
    int               cipher_count;
} eb_tls_config_t;

eb_tls_config_t  eb_tls_config_default(void);
int              eb_tls_init(eb_tls_ctx_t *ctx, const eb_tls_config_t *config);
int              eb_tls_set_hostname(eb_tls_ctx_t *ctx, const char *hostname);
int              eb_tls_handshake(eb_tls_ctx_t *ctx, int socket_fd);
int              eb_tls_write(eb_tls_ctx_t *ctx, const uint8_t *data, size_t len);
int              eb_tls_read(eb_tls_ctx_t *ctx, uint8_t *buf, size_t buf_len);
eb_cert_status_t eb_tls_verify_certificate(const eb_tls_ctx_t *ctx);
const eb_certificate_t *eb_tls_get_peer_certificate(const eb_tls_ctx_t *ctx);
void             eb_tls_close(eb_tls_ctx_t *ctx);
void             eb_tls_free(eb_tls_ctx_t *ctx);

eb_cert_status_t eb_cert_validate_chain(const eb_cert_chain_t *chain, const char *hostname);
eb_cert_status_t eb_cert_check_expiry(const eb_certificate_t *cert, uint64_t now);
bool             eb_cert_hostname_match(const char *cert_cn, const char *hostname);
const char      *eb_cert_status_string(eb_cert_status_t status);

int              eb_tls_session_save(const eb_tls_session_t *session);
int              eb_tls_session_load(const char *hostname, eb_tls_session_t *session);
void             eb_tls_session_invalidate(const char *hostname);

#endif /* eBrowser_TLS_H */
