// SPDX-License-Identifier: MIT
// Copyright (c) 2026 EoS Project
// eBot — AI chat client for EAI framework
// ISO/IEC 25000 | ISO/IEC/IEEE 15288:2023

#include "ebot.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#ifdef EAPPS_PLATFORM_EOS
#include "eos_sdk.h"
#endif

/* ── Network includes (platform-specific) ── */
#ifdef _WIN32
  #include <winsock2.h>
  #include <ws2tcpip.h>
  #pragma comment(lib, "ws2_32.lib")
  #define CLOSE_SOCKET closesocket
#else
  #include <sys/socket.h>
  #include <netinet/in.h>
  #include <arpa/inet.h>
  #include <unistd.h>
  #define CLOSE_SOCKET close
#endif

/* ══════════════════════════════════════════════════════════════════════
 *  HTTP transport — talks to EAI Ebot Server (/v1/chat, /v1/complete…)
 * ══════════════════════════════════════════════════════════════════════ */

static int ebot_http_request(ebot_state_t *s, const char *method,
                             const char *path, const char *body,
                             char *response, int max_len) {
    int fd = socket(AF_INET, SOCK_STREAM, 0);
    if (fd < 0) return -1;

    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_port   = htons(s->port);
    inet_pton(AF_INET, s->host, &addr.sin_addr);

    if (connect(fd, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        CLOSE_SOCKET(fd);
        s->connected = false;
        return -1;
    }
    s->connected = true;

    char request[EBOT_RESPONSE_BUF];
    int rlen;
    if (body && strlen(body) > 0) {
        rlen = snprintf(request, sizeof(request),
            "%s %s HTTP/1.1\r\n"
            "Host: %s:%d\r\n"
            "Content-Type: application/json\r\n"
            "Content-Length: %d\r\n"
            "Connection: close\r\n\r\n%s",
            method, path, s->host, s->port, (int)strlen(body), body);
    } else {
        rlen = snprintf(request, sizeof(request),
            "%s %s HTTP/1.1\r\n"
            "Host: %s:%d\r\n"
            "Connection: close\r\n\r\n",
            method, path, s->host, s->port);
    }
    send(fd, request, rlen, 0);

    int total = 0;
    char buf[4096];
    while (total < max_len - 1) {
        int n = recv(fd, buf, sizeof(buf) - 1, 0);
        if (n <= 0) break;
        buf[n] = '\0';
        int copy = (total + n < max_len - 1) ? n : max_len - 1 - total;
        memcpy(response + total, buf, copy);
        total += copy;
    }
    response[total] = '\0';
    CLOSE_SOCKET(fd);

    char *json = strstr(response, "\r\n\r\n");
    if (json) { json += 4; memmove(response, json, strlen(json) + 1); }
    return 0;
}

/* ── Simple JSON value extractor (no dependency on cJSON) ── */
static const char *json_get_string(const char *json, const char *key,
                                   char *out, int max_len) {
    char pattern[128];
    snprintf(pattern, sizeof(pattern), "\"%s\"", key);
    const char *p = strstr(json, pattern);
    if (!p) return NULL;
    p = strchr(p + strlen(pattern), ':');
    if (!p) return NULL;
    while (*p == ':' || *p == ' ' || *p == '\t') p++;
    if (*p == '"') {
        p++;
        int i = 0;
        while (*p && *p != '"' && i < max_len - 1) {
            if (*p == '\\' && *(p + 1)) { p++; }
            out[i++] = *p++;
        }
        out[i] = '\0';
        return out;
    }
    return NULL;
}

/* ── Add a message to chat history ── */
static void ebot_add_message(ebot_state_t *s, ebot_msg_type_t type,
                              const char *text) {
    if (s->msg_count >= EBOT_MAX_MESSAGES) {
        memmove(&s->messages[0], &s->messages[1],
                sizeof(ebot_message_t) * (EBOT_MAX_MESSAGES - 1));
        s->msg_count = EBOT_MAX_MESSAGES - 1;
    }
    ebot_message_t *msg = &s->messages[s->msg_count++];
    msg->type = type;
    strncpy(msg->text, text, EBOT_MAX_MSG_LEN - 1);
    msg->text[EBOT_MAX_MSG_LEN - 1] = '\0';
    msg->timestamp = (uint32_t)time(NULL);
}

/* ══════════════════════════════════════════════════════════════════════
 *  Public API — state management and EAI communication
 * ══════════════════════════════════════════════════════════════════════ */

int ebot_state_init(ebot_state_t *state, const char *host, uint16_t port) {
    if (!state) return -1;
    memset(state, 0, sizeof(*state));
    strncpy(state->host, host ? host : EBOT_DEFAULT_HOST, 255);
    state->port       = port ? port : EBOT_DEFAULT_PORT;
    state->timeout_ms = 30000;
    state->connected  = false;
#ifdef _WIN32
    WSADATA wsa;
    WSAStartup(MAKEWORD(2, 2), &wsa);
#endif
    ebot_add_message(state, EBOT_MSG_SYSTEM,
        "eBot v" EBOT_VERSION " — connected to EAI. Type a message to begin.");
    return 0;
}

int ebot_send_message(ebot_state_t *state, const char *message) {
    if (!state || !message || !*message) return -1;

    ebot_add_message(state, EBOT_MSG_USER, message);

    char body[8192];
    snprintf(body, sizeof(body), "{\"message\":\"%s\"}", message);

    char *response = (char *)malloc(EBOT_RESPONSE_BUF);
    if (!response) return -1;

    int rc = ebot_http_request(state, "POST", "/v1/chat", body,
                               response, EBOT_RESPONSE_BUF);
    if (rc == 0) {
        char reply[EBOT_MAX_MSG_LEN];
        if (json_get_string(response, "response", reply, sizeof(reply))) {
            ebot_add_message(state, EBOT_MSG_BOT, reply);
        } else if (json_get_string(response, "text", reply, sizeof(reply))) {
            ebot_add_message(state, EBOT_MSG_BOT, reply);
        } else {
            ebot_add_message(state, EBOT_MSG_BOT, response);
        }

        char tool_name[128];
        if (json_get_string(response, "tool_call", tool_name, sizeof(tool_name))) {
            char tool_msg[EBOT_MAX_MSG_LEN];
            snprintf(tool_msg, sizeof(tool_msg), "[Tool Call] %s", tool_name);
            ebot_add_message(state, EBOT_MSG_TOOL_CALL, tool_msg);
        }
        state->total_requests++;
    } else {
        ebot_add_message(state, EBOT_MSG_ERROR,
            "Failed to connect to EAI server.");
    }

    free(response);
    return rc;
}

int ebot_complete(ebot_state_t *state, const char *prompt) {
    if (!state || !prompt) return -1;

    ebot_add_message(state, EBOT_MSG_USER, prompt);

    char body[8192];
    snprintf(body, sizeof(body), "{\"prompt\":\"%s\"}", prompt);

    char *response = (char *)malloc(EBOT_RESPONSE_BUF);
    if (!response) return -1;

    int rc = ebot_http_request(state, "POST", "/v1/complete", body,
                               response, EBOT_RESPONSE_BUF);
    if (rc == 0) {
        char reply[EBOT_MAX_MSG_LEN];
        if (json_get_string(response, "text", reply, sizeof(reply))) {
            ebot_add_message(state, EBOT_MSG_BOT, reply);
        } else {
            ebot_add_message(state, EBOT_MSG_BOT, response);
        }
        state->total_requests++;
    } else {
        ebot_add_message(state, EBOT_MSG_ERROR,
            "Completion request failed.");
    }

    free(response);
    return rc;
}

int ebot_fetch_status(ebot_state_t *state) {
    if (!state) return -1;
    char *response = (char *)malloc(EBOT_RESPONSE_BUF);
    if (!response) return -1;

    int rc = ebot_http_request(state, "GET", "/v1/status", NULL,
                               response, EBOT_RESPONSE_BUF);
    if (rc == 0) {
        char val[64];
        if (json_get_string(response, "total_requests", val, sizeof(val)))
            state->total_requests = (uint32_t)atoi(val);
        if (json_get_string(response, "total_tokens", val, sizeof(val)))
            state->total_tokens = (uint32_t)atoi(val);
    }

    free(response);
    return rc;
}

int ebot_fetch_models(ebot_state_t *state) {
    if (!state) return -1;
    char *response = (char *)malloc(EBOT_RESPONSE_BUF);
    if (!response) return -1;

    int rc = ebot_http_request(state, "GET", "/v1/models", NULL,
                               response, EBOT_RESPONSE_BUF);
    if (rc == 0) {
        state->model_count = 0;
        const char *p = response;
        while (state->model_count < EBOT_MAX_MODELS) {
            char name[64];
            if (!json_get_string(p, "name", name, sizeof(name))) break;
            strncpy(state->models[state->model_count].name, name, 63);

            char tier[16];
            if (json_get_string(p, "tier", tier, sizeof(tier)))
                strncpy(state->models[state->model_count].tier, tier, 15);

            char params[16];
            if (json_get_string(p, "params", params, sizeof(params)))
                strncpy(state->models[state->model_count].params, params, 15);

            state->model_count++;
            p = strstr(p + 1, "\"name\"");
            if (!p) break;
        }
    }

    free(response);
    return rc;
}

int ebot_fetch_tools(ebot_state_t *state) {
    if (!state) return -1;
    char *response = (char *)malloc(EBOT_RESPONSE_BUF);
    if (!response) return -1;

    int rc = ebot_http_request(state, "GET", "/v1/tools", NULL,
                               response, EBOT_RESPONSE_BUF);
    if (rc == 0) {
        state->tool_count = 0;
        const char *p = response;
        while (state->tool_count < EBOT_MAX_TOOLS) {
            char name[64];
            if (!json_get_string(p, "name", name, sizeof(name))) break;
            strncpy(state->tools[state->tool_count].name, name, 63);

            char desc[256];
            if (json_get_string(p, "description", desc, sizeof(desc)))
                strncpy(state->tools[state->tool_count].description, desc, 255);

            char perm[64];
            if (json_get_string(p, "permission", perm, sizeof(perm)))
                strncpy(state->tools[state->tool_count].permission, perm, 63);

            state->tool_count++;
            p = strstr(p + 1, "\"name\"");
            if (!p) break;
        }
    }

    free(response);
    return rc;
}

int ebot_reset_session(ebot_state_t *state) {
    if (!state) return -1;
    char response[1024];
    int rc = ebot_http_request(state, "POST", "/v1/reset", "{}",
                               response, sizeof(response));
    if (rc == 0) {
        state->msg_count = 0;
        ebot_add_message(state, EBOT_MSG_SYSTEM, "Session reset.");
    }
    return rc;
}

/* ══════════════════════════════════════════════════════════════════════
 *  CLI mode — `ebot chat "msg"`, `ebot complete "prompt"`, etc.
 * ══════════════════════════════════════════════════════════════════════ */

static void ebot_cli_usage(void) {
    printf(
        "eBot v" EBOT_VERSION " — AI chat client for EAI\n\n"
        "Usage:\n"
        "  ebot chat \"message\"              Send a chat message\n"
        "  ebot complete \"prompt\"            Single-shot completion\n"
        "  ebot models                       List available LLM models\n"
        "  ebot tools                        List available tools\n"
        "  ebot status                       Show server status\n"
        "  ebot reset                        Reset conversation\n"
        "  ebot interactive                  Interactive chat mode\n"
        "\n"
        "Options:\n"
        "  --host <ip>                       EAI server host (default: %s)\n"
        "  --port <port>                     EAI server port (default: %d)\n"
        "  --help                            Show this help\n",
        EBOT_DEFAULT_HOST, EBOT_DEFAULT_PORT);
}

static void ebot_cli_interactive(ebot_state_t *state) {
    printf("eBot v" EBOT_VERSION " interactive mode\n");
    printf("Server: %s:%d\n", state->host, state->port);
    printf("Type 'quit' to exit, 'reset' to clear history\n\n");

    char input[EBOT_MAX_MSG_LEN];
    while (1) {
        printf("\033[36myou>\033[0m ");
        fflush(stdout);
        if (!fgets(input, sizeof(input), stdin)) break;

        size_t len = strlen(input);
        if (len > 0 && input[len - 1] == '\n') input[len - 1] = '\0';
        if (strlen(input) == 0) continue;

        if (strcmp(input, "quit") == 0 || strcmp(input, "exit") == 0) break;
        if (strcmp(input, "reset") == 0) {
            ebot_reset_session(state);
            printf("\033[33m[session reset]\033[0m\n");
            continue;
        }
        if (strcmp(input, "models") == 0) {
            ebot_fetch_models(state);
            for (int i = 0; i < state->model_count; i++) {
                printf("  %s%s (%s, %s)\n",
                       state->models[i].active ? "* " : "  ",
                       state->models[i].name,
                       state->models[i].tier,
                       state->models[i].params);
            }
            continue;
        }
        if (strcmp(input, "tools") == 0) {
            ebot_fetch_tools(state);
            for (int i = 0; i < state->tool_count; i++) {
                printf("  %s — %s [%s]\n",
                       state->tools[i].name,
                       state->tools[i].description,
                       state->tools[i].permission);
            }
            continue;
        }
        if (strcmp(input, "status") == 0) {
            ebot_fetch_status(state);
            printf("  Requests: %u  Tokens: %u  Connected: %s\n",
                   state->total_requests, state->total_tokens,
                   state->connected ? "yes" : "no");
            continue;
        }

        if (ebot_send_message(state, input) == 0) {
            ebot_message_t *last = &state->messages[state->msg_count - 1];
            if (last->type == EBOT_MSG_TOOL_CALL) {
                printf("\033[35m%s\033[0m\n", last->text);
                if (state->msg_count >= 2) {
                    ebot_message_t *reply = &state->messages[state->msg_count - 2];
                    if (reply->type == EBOT_MSG_BOT)
                        printf("\033[32mbot>\033[0m %s\n", reply->text);
                }
            } else if (last->type == EBOT_MSG_BOT) {
                printf("\033[32mbot>\033[0m %s\n", last->text);
            } else if (last->type == EBOT_MSG_ERROR) {
                printf("\033[31merror>\033[0m %s\n", last->text);
            }
        } else {
            printf("\033[31merror>\033[0m Connection failed\n");
        }
    }
}

int ebot_cli_main(int argc, char **argv) {
    const char *host = EBOT_DEFAULT_HOST;
    uint16_t port = EBOT_DEFAULT_PORT;

    int cmd_idx = 1;
    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--host") == 0 && i + 1 < argc) {
            host = argv[++i];
            cmd_idx = i + 1;
        } else if (strcmp(argv[i], "--port") == 0 && i + 1 < argc) {
            port = (uint16_t)atoi(argv[++i]);
            cmd_idx = i + 1;
        } else if (strcmp(argv[i], "--help") == 0) {
            ebot_cli_usage();
            return 0;
        } else {
            cmd_idx = i;
            break;
        }
    }

    if (cmd_idx >= argc) {
        ebot_cli_usage();
        return 1;
    }

    ebot_state_t state;
    ebot_state_init(&state, host, port);

    const char *cmd = argv[cmd_idx];

    if (strcmp(cmd, "chat") == 0) {
        if (cmd_idx + 1 >= argc) {
            fprintf(stderr, "Usage: ebot chat \"message\"\n");
            return 1;
        }
        if (ebot_send_message(&state, argv[cmd_idx + 1]) == 0) {
            ebot_message_t *last = &state.messages[state.msg_count - 1];
            printf("%s\n", last->text);
        } else {
            fprintf(stderr, "Error: could not reach EAI at %s:%d\n", host, port);
            return 1;
        }
    } else if (strcmp(cmd, "complete") == 0) {
        if (cmd_idx + 1 >= argc) {
            fprintf(stderr, "Usage: ebot complete \"prompt\"\n");
            return 1;
        }
        if (ebot_complete(&state, argv[cmd_idx + 1]) == 0) {
            ebot_message_t *last = &state.messages[state.msg_count - 1];
            printf("%s\n", last->text);
        } else {
            fprintf(stderr, "Error: completion failed\n");
            return 1;
        }
    } else if (strcmp(cmd, "models") == 0) {
        if (ebot_fetch_models(&state) == 0) {
            printf("Available models:\n");
            for (int i = 0; i < state.model_count; i++) {
                printf("  %s%s (%s, %s)\n",
                       state.models[i].active ? "* " : "  ",
                       state.models[i].name,
                       state.models[i].tier,
                       state.models[i].params);
            }
        } else {
            fprintf(stderr, "Error: could not fetch models\n");
            return 1;
        }
    } else if (strcmp(cmd, "tools") == 0) {
        if (ebot_fetch_tools(&state) == 0) {
            printf("Available tools:\n");
            for (int i = 0; i < state.tool_count; i++) {
                printf("  %-20s %s [%s]\n",
                       state.tools[i].name,
                       state.tools[i].description,
                       state.tools[i].permission);
            }
        } else {
            fprintf(stderr, "Error: could not fetch tools\n");
            return 1;
        }
    } else if (strcmp(cmd, "status") == 0) {
        if (ebot_fetch_status(&state) == 0) {
            printf("EAI Server: %s:%d\n", state.host, state.port);
            printf("Requests: %u  Tokens: %u\n",
                   state.total_requests, state.total_tokens);
        } else {
            fprintf(stderr, "Error: could not fetch status\n");
            return 1;
        }
    } else if (strcmp(cmd, "reset") == 0) {
        if (ebot_reset_session(&state) == 0) {
            printf("Session reset.\n");
        } else {
            fprintf(stderr, "Error: could not reset session\n");
            return 1;
        }
    } else if (strcmp(cmd, "interactive") == 0) {
        ebot_cli_interactive(&state);
    } else {
        fprintf(stderr, "Unknown command: %s\n", cmd);
        ebot_cli_usage();
        return 1;
    }

    return 0;
}

