// SPDX-License-Identifier: MIT
// Comprehensive DOM tree tests for eBrowser web browser
#include "eBrowser/dom.h"
#include <stdio.h>
#include <string.h>

static int s_pass = 0, s_fail = 0;
#define TEST(name) static void name(void)
#define RUN(name) do { printf("  %s... ", #name); name(); printf("PASS\n"); s_pass++; } while(0)
#define ASSERT(cond) do { if(!(cond)) { printf("FAIL: %s:%d: %s\n", __FILE__, __LINE__, #cond); s_fail++; return; } } while(0)

// --- Node Creation ---

TEST(test_create_document) {
    eb_dom_node_t *doc = eb_dom_create_document();
    ASSERT(doc != NULL);
    ASSERT(doc->type == EB_NODE_DOCUMENT);
    ASSERT(strcmp(doc->tag, "#document") == 0);
    ASSERT(doc->child_count == 0);
    ASSERT(doc->parent == NULL);
    eb_dom_destroy(doc);
}

TEST(test_create_element) {
    eb_dom_node_t *el = eb_dom_create_element("div");
    ASSERT(el != NULL);
    ASSERT(el->type == EB_NODE_ELEMENT);
    ASSERT(strcmp(el->tag, "div") == 0);
    ASSERT(el->child_count == 0);
    ASSERT(el->attr_count == 0);
    eb_dom_destroy(el);
}

TEST(test_create_element_null) {
    eb_dom_node_t *el = eb_dom_create_element(NULL);
    ASSERT(el == NULL);
}

TEST(test_create_text) {
    eb_dom_node_t *txt = eb_dom_create_text("Hello, World!");
    ASSERT(txt != NULL);
    ASSERT(txt->type == EB_NODE_TEXT);
    ASSERT(strcmp(txt->tag, "#text") == 0);
    ASSERT(strcmp(txt->text, "Hello, World!") == 0);
    eb_dom_destroy(txt);
}

TEST(test_create_text_null) {
    eb_dom_node_t *txt = eb_dom_create_text(NULL);
    ASSERT(txt == NULL);
}

TEST(test_create_comment) {
    eb_dom_node_t *cmt = eb_dom_create_comment("This is a comment");
    ASSERT(cmt != NULL);
    ASSERT(cmt->type == EB_NODE_COMMENT);
    ASSERT(strcmp(cmt->tag, "#comment") == 0);
    ASSERT(strcmp(cmt->text, "This is a comment") == 0);
    eb_dom_destroy(cmt);
}

TEST(test_create_comment_null) {
    eb_dom_node_t *cmt = eb_dom_create_comment(NULL);
    ASSERT(cmt == NULL);
}

// --- Tree Operations ---

TEST(test_append_child_basic) {
    eb_dom_node_t *parent = eb_dom_create_element("div");
    eb_dom_node_t *child = eb_dom_create_element("p");
    ASSERT(eb_dom_append_child(parent, child) == true);
    ASSERT(parent->child_count == 1);
    ASSERT(parent->children[0] == child);
    ASSERT(child->parent == parent);
    eb_dom_destroy(parent);
}

TEST(test_append_multiple_children) {
    eb_dom_node_t *parent = eb_dom_create_element("ul");
    for (int i = 0; i < 5; i++) {
        eb_dom_node_t *li = eb_dom_create_element("li");
        ASSERT(eb_dom_append_child(parent, li) == true);
    }
    ASSERT(parent->child_count == 5);
    eb_dom_destroy(parent);
}

TEST(test_append_child_null_parent) {
    eb_dom_node_t *child = eb_dom_create_element("p");
    ASSERT(eb_dom_append_child(NULL, child) == false);
    eb_dom_destroy(child);
}

TEST(test_append_child_null_child) {
    eb_dom_node_t *parent = eb_dom_create_element("div");
    ASSERT(eb_dom_append_child(parent, NULL) == false);
    eb_dom_destroy(parent);
}

TEST(test_append_child_max_children) {
    eb_dom_node_t *parent = eb_dom_create_element("div");
    for (int i = 0; i < EB_DOM_MAX_CHILDREN; i++) {
        eb_dom_node_t *child = eb_dom_create_element("span");
        ASSERT(eb_dom_append_child(parent, child) == true);
    }
    eb_dom_node_t *overflow = eb_dom_create_element("span");
    ASSERT(eb_dom_append_child(parent, overflow) == false);
    eb_dom_destroy(overflow);
    eb_dom_destroy(parent);
}

