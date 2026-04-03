// SPDX-License-Identifier: MIT
// Comprehensive HTML parser tests for eBrowser web browser
#include "eBrowser/html_parser.h"
#include <stdio.h>
#include <string.h>
#include <ctype.h>

static int s_pass = 0, s_fail = 0;
#define TEST(name) static void name(void)
#define RUN(name) do { printf("  %s... ", #name); name(); printf("PASS\n"); s_pass++; } while(0)
#define ASSERT(cond) do { if(!(cond)) { printf("FAIL: %s:%d: %s\n", __FILE__, __LINE__, #cond); s_fail++; return; } } while(0)

// --- Tokenizer ---

TEST(test_tokenizer_empty) {
    eb_tokenizer_t tok;
    eb_tokenizer_init(&tok, "", 0);
    eb_html_token_t t = eb_tokenizer_next(&tok);
    ASSERT(t.type == EB_TOK_EOF);
}

TEST(test_tokenizer_text_only) {
    const char *html = "Hello World";
    eb_tokenizer_t tok;
    eb_tokenizer_init(&tok, html, strlen(html));
    eb_html_token_t t = eb_tokenizer_next(&tok);
    ASSERT(t.type == EB_TOK_TEXT);
    ASSERT(strcmp(t.text, "Hello World") == 0);
    t = eb_tokenizer_next(&tok);
    ASSERT(t.type == EB_TOK_EOF);
}

TEST(test_tokenizer_start_tag) {
    const char *html = "<div>";
    eb_tokenizer_t tok;
    eb_tokenizer_init(&tok, html, strlen(html));
    eb_html_token_t t = eb_tokenizer_next(&tok);
    ASSERT(t.type == EB_TOK_START_TAG);
    ASSERT(strcmp(t.tag, "div") == 0);
}

TEST(test_tokenizer_end_tag) {
    const char *html = "</div>";
    eb_tokenizer_t tok;
    eb_tokenizer_init(&tok, html, strlen(html));
    eb_html_token_t t = eb_tokenizer_next(&tok);
    ASSERT(t.type == EB_TOK_END_TAG);
    ASSERT(strcmp(t.tag, "div") == 0);
}

TEST(test_tokenizer_self_closing) {
    const char *html = "<br/>";
    eb_tokenizer_t tok;
    eb_tokenizer_init(&tok, html, strlen(html));
    eb_html_token_t t = eb_tokenizer_next(&tok);
    ASSERT(t.type == EB_TOK_SELF_CLOSING_TAG);
    ASSERT(strcmp(t.tag, "br") == 0);
}

TEST(test_tokenizer_void_auto_close) {
    const char *html = "<br>";
    eb_tokenizer_t tok;
    eb_tokenizer_init(&tok, html, strlen(html));
    eb_html_token_t t = eb_tokenizer_next(&tok);
    ASSERT(t.type == EB_TOK_SELF_CLOSING_TAG);
    ASSERT(strcmp(t.tag, "br") == 0);
}

TEST(test_tokenizer_doctype) {
    const char *html = "<!DOCTYPE html>";
    eb_tokenizer_t tok;
    eb_tokenizer_init(&tok, html, strlen(html));
    eb_html_token_t t = eb_tokenizer_next(&tok);
    ASSERT(t.type == EB_TOK_DOCTYPE);
}

TEST(test_tokenizer_comment) {
    const char *html = "<!-- This is a comment -->";
    eb_tokenizer_t tok;
    eb_tokenizer_init(&tok, html, strlen(html));
    eb_html_token_t t = eb_tokenizer_next(&tok);
    ASSERT(t.type == EB_TOK_COMMENT);
    ASSERT(strstr(t.text, "This is a comment") != NULL);
}

TEST(test_tokenizer_attributes_double_quotes) {
    const char *html = "<a href=\"https://example.com\" class=\"link\">";
    eb_tokenizer_t tok;
    eb_tokenizer_init(&tok, html, strlen(html));
    eb_html_token_t t = eb_tokenizer_next(&tok);
    ASSERT(t.type == EB_TOK_START_TAG);
    ASSERT(strcmp(t.tag, "a") == 0);
    ASSERT(t.attr_count == 2);
    ASSERT(strcmp(t.attrs[0].name, "href") == 0);
    ASSERT(strcmp(t.attrs[0].value, "https://example.com") == 0);
    ASSERT(strcmp(t.attrs[1].name, "class") == 0);
    ASSERT(strcmp(t.attrs[1].value, "link") == 0);
}

