// SPDX-License-Identifier: MIT
// Security module tests for eBrowser web browser
#include "eBrowser/security.h"
#include <stdio.h>
#include <string.h>

static int s_pass = 0, s_fail = 0;
#define TEST(name) static void name(void)
#define RUN(name) do { printf("  %s... ", #name); name(); printf("PASS\n"); s_pass++; } while(0)
#define ASSERT(cond) do { if(!(cond)) { printf("FAIL: %s:%d: %s\n", __FILE__, __LINE__, #cond); s_fail++; return; } } while(0)

// --- XSS ---
TEST(test_xss_detect_script) {
    int t = eb_xss_scan_html("<script>alert('xss')</script>", 29);
    ASSERT(t & EB_XSS_SCRIPT);
}
TEST(test_xss_detect_event_handler) {
    int t = eb_xss_scan_html("<img onerror=alert(1)>", 22);
    ASSERT(t & EB_XSS_EVENT);
}
TEST(test_xss_detect_iframe) {
    int t = eb_xss_scan_html("<iframe src=evil.com>", 21);
    ASSERT(t & EB_XSS_IFRAME);
}
TEST(test_xss_detect_javascript_uri) {
    int t = eb_xss_scan_html("<a href=\"javascript:alert(1)\">", 30);
    ASSERT(t & EB_XSS_JS_URI);
}
TEST(test_xss_detect_data_uri) {
    int t = eb_xss_scan_html("<a href=\"data:text/html,<script>alert(1)</script>\">", 51);
    ASSERT(t & EB_XSS_DATA_URI);
}
TEST(test_xss_safe_html) {
    int t = eb_xss_scan_html("<p>Hello world</p>", 18);
    ASSERT(t == EB_XSS_NONE);
}
TEST(test_xss_case_insensitive) {
    int t = eb_xss_scan_html("<SCRIPT>alert(1)</SCRIPT>", 25);
    ASSERT(t & EB_XSS_SCRIPT);
}
TEST(test_safe_attribute) {
    ASSERT(eb_xss_is_safe_attribute("href", "https://example.com") == true);
    ASSERT(eb_xss_is_safe_attribute("class", "btn") == true);
    ASSERT(eb_xss_is_safe_attribute("id", "main") == true);
}
TEST(test_unsafe_attribute) {
    ASSERT(eb_xss_is_safe_attribute("onclick", "alert(1)") == false);
    ASSERT(eb_xss_is_safe_attribute("onerror", "hack()") == false);
    ASSERT(eb_xss_is_safe_attribute("onload", "steal()") == false);
}
TEST(test_unsafe_attribute_value) {
    ASSERT(eb_xss_is_safe_attribute("href", "javascript:alert(1)") == false);
    ASSERT(eb_xss_is_safe_attribute("src", "data:text/html,<script>x</script>") == false);
}
TEST(test_safe_url) {
    ASSERT(eb_xss_is_safe_url("https://example.com") == true);
    ASSERT(eb_xss_is_safe_url("http://test.org/page") == true);
    ASSERT(eb_xss_is_safe_url("/relative/path") == true);
}
TEST(test_unsafe_url) {
    ASSERT(eb_xss_is_safe_url("javascript:alert(1)") == false);
    ASSERT(eb_xss_is_safe_url("vbscript:run") == false);
    ASSERT(eb_xss_is_safe_url("data:text/html,evil") == false);
    ASSERT(eb_xss_is_safe_url(NULL) == false);
}
TEST(test_html_escape) {
    char out[128];
    eb_xss_escape_html("<script>alert('xss')</script>", out, sizeof(out));
    ASSERT(strstr(out, "&lt;script&gt;") != NULL);
    ASSERT(strstr(out, "<script>") == NULL);
}

// --- URL Security ---
TEST(test_url_safe) { ASSERT(eb_security_check_url("https://example.com") == EB_URL_SAFE); }
TEST(test_url_javascript_blocked) { ASSERT(eb_security_check_url("javascript:alert(1)") == EB_URL_BLOCKED_JAVASCRIPT); }
TEST(test_url_data_blocked) { ASSERT(eb_security_check_url("data:text/html,hi") == EB_URL_BLOCKED_DATA); }
TEST(test_url_null) { ASSERT(eb_security_check_url(NULL) == EB_URL_SUSPICIOUS); }
TEST(test_mixed_content_detected) {
    ASSERT(eb_security_is_mixed_content("https://secure.com", "http://insecure.com/img.png") == true);
}
TEST(test_mixed_content_ok) {
    ASSERT(eb_security_is_mixed_content("https://secure.com", "https://cdn.com/img.png") == false);
    ASSERT(eb_security_is_mixed_content("http://page.com", "http://other.com/img.png") == false);
}
TEST(test_secure_origin) {
    ASSERT(eb_security_is_secure_origin("https://example.com") == true);
    ASSERT(eb_security_is_secure_origin("http://localhost") == true);
    ASSERT(eb_security_is_secure_origin("http://127.0.0.1") == true);
    ASSERT(eb_security_is_secure_origin("file:///home/user") == true);
    ASSERT(eb_security_is_secure_origin("http://evil.com") == false);
}