TEST(test_deep_nesting) {
    eb_dom_node_t *root = eb_dom_create_element("div");
    eb_dom_node_t *current = root;
    for (int i = 0; i < 20; i++) {
        eb_dom_node_t *child = eb_dom_create_element("div");
        eb_dom_append_child(current, child);
        current = child;
    }
    eb_dom_node_t *leaf = eb_dom_create_text("deep text");
    eb_dom_append_child(current, leaf);
    ASSERT(leaf->parent == current);
    ASSERT(strcmp(leaf->text, "deep text") == 0);
    eb_dom_destroy(root);
}

// --- Attributes ---

TEST(test_set_attribute) {
    eb_dom_node_t *el = eb_dom_create_element("a");
    ASSERT(eb_dom_set_attribute(el, "href", "https://example.com") == true);
    ASSERT(el->attr_count == 1);
    ASSERT(strcmp(el->attrs[0].name, "href") == 0);
    ASSERT(strcmp(el->attrs[0].value, "https://example.com") == 0);
    eb_dom_destroy(el);
}

TEST(test_set_attribute_overwrite) {
    eb_dom_node_t *el = eb_dom_create_element("input");
    eb_dom_set_attribute(el, "type", "text");
    ASSERT(el->attr_count == 1);
    eb_dom_set_attribute(el, "type", "password");
    ASSERT(el->attr_count == 1);
    ASSERT(strcmp(el->attrs[0].value, "password") == 0);
    eb_dom_destroy(el);
}

TEST(test_set_multiple_attributes) {
    eb_dom_node_t *el = eb_dom_create_element("img");
    eb_dom_set_attribute(el, "src", "logo.png");
    eb_dom_set_attribute(el, "alt", "Logo");
    eb_dom_set_attribute(el, "width", "100");
    eb_dom_set_attribute(el, "height", "50");
    ASSERT(el->attr_count == 4);
    ASSERT(strcmp(eb_dom_get_attribute(el, "src"), "logo.png") == 0);
    ASSERT(strcmp(eb_dom_get_attribute(el, "alt"), "Logo") == 0);
    ASSERT(strcmp(eb_dom_get_attribute(el, "width"), "100") == 0);
    ASSERT(strcmp(eb_dom_get_attribute(el, "height"), "50") == 0);
    eb_dom_destroy(el);
}

TEST(test_set_attribute_null_value) {
    eb_dom_node_t *el = eb_dom_create_element("input");
    eb_dom_set_attribute(el, "disabled", NULL);
    ASSERT(el->attr_count == 1);
    ASSERT(strcmp(el->attrs[0].name, "disabled") == 0);
    ASSERT(el->attrs[0].value[0] == '\0');
    eb_dom_destroy(el);
}

TEST(test_set_attribute_null_node) {
    ASSERT(eb_dom_set_attribute(NULL, "id", "test") == false);
}

TEST(test_set_attribute_null_name) {
    eb_dom_node_t *el = eb_dom_create_element("div");
    ASSERT(eb_dom_set_attribute(el, NULL, "value") == false);
    eb_dom_destroy(el);
}

TEST(test_set_attribute_max) {
    eb_dom_node_t *el = eb_dom_create_element("div");
    char name[16];
    for (int i = 0; i < EB_DOM_MAX_ATTRS; i++) {
        snprintf(name, sizeof(name), "attr%d", i);
        ASSERT(eb_dom_set_attribute(el, name, "val") == true);
    }
    ASSERT(eb_dom_set_attribute(el, "overflow", "val") == false);
    eb_dom_destroy(el);
}

TEST(test_get_attribute_nonexistent) {
    eb_dom_node_t *el = eb_dom_create_element("div");
    ASSERT(eb_dom_get_attribute(el, "nonexistent") == NULL);
    eb_dom_destroy(el);
}

TEST(test_has_attribute) {
    eb_dom_node_t *el = eb_dom_create_element("a");
    eb_dom_set_attribute(el, "href", "#");
    ASSERT(eb_dom_has_attribute(el, "href") == true);
    ASSERT(eb_dom_has_attribute(el, "class") == false);
    eb_dom_destroy(el);
}

// --- Search ---

TEST(test_find_by_tag_basic) {
    eb_dom_node_t *doc = eb_dom_create_document();
    eb_dom_node_t *html = eb_dom_create_element("html");
    eb_dom_node_t *body = eb_dom_create_element("body");
    eb_dom_node_t *p = eb_dom_create_element("p");
    eb_dom_append_child(doc, html);
    eb_dom_append_child(html, body);
    eb_dom_append_child(body, p);
    ASSERT(eb_dom_find_by_tag(doc, "p") == p);
    ASSERT(eb_dom_find_by_tag(doc, "body") == body);
    ASSERT(eb_dom_find_by_tag(doc, "html") == html);
    eb_dom_destroy(doc);
}

