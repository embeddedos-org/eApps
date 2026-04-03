// SPDX-License-Identifier: MIT
#ifndef eBrowser_INPUT_H
#define eBrowser_INPUT_H

#include <stdint.h>
#include <stdbool.h>

typedef enum {
    EB_INPUT_POINTER,
    EB_INPUT_KEYBOARD,
    EB_INPUT_TOUCH
} eb_input_type_t;

typedef enum {
    EB_KEY_NONE = 0,
    EB_KEY_ENTER,
    EB_KEY_BACKSPACE,
    EB_KEY_TAB,
    EB_KEY_ESCAPE,
    EB_KEY_LEFT,
    EB_KEY_RIGHT,
    EB_KEY_UP,
    EB_KEY_DOWN,
    EB_KEY_HOME,
    EB_KEY_END,
    EB_KEY_F5
} eb_key_t;

typedef struct {
    eb_input_type_t type;
    int             x, y;
    bool            pressed;
    eb_key_t        key;
    char            character;
} eb_input_event_t;

typedef void (*eb_input_callback_t)(const eb_input_event_t *event, void *user_data);

void eb_input_init(void);
void eb_input_deinit(void);
void eb_input_register_callback(eb_input_callback_t cb, void *user_data);
void eb_input_process(const eb_input_event_t *event);

#endif /* eBrowser_INPUT_H */