/* ══════════════════════════════════════════════════════════════════════
 *  GUI — LVGL chat interface (touchscreen / desktop)
 * ══════════════════════════════════════════════════════════════════════ */

static ebot_state_t g_ebot;
static lv_obj_t    *g_chat_list;
static lv_obj_t    *g_input_ta;
static lv_obj_t    *g_status_label;
static lv_obj_t    *g_model_dropdown;

static void ebot_gui_refresh_chat(void) {
    if (!g_chat_list) return;
    lv_obj_clean(g_chat_list);

    for (int i = 0; i < g_ebot.msg_count; i++) {
        ebot_message_t *m = &g_ebot.messages[i];
        lv_obj_t *bubble = lv_obj_create(g_chat_list);
        lv_obj_set_width(bubble, lv_pct(85));
        lv_obj_set_height(bubble, LV_SIZE_CONTENT);
        lv_obj_set_style_pad_all(bubble, 8, 0);
        lv_obj_set_style_radius(bubble, 12, 0);

        switch (m->type) {
        case EBOT_MSG_USER:
            lv_obj_set_style_bg_color(bubble, lv_color_hex(0x1565C0), 0);
            lv_obj_align(bubble, LV_ALIGN_RIGHT_MID, 0, 0);
            break;
        case EBOT_MSG_BOT:
            lv_obj_set_style_bg_color(bubble, lv_color_hex(0x2E7D32), 0);
            lv_obj_align(bubble, LV_ALIGN_LEFT_MID, 0, 0);
            break;
        case EBOT_MSG_TOOL_CALL:
            lv_obj_set_style_bg_color(bubble, lv_color_hex(0x6A1B9A), 0);
            lv_obj_align(bubble, LV_ALIGN_LEFT_MID, 0, 0);
            break;
        case EBOT_MSG_SYSTEM:
            lv_obj_set_style_bg_color(bubble, lv_color_hex(0x424242), 0);
            lv_obj_align(bubble, LV_ALIGN_CENTER, 0, 0);
            break;
        case EBOT_MSG_ERROR:
            lv_obj_set_style_bg_color(bubble, lv_color_hex(0xC62828), 0);
            lv_obj_align(bubble, LV_ALIGN_LEFT_MID, 0, 0);
            break;
        }

        lv_obj_t *label = lv_label_create(bubble);
        lv_label_set_long_mode(label, LV_LABEL_LONG_WRAP);
        lv_obj_set_width(label, lv_pct(100));
        lv_label_set_text(label, m->text);
        lv_obj_set_style_text_color(label, lv_color_hex(0xFFFFFF), 0);
    }

    lv_obj_scroll_to_y(g_chat_list, LV_COORD_MAX, LV_ANIM_ON);
}

