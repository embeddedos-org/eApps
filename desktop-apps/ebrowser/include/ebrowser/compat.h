// SPDX-License-Identifier: MIT
// Cross-platform compatibility shims for eBrowser
#ifndef eBrowser_COMPAT_H
#define eBrowser_COMPAT_H

#ifdef _WIN32
#define strcasecmp  _stricmp
#define strncasecmp _strnicmp
#else
#include <strings.h>
#endif

#endif /* eBrowser_COMPAT_H */
