# eApps Architecture

## Overview

eApps is a **Kotlin Multiplatform (KMP) + Compose Multiplatform** monorepo containing 38 cross-platform apps organized into a unified suite.

**One codebase → 7+ platform outputs:**
- Android (Phone + Tablet) via `androidTarget()`
- iOS (iPhone + iPad) via `iosArm64()/iosSimulatorArm64()`
- Windows/macOS/Linux via `jvm()`
- Web (any browser) via `wasmJs()`

## Module Structure

```
eApps/
├── build-logic/                    # Convention plugins
│   └── src/main/kotlin/
│       ├── kmp-library-convention  # Shared library config
│       └── compose-app-convention  # App module config
├── core/                           # Shared libraries
│   ├── common/                     # Models, utils, AppRegistry, DI
│   ├── ui/                         # Theme, components, GameCanvas, responsive
│   ├── storage/                    # Multiplatform Settings (prefs)
│   ├── network/                    # Ktor HTTP client (per-platform engines)
│   └── platform/                   # Platform APIs (clipboard, system info)
├── apps/                           # 37 individual apps + suite launcher
│   ├── suite/                      # Tabbed workspace launcher
│   ├── echess/                     # Chess game
│   ├── snake/                      # Snake game
│   ├── ecal/                       # Calculator
│   └── ...                         # 33 more apps
├── gradle/libs.versions.toml       # Version catalog
├── settings.gradle.kts             # Conditional module inclusion
└── build.gradle.kts                # Root build + aggregate tasks
```

## Convention Plugins

### `kmp-library-convention`
Applied to `core/*` modules. Configures:
- KMP targets (Android, JVM, iOS, WASM) — conditionally via properties
- Common dependencies (coroutines, serialization, datetime)
- Android library setup (compileSdk, minSdk)

### `compose-app-convention`
Applied to `apps/*` modules. Extends library convention with:
- Compose Multiplatform plugin
- Compose UI dependencies (Material3, foundation, resources)
- Android application setup (applicationId, versionCode)
- Desktop JVM main class configuration

## Responsive UI System

The responsive system auto-adapts UI for any screen:

1. **WindowSize** enum: `COMPACT`, `MEDIUM`, `EXPANDED`, `LARGE`
2. **AdaptiveScaffold**: Auto-switches navigation pattern
   - COMPACT → Bottom navigation bar
   - MEDIUM → Navigation rail
   - EXPANDED/LARGE → Persistent side drawer
3. **PlatformScaling**: Auto-adjusts text sizes and touch targets
4. **SafeAreaLayout**: Handles notches/insets across platforms

## Build Configuration

Properties in `gradle.properties` control:
- **Platform targets**: `eapps.target.{android,ios,jvm,wasm}=true/false`
- **App categories**: `eapps.apps.{productivity,media,games,connectivity,security}=true/false`
- **Build mode**: `eapps.build.mode=suite|standalone`

## App Categories

| Category | Count | Apps |
|----------|-------|------|
| Productivity | 13 | ecal, enote, eftp, econverter, etools, ebuffer, ecleaner, eclock, efiles, ezip, epaint, epdf, eguard |
| Media | 4 | emusic, evideo, egallery, eplay |
| Games | 11 | snake, tetris, minesweeper, dice, echess, ebirds, eslice, erunner, eblocks, ecrush, esurfer |
| Connectivity | 5 | essh, eserial, echat, etunnel, evpn |
| Security | 2 | evirustower, evnc |
| Web | 1 | eweb |