static void ebot_gui_update_status(void) {
    if (!g_status_label) return;
    char buf[128];
    snprintf(buf, sizeof(buf), "%s:%d | %s | Req: %u",
             g_ebot.host, g_ebot.port,
             g_ebot.connected ? "Connected" : "Disconnected",
             g_ebot.total_requests);
    lv_label_set_text(g_status_label, buf);
}

static void ebot_gui_send_cb(lv_event_t *e) {
    (void)e;
    if (!g_input_ta) return;
    const char *text = lv_textarea_get_text(g_input_ta);
    if (!text || !*text) return;

    ebot_send_message(&g_ebot, text);
    lv_textarea_set_text(g_input_ta, "");
    ebot_gui_refresh_chat();
    ebot_gui_update_status();
}

static void ebot_gui_input_cb(lv_event_t *e) {
    lv_event_code_t code = lv_event_get_code(e);
    if (code == LV_EVENT_READY) {
        ebot_gui_send_cb(e);
    }
}

static void ebot_gui_reset_cb(lv_event_t *e) {
    (void)e;
    ebot_reset_session(&g_ebot);
    ebot_gui_refresh_chat();
    ebot_gui_update_status();
}

static void ebot_gui_tools_cb(lv_event_t *e) {
    (void)e;
    ebot_fetch_tools(&g_ebot);
    char buf[EBOT_MAX_MSG_LEN] = "Available tools:\n";
    for (int i = 0; i < g_ebot.tool_count; i++) {
        char line[320];
        snprintf(line, sizeof(line), "• %s — %s\n",
                 g_ebot.tools[i].name, g_ebot.tools[i].description);
        strncat(buf, line, sizeof(buf) - strlen(buf) - 1);
    }
    ebot_add_message(&g_ebot, EBOT_MSG_SYSTEM, buf);
    ebot_gui_refresh_chat();
}

