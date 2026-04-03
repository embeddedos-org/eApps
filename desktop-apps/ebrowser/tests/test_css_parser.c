// SPDX-License-Identifier: MIT
// Comprehensive CSS parser tests for eBrowser web browser
#include "eBrowser/css_parser.h"
#include <stdio.h>
#include <string.h>

static int s_pass = 0, s_fail = 0;
#define TEST(name) static void name(void)
#define RUN(name) do { printf("  %s... ", #name); name(); printf("PASS\n"); s_pass++; } while(0)
#define ASSERT(cond) do { if(!(cond)) { printf("FAIL: %s:%d: %s\n", __FILE__, __LINE__, #cond); s_fail++; return; } } while(0)

// --- Color Parsing ---

TEST(test_hex_6digit) {
    eb_color_t c = eb_css_parse_color("#ff0000");
    ASSERT(c.r == 255 && c.g == 0 && c.b == 0 && c.a == 255);
    c = eb_css_parse_color("#00ff00");
    ASSERT(c.r == 0 && c.g == 255 && c.b == 0);
    c = eb_css_parse_color("#0000ff");
    ASSERT(c.r == 0 && c.g == 0 && c.b == 255);
    c = eb_css_parse_color("#ffffff");
    ASSERT(c.r == 255 && c.g == 255 && c.b == 255);
    c = eb_css_parse_color("#000000");
    ASSERT(c.r == 0 && c.g == 0 && c.b == 0);
}

TEST(test_hex_3digit) {
    eb_color_t c = eb_css_parse_color("#f00");
    ASSERT(c.r == 255 && c.g == 0 && c.b == 0);
    c = eb_css_parse_color("#0f0");
    ASSERT(c.r == 0 && c.g == 255 && c.b == 0);
    c = eb_css_parse_color("#00f");
    ASSERT(c.r == 0 && c.g == 0 && c.b == 255);
    c = eb_css_parse_color("#fff");
    ASSERT(c.r == 255 && c.g == 255 && c.b == 255);
}

TEST(test_named_colors) {
    struct { const char *name; uint8_t r, g, b; } cases[] = {
        {"red", 255, 0, 0}, {"green", 0, 128, 0}, {"blue", 0, 0, 255},
        {"white", 255, 255, 255}, {"black", 0, 0, 0}, {"yellow", 255, 255, 0},
        {"gray", 128, 128, 128}, {"grey", 128, 128, 128}, {"orange", 255, 165, 0},
        {"purple", 128, 0, 128}, {"navy", 0, 0, 128}, {"teal", 0, 128, 128},
        {"aqua", 0, 255, 255}, {"lime", 0, 255, 0}, {"silver", 192, 192, 192},
        {"maroon", 128, 0, 0}, {NULL, 0, 0, 0}
    };
    for (int i = 0; cases[i].name; i++) {
        eb_color_t c = eb_css_parse_color(cases[i].name);
        ASSERT(c.r == cases[i].r && c.g == cases[i].g && c.b == cases[i].b);
    }
}

TEST(test_color_transparent) {
    eb_color_t c = eb_css_parse_color("transparent");
    ASSERT(c.a == 0);
}

TEST(test_color_rgb_function) {
    eb_color_t c = eb_css_parse_color("rgb(100,200,50)");
    ASSERT(c.r == 100 && c.g == 200 && c.b == 50);
}

TEST(test_color_null) {
    eb_color_t c = eb_css_parse_color(NULL);
    ASSERT(c.r == 0 && c.g == 0 && c.b == 0);
}

TEST(test_color_whitespace) {
    eb_color_t c = eb_css_parse_color("  #ff0000  ");
    ASSERT(c.r == 255 && c.g == 0 && c.b == 0);
}

// --- Length Parsing ---

TEST(test_parse_length_px) {
    ASSERT(eb_css_parse_length("16px") == 16);
    ASSERT(eb_css_parse_length("100px") == 100);
    ASSERT(eb_css_parse_length("0px") == 0);
}

