// SPDX-License-Identifier: MIT
#include "eapps/expr_parser.h"
#include <math.h>
#include <string.h>
#include <ctype.h>
#include <stdlib.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif
#ifndef M_E
#define M_E 2.71828182845904523536
#endif

typedef struct {
    const char *str;
    int         pos;
    eapps_expr_error_t err;
} parser_t;

static double parse_expr(parser_t *p);

static void skip_ws(parser_t *p) {
    while (p->str[p->pos] && isspace((unsigned char)p->str[p->pos])) p->pos++;
}

static double parse_number(parser_t *p) {
    skip_ws(p);
    const char *start = p->str + p->pos;
    char *end;
    double val = strtod(start, &end);
    if (end == start) { p->err = EAPPS_EXPR_ERR_SYNTAX; return 0; }
    p->pos += (int)(end - start);
    return val;
}

static double parse_func(parser_t *p, const char *name) {
    skip_ws(p);
    if (p->str[p->pos] != '(') { p->err = EAPPS_EXPR_ERR_SYNTAX; return 0; }
    p->pos++;
    double arg = parse_expr(p);
    if (p->err != EAPPS_EXPR_OK) return 0;
    skip_ws(p);
    if (p->str[p->pos] != ')') { p->err = EAPPS_EXPR_ERR_PAREN_MISMATCH; return 0; }
    p->pos++;

    if (strcmp(name, "sin") == 0) return sin(arg);
    if (strcmp(name, "cos") == 0) return cos(arg);
    if (strcmp(name, "tan") == 0) return tan(arg);
    if (strcmp(name, "log") == 0) return log10(arg);
    if (strcmp(name, "ln") == 0)  return log(arg);
    if (strcmp(name, "sqrt") == 0) return sqrt(arg);
    if (strcmp(name, "abs") == 0) return fabs(arg);
    if (strcmp(name, "exp") == 0) return exp(arg);
    p->err = EAPPS_EXPR_ERR_UNKNOWN_FUNC;
    return 0;
}

static double parse_primary(parser_t *p) {
    skip_ws(p);
    if (p->err != EAPPS_EXPR_OK) return 0;

    char c = p->str[p->pos];

    if (c == '(') {
        p->pos++;
        double val = parse_expr(p);
        if (p->err != EAPPS_EXPR_OK) return 0;
        skip_ws(p);
        if (p->str[p->pos] != ')') { p->err = EAPPS_EXPR_ERR_PAREN_MISMATCH; return 0; }
        p->pos++;
        return val;
    }

    if (c == '-') {
        p->pos++;
        return -parse_primary(p);
    }
    if (c == '+') {
        p->pos++;
        return parse_primary(p);
    }

    if (isalpha((unsigned char)c)) {
        char name[16];
        int ni = 0;
        while (isalpha((unsigned char)p->str[p->pos]) && ni < 15) {
            name[ni++] = p->str[p->pos++];
        }
        name[ni] = '\0';

        if (strcmp(name, "pi") == 0) return M_PI;
        if (strcmp(name, "e") == 0)  return M_E;

        return parse_func(p, name);
    }

    return parse_number(p);
}

static double parse_power(parser_t *p) {
    double base = parse_primary(p);
    if (p->err != EAPPS_EXPR_OK) return 0;
    skip_ws(p);
    if (p->str[p->pos] == '^') {
        p->pos++;
        double exp_val = parse_power(p);
        if (p->err != EAPPS_EXPR_OK) return 0;
        return pow(base, exp_val);
    }
    return base;
}

static double parse_term(parser_t *p) {
    double left = parse_power(p);
    if (p->err != EAPPS_EXPR_OK) return 0;
    while (1) {
        skip_ws(p);
        char c = p->str[p->pos];
        if (c == '*') { p->pos++; left *= parse_power(p); }
        else if (c == '/') {
            p->pos++;
            double d = parse_power(p);
            if (p->err != EAPPS_EXPR_OK) return 0;
            if (d == 0.0) { p->err = EAPPS_EXPR_ERR_DIV_ZERO; return 0; }
            left /= d;
        } else if (c == '%') {
            p->pos++;
            double d = parse_power(p);
            if (p->err != EAPPS_EXPR_OK) return 0;
            if (d == 0.0) { p->err = EAPPS_EXPR_ERR_DIV_ZERO; return 0; }
            left = fmod(left, d);
        } else break;
        if (p->err != EAPPS_EXPR_OK) return 0;
    }
    return left;
}

static double parse_expr(parser_t *p) {
    double left = parse_term(p);
    if (p->err != EAPPS_EXPR_OK) return 0;
    while (1) {
        skip_ws(p);
        char c = p->str[p->pos];
        if (c == '+') { p->pos++; left += parse_term(p); }
        else if (c == '-') { p->pos++; left -= parse_term(p); }
        else break;
        if (p->err != EAPPS_EXPR_OK) return 0;
    }
    return left;
}

void eapps_expr_ctx_init(eapps_expr_ctx_t *ctx) {
    if (!ctx) return;
    ctx->memory = 0.0;
    ctx->has_memory = false;
}

eapps_expr_error_t eapps_expr_eval(eapps_expr_ctx_t *ctx, const char *expr, double *result) {
    (void)ctx;
    if (!expr || !result) return EAPPS_EXPR_ERR_EMPTY;
    while (*expr && isspace((unsigned char)*expr)) expr++;
    if (*expr == '\0') return EAPPS_EXPR_ERR_EMPTY;

    parser_t p = { .str = expr, .pos = 0, .err = EAPPS_EXPR_OK };
    *result = parse_expr(&p);
    if (p.err != EAPPS_EXPR_OK) return p.err;
    skip_ws(&p);
    if (p.str[p.pos] != '\0') return EAPPS_EXPR_ERR_SYNTAX;
    return EAPPS_EXPR_OK;
}

void eapps_expr_mem_clear(eapps_expr_ctx_t *ctx) {
    if (!ctx) return;
    ctx->memory = 0.0;
    ctx->has_memory = false;
}

void eapps_expr_mem_recall(eapps_expr_ctx_t *ctx, double *out) {
    if (!ctx || !out) return;
    *out = ctx->memory;
}

void eapps_expr_mem_add(eapps_expr_ctx_t *ctx, double val) {
    if (!ctx) return;
    ctx->memory += val;
    ctx->has_memory = true;
}

void eapps_expr_mem_sub(eapps_expr_ctx_t *ctx, double val) {
    if (!ctx) return;
    ctx->memory -= val;
    ctx->has_memory = true;
}

const char *eapps_expr_error_str(eapps_expr_error_t err) {
    switch (err) {
        case EAPPS_EXPR_OK:               return "OK";
        case EAPPS_EXPR_ERR_SYNTAX:       return "Syntax error";
        case EAPPS_EXPR_ERR_DIV_ZERO:     return "Division by zero";
        case EAPPS_EXPR_ERR_UNKNOWN_FUNC: return "Unknown function";
        case EAPPS_EXPR_ERR_PAREN_MISMATCH: return "Parenthesis mismatch";
        case EAPPS_EXPR_ERR_EMPTY:        return "Empty expression";
        default:                           return "Unknown error";
    }
}
