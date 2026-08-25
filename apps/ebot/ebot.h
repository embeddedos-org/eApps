// SPDX-License-Identifier: MIT
// eBot — EoS LVGL Application
#pragma once
#include "lvgl.h"
#include "eapps_core.h"

/* ------------------------------------------------------------------------
 * eBot client API
 *
 * ebot.c uses this type layer, but the header only ever declared the two
 * eapps_* lifecycle symbols, so the app has never compiled: 17 identifiers were
 * undefined. Same failure mode as the missing core/common/include/eapps_core.h.
 *
 * Every struct field and its width below is RECOVERED from ebot.c, not invented:
 *
 *   host[256]                  strncpy(state->host, ..., 255)          :132
 *   port          uint16_t     ebot_state_init(..., uint16_t port)     :129
 *   timeout_ms                 state->timeout_ms = 30000              :134
 *   connected     bool         state->connected = false               :135
 *   total_requests/_tokens     (uint32_t)atoi(val)                    :224,226
 *   models[].name[64]          strncpy(..., 63); name[63] = 0          :246
 *   models[].tier[16]          strncpy(..., 15); tier[15] = 0          :251
 *   models[].params[16]        strncpy(..., 15); params[15] = 0        :257
 *   models[].active   bool     models[i].active ? "* " : "  "     :369,474
 *   tools[].name[64]           strncpy(..., 63)                        :284
 *   tools[].description[256]   strncpy(..., 255)                       :289
 *   tools[].permission[64]     strncpy(..., 63)                        :295
 *   message.type/text/timestamp                                       :119-122
 *
 * The five CAPACITIES are the exception - they are choices, because nothing in
 * ebot.c pins them. They are marked below. Adjust freely; only EBOT_MAX_MESSAGES
 * has structural meaning, as the message ring shifts by one at :113-117.
 * ------------------------------------------------------------------------ */

#include <stdbool.h>
#include <stdint.h>

#define EBOT_VERSION       "2.0.0"          /* matches ebot_info.version */
#define EBOT_DEFAULT_HOST  "127.0.0.1"      /* local eAI Ebot Server */
#define EBOT_DEFAULT_PORT  8080

/* Capacities - chosen, not recovered from ebot.c. */
#define EBOT_MAX_MESSAGES  64
#define EBOT_MAX_MSG_LEN   2048
#define EBOT_MAX_MODELS    32
#define EBOT_MAX_TOOLS     32
#define EBOT_RESPONSE_BUF  8192

typedef enum {
    EBOT_MSG_USER = 0,
    EBOT_MSG_BOT,
    EBOT_MSG_SYSTEM,
    EBOT_MSG_TOOL_CALL,
    EBOT_MSG_ERROR,
} ebot_msg_type_t;

typedef struct {
    ebot_msg_type_t type;
    char            text[EBOT_MAX_MSG_LEN];
    uint32_t        timestamp;              /**< Unix seconds. */
} ebot_message_t;

typedef struct {
    char name[64];
    char tier[16];
    char params[16];
    bool active;        /**< Marked "* " in the model list at :369, :474. */
} ebot_model_t;

typedef struct {
    char name[64];
    char description[256];
    char permission[64];
} ebot_tool_t;

typedef struct {
    char           host[256];
    uint16_t       port;
    uint32_t       timeout_ms;
    bool           connected;
    uint32_t       total_requests;
    uint32_t       total_tokens;

    ebot_message_t messages[EBOT_MAX_MESSAGES];
    int            msg_count;
    ebot_model_t   models[EBOT_MAX_MODELS];
    int            model_count;
    ebot_tool_t    tools[EBOT_MAX_TOOLS];
    int            tool_count;
} ebot_state_t;

int ebot_state_init(ebot_state_t *state, const char *host, uint16_t port);
int ebot_send_message(ebot_state_t *state, const char *message);
int ebot_complete(ebot_state_t *state, const char *prompt);
int ebot_fetch_status(ebot_state_t *state);
int ebot_fetch_models(ebot_state_t *state);
int ebot_fetch_tools(ebot_state_t *state);
int ebot_reset_session(ebot_state_t *state);
int ebot_cli_main(int argc, char **argv);

extern const eapps_app_info_t ebot_info;
extern const eapps_app_lifecycle_t ebot_lifecycle;