TEST(test_parse_length_plain) {
    ASSERT(eb_css_parse_length("42") == 42);
    ASSERT(eb_css_parse_length("0") == 0);
}

TEST(test_parse_length_null) {
    ASSERT(eb_css_parse_length(NULL) == 0);
}

TEST(test_parse_length_whitespace) {
    ASSERT(eb_css_parse_length("  24px") == 24);
}

// --- Default Styles ---

TEST(test_default_block_elements) {
    const char *block[] = {"div","p","h1","h2","h3","h4","h5","h6","ul","ol",
                           "section","article","header","footer","nav","main",
                           "aside","form","blockquote","pre","hr",NULL};
    for (int i = 0; block[i]; i++) {
        eb_computed_style_t s = eb_css_default_style(block[i]);
        ASSERT(s.display == EB_DISPLAY_BLOCK || s.display == EB_DISPLAY_TABLE);
    }
    ASSERT(eb_css_default_style("li").display == EB_DISPLAY_LIST_ITEM);
    ASSERT(eb_css_default_style("table").display == EB_DISPLAY_TABLE);
}

TEST(test_default_inline_elements) {
    const char *inl[] = {"span","a","b","strong","i","em","u","code","small",NULL};
    for (int i = 0; inl[i]; i++) {
        eb_computed_style_t s = eb_css_default_style(inl[i]);
        ASSERT(s.display == EB_DISPLAY_INLINE);
    }
}

TEST(test_default_heading_sizes) {
    ASSERT(eb_css_default_style("h1").font_size == 32);
    ASSERT(eb_css_default_style("h2").font_size == 24);
    ASSERT(eb_css_default_style("h3").font_size == 19);
    ASSERT(eb_css_default_style("h4").font_size == 16);
    ASSERT(eb_css_default_style("h5").font_size == 13);
    ASSERT(eb_css_default_style("h6").font_size == 11);
}

TEST(test_default_heading_bold) {
    for (int i = 1; i <= 6; i++) {
        char tag[4]; snprintf(tag, sizeof(tag), "h%d", i);
        ASSERT(eb_css_default_style(tag).font_weight == EB_FONT_WEIGHT_BOLD);
    }
}

TEST(test_default_bold_tags) {
    ASSERT(eb_css_default_style("b").font_weight == EB_FONT_WEIGHT_BOLD);
    ASSERT(eb_css_default_style("strong").font_weight == EB_FONT_WEIGHT_BOLD);
}

TEST(test_default_italic_tags) {
    ASSERT(eb_css_default_style("i").font_style == EB_FONT_STYLE_ITALIC);
    ASSERT(eb_css_default_style("em").font_style == EB_FONT_STYLE_ITALIC);
}

TEST(test_default_underline_tag) {
    ASSERT(eb_css_default_style("u").text_decoration == EB_TEXT_DECORATION_UNDERLINE);
}

TEST(test_default_link_style) {
    eb_computed_style_t s = eb_css_default_style("a");
    ASSERT(s.color.b > 200);
    ASSERT(s.text_decoration == EB_TEXT_DECORATION_UNDERLINE);
}

TEST(test_default_body_margins) {
    eb_computed_style_t s = eb_css_default_style("body");
    ASSERT(s.margin.top == 8 && s.margin.right == 8 && s.margin.bottom == 8 && s.margin.left == 8);
}

TEST(test_default_paragraph_margins) {
    eb_computed_style_t s = eb_css_default_style("p");
    ASSERT(s.margin.top == 16 && s.margin.bottom == 16);
}

TEST(test_default_null_tag) {
    eb_computed_style_t s = eb_css_default_style(NULL);
    ASSERT(s.display == EB_DISPLAY_INLINE);
    ASSERT(s.font_size == 16);
    ASSERT(s.width_auto == true);
    ASSERT(s.height_auto == true);
}

// --- Stylesheet Parsing ---

TEST(test_stylesheet_init) {
    eb_stylesheet_t ss;
    eb_css_init_stylesheet(&ss);
    ASSERT(ss.rule_count == 0);
}

