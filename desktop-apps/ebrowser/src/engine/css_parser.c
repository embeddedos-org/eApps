// SPDX-License-Identifier: MIT
#include "eBrowser/css_parser.h"
#include "eBrowser/compat.h"
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <stdio.h>

void eb_css_init_stylesheet(eb_stylesheet_t *ss) {
    if (!ss) return;
    memset(ss, 0, sizeof(eb_stylesheet_t));
}

static void trim(char *s) {
    if (!s) return;
    char *start = s;
    while (*start && isspace((unsigned char)*start)) start++;
    if (start != s) memmove(s, start, strlen(start) + 1);
    size_t len = strlen(s);
    while (len > 0 && isspace((unsigned char)s[len - 1])) s[--len] = '\0';
}

eb_color_t eb_css_parse_color(const char *str) {
    eb_color_t c = {0, 0, 0, 255};
    if (!str) return c;
    while (isspace((unsigned char)*str)) str++;
    if (*str == '#') {
        str++;
        unsigned int hex = 0;
        size_t len = 0;
        const char *p = str;
        while (isxdigit((unsigned char)*p)) { p++; len++; }
        sscanf(str, "%x", &hex);
        if (len == 6) { c.r = (uint8_t)((hex >> 16) & 0xFF); c.g = (uint8_t)((hex >> 8) & 0xFF); c.b = (uint8_t)(hex & 0xFF); }
        else if (len == 3) { c.r = (uint8_t)(((hex >> 8) & 0xF) * 17); c.g = (uint8_t)(((hex >> 4) & 0xF) * 17); c.b = (uint8_t)((hex & 0xF) * 17); }
        return c;
    }
    if (strncasecmp(str, "rgb(", 4) == 0) {
        int r, g, b;
        if (sscanf(str, "rgb(%d,%d,%d)", &r, &g, &b) == 3 || sscanf(str, "rgb( %d , %d , %d )", &r, &g, &b) == 3) {
            c.r = (uint8_t)(r < 0 ? 0 : r > 255 ? 255 : r); c.g = (uint8_t)(g < 0 ? 0 : g > 255 ? 255 : g); c.b = (uint8_t)(b < 0 ? 0 : b > 255 ? 255 : b);
        }
        return c;
    }
    struct { const char *name; uint8_t r, g, b; } named[] = {
        {"black",0,0,0},{"white",255,255,255},{"red",255,0,0},{"green",0,128,0},{"blue",0,0,255},{"yellow",255,255,0},
        {"gray",128,128,128},{"grey",128,128,128},{"silver",192,192,192},{"orange",255,165,0},{"purple",128,0,128},
        {"navy",0,0,128},{"teal",0,128,128},{"maroon",128,0,0},{"aqua",0,255,255},{"lime",0,255,0},{"transparent",0,0,0},{NULL,0,0,0}
    };
    for (int i = 0; named[i].name; i++) {
        if (strcasecmp(str, named[i].name) == 0) { c.r = named[i].r; c.g = named[i].g; c.b = named[i].b; if (strcasecmp(str,"transparent")==0) c.a=0; return c; }
    }
    return c;
}

int eb_css_parse_length(const char *str) { if (!str) return 0; while (isspace((unsigned char)*str)) str++; return atoi(str); }

int eb_css_compute_specificity(const char *selector) {
    if (!selector) return 0;
    int ids=0, classes=0, elements=0;
    const char *p = selector;
    while (*p) {
        if (*p=='#') { ids++; p++; while (*p&&(isalnum((unsigned char)*p)||*p=='-'||*p=='_')) p++; }
        else if (*p=='.') { classes++; p++; while (*p&&(isalnum((unsigned char)*p)||*p=='-'||*p=='_')) p++; }
        else if (*p=='[') { classes++; while (*p&&*p!=']') p++; if (*p) p++; }
        else if (*p==':') { classes++; p++; while (*p&&(isalnum((unsigned char)*p)||*p=='-')) p++; }
        else if (*p=='>'||*p=='+'||*p=='~'||*p=='*') { p++; }
        else if (isalpha((unsigned char)*p)) { elements++; while (*p&&(isalnum((unsigned char)*p)||*p=='-')) p++; }
        else { p++; }
    }
    return (ids*100)+(classes*10)+elements;
}

