// SPDX-License-Identifier: MIT
#include "eBrowser/input.h"
#include <string.h>

#define EB_INPUT_MAX_CALLBACKS 8

static struct {
    eb_input_callback_t cb;
    void *user_data;
} s_callbacks[EB_INPUT_MAX_CALLBACKS];
static int s_callback_count = 0;

void eb_input_init(void) {
    s_callback_count = 0;
    memset(s_callbacks, 0, sizeof(s_callbacks));
}

void eb_input_deinit(void) {
    s_callback_count = 0;
}

void eb_input_register_callback(eb_input_callback_t cb, void *user_data) {
    if (!cb || s_callback_count >= EB_INPUT_MAX_CALLBACKS) return;
    s_callbacks[s_callback_count].cb = cb;
    s_callbacks[s_callback_count].user_data = user_data;
    s_callback_count++;
}

void eb_input_process(const eb_input_event_t *event) {
    if (!event) return;
    for (int i = 0; i < s_callback_count; i++) {
        if (s_callbacks[i].cb) {
            s_callbacks[i].cb(event, s_callbacks[i].user_data);
        }
    }
}
