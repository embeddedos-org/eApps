// SPDX-License-Identifier: MIT
// Comprehensive URL parser tests for eBrowser web browser
#include "eBrowser/url.h"
#include <stdio.h>
#include <string.h>

static int s_pass = 0, s_fail = 0;
#define TEST(name) static void name(void)
#define RUN(name) do { printf("  %s... ", #name); name(); printf("PASS\n"); s_pass++; } while(0)
#define ASSERT(cond) do { if(!(cond)) { printf("FAIL: %s:%d: %s\n", __FILE__, __LINE__, #cond); s_fail++; return; } } while(0)

// --- Default Ports ---

TEST(test_default_port_http) { ASSERT(eb_url_default_port("http") == 80); }
TEST(test_default_port_https) { ASSERT(eb_url_default_port("https") == 443); }
TEST(test_default_port_ftp) { ASSERT(eb_url_default_port("ftp") == 21); }
TEST(test_default_port_unknown) { ASSERT(eb_url_default_port("ws") == 80); }
TEST(test_default_port_null) { ASSERT(eb_url_default_port(NULL) == 80); }

// --- URL Parsing ---

TEST(test_parse_full_url) {
    eb_url_t u;
    ASSERT(eb_url_parse("https://example.com:8080/path/page?q=1&r=2#section", &u));
    ASSERT(strcmp(u.scheme, "https") == 0);
    ASSERT(strcmp(u.host, "example.com") == 0);
    ASSERT(u.port == 8080);
    ASSERT(strcmp(u.path, "/path/page") == 0);
    ASSERT(strcmp(u.query, "q=1&r=2") == 0);
    ASSERT(strcmp(u.fragment, "section") == 0);
}

TEST(test_parse_http_simple) {
    eb_url_t u;
    ASSERT(eb_url_parse("http://test.org/page", &u));
    ASSERT(strcmp(u.scheme, "http") == 0);
    ASSERT(strcmp(u.host, "test.org") == 0);
    ASSERT(u.port == 80);
    ASSERT(strcmp(u.path, "/page") == 0);
}

TEST(test_parse_https_default_port) {
    eb_url_t u;
    ASSERT(eb_url_parse("https://secure.example.com/login", &u));
    ASSERT(u.port == 443);
}

TEST(test_parse_no_path) {
    eb_url_t u;
    ASSERT(eb_url_parse("http://example.com", &u));
    ASSERT(strcmp(u.host, "example.com") == 0);
    ASSERT(strcmp(u.path, "/") == 0);
}

TEST(test_parse_root_path) {
    eb_url_t u;
    ASSERT(eb_url_parse("http://example.com/", &u));
    ASSERT(strcmp(u.path, "/") == 0);
}

TEST(test_parse_deep_path) {
    eb_url_t u;
    ASSERT(eb_url_parse("https://cdn.example.com/assets/images/logo.png", &u));
    ASSERT(strcmp(u.path, "/assets/images/logo.png") == 0);
}

TEST(test_parse_query_only) {
    eb_url_t u;
    ASSERT(eb_url_parse("http://api.example.com/search?q=hello+world&lang=en", &u));
    ASSERT(strcmp(u.query, "q=hello+world&lang=en") == 0);
    ASSERT(u.fragment[0] == '\0');
}

TEST(test_parse_fragment_only) {
    eb_url_t u;
    ASSERT(eb_url_parse("http://docs.example.com/guide#chapter-3", &u));
    ASSERT(u.query[0] == '\0');
    ASSERT(strcmp(u.fragment, "chapter-3") == 0);
}

TEST(test_parse_custom_port) {
    eb_url_t u;
    ASSERT(eb_url_parse("http://localhost:3000/api/v1/users", &u));
    ASSERT(strcmp(u.host, "localhost") == 0);
    ASSERT(u.port == 3000);
    ASSERT(strcmp(u.path, "/api/v1/users") == 0);
}

TEST(test_parse_high_port) {
    eb_url_t u;
    ASSERT(eb_url_parse("http://server:65535/", &u));
    ASSERT(u.port == 65535);
}

TEST(test_parse_subdomain) {
    eb_url_t u;
    ASSERT(eb_url_parse("https://www.blog.example.co.uk/posts/123", &u));
    ASSERT(strcmp(u.host, "www.blog.example.co.uk") == 0);
    ASSERT(strcmp(u.path, "/posts/123") == 0);
}

TEST(test_parse_no_scheme) {
    eb_url_t u;
    ASSERT(eb_url_parse("example.com/page", &u));
    ASSERT(strcmp(u.scheme, "http") == 0);
}

TEST(test_parse_case_insensitive_scheme) {
    eb_url_t u;
    ASSERT(eb_url_parse("HTTPS://Example.Com/Path", &u));
    ASSERT(strcmp(u.scheme, "https") == 0);
}

TEST(test_parse_null) {
    eb_url_t u;
    ASSERT(eb_url_parse(NULL, &u) == false);
    ASSERT(eb_url_parse("http://test.com", NULL) == false);
}

TEST(test_parse_ftp_url) {
    eb_url_t u;
    ASSERT(eb_url_parse("ftp://files.example.com/pub/docs/readme.txt", &u));
    ASSERT(strcmp(u.scheme, "ftp") == 0);
    ASSERT(u.port == 21);
}

// --- URL to String ---

TEST(test_to_string_basic) {
    eb_url_t u;
    eb_url_parse("https://example.com/test", &u);
    char buf[512];
    eb_url_to_string(&u, buf, sizeof(buf));
    ASSERT(strstr(buf, "https://example.com/test") != NULL);
}