eb_computed_style_t eb_css_default_style(const char *tag) {
    eb_computed_style_t s;
    memset(&s, 0, sizeof(s));
    s.color = (eb_color_t){0,0,0,255}; s.background_color = (eb_color_t){0,0,0,0};
    s.display = EB_DISPLAY_INLINE; s.position = EB_POSITION_STATIC; s.css_float = EB_FLOAT_NONE;
    s.overflow = EB_OVERFLOW_VISIBLE; s.font_size = 16; s.font_weight = EB_FONT_WEIGHT_NORMAL;
    s.font_style = EB_FONT_STYLE_NORMAL; s.text_align = EB_TEXT_ALIGN_LEFT;
    s.text_decoration = EB_TEXT_DECORATION_NONE; s.text_transform = EB_TEXT_TRANSFORM_NONE;
    s.list_style = EB_LIST_STYLE_NONE; s.width_auto = true; s.height_auto = true; s.opacity = 255;
    s.flex_direction = EB_FLEX_DIRECTION_ROW; s.justify_content = EB_JUSTIFY_FLEX_START; s.align_items = EB_ALIGN_STRETCH;
    if (!tag) return s;
    const char *block_tags[] = {"html","body","div","p","h1","h2","h3","h4","h5","h6","ul","ol","section","article",
        "header","footer","nav","main","aside","form","blockquote","pre","hr","figure","figcaption","details","summary","fieldset","address",NULL};
    for (int i = 0; block_tags[i]; i++) { if (strcasecmp(tag, block_tags[i]) == 0) { s.display = EB_DISPLAY_BLOCK; break; } }
    if (strcasecmp(tag,"li")==0) { s.display=EB_DISPLAY_LIST_ITEM; s.margin.left=40; s.list_style=EB_LIST_STYLE_DISC; }
    else if (strcasecmp(tag,"table")==0) { s.display=EB_DISPLAY_TABLE; s.border_width=1; }
    else if (strcasecmp(tag,"tr")==0) { s.display=EB_DISPLAY_TABLE_ROW; }
    else if (strcasecmp(tag,"td")==0||strcasecmp(tag,"th")==0) { s.display=EB_DISPLAY_TABLE_CELL; s.padding=(eb_edges_t){1,4,1,4}; }
    else if (strcasecmp(tag,"h1")==0) { s.font_size=32; s.font_weight=EB_FONT_WEIGHT_BOLD; s.margin.top=21; s.margin.bottom=21; }
    else if (strcasecmp(tag,"h2")==0) { s.font_size=24; s.font_weight=EB_FONT_WEIGHT_BOLD; s.margin.top=19; s.margin.bottom=19; }
    else if (strcasecmp(tag,"h3")==0) { s.font_size=19; s.font_weight=EB_FONT_WEIGHT_BOLD; s.margin.top=18; s.margin.bottom=18; }
    else if (strcasecmp(tag,"h4")==0) { s.font_size=16; s.font_weight=EB_FONT_WEIGHT_BOLD; s.margin.top=21; s.margin.bottom=21; }
    else if (strcasecmp(tag,"h5")==0) { s.font_size=13; s.font_weight=EB_FONT_WEIGHT_BOLD; }
    else if (strcasecmp(tag,"h6")==0) { s.font_size=11; s.font_weight=EB_FONT_WEIGHT_BOLD; }
    else if (strcasecmp(tag,"p")==0) { s.margin.top=16; s.margin.bottom=16; }
    else if (strcasecmp(tag,"b")==0||strcasecmp(tag,"strong")==0) { s.font_weight=EB_FONT_WEIGHT_BOLD; }
    else if (strcasecmp(tag,"i")==0||strcasecmp(tag,"em")==0) { s.font_style=EB_FONT_STYLE_ITALIC; }
    else if (strcasecmp(tag,"u")==0) { s.text_decoration=EB_TEXT_DECORATION_UNDERLINE; }
    else if (strcasecmp(tag,"s")==0||strcasecmp(tag,"del")==0) { s.text_decoration=EB_TEXT_DECORATION_LINE_THROUGH; }
    else if (strcasecmp(tag,"a")==0) { s.color=(eb_color_t){0,0,238,255}; s.text_decoration=EB_TEXT_DECORATION_UNDERLINE; }
    else if (strcasecmp(tag,"hr")==0) { s.border_width=1; s.border_color=(eb_color_t){128,128,128,255}; s.margin.top=8; s.margin.bottom=8; }
    else if (strcasecmp(tag,"body")==0) { s.margin.top=8; s.margin.right=8; s.margin.bottom=8; s.margin.left=8; }
    else if (strcasecmp(tag,"pre")==0||strcasecmp(tag,"code")==0) { s.margin.top=16; s.margin.bottom=16; }
    else if (strcasecmp(tag,"blockquote")==0) { s.margin.top=16; s.margin.bottom=16; s.margin.left=40; s.margin.right=40; }
    else if (strcasecmp(tag,"th")==0) { s.font_weight=EB_FONT_WEIGHT_BOLD; s.text_align=EB_TEXT_ALIGN_CENTER; }
    else if (strcasecmp(tag,"ol")==0) { s.list_style=EB_LIST_STYLE_DECIMAL; s.margin.top=16; s.margin.bottom=16; }
    else if (strcasecmp(tag,"ul")==0) { s.list_style=EB_LIST_STYLE_DISC; s.margin.top=16; s.margin.bottom=16; }
    else if (strcasecmp(tag,"mark")==0) { s.background_color=(eb_color_t){255,255,0,255}; }
    return s;
}

