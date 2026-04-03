// SPDX-License-Identifier: MIT
#include "eBrowser/security.h"
#include "eBrowser/compat.h"
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <stdio.h>

// --- CSP ---

void eb_csp_init(eb_csp_policy_t *policy) {
    if (!policy) return;
    memset(policy, 0, sizeof(eb_csp_policy_t));
    policy->block_inline_scripts = true;
    policy->block_eval = true;
}

static eb_csp_directive_t parse_directive_name(const char *name) {
    if (!name) return EB_CSP_DEFAULT_SRC;
    if (strncmp(name, "default-src", 11) == 0) return EB_CSP_DEFAULT_SRC;
    if (strncmp(name, "script-src", 10) == 0) return EB_CSP_SCRIPT_SRC;
    if (strncmp(name, "style-src", 9) == 0) return EB_CSP_STYLE_SRC;
    if (strncmp(name, "img-src", 7) == 0) return EB_CSP_IMG_SRC;
    if (strncmp(name, "font-src", 8) == 0) return EB_CSP_FONT_SRC;
    if (strncmp(name, "connect-src", 11) == 0) return EB_CSP_CONNECT_SRC;
    if (strncmp(name, "frame-src", 9) == 0) return EB_CSP_FRAME_SRC;
    if (strncmp(name, "object-src", 10) == 0) return EB_CSP_OBJECT_SRC;
    return EB_CSP_DEFAULT_SRC;
}

bool eb_csp_parse(eb_csp_policy_t *policy, const char *header) {
    if (!policy || !header) return false;
    const char *p = header;
    while (*p && policy->rule_count < EB_CSP_MAX_DIRECTIVES) {
        while (*p && isspace((unsigned char)*p)) p++;
        if (!*p) break;
        const char *dir_start = p;
        while (*p && *p != ' ' && *p != ';') p++;
        size_t dir_len = (size_t)(p - dir_start);
        eb_csp_rule_t *rule = &policy->rules[policy->rule_count];
        char dir_name[64] = {0};
        if (dir_len >= sizeof(dir_name)) dir_len = sizeof(dir_name) - 1;
        memcpy(dir_name, dir_start, dir_len);
        rule->directive = parse_directive_name(dir_name);
        while (*p && *p != ';') {
            while (*p && isspace((unsigned char)*p)) p++;
            if (!*p || *p == ';') break;
            const char *src_start = p;
            while (*p && *p != ' ' && *p != ';') p++;
            size_t src_len = (size_t)(p - src_start);
            if (rule->source_count < EB_CSP_MAX_SOURCES && src_len < EB_CSP_MAX_VALUE) {
                memcpy(rule->sources[rule->source_count], src_start, src_len);
                if (strncmp(rule->sources[rule->source_count], "'unsafe-inline'", 15) == 0)
                    policy->block_inline_scripts = false;
                if (strncmp(rule->sources[rule->source_count], "'unsafe-eval'", 13) == 0)
                    policy->block_eval = false;
                if (strncmp(rule->sources[rule->source_count], "upgrade-insecure-requests", 25) == 0)
                    policy->upgrade_insecure = true;
                rule->source_count++;
            }
        }
        policy->rule_count++;
        if (*p == ';') p++;
    }
    return true;
}

bool eb_csp_allows_source(const eb_csp_policy_t *policy, eb_csp_directive_t directive,
                           const char *source_url) {
    if (!policy || !source_url) return false;
    for (int i = 0; i < policy->rule_count; i++) {
        if (policy->rules[i].directive == directive) {
            for (int j = 0; j < policy->rules[i].source_count; j++) {
                const char *src = policy->rules[i].sources[j];
                if (strcmp(src, "'self'") == 0) return true;
                if (strcmp(src, "*") == 0) return true;
                if (strstr(source_url, src) != NULL) return true;
            }
            return false;
        }
    }
    for (int i = 0; i < policy->rule_count; i++) {
        if (policy->rules[i].directive == EB_CSP_DEFAULT_SRC) {
            for (int j = 0; j < policy->rules[i].source_count; j++) {
                if (strcmp(policy->rules[i].sources[j], "'self'") == 0) return true;
                if (strcmp(policy->rules[i].sources[j], "*") == 0) return true;
            }
            return false;
        }
    }
    return true;
}

bool eb_csp_allows_inline(const eb_csp_policy_t *policy) {
    return policy ? !policy->block_inline_scripts : true;
}

bool eb_csp_allows_eval(const eb_csp_policy_t *policy) {
    return policy ? !policy->block_eval : true;
}

// --- XSS Prevention ---

static bool ci_strstr(const char *haystack, const char *needle) {
    if (!haystack || !needle) return false;
    size_t hlen = strlen(haystack), nlen = strlen(needle);
    if (nlen > hlen) return false;
    for (size_t i = 0; i <= hlen - nlen; i++) {
        bool match = true;
        for (size_t j = 0; j < nlen; j++) {
            if (tolower((unsigned char)haystack[i+j]) != tolower((unsigned char)needle[j])) {
                match = false; break;
            }
        }
        if (match) return true;
    }
    return false;
}

