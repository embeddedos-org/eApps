# 🧩 Browser Extensions — EoS In-Browser Tools

[![Chrome](https://img.shields.io/badge/Chrome-Extension-green?logo=googlechrome)]()
[![Firefox](https://img.shields.io/badge/Firefox-Add--on-orange?logo=firefox)]()
[![Safari](https://img.shields.io/badge/Safari-Extension-blue?logo=safari)]()
[![Edge](https://img.shields.io/badge/Edge-Extension-blue?logo=microsoftedge)]()

**Lightweight browser extensions that bring EoS tools directly into your browser toolbar.**

Each extension works across Chrome, Firefox, Safari, and Edge via WebExtensions API.

---

## 📦 Extensions (20 Browser Extensions)

| Extension | Description | Popup | Sidebar | Content Script | Status |
|-----------|-------------|-------|---------|----------------|--------|
| **ecal** | Quick calendar view & event add | ✅ | ✅ | — | 🔲 Planned |
| **echat** | Browser-integrated messaging | ✅ | ✅ | — | 🔲 Planned |
| **enote** | Quick notes from any page | ✅ | ✅ | ✅ Highlight-to-note | 🔲 Planned |
| **epdf** | In-browser PDF tools | ✅ | — | ✅ PDF override | 🔲 Planned |
| **ebot** | AI assistant sidebar | ✅ | ✅ | ✅ Page context | 🔲 Planned |
| **econverter** | Quick unit/currency convert | ✅ | — | ✅ Auto-detect | 🔲 Planned |
| **eclock** | World clock in toolbar | ✅ | — | — | 🔲 Planned |
| **etimer** | Pomodoro/timer in toolbar | ✅ | — | — | 🔲 Planned |
| **etools** | Utility toolkit (color picker, ruler) | ✅ | ✅ | ✅ | 🔲 Planned |
| **etrack** | Task tracker sidebar | ✅ | ✅ | — | 🔲 Planned |
| **eguard** | Privacy & ad blocker | — | — | ✅ Block/filter | 🔲 Planned |
| **efiles** | Quick file access panel | ✅ | ✅ | — | 🔲 Planned |
| **emusic** | Music controls in toolbar | ✅ | — | ✅ Media control | 🔲 Planned |
| **eplay** | Media player controls | ✅ | — | ✅ Media control | 🔲 Planned |
| **evpn** | VPN toggle & status | ✅ | — | — | 🔲 Planned |
| **ezip** | Download & compress files | ✅ | — | ✅ Download intercept | 🔲 Planned |
| **esurfer** | Tab & session manager | ✅ | ✅ | — | 🔲 Planned |
| **eweb** | Page inspector & tools | ✅ | ✅ | ✅ DOM tools | 🔲 Planned |
| **egallery** | Image saver & gallery | ✅ | ✅ | ✅ Image detect | 🔲 Planned |
| **eviewer** | Document quick viewer | ✅ | — | ✅ File preview | 🔲 Planned |

---

## 🏗️ Architecture

```
browser-extensions/
├── README.md
├── shared/                     # Shared extension code
│   ├── background-common.js    # Common background script
│   ├── popup-shell.html        # Shared popup template
│   ├── styles/                 # Shared CSS
│   └── icons/                  # Shared icon set
├── ecal/
│   ├── manifest.json           # WebExtensions manifest v3
│   ├── background.js           # Service worker
│   ├── popup/
│   │   ├── popup.html
│   │   ├── popup.js
│   │   └── popup.css
│   ├── sidebar/                # Optional sidebar panel
│   ├── content/                # Content scripts (if needed)
│   ├── icons/
│   └── _locales/               # i18n
└── [extension]/
    └── ...
```

## 🚀 Quick Start

```bash
# Load in Chrome
# 1. Navigate to chrome://extensions
# 2. Enable "Developer mode"
# 3. Click "Load unpacked" → select browser-extensions/ecal/

# Load in Firefox
# 1. Navigate to about:debugging#/runtime/this-firefox
# 2. Click "Load Temporary Add-on" → select manifest.json

# Package for distribution
cd browser-extensions/ecal && zip -r ecal-chrome.zip . -x "*.git*"
```

## 📤 Distribution

| Browser | Format | Store |
|---------|--------|-------|
| Chrome | `.zip` / `.crx` | Chrome Web Store |
| Firefox | `.xpi` | Firefox Add-ons (AMO) |
| Safari | Xcode project | Mac App Store |
| Edge | `.zip` | Edge Add-ons |

## 📄 License

[Apache License 2.0](../LICENSE)
