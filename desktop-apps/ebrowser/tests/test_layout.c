// SPDX-License-Identifier: MIT
// Comprehensive layout engine tests for eBrowser web browser
#include "eBrowser/layout.h"
#include "eBrowser/html_parser.h"
#include <stdio.h>
#include <string.h>

static int s_pass = 0, s_fail = 0;
#define TEST(name) static void name(void)
#define RUN(name) do { printf("  %s... ", #name); name(); printf("PASS\n"); s_pass++; } while(0)
#define ASSERT(cond) do { if(!(cond)) { printf("FAIL: %s:%d: %s\n", __FILE__, __LINE__, #cond); s_fail++; return; } } while(0)

// --- Context Initialization ---

TEST(test_layout_init_800x480) {
    eb_layout_context_t ctx;
    eb_layout_init(&ctx, 800, 480);
    ASSERT(ctx.viewport_width == 800);
    ASSERT(ctx.viewport_height == 480);
    ASSERT(ctx.box_count == 0);
}

TEST(test_layout_init_320x240) {
    eb_layout_context_t ctx;
    eb_layout_init(&ctx, 320, 240);
    ASSERT(ctx.viewport_width == 320);
    ASSERT(ctx.viewport_height == 240);
}

TEST(test_layout_init_1920x1080) {
    eb_layout_context_t ctx;
    eb_layout_init(&ctx, 1920, 1080);
    ASSERT(ctx.viewport_width == 1920);
    ASSERT(ctx.viewport_height == 1080);
}

// --- Tree Building ---

TEST(test_build_simple_paragraph) {
    const char *html = "<html><body><p>Hello World</p></body></html>";
    eb_dom_node_t *dom = eb_html_parse(html, strlen(html));
    ASSERT(dom != NULL);
    eb_stylesheet_t ss;
    eb_css_init_stylesheet(&ss);
    eb_layout_context_t ctx;
    eb_layout_init(&ctx, 800, 480);
    eb_layout_box_t *root = eb_layout_build(&ctx, dom, &ss);
    ASSERT(root != NULL);
    ASSERT(ctx.box_count > 0);
    eb_dom_destroy(dom);
}

TEST(test_build_nested_divs) {
    const char *html = "<div><div><div><p>Deep</p></div></div></div>";
    eb_dom_node_t *dom = eb_html_parse(html, strlen(html));
    eb_stylesheet_t ss;
    eb_css_init_stylesheet(&ss);
    eb_layout_context_t ctx;
    eb_layout_init(&ctx, 800, 480);
    eb_layout_box_t *root = eb_layout_build(&ctx, dom, &ss);
    ASSERT(root != NULL);
    ASSERT(root->child_count > 0);
    eb_dom_destroy(dom);
}

TEST(test_build_display_none_skipped) {
    const char *css = ".hidden { display: none; }";
    const char *html = "<div><div class=\"hidden\">Hidden</div><p>Visible</p></div>";
    eb_dom_node_t *dom = eb_html_parse(html, strlen(html));
    eb_stylesheet_t ss;
    eb_css_init_stylesheet(&ss);
    eb_css_parse(&ss, css, strlen(css));
    eb_layout_context_t ctx;
    eb_layout_init(&ctx, 800, 480);
    eb_layout_box_t *root = eb_layout_build(&ctx, dom, &ss);
    ASSERT(root != NULL);
    eb_dom_destroy(dom);
}

TEST(test_build_null_dom) {
    eb_layout_context_t ctx;
    eb_layout_init(&ctx, 800, 480);
    eb_layout_box_t *root = eb_layout_build(&ctx, NULL, NULL);
    ASSERT(root == NULL);
}

TEST(test_build_null_context) {
    const char *html = "<p>Test</p>";
    eb_dom_node_t *dom = eb_html_parse(html, strlen(html));
    eb_layout_box_t *root = eb_layout_build(NULL, dom, NULL);
    ASSERT(root == NULL);
    eb_dom_destroy(dom);
}

