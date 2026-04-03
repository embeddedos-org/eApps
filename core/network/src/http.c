// SPDX-License-Identifier: MIT
#include "eapps/http.h"
#include <stdlib.h>
#include <string.h>

void eapps_http_response_free(eapps_http_response_t *resp) {
    if (resp && resp->body) { free(resp->body); resp->body = NULL; resp->body_len = 0; }
}
