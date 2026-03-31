# eApps

**38 apps. One codebase. Every platform.**

eApps is a Kotlin Multiplatform + Compose Multiplatform monorepo that delivers productivity tools, media apps, games, and system utilities across Android, iOS, Windows, macOS, Linux, and Web (WASM).

## Quick Start

```bash
# Run the suite launcher on desktop
./gradlew :apps:suite:jvmRun

# Run a single app
./gradlew :apps:echess:jvmRun

# Run in browser
./gradlew :apps:suite:wasmJsBrowserRun

# Build Android APK
./gradlew :apps:suite:assembleDebug
```

## Apps (38 total)

| Category | Apps |
|----------|------|
| 🔧 **Productivity** (13) | eCalc, eNote, eFTP, eConverter, eTools, eBuffer, eCleaner, eClock, eFiles, eZip, ePaint, ePDF, eGuard |
| 🎵 **Media** (4) | eMusic, eVideo, eGallery, ePlay |
| 🎮 **Games** (11) | Snake, Tetris, Minesweeper, Dice, eChess, eBirds, eSlice, eRunner, eBlocks, eCrush, eSurfer |
| 🔌 **Connectivity** (5) | eSSH, eSerial, eChat, eTunnel, eVPN |
| 🛡️ **Security** (2) | eVirusTower, eVNC |
| 🌐 **Web** (1) | eWeb |

## Platform Support

| Platform | Target | Output |
|----------|--------|--------|
| Android Phone/Tablet | `androidTarget()` | APK/AAB |
| iOS iPhone/iPad | `iosArm64()` | .ipa |
| Windows/macOS/Linux | `jvm()` | JAR / native executable |
| Web (any browser) | `wasmJs()` | WebAssembly |

## Architecture

- **Kotlin Multiplatform** — shared business logic in `commonMain`
- **Compose Multiplatform** — declarative UI on all platforms
- **5 core modules** — common, ui, storage, network, platform
- **Convention plugins** — consistent build config across 38 app modules
- **Responsive UI** — auto-adapts layout for phones, tablets, desktops, browsers
- **Granular builds** — toggle platforms and app categories via properties

## Build Control

```bash
# Build only games for desktop
./gradlew build -Peapps.apps.games=true -Peapps.apps.media=false

# Build for Android only
./gradlew build -Peapps.target.jvm=false -Peapps.target.ios=false -Peapps.target.wasm=false
```

## Documentation

- [Architecture](docs/architecture.md)
- [Platform Guide](docs/platform-guide.md)

## Standards Compliance

This project is part of the EoS ecosystem and aligns with international standards including ISO/IEC/IEEE 15288:2023, ISO/IEC 12207, ISO/IEC 25000, ISO/IEC 27001, and more. See the [EoS Compliance Documentation](https://github.com/embeddedos-org/.github/tree/master/docs/compliance) for full details.

## License

MIT License — see [LICENSE](LICENSE) for details.
