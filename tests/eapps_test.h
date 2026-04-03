// SPDX-License-Identifier: MIT
// eApps Test Framework — shared macros for all test files
#ifndef EAPPS_TEST_H
#define EAPPS_TEST_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

/* ---- Color Output ---- */
#ifdef _WIN32
#define T_GREEN  ""
#define T_RED    ""
#define T_YELLOW ""
#define T_RESET  ""
#else
#define T_GREEN  "\033[32m"
#define T_RED    "\033[31m"
#define T_YELLOW "\033[33m"
#define T_RESET  "\033[0m"
#endif

/* ---- Counters ---- */
static int t_passes = 0;
static int t_failures = 0;
static const char *t_current_suite = "";

/* ---- Suite Management ---- */
#define TEST_SUITE(name) \
    do { t_current_suite = name; \
         printf("\n=== %s ===\n", name); } while(0)

#define TEST_RESULTS() \
    do { printf("\n--- Results: %s%d passed%s, %s%d failed%s ---\n", \
         T_GREEN, t_passes, T_RESET, \
         t_failures ? T_RED : T_GREEN, t_failures, T_RESET); \
    } while(0)

#define TEST_EXIT() \
    do { TEST_RESULTS(); return t_failures > 0 ? 1 : 0; } while(0)

/* ---- Assertions ---- */
#define ASSERT_TRUE(cond, msg) do { \
    if (!(cond)) { \
        fprintf(stderr, "%sFAIL%s: %s (%s:%d)\n", T_RED, T_RESET, msg, __FILE__, __LINE__); \
        t_failures++; \
    } else { t_passes++; } \
} while(0)

#define ASSERT_FALSE(cond, msg) ASSERT_TRUE(!(cond), msg)

#define ASSERT_EQ(a, b, msg) do { \
    if ((a) != (b)) { \
        fprintf(stderr, "%sFAIL%s: %s — got %d, expected %d (%s:%d)\n", \
                T_RED, T_RESET, msg, (int)(a), (int)(b), __FILE__, __LINE__); \
        t_failures++; \
    } else { t_passes++; } \
} while(0)

#define ASSERT_NEQ(a, b, msg) do { \
    if ((a) == (b)) { \
        fprintf(stderr, "%sFAIL%s: %s — values should differ (%s:%d)\n", \
                T_RED, T_RESET, msg, __FILE__, __LINE__); \
        t_failures++; \
    } else { t_passes++; } \
} while(0)

#define ASSERT_STR_EQ(a, b, msg) do { \
    if (strcmp((a), (b)) != 0) { \
        fprintf(stderr, "%sFAIL%s: %s — got \"%s\", expected \"%s\" (%s:%d)\n", \
                T_RED, T_RESET, msg, (a), (b), __FILE__, __LINE__); \
        t_failures++; \
    } else { t_passes++; } \
} while(0)

#define ASSERT_NOT_NULL(ptr, msg) do { \
    if ((ptr) == NULL) { \
        fprintf(stderr, "%sFAIL%s: %s — expected non-NULL (%s:%d)\n", \
                T_RED, T_RESET, msg, __FILE__, __LINE__); \
        t_failures++; \
    } else { t_passes++; } \
} while(0)

#define ASSERT_NULL(ptr, msg) do { \
    if ((ptr) != NULL) { \
        fprintf(stderr, "%sFAIL%s: %s — expected NULL (%s:%d)\n", \
                T_RED, T_RESET, msg, __FILE__, __LINE__); \
        t_failures++; \
    } else { t_passes++; } \
} while(0)

#define ASSERT_GT(a, b, msg) ASSERT_TRUE((a) > (b), msg)
#define ASSERT_GTE(a, b, msg) ASSERT_TRUE((a) >= (b), msg)
#define ASSERT_LT(a, b, msg) ASSERT_TRUE((a) < (b), msg)
#define ASSERT_LTE(a, b, msg) ASSERT_TRUE((a) <= (b), msg)

#define ASSERT_FLOAT_EQ(a, b, eps, msg) do { \
    if (fabs((double)(a) - (double)(b)) > (eps)) { \
        fprintf(stderr, "%sFAIL%s: %s — got %f, expected %f (%s:%d)\n", \
                T_RED, T_RESET, msg, (double)(a), (double)(b), __FILE__, __LINE__); \
        t_failures++; \
    } else { t_passes++; } \
} while(0)

#endif /* EAPPS_TEST_H */
