// SPDX-License-Identifier: MIT
#ifndef eBrowser_SECURITY_H
#define eBrowser_SECURITY_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#define EB_CSP_MAX_DIRECTIVES    16
#define EB_CSP_MAX_SOURCES       32
#define EB_CSP_MAX_VALUE         512
#define EB_SECURITY_MAX_ORIGINS  16

// --- Content Security Policy ---

typedef enum {
    EB_CSP_DEFAULT_SRC,
    EB_CSP_SCRIPT_SRC,
    EB_CSP_STYLE_SRC,
    EB_CSP_IMG_SRC,
    EB_CSP_FONT_SRC,
    EB_CSP_CONNECT_SRC,
    EB_CSP_MEDIA_SRC,
    EB_CSP_FRAME_SRC,
    EB_CSP_OBJECT_SRC,
    EB_CSP_BASE_URI,
    EB_CSP_FORM_ACTION
} eb_csp_directive_t;

typedef struct {
    eb_csp_directive_t directive;
    char               sources[EB_CSP_MAX_SOURCES][EB_CSP_MAX_VALUE];
    int                source_count;
} eb_csp_rule_t;

typedef struct {
    eb_csp_rule_t rules[EB_CSP_MAX_DIRECTIVES];
    int           rule_count;
    bool          block_inline_scripts;
    bool          block_eval;
    bool          upgrade_insecure;
} eb_csp_policy_t;

void eb_csp_init(eb_csp_policy_t *policy);
bool eb_csp_parse(eb_csp_policy_t *policy, const char *header);
bool eb_csp_allows_source(const eb_csp_policy_t *policy, eb_csp_directive_t directive,
                           const char *source_url);
bool eb_csp_allows_inline(const eb_csp_policy_t *policy);
bool eb_csp_allows_eval(const eb_csp_policy_t *policy);

// --- XSS Prevention ---

typedef enum {
    EB_XSS_NONE    = 0,
    EB_XSS_SCRIPT  = (1 << 0),
    EB_XSS_EVENT   = (1 << 1),
    EB_XSS_IFRAME  = (1 << 2),
    EB_XSS_OBJECT  = (1 << 3),
    EB_XSS_DATA_URI = (1 << 4),
    EB_XSS_JS_URI  = (1 << 5),
    EB_XSS_SVG     = (1 << 6)
} eb_xss_threat_t;

int  eb_xss_scan_html(const char *html, size_t len);
bool eb_xss_is_safe_attribute(const char *attr_name, const char *attr_value);
bool eb_xss_is_safe_url(const char *url);
int  eb_xss_sanitize_html(const char *input, size_t in_len, char *output, size_t out_max);
int  eb_xss_escape_html(const char *input, char *output, size_t out_max);

// --- URL Security ---

typedef enum {
    EB_URL_SAFE,
    EB_URL_SUSPICIOUS,
    EB_URL_BLOCKED_JAVASCRIPT,
    EB_URL_BLOCKED_DATA,
    EB_URL_BLOCKED_PHISHING,
    EB_URL_MIXED_CONTENT
} eb_url_safety_t;

eb_url_safety_t eb_security_check_url(const char *url);
bool            eb_security_is_mixed_content(const char *page_url, const char *resource_url);
bool            eb_security_is_secure_origin(const char *url);

// --- CORS ---

typedef struct {
    char allowed_origins[EB_SECURITY_MAX_ORIGINS][256];
    int  origin_count;
    bool allow_credentials;
    bool allow_all_origins;
} eb_cors_policy_t;

void eb_cors_init(eb_cors_policy_t *policy);
bool eb_cors_parse_header(eb_cors_policy_t *policy, const char *header);
bool eb_cors_is_allowed(const eb_cors_policy_t *policy, const char *origin);

// --- HTTP Security Headers ---

typedef struct {
    bool   hsts_enabled;
    int    hsts_max_age;
    bool   hsts_include_subdomains;
    bool   x_content_type_nosniff;
    bool   x_frame_deny;
    char   x_frame_allow_from[256];
    bool   x_xss_protection;
    char   referrer_policy[64];
} eb_security_headers_t;

void eb_security_headers_init(eb_security_headers_t *headers);
void eb_security_headers_parse(eb_security_headers_t *headers,
                                const char *name, const char *value);
bool eb_security_should_upgrade_to_https(const eb_security_headers_t *headers);

// --- Cookie Security ---

typedef struct {
    char  name[128];
    char  value[512];
    char  domain[256];
    char  path[256];
    bool  secure;
    bool  http_only;
    char  same_site[16];
    int64_t expires;
} eb_secure_cookie_t;

bool eb_cookie_parse(eb_secure_cookie_t *cookie, const char *set_cookie_header);
bool eb_cookie_is_secure(const eb_secure_cookie_t *cookie);
bool eb_cookie_matches_domain(const eb_secure_cookie_t *cookie, const char *domain);
bool eb_cookie_should_send(const eb_secure_cookie_t *cookie, const char *url, bool is_https);

#endif /* eBrowser_SECURITY_H */
