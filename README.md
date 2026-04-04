# ⚡ eApps — EoS Unified Marketplace & App Store

[![Marketplace](https://img.shields.io/badge/🏪_Marketplace-Live-blue?logo=github)](https://embeddedos-org.github.io/eApps/)
[![License](https://img.shields.io/badge/License-Apache_2.0-green.svg)](LICENSE)
[![CI](https://img.shields.io/github/actions/workflow/status/embeddedos-org/eApps/ci-native.yml?label=CI&logo=github)](https://github.com/embeddedos-org/eApps/actions)

**One repository. Every EoS app. All platforms. Automated delivery.**

eApps is the unified marketplace, monorepo, and automated app store for the entire [EoS (Embedded Operating System)](https://github.com/embeddedos-org) ecosystem — **50 apps across 8 platform categories = 188 platform targets**. Native apps, desktop apps, mobile apps, web PWAs, browser extensions, dev tools, CLI tools, and enterprise deployments.

🌐 **Live App Store:** [embeddedos-org.github.io/eApps](https://embeddedos-org.github.io/eApps/)

---

## 🏗️ What's Inside

| Category | Folder | Count | Technologies | Artifacts |
|---|---|---|---|---|
| ⚙️ **Native Apps** | `apps/` | 46 | C + LVGL (cross-platform via CMake) | Binaries, WASM |
| 🖥️ **Desktop Apps** | `desktop-apps/` | 4 | Electron, Python/Tkinter, Python/QEMU, C/SDL2 | `.exe` `.dmg` `.AppImage` `.deb` `.eapp` |
| 📱 **Mobile Apps** | `mobile-apps/` | 32 | Flutter (Android + iOS) | `.apk` `.aab` `.ipa` (TestFlight) |
| 🌐 **Web Apps** | `web-apps/` | 34 | HTML5/JS/WASM PWA | GitHub Pages PWA |
| 🧩 **Browser Extensions** | `browser-extensions/` | 20 | WebExtensions Manifest V3 | `.zip` `.crx` `.xpi` |
| 🛠️ **Dev Tools** | `dev-tools/` | 14 | VS Code TS, JetBrains Kotlin, Vim | `.vsix` `.jar` |
| ⌨️ **CLI Tools** | `cli-tools/` | 22 | Node.js, Python | npm, pip, Homebrew |
| 🏢 **Enterprise** | `enterprise/` | 16 | Docker, Helm, MSI, MDM | Docker images, Helm charts, `.msi` |
| 🧩 **Legacy Extensions** | `extensions/` | 11 | Chrome, Firefox, Safari, VS Code, JetBrains, Obsidian, Slack, Raycast, GitHub, Google WS, Office 365 | `.zip` `.crx` `.xpi` `.vsix` |

> **Total: 50 apps × 8 platform categories = 188 platform targets**

### Headline Products

| Product | Description | Platforms |
|---|---|---|
| **eOffice** | Full office suite — eDocs, eSheets, eSlides, ePlanner, eNotes, eMail, eDrive, eConnect, eDB, eForms, eSway | Desktop, Web, Chrome, Firefox, Safari, VS Code, JetBrains, Obsidian, Slack, Raycast, GitHub, Google WS, Office 365 |
| **EoStudio** | Visual design IDE — UI, 3D, CAD, games, hardware, code generation | Windows, macOS, Linux |
| **EoSim** | Hardware & platform simulator — 63+ boards (ARM, RISC-V, ESP32, STM32, RPi, Jetson), QEMU, GUI renderers | Windows, macOS, Linux, Docker |
| **eBrowser** | Privacy-first web browser with custom rendering engine | Windows, macOS, Linux, EoS, WASM |
| **eServiceApps** | eRide, eSocial, eTrack, eTravel, eWallet | Android, iOS |

---

## 🌐 How Apps Are Hosted & Delivered

```
                    ┌─────────────────────────────────────────────┐
                    │   https://embeddedos-org.github.io/eApps/   │
                    │       GitHub Pages — App Store Frontend      │
                    │   Browse · Filter · Search · Download All    │
                    └──────────────────┬──────────────────────────┘
                                       │ reads
                                       ▼
                    ┌─────────────────────────────────────────────┐
                    │           data/apps.json                     │
                    │   Central catalog — auto-updated by CI/CD    │
                    └──────────────────┬──────────────────────────┘
                                       │ links to
                                       ▼
                    ┌─────────────────────────────────────────────┐
                    │         GitHub Releases (per app)            │
                    │  .zip .crx .xpi .vsix .exe .dmg .AppImage   │
                    │  .apk .aab .ipa — versioned artifacts       │
                    └─────────────────────────────────────────────┘
```

### Platform-Specific Hosting & Installation

| Platform | File Format | Hosted On | How Users Install |
|---|---|---|---|
| **Chrome** | `.zip` / `.crx` | GitHub Releases | Download → `chrome://extensions/` → "Load unpacked" |
| **Firefox** | `.xpi` | GitHub Releases | Download → `about:addons` → "Install from File" |
| **Safari** | `.zip` | GitHub Releases | Download → Enable in Safari Preferences |
| **VS Code** | `.vsix` | GitHub Releases + VS Code Marketplace | `code --install-extension eoffice.vsix` |
| **JetBrains** | `.jar` / `.zip` | GitHub Releases + JetBrains Marketplace | Install from disk in IDE settings |
| **Android** | `.apk` / `.aab` | GitHub Releases | Download APK → Allow "Unknown Sources" → Install |
| **iOS** | `.ipa` | TestFlight | Invite link → TestFlight app → Install |
| **Windows** | `.exe` | GitHub Releases | Download → Run installer (signed if configured) |
| **macOS** | `.dmg` | GitHub Releases | Download → Drag to Applications |
| **Linux** | `.AppImage` / `.deb` | GitHub Releases | Download → `chmod +x` → Run |
| **EoS** | `.eapp` | GitHub Releases | Built-in package manager |
| **Docker** | Docker image | Docker Hub | `docker pull embeddedos/eosim` |
| **Web/WASM** | HTML/JS/WASM | GitHub Pages | Visit URL directly in browser |

### Auto-Update Support

| Platform | Mechanism |
|---|---|
| Chrome | `updates/chrome-updates.xml` hosted on GitHub Pages |
| Firefox | `updates/firefox-updates.json` hosted on GitHub Pages |
| VS Code | VS Code Marketplace auto-updates (if published) |
| Desktop | Check GitHub Releases API for latest version |
| Mobile | GitHub Releases or store updates |

---

## 📂 Repository Structure

```
eApps/
├── index.html                      # 🏪 App Store website (GitHub Pages)
├── css/marketplace.css             # Store frontend styles
├── js/marketplace.js               # Dynamic app grid from apps.json
├── data/apps.json                  # 📋 Single source of truth for all listings
├── updates/                        # Auto-update manifests (Chrome XML, Firefox JSON)
│
├── extensions/                     # 🧩 Browser & editor extensions (from eOffice)
│   ├── browser/                    #   Chrome / Firefox / Safari
│   ├── vscode/                     #   VS Code extension
│   ├── jetbrains/                  #   JetBrains plugin
│   ├── obsidian/                   #   Obsidian plugin
│   ├── slack/                      #   Slack app
│   ├── raycast/                    #   Raycast extension
│   ├── github/                     #   GitHub App
│   ├── google-workspace/           #   Google Workspace add-on
│   └── office365/                  #   Office 365 add-in
│
├── desktop-apps/                   # 🖥️ Desktop applications
│   ├── eoffice/                    #   Electron app + 12 office suite apps + web apps
│   ├── eostudio/                   #   Python/Tkinter visual design IDE
│   ├── eosim/                      #   Python/QEMU hardware simulator (63+ platforms)
│   └── ebrowser/                   #   C/SDL2 browser engine
│
├── mobile-apps/                    # 📱 32 Flutter mobile apps (incl. eServiceApps)
├── web-apps/                       # 🌐 34 PWA web apps (HTML5/JS/WASM)
├── browser-extensions/             # 🧩 20 browser extensions (Manifest V3)
├── dev-tools/                      # 🛠️ 14 IDE extensions (VS Code, JetBrains)
├── cli-tools/                      # ⌨️ 22 CLI tools (Node.js, Python)
├── enterprise/                     # 🏢 16 enterprise deployments (Docker, Helm, MSI)
├── shared/                         # 🔗 Reusable code (JS, Flutter, C, Python)
│
├── apps/                           # ⚙️ 40+ native LVGL apps (original eApps)
├── core/                           # Native shared core (C)
├── cmake/                          # Cross-platform CMake toolchains
├── port/                           # Platform ports (SDL2, Android, iOS, Web, EoS)
├── tests/                          # Test suites (native + merge validation)
│
├── .github/workflows/              # 🔄 CI/CD automation (7 workflows)
│   ├── build-browser-extensions.yml  # Chrome .zip + Firefox .xpi + auto-update
│   ├── build-vscode-extension.yml    # VS Code .vsix + Marketplace publish
│   ├── build-mobile.yml              # Android APK/AAB + iOS IPA/TestFlight
│   ├── build-desktop.yml             # Electron/PyInstaller/CMake → .exe/.dmg/.AppImage
│   ├── ci-native.yml                 # Native C app CI (Linux, Windows, WASM)
│   ├── release-app.yml               # Generic tag-based release
│   └── deploy-marketplace.yml        # Deploy storefront to GitHub Pages
│
└── docs/                           # 📖 Documentation
    ├── marketplace-architecture.md
    ├── adding-apps.md
    ├── platform-guide.md
    └── porting-guide.md
```

---

## 🚀 Quick Start

### Browse the App Store
Visit **[embeddedos-org.github.io/eApps](https://embeddedos-org.github.io/eApps/)** — filter by category, search by name/tag, download for any platform.

### Install Apps

```bash
# Chrome extension
# Download .zip from Releases → chrome://extensions → Load unpacked

# VS Code extension
code --install-extension eoffice-vscode-1.0.0.vsix

# Android app
adb install eride-1.0.0.apk

# Desktop app (Linux)
chmod +x EoStudio.AppImage && ./EoStudio.AppImage

# Docker (EoSim)
docker run -it embeddedos/eosim
```

### Build from Source

```bash
# Clone
git clone --recursive https://github.com/embeddedos-org/eApps.git
cd eApps

# Native apps (C/LVGL)
cmake -B build && cmake --build build && cd build && ctest

# eOffice Desktop (Electron)
cd desktop-apps/eoffice && npm install && npm start

# EoStudio (Python)
cd desktop-apps/eostudio && pip install -e . && python -m eostudio

# EoSim (Python + QEMU)
cd desktop-apps/eosim && pip install -e . && python -m eosim

# eBrowser (C/CMake)
cd desktop-apps/ebrowser && cmake -B build && cmake --build build

# Mobile apps (Flutter)
cd mobile-apps/eserviceapps && flutter pub get && flutter run

# Run App Store locally
npx serve . # or python -m http.server 8000
```

---

## 🔄 CI/CD Pipeline

```
Push code / Tag release
        │
        ▼
GitHub Actions (7 workflows)
        │
        ├── Build & Test
        ├── Package artifacts (.exe, .dmg, .apk, .zip, .vsix, etc.)
        ├── Sign (code signing via secrets)
        ├── Create GitHub Release with artifacts
        ├── Auto-update data/apps.json with new version
        ├── Update auto-update manifests (Chrome XML, Firefox JSON)
        └── Redeploy App Store to GitHub Pages
```

| Workflow | File | Trigger | Output |
|---|---|---|---|
| **Browser Extensions** | `build-browser-extensions.yml` | Tag `eoffice-chrome-v*` / `eoffice-firefox-v*` | `.zip` `.xpi` + auto-update manifests |
| **VS Code Extension** | `build-vscode-extension.yml` | Tag `eoffice-vscode-v*` | `.vsix` + optional Marketplace publish |
| **Mobile Apps** | `build-mobile.yml` | Tag `eride-v*` / `esocial-v*` / etc. | `.apk` `.aab` + iOS TestFlight |
| **Desktop Apps** | `build-desktop.yml` | Tag `eoffice-desktop-v*` / `eostudio-v*` / `eosim-v*` / `ebrowser-v*` | `.exe` `.dmg` `.AppImage` + Docker |
| **Native CI** | `ci-native.yml` | Push to `apps/` `core/` `cmake/` | Linux + Windows + WASM builds |
| **Generic Release** | `release-app.yml` | Tag `*-v*` | GitHub Release + apps.json update |
| **Deploy Store** | `deploy-marketplace.yml` | Push to `index.html` `css/` `js/` `data/` | GitHub Pages deployment |

### How to Release

```bash
# Browser extension
git tag eoffice-chrome-v1.1.0 && git push origin eoffice-chrome-v1.1.0

# VS Code extension
git tag eoffice-vscode-v1.1.0 && git push origin eoffice-vscode-v1.1.0

# Mobile app
git tag eride-v2.0.0 && git push origin eride-v2.0.0

# Desktop app
git tag eoffice-desktop-v1.1.0 && git push origin eoffice-desktop-v1.1.0
git tag eosim-v1.2.0 && git push origin eosim-v1.2.0
git tag ebrowser-v1.0.1 && git push origin ebrowser-v1.0.1
```

Each tag → **build → test → package → sign → release → update `apps.json` → redeploy store** automatically.

---

## 🔐 Security & Code Signing

| Platform | Signing Method | Secret Required |
|---|---|---|
| Windows `.exe` | EV Code Signing Certificate | `WIN_CSC_LINK`, `WIN_CSC_KEY_PASSWORD` |
| macOS `.dmg` | Apple Developer Certificate | `CSC_LINK`, `CSC_KEY_PASSWORD` |
| Android `.apk` | Keystore signing | `ANDROID_KEYSTORE`, `ANDROID_KEY_ALIAS`, `ANDROID_KEY_PASSWORD` |
| VS Code `.vsix` | VS Code Marketplace PAT | `VSCE_PAT` |
| iOS `.ipa` | Apple Distribution Certificate | `IOS_CERTIFICATE`, `IOS_PROVISIONING_PROFILE` |
| Docker | Docker Hub credentials | `DOCKER_TOKEN` |

> Configure secrets in **Settings → Secrets and variables → Actions** on GitHub.

---

## 🔗 Shared Code

The `shared/` directory contains reusable code across platforms:

| Language | Path | Used By |
|---|---|---|
| JavaScript | `shared/js/` | Extensions, Desktop (Electron), Web |
| Flutter/Dart | `shared/flutter/` | Mobile apps |
| C | `shared/libs/` | Native apps, eBrowser |
| Python | `shared/python/` | EoStudio, EoSim |

> One fix in `shared/` → benefits all platforms automatically.

---

## 📊 Merged From

| Original Repo | Merged Into | Content |
|---|---|---|
| [eOffice](https://github.com/embeddedos-org/eOffice) | `extensions/`, `desktop-apps/eoffice/` | 11 extensions, Electron desktop, 12 office apps, web apps, server |
| [EoStudio](https://github.com/embeddedos-org/EoStudio) | `desktop-apps/eostudio/` | Visual design IDE, codegen, 13 GUI editors |
| [EoSim](https://github.com/embeddedos-org/EoSim) | `desktop-apps/eosim/` | Hardware simulator, 63 platforms, QEMU, GUI renderers |
| [eServiceApps](https://github.com/embeddedos-org/eServiceApps) | `mobile-apps/eserviceapps/` | Flutter mobile apps, Firebase backend |
| [eBrowser](https://github.com/embeddedos-org/eBrowser) | `desktop-apps/ebrowser/` | C browser engine, rendering, TLS, plugins |

> All original repos can be archived. This is the single source of truth.

---

## 📖 Documentation

- [Architecture Overview](docs/marketplace-architecture.md) — Full Mermaid diagram, data flow, merge history
- [Adding New Apps](docs/adding-apps.md) — How to add a new app to the catalog
- [Platform Porting Guide](docs/porting-guide.md) — Port native apps to new platforms
- [Platform Build Guide](docs/platform-guide.md) — Platform-specific build instructions

---

## 🧪 Testing

```bash
# Run merge validation tests (94 tests)
python -m pytest tests/test_merge_validation.py -v

# Run native app tests
cd build && ctest --output-on-failure

# Run Flutter tests
cd mobile-apps/eserviceapps && flutter test

# Run EoStudio tests
cd desktop-apps/eostudio && python -m pytest tests/ -v

# Run EoSim tests
cd desktop-apps/eosim && python -m pytest tests/ -v
```

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines. In summary:

1. Fork and create a feature branch
2. Make changes in the appropriate category folder
3. Update `data/apps.json` if adding a new app
4. Run tests: `python -m pytest tests/test_merge_validation.py`
5. Open a pull request

---

## 📄 License

[Apache License 2.0](LICENSE)

---

<p align="center">
  <strong>🏪 <a href="https://embeddedos-org.github.io/eApps/">Visit the EoS App Store</a></strong><br/>
  Built with ❤️ by <a href="https://github.com/embeddedos-org">embeddedos-org</a>
</p>