static void apply_property(eb_computed_style_t *s, const char *name, const char *value) {
    if (!s||!name||!value) return;
    if (strcmp(name,"color")==0) s->color=eb_css_parse_color(value);
    else if (strcmp(name,"background-color")==0||strcmp(name,"background")==0) s->background_color=eb_css_parse_color(value);
    else if (strcmp(name,"font-size")==0) s->font_size=eb_css_parse_length(value);
    else if (strcmp(name,"font-weight")==0) s->font_weight=(strcasecmp(value,"bold")==0||atoi(value)>=700)?EB_FONT_WEIGHT_BOLD:EB_FONT_WEIGHT_NORMAL;
    else if (strcmp(name,"font-style")==0) s->font_style=(strcasecmp(value,"italic")==0)?EB_FONT_STYLE_ITALIC:EB_FONT_STYLE_NORMAL;
    else if (strcmp(name,"text-align")==0) {
        if (strcasecmp(value,"center")==0) s->text_align=EB_TEXT_ALIGN_CENTER;
        else if (strcasecmp(value,"right")==0) s->text_align=EB_TEXT_ALIGN_RIGHT;
        else if (strcasecmp(value,"justify")==0) s->text_align=EB_TEXT_ALIGN_JUSTIFY;
        else s->text_align=EB_TEXT_ALIGN_LEFT;
    }
    else if (strcmp(name,"text-decoration")==0) {
        if (strcasecmp(value,"underline")==0) s->text_decoration=EB_TEXT_DECORATION_UNDERLINE;
        else if (strcasecmp(value,"line-through")==0) s->text_decoration=EB_TEXT_DECORATION_LINE_THROUGH;
        else if (strcasecmp(value,"overline")==0) s->text_decoration=EB_TEXT_DECORATION_OVERLINE;
        else s->text_decoration=EB_TEXT_DECORATION_NONE;
    }
    else if (strcmp(name,"text-transform")==0) {
        if (strcasecmp(value,"uppercase")==0) s->text_transform=EB_TEXT_TRANSFORM_UPPERCASE;
        else if (strcasecmp(value,"lowercase")==0) s->text_transform=EB_TEXT_TRANSFORM_LOWERCASE;
        else if (strcasecmp(value,"capitalize")==0) s->text_transform=EB_TEXT_TRANSFORM_CAPITALIZE;
        else s->text_transform=EB_TEXT_TRANSFORM_NONE;
    }
    else if (strcmp(name,"display")==0) {
        if (strcasecmp(value,"block")==0) s->display=EB_DISPLAY_BLOCK;
        else if (strcasecmp(value,"inline")==0) s->display=EB_DISPLAY_INLINE;
        else if (strcasecmp(value,"inline-block")==0) s->display=EB_DISPLAY_INLINE_BLOCK;
        else if (strcasecmp(value,"none")==0) s->display=EB_DISPLAY_NONE;
        else if (strcasecmp(value,"flex")==0) s->display=EB_DISPLAY_FLEX;
        else if (strcasecmp(value,"table")==0) s->display=EB_DISPLAY_TABLE;
        else if (strcasecmp(value,"table-row")==0) s->display=EB_DISPLAY_TABLE_ROW;
        else if (strcasecmp(value,"table-cell")==0) s->display=EB_DISPLAY_TABLE_CELL;
        else if (strcasecmp(value,"list-item")==0) s->display=EB_DISPLAY_LIST_ITEM;
    }
    else if (strcmp(name,"position")==0) {
        if (strcasecmp(value,"relative")==0) s->position=EB_POSITION_RELATIVE;
        else if (strcasecmp(value,"absolute")==0) s->position=EB_POSITION_ABSOLUTE;
        else if (strcasecmp(value,"fixed")==0) s->position=EB_POSITION_FIXED;
        else s->position=EB_POSITION_STATIC;
    }
    else if (strcmp(name,"float")==0) { if (strcasecmp(value,"left")==0) s->css_float=EB_FLOAT_LEFT; else if (strcasecmp(value,"right")==0) s->css_float=EB_FLOAT_RIGHT; else s->css_float=EB_FLOAT_NONE; }
    else if (strcmp(name,"overflow")==0) { if (strcasecmp(value,"hidden")==0) s->overflow=EB_OVERFLOW_HIDDEN; else if (strcasecmp(value,"scroll")==0) s->overflow=EB_OVERFLOW_SCROLL; else if (strcasecmp(value,"auto")==0) s->overflow=EB_OVERFLOW_AUTO; else s->overflow=EB_OVERFLOW_VISIBLE; }
    else if (strcmp(name,"z-index")==0) s->z_index=atoi(value);
    else if (strcmp(name,"opacity")==0) { float f=(float)atof(value); s->opacity=(int)(f<0?0:f>1.0f?255:f*255); }
    else if (strcmp(name,"margin")==0) { int v=eb_css_parse_length(value); s->margin=(eb_edges_t){v,v,v,v}; }
    else if (strcmp(name,"margin-top")==0) s->margin.top=eb_css_parse_length(value);
    else if (strcmp(name,"margin-right")==0) s->margin.right=eb_css_parse_length(value);
    else if (strcmp(name,"margin-bottom")==0) s->margin.bottom=eb_css_parse_length(value);
    else if (strcmp(name,"margin-left")==0) s->margin.left=eb_css_parse_length(value);
    else if (strcmp(name,"padding")==0) { int v=eb_css_parse_length(value); s->padding=(eb_edges_t){v,v,v,v}; }
    else if (strcmp(name,"padding-top")==0) s->padding.top=eb_css_parse_length(value);
    else if (strcmp(name,"padding-right")==0) s->padding.right=eb_css_parse_length(value);
    else if (strcmp(name,"padding-bottom")==0) s->padding.bottom=eb_css_parse_length(value);
    else if (strcmp(name,"padding-left")==0) s->padding.left=eb_css_parse_length(value);
    else if (strcmp(name,"width")==0) { if (strcasecmp(value,"auto")==0) s->width_auto=true; else { s->width=eb_css_parse_length(value); s->width_auto=false; } }
    else if (strcmp(name,"height")==0) { if (strcasecmp(value,"auto")==0) s->height_auto=true; else { s->height=eb_css_parse_length(value); s->height_auto=false; } }
    else if (strcmp(name,"border-width")==0) s->border_width=eb_css_parse_length(value);
    else if (strcmp(name,"border-color")==0) s->border_color=eb_css_parse_color(value);
    else if (strcmp(name,"border-radius")==0) s->border_radius=eb_css_parse_length(value);
    else if (strcmp(name,"line-height")==0) s->line_height=eb_css_parse_length(value);
    else if (strcmp(name,"list-style")==0||strcmp(name,"list-style-type")==0) {
        if (strcasecmp(value,"none")==0) s->list_style=EB_LIST_STYLE_NONE; else if (strcasecmp(value,"disc")==0) s->list_style=EB_LIST_STYLE_DISC;
        else if (strcasecmp(value,"circle")==0) s->list_style=EB_LIST_STYLE_CIRCLE; else if (strcasecmp(value,"square")==0) s->list_style=EB_LIST_STYLE_SQUARE;
        else if (strcasecmp(value,"decimal")==0) s->list_style=EB_LIST_STYLE_DECIMAL;
    }
    else if (strcmp(name,"flex-direction")==0) { if (strcasecmp(value,"column")==0) s->flex_direction=EB_FLEX_DIRECTION_COLUMN; else if (strcasecmp(value,"row-reverse")==0) s->flex_direction=EB_FLEX_DIRECTION_ROW_REVERSE; else if (strcasecmp(value,"column-reverse")==0) s->flex_direction=EB_FLEX_DIRECTION_COLUMN_REVERSE; else s->flex_direction=EB_FLEX_DIRECTION_ROW; }
    else if (strcmp(name,"justify-content")==0) { if (strcasecmp(value,"center")==0) s->justify_content=EB_JUSTIFY_CENTER; else if (strcasecmp(value,"flex-end")==0) s->justify_content=EB_JUSTIFY_FLEX_END; else if (strcasecmp(value,"space-between")==0) s->justify_content=EB_JUSTIFY_SPACE_BETWEEN; else if (strcasecmp(value,"space-around")==0) s->justify_content=EB_JUSTIFY_SPACE_AROUND; else s->justify_content=EB_JUSTIFY_FLEX_START; }
    else if (strcmp(name,"align-items")==0) { if (strcasecmp(value,"center")==0) s->align_items=EB_ALIGN_CENTER; else if (strcasecmp(value,"flex-start")==0) s->align_items=EB_ALIGN_FLEX_START; else if (strcasecmp(value,"flex-end")==0) s->align_items=EB_ALIGN_FLEX_END; else if (strcasecmp(value,"baseline")==0) s->align_items=EB_ALIGN_BASELINE; else s->align_items=EB_ALIGN_STRETCH; }
    else if (strcmp(name,"flex-grow")==0) s->flex_grow=atoi(value);
    else if (strcmp(name,"gap")==0) s->gap=eb_css_parse_length(value);
}