int eb_xss_scan_html(const char *html, size_t len) {
    if (!html || len == 0) return EB_XSS_NONE;
    int threats = EB_XSS_NONE;
    if (ci_strstr(html, "<script")) threats |= EB_XSS_SCRIPT;
    if (ci_strstr(html, "onerror=") || ci_strstr(html, "onclick=") ||
        ci_strstr(html, "onload=") || ci_strstr(html, "onmouseover="))
        threats |= EB_XSS_EVENT;
    if (ci_strstr(html, "<iframe")) threats |= EB_XSS_IFRAME;
    if (ci_strstr(html, "<object") || ci_strstr(html, "<embed")) threats |= EB_XSS_OBJECT;
    if (ci_strstr(html, "data:text/html") || ci_strstr(html, "data:application"))
        threats |= EB_XSS_DATA_URI;
    if (ci_strstr(html, "javascript:")) threats |= EB_XSS_JS_URI;
    if (ci_strstr(html, "<svg") && ci_strstr(html, "onload")) threats |= EB_XSS_SVG;
    return threats;
}

bool eb_xss_is_safe_attribute(const char *attr_name, const char *attr_value) {
    if (!attr_name) return false;
    const char *dangerous[] = {"onclick","onerror","onload","onmouseover","onfocus",
                                "onblur","onsubmit","onchange","onkeydown","onkeyup",NULL};
    for (int i = 0; dangerous[i]; i++) {
        if (strcasecmp(attr_name, dangerous[i]) == 0) return false;
    }
    if (attr_value) {
        if (ci_strstr(attr_value, "javascript:")) return false;
        if (ci_strstr(attr_value, "data:text/html")) return false;
        if (ci_strstr(attr_value, "vbscript:")) return false;
    }
    return true;
}

bool eb_xss_is_safe_url(const char *url) {
    if (!url) return false;
    while (isspace((unsigned char)*url)) url++;
    if (strncasecmp(url, "javascript:", 11) == 0) return false;
    if (strncasecmp(url, "vbscript:", 9) == 0) return false;
    if (strncasecmp(url, "data:text/html", 14) == 0) return false;
    return true;
}

int eb_xss_escape_html(const char *input, char *output, size_t out_max) {
    if (!input || !output || out_max == 0) return -1;
    size_t j = 0;
    for (size_t i = 0; input[i] && j < out_max - 6; i++) {
        switch (input[i]) {
            case '<':  memcpy(output+j, "&lt;", 4); j += 4; break;
            case '>':  memcpy(output+j, "&gt;", 4); j += 4; break;
            case '&':  memcpy(output+j, "&amp;", 5); j += 5; break;
            case '"':  memcpy(output+j, "&quot;", 6); j += 6; break;
            case '\'': memcpy(output+j, "&#39;", 5); j += 5; break;
            default:   output[j++] = input[i]; break;
        }
    }
    output[j] = '\0';
    return (int)j;
}

int eb_xss_sanitize_html(const char *input, size_t in_len, char *output, size_t out_max) {
    if (!input || !output || out_max == 0) return -1;
    size_t j = 0;
    size_t i = 0;
    while (i < in_len && j < out_max - 1) {
        if (input[i] == '<') {
            if (ci_strstr(input + i, "<script") || ci_strstr(input + i, "<iframe") ||
                ci_strstr(input + i, "<object") || ci_strstr(input + i, "<embed")) {
                while (i < in_len && input[i] != '>') i++;
                if (i < in_len) i++;
                continue;
            }
        }
        output[j++] = input[i++];
    }
    output[j] = '\0';
    return (int)j;
}

// --- URL Security ---

eb_url_safety_t eb_security_check_url(const char *url) {
    if (!url) return EB_URL_SUSPICIOUS;
    while (isspace((unsigned char)*url)) url++;
    if (strncasecmp(url, "javascript:", 11) == 0) return EB_URL_BLOCKED_JAVASCRIPT;
    if (strncasecmp(url, "data:", 5) == 0) return EB_URL_BLOCKED_DATA;
    if (strncasecmp(url, "vbscript:", 9) == 0) return EB_URL_BLOCKED_JAVASCRIPT;
    return EB_URL_SAFE;
}

bool eb_security_is_mixed_content(const char *page_url, const char *resource_url) {
    if (!page_url || !resource_url) return false;
    bool page_https = (strncasecmp(page_url, "https://", 8) == 0);
    bool res_http = (strncasecmp(resource_url, "http://", 7) == 0);
    return page_https && res_http;
}

bool eb_security_is_secure_origin(const char *url) {
    if (!url) return false;
    if (strncasecmp(url, "https://", 8) == 0) return true;
    if (strncasecmp(url, "http://localhost", 16) == 0) return true;
    if (strncasecmp(url, "http://127.0.0.1", 16) == 0) return true;
    if (strncasecmp(url, "file://", 7) == 0) return true;
    return false;
}

