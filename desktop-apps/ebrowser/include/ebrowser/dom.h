// SPDX-License-Identifier: MIT
#ifndef eBrowser_DOM_H
#define eBrowser_DOM_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#define EB_DOM_MAX_CHILDREN   64
#define EB_DOM_MAX_ATTRS      16
#define EB_DOM_MAX_TAG_LEN    32
#define EB_DOM_MAX_ATTR_LEN   256
#define EB_DOM_MAX_TEXT_LEN   4096
#define EB_DOM_MAX_RESULTS    128

typedef enum {
    EB_NODE_DOCUMENT,
    EB_NODE_ELEMENT,
    EB_NODE_TEXT,
    EB_NODE_COMMENT
} eb_node_type_t;

typedef struct {
    char name[EB_DOM_MAX_TAG_LEN];
    char value[EB_DOM_MAX_ATTR_LEN];
} eb_attribute_t;

typedef struct eb_dom_node eb_dom_node_t;

struct eb_dom_node {
    eb_node_type_t      type;
    char                tag[EB_DOM_MAX_TAG_LEN];
    char                text[EB_DOM_MAX_TEXT_LEN];
    eb_attribute_t      attrs[EB_DOM_MAX_ATTRS];
    int                 attr_count;
    eb_dom_node_t      *parent;
    eb_dom_node_t      *children[EB_DOM_MAX_CHILDREN];
    int                 child_count;
};

typedef struct {
    eb_dom_node_t *nodes[EB_DOM_MAX_RESULTS];
    int            count;
} eb_dom_node_list_t;

eb_dom_node_t *eb_dom_create_document(void);
eb_dom_node_t *eb_dom_create_element(const char *tag);
eb_dom_node_t *eb_dom_create_text(const char *text);
eb_dom_node_t *eb_dom_create_comment(const char *text);

bool           eb_dom_append_child(eb_dom_node_t *parent, eb_dom_node_t *child);
bool           eb_dom_remove_child(eb_dom_node_t *parent, eb_dom_node_t *child);
bool           eb_dom_insert_before(eb_dom_node_t *parent, eb_dom_node_t *new_child,
                                     eb_dom_node_t *ref_child);
bool           eb_dom_replace_child(eb_dom_node_t *parent, eb_dom_node_t *new_child,
                                     eb_dom_node_t *old_child);

bool           eb_dom_set_attribute(eb_dom_node_t *node, const char *name, const char *value);
const char    *eb_dom_get_attribute(const eb_dom_node_t *node, const char *name);
bool           eb_dom_has_attribute(const eb_dom_node_t *node, const char *name);
bool           eb_dom_remove_attribute(eb_dom_node_t *node, const char *name);

eb_dom_node_t *eb_dom_find_by_tag(eb_dom_node_t *root, const char *tag);
eb_dom_node_t *eb_dom_find_by_id(eb_dom_node_t *root, const char *id);
void           eb_dom_find_all_by_tag(eb_dom_node_t *root, const char *tag,
                                       eb_dom_node_list_t *results);
void           eb_dom_find_all_by_class(eb_dom_node_t *root, const char *class_name,
                                         eb_dom_node_list_t *results);

bool           eb_dom_class_list_contains(const eb_dom_node_t *node, const char *cls);
bool           eb_dom_class_list_add(eb_dom_node_t *node, const char *cls);
bool           eb_dom_class_list_remove(eb_dom_node_t *node, const char *cls);
bool           eb_dom_class_list_toggle(eb_dom_node_t *node, const char *cls);

bool           eb_dom_set_inner_text(eb_dom_node_t *node, const char *text);
const char    *eb_dom_get_inner_text(const eb_dom_node_t *node, char *buf, size_t buf_size);

eb_dom_node_t *eb_dom_clone_node(const eb_dom_node_t *node, bool deep);

void           eb_dom_destroy(eb_dom_node_t *node);
void           eb_dom_print(const eb_dom_node_t *node, int depth);

#endif
