// SPDX-License-Identifier: MIT
#include "eBrowser/cookies.h"
#include "eBrowser/compat.h"
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <time.h>

void eb_cookie_jar_init(eb_cookie_jar_t *jar) { if (jar) memset(jar, 0, sizeof(eb_cookie_jar_t)); }

bool eb_cookie_jar_parse_set_cookie(eb_cookie_jar_t *jar, const char *header, const char *domain) {
    if (!jar || !header) return false;
    eb_cookie_t c; memset(&c, 0, sizeof(c));
    if (domain) strncpy(c.domain, domain, EB_COOKIE_MAX_DOMAIN - 1);
    strcpy(c.path, "/"); c.valid = true;
    const char *p = header;
    while (*p && isspace((unsigned char)*p)) p++;
    const char *eq = strchr(p, '=');
    if (!eq) return false;
    size_t nlen = (size_t)(eq - p); if (nlen >= EB_COOKIE_MAX_NAME) nlen = EB_COOKIE_MAX_NAME - 1;
    strncpy(c.name, p, nlen); p = eq + 1;
    const char *semi = strchr(p, ';');
    size_t vlen = semi ? (size_t)(semi - p) : strlen(p);
    if (vlen >= EB_COOKIE_MAX_VALUE) vlen = EB_COOKIE_MAX_VALUE - 1;
    strncpy(c.value, p, vlen);
    if (semi) p = semi + 1; else p += vlen;
    while (*p) {
        while (*p && (isspace((unsigned char)*p) || *p == ';')) p++;
        if (!*p) break;
        if (strncasecmp(p, "Secure", 6) == 0) { c.secure = true; p += 6; }
        else if (strncasecmp(p, "HttpOnly", 8) == 0) { c.http_only = true; p += 8; }
        else if (strncasecmp(p, "Path=", 5) == 0) { p += 5; const char *e = strchr(p, ';'); size_t l = e ? (size_t)(e-p) : strlen(p); if (l >= EB_COOKIE_MAX_PATH) l = EB_COOKIE_MAX_PATH-1; memset(c.path,0,sizeof(c.path)); strncpy(c.path, p, l); p += l; }
        else if (strncasecmp(p, "Domain=", 7) == 0) { p += 7; const char *e = strchr(p, ';'); size_t l = e ? (size_t)(e-p) : strlen(p); if (l >= EB_COOKIE_MAX_DOMAIN) l = EB_COOKIE_MAX_DOMAIN-1; strncpy(c.domain, p, l); p += l; }
        else if (strncasecmp(p, "Max-Age=", 8) == 0) { p += 8; c.expires = (int64_t)time(NULL) + atoi(p); while (*p && *p != ';') p++; }
        else if (strncasecmp(p, "SameSite=", 9) == 0) { p += 9; const char *e = strchr(p, ';'); size_t l = e ? (size_t)(e-p) : strlen(p); if (l > 15) l = 15; strncpy(c.same_site, p, l); p += l; }
        else { while (*p && *p != ';') p++; }
    }
    for (int i = 0; i < jar->count; i++) {
        if (jar->cookies[i].valid && strcmp(jar->cookies[i].name, c.name) == 0 && strcmp(jar->cookies[i].domain, c.domain) == 0) {
            jar->cookies[i] = c; return true;
        }
    }
    if (jar->count >= EB_COOKIE_JAR_SIZE) return false;
    jar->cookies[jar->count++] = c;
    return true;
}

int eb_cookie_jar_get_for_url(const eb_cookie_jar_t *jar, const char *url, bool is_https, char *out, size_t out_max) {
    if (!jar || !url || !out || out_max == 0) return 0;
    out[0] = '\0'; size_t pos = 0; int count = 0;
    int64_t now = (int64_t)time(NULL);
    for (int i = 0; i < jar->count; i++) {
        const eb_cookie_t *ck = &jar->cookies[i];
        if (!ck->valid) continue;
        if (ck->expires > 0 && now > ck->expires) continue;
        if (ck->secure && !is_https) continue;
        if (ck->domain[0] && !strstr(url, ck->domain)) continue;
        size_t needed = strlen(ck->name) + strlen(ck->value) + 3;
        if (pos + needed >= out_max) break;
        if (count > 0) { out[pos++] = ';'; out[pos++] = ' '; }
        pos += (size_t)snprintf(out + pos, out_max - pos, "%s=%s", ck->name, ck->value);
        count++;
    }
    return count;
}

bool eb_cookie_jar_set(eb_cookie_jar_t *jar, const char *name, const char *value, const char *domain, const char *path, int max_age) {
    if (!jar || !name || !value) return false;
    char header[1024];
    snprintf(header, sizeof(header), "%s=%s; Path=%s; Max-Age=%d", name, value, path ? path : "/", max_age);
    return eb_cookie_jar_parse_set_cookie(jar, header, domain);
}

bool eb_cookie_jar_remove(eb_cookie_jar_t *jar, const char *name, const char *domain) {
    if (!jar || !name) return false;
    for (int i = 0; i < jar->count; i++) {
        if (jar->cookies[i].valid && strcmp(jar->cookies[i].name, name) == 0 && (!domain || strcmp(jar->cookies[i].domain, domain) == 0)) {
            jar->cookies[i].valid = false; return true;
        }
    }
    return false;
}

void eb_cookie_jar_clear(eb_cookie_jar_t *jar) { if (jar) { memset(jar->cookies, 0, sizeof(jar->cookies)); jar->count = 0; } }

void eb_cookie_jar_purge_expired(eb_cookie_jar_t *jar) {
    if (!jar) return;
    int64_t now = (int64_t)time(NULL);
    for (int i = 0; i < jar->count; i++) if (jar->cookies[i].valid && jar->cookies[i].expires > 0 && now > jar->cookies[i].expires) jar->cookies[i].valid = false;
}

int eb_cookie_jar_count(const eb_cookie_jar_t *jar) {
    if (!jar) return 0;
    int c = 0; for (int i = 0; i < jar->count; i++) if (jar->cookies[i].valid) c++;
    return c;
}