bool eb_css_parse(eb_stylesheet_t *ss, const char *css, size_t len) {
    if (!ss||!css||len==0) return false;
    size_t pos = 0;
    while (pos < len && ss->rule_count < EB_CSS_MAX_RULES) {
        while (pos < len && isspace((unsigned char)css[pos])) pos++;
        if (pos >= len) break;
        if (css[pos]=='/'&&pos+1<len&&css[pos+1]=='*') { pos+=2; while (pos+1<len&&!(css[pos]=='*'&&css[pos+1]=='/')) pos++; if (pos+1<len) pos+=2; continue; }
        if (css[pos]=='@') { while (pos<len&&css[pos]!='{') pos++; if (pos<len) { pos++; int depth=1; while (pos<len&&depth>0) { if (css[pos]=='{') depth++; else if (css[pos]=='}') depth--; pos++; } } continue; }
        char sel[EB_CSS_MAX_SELECTOR]={0}; size_t si=0;
        while (pos<len&&css[pos]!='{'&&si<EB_CSS_MAX_SELECTOR-1) sel[si++]=css[pos++];
        sel[si]='\0'; trim(sel); if (pos>=len||css[pos]!='{') break; pos++;
        eb_css_rule_t *rule = &ss->rules[ss->rule_count];
        strncpy(rule->selector, sel, EB_CSS_MAX_SELECTOR-1);
        rule->specificity = eb_css_compute_specificity(sel);
        while (pos<len&&css[pos]!='}'&&rule->prop_count<EB_CSS_MAX_PROPERTIES) {
            while (pos<len&&isspace((unsigned char)css[pos])) pos++;
            if (pos>=len||css[pos]=='}') break;
            char name[EB_CSS_MAX_VALUE]={0}; size_t ni=0;
            while (pos<len&&css[pos]!=':'&&css[pos]!='}'&&ni<EB_CSS_MAX_VALUE-1) name[ni++]=css[pos++];
            name[ni]='\0'; trim(name); if (pos>=len||css[pos]!=':') break; pos++;
            char value[EB_CSS_MAX_VALUE]={0}; size_t vi=0;
            while (pos<len&&css[pos]!=';'&&css[pos]!='}'&&vi<EB_CSS_MAX_VALUE-1) value[vi++]=css[pos++];
            value[vi]='\0'; trim(value); if (pos<len&&css[pos]==';') pos++;
            if (name[0]&&value[0]) { strncpy(rule->properties[rule->prop_count].name,name,EB_CSS_MAX_VALUE-1); strncpy(rule->properties[rule->prop_count].value,value,EB_CSS_MAX_VALUE-1); rule->prop_count++; }
        }
        if (pos<len&&css[pos]=='}') pos++;
        ss->rule_count++;
    }
    return true;
}

