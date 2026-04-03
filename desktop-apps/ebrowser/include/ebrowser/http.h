// SPDX-License-Identifier: MIT
#ifndef eBrowser_HTTP_H
#define eBrowser_HTTP_H

#include <stddef.h>

typedef struct {
    int    status_code;
    char  *body;
    size_t body_len;
    char  *content_type;
    char  *headers;
} eb_http_response_t;

int  eb_http_get(const char *url, eb_http_response_t *resp);
int  eb_http_post(const char *url, const char *body, size_t body_len, eb_http_response_t *resp);
void eb_http_response_free(eb_http_response_t *resp);

#endif /* eBrowser_HTTP_H */
