// SPDX-License-Identifier: MIT
// Copyright (c) 2026 EoS Project

#ifndef EAPPS_EXPR_PARSER_H
#define EAPPS_EXPR_PARSER_H

#include <stdbool.h>

typedef enum {
    EAPPS_EXPR_OK,
    EAPPS_EXPR_ERR_SYNTAX,
    EAPPS_EXPR_ERR_DIV_ZERO,
    EAPPS_EXPR_ERR_UNKNOWN_FUNC,
    EAPPS_EXPR_ERR_PAREN_MISMATCH,
    EAPPS_EXPR_ERR_EMPTY,
} eapps_expr_error_t;

typedef struct {
    double memory;
    bool   has_memory;
} eapps_expr_ctx_t;

void               eapps_expr_ctx_init(eapps_expr_ctx_t *ctx);
eapps_expr_error_t eapps_expr_eval(eapps_expr_ctx_t *ctx, const char *expr, double *result);
void               eapps_expr_mem_clear(eapps_expr_ctx_t *ctx);
void               eapps_expr_mem_recall(eapps_expr_ctx_t *ctx, double *out);
void               eapps_expr_mem_add(eapps_expr_ctx_t *ctx, double val);
void               eapps_expr_mem_sub(eapps_expr_ctx_t *ctx, double val);
const char        *eapps_expr_error_str(eapps_expr_error_t err);

#endif /* EAPPS_EXPR_PARSER_H */
