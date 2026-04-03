# 🖥️ Desktop Applications

Native desktop applications built with Electron, Python/Tk, and C/SDL2.

## Contents

| App | Technology | Platforms | Source |
|---|---|---|---|
| **eOffice Desktop** | Electron + Node.js | Windows, macOS, Linux | `eoffice/` |
| **EoStudio** | Python + Tkinter | Windows, macOS, Linux | `eostudio/` |
| **EoSim** | Python + QEMU | Windows, macOS, Linux, Docker | `eosim/` |
| **eBrowser** | C + LVGL/SDL2 | Windows, macOS, Linux, EoS | `ebrowser/` |

## Origin

| Folder | Merged From |
|---|---|
| `eoffice/` | [embeddedos-org/eOffice → desktop/](https://github.com/embeddedos-org/eOffice/tree/main/desktop) |
| `eostudio/` | [embeddedos-org/EoStudio](https://github.com/embeddedos-org/EoStudio) |
| `eosim/` | [embeddedos-org/EoSim](https://github.com/embeddedos-org/EoSim) |
| `ebrowser/` | [embeddedos-org/eBrowser](https://github.com/embeddedos-org/eBrowser) |

## Build

```bash
# eOffice Desktop (Electron)
cd eoffice && npm install && npm run build

# EoStudio (Python)
cd eostudio && pip install -e . && python -m eostudio

# EoSim (Python + QEMU)
cd eosim && pip install -e . && python -m eosim

# eBrowser (C/CMake)
cd ebrowser && mkdir build && cd build && cmake .. && cmake --build .
```

## Release Artifacts

| App | Windows | macOS | Linux |
|---|---|---|---|
| eOffice Desktop | `.exe` installer | `.dmg` | `.AppImage` |
| EoStudio | `.exe` installer | `.dmg` | `.AppImage` |
| EoSim | `.exe` installer | `.dmg` | `.AppImage` / Docker |
| eBrowser | `.exe` installer | `.dmg` | `.AppImage` |

All releases published to [GitHub Releases](https://github.com/embeddedos-org/eApps/releases), registered in `data/apps.json`, and listed on the **[EoS App Store](https://embeddedos-org.github.io/eApps/)**.

## CI/CD

Automated via `.github/workflows/build-desktop.yml`:
- **eOffice:** Electron Builder → `.exe` `.dmg` `.AppImage` (signed if secrets configured)
- **EoStudio:** PyInstaller → `.exe` `.dmg` `.AppImage`
- **EoSim:** PyInstaller → `.exe` `.dmg` `.AppImage` + Docker image to Docker Hub
- **eBrowser:** CMake → native binaries + WASM via Emscripten

```bash
# Tag to release
git tag eoffice-desktop-v1.1.0 && git push origin eoffice-desktop-v1.1.0
git tag eostudio-v1.2.0 && git push origin eostudio-v1.2.0
git tag eosim-v1.0.0 && git push origin eosim-v1.0.0
git tag ebrowser-v1.0.0 && git push origin ebrowser-v1.0.0
```