// --- Layout Computation ---

TEST(test_compute_block_width) {
    const char *html = "<html><body><div><p>Content</p></div></body></html>";
    eb_dom_node_t *dom = eb_html_parse(html, strlen(html));
    eb_stylesheet_t ss;
    eb_css_init_stylesheet(&ss);
    eb_layout_context_t ctx;
    eb_layout_init(&ctx, 800, 480);
    eb_layout_box_t *root = eb_layout_build(&ctx, dom, &ss);
    ASSERT(root != NULL);
    eb_layout_compute(&ctx, root);
    ASSERT(root->width > 0);
    ASSERT(root->width <= 800);
    eb_dom_destroy(dom);
}

TEST(test_compute_block_stacking) {
    const char *html = "<div><p>First</p><p>Second</p><p>Third</p></div>";
    eb_dom_node_t *dom = eb_html_parse(html, strlen(html));
    eb_stylesheet_t ss;
    eb_css_init_stylesheet(&ss);
    eb_layout_context_t ctx;
    eb_layout_init(&ctx, 800, 480);
    eb_layout_box_t *root = eb_layout_build(&ctx, dom, &ss);
    eb_layout_compute(&ctx, root);
    ASSERT(root != NULL);
    ASSERT(root->height > 0);
    eb_dom_destroy(dom);
}

TEST(test_compute_margin_spacing) {
    const char *css = "p { margin: 20px; }";
    const char *html = "<div><p>With margins</p></div>";
    eb_dom_node_t *dom = eb_html_parse(html, strlen(html));
    eb_stylesheet_t ss;
    eb_css_init_stylesheet(&ss);
    eb_css_parse(&ss, css, strlen(css));
    eb_layout_context_t ctx;
    eb_layout_init(&ctx, 800, 480);
    eb_layout_box_t *root = eb_layout_build(&ctx, dom, &ss);
    eb_layout_compute(&ctx, root);
    eb_dom_destroy(dom);
}

TEST(test_compute_padding) {
    const char *css = "div { padding: 10px; }";
    const char *html = "<div><p>Padded</p></div>";
    eb_dom_node_t *dom = eb_html_parse(html, strlen(html));
    eb_stylesheet_t ss;
    eb_css_init_stylesheet(&ss);
    eb_css_parse(&ss, css, strlen(css));
    eb_layout_context_t ctx;
    eb_layout_init(&ctx, 800, 480);
    eb_layout_box_t *root = eb_layout_build(&ctx, dom, &ss);
    eb_layout_compute(&ctx, root);
    eb_dom_destroy(dom);
}

TEST(test_compute_fixed_width) {
    const char *css = "div { width: 400px; }";
    const char *html = "<div>Fixed width</div>";
    eb_dom_node_t *dom = eb_html_parse(html, strlen(html));
    eb_stylesheet_t ss;
    eb_css_init_stylesheet(&ss);
    eb_css_parse(&ss, css, strlen(css));
    eb_layout_context_t ctx;
    eb_layout_init(&ctx, 800, 480);
    eb_layout_box_t *root = eb_layout_build(&ctx, dom, &ss);
    eb_layout_compute(&ctx, root);
    eb_dom_destroy(dom);
}

TEST(test_compute_fixed_height) {
    const char *css = "div { height: 200px; }";
    const char *html = "<div>Fixed height</div>";
    eb_dom_node_t *dom = eb_html_parse(html, strlen(html));
    eb_stylesheet_t ss;
    eb_css_init_stylesheet(&ss);
    eb_css_parse(&ss, css, strlen(css));
    eb_layout_context_t ctx;
    eb_layout_init(&ctx, 800, 480);
    eb_layout_box_t *root = eb_layout_build(&ctx, dom, &ss);
    eb_layout_compute(&ctx, root);
    eb_dom_destroy(dom);
}