TEST(test_to_string_with_port) {
    eb_url_t u;
    eb_url_parse("http://localhost:8080/api", &u);
    char buf[512];
    eb_url_to_string(&u, buf, sizeof(buf));
    ASSERT(strstr(buf, ":8080") != NULL);
    ASSERT(strstr(buf, "/api") != NULL);
}

TEST(test_to_string_default_port_omitted) {
    eb_url_t u;
    eb_url_parse("http://example.com/path", &u);
    char buf[512];
    eb_url_to_string(&u, buf, sizeof(buf));
    ASSERT(strstr(buf, ":80") == NULL);
}

TEST(test_to_string_with_query) {
    eb_url_t u;
    eb_url_parse("http://example.com/search?q=test", &u);
    char buf[512];
    eb_url_to_string(&u, buf, sizeof(buf));
    ASSERT(strstr(buf, "?q=test") != NULL);
}

TEST(test_to_string_with_fragment) {
    eb_url_t u;
    eb_url_parse("http://example.com/page#top", &u);
    char buf[512];
    eb_url_to_string(&u, buf, sizeof(buf));
    ASSERT(strstr(buf, "#top") != NULL);
}

// --- URL Resolution ---

TEST(test_resolve_absolute_url) {
    eb_url_t base, out;
    eb_url_parse("https://example.com/dir/page.html", &base);
    ASSERT(eb_url_resolve(&base, "https://other.com/new", &out));
    ASSERT(strcmp(out.host, "other.com") == 0);
    ASSERT(strcmp(out.path, "/new") == 0);
}

TEST(test_resolve_absolute_path) {
    eb_url_t base, out;
    eb_url_parse("https://example.com/dir/page.html", &base);
    ASSERT(eb_url_resolve(&base, "/new/path", &out));
    ASSERT(strcmp(out.host, "example.com") == 0);
    ASSERT(strcmp(out.path, "/new/path") == 0);
}

TEST(test_resolve_relative_path) {
    eb_url_t base, out;
    eb_url_parse("https://example.com/dir/page.html", &base);
    ASSERT(eb_url_resolve(&base, "other.html", &out));
    ASSERT(strcmp(out.host, "example.com") == 0);
    ASSERT(strstr(out.path, "other.html") != NULL);
}

TEST(test_resolve_null) {
    eb_url_t base, out;
    ASSERT(eb_url_resolve(NULL, "/test", &out) == false);
    ASSERT(eb_url_resolve(&base, NULL, &out) == false);
    ASSERT(eb_url_resolve(&base, "/test", NULL) == false);
}

TEST(test_resolve_clears_query_fragment) {
    eb_url_t base, out;
    eb_url_parse("https://example.com/page?old=1#old", &base);
    ASSERT(eb_url_resolve(&base, "/new", &out));
    ASSERT(out.query[0] == '\0');
    ASSERT(out.fragment[0] == '\0');
}

// --- Real-world URLs ---

TEST(test_parse_google_search) {
    eb_url_t u;
    ASSERT(eb_url_parse("https://www.google.com/search?q=embedded+browser&hl=en", &u));
    ASSERT(strcmp(u.host, "www.google.com") == 0);
    ASSERT(strcmp(u.path, "/search") == 0);
    ASSERT(strstr(u.query, "q=embedded+browser") != NULL);
}

TEST(test_parse_github_url) {
    eb_url_t u;
    ASSERT(eb_url_parse("https://github.com/embeddedos-org/eBrowser/blob/main/README.md", &u));
    ASSERT(strcmp(u.host, "github.com") == 0);
    ASSERT(strstr(u.path, "eBrowser") != NULL);
}

TEST(test_parse_localhost) {
    eb_url_t u;
    ASSERT(eb_url_parse("http://127.0.0.1:8080/", &u));
    ASSERT(strcmp(u.host, "127.0.0.1") == 0);
    ASSERT(u.port == 8080);
}

int main(void) {
    printf("=== URL Parser Tests ===\n");
    RUN(test_default_port_http);
    RUN(test_default_port_https);
    RUN(test_default_port_ftp);
    RUN(test_default_port_unknown);
    RUN(test_default_port_null);
    RUN(test_parse_full_url);
    RUN(test_parse_http_simple);
    RUN(test_parse_https_default_port);
    RUN(test_parse_no_path);
    RUN(test_parse_root_path);
    RUN(test_parse_deep_path);
    RUN(test_parse_query_only);
    RUN(test_parse_fragment_only);
    RUN(test_parse_custom_port);
    RUN(test_parse_high_port);
    RUN(test_parse_subdomain);
    RUN(test_parse_no_scheme);
    RUN(test_parse_case_insensitive_scheme);
    RUN(test_parse_null);
    RUN(test_parse_ftp_url);
    RUN(test_to_string_basic);
    RUN(test_to_string_with_port);
    RUN(test_to_string_default_port_omitted);
    RUN(test_to_string_with_query);
    RUN(test_to_string_with_fragment);
    RUN(test_resolve_absolute_url);
    RUN(test_resolve_absolute_path);
    RUN(test_resolve_relative_path);
    RUN(test_resolve_null);
    RUN(test_resolve_clears_query_fragment);
    RUN(test_parse_google_search);
    RUN(test_parse_github_url);
    RUN(test_parse_localhost);
    printf("\nResults: %d passed, %d failed\n", s_pass, s_fail);
    return s_fail > 0 ? 1 : 0;
}
