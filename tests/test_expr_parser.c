// SPDX-License-Identifier: MIT
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "../core/common/include/eapps/expr_parser.h"

#define EAPPS_ASSERT(cond, msg) do { \
    if (!(cond)) { fprintf(stderr, "FAIL: %s (%s:%d)\n", msg, __FILE__, __LINE__); failures++; } \
    else { passes++; } \
} while(0)

static int passes = 0, failures = 0;

static void test_basic_arithmetic(void) {
    eapps_expr_ctx_t ctx;
    eapps_expr_ctx_init(&ctx);
    double r;

    EAPPS_ASSERT(eapps_expr_eval(&ctx, "2+3", &r) == EAPPS_EXPR_OK && r == 5.0, "2+3=5");
    EAPPS_ASSERT(eapps_expr_eval(&ctx, "10-4", &r) == EAPPS_EXPR_OK && r == 6.0, "10-4=6");
    EAPPS_ASSERT(eapps_expr_eval(&ctx, "3*7", &r) == EAPPS_EXPR_OK && r == 21.0, "3*7=21");
    EAPPS_ASSERT(eapps_expr_eval(&ctx, "20/4", &r) == EAPPS_EXPR_OK && r == 5.0, "20/4=5");
    EAPPS_ASSERT(eapps_expr_eval(&ctx, "7%3", &r) == EAPPS_EXPR_OK && r == 1.0, "7%3=1");
}

static void test_precedence(void) {
    eapps_expr_ctx_t ctx;
    eapps_expr_ctx_init(&ctx);
    double r;

    EAPPS_ASSERT(eapps_expr_eval(&ctx, "2+3*4", &r) == EAPPS_EXPR_OK && r == 14.0, "2+3*4=14");
    EAPPS_ASSERT(eapps_expr_eval(&ctx, "(2+3)*4", &r) == EAPPS_EXPR_OK && r == 20.0, "(2+3)*4=20");
    EAPPS_ASSERT(eapps_expr_eval(&ctx, "2^3", &r) == EAPPS_EXPR_OK && r == 8.0, "2^3=8");
}

static void test_functions(void) {
    eapps_expr_ctx_t ctx;
    eapps_expr_ctx_init(&ctx);
    double r;

    EAPPS_ASSERT(eapps_expr_eval(&ctx, "sqrt(16)", &r) == EAPPS_EXPR_OK && r == 4.0, "sqrt(16)=4");
    EAPPS_ASSERT(eapps_expr_eval(&ctx, "abs(-5)", &r) == EAPPS_EXPR_OK && r == 5.0, "abs(-5)=5");
    EAPPS_ASSERT(eapps_expr_eval(&ctx, "sin(0)", &r) == EAPPS_EXPR_OK && fabs(r) < 0.001, "sin(0)=0");
    EAPPS_ASSERT(eapps_expr_eval(&ctx, "cos(0)", &r) == EAPPS_EXPR_OK && fabs(r - 1.0) < 0.001, "cos(0)=1");
    EAPPS_ASSERT(eapps_expr_eval(&ctx, "log(100)", &r) == EAPPS_EXPR_OK && fabs(r - 2.0) < 0.001, "log(100)=2");
}

static void test_errors(void) {
    eapps_expr_ctx_t ctx;
    eapps_expr_ctx_init(&ctx);
    double r;

    EAPPS_ASSERT(eapps_expr_eval(&ctx, "1/0", &r) == EAPPS_EXPR_ERR_DIV_ZERO, "div by zero");
    EAPPS_ASSERT(eapps_expr_eval(&ctx, "(1+2", &r) == EAPPS_EXPR_ERR_PAREN_MISMATCH, "paren mismatch");
    EAPPS_ASSERT(eapps_expr_eval(&ctx, "", &r) == EAPPS_EXPR_ERR_EMPTY, "empty expr");
    EAPPS_ASSERT(eapps_expr_eval(&ctx, "foo(1)", &r) == EAPPS_EXPR_ERR_UNKNOWN_FUNC, "unknown func");
}

static void test_constants(void) {
    eapps_expr_ctx_t ctx;
    eapps_expr_ctx_init(&ctx);
    double r;

    EAPPS_ASSERT(eapps_expr_eval(&ctx, "pi", &r) == EAPPS_EXPR_OK && fabs(r - 3.14159) < 0.001, "pi");
    EAPPS_ASSERT(eapps_expr_eval(&ctx, "e", &r) == EAPPS_EXPR_OK && fabs(r - 2.71828) < 0.001, "e");
}

static void test_memory(void) {
    eapps_expr_ctx_t ctx;
    eapps_expr_ctx_init(&ctx);
    double out;

    eapps_expr_mem_add(&ctx, 10.0);
    eapps_expr_mem_recall(&ctx, &out);
    EAPPS_ASSERT(out == 10.0, "mem add 10");

    eapps_expr_mem_sub(&ctx, 3.0);
    eapps_expr_mem_recall(&ctx, &out);
    EAPPS_ASSERT(out == 7.0, "mem sub 3");

    eapps_expr_mem_clear(&ctx);
    eapps_expr_mem_recall(&ctx, &out);
    EAPPS_ASSERT(out == 0.0, "mem clear");
}

int main(void) {
    test_basic_arithmetic();
    test_precedence();
    test_functions();
    test_errors();
    test_constants();
    test_memory();
    printf("test_expr_parser: %d passed, %d failed\n", passes, failures);
    return failures > 0 ? 1 : 0;
}