TEST(test_compute_null) {
    eb_layout_context_t ctx;
    eb_layout_init(&ctx, 800, 480);
    eb_layout_compute(NULL, NULL);
    eb_layout_compute(&ctx, NULL);
}

// --- Real-world Layouts ---

TEST(test_layout_blog_post) {
    const char *html =
        "<html><body>"
        "<header><h1>Blog Title</h1></header>"
        "<article>"
        "<h2>Post Title</h2>"
        "<p>First paragraph of the post with some text.</p>"
        "<p>Second paragraph with <strong>bold</strong> and <em>italic</em> text.</p>"
        "<ul><li>Item 1</li><li>Item 2</li><li>Item 3</li></ul>"
        "</article>"
        "<footer><p>Copyright 2025</p></footer>"
        "</body></html>";
    eb_dom_node_t *dom = eb_html_parse(html, strlen(html));
    eb_stylesheet_t ss;
    eb_css_init_stylesheet(&ss);
    eb_layout_context_t ctx;
    eb_layout_init(&ctx, 800, 480);
    eb_layout_box_t *root = eb_layout_build(&ctx, dom, &ss);
    ASSERT(root != NULL);
    eb_layout_compute(&ctx, root);
    ASSERT(root->width > 0);
    ASSERT(root->height > 0);
    eb_dom_destroy(dom);
}

TEST(test_layout_with_css) {
    const char *css =
        "body { margin: 0; padding: 20px; }"
        "h1 { color: #333; margin-bottom: 10px; }"
        ".container { width: 600px; margin: 0; padding: 10px; }"
        "p { font-size: 14px; margin: 8px; }";
    const char *html =
        "<body><div class=\"container\">"
        "<h1>Styled Page</h1>"
        "<p>This page has CSS styling applied.</p>"
        "</div></body>";
    eb_dom_node_t *dom = eb_html_parse(html, strlen(html));
    eb_stylesheet_t ss;
    eb_css_init_stylesheet(&ss);
    eb_css_parse(&ss, css, strlen(css));
    eb_layout_context_t ctx;
    eb_layout_init(&ctx, 800, 480);
    eb_layout_box_t *root = eb_layout_build(&ctx, dom, &ss);
    ASSERT(root != NULL);
    eb_layout_compute(&ctx, root);
    eb_dom_destroy(dom);
}

TEST(test_layout_small_viewport) {
    const char *html = "<body><div><p>Small screen content</p><p>Another paragraph</p></div></body>";
    eb_dom_node_t *dom = eb_html_parse(html, strlen(html));
    eb_stylesheet_t ss;
    eb_css_init_stylesheet(&ss);
    eb_layout_context_t ctx;
    eb_layout_init(&ctx, 320, 240);
    eb_layout_box_t *root = eb_layout_build(&ctx, dom, &ss);
    ASSERT(root != NULL);
    eb_layout_compute(&ctx, root);
    ASSERT(root->width <= 320);
    eb_dom_destroy(dom);
}

int main(void) {
    printf("=== Layout Engine Tests ===\n");
    RUN(test_layout_init_800x480);
    RUN(test_layout_init_320x240);
    RUN(test_layout_init_1920x1080);
    RUN(test_build_simple_paragraph);
    RUN(test_build_nested_divs);
    RUN(test_build_display_none_skipped);
    RUN(test_build_null_dom);
    RUN(test_build_null_context);
    RUN(test_compute_block_width);
    RUN(test_compute_block_stacking);
    RUN(test_compute_margin_spacing);
    RUN(test_compute_padding);
    RUN(test_compute_fixed_width);
    RUN(test_compute_fixed_height);
    RUN(test_compute_null);
    RUN(test_layout_blog_post);
    RUN(test_layout_with_css);
    RUN(test_layout_small_viewport);
    printf("\nResults: %d passed, %d failed\n", s_pass, s_fail);
    return s_fail > 0 ? 1 : 0;
}
