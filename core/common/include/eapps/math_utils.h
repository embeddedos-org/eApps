// SPDX-License-Identifier: MIT
// Copyright (c) 2026 EoS Project

#ifndef EAPPS_MATH_UTILS_H
#define EAPPS_MATH_UTILS_H

#include <stdint.h>
#include <stddef.h>

int    eapps_clamp(int val, int min_val, int max_val);
float  eapps_clampf(float val, float min_val, float max_val);
float  eapps_lerp(float a, float b, float t);
float  eapps_map(float val, float in_min, float in_max, float out_min, float out_max);
void   eapps_format_file_size(uint64_t bytes, char *buf, size_t buf_len);
float  eapps_deg_to_rad(float deg);
float  eapps_rad_to_deg(float rad);
int    eapps_rand_range(int min_val, int max_val);

#endif /* EAPPS_MATH_UTILS_H */
