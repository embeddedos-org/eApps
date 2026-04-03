// SPDX-License-Identifier: MIT
#include "ebowser/metrics.h"
#include <string.h>
#include <stdio.h>

void eb_metrics_init(eb_metrics_t *m) { if (m) memset(m, 0, sizeof(eb_metrics_t)); }
void eb_metrics_reset(eb_metrics_t *m) { if (m) memset(m, 0, sizeof(eb_metrics_t)); }
void eb_metrics_record_parse(eb_metrics_t *m, uint64_t us) { if (m) m->parse_time_us += us; }
void eb_metrics_record_layout(eb_metrics_t *m, uint64_t us) { if (m) m->layout_time_us += us; }
void eb_metrics_record_render(eb_metrics_t *m, uint64_t us) { if (m) m->render_time_us += us; }
void eb_metrics_record_network(eb_metrics_t *m, uint64_t us) { if (m) m->network_time_us += us; }
void eb_metrics_record_js(eb_metrics_t *m, uint64_t us) { if (m) m->js_time_us += us; }
void eb_metrics_tick_frame(eb_metrics_t *m) { if (m) m->frame_count++; }

void eb_metrics_print(const eb_metrics_t *m) {
    if (!m) return;
    printf("=== eBowser Metrics ===\n");
    printf("Parse: %llu us | Layout: %llu us | Render: %llu us\n",
           (unsigned long long)m->parse_time_us, (unsigned long long)m->layout_time_us,
           (unsigned long long)m->render_time_us);
    printf("Network: %llu us | JS: %llu us\n",
           (unsigned long long)m->network_time_us, (unsigned long long)m->js_time_us);
    printf("Frames: %u | Memory: %zu / %zu peak\n", m->frame_count, m->memory_used, m->memory_peak);
}
