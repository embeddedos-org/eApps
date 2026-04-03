// SPDX-License-Identifier: MIT
// Input layer tests for eBrowser web browser
#include "eBrowser/input.h"
#include <stdio.h>
#include <string.h>

static int s_pass = 0, s_fail = 0;
#define TEST(name) static void name(void)
#define RUN(name) do { printf("  %s... ", #name); name(); printf("PASS\n"); s_pass++; } while(0)
#define ASSERT(cond) do { if(!(cond)) { printf("FAIL: %s:%d: %s\n", __FILE__, __LINE__, #cond); s_fail++; return; } } while(0)

static int s_callback_count = 0;
static eb_input_event_t s_last_event;

static void test_callback(const eb_input_event_t *event, void *user_data) {
    s_callback_count++;
    s_last_event = *event;
    (void)user_data;
}

static void reset_callback_state(void) {
    s_callback_count = 0;
    memset(&s_last_event, 0, sizeof(s_last_event));
}

TEST(test_init_deinit) {
    eb_input_init();
    eb_input_deinit();
}

TEST(test_register_callback) {
    eb_input_init();
    eb_input_register_callback(test_callback, NULL);
    eb_input_deinit();
}

TEST(test_register_null_callback) {
    eb_input_init();
    eb_input_register_callback(NULL, NULL);
    eb_input_deinit();
}

TEST(test_process_pointer_click) {
    eb_input_init();
    reset_callback_state();
    eb_input_register_callback(test_callback, NULL);
    eb_input_event_t ev = {.type = EB_INPUT_POINTER, .x = 100, .y = 200, .pressed = true};
    eb_input_process(&ev);
    ASSERT(s_callback_count == 1);
    ASSERT(s_last_event.type == EB_INPUT_POINTER);
    ASSERT(s_last_event.x == 100);
    ASSERT(s_last_event.y == 200);
    ASSERT(s_last_event.pressed == true);
    eb_input_deinit();
}

TEST(test_process_pointer_release) {
    eb_input_init();
    reset_callback_state();
    eb_input_register_callback(test_callback, NULL);
    eb_input_event_t ev = {.type = EB_INPUT_POINTER, .x = 50, .y = 75, .pressed = false};
    eb_input_process(&ev);
    ASSERT(s_last_event.pressed == false);
    eb_input_deinit();
}

TEST(test_process_keyboard_enter) {
    eb_input_init();
    reset_callback_state();
    eb_input_register_callback(test_callback, NULL);
    eb_input_event_t ev = {.type = EB_INPUT_KEYBOARD, .key = EB_KEY_ENTER};
    eb_input_process(&ev);
    ASSERT(s_last_event.type == EB_INPUT_KEYBOARD);
    ASSERT(s_last_event.key == EB_KEY_ENTER);
    eb_input_deinit();
}

TEST(test_process_keyboard_backspace) {
    eb_input_init();
    reset_callback_state();
    eb_input_register_callback(test_callback, NULL);
    eb_input_event_t ev = {.type = EB_INPUT_KEYBOARD, .key = EB_KEY_BACKSPACE};
    eb_input_process(&ev);
    ASSERT(s_last_event.key == EB_KEY_BACKSPACE);
    eb_input_deinit();
}

TEST(test_process_keyboard_f5_refresh) {
    eb_input_init();
    reset_callback_state();
    eb_input_register_callback(test_callback, NULL);
    eb_input_event_t ev = {.type = EB_INPUT_KEYBOARD, .key = EB_KEY_F5};
    eb_input_process(&ev);
    ASSERT(s_last_event.key == EB_KEY_F5);
    eb_input_deinit();
}

TEST(test_process_keyboard_escape) {
    eb_input_init();
    reset_callback_state();
    eb_input_register_callback(test_callback, NULL);
    eb_input_event_t ev = {.type = EB_INPUT_KEYBOARD, .key = EB_KEY_ESCAPE};
    eb_input_process(&ev);
    ASSERT(s_last_event.key == EB_KEY_ESCAPE);
    eb_input_deinit();
}