TEST(test_tokenizer_attributes_single_quotes) {
    const char *html = "<a href='https://test.org'>";
    eb_tokenizer_t tok;
    eb_tokenizer_init(&tok, html, strlen(html));
    eb_html_token_t t = eb_tokenizer_next(&tok);
    ASSERT(t.type == EB_TOK_START_TAG);
    ASSERT(strcmp(t.attrs[0].value, "https://test.org") == 0);
}

TEST(test_tokenizer_case_insensitive_tags) {
    const char *html = "<DIV><P>text</P></DIV>";
    eb_tokenizer_t tok;
    eb_tokenizer_init(&tok, html, strlen(html));
    eb_html_token_t t = eb_tokenizer_next(&tok);
    ASSERT(strcmp(t.tag, "div") == 0);
    t = eb_tokenizer_next(&tok);
    ASSERT(strcmp(t.tag, "p") == 0);
}

// --- Void Elements ---

TEST(test_void_elements_list) {
    const char *voids[] = {"area","base","br","col","embed","hr","img","input","link","meta","param","source","track","wbr",NULL};
    for (int i = 0; voids[i]; i++) {
        ASSERT(eb_html_is_void_element(voids[i]) == true);
    }
}

TEST(test_non_void_elements) {
    const char *non_voids[] = {"div","span","p","a","table","body","html","head","form","button","select",NULL};
    for (int i = 0; non_voids[i]; i++) {
        ASSERT(eb_html_is_void_element(non_voids[i]) == false);
    }
}

// --- Full Parsing ---

TEST(test_parse_null) {
    ASSERT(eb_html_parse(NULL, 0) == NULL);
    ASSERT(eb_html_parse("", 0) == NULL);
}

TEST(test_parse_minimal_html) {
    const char *html = "<html><body><p>Hello</p></body></html>";
    eb_dom_node_t *doc = eb_html_parse(html, strlen(html));
    ASSERT(doc != NULL);
    ASSERT(doc->type == EB_NODE_DOCUMENT);
    eb_dom_node_t *p = eb_dom_find_by_tag(doc, "p");
    ASSERT(p != NULL);
    ASSERT(p->child_count == 1);
    ASSERT(p->children[0]->type == EB_NODE_TEXT);
    ASSERT(strstr(p->children[0]->text, "Hello") != NULL);
    eb_dom_destroy(doc);
}

TEST(test_parse_full_html5_page) {
    const char *html =
        "<!DOCTYPE html>"
        "<html lang=\"en\">"
        "<head>"
        "<meta charset=\"UTF-8\">"
        "<title>Test Page</title>"
        "</head>"
        "<body>"
        "<h1>Welcome</h1>"
        "<p>This is a <strong>test</strong> page.</p>"
        "<img src=\"logo.png\" alt=\"Logo\">"
        "<a href=\"/about\">About Us</a>"
        "</body>"
        "</html>";
    eb_dom_node_t *doc = eb_html_parse(html, strlen(html));
    ASSERT(doc != NULL);

    eb_dom_node_t *title = eb_dom_find_by_tag(doc, "title");
    ASSERT(title != NULL);
    ASSERT(title->child_count == 1);
    ASSERT(strstr(title->children[0]->text, "Test Page") != NULL);

    eb_dom_node_t *h1 = eb_dom_find_by_tag(doc, "h1");
    ASSERT(h1 != NULL);

    eb_dom_node_t *img = eb_dom_find_by_tag(doc, "img");
    ASSERT(img != NULL);
    ASSERT(strcmp(eb_dom_get_attribute(img, "src"), "logo.png") == 0);
    ASSERT(strcmp(eb_dom_get_attribute(img, "alt"), "Logo") == 0);

    eb_dom_node_t *a = eb_dom_find_by_tag(doc, "a");
    ASSERT(a != NULL);
    ASSERT(strcmp(eb_dom_get_attribute(a, "href"), "/about") == 0);

    eb_dom_node_t *strong = eb_dom_find_by_tag(doc, "strong");
    ASSERT(strong != NULL);

    eb_dom_destroy(doc);
}

