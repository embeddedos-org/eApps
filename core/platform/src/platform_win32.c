// SPDX-License-Identifier: MIT
#include "eapps/platform.h"
#include <stdio.h>
#include <string.h>

#ifdef _WIN32
#include <windows.h>

int eapps_clipboard_get(char *buf, int buf_len) {
    if (!OpenClipboard(NULL)) return -1;
    HANDLE h = GetClipboardData(CF_TEXT);
    if (!h) { CloseClipboard(); return -1; }
    const char *data = (const char *)GlobalLock(h);
    if (!data) { CloseClipboard(); return -1; }
    snprintf(buf, (size_t)buf_len, "%s", data);
    GlobalUnlock(h);
    CloseClipboard();
    return (int)strlen(buf);
}

int eapps_clipboard_set(const char *text) {
    if (!OpenClipboard(NULL)) return -1;
    EmptyClipboard();
    size_t len = strlen(text) + 1;
    HGLOBAL h = GlobalAlloc(GMEM_MOVEABLE, len);
    if (!h) { CloseClipboard(); return -1; }
    memcpy(GlobalLock(h), text, len);
    GlobalUnlock(h);
    SetClipboardData(CF_TEXT, h);
    CloseClipboard();
    return 0;
}

void eapps_sysinfo_hostname(char *buf, int buf_len) {
    DWORD sz = (DWORD)buf_len;
    GetComputerNameA(buf, &sz);
}

void eapps_sysinfo_os(char *buf, int buf_len) {
    snprintf(buf, (size_t)buf_len, "Windows");
}

int eapps_sysinfo_cpu_count(void) {
    SYSTEM_INFO si;
    GetSystemInfo(&si);
    return (int)si.dwNumberOfProcessors;
}

uint64_t eapps_sysinfo_ram_total(void) {
    MEMORYSTATUSEX ms;
    ms.dwLength = sizeof(ms);
    GlobalMemoryStatusEx(&ms);
    return ms.ullTotalPhys;
}

void eapps_keepawake_enable(void) {
    SetThreadExecutionState(ES_CONTINUOUS | ES_DISPLAY_REQUIRED | ES_SYSTEM_REQUIRED);
}

void eapps_keepawake_disable(void) {
    SetThreadExecutionState(ES_CONTINUOUS);
}

int eapps_process_launch(const char *cmd) {
    return system(cmd);
}

uint32_t eapps_tick_get_ms(void) {
    return (uint32_t)GetTickCount64();
}
#endif