// --- CORS ---

void eb_cors_init(eb_cors_policy_t *policy) {
    if (!policy) return;
    memset(policy, 0, sizeof(eb_cors_policy_t));
}

bool eb_cors_parse_header(eb_cors_policy_t *policy, const char *header) {
    if (!policy || !header) return false;
    if (strcmp(header, "*") == 0) {
        policy->allow_all_origins = true;
        return true;
    }
    if (policy->origin_count < EB_SECURITY_MAX_ORIGINS) {
        strncpy(policy->allowed_origins[policy->origin_count], header, 255);
        policy->origin_count++;
    }
    return true;
}

bool eb_cors_is_allowed(const eb_cors_policy_t *policy, const char *origin) {
    if (!policy || !origin) return false;
    if (policy->allow_all_origins) return true;
    for (int i = 0; i < policy->origin_count; i++) {
        if (strcmp(policy->allowed_origins[i], origin) == 0) return true;
    }
    return false;
}

// --- HTTP Security Headers ---

void eb_security_headers_init(eb_security_headers_t *headers) {
    if (!headers) return;
    memset(headers, 0, sizeof(eb_security_headers_t));
}

void eb_security_headers_parse(eb_security_headers_t *headers,
                                const char *name, const char *value) {
    if (!headers || !name || !value) return;
    if (strcasecmp(name, "Strict-Transport-Security") == 0) {
        headers->hsts_enabled = true;
        const char *ma = strstr(value, "max-age=");
        if (ma) headers->hsts_max_age = atoi(ma + 8);
        headers->hsts_include_subdomains = (strstr(value, "includeSubDomains") != NULL);
    }
    else if (strcasecmp(name, "X-Content-Type-Options") == 0) {
        headers->x_content_type_nosniff = (strcasecmp(value, "nosniff") == 0);
    }
    else if (strcasecmp(name, "X-Frame-Options") == 0) {
        headers->x_frame_deny = (strcasecmp(value, "DENY") == 0);
        const char *af = strstr(value, "ALLOW-FROM");
        if (af) strncpy(headers->x_frame_allow_from, af + 11, 255);
    }
    else if (strcasecmp(name, "X-XSS-Protection") == 0) {
        headers->x_xss_protection = (value[0] == '1');
    }
    else if (strcasecmp(name, "Referrer-Policy") == 0) {
        strncpy(headers->referrer_policy, value, 63);
    }
}

bool eb_security_should_upgrade_to_https(const eb_security_headers_t *headers) {
    return headers ? headers->hsts_enabled : false;
}

// --- Cookie Security ---

bool eb_cookie_parse(eb_secure_cookie_t *cookie, const char *set_cookie_header) {
    if (!cookie || !set_cookie_header) return false;
    memset(cookie, 0, sizeof(eb_secure_cookie_t));
    const char *eq = strchr(set_cookie_header, '=');
    if (!eq) return false;
    size_t name_len = (size_t)(eq - set_cookie_header);
    if (name_len >= sizeof(cookie->name)) name_len = sizeof(cookie->name) - 1;
    memcpy(cookie->name, set_cookie_header, name_len);
    eq++;
    const char *semi = strchr(eq, ';');
    size_t val_len = semi ? (size_t)(semi - eq) : strlen(eq);
    if (val_len >= sizeof(cookie->value)) val_len = sizeof(cookie->value) - 1;
    memcpy(cookie->value, eq, val_len);
    cookie->secure = (ci_strstr(set_cookie_header, "Secure") != false);
    cookie->http_only = (ci_strstr(set_cookie_header, "HttpOnly") != false);
    const char *ss = strstr(set_cookie_header, "SameSite=");
    if (ss) {
        ss += 9;
        const char *end = strchr(ss, ';');
        size_t sslen = end ? (size_t)(end - ss) : strlen(ss);
        if (sslen >= sizeof(cookie->same_site)) sslen = sizeof(cookie->same_site) - 1;
        memcpy(cookie->same_site, ss, sslen);
    } else {
        strncpy(cookie->same_site, "Lax", sizeof(cookie->same_site) - 1);
    }
    return true;
}

bool eb_cookie_is_secure(const eb_secure_cookie_t *cookie) {
    return cookie ? cookie->secure : false;
}

bool eb_cookie_matches_domain(const eb_secure_cookie_t *cookie, const char *domain) {
    if (!cookie || !domain) return false;
    if (cookie->domain[0] == '\0') return true;
    if (strcasecmp(cookie->domain, domain) == 0) return true;
    size_t dlen = strlen(domain), clen = strlen(cookie->domain);
    if (dlen > clen && strcasecmp(domain + dlen - clen, cookie->domain) == 0)
        return true;
    return false;
}

bool eb_cookie_should_send(const eb_secure_cookie_t *cookie, const char *url, bool is_https) {
    if (!cookie || !url) return false;
    if (cookie->secure && !is_https) return false;
    return true;
}
