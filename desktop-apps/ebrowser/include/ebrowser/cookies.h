// SPDX-License-Identifier: MIT
#ifndef eBrowser_COOKIES_H
#define eBrowser_COOKIES_H

#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>

#define EB_COOKIE_MAX_NAME   128
#define EB_COOKIE_MAX_VALUE  512
#define EB_COOKIE_MAX_DOMAIN 256
#define EB_COOKIE_MAX_PATH   256
#define EB_COOKIE_JAR_SIZE   128

typedef struct {
    char    name[EB_COOKIE_MAX_NAME];
    char    value[EB_COOKIE_MAX_VALUE];
    char    domain[EB_COOKIE_MAX_DOMAIN];
    char    path[EB_COOKIE_MAX_PATH];
    bool    secure;
    bool    http_only;
    char    same_site[16];
    int64_t expires;
    bool    valid;
} eb_cookie_t;

typedef struct {
    eb_cookie_t cookies[EB_COOKIE_JAR_SIZE];
    int         count;
} eb_cookie_jar_t;

void          eb_cookie_jar_init(eb_cookie_jar_t *jar);
bool          eb_cookie_jar_parse_set_cookie(eb_cookie_jar_t *jar, const char *header, const char *domain);
int           eb_cookie_jar_get_for_url(const eb_cookie_jar_t *jar, const char *url, bool is_https, char *out, size_t out_max);
bool          eb_cookie_jar_set(eb_cookie_jar_t *jar, const char *name, const char *value, const char *domain, const char *path, int max_age);
bool          eb_cookie_jar_remove(eb_cookie_jar_t *jar, const char *name, const char *domain);
void          eb_cookie_jar_clear(eb_cookie_jar_t *jar);
void          eb_cookie_jar_purge_expired(eb_cookie_jar_t *jar);
int           eb_cookie_jar_count(const eb_cookie_jar_t *jar);

#endif
