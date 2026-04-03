// SPDX-License-Identifier: MIT
// SVG parser tests for eBrowser
#include "eBrowser/svg.h"
#include <stdio.h>
#include <string.h>

static int s_pass = 0, s_fail = 0;
#define TEST(name) static void name(void)
#define RUN(name) do { printf("  %s... ", #name); name(); printf("PASS\n"); s_pass++; } while(0)
#define ASSERT(cond) do { if(!(cond)) { printf("FAIL: %s:%d: %s\n", __FILE__, __LINE__, #cond); s_fail++; return; } } while(0)

TEST(test_svg_parse_null) {
    eb_svg_element_t svg;
    ASSERT(eb_svg_parse(&svg, NULL, 0) == false);
    ASSERT(eb_svg_parse(NULL, "<svg></svg>", 11) == false);
}

TEST(test_svg_parse_rect) {
    const char *s = "<svg width=\"100\" height=\"100\"><rect x=\"10\" y=\"20\" width=\"50\" height=\"30\" fill=\"red\"/></svg>";
    eb_svg_element_t svg;
    ASSERT(eb_svg_parse(&svg, s, strlen(s)));
    ASSERT(svg.width == 100);
    ASSERT(svg.height == 100);
    ASSERT(svg.shape_count == 1);
    ASSERT(svg.shapes[0].type == EB_SVG_RECT);
    ASSERT(svg.shapes[0].data.rect.x == 10);
    ASSERT(svg.shapes[0].data.rect.y == 20);
    ASSERT(svg.shapes[0].data.rect.width == 50);
    ASSERT(svg.shapes[0].data.rect.height == 30);
    ASSERT(svg.shapes[0].has_fill == true);
    ASSERT(svg.shapes[0].fill.r == 255);
}

TEST(test_svg_parse_circle) {
    const char *s = "<svg><circle cx=\"50\" cy=\"50\" r=\"25\" fill=\"blue\" stroke=\"black\" stroke-width=\"2\"/></svg>";
    eb_svg_element_t svg;
    ASSERT(eb_svg_parse(&svg, s, strlen(s)));
    ASSERT(svg.shape_count == 1);
    ASSERT(svg.shapes[0].type == EB_SVG_CIRCLE);
    ASSERT(svg.shapes[0].data.circle.cx == 50);
    ASSERT(svg.shapes[0].data.circle.cy == 50);
    ASSERT(svg.shapes[0].data.circle.r == 25);
    ASSERT(svg.shapes[0].has_stroke == true);
    ASSERT(svg.shapes[0].stroke_width == 2);
}

TEST(test_svg_parse_ellipse) {
    const char *s = "<svg><ellipse cx=\"100\" cy=\"50\" rx=\"60\" ry=\"30\" fill=\"green\"/></svg>";
    eb_svg_element_t svg;
    ASSERT(eb_svg_parse(&svg, s, strlen(s)));
    ASSERT(svg.shape_count == 1);
    ASSERT(svg.shapes[0].type == EB_SVG_ELLIPSE);
    ASSERT(svg.shapes[0].data.ellipse.rx == 60);
    ASSERT(svg.shapes[0].data.ellipse.ry == 30);
}

TEST(test_svg_parse_line) {
    const char *s = "<svg><line x1=\"0\" y1=\"0\" x2=\"100\" y2=\"100\" stroke=\"black\"/></svg>";
    eb_svg_element_t svg;
    ASSERT(eb_svg_parse(&svg, s, strlen(s)));
    ASSERT(svg.shape_count == 1);
    ASSERT(svg.shapes[0].type == EB_SVG_LINE);
    ASSERT(svg.shapes[0].data.line.x1 == 0);
    ASSERT(svg.shapes[0].data.line.y1 == 0);
    ASSERT(svg.shapes[0].data.line.x2 == 100);
    ASSERT(svg.shapes[0].data.line.y2 == 100);
}

