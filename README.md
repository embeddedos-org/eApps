# ⚡ eApps — EoS Unified Marketplace

[![GitHub Pages](https://img.shields.io/badge/Marketplace-Live-blue?logo=github)](https://embeddedos-org.github.io/eApps/)
[![License](https://img.shields.io/badge/License-Apache_2.0-green.svg)](LICENSE)

**One repository. Every EoS app. All platforms.**

eApps is the unified marketplace and monorepo for the entire [EoS (Embedded Operating System)](https://github.com/embeddedos-org) ecosystem — browser extensions, desktop applications, mobile apps, cloud services, and 40+ embedded-native apps.

🌐 **Live Marketplace:** [embeddedos-org.github.io/eApps](https://embeddedos-org.github.io/eApps/)

---

## 🏗️ What's Inside

| Category | Folder | Count | Technologies |
|---|---|---|---|
| 🧩 **Extensions** | `extensions/` | 11 | Chrome, Firefox, Safari, VS Code, JetBrains, Obsidian, Slack, Raycast, GitHub, Google WS, Office 365 |
| 🖥️ **Desktop Apps** | `desktop-apps/` | 4 | Electron, Python/Tkinter, Python/QEMU, C/SDL2 |
| 📱 **Mobile Apps** | `mobile-apps/` | 5 | Flutter (Android + iOS) |
| ☁️ **Service Apps** | `service-apps/` | 2 | Firebase, Docker, Node.js |
| ⚙️ **Native Apps** | `apps/` | 40+ | C + LVGL (cross-platform via CMake) |
| 🌐 **Web Apps** | `desktop-apps/eoffice/browser/` | 1 | HTML/CSS/JS |

### Headline Products

- **eOffice** — Full office suite (eDocs, eSheets, eSlides, ePlanner, eNotes, eMail, eDrive, eConnect, eDB, eForms, eSway)
- **EoStudio** — Visual design IDE for UI, 3D, CAD, games, hardware, and code generation
- **EoSim** — Hardware & platform simulator for 63+ boards (ARM, RISC-V, ESP32, STM32, RPi, Jetson) with QEMU, GUI, and domain renderers
- **eBrowser** — Privacy-first web browser with custom rendering engine
- **eServiceApps** — eRide, eSocial, eTrack, eTravel, eWallet

---

## 📂 Repository Structure

```
eApps/
├── index.html                 # 🏪 Marketplace website (GitHub Pages)
├── css/ js/                   # Marketplace frontend
├── data/apps.json             # 📋 Single source of truth for all listings
│
├── extensions/                # 🧩 Browser & editor extensions (from eOffice)
├── desktop-apps/              # 🖥️ eOffice Desktop, EoStudio, EoSim, eBrowser
├── mobile-apps/               # 📱 eRide, eSocial, eTrack, eTravel, eWallet
├── service-apps/              # ☁️ Firebase backend, eOffice Server
├── shared/                    # 🔗 Reusable code (JS, Flutter, C, Python)
│
├── apps/                      # ⚙️ 40+ native LVGL apps
├── core/                      # Native shared core
├── cmake/                     # Cross-platform toolchains
├── port/                      # Platform ports (SDL2, Android, iOS, Web, EoS)
├── tests/                     # Native test suite
│
├── .github/workflows/         # CI/CD automation
└── docs/                      # Documentation
```

---

## 🚀 Quick Start

### Browse the Marketplace
Visit [embeddedos-org.github.io/eApps](https://embeddedos-org.github.io/eApps/) — filter by category, search, and download.

### Build Native Apps
```bash
git clone --recursive https://github.com/embeddedos-org/eApps.git
cd eApps
cmake -B build && cmake --build build
cd build && ctest
```

### Build Desktop Apps
```bash
# eOffice (Electron)
cd desktop-apps/eoffice && npm install && npm start

# EoStudio (Python)
cd desktop-apps/eostudio && pip install -e . && python -m eostudio

# EoSim (Python + QEMU)
cd desktop-apps/eosim && pip install -e . && python -m eosim

# eBrowser (C)
cd desktop-apps/ebrowser && cmake -B build && cmake --build build
```

### Build Mobile Apps
```bash
cd mobile-apps/eride && flutter pub get && flutter run
```

### Run Marketplace Locally
```bash
# Any static file server
npx serve .
# or
python -m http.server 8000
```

---

## 🔄 CI/CD Pipeline

```
Push code → GitHub Actions → Build & Test → Package → GitHub Releases → Auto-update apps.json → Deploy marketplace
```

| Workflow | Trigger | Purpose |
|---|---|---|
| `ci-native.yml` | Push to `apps/`, `core/`, `cmake/` | Build & test native C apps |
| `release-app.yml` | Tag `*-v*` (e.g. `eride-v1.2.0`) | Build, release, update `apps.json` |
| `deploy-marketplace.yml` | Push to `index.html`, `css/`, `js/`, `data/` | Deploy marketplace to GitHub Pages |

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

| Original Repo | Status | Content |
|---|---|---|
| [eOffice](https://github.com/embeddedos-org/eOffice) | ✅ Merged | Extensions, Desktop, Web, Server |
| [EoStudio](https://github.com/embeddedos-org/EoStudio) | ✅ Merged | Desktop IDE |
| [EoSim](https://github.com/embeddedos-org/EoSim) | ✅ Merged | Hardware & platform simulator |
| [eServiceApps](https://github.com/embeddedos-org/eServiceApps) | ✅ Merged | Mobile apps, Backend services |
| [eBrowser](https://github.com/embeddedos-org/eBrowser) | ✅ Merged | Desktop browser |

See [docs/marketplace-architecture.md](docs/marketplace-architecture.md) for full architecture diagram and merge commands.

---

## 📖 Documentation

- [Architecture Overview](docs/marketplace-architecture.md)
- [Adding New Apps](docs/adding-apps.md)
- [Platform Porting Guide](docs/porting-guide.md)
- [Platform Build Guide](docs/platform-guide.md)

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines. In summary:

1. Fork and create a feature branch
2. Make changes in the appropriate category folder
3. Update `data/apps.json` if adding a new app
4. Open a pull request

---

## 📄 License

[Apache License 2.0](LICENSE)

---

<p align="center">
  Built with ❤️ by <a href="https://github.com/embeddedos-org">embeddedos-org</a>
</p>
