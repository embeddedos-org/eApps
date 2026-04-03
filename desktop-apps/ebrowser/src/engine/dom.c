// SPDX-License-Identifier: MIT
#include "eBrowser/dom.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

static eb_dom_node_t *alloc_node(eb_node_type_t type) {
    eb_dom_node_t *n = (eb_dom_node_t *)calloc(1, sizeof(eb_dom_node_t));
    if (n) n->type = type;
    return n;
}

eb_dom_node_t *eb_dom_create_document(void) {
    eb_dom_node_t *n = alloc_node(EB_NODE_DOCUMENT);
    if (n) strncpy(n->tag, "#document", EB_DOM_MAX_TAG_LEN - 1);
    return n;
}

eb_dom_node_t *eb_dom_create_element(const char *tag) {
    if (!tag) return NULL;
    eb_dom_node_t *n = alloc_node(EB_NODE_ELEMENT);
    if (n) strncpy(n->tag, tag, EB_DOM_MAX_TAG_LEN - 1);
    return n;
}

eb_dom_node_t *eb_dom_create_text(const char *text) {
    if (!text) return NULL;
    eb_dom_node_t *n = alloc_node(EB_NODE_TEXT);
    if (n) {
        strncpy(n->tag, "#text", EB_DOM_MAX_TAG_LEN - 1);
        strncpy(n->text, text, EB_DOM_MAX_TEXT_LEN - 1);
    }
    return n;
}

eb_dom_node_t *eb_dom_create_comment(const char *text) {
    if (!text) return NULL;
    eb_dom_node_t *n = alloc_node(EB_NODE_COMMENT);
    if (n) {
        strncpy(n->tag, "#comment", EB_DOM_MAX_TAG_LEN - 1);
        strncpy(n->text, text, EB_DOM_MAX_TEXT_LEN - 1);
    }
    return n;
}

bool eb_dom_append_child(eb_dom_node_t *parent, eb_dom_node_t *child) {
    if (!parent || !child) return false;
    if (parent->child_count >= EB_DOM_MAX_CHILDREN) return false;
    parent->children[parent->child_count++] = child;
    child->parent = parent;
    return true;
}

bool eb_dom_remove_child(eb_dom_node_t *parent, eb_dom_node_t *child) {
    if (!parent || !child) return false;
    for (int i = 0; i < parent->child_count; i++) {
        if (parent->children[i] == child) {
            for (int j = i; j < parent->child_count - 1; j++) {
                parent->children[j] = parent->children[j + 1];
            }
            parent->children[--parent->child_count] = NULL;
            child->parent = NULL;
            return true;
        }
    }
    return false;
}

bool eb_dom_insert_before(eb_dom_node_t *parent, eb_dom_node_t *new_child,
                           eb_dom_node_t *ref_child) {
    if (!parent || !new_child) return false;
    if (!ref_child) return eb_dom_append_child(parent, new_child);
    if (parent->child_count >= EB_DOM_MAX_CHILDREN) return false;

    for (int i = 0; i < parent->child_count; i++) {
        if (parent->children[i] == ref_child) {
            for (int j = parent->child_count; j > i; j--) {
                parent->children[j] = parent->children[j - 1];
            }
            parent->children[i] = new_child;
            parent->child_count++;
            new_child->parent = parent;
            return true;
        }
    }
    return false;
}

bool eb_dom_replace_child(eb_dom_node_t *parent, eb_dom_node_t *new_child,
                           eb_dom_node_t *old_child) {
    if (!parent || !new_child || !old_child) return false;
    for (int i = 0; i < parent->child_count; i++) {
        if (parent->children[i] == old_child) {
            parent->children[i] = new_child;
            new_child->parent = parent;
            old_child->parent = NULL;
            return true;
        }
    }
    return false;
}

bool eb_dom_set_attribute(eb_dom_node_t *node, const char *name, const char *value) {
    if (!node || !name) return false;
    for (int i = 0; i < node->attr_count; i++) {
        if (strcmp(node->attrs[i].name, name) == 0) {
            if (value) strncpy(node->attrs[i].value, value, EB_DOM_MAX_ATTR_LEN - 1);
            else node->attrs[i].value[0] = '\0';
            return true;
        }
    }
    if (node->attr_count >= EB_DOM_MAX_ATTRS) return false;
    strncpy(node->attrs[node->attr_count].name, name, EB_DOM_MAX_TAG_LEN - 1);
    if (value) strncpy(node->attrs[node->attr_count].value, value, EB_DOM_MAX_ATTR_LEN - 1);
    node->attr_count++;
    return true;
}