TEST(test_parse_single_rule) {
    const char *css = "p { color: red; }";
    eb_stylesheet_t ss;
    eb_css_init_stylesheet(&ss);
    ASSERT(eb_css_parse(&ss, css, strlen(css)));
    ASSERT(ss.rule_count == 1);
    ASSERT(strcmp(ss.rules[0].selector, "p") == 0);
    ASSERT(ss.rules[0].prop_count == 1);
    ASSERT(strcmp(ss.rules[0].properties[0].name, "color") == 0);
    ASSERT(strcmp(ss.rules[0].properties[0].value, "red") == 0);
}

TEST(test_parse_multiple_rules) {
    const char *css =
        "h1 { font-size: 32px; color: #333; }"
        "p { margin: 10px; padding: 5px; }"
        ".highlight { background-color: yellow; }"
        "#main { width: 800px; }";
    eb_stylesheet_t ss;
    eb_css_init_stylesheet(&ss);
    ASSERT(eb_css_parse(&ss, css, strlen(css)));
    ASSERT(ss.rule_count == 4);
}

TEST(test_parse_multiple_properties) {
    const char *css =
        "div { color: blue; background-color: #fff; font-size: 14px; "
        "margin: 10px; padding: 5px; display: block; "
        "font-weight: bold; text-align: center; }";
    eb_stylesheet_t ss;
    eb_css_init_stylesheet(&ss);
    ASSERT(eb_css_parse(&ss, css, strlen(css)));
    ASSERT(ss.rules[0].prop_count == 8);
}

TEST(test_parse_css_comments) {
    const char *css = "/* header styles */ h1 { color: red; } /* footer */ p { margin: 0; }";
    eb_stylesheet_t ss;
    eb_css_init_stylesheet(&ss);
    ASSERT(eb_css_parse(&ss, css, strlen(css)));
    ASSERT(ss.rule_count == 2);
}

TEST(test_parse_id_selector) {
    const char *css = "#container { width: 960px; margin: 0; }";
    eb_stylesheet_t ss;
    eb_css_init_stylesheet(&ss);
    ASSERT(eb_css_parse(&ss, css, strlen(css)));
    ASSERT(ss.rules[0].selector[0] == '#');
}

TEST(test_parse_class_selector) {
    const char *css = ".btn { padding: 10px; background-color: blue; }";
    eb_stylesheet_t ss;
    eb_css_init_stylesheet(&ss);
    ASSERT(eb_css_parse(&ss, css, strlen(css)));
    ASSERT(ss.rules[0].selector[0] == '.');
}

TEST(test_parse_null_input) {
    eb_stylesheet_t ss;
    eb_css_init_stylesheet(&ss);
    ASSERT(eb_css_parse(NULL, "p{}", 3) == false);
    ASSERT(eb_css_parse(&ss, NULL, 0) == false);
    ASSERT(eb_css_parse(&ss, "", 0) == false);
}

// --- Style Resolution ---

TEST(test_resolve_tag_selector) {
    const char *css = "p { color: blue; font-size: 20px; }";
    eb_stylesheet_t ss;
    eb_css_init_stylesheet(&ss);
    eb_css_parse(&ss, css, strlen(css));
    eb_computed_style_t s = eb_css_resolve_style(&ss, "p", NULL, NULL);
    ASSERT(s.color.b == 255 && s.color.r == 0);
    ASSERT(s.font_size == 20);
}

TEST(test_resolve_id_selector) {
    const char *css = "#header { background-color: #333; }";
    eb_stylesheet_t ss;
    eb_css_init_stylesheet(&ss);
    eb_css_parse(&ss, css, strlen(css));
    eb_computed_style_t s = eb_css_resolve_style(&ss, "div", "header", NULL);
    ASSERT(s.background_color.r == 0x33);
}

