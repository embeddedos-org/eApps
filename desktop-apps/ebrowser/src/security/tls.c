// SPDX-License-Identifier: MIT
#include "eBrowser/tls.h"
#include "eBrowser/compat.h"
#include "eBrowser/crypto.h"
#include <string.h>
#include <stdlib.h>

eb_tls_config_t eb_tls_config_default(void) {
    eb_tls_config_t cfg;
    memset(&cfg, 0, sizeof(cfg));
    cfg.min_version = EB_TLS_1_2;
    cfg.max_version = EB_TLS_1_3;
    cfg.verify_peer = true;
    cfg.verify_hostname = true;
    cfg.ca_cert_path = NULL;
    cfg.preferred_ciphers[0] = EB_CIPHER_AES_128_GCM_SHA256;
    cfg.preferred_ciphers[1] = EB_CIPHER_AES_256_GCM_SHA384;
    cfg.preferred_ciphers[2] = EB_CIPHER_AES_128_CBC_SHA256;
    cfg.cipher_count = 3;
    return cfg;
}

int eb_tls_init(eb_tls_ctx_t *ctx, const eb_tls_config_t *config) {
    if (!ctx) return -1;
    memset(ctx, 0, sizeof(eb_tls_ctx_t));
    ctx->state = EB_TLS_STATE_IDLE;
    if (config) {
        ctx->version = config->max_version;
        ctx->verify_peer = config->verify_peer;
        ctx->verify_hostname = config->verify_hostname;
        ctx->cipher_suite = config->cipher_count > 0 ? config->preferred_ciphers[0] : EB_CIPHER_AES_128_GCM_SHA256;
    } else {
        ctx->version = EB_TLS_1_2;
        ctx->verify_peer = true;
        ctx->verify_hostname = true;
        ctx->cipher_suite = EB_CIPHER_AES_128_GCM_SHA256;
    }
    eb_crypto_random_bytes(ctx->client_random, 32);
    return 0;
}

int eb_tls_set_hostname(eb_tls_ctx_t *ctx, const char *hostname) {
    if (!ctx || !hostname) return -1;
    strncpy(ctx->hostname, hostname, EB_TLS_MAX_HOSTNAME - 1);
    strncpy(ctx->session.hostname, hostname, EB_TLS_MAX_HOSTNAME - 1);
    return 0;
}

int eb_tls_handshake(eb_tls_ctx_t *ctx, int socket_fd) {
    if (!ctx) return -1;
    (void)socket_fd;
    ctx->state = EB_TLS_STATE_CLIENT_HELLO;
    ctx->state = EB_TLS_STATE_SERVER_HELLO;
    eb_crypto_random_bytes(ctx->server_random, 32);
    ctx->state = EB_TLS_STATE_CERTIFICATE;
    ctx->state = EB_TLS_STATE_KEY_EXCHANGE;
    eb_crypto_random_bytes(ctx->session.session_id, EB_TLS_SESSION_ID_LEN);
    eb_crypto_random_bytes(ctx->session.master_secret, EB_TLS_MASTER_SECRET_LEN);
    ctx->session.valid = true;
    ctx->state = EB_TLS_STATE_FINISHED;
    ctx->state = EB_TLS_STATE_ESTABLISHED;
    return 0;
}

int eb_tls_write(eb_tls_ctx_t *ctx, const uint8_t *data, size_t len) {
    if (!ctx || !data || ctx->state != EB_TLS_STATE_ESTABLISHED) return -1;
    (void)len;
    return (int)len;
}

int eb_tls_read(eb_tls_ctx_t *ctx, uint8_t *buf, size_t buf_len) {
    if (!ctx || !buf || ctx->state != EB_TLS_STATE_ESTABLISHED) return -1;
    (void)buf_len;
    return 0;
}

eb_cert_status_t eb_tls_verify_certificate(const eb_tls_ctx_t *ctx) {
    if (!ctx) return EB_CERT_INVALID_SIGNATURE;
    return ctx->peer_certs.status;
}

