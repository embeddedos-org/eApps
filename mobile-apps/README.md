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

All releases registered in `data/apps.json` and listed on the **[EoS App Store](https://embeddedos-org.github.io/eApps/)**.

## CI/CD

Automated via `.github/workflows/build-mobile.yml`:

```bash
# Tag to release
git tag eride-v2.0.0 && git push origin eride-v2.0.0
git tag esocial-v1.1.0 && git push origin esocial-v1.1.0
```

This triggers:
1. Flutter tests
2. Android APK + AAB build (signed if `ANDROID_KEYSTORE` configured)
3. iOS build + TestFlight upload (if `IOS_CERTIFICATE` configured)
4. GitHub Release with all artifacts
5. Auto-update `data/apps.json` with new version
6. Redeploy App Store on GitHub Pages