TEST(test_parse_nested_divs) {
    const char *html =
        "<div id=\"outer\">"
        "  <div id=\"middle\">"
        "    <div id=\"inner\">"
        "      <span>Deep content</span>"
        "    </div>"
        "  </div>"
        "</div>";
    eb_dom_node_t *doc = eb_html_parse(html, strlen(html));
    ASSERT(doc != NULL);
    eb_dom_node_t *outer = eb_dom_find_by_id(doc, "outer");
    ASSERT(outer != NULL);
    eb_dom_node_t *inner = eb_dom_find_by_id(doc, "inner");
    ASSERT(inner != NULL);
    eb_dom_node_t *span = eb_dom_find_by_tag(doc, "span");
    ASSERT(span != NULL);
    ASSERT(span->parent != NULL);
    eb_dom_destroy(doc);
}

TEST(test_parse_void_elements_in_context) {
    const char *html =
        "<p>Line 1<br>Line 2<br>Line 3</p>"
        "<hr>"
        "<img src=\"test.png\">";
    eb_dom_node_t *doc = eb_html_parse(html, strlen(html));
    ASSERT(doc != NULL);
    eb_dom_node_t *p = eb_dom_find_by_tag(doc, "p");
    ASSERT(p != NULL);
    ASSERT(p->child_count == 5);
    ASSERT(strcmp(p->children[1]->tag, "br") == 0);
    ASSERT(strcmp(p->children[3]->tag, "br") == 0);
    eb_dom_node_t *hr = eb_dom_find_by_tag(doc, "hr");
    ASSERT(hr != NULL);
    eb_dom_node_t *img = eb_dom_find_by_tag(doc, "img");
    ASSERT(img != NULL);
    eb_dom_destroy(doc);
}

TEST(test_parse_list) {
    const char *html =
        "<ul>"
        "  <li>Item 1</li>"
        "  <li>Item 2</li>"
        "  <li>Item 3</li>"
        "</ul>";
    eb_dom_node_t *doc = eb_html_parse(html, strlen(html));
    ASSERT(doc != NULL);
    eb_dom_node_t *ul = eb_dom_find_by_tag(doc, "ul");
    ASSERT(ul != NULL);
    int li_count = 0;
    for (int i = 0; i < ul->child_count; i++) {
        if (ul->children[i]->type == EB_NODE_ELEMENT && strcmp(ul->children[i]->tag, "li") == 0)
            li_count++;
    }
    ASSERT(li_count == 3);
    eb_dom_destroy(doc);
}

TEST(test_parse_table) {
    const char *html =
        "<table>"
        "<tr><th>Name</th><th>Age</th></tr>"
        "<tr><td>Alice</td><td>30</td></tr>"
        "<tr><td>Bob</td><td>25</td></tr>"
        "</table>";
    eb_dom_node_t *doc = eb_html_parse(html, strlen(html));
    ASSERT(doc != NULL);
    eb_dom_node_t *table = eb_dom_find_by_tag(doc, "table");
    ASSERT(table != NULL);
    eb_dom_node_t *th = eb_dom_find_by_tag(doc, "th");
    ASSERT(th != NULL);
    eb_dom_node_t *td = eb_dom_find_by_tag(doc, "td");
    ASSERT(td != NULL);
    eb_dom_destroy(doc);
}

TEST(test_parse_form) {
    const char *html =
        "<form action=\"/submit\" method=\"POST\">"
        "<input type=\"text\" name=\"user\" placeholder=\"Username\">"
        "<input type=\"password\" name=\"pass\">"
        "<button type=\"submit\">Login</button>"
        "</form>";
    eb_dom_node_t *doc = eb_html_parse(html, strlen(html));
    ASSERT(doc != NULL);
    eb_dom_node_t *form = eb_dom_find_by_tag(doc, "form");
    ASSERT(form != NULL);
    ASSERT(strcmp(eb_dom_get_attribute(form, "action"), "/submit") == 0);
    ASSERT(strcmp(eb_dom_get_attribute(form, "method"), "post") == 0 ||
           strcmp(eb_dom_get_attribute(form, "method"), "POST") == 0);
    eb_dom_destroy(doc);
}

TEST(test_parse_comments_preserved) {
    const char *html = "<div><!-- nav --><nav>Menu</nav><!-- footer --><footer>End</footer></div>";
    eb_dom_node_t *doc = eb_html_parse(html, strlen(html));
    ASSERT(doc != NULL);
    eb_dom_node_t *div = eb_dom_find_by_tag(doc, "div");
    ASSERT(div != NULL);
    int comment_count = 0;
    for (int i = 0; i < div->child_count; i++) {
        if (div->children[i]->type == EB_NODE_COMMENT) comment_count++;
    }
    ASSERT(comment_count == 2);
    eb_dom_destroy(doc);
}

