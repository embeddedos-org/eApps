// SPDX-License-Identifier: MIT
#include "eBrowser/html_parser.h"
#include "eBrowser/compat.h"
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <stdio.h>

static const char *s_void_elements[] = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr", NULL
};

static const char *s_raw_text_elements[] = {
    "script", "style", "textarea", NULL
};

bool eb_html_is_void_element(const char *tag) {
    if (!tag) return false;
    for (int i = 0; s_void_elements[i]; i++) {
        if (strcasecmp(tag, s_void_elements[i]) == 0) return true;
    }
    return false;
}

static bool is_raw_text_element(const char *tag) {
    if (!tag) return false;
    for (int i = 0; s_raw_text_elements[i]; i++) {
        if (strcasecmp(tag, s_raw_text_elements[i]) == 0) return true;
    }
    return false;
}

void eb_tokenizer_init(eb_tokenizer_t *tok, const char *html, size_t len) {
    if (!tok) return;
    tok->input = html;
    tok->pos = 0;
    tok->len = len;
}

static void skip_whitespace(eb_tokenizer_t *tok) {
    while (tok->pos < tok->len && isspace((unsigned char)tok->input[tok->pos]))
        tok->pos++;
}

static char peek(eb_tokenizer_t *tok) {
    return (tok->pos < tok->len) ? tok->input[tok->pos] : '\0';
}

static char advance(eb_tokenizer_t *tok) {
    return (tok->pos < tok->len) ? tok->input[tok->pos++] : '\0';
}

static bool starts_with(eb_tokenizer_t *tok, const char *str) {
    size_t slen = strlen(str);
    if (tok->pos + slen > tok->len) return false;
    return strncasecmp(tok->input + tok->pos, str, slen) == 0;
}

static void parse_tag_name(eb_tokenizer_t *tok, char *out, size_t max) {
    size_t i = 0;
    while (tok->pos < tok->len && i < max - 1) {
        char c = peek(tok);
        if (isalnum((unsigned char)c) || c == '-' || c == '_') {
            out[i++] = (char)tolower((unsigned char)c);
            advance(tok);
        } else break;
    }
    out[i] = '\0';
}

static void parse_attr_value(eb_tokenizer_t *tok, char *out, size_t max) {
    char quote = peek(tok);
    size_t i = 0;
    if (quote == '"' || quote == '\'') {
        advance(tok);
        while (tok->pos < tok->len && i < max - 1) {
            char c = advance(tok);
            if (c == quote) break;
            out[i++] = c;
        }
    } else {
        while (tok->pos < tok->len && i < max - 1) {
            char c = peek(tok);
            if (isspace((unsigned char)c) || c == '>' || c == '/') break;
            out[i++] = advance(tok);
        }
    }
    out[i] = '\0';
}

static void parse_attributes(eb_tokenizer_t *tok, eb_html_token_t *token) {
    while (tok->pos < tok->len && token->attr_count < EB_DOM_MAX_ATTRS) {
        skip_whitespace(tok);
        char c = peek(tok);
        if (c == '>' || c == '/' || c == '\0') break;
        char name[EB_DOM_MAX_TAG_LEN] = {0};
        size_t ni = 0;
        while (tok->pos < tok->len && ni < EB_DOM_MAX_TAG_LEN - 1) {
            c = peek(tok);
            if (c == '=' || c == '>' || c == '/' || isspace((unsigned char)c)) break;
            name[ni++] = (char)tolower((unsigned char)advance(tok));
        }
        name[ni] = '\0';
        if (ni == 0) { advance(tok); continue; }
        skip_whitespace(tok);
        char value[EB_DOM_MAX_ATTR_LEN] = {0};
        if (peek(tok) == '=') {
            advance(tok);
            skip_whitespace(tok);
            parse_attr_value(tok, value, EB_DOM_MAX_ATTR_LEN);
        }
        strncpy(token->attrs[token->attr_count].name, name, EB_DOM_MAX_TAG_LEN - 1);
        strncpy(token->attrs[token->attr_count].value, value, EB_DOM_MAX_ATTR_LEN - 1);
        token->attr_count++;
    }
}