TEST(test_find_by_tag_not_found) {
    eb_dom_node_t *doc = eb_dom_create_document();
    eb_dom_node_t *div = eb_dom_create_element("div");
    eb_dom_append_child(doc, div);
    ASSERT(eb_dom_find_by_tag(doc, "span") == NULL);
    eb_dom_destroy(doc);
}

TEST(test_find_by_tag_null) {
    ASSERT(eb_dom_find_by_tag(NULL, "div") == NULL);
    eb_dom_node_t *doc = eb_dom_create_document();
    ASSERT(eb_dom_find_by_tag(doc, NULL) == NULL);
    eb_dom_destroy(doc);
}

TEST(test_find_by_id_basic) {
    eb_dom_node_t *doc = eb_dom_create_document();
    eb_dom_node_t *div = eb_dom_create_element("div");
    eb_dom_set_attribute(div, "id", "main-content");
    eb_dom_append_child(doc, div);
    ASSERT(eb_dom_find_by_id(doc, "main-content") == div);
    eb_dom_destroy(doc);
}

TEST(test_find_by_id_deep) {
    eb_dom_node_t *doc = eb_dom_create_document();
    eb_dom_node_t *div1 = eb_dom_create_element("div");
    eb_dom_node_t *div2 = eb_dom_create_element("div");
    eb_dom_node_t *span = eb_dom_create_element("span");
    eb_dom_set_attribute(span, "id", "deep-target");
    eb_dom_append_child(doc, div1);
    eb_dom_append_child(div1, div2);
    eb_dom_append_child(div2, span);
    ASSERT(eb_dom_find_by_id(doc, "deep-target") == span);
    eb_dom_destroy(doc);
}

TEST(test_find_by_id_not_found) {
    eb_dom_node_t *doc = eb_dom_create_document();
    eb_dom_node_t *div = eb_dom_create_element("div");
    eb_dom_set_attribute(div, "id", "test");
    eb_dom_append_child(doc, div);
    ASSERT(eb_dom_find_by_id(doc, "missing-id") == NULL);
    eb_dom_destroy(doc);
}

// --- Mixed Content ---

TEST(test_mixed_content_tree) {
    eb_dom_node_t *doc = eb_dom_create_document();
    eb_dom_node_t *p = eb_dom_create_element("p");
    eb_dom_node_t *txt1 = eb_dom_create_text("Hello ");
    eb_dom_node_t *b = eb_dom_create_element("b");
    eb_dom_node_t *txt2 = eb_dom_create_text("world");
    eb_dom_node_t *txt3 = eb_dom_create_text("!");
    eb_dom_append_child(doc, p);
    eb_dom_append_child(p, txt1);
    eb_dom_append_child(p, b);
    eb_dom_append_child(b, txt2);
    eb_dom_append_child(p, txt3);
    ASSERT(p->child_count == 3);
    ASSERT(p->children[0]->type == EB_NODE_TEXT);
    ASSERT(p->children[1]->type == EB_NODE_ELEMENT);
    ASSERT(p->children[2]->type == EB_NODE_TEXT);
    ASSERT(b->child_count == 1);
    eb_dom_destroy(doc);
}

int main(void) {
    printf("=== DOM Tests ===\n");
    RUN(test_create_document);
    RUN(test_create_element);
    RUN(test_create_element_null);
    RUN(test_create_text);
    RUN(test_create_text_null);
    RUN(test_create_comment);
    RUN(test_create_comment_null);
    RUN(test_append_child_basic);
    RUN(test_append_multiple_children);
    RUN(test_append_child_null_parent);
    RUN(test_append_child_null_child);
    RUN(test_append_child_max_children);
    RUN(test_deep_nesting);
    RUN(test_set_attribute);
    RUN(test_set_attribute_overwrite);
    RUN(test_set_multiple_attributes);
    RUN(test_set_attribute_null_value);
    RUN(test_set_attribute_null_node);
    RUN(test_set_attribute_null_name);
    RUN(test_set_attribute_max);
    RUN(test_get_attribute_nonexistent);
    RUN(test_has_attribute);
    RUN(test_find_by_tag_basic);
    RUN(test_find_by_tag_not_found);
    RUN(test_find_by_tag_null);
    RUN(test_find_by_id_basic);
    RUN(test_find_by_id_deep);
    RUN(test_find_by_id_not_found);
    RUN(test_mixed_content_tree);
    printf("\nResults: %d passed, %d failed\n", s_pass, s_fail);
    return s_fail > 0 ? 1 : 0;
}