// --- CORS ---
TEST(test_cors_wildcard) {
    eb_cors_policy_t policy;
    eb_cors_init(&policy);
    eb_cors_parse_header(&policy, "*");
    ASSERT(eb_cors_is_allowed(&policy, "https://any.com") == true);
}
TEST(test_cors_specific) {
    eb_cors_policy_t policy;
    eb_cors_init(&policy);
    eb_cors_parse_header(&policy, "https://allowed.com");
    ASSERT(eb_cors_is_allowed(&policy, "https://allowed.com") == true);
    ASSERT(eb_cors_is_allowed(&policy, "https://blocked.com") == false);
}

// --- Security Headers ---
TEST(test_hsts) {
    eb_security_headers_t h;
    eb_security_headers_init(&h);
    eb_security_headers_parse(&h, "Strict-Transport-Security", "max-age=31536000; includeSubDomains");
    ASSERT(h.hsts_enabled == true);
    ASSERT(h.hsts_max_age == 31536000);
    ASSERT(h.hsts_include_subdomains == true);
    ASSERT(eb_security_should_upgrade_to_https(&h) == true);
}
TEST(test_nosniff) {
    eb_security_headers_t h;
    eb_security_headers_init(&h);
    eb_security_headers_parse(&h, "X-Content-Type-Options", "nosniff");
    ASSERT(h.x_content_type_nosniff == true);
}
TEST(test_x_frame_deny) {
    eb_security_headers_t h;
    eb_security_headers_init(&h);
    eb_security_headers_parse(&h, "X-Frame-Options", "DENY");
    ASSERT(h.x_frame_deny == true);
}
TEST(test_xss_protection_header) {
    eb_security_headers_t h;
    eb_security_headers_init(&h);
    eb_security_headers_parse(&h, "X-XSS-Protection", "1; mode=block");
    ASSERT(h.x_xss_protection == true);
}

// --- Cookies ---
TEST(test_cookie_parse) {
    eb_secure_cookie_t c;
    ASSERT(eb_cookie_parse(&c, "session=abc123; Secure; HttpOnly; SameSite=Strict"));
    ASSERT(strcmp(c.name, "session") == 0);
    ASSERT(strcmp(c.value, "abc123") == 0);
    ASSERT(c.secure == true);
    ASSERT(c.http_only == true);
    ASSERT(strcmp(c.same_site, "Strict") == 0);
}
TEST(test_cookie_secure_check) {
    eb_secure_cookie_t c;
    eb_cookie_parse(&c, "token=xyz; Secure");
    ASSERT(eb_cookie_is_secure(&c) == true);
    ASSERT(eb_cookie_should_send(&c, "https://example.com", true) == true);
    ASSERT(eb_cookie_should_send(&c, "http://example.com", false) == false);
}
TEST(test_cookie_not_secure) {
    eb_secure_cookie_t c;
    eb_cookie_parse(&c, "pref=dark");
    ASSERT(eb_cookie_should_send(&c, "http://example.com", false) == true);
}

// --- CSP ---
TEST(test_csp_init) {
    eb_csp_policy_t p;
    eb_csp_init(&p);
    ASSERT(p.block_inline_scripts == true);
    ASSERT(p.block_eval == true);
    ASSERT(eb_csp_allows_inline(&p) == false);
    ASSERT(eb_csp_allows_eval(&p) == false);
}

int main(void) {
    printf("=== Security Tests ===\n");
    RUN(test_xss_detect_script); RUN(test_xss_detect_event_handler);
    RUN(test_xss_detect_iframe); RUN(test_xss_detect_javascript_uri);
    RUN(test_xss_detect_data_uri); RUN(test_xss_safe_html);
    RUN(test_xss_case_insensitive);
    RUN(test_safe_attribute); RUN(test_unsafe_attribute); RUN(test_unsafe_attribute_value);
    RUN(test_safe_url); RUN(test_unsafe_url); RUN(test_html_escape);
    RUN(test_url_safe); RUN(test_url_javascript_blocked); RUN(test_url_data_blocked); RUN(test_url_null);
    RUN(test_mixed_content_detected); RUN(test_mixed_content_ok); RUN(test_secure_origin);
    RUN(test_cors_wildcard); RUN(test_cors_specific);
    RUN(test_hsts); RUN(test_nosniff); RUN(test_x_frame_deny); RUN(test_xss_protection_header);
    RUN(test_cookie_parse); RUN(test_cookie_secure_check); RUN(test_cookie_not_secure);
    RUN(test_csp_init);
    printf("\nResults: %d passed, %d failed\n", s_pass, s_fail);
    return s_fail > 0 ? 1 : 0;
}