TEST(test_svg_parse_polyline) {
    const char *s = "<svg><polyline points=\"0,0 50,25 100,0\" fill=\"none\" stroke=\"red\"/></svg>";
    eb_svg_element_t svg;
    ASSERT(eb_svg_parse(&svg, s, strlen(s)));
    ASSERT(svg.shape_count == 1);
    ASSERT(svg.shapes[0].type == EB_SVG_POLYLINE);
    ASSERT(svg.shapes[0].data.poly.count == 3);
    ASSERT(svg.shapes[0].data.poly.points[0].x == 0);
    ASSERT(svg.shapes[0].data.poly.points[1].x == 50);
    ASSERT(svg.shapes[0].data.poly.points[2].x == 100);
}

TEST(test_svg_parse_path_basic) {
    const char *s = "<svg><path d=\"M10 20 L30 40 L50 20 Z\" fill=\"orange\"/></svg>";
    eb_svg_element_t svg;
    ASSERT(eb_svg_parse(&svg, s, strlen(s)));
    ASSERT(svg.shape_count == 1);
    ASSERT(svg.shapes[0].type == EB_SVG_PATH);
    ASSERT(svg.shapes[0].data.path.count >= 3);
    ASSERT(svg.shapes[0].data.path.points[0].x == 10);
    ASSERT(svg.shapes[0].data.path.points[0].y == 20);
}

TEST(test_svg_parse_viewbox) {
    const char *s = "<svg viewBox=\"0 0 200 100\" width=\"400\" height=\"200\"><rect x=\"0\" y=\"0\" width=\"200\" height=\"100\"/></svg>";
    eb_svg_element_t svg;
    ASSERT(eb_svg_parse(&svg, s, strlen(s)));
    ASSERT(svg.viewbox_width == 200);
    ASSERT(svg.viewbox_height == 100);
    ASSERT(svg.width == 400);
    ASSERT(svg.height == 200);
}

TEST(test_svg_parse_multiple_shapes) {
    const char *s =
        "<svg width=\"200\" height=\"200\">"
        "<rect x=\"0\" y=\"0\" width=\"100\" height=\"100\" fill=\"red\"/>"
        "<circle cx=\"150\" cy=\"50\" r=\"40\" fill=\"blue\"/>"
        "<line x1=\"0\" y1=\"200\" x2=\"200\" y2=\"200\" stroke=\"gray\"/>"
        "</svg>";
    eb_svg_element_t svg;
    ASSERT(eb_svg_parse(&svg, s, strlen(s)));
    ASSERT(svg.shape_count == 3);
    ASSERT(svg.shapes[0].type == EB_SVG_RECT);
    ASSERT(svg.shapes[1].type == EB_SVG_CIRCLE);
    ASSERT(svg.shapes[2].type == EB_SVG_LINE);
}

TEST(test_svg_default_fill) {
    const char *s = "<svg><rect x=\"0\" y=\"0\" width=\"50\" height=\"50\"/></svg>";
    eb_svg_element_t svg;
    ASSERT(eb_svg_parse(&svg, s, strlen(s)));
    ASSERT(svg.shapes[0].has_fill == true);
    ASSERT(svg.shapes[0].fill.r == 0 && svg.shapes[0].fill.g == 0 && svg.shapes[0].fill.b == 0);
}

int main(void) {
    printf("=== SVG Parser Tests ===\n");
    RUN(test_svg_parse_null);
    RUN(test_svg_parse_rect);
    RUN(test_svg_parse_circle);
    RUN(test_svg_parse_ellipse);
    RUN(test_svg_parse_line);
    RUN(test_svg_parse_polyline);
    RUN(test_svg_parse_path_basic);
    RUN(test_svg_parse_viewbox);
    RUN(test_svg_parse_multiple_shapes);
    RUN(test_svg_default_fill);
    printf("\nResults: %d passed, %d failed\n", s_pass, s_fail);
    return s_fail > 0 ? 1 : 0;
}