eb_html_token_t eb_tokenizer_next(eb_tokenizer_t *tok) {
    eb_html_token_t token;
    memset(&token, 0, sizeof(token));
    if (!tok || tok->pos >= tok->len) { token.type = EB_TOK_EOF; return token; }

    if (peek(tok) == '<') {
        advance(tok);
        if (starts_with(tok, "!DOCTYPE") || starts_with(tok, "!doctype")) {
            token.type = EB_TOK_DOCTYPE;
            while (tok->pos < tok->len && advance(tok) != '>') {}
            return token;
        }
        if (starts_with(tok, "!--")) {
            tok->pos += 3;
            token.type = EB_TOK_COMMENT;
            size_t ti = 0;
            while (tok->pos < tok->len && ti < EB_DOM_MAX_TEXT_LEN - 1) {
                if (starts_with(tok, "-->")) { tok->pos += 3; break; }
                token.text[ti++] = advance(tok);
            }
            token.text[ti] = '\0';
            return token;
        }
        if (peek(tok) == '/') {
            advance(tok);
            token.type = EB_TOK_END_TAG;
            parse_tag_name(tok, token.tag, EB_DOM_MAX_TAG_LEN);
            while (tok->pos < tok->len && advance(tok) != '>') {}
            return token;
        }
        token.type = EB_TOK_START_TAG;
        parse_tag_name(tok, token.tag, EB_DOM_MAX_TAG_LEN);
        parse_attributes(tok, &token);
        skip_whitespace(tok);
        if (peek(tok) == '/') { advance(tok); token.type = EB_TOK_SELF_CLOSING_TAG; }
        if (peek(tok) == '>') advance(tok);
        if (token.type == EB_TOK_START_TAG && eb_html_is_void_element(token.tag))
            token.type = EB_TOK_SELF_CLOSING_TAG;
        return token;
    }

    token.type = EB_TOK_TEXT;
    size_t ti = 0;
    while (tok->pos < tok->len && ti < EB_DOM_MAX_TEXT_LEN - 1) {
        if (peek(tok) == '<') break;
        token.text[ti++] = advance(tok);
    }
    token.text[ti] = '\0';
    return token;
}

static void parse_raw_text_content(eb_tokenizer_t *tok, const char *tag, eb_dom_node_t *parent) {
    char end_tag[EB_DOM_MAX_TAG_LEN + 4];
    snprintf(end_tag, sizeof(end_tag), "</%s>", tag);
    size_t end_len = strlen(end_tag);
    char buf[EB_DOM_MAX_TEXT_LEN] = {0};
    size_t bi = 0;
    while (tok->pos < tok->len && bi < EB_DOM_MAX_TEXT_LEN - 1) {
        if (tok->pos + end_len <= tok->len &&
            strncasecmp(tok->input + tok->pos, end_tag, end_len) == 0) {
            tok->pos += end_len;
            break;
        }
        buf[bi++] = tok->input[tok->pos++];
    }
    buf[bi] = '\0';
    if (bi > 0) {
        eb_dom_node_t *txt = eb_dom_create_text(buf);
        if (txt) eb_dom_append_child(parent, txt);
    }
}

eb_dom_node_t *eb_html_parse(const char *html, size_t len) {
    if (!html || len == 0) return NULL;
    eb_dom_node_t *doc = eb_dom_create_document();
    if (!doc) return NULL;
    eb_tokenizer_t tok;
    eb_tokenizer_init(&tok, html, len);
    eb_dom_node_t *stack[256];
    int stack_top = 0;
    stack[stack_top] = doc;

    while (1) {
        eb_html_token_t token = eb_tokenizer_next(&tok);
        if (token.type == EB_TOK_EOF) break;
        eb_dom_node_t *current = stack[stack_top];
        switch (token.type) {
            case EB_TOK_DOCTYPE: break;
            case EB_TOK_START_TAG: {
                eb_dom_node_t *el = eb_dom_create_element(token.tag);
                if (!el) break;
                for (int i = 0; i < token.attr_count; i++)
                    eb_dom_set_attribute(el, token.attrs[i].name, token.attrs[i].value);
                eb_dom_append_child(current, el);
                if (is_raw_text_element(token.tag))
                    parse_raw_text_content(&tok, token.tag, el);
                else if (stack_top < 255)
                    stack[++stack_top] = el;
                break;
            }
            case EB_TOK_SELF_CLOSING_TAG: {
                eb_dom_node_t *el = eb_dom_create_element(token.tag);
                if (!el) break;
                for (int i = 0; i < token.attr_count; i++)
                    eb_dom_set_attribute(el, token.attrs[i].name, token.attrs[i].value);
                eb_dom_append_child(current, el);
                break;
            }
            case EB_TOK_END_TAG: {
                for (int i = stack_top; i > 0; i--) {
                    if (strcmp(stack[i]->tag, token.tag) == 0) { stack_top = i - 1; break; }
                }
                break;
            }
            case EB_TOK_TEXT: {
                bool only_space = true;
                for (size_t i = 0; token.text[i]; i++) {
                    if (!isspace((unsigned char)token.text[i])) { only_space = false; break; }
                }
                if (!only_space) {
                    eb_dom_node_t *txt = eb_dom_create_text(token.text);
                    if (txt) eb_dom_append_child(current, txt);
                }
                break;
            }
            case EB_TOK_COMMENT: {
                eb_dom_node_t *cmt = eb_dom_create_comment(token.text);
                if (cmt) eb_dom_append_child(current, cmt);
                break;
            }
            default: break;
        }
    }
    return doc;
}