static bool selector_matches(const char *selector, const char *tag, const char *id, const char *class_name) {
    if (!selector||!tag) return false;
    const char *last = selector+strlen(selector)-1;
    while (last>selector&&isspace((unsigned char)*last)) last--;
    const char *start = last;
    while (start>selector&&!isspace((unsigned char)*(start-1))&&*(start-1)!='>') start--;
    char part[EB_CSS_MAX_SELECTOR]={0};
    size_t plen = (size_t)(last-start+1);
    if (plen>=EB_CSS_MAX_SELECTOR) plen=EB_CSS_MAX_SELECTOR-1;
    strncpy(part, start, plen);
    const char *p = part; bool has_constraint = false;
    while (*p) {
        if (*p=='#') { has_constraint=true; p++; char id_buf[EB_CSS_MAX_TAG_LEN]={0}; size_t i=0; while (*p&&*p!='.'&&*p!='#'&&i<EB_CSS_MAX_TAG_LEN-1) id_buf[i++]=*p++; if (!id||strcmp(id_buf,id)!=0) return false; }
        else if (*p=='.') { has_constraint=true; p++; char cls[EB_CSS_MAX_TAG_LEN]={0}; size_t i=0; while (*p&&*p!='.'&&*p!='#'&&i<EB_CSS_MAX_TAG_LEN-1) cls[i++]=*p++; if (!class_name||strstr(class_name,cls)==NULL) return false; }
        else if (*p=='*') { has_constraint=true; p++; }
        else if (isalpha((unsigned char)*p)) { has_constraint=true; char tb[EB_CSS_MAX_TAG_LEN]={0}; size_t i=0; while (*p&&isalnum((unsigned char)*p)&&i<EB_CSS_MAX_TAG_LEN-1) tb[i++]=(char)tolower((unsigned char)*p++); if (strcasecmp(tb,tag)!=0) return false; }
        else { p++; }
    }
    return has_constraint;
}