const char *eb_dom_get_attribute(const eb_dom_node_t *node, const char *name) {
    if (!node || !name) return NULL;
    for (int i = 0; i < node->attr_count; i++) {
        if (strcmp(node->attrs[i].name, name) == 0) return node->attrs[i].value;
    }
    return NULL;
}

bool eb_dom_has_attribute(const eb_dom_node_t *node, const char *name) {
    return eb_dom_get_attribute(node, name) != NULL;
}

bool eb_dom_remove_attribute(eb_dom_node_t *node, const char *name) {
    if (!node || !name) return false;
    for (int i = 0; i < node->attr_count; i++) {
        if (strcmp(node->attrs[i].name, name) == 0) {
            for (int j = i; j < node->attr_count - 1; j++) {
                node->attrs[j] = node->attrs[j + 1];
            }
            memset(&node->attrs[--node->attr_count], 0, sizeof(eb_attribute_t));
            return true;
        }
    }
    return false;
}

eb_dom_node_t *eb_dom_find_by_tag(eb_dom_node_t *root, const char *tag) {
    if (!root || !tag) return NULL;
    if (root->type == EB_NODE_ELEMENT && strcmp(root->tag, tag) == 0) return root;
    for (int i = 0; i < root->child_count; i++) {
        eb_dom_node_t *found = eb_dom_find_by_tag(root->children[i], tag);
        if (found) return found;
    }
    return NULL;
}

eb_dom_node_t *eb_dom_find_by_id(eb_dom_node_t *root, const char *id) {
    if (!root || !id) return NULL;
    const char *node_id = eb_dom_get_attribute(root, "id");
    if (node_id && strcmp(node_id, id) == 0) return root;
    for (int i = 0; i < root->child_count; i++) {
        eb_dom_node_t *found = eb_dom_find_by_id(root->children[i], id);
        if (found) return found;
    }
    return NULL;
}

void eb_dom_find_all_by_tag(eb_dom_node_t *root, const char *tag,
                             eb_dom_node_list_t *results) {
    if (!root || !tag || !results) return;
    if (root->type == EB_NODE_ELEMENT && strcmp(root->tag, tag) == 0) {
        if (results->count < EB_DOM_MAX_RESULTS) {
            results->nodes[results->count++] = root;
        }
    }
    for (int i = 0; i < root->child_count; i++) {
        eb_dom_find_all_by_tag(root->children[i], tag, results);
    }
}

static bool has_class(const char *class_attr, const char *cls) {
    if (!class_attr || !cls) return false;
    size_t cls_len = strlen(cls);
    const char *p = class_attr;
    while (*p) {
        while (*p == ' ') p++;
        if (*p == '\0') break;
        const char *start = p;
        while (*p && *p != ' ') p++;
        size_t word_len = (size_t)(p - start);
        if (word_len == cls_len && strncmp(start, cls, cls_len) == 0) return true;
    }
    return false;
}

void eb_dom_find_all_by_class(eb_dom_node_t *root, const char *class_name,
                               eb_dom_node_list_t *results) {
    if (!root || !class_name || !results) return;
    if (root->type == EB_NODE_ELEMENT) {
        const char *cls = eb_dom_get_attribute(root, "class");
        if (has_class(cls, class_name)) {
            if (results->count < EB_DOM_MAX_RESULTS) {
                results->nodes[results->count++] = root;
            }
        }
    }
    for (int i = 0; i < root->child_count; i++) {
        eb_dom_find_all_by_class(root->children[i], class_name, results);
    }
}

bool eb_dom_class_list_contains(const eb_dom_node_t *node, const char *cls) {
    if (!node || !cls) return false;
    const char *class_attr = eb_dom_get_attribute(node, "class");
    return has_class(class_attr, cls);
}

bool eb_dom_class_list_add(eb_dom_node_t *node, const char *cls) {
    if (!node || !cls) return false;
    if (eb_dom_class_list_contains(node, cls)) return true;

    const char *existing = eb_dom_get_attribute(node, "class");
    char buf[EB_DOM_MAX_ATTR_LEN] = {0};
    if (existing && existing[0]) {
        snprintf(buf, sizeof(buf), "%s %s", existing, cls);
    } else {
        strncpy(buf, cls, sizeof(buf) - 1);
    }
    return eb_dom_set_attribute(node, "class", buf);
}

