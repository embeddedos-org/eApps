// SPDX-License-Identifier: MIT
#include "eBrowser/url.h"
#include "eBrowser/compat.h"
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <stdio.h>

int eb_url_default_port(const char *scheme) {
    if (!scheme) return 80;
    if (strcasecmp(scheme, "https") == 0) return 443;
    if (strcasecmp(scheme, "http") == 0) return 80;
    if (strcasecmp(scheme, "ftp") == 0) return 21;
    return 80;
}

bool eb_url_parse(const char *url_str, eb_url_t *out) {
    if (!url_str || !out) return false;
    memset(out, 0, sizeof(eb_url_t));

    const char *p = url_str;

    const char *scheme_end = strstr(p, "://");
    if (scheme_end) {
        size_t slen = (size_t)(scheme_end - p);
        if (slen >= EB_URL_MAX_SCHEME) slen = EB_URL_MAX_SCHEME - 1;
        for (size_t i = 0; i < slen; i++)
            out->scheme[i] = (char)tolower((unsigned char)p[i]);
        p = scheme_end + 3;
    } else {
        strncpy(out->scheme, "http", EB_URL_MAX_SCHEME - 1);
    }

    out->port = eb_url_default_port(out->scheme);

    const char *host_end = p;
    while (*host_end && *host_end != '/' && *host_end != ':' && *host_end != '?' && *host_end != '#')
        host_end++;

    size_t hlen = (size_t)(host_end - p);
    if (hlen >= EB_URL_MAX_HOST) hlen = EB_URL_MAX_HOST - 1;
    strncpy(out->host, p, hlen);
    p = host_end;

    if (*p == ':') {
        p++;
        out->port = atoi(p);
        while (*p && isdigit((unsigned char)*p)) p++;
    }

    if (*p == '/') {
        const char *path_end = p;
        while (*path_end && *path_end != '?' && *path_end != '#') path_end++;
        size_t plen = (size_t)(path_end - p);
        if (plen >= EB_URL_MAX_PATH) plen = EB_URL_MAX_PATH - 1;
        strncpy(out->path, p, plen);
        p = path_end;
    } else {
        strncpy(out->path, "/", EB_URL_MAX_PATH - 1);
    }

    if (*p == '?') {
        p++;
        const char *qend = p;
        while (*qend && *qend != '#') qend++;
        size_t qlen = (size_t)(qend - p);
        if (qlen >= EB_URL_MAX_QUERY) qlen = EB_URL_MAX_QUERY - 1;
        strncpy(out->query, p, qlen);
        p = qend;
    }

    if (*p == '#') {
        p++;
        strncpy(out->fragment, p, EB_URL_MAX_FRAGMENT - 1);
    }

    return out->host[0] != '\0';
}

void eb_url_to_string(const eb_url_t *url, char *buf, size_t buf_len) {
    if (!url || !buf || buf_len == 0) return;
    int port_default = eb_url_default_port(url->scheme);
    if (url->port != port_default && url->port > 0) {
        snprintf(buf, buf_len, "%s://%s:%d%s%s%s%s%s",
                 url->scheme, url->host, url->port, url->path,
                 url->query[0] ? "?" : "", url->query,
                 url->fragment[0] ? "#" : "", url->fragment);
    } else {
        snprintf(buf, buf_len, "%s://%s%s%s%s%s%s",
                 url->scheme, url->host, url->path,
                 url->query[0] ? "?" : "", url->query,
                 url->fragment[0] ? "#" : "", url->fragment);
    }
}

bool eb_url_resolve(const eb_url_t *base, const char *relative, eb_url_t *out) {
    if (!base || !relative || !out) return false;

    if (strstr(relative, "://")) return eb_url_parse(relative, out);

    *out = *base;
    out->query[0] = '\0';
    out->fragment[0] = '\0';

    if (relative[0] == '/') {
        strncpy(out->path, relative, EB_URL_MAX_PATH - 1);
    } else {
        char *last_slash = strrchr(out->path, '/');
        if (last_slash) *(last_slash + 1) = '\0';
        size_t plen = strlen(out->path);
        strncat(out->path, relative, EB_URL_MAX_PATH - 1 - plen);
    }
    return true;
}
