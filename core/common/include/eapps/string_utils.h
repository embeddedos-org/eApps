// SPDX-License-Identifier: MIT
// Copyright (c) 2026 EoS Project

#ifndef EAPPS_STRING_UTILS_H
#define EAPPS_STRING_UTILS_H

#include <stddef.h>
#include <stdbool.h>
#include <stdint.h>

void   eapps_str_truncate(const char *src, char *dst, size_t max_len);
void   eapps_hexdump(const uint8_t *data, size_t len, char *out, size_t out_len);
int    eapps_base64_encode(const uint8_t *src, size_t src_len, char *dst, size_t dst_len);
int    eapps_base64_decode(const char *src, uint8_t *dst, size_t dst_len);
void   eapps_str_to_lower(char *str);
void   eapps_str_to_upper(char *str);
bool   eapps_str_contains_ci(const char *haystack, const char *needle);

#endif /* EAPPS_STRING_UTILS_H */
