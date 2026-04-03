// SPDX-License-Identifier: MIT
#include "eapps/math_utils.h"
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

int eapps_clamp(int val, int min_val, int max_val) {
    if (val < min_val) return min_val;
    if (val > max_val) return max_val;
    return val;
}

float eapps_clampf(float val, float min_val, float max_val) {
    if (val < min_val) return min_val;
    if (val > max_val) return max_val;
    return val;
}

float eapps_lerp(float a, float b, float t) {
    return a + (b - a) * t;
}

float eapps_map(float val, float in_min, float in_max, float out_min, float out_max) {
    return (val - in_min) / (in_max - in_min) * (out_max - out_min) + out_min;
}

void eapps_format_file_size(uint64_t bytes, char *buf, size_t buf_len) {
    if (!buf || buf_len == 0) return;
    const char *units[] = {"B", "KB", "MB", "GB", "TB"};
    int u = 0;
    double size = (double)bytes;
    while (size >= 1024.0 && u < 4) { size /= 1024.0; u++; }
    if (u == 0) snprintf(buf, buf_len, "%d B", (int)bytes);
    else        snprintf(buf, buf_len, "%.1f %s", size, units[u]);
}

float eapps_deg_to_rad(float deg) {
    return deg * (float)(M_PI / 180.0);
}

float eapps_rad_to_deg(float rad) {
    return rad * (float)(180.0 / M_PI);
}

int eapps_rand_range(int min_val, int max_val) {
    if (min_val >= max_val) return min_val;
    return min_val + rand() % (max_val - min_val + 1);
}