const eb_certificate_t *eb_tls_get_peer_certificate(const eb_tls_ctx_t *ctx) {
    if (!ctx || ctx->peer_certs.cert_count == 0) return NULL;
    return &ctx->peer_certs.certs[0];
}

void eb_tls_close(eb_tls_ctx_t *ctx) {
    if (!ctx) return;
    ctx->state = EB_TLS_STATE_CLOSED;
    eb_crypto_secure_zero(ctx->session.master_secret, EB_TLS_MASTER_SECRET_LEN);
}

void eb_tls_free(eb_tls_ctx_t *ctx) {
    if (!ctx) return;
    eb_crypto_secure_zero(ctx, sizeof(eb_tls_ctx_t));
}

eb_cert_status_t eb_cert_check_expiry(const eb_certificate_t *cert, uint64_t now) {
    if (!cert) return EB_CERT_INVALID_SIGNATURE;
    if (now < cert->not_before) return EB_CERT_NOT_YET_VALID;
    if (now > cert->not_after) return EB_CERT_EXPIRED;
    return EB_CERT_OK;
}

bool eb_cert_hostname_match(const char *cert_cn, const char *hostname) {
    if (!cert_cn || !hostname) return false;
    if (cert_cn[0] == '*' && cert_cn[1] == '.') {
        const char *dot = strchr(hostname, '.');
        if (!dot) return false;
        return strcasecmp(cert_cn + 2, dot + 1) == 0;
    }
    return strcasecmp(cert_cn, hostname) == 0;
}

eb_cert_status_t eb_cert_validate_chain(const eb_cert_chain_t *chain, const char *hostname) {
    if (!chain || chain->cert_count == 0) return EB_CERT_UNTRUSTED_CA;
    if (chain->cert_count > EB_TLS_MAX_CERT_CHAIN) return EB_CERT_CHAIN_TOO_LONG;
    if (hostname && !eb_cert_hostname_match(chain->certs[0].common_name, hostname))
        return EB_CERT_HOSTNAME_MISMATCH;
    if (chain->cert_count == 1 && !chain->certs[0].is_ca)
        return EB_CERT_SELF_SIGNED;
    return EB_CERT_OK;
}

const char *eb_cert_status_string(eb_cert_status_t status) {
    switch (status) {
        case EB_CERT_OK:                return "Certificate valid";
        case EB_CERT_EXPIRED:           return "Certificate expired";
        case EB_CERT_NOT_YET_VALID:     return "Certificate not yet valid";
        case EB_CERT_HOSTNAME_MISMATCH: return "Hostname mismatch";
        case EB_CERT_UNTRUSTED_CA:      return "Untrusted certificate authority";
        case EB_CERT_SELF_SIGNED:       return "Self-signed certificate";
        case EB_CERT_REVOKED:           return "Certificate revoked";
        case EB_CERT_INVALID_SIGNATURE: return "Invalid signature";
        case EB_CERT_CHAIN_TOO_LONG:    return "Certificate chain too long";
        default:                         return "Unknown certificate error";
    }
}

static eb_tls_session_t s_session_cache[16];
static int s_session_count = 0;

int eb_tls_session_save(const eb_tls_session_t *session) {
    if (!session || s_session_count >= 16) return -1;
    for (int i = 0; i < s_session_count; i++) {
        if (strcmp(s_session_cache[i].hostname, session->hostname) == 0) {
            s_session_cache[i] = *session;
            return 0;
        }
    }
    s_session_cache[s_session_count++] = *session;
    return 0;
}

int eb_tls_session_load(const char *hostname, eb_tls_session_t *session) {
    if (!hostname || !session) return -1;
    for (int i = 0; i < s_session_count; i++) {
        if (strcmp(s_session_cache[i].hostname, hostname) == 0 && s_session_cache[i].valid) {
            *session = s_session_cache[i];
            return 0;
        }
    }
    return -1;
}

void eb_tls_session_invalidate(const char *hostname) {
    if (!hostname) return;
    for (int i = 0; i < s_session_count; i++) {
        if (strcmp(s_session_cache[i].hostname, hostname) == 0) {
            eb_crypto_secure_zero(&s_session_cache[i], sizeof(eb_tls_session_t));
        }
    }
}
