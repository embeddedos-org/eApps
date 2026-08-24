// SPDX-License-Identifier: MIT
// eWiFi — shell argument quoting for the platform network-manager commands

/**
 * @file ewifi_shellsafe.c
 * @brief Safe construction of shell arguments from untrusted network data.
 *
 * The platform connect and credential-read paths invoke nmcli, netsh and
 * networksetup through system()/popen(). Their arguments are SSIDs and
 * passphrases, and an SSID is attacker-controlled — anyone in radio range can
 * broadcast one. Interpolating it into a double-quoted shell string, as this
 * code previously did, let an SSID such as
 *
 *     x" ; rm -rf ~ ; "
 *
 * close the quote and run arbitrary commands.
 */

#include "ewifi.h"

#include <string.h>

bool ewifi_shell_quote_posix(const char *in, char *out, size_t out_sz)
{
    size_t o = 0;
    size_t i;

    if (!in || !out || out_sz < 3) return false;

    /* Single quotes suppress every form of shell expansion, so the only
     * character needing care is the single quote itself: close the quoted run,
     * emit an escaped quote, reopen. This preserves the argument byte for byte,
     * which matters because a WPA passphrase may legitimately contain any
     * printable character. */
    out[o++] = '\'';
    for (i = 0; in[i] != '\0'; i++) {
        unsigned char c = (unsigned char)in[i];

        /* A newline or NUL cannot be carried safely through these command
         * lines, and no valid SSID or passphrase contains one. */
        if (c == '\n' || c == '\r') return false;

        if (c == '\'') {
            if (o + 4 >= out_sz) return false;
            out[o++] = '\'';
            out[o++] = '\\';
            out[o++] = '\'';
            out[o++] = '\'';
        } else {
            if (o + 1 >= out_sz) return false;
            out[o++] = (char)c;
        }
    }
    if (o + 2 > out_sz) return false;
    out[o++] = '\'';
    out[o] = '\0';
    return true;
}

bool ewifi_shell_arg_is_safe_win(const char *in)
{
    size_t i;

    if (!in || in[0] == '\0') return false;

    /* cmd.exe quoting cannot be made watertight by escaping alone — the parser
     * expands %VAR% inside double quotes, and the caret escape interacts with
     * quoting in ways that differ between cmd.exe and the called program's own
     * argv parsing. So this path fails closed on an allowlist instead. It
     * rejects some legitimate SSIDs; that is the intended trade. */
    for (i = 0; in[i] != '\0'; i++) {
        unsigned char c = (unsigned char)in[i];
        if (c >= 'A' && c <= 'Z') continue;
        if (c >= 'a' && c <= 'z') continue;
        if (c >= '0' && c <= '9') continue;
        if (c == ' ' || c == '.' || c == '_' || c == '-') continue;
        return false;
    }
    return true;
}