typedef struct { int specificity; int rule_index; } eb_rule_match_t;
static int compare_matches(const void *a, const void *b) { const eb_rule_match_t *ma=(const eb_rule_match_t *)a; const eb_rule_match_t *mb=(const eb_rule_match_t *)b; if (ma->specificity!=mb->specificity) return ma->specificity-mb->specificity; return ma->rule_index-mb->rule_index; }

eb_computed_style_t eb_css_resolve_style(const eb_stylesheet_t *ss, const char *tag, const char *id, const char *class_name) {
    eb_computed_style_t s = eb_css_default_style(tag);
    if (!ss) return s;
    eb_rule_match_t matches[EB_CSS_MAX_RULES]; int match_count=0;
    for (int i=0; i<ss->rule_count; i++) { if (selector_matches(ss->rules[i].selector,tag,id,class_name)) { matches[match_count].specificity=ss->rules[i].specificity; matches[match_count].rule_index=i; match_count++; } }
    qsort(matches,(size_t)match_count,sizeof(eb_rule_match_t),compare_matches);
    for (int m=0; m<match_count; m++) { const eb_css_rule_t *rule=&ss->rules[matches[m].rule_index]; for (int j=0; j<rule->prop_count; j++) apply_property(&s,rule->properties[j].name,rule->properties[j].value); }
    return s;
}