TEST(test_resolve_class_selector) {
    const char *css = ".active { color: green; }";
    eb_stylesheet_t ss;
    eb_css_init_stylesheet(&ss);
    eb_css_parse(&ss, css, strlen(css));
    eb_computed_style_t s = eb_css_resolve_style(&ss, "span", NULL, "active");
    ASSERT(s.color.g == 128);
}

TEST(test_resolve_display_property) {
    const char *css = ".hidden { display: none; } .flex { display: flex; }";
    eb_stylesheet_t ss;
    eb_css_init_stylesheet(&ss);
    eb_css_parse(&ss, css, strlen(css));
    eb_computed_style_t s1 = eb_css_resolve_style(&ss, "div", NULL, "hidden");
    ASSERT(s1.display == EB_DISPLAY_NONE);
    eb_computed_style_t s2 = eb_css_resolve_style(&ss, "div", NULL, "flex");
    ASSERT(s2.display == EB_DISPLAY_FLEX);
}

TEST(test_resolve_text_align) {
    const char *css = ".center { text-align: center; } .right { text-align: right; }";
    eb_stylesheet_t ss;
    eb_css_init_stylesheet(&ss);
    eb_css_parse(&ss, css, strlen(css));
    eb_computed_style_t s1 = eb_css_resolve_style(&ss, "p", NULL, "center");
    ASSERT(s1.text_align == EB_TEXT_ALIGN_CENTER);
    eb_computed_style_t s2 = eb_css_resolve_style(&ss, "p", NULL, "right");
    ASSERT(s2.text_align == EB_TEXT_ALIGN_RIGHT);
}

TEST(test_resolve_margin_shorthand) {
    const char *css = "div { margin: 20px; }";
    eb_stylesheet_t ss;
    eb_css_init_stylesheet(&ss);
    eb_css_parse(&ss, css, strlen(css));
    eb_computed_style_t s = eb_css_resolve_style(&ss, "div", NULL, NULL);
    ASSERT(s.margin.top == 20 && s.margin.right == 20 && s.margin.bottom == 20 && s.margin.left == 20);
}

TEST(test_resolve_padding_shorthand) {
    const char *css = "div { padding: 15px; }";
    eb_stylesheet_t ss;
    eb_css_init_stylesheet(&ss);
    eb_css_parse(&ss, css, strlen(css));
    eb_computed_style_t s = eb_css_resolve_style(&ss, "div", NULL, NULL);
    ASSERT(s.padding.top == 15 && s.padding.right == 15 && s.padding.bottom == 15 && s.padding.left == 15);
}

TEST(test_resolve_individual_margins) {
    const char *css = "div { margin-top: 10px; margin-right: 20px; margin-bottom: 30px; margin-left: 40px; }";
    eb_stylesheet_t ss;
    eb_css_init_stylesheet(&ss);
    eb_css_parse(&ss, css, strlen(css));
    eb_computed_style_t s = eb_css_resolve_style(&ss, "div", NULL, NULL);
    ASSERT(s.margin.top == 10 && s.margin.right == 20 && s.margin.bottom == 30 && s.margin.left == 40);
}

TEST(test_resolve_width_height) {
    const char *css = "div { width: 200px; height: 100px; }";
    eb_stylesheet_t ss;
    eb_css_init_stylesheet(&ss);
    eb_css_parse(&ss, css, strlen(css));
    eb_computed_style_t s = eb_css_resolve_style(&ss, "div", NULL, NULL);
    ASSERT(s.width == 200 && s.height == 100);
    ASSERT(s.width_auto == false && s.height_auto == false);
}

TEST(test_resolve_unmatched_selector) {
    const char *css = "span { color: red; }";
    eb_stylesheet_t ss;
    eb_css_init_stylesheet(&ss);
    eb_css_parse(&ss, css, strlen(css));
    eb_computed_style_t s = eb_css_resolve_style(&ss, "div", NULL, NULL);
    ASSERT(s.color.r == 0);
}