bool eb_dom_class_list_remove(eb_dom_node_t *node, const char *cls) {
    if (!node || !cls) return false;
    const char *existing = eb_dom_get_attribute(node, "class");
    if (!existing) return false;

    char buf[EB_DOM_MAX_ATTR_LEN] = {0};
    size_t cls_len = strlen(cls);
    size_t buf_pos = 0;
    const char *p = existing;
    bool first = true;

    while (*p) {
        while (*p == ' ') p++;
        if (*p == '\0') break;
        const char *start = p;
        while (*p && *p != ' ') p++;
        size_t word_len = (size_t)(p - start);

        if (word_len == cls_len && strncmp(start, cls, cls_len) == 0) continue;
        if (!first && buf_pos < sizeof(buf) - 1) buf[buf_pos++] = ' ';
        size_t copy_len = word_len;
        if (buf_pos + copy_len >= sizeof(buf) - 1) copy_len = sizeof(buf) - 1 - buf_pos;
        memcpy(buf + buf_pos, start, copy_len);
        buf_pos += copy_len;
        first = false;
    }
    buf[buf_pos] = '\0';
    return eb_dom_set_attribute(node, "class", buf);
}

bool eb_dom_class_list_toggle(eb_dom_node_t *node, const char *cls) {
    if (!node || !cls) return false;
    if (eb_dom_class_list_contains(node, cls)) {
        eb_dom_class_list_remove(node, cls);
        return false;
    }
    eb_dom_class_list_add(node, cls);
    return true;
}

bool eb_dom_set_inner_text(eb_dom_node_t *node, const char *text) {
    if (!node) return false;
    for (int i = 0; i < node->child_count; i++) {
        eb_dom_destroy(node->children[i]);
        node->children[i] = NULL;
    }
    node->child_count = 0;
    if (text && text[0]) {
        eb_dom_node_t *txt = eb_dom_create_text(text);
        if (!txt) return false;
        return eb_dom_append_child(node, txt);
    }
    return true;
}

const char *eb_dom_get_inner_text(const eb_dom_node_t *node, char *buf, size_t buf_size) {
    if (!node || !buf || buf_size == 0) return NULL;
    buf[0] = '\0';
    size_t pos = 0;

    for (int i = 0; i < node->child_count && pos < buf_size - 1; i++) {
        const eb_dom_node_t *child = node->children[i];
        if (child->type == EB_NODE_TEXT) {
            size_t tlen = strlen(child->text);
            if (pos + tlen >= buf_size - 1) tlen = buf_size - 1 - pos;
            memcpy(buf + pos, child->text, tlen);
            pos += tlen;
        } else if (child->type == EB_NODE_ELEMENT) {
            char sub[EB_DOM_MAX_TEXT_LEN];
            eb_dom_get_inner_text(child, sub, sizeof(sub));
            size_t slen = strlen(sub);
            if (pos + slen >= buf_size - 1) slen = buf_size - 1 - pos;
            memcpy(buf + pos, sub, slen);
            pos += slen;
        }
    }
    buf[pos] = '\0';
    return buf;
}

eb_dom_node_t *eb_dom_clone_node(const eb_dom_node_t *node, bool deep) {
    if (!node) return NULL;
    eb_dom_node_t *clone = alloc_node(node->type);
    if (!clone) return NULL;

    memcpy(clone->tag, node->tag, EB_DOM_MAX_TAG_LEN);
    memcpy(clone->text, node->text, EB_DOM_MAX_TEXT_LEN);
    clone->attr_count = node->attr_count;
    for (int i = 0; i < node->attr_count; i++) {
        clone->attrs[i] = node->attrs[i];
    }

    if (deep) {
        for (int i = 0; i < node->child_count; i++) {
            eb_dom_node_t *child_clone = eb_dom_clone_node(node->children[i], true);
            if (child_clone) {
                eb_dom_append_child(clone, child_clone);
            }
        }
    }
    return clone;
}

void eb_dom_destroy(eb_dom_node_t *node) {
    if (!node) return;
    for (int i = 0; i < node->child_count; i++) {
        eb_dom_destroy(node->children[i]);
    }
    free(node);
}

void eb_dom_print(const eb_dom_node_t *node, int depth) {
    if (!node) return;
    for (int i = 0; i < depth; i++) printf("  ");
    switch (node->type) {
        case EB_NODE_DOCUMENT: printf("[DOCUMENT]\n"); break;
        case EB_NODE_ELEMENT:
            printf("<%s", node->tag);
            for (int i = 0; i < node->attr_count; i++)
                printf(" %s=\"%s\"", node->attrs[i].name, node->attrs[i].value);
            printf(">\n");
            break;
        case EB_NODE_TEXT: printf("\"%s\"\n", node->text); break;
        case EB_NODE_COMMENT: printf("<!-- %s -->\n", node->text); break;
    }
    for (int i = 0; i < node->child_count; i++) {
        eb_dom_print(node->children[i], depth + 1);
    }
}
