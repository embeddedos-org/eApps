// SPDX-License-Identifier: MIT
#include "eapps/http.h"

int eapps_http_get(const char *url, eapps_http_response_t *resp) {
    (void)url; (void)resp;
    return -1; /* TODO: WinHTTP implementation */
}

int eapps_http_post(const char *url, const char *body, size_t body_len, eapps_http_response_t *resp) {
    (void)url; (void)body; (void)body_len; (void)resp;
    return -1;
}

int eapps_http_download(const char *url, const char *filepath) {
    (void)url; (void)filepath;
    return -1;
}
