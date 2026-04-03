# 📱 Mobile Applications

Mobile apps built with Flutter and native C/LVGL ports.

## Contents

| App | Technology | Platforms | Source |
|---|---|---|---|
| **eRide** | Flutter | Android, iOS | `eride/` |
| **eSocial** | Flutter | Android, iOS | `esocial/` |
| **eTrack** | Flutter | Android, iOS | `etrack/` |
| **eTravel** | Flutter | Android, iOS | `etravel/` |
| **eWallet** | Flutter | Android, iOS | `ewallet/` |
| **eApps Native** | C + LVGL | Android, iOS | See `../apps/` + `../port/android/`, `../port/ios/` |

## Origin

All Flutter apps merged from [embeddedos-org/eServiceApps](https://github.com/embeddedos-org/eServiceApps).

Native apps are cross-compiled from the main `apps/` directory using CMake toolchains in `cmake/android.cmake` and `cmake/ios.cmake`.

## Build

```bash
# Flutter apps
cd eride && flutter pub get && flutter build apk
cd esocial && flutter pub get && flutter build apk

# Native apps (Android via CMake)
cmake -B build-android -DCMAKE_TOOLCHAIN_FILE=cmake/android.cmake ..
cmake --build build-android
```

## Release Artifacts

| Format | Distribution |
|---|---|
| `.apk` | GitHub Releases / direct sideload |
| `.aab` | Google Play Store (future) |
| TestFlight | iOS beta distribution |

All releases registered in `data/apps.json`.