TEST(test_process_keyboard_character) {
    eb_input_init();
    reset_callback_state();
    eb_input_register_callback(test_callback, NULL);
    eb_input_event_t ev = {.type = EB_INPUT_KEYBOARD, .character = 'a'};
    eb_input_process(&ev);
    ASSERT(s_last_event.character == 'a');
    eb_input_deinit();
}

TEST(test_process_touch_event) {
    eb_input_init();
    reset_callback_state();
    eb_input_register_callback(test_callback, NULL);
    eb_input_event_t ev = {.type = EB_INPUT_TOUCH, .x = 300, .y = 400, .pressed = true};
    eb_input_process(&ev);
    ASSERT(s_last_event.type == EB_INPUT_TOUCH);
    ASSERT(s_last_event.x == 300);
    ASSERT(s_last_event.y == 400);
    eb_input_deinit();
}

static int s_cb2_count = 0;
static void test_callback2(const eb_input_event_t *event, void *user_data) {
    s_cb2_count++;
    (void)event; (void)user_data;
}

TEST(test_multiple_callbacks) {
    eb_input_init();
    reset_callback_state();
    s_cb2_count = 0;
    eb_input_register_callback(test_callback, NULL);
    eb_input_register_callback(test_callback2, NULL);
    eb_input_event_t ev = {.type = EB_INPUT_POINTER, .x = 10, .y = 20, .pressed = true};
    eb_input_process(&ev);
    ASSERT(s_callback_count == 1);
    ASSERT(s_cb2_count == 1);
    eb_input_deinit();
}

TEST(test_process_null_event) {
    eb_input_init();
    reset_callback_state();
    eb_input_register_callback(test_callback, NULL);
    eb_input_process(NULL);
    ASSERT(s_callback_count == 0);
    eb_input_deinit();
}

TEST(test_multiple_events) {
    eb_input_init();
    reset_callback_state();
    eb_input_register_callback(test_callback, NULL);
    for (int i = 0; i < 10; i++) {
        eb_input_event_t ev = {.type = EB_INPUT_POINTER, .x = i * 10, .y = i * 20, .pressed = true};
        eb_input_process(&ev);
    }
    ASSERT(s_callback_count == 10);
    ASSERT(s_last_event.x == 90);
    ASSERT(s_last_event.y == 180);
    eb_input_deinit();
}

static void *s_user_data_received = NULL;
static void user_data_callback(const eb_input_event_t *event, void *user_data) {
    s_user_data_received = user_data;
    (void)event;
}

TEST(test_callback_user_data) {
    eb_input_init();
    int ctx = 42;
    s_user_data_received = NULL;
    eb_input_register_callback(user_data_callback, &ctx);
    eb_input_event_t ev = {.type = EB_INPUT_POINTER};
    eb_input_process(&ev);
    ASSERT(s_user_data_received == &ctx);
    eb_input_deinit();
}

TEST(test_arrow_keys) {
    eb_input_init();
    reset_callback_state();
    eb_input_register_callback(test_callback, NULL);
    eb_key_t arrows[] = {EB_KEY_LEFT, EB_KEY_RIGHT, EB_KEY_UP, EB_KEY_DOWN};
    for (int i = 0; i < 4; i++) {
        eb_input_event_t ev = {.type = EB_INPUT_KEYBOARD, .key = arrows[i]};
        eb_input_process(&ev);
    }
    ASSERT(s_callback_count == 4);
    eb_input_deinit();
}

int main(void) {
    printf("=== Input Layer Tests ===\n");
    RUN(test_init_deinit);
    RUN(test_register_callback);
    RUN(test_register_null_callback);
    RUN(test_process_pointer_click);
    RUN(test_process_pointer_release);
    RUN(test_process_keyboard_enter);
    RUN(test_process_keyboard_backspace);
    RUN(test_process_keyboard_f5_refresh);
    RUN(test_process_keyboard_escape);
    RUN(test_process_keyboard_character);
    RUN(test_process_touch_event);
    RUN(test_multiple_callbacks);
    RUN(test_process_null_event);
    RUN(test_multiple_events);
    RUN(test_callback_user_data);
    RUN(test_arrow_keys);
    printf("\nResults: %d passed, %d failed\n", s_pass, s_fail);
    return s_fail > 0 ? 1 : 0;
}
