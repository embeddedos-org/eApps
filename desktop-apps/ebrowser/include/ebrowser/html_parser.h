// SPDX-License-Identifier: MIT
#ifndef eBrowser_HTML_PARSER_H
#define eBrowser_HTML_PARSER_H

#include "eBrowser/dom.h"

typedef enum {
    EB_TOK_DOCTYPE,
    EB_TOK_START_TAG,
    EB_TOK_END_TAG,
    EB_TOK_SELF_CLOSING_TAG,
    EB_TOK_TEXT,
    EB_TOK_COMMENT,
    EB_TOK_EOF
} eb_token_type_t;

typedef struct {
    eb_token_type_t  type;
    char             tag[EB_DOM_MAX_TAG_LEN];
    char             text[EB_DOM_MAX_TEXT_LEN];
    eb_attribute_t   attrs[EB_DOM_MAX_ATTRS];
    int              attr_count;
} eb_html_token_t;

typedef struct {
    const char *input;
    size_t      pos;
    size_t      len;
} eb_tokenizer_t;

void             eb_tokenizer_init(eb_tokenizer_t *tok, const char *html, size_t len);
eb_html_token_t  eb_tokenizer_next(eb_tokenizer_t *tok);

eb_dom_node_t   *eb_html_parse(const char *html, size_t len);

bool             eb_html_is_void_element(const char *tag);

#endif /* eBrowser_HTML_PARSER_H */
