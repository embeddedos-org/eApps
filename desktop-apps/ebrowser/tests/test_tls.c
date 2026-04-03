// SPDX-License-Identifier: MIT
// TLS module tests for eBrowser web browser
#include "eBrowser/tls.h"
#include <stdio.h>
#include <string.h>

static int s_pass = 0, s_fail = 0;
#define TEST(name) static void name(void)
#define RUN(name) do { printf("  %s... ", #name); name(); printf("PASS\n"); s_pass++; } while(0)
#define ASSERT(cond) do { if(!(cond)) { printf("FAIL: %s:%d: %s\n", __FILE__, __LINE__, #cond); s_fail++; return; } } while(0)

TEST(test_config_default) {
    eb_tls_config_t cfg = eb_tls_config_default();
    ASSERT(cfg.min_version == EB_TLS_1_2);
    ASSERT(cfg.max_version == EB_TLS_1_3);
    ASSERT(cfg.verify_peer == true);
    ASSERT(cfg.verify_hostname == true);
    ASSERT(cfg.cipher_count == 3);
}

TEST(test_tls_init) {
    eb_tls_ctx_t ctx;
    ASSERT(eb_tls_init(&ctx, NULL) == 0);
    ASSERT(ctx.state == EB_TLS_STATE_IDLE);
    ASSERT(ctx.verify_peer == true);
}

TEST(test_tls_init_with_config) {
    eb_tls_config_t cfg = eb_tls_config_default();
    cfg.verify_peer = false;
    eb_tls_ctx_t ctx;
    ASSERT(eb_tls_init(&ctx, &cfg) == 0);
    ASSERT(ctx.verify_peer == false);
}

TEST(test_tls_set_hostname) {
    eb_tls_ctx_t ctx;
    eb_tls_init(&ctx, NULL);
    ASSERT(eb_tls_set_hostname(&ctx, "example.com") == 0);
    ASSERT(strcmp(ctx.hostname, "example.com") == 0);
}

TEST(test_tls_handshake) {
    eb_tls_ctx_t ctx;
    eb_tls_init(&ctx, NULL);
    ASSERT(eb_tls_handshake(&ctx, -1) == 0);
    ASSERT(ctx.state == EB_TLS_STATE_ESTABLISHED);
    ASSERT(ctx.session.valid == true);
}

TEST(test_tls_close) {
    eb_tls_ctx_t ctx;
    eb_tls_init(&ctx, NULL);
    eb_tls_handshake(&ctx, -1);
    eb_tls_close(&ctx);
    ASSERT(ctx.state == EB_TLS_STATE_CLOSED);
}

TEST(test_tls_free) {
    eb_tls_ctx_t ctx;
    eb_tls_init(&ctx, NULL);
    eb_tls_free(&ctx);
    ASSERT(ctx.state == 0);
}

TEST(test_cert_hostname_exact) {
    ASSERT(eb_cert_hostname_match("example.com", "example.com") == true);
    ASSERT(eb_cert_hostname_match("example.com", "other.com") == false);
}

TEST(test_cert_hostname_wildcard) {
    ASSERT(eb_cert_hostname_match("*.example.com", "www.example.com") == true);
    ASSERT(eb_cert_hostname_match("*.example.com", "api.example.com") == true);
    ASSERT(eb_cert_hostname_match("*.example.com", "example.com") == false);
}

TEST(test_cert_hostname_null) {
    ASSERT(eb_cert_hostname_match(NULL, "test.com") == false);
    ASSERT(eb_cert_hostname_match("test.com", NULL) == false);
}

TEST(test_cert_check_expiry) {
    eb_certificate_t cert = {0};
    cert.not_before = 1000;
    cert.not_after = 2000;
    ASSERT(eb_cert_check_expiry(&cert, 1500) == EB_CERT_OK);
    ASSERT(eb_cert_check_expiry(&cert, 500) == EB_CERT_NOT_YET_VALID);
    ASSERT(eb_cert_check_expiry(&cert, 3000) == EB_CERT_EXPIRED);
}

TEST(test_cert_validate_empty_chain) {
    eb_cert_chain_t chain = {0};
    ASSERT(eb_cert_validate_chain(&chain, "test.com") == EB_CERT_UNTRUSTED_CA);
}

TEST(test_cert_validate_hostname_mismatch) {
    eb_cert_chain_t chain = {0};
    chain.cert_count = 2;
    strncpy(chain.certs[0].common_name, "other.com", 255);
    chain.certs[1].is_ca = true;
    ASSERT(eb_cert_validate_chain(&chain, "example.com") == EB_CERT_HOSTNAME_MISMATCH);
}

TEST(test_cert_validate_self_signed) {
    eb_cert_chain_t chain = {0};
    chain.cert_count = 1;
    strncpy(chain.certs[0].common_name, "example.com", 255);
    ASSERT(eb_cert_validate_chain(&chain, "example.com") == EB_CERT_SELF_SIGNED);
}

TEST(test_cert_status_strings) {
    ASSERT(strcmp(eb_cert_status_string(EB_CERT_OK), "Certificate valid") == 0);
    ASSERT(strcmp(eb_cert_status_string(EB_CERT_EXPIRED), "Certificate expired") == 0);
    ASSERT(strcmp(eb_cert_status_string(EB_CERT_HOSTNAME_MISMATCH), "Hostname mismatch") == 0);
    ASSERT(strcmp(eb_cert_status_string(EB_CERT_SELF_SIGNED), "Self-signed certificate") == 0);
}

TEST(test_session_save_load) {
    eb_tls_session_t session = {0};
    strncpy(session.hostname, "test.com", EB_TLS_MAX_HOSTNAME - 1);
    session.valid = true;
    session.master_secret[0] = 42;
    ASSERT(eb_tls_session_save(&session) == 0);
    eb_tls_session_t loaded;
    ASSERT(eb_tls_session_load("test.com", &loaded) == 0);
    ASSERT(loaded.master_secret[0] == 42);
}

TEST(test_session_invalidate) {
    eb_tls_session_t session = {0};
    strncpy(session.hostname, "invalidate.com", EB_TLS_MAX_HOSTNAME - 1);
    session.valid = true;
    eb_tls_session_save(&session);
    eb_tls_session_invalidate("invalidate.com");
    eb_tls_session_t loaded;
    ASSERT(eb_tls_session_load("invalidate.com", &loaded) != 0);
}

int main(void) {
    printf("=== TLS Tests ===\n");
    RUN(test_config_default); RUN(test_tls_init); RUN(test_tls_init_with_config);
    RUN(test_tls_set_hostname); RUN(test_tls_handshake); RUN(test_tls_close); RUN(test_tls_free);
    RUN(test_cert_hostname_exact); RUN(test_cert_hostname_wildcard); RUN(test_cert_hostname_null);
    RUN(test_cert_check_expiry); RUN(test_cert_validate_empty_chain);
    RUN(test_cert_validate_hostname_mismatch); RUN(test_cert_validate_self_signed);
    RUN(test_cert_status_strings); RUN(test_session_save_load); RUN(test_session_invalidate);
    printf("\nResults: %d passed, %d failed\n", s_pass, s_fail);
    return s_fail > 0 ? 1 : 0;
}