eb_computed_style_t eb_css_resolve_style_inherited(const eb_stylesheet_t *ss, const char *tag, const char *id, const char *class_name, const eb_computed_style_t *parent_style) {
    eb_computed_style_t s = eb_css_resolve_style(ss, tag, id, class_name);
    if (parent_style) {
        eb_computed_style_t def = eb_css_default_style(tag);
        if (s.color.r==def.color.r&&s.color.g==def.color.g&&s.color.b==def.color.b&&s.color.a==def.color.a) s.color=parent_style->color;
        if (s.font_size==def.font_size&&parent_style->font_size!=16) s.font_size=parent_style->font_size;
        if (s.font_weight==def.font_weight) s.font_weight=parent_style->font_weight;
        if (s.font_style==def.font_style) s.font_style=parent_style->font_style;
        if (s.text_align==def.text_align) s.text_align=parent_style->text_align;
        if (s.line_height==0&&parent_style->line_height!=0) s.line_height=parent_style->line_height;
        if (s.list_style==EB_LIST_STYLE_NONE&&parent_style->list_style!=EB_LIST_STYLE_NONE) s.list_style=parent_style->list_style;
        if (s.text_transform==EB_TEXT_TRANSFORM_NONE) s.text_transform=parent_style->text_transform;
    }
    return s;
}

void eb_css_apply_inline_style(eb_computed_style_t *style, const char *inline_css) {
    if (!style||!inline_css) return;
    char buf[EB_CSS_MAX_VALUE*2]; strncpy(buf,inline_css,sizeof(buf)-1); buf[sizeof(buf)-1]='\0';
    char *p = buf;
    while (*p) {
        while (*p&&isspace((unsigned char)*p)) p++; if (!*p) break;
        char *ns=p; while (*p&&*p!=':') p++; if (!*p) break; *p='\0';
        char name[EB_CSS_MAX_VALUE]={0}; strncpy(name,ns,EB_CSS_MAX_VALUE-1); trim(name); p++;
        while (*p&&isspace((unsigned char)*p)) p++; char *vs=p; while (*p&&*p!=';') p++; if (*p) { *p='\0'; p++; }
        char value[EB_CSS_MAX_VALUE]={0}; strncpy(value,vs,EB_CSS_MAX_VALUE-1); trim(value);
        if (name[0]&&value[0]) apply_property(style,name,value);
    }
}
