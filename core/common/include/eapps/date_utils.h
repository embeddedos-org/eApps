// SPDX-License-Identifier: MIT
// Copyright (c) 2026 EoS Project

#ifndef EAPPS_DATE_UTILS_H
#define EAPPS_DATE_UTILS_H

#include <stddef.h>
#include <stdint.h>
#include <time.h>

void eapps_date_format(time_t t, const char *fmt, char *buf, size_t buf_len);
void eapps_time_ago(time_t t, char *buf, size_t buf_len);
void eapps_format_duration(uint32_t seconds, char *buf, size_t buf_len);

#endif /* EAPPS_DATE_UTILS_H */
