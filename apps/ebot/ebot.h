// SPDX-License-Identifier: MIT
// Copyright (c) 2026 EoS Project
// eBot — AI chat client for EAI framework

#ifndef EAPPS_APP_EBOT_H
#define EAPPS_APP_EBOT_H

#include "eapps/types.h"
#include <stdint.h>
#include <stdbool.h>

#define EBOT_VERSION          "1.0.0"
#define EBOT_MAX_MESSAGES     256
#define EBOT_MAX_MSG_LEN      4096
#define EBOT_MAX_MODELS       16
#define EBOT_MAX_TOOLS        32
#define EBOT_RESPONSE_BUF     65536

#define EBOT_DEFAULT_HOST     "192.168.1.100"
#define EBOT_DEFAULT_PORT     8420

typedef enum {
    EBOT_MSG_USER,
    EBOT_MSG_BOT,
    EBOT_MSG_SYSTEM,
    EBOT_MSG_TOOL_CALL,
    EBOT_MSG_ERROR,
} ebot_msg_type_t;

typedef struct {
    ebot_msg_type_t type;
    char            text[EBOT_MAX_MSG_LEN];
    uint32_t        timestamp;
} ebot_message_t;

typedef struct {
    char name[64];
    char description[256];
    char permission[64];
} ebot_tool_info_t;

typedef struct {
    char name[64];
    char tier[16];
    char params[16];
    bool active;
} ebot_model_info_t;

typedef struct {
    char     host[256];
    uint16_t port;
    int      timeout_ms;
    bool     connected;

    ebot_message_t  messages[EBOT_MAX_MESSAGES];
    int             msg_count;

    ebot_model_info_t models[EBOT_MAX_MODELS];
    int               model_count;
    int               active_model;

    ebot_tool_info_t  tools[EBOT_MAX_TOOLS];
    int               tool_count;

    uint32_t total_requests;
    uint32_t total_tokens;
} ebot_state_t;

int  ebot_state_init(ebot_state_t *state, const char *host, uint16_t port);
int  ebot_send_message(ebot_state_t *state, const char *message);
int  ebot_complete(ebot_state_t *state, const char *prompt);
int  ebot_fetch_status(ebot_state_t *state);
int  ebot_fetch_models(ebot_state_t *state);
int  ebot_fetch_tools(ebot_state_t *state);
int  ebot_reset_session(ebot_state_t *state);
int  ebot_cli_main(int argc, char **argv);

extern const eapps_app_info_t      ebot_info;
extern const eapps_app_lifecycle_t ebot_lifecycle;

#endif /* EAPPS_APP_EBOT_H */