static void ebot_gui_models_cb(lv_event_t *e) {
    (void)e;
    ebot_fetch_models(&g_ebot);
    if (g_model_dropdown) {
        char opts[1024] = "";
        for (int i = 0; i < g_ebot.model_count; i++) {
            if (i > 0) strncat(opts, "\n", sizeof(opts) - strlen(opts) - 1);
            strncat(opts, g_ebot.models[i].name,
                    sizeof(opts) - strlen(opts) - 1);
        }
        lv_dropdown_set_options(g_model_dropdown, opts);
    }
}

static bool ebot_init(lv_obj_t *parent) {
    ebot_state_init(&g_ebot, NULL, 0);

    lv_obj_t *main_col = lv_obj_create(parent);
    lv_obj_set_size(main_col, lv_pct(100), lv_pct(100));
    lv_obj_set_flex_flow(main_col, LV_FLEX_FLOW_COLUMN);
    lv_obj_set_style_pad_all(main_col, 4, 0);
    lv_obj_set_style_bg_opa(main_col, LV_OPA_TRANSP, 0);
    lv_obj_set_style_border_width(main_col, 0, 0);

    /* ── Top bar: title + model dropdown + tools/reset buttons ── */
    lv_obj_t *top_bar = lv_obj_create(main_col);
    lv_obj_set_width(top_bar, lv_pct(100));
    lv_obj_set_height(top_bar, 44);
    lv_obj_set_flex_flow(top_bar, LV_FLEX_FLOW_ROW);
    lv_obj_set_flex_align(top_bar, LV_FLEX_ALIGN_SPACE_BETWEEN,
                          LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER);
    lv_obj_set_style_pad_all(top_bar, 4, 0);

    lv_obj_t *title = lv_label_create(top_bar);
    lv_label_set_text(title, LV_SYMBOL_CHARGE " eBot");
    lv_obj_set_style_text_font(title, &lv_font_montserrat_16, 0);

    g_model_dropdown = lv_dropdown_create(top_bar);
    lv_dropdown_set_options(g_model_dropdown, "phi-3-mini-q4\n(fetch models...)");
    lv_obj_set_width(g_model_dropdown, 160);

    lv_obj_t *btn_tools = lv_btn_create(top_bar);
    lv_obj_t *lbl_tools = lv_label_create(btn_tools);
    lv_label_set_text(lbl_tools, LV_SYMBOL_LIST);
    lv_obj_add_event_cb(btn_tools, ebot_gui_tools_cb, LV_EVENT_CLICKED, NULL);

    lv_obj_t *btn_models = lv_btn_create(top_bar);
    lv_obj_t *lbl_models = lv_label_create(btn_models);
    lv_label_set_text(lbl_models, LV_SYMBOL_REFRESH);
    lv_obj_add_event_cb(btn_models, ebot_gui_models_cb, LV_EVENT_CLICKED, NULL);

    lv_obj_t *btn_reset = lv_btn_create(top_bar);
    lv_obj_t *lbl_reset = lv_label_create(btn_reset);
    lv_label_set_text(lbl_reset, LV_SYMBOL_TRASH);
    lv_obj_add_event_cb(btn_reset, ebot_gui_reset_cb, LV_EVENT_CLICKED, NULL);

    /* ── Chat message list (scrollable) ── */
    g_chat_list = lv_obj_create(main_col);
    lv_obj_set_width(g_chat_list, lv_pct(100));
    lv_obj_set_flex_grow(g_chat_list, 1);
    lv_obj_set_flex_flow(g_chat_list, LV_FLEX_FLOW_COLUMN);
    lv_obj_set_style_pad_row(g_chat_list, 6, 0);
    lv_obj_set_scrollbar_mode(g_chat_list, LV_SCROLLBAR_MODE_AUTO);

    /* ── Input bar: text area + send button ── */
    lv_obj_t *input_bar = lv_obj_create(main_col);
    lv_obj_set_width(input_bar, lv_pct(100));
    lv_obj_set_height(input_bar, 50);
    lv_obj_set_flex_flow(input_bar, LV_FLEX_FLOW_ROW);
    lv_obj_set_style_pad_all(input_bar, 4, 0);

    g_input_ta = lv_textarea_create(input_bar);
    lv_textarea_set_placeholder_text(g_input_ta, "Type a message...");
    lv_textarea_set_one_line(g_input_ta, true);
    lv_obj_set_flex_grow(g_input_ta, 1);
    lv_obj_add_event_cb(g_input_ta, ebot_gui_input_cb, LV_EVENT_READY, NULL);

    lv_obj_t *btn_send = lv_btn_create(input_bar);
    lv_obj_set_size(btn_send, 50, 42);
    lv_obj_t *lbl_send = lv_label_create(btn_send);
    lv_label_set_text(lbl_send, LV_SYMBOL_RIGHT);
    lv_obj_center(lbl_send);
    lv_obj_add_event_cb(btn_send, ebot_gui_send_cb, LV_EVENT_CLICKED, NULL);

    /* ── Status bar ── */
    g_status_label = lv_label_create(main_col);
    lv_obj_set_width(g_status_label, lv_pct(100));
    lv_obj_set_style_text_font(g_status_label, &lv_font_montserrat_10, 0);
    lv_obj_set_style_text_color(g_status_label,
                                lv_color_hex(0x888888), 0);
    ebot_gui_update_status();

    ebot_gui_refresh_chat();
    return true;
}

static void ebot_deinit(void) {
    g_chat_list     = NULL;
    g_input_ta      = NULL;
    g_status_label  = NULL;
    g_model_dropdown = NULL;
    memset(&g_ebot, 0, sizeof(g_ebot));
}

static void ebot_on_show(void) {
    ebot_gui_update_status();
}

static void ebot_on_hide(void) { }

/* ══════════════════════════════════════════════════════════════════════
 *  App registration
 * ══════════════════════════════════════════════════════════════════════ */

const eapps_app_info_t ebot_info = {
    .id          = "ebot",
    .name        = "eBot",
    .icon        = "ai",
    .description = "AI chat client: EAI LLM, tool calls, model switching",
    .category    = EAPPS_CAT_SECURITY,
    .version     = EBOT_VERSION,
};

const eapps_app_lifecycle_t ebot_lifecycle = {
    .init    = ebot_init,
    .deinit  = ebot_deinit,
    .on_show = ebot_on_show,
    .on_hide = ebot_on_hide,
};
