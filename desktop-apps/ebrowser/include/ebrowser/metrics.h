// SPDX-License-Identifier: MIT
#ifndef eBrowser_METRICS_H
#define eBrowser_METRICS_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct {
    uint64_t parse_time_us;
    uint64_t layout_time_us;
    uint64_t render_time_us;
    uint64_t network_time_us;
    uint64_t js_time_us;
    uint32_t frame_count;
    uint32_t fps;
    size_t   memory_used;
    size_t   memory_peak;
    uint32_t alloc_count;
    uint32_t dom_node_count;
    uint32_t http_request_count;
} eb_metrics_t;

void     eb_metrics_init(eb_metrics_t *m);
void     eb_metrics_reset(eb_metrics_t *m);
void     eb_metrics_record_parse(eb_metrics_t *m, uint64_t us);
void     eb_metrics_record_layout(eb_metrics_t *m, uint64_t us);
void     eb_metrics_record_render(eb_metrics_t *m, uint64_t us);
void     eb_metrics_record_network(eb_metrics_t *m, uint64_t us);
void     eb_metrics_record_js(eb_metrics_t *m, uint64_t us);
void     eb_metrics_tick_frame(eb_metrics_t *m);
void     eb_metrics_print(const eb_metrics_t *m);

#endif