TEST(test_parse_inline_styles) {
    const char *html = "<div style=\"color:red;background:#fff;margin:10px\">Styled</div>";
    eb_dom_node_t *doc = eb_html_parse(html, strlen(html));
    ASSERT(doc != NULL);
    eb_dom_node_t *div = eb_dom_find_by_tag(doc, "div");
    ASSERT(div != NULL);
    const char *style = eb_dom_get_attribute(div, "style");
    ASSERT(style != NULL);
    ASSERT(strstr(style, "color:red") != NULL);
    eb_dom_destroy(doc);
}

TEST(test_parse_data_attributes) {
    const char *html = "<div data-id=\"42\" data-name=\"test\" data-active=\"true\">Data</div>";
    eb_dom_node_t *doc = eb_html_parse(html, strlen(html));
    ASSERT(doc != NULL);
    eb_dom_node_t *div = eb_dom_find_by_tag(doc, "div");
    ASSERT(div != NULL);
    ASSERT(strcmp(eb_dom_get_attribute(div, "data-id"), "42") == 0);
    ASSERT(strcmp(eb_dom_get_attribute(div, "data-name"), "test") == 0);
    ASSERT(strcmp(eb_dom_get_attribute(div, "data-active"), "true") == 0);
    eb_dom_destroy(doc);
}

TEST(test_parse_whitespace_handling) {
    const char *html = "<p>   Hello   World   </p>";
    eb_dom_node_t *doc = eb_html_parse(html, strlen(html));
    ASSERT(doc != NULL);
    eb_dom_node_t *p = eb_dom_find_by_tag(doc, "p");
    ASSERT(p != NULL);
    ASSERT(p->child_count >= 1);
    eb_dom_destroy(doc);
}

TEST(test_parse_empty_tags) {
    const char *html = "<div></div><span></span><p></p>";
    eb_dom_node_t *doc = eb_html_parse(html, strlen(html));
    ASSERT(doc != NULL);
    eb_dom_node_t *div = eb_dom_find_by_tag(doc, "div");
    ASSERT(div != NULL);
    ASSERT(div->child_count == 0);
    eb_dom_destroy(doc);
}

TEST(test_parse_semantic_html5) {
    const char *html =
        "<header><nav><a href=\"/\">Home</a></nav></header>"
        "<main><article><section><h2>Title</h2><p>Content</p></section></article></main>"
        "<footer><p>Footer</p></footer>";
    eb_dom_node_t *doc = eb_html_parse(html, strlen(html));
    ASSERT(doc != NULL);
    ASSERT(eb_dom_find_by_tag(doc, "header") != NULL);
    ASSERT(eb_dom_find_by_tag(doc, "nav") != NULL);
    ASSERT(eb_dom_find_by_tag(doc, "main") != NULL);
    ASSERT(eb_dom_find_by_tag(doc, "article") != NULL);
    ASSERT(eb_dom_find_by_tag(doc, "section") != NULL);
    ASSERT(eb_dom_find_by_tag(doc, "footer") != NULL);
    eb_dom_destroy(doc);
}

int main(void) {
    printf("=== HTML Parser Tests ===\n");
    RUN(test_tokenizer_empty);
    RUN(test_tokenizer_text_only);
    RUN(test_tokenizer_start_tag);
    RUN(test_tokenizer_end_tag);
    RUN(test_tokenizer_self_closing);
    RUN(test_tokenizer_void_auto_close);
    RUN(test_tokenizer_doctype);
    RUN(test_tokenizer_comment);
    RUN(test_tokenizer_attributes_double_quotes);
    RUN(test_tokenizer_attributes_single_quotes);
    RUN(test_tokenizer_case_insensitive_tags);
    RUN(test_void_elements_list);
    RUN(test_non_void_elements);
    RUN(test_parse_null);
    RUN(test_parse_minimal_html);
    RUN(test_parse_full_html5_page);
    RUN(test_parse_nested_divs);
    RUN(test_parse_void_elements_in_context);
    RUN(test_parse_list);
    RUN(test_parse_table);
    RUN(test_parse_form);
    RUN(test_parse_comments_preserved);
    RUN(test_parse_inline_styles);
    RUN(test_parse_data_attributes);
    RUN(test_parse_whitespace_handling);
    RUN(test_parse_empty_tags);
    RUN(test_parse_semantic_html5);
    printf("\nResults: %d passed, %d failed\n", s_pass, s_fail);
    return s_fail > 0 ? 1 : 0;
}
