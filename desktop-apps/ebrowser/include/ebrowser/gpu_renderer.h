// SPDX-License-Identifier: MIT
#ifndef eBrowser_GPU_RENDERER_H
#define eBrowser_GPU_RENDERER_H

#include <stdbool.h>
#include "eBrowser/layout.h"

typedef enum {
    EB_GPU_BACKEND_NONE,
    EB_GPU_BACKEND_OPENGL_ES2,
    EB_GPU_BACKEND_VULKAN
} eb_gpu_backend_t;

typedef struct {
    eb_gpu_backend_t backend;
    int              width, height;
    bool             initialized;
    unsigned int     texture_atlas_id;
} eb_gpu_ctx_t;

bool eb_gpu_init(eb_gpu_ctx_t *ctx, eb_gpu_backend_t backend, int w, int h);
void eb_gpu_clear(eb_gpu_ctx_t *ctx, float r, float g, float b, float a);
void eb_gpu_render_box(eb_gpu_ctx_t *ctx, const eb_layout_box_t *box);
void eb_gpu_present(eb_gpu_ctx_t *ctx);
void eb_gpu_resize(eb_gpu_ctx_t *ctx, int w, int h);
void eb_gpu_deinit(eb_gpu_ctx_t *ctx);
bool eb_gpu_is_available(void);

#endif
