// SPDX-License-Identifier: MIT
#include "eBrowser/gpu_renderer.h"
#include <string.h>
#include <stdio.h>

bool eb_gpu_is_available(void) { return false; }

bool eb_gpu_init(eb_gpu_ctx_t *ctx, eb_gpu_backend_t backend, int w, int h) {
    if (!ctx) return false;
    memset(ctx, 0, sizeof(eb_gpu_ctx_t));
    ctx->backend = backend;
    ctx->width = w;
    ctx->height = h;
    if (backend == EB_GPU_BACKEND_NONE) { ctx->initialized = true; return true; }
    ctx->initialized = false;
    return false;
}

void eb_gpu_clear(eb_gpu_ctx_t *ctx, float r, float g, float b, float a) {
    (void)ctx; (void)r; (void)g; (void)b; (void)a;
}

void eb_gpu_render_box(eb_gpu_ctx_t *ctx, const eb_layout_box_t *box) {
    (void)ctx; (void)box;
}

void eb_gpu_present(eb_gpu_ctx_t *ctx) { (void)ctx; }

void eb_gpu_resize(eb_gpu_ctx_t *ctx, int w, int h) {
    if (!ctx) return;
    ctx->width = w; ctx->height = h;
}

void eb_gpu_deinit(eb_gpu_ctx_t *ctx) {
    if (!ctx) return;
    ctx->initialized = false;
}