TEST(test_resolve_no_stylesheet) {
    eb_computed_style_t s = eb_css_resolve_style(NULL, "p", NULL, NULL);
    ASSERT(s.display == EB_DISPLAY_BLOCK);
    ASSERT(s.font_size == 16);
}

TEST(test_resolve_text_decoration) {
    const char *css = ".strike { text-decoration: line-through; } .underline { text-decoration: underline; }";
    eb_stylesheet_t ss;
    eb_css_init_stylesheet(&ss);
    eb_css_parse(&ss, css, strlen(css));
    eb_computed_style_t s1 = eb_css_resolve_style(&ss, "span", NULL, "strike");
    ASSERT(s1.text_decoration == EB_TEXT_DECORATION_LINE_THROUGH);
    eb_computed_style_t s2 = eb_css_resolve_style(&ss, "span", NULL, "underline");
    ASSERT(s2.text_decoration == EB_TEXT_DECORATION_UNDERLINE);
}

TEST(test_resolve_font_weight_numeric) {
    const char *css = ".bold { font-weight: 700; } .normal { font-weight: 400; }";
    eb_stylesheet_t ss;
    eb_css_init_stylesheet(&ss);
    eb_css_parse(&ss, css, strlen(css));
    eb_computed_style_t s1 = eb_css_resolve_style(&ss, "span", NULL, "bold");
    ASSERT(s1.font_weight == EB_FONT_WEIGHT_BOLD);
    eb_computed_style_t s2 = eb_css_resolve_style(&ss, "span", NULL, "normal");
    ASSERT(s2.font_weight == EB_FONT_WEIGHT_NORMAL);
}

TEST(test_resolve_border) {
    const char *css = "div { border-width: 2px; border-color: #ff0000; }";
    eb_stylesheet_t ss;
    eb_css_init_stylesheet(&ss);
    eb_css_parse(&ss, css, strlen(css));
    eb_computed_style_t s = eb_css_resolve_style(&ss, "div", NULL, NULL);
    ASSERT(s.border_width == 2);
    ASSERT(s.border_color.r == 255);
}

int main(void) {
    printf("=== CSS Parser Tests ===\n");
    RUN(test_hex_6digit);
    RUN(test_hex_3digit);
    RUN(test_named_colors);
    RUN(test_color_transparent);
    RUN(test_color_rgb_function);
    RUN(test_color_null);
    RUN(test_color_whitespace);
    RUN(test_parse_length_px);
    RUN(test_parse_length_plain);
    RUN(test_parse_length_null);
    RUN(test_parse_length_whitespace);
    RUN(test_default_block_elements);
    RUN(test_default_inline_elements);
    RUN(test_default_heading_sizes);
    RUN(test_default_heading_bold);
    RUN(test_default_bold_tags);
    RUN(test_default_italic_tags);
    RUN(test_default_underline_tag);
    RUN(test_default_link_style);
    RUN(test_default_body_margins);
    RUN(test_default_paragraph_margins);
    RUN(test_default_null_tag);
    RUN(test_stylesheet_init);
    RUN(test_parse_single_rule);
    RUN(test_parse_multiple_rules);
    RUN(test_parse_multiple_properties);
    RUN(test_parse_css_comments);
    RUN(test_parse_id_selector);
    RUN(test_parse_class_selector);
    RUN(test_parse_null_input);
    RUN(test_resolve_tag_selector);
    RUN(test_resolve_id_selector);
    RUN(test_resolve_class_selector);
    RUN(test_resolve_display_property);
    RUN(test_resolve_text_align);
    RUN(test_resolve_margin_shorthand);
    RUN(test_resolve_padding_shorthand);
    RUN(test_resolve_individual_margins);
    RUN(test_resolve_width_height);
    RUN(test_resolve_unmatched_selector);
    RUN(test_resolve_no_stylesheet);
    RUN(test_resolve_text_decoration);
    RUN(test_resolve_font_weight_numeric);
    RUN(test_resolve_border);
    printf("\nResults: %d passed, %d failed\n", s_pass, s_fail);
    return s_fail > 0 ? 1 : 0;
}
