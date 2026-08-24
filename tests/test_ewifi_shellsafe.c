// SPDX-License-Identifier: MIT
// Copyright (c) 2026 EoS Project

/**
 * @file test_ewifi_shellsafe.c
 * @brief Regression tests for eWiFi shell-argument hardening.
 *
 * eWiFi drives nmcli, netsh and networksetup through system()/popen() with
 * SSIDs and passphrases as arguments. An SSID is chosen by whoever broadcasts
 * it, so it is untrusted input. It used to be interpolated into a
 * double-quoted shell string, which let an SSID of
 *
 *     x" ; touch /tmp/... ; "
 *
 * close the quote and execute a second command. The first case below asserts
 * that this no longer happens, by running the constructed command for real and
 * checking the side effect never occurred.
 */

#include "eapps_test.h"
#include "ewifi.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifndef _WIN32
#include <unistd.h>
#endif

#define PWNED_MARKER "/tmp/eapps_ewifi_shellsafe_marker"

/**
 * Quote @p in, hand it to a real shell as an argument to printf, and report
 * whether the command saw exactly the original bytes.
 */
static int shell_round_trip(const char *in)
{
#ifdef _WIN32
    (void)in;
    return 0;   /* POSIX quoting is not the Windows path; see the allowlist. */
#else
    char quoted[512], cmd[1024], got[512];
    size_t n;
    FILE *fp;

    if (!ewifi_shell_quote_posix(in, quoted, sizeof(quoted))) return -1;
    snprintf(cmd, sizeof(cmd), "printf %%s %s", quoted);

    fp = popen(cmd, "r");
    if (!fp) return -2;
    n = fread(got, 1, sizeof(got) - 1, fp);
    got[n] = '\0';
    pclose(fp);

    return strcmp(got, in) == 0 ? 0 : 1;
#endif
}

static void test_injection_does_not_execute(void)
{
#ifndef _WIN32
    const char *evil = "x\" ; touch " PWNED_MARKER " ; \"";
    char quoted[512], cmd[1024];

    remove(PWNED_MARKER);

    ASSERT_TRUE(ewifi_shell_quote_posix(evil, quoted, sizeof(quoted)),
                "hostile SSID can be quoted");

    snprintf(cmd, sizeof(cmd), "printf %%s %s >/dev/null 2>&1", quoted);
    if (system(cmd) == -1) { /* shell unavailable; the assert below still holds */ }

    ASSERT_TRUE(access(PWNED_MARKER, F_OK) != 0,
                "command injected via SSID did not execute");
    remove(PWNED_MARKER);
#endif
}

static void test_round_trip_preserves_bytes(void)
{
    /* Every one of these is a legal WPA passphrase character or a plausible
     * SSID, and every one is shell metacharacter soup. */
    static const char *cases[] = {
        "PlainSSID", "My Home 5G", "cafe-wifi_2.4",
        "it's mine", "a'b'c", "''",
        "$HOME", "`id`", "$(id)", "${x}",
        "semi;colon", "pipe|it", "amp&&and", "redir>out", "in<file",
        "back\\slash", "quote\"dq", "star*glob", "quest?ion",
        "tilde~x", "hash#x", "bang!x", "(paren)", "{brace}", "[brack]",
        "pct%s", "at@x", "caret^x", "colon:x", "eq=x", "plus+x",
    };
    unsigned i;

    for (i = 0; i < sizeof(cases) / sizeof(cases[0]); i++) {
        char label[192];
        snprintf(label, sizeof(label),
                 "shell round trip preserves \"%s\"", cases[i]);
        ASSERT_EQ(shell_round_trip(cases[i]), 0, label);
    }
}

static void test_quote_refuses_unsafe_input(void)
{
    char out[512];
    char tiny[8];

    ASSERT_FALSE(ewifi_shell_quote_posix("has\nnewline", out, sizeof(out)),
                 "newline is refused");
    ASSERT_FALSE(ewifi_shell_quote_posix("has\rreturn", out, sizeof(out)),
                 "carriage return is refused");
    ASSERT_FALSE(ewifi_shell_quote_posix(NULL, out, sizeof(out)),
                 "NULL input is refused");
    ASSERT_FALSE(ewifi_shell_quote_posix("abc", NULL, sizeof(out)),
                 "NULL output is refused");
    ASSERT_FALSE(ewifi_shell_quote_posix("abc", out, 2),
                 "buffer too small for quotes is refused");
    /* Each single quote expands to four bytes, so this must refuse rather
     * than run past the end of the buffer. */
    ASSERT_FALSE(ewifi_shell_quote_posix("''''''''", tiny, sizeof(tiny)),
                 "overflow from quote expansion is refused");

    /* An empty string is still a valid argument: it must quote to ''. */
    ASSERT_TRUE(ewifi_shell_quote_posix("", out, sizeof(out)),
                "empty string is quotable");
    ASSERT_STR_EQ(out, "''", "empty string quotes to two single quotes");
}

static void test_windows_allowlist(void)
{
    ASSERT_TRUE(ewifi_shell_arg_is_safe_win("Home_WiFi-5G 2.4"),
                "benign SSID accepted by the Windows allowlist");
    ASSERT_FALSE(ewifi_shell_arg_is_safe_win("%PATH%"),
                 "cmd.exe variable expansion rejected");
    ASSERT_FALSE(ewifi_shell_arg_is_safe_win("a\"b"), "double quote rejected");
    ASSERT_FALSE(ewifi_shell_arg_is_safe_win("a&b"), "ampersand rejected");
    ASSERT_FALSE(ewifi_shell_arg_is_safe_win("a|b"), "pipe rejected");
    ASSERT_FALSE(ewifi_shell_arg_is_safe_win("a^b"), "caret rejected");
    ASSERT_FALSE(ewifi_shell_arg_is_safe_win("a>b"), "redirect rejected");
    ASSERT_FALSE(ewifi_shell_arg_is_safe_win(""), "empty string rejected");
    ASSERT_FALSE(ewifi_shell_arg_is_safe_win(NULL), "NULL rejected");
}

static void test_connect_refuses_hostile_ssid(void)
{
    /* ewifi_ac_connect() must refuse rather than build a command from input it
     * cannot quote. A newline cannot be carried safely, so it is rejected. */
    ASSERT_FALSE(ewifi_ac_connect("bad\nssid", "pass"),
                 "connect refuses an SSID containing a newline");
    ASSERT_FALSE(ewifi_ac_connect(NULL, "pass"),
                 "connect refuses a NULL SSID");
    ASSERT_FALSE(ewifi_ac_connect("", "pass"),
                 "connect refuses an empty SSID");
}

int main(void)
{
    TEST_SUITE("eWiFi shell-argument hardening");

    test_injection_does_not_execute();
    test_round_trip_preserves_bytes();
    test_quote_refuses_unsafe_input();
    test_windows_allowlist();
    test_connect_refuses_hostile_ssid();

    TEST_RESULTS();
    TEST_EXIT();
}
