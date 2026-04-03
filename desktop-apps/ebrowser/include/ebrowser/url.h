// SPDX-License-Identifier: MIT
#ifndef eBrowser_URL_H
#define eBrowser_URL_H

#include <stdbool.h>
#include <stddef.h>

#define EB_URL_MAX_SCHEME   16
#define EB_URL_MAX_HOST     256
#define EB_URL_MAX_PATH     1024
#define EB_URL_MAX_QUERY    1024
#define EB_URL_MAX_FRAGMENT 256
#define EB_URL_MAX_FULL     2048

typedef struct {
    char  scheme[EB_URL_MAX_SCHEME];
    char  host[EB_URL_MAX_HOST];
    int   port;
    char  path[EB_URL_MAX_PATH];
    char  query[EB_URL_MAX_QUERY];
    char  fragment[EB_URL_MAX_FRAGMENT];
} eb_url_t;

bool eb_url_parse(const char *url_str, eb_url_t *out);
void eb_url_to_string(const eb_url_t *url, char *buf, size_t buf_len);
bool eb_url_resolve(const eb_url_t *base, const char *relative, eb_url_t *out);
int  eb_url_default_port(const char *scheme);

#endif /* eBrowser_URL_H */
