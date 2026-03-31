// SPDX-License-Identifier: MIT
#ifndef EAPPS_HTTP_H
#define EAPPS_HTTP_H

#include <stddef.h>

typedef struct {
    int    status_code;
    char  *body;
    size_t body_len;
} eapps_http_response_t;

int  eapps_http_get(const char *url, eapps_http_response_t *resp);
int  eapps_http_post(const char *url, const char *body, size_t body_len, eapps_http_response_t *resp);
int  eapps_http_download(const char *url, const char *filepath);
void eapps_http_response_free(eapps_http_response_t *resp);

#endif /* EAPPS_HTTP_H */
