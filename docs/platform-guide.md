# eApps Platform Guide

## Build Requirements

| Platform | Requirements |
|----------|-------------|
| **Android** | JDK 17+, Android SDK 34 |
| **iOS** | macOS, Xcode 15+, JDK 17+ |
| **Windows** | JDK 17+ |
| **macOS** | JDK 17+ |
| **Linux** | JDK 17+ |
| **Web (WASM)** | JDK 17+, modern browser |

## Quick Start

```bash
# Clone and build
git clone https://github.com/embeddedos-org/eapps.git
cd eApps

# Build everything
./gradlew build

# Run suite on desktop
./gradlew :apps:suite:jvmRun

# Run single app on desktop
./gradlew :apps:echess:jvmRun

# Run in browser (WASM)
./gradlew :apps:suite:wasmJsBrowserRun
```

## Platform Build Commands

### Android
```bash
./gradlew :apps:suite:assembleDebug          # Debug APK
./gradlew :apps:echess:assembleRelease       # Release APK
./gradlew buildAndroid                       # All apps as APKs
```

### iOS
```bash
./gradlew :apps:suite:linkReleaseFrameworkIosArm64    # iOS framework
./gradlew buildIos                                     # All apps
```

### Desktop (JVM — Windows/macOS/Linux)
```bash
./gradlew :apps:suite:jvmRun                # Run desktop suite
./gradlew :apps:echess:jvmRun               # Run single app
./gradlew buildDesktop                       # Build all desktop
```

### Web (WASM)
```bash
./gradlew :apps:suite:wasmJsBrowserRun       # Dev server
./gradlew :apps:suite:wasmJsBrowserDistribution  # Production build
./gradlew buildWeb                           # All apps as WASM
```

## Selective Builds

Control which apps and platforms compile via `gradle.properties` or CLI flags:

```bash
# Build only games for desktop
./gradlew build \
  -Peapps.apps.games=true \
  -Peapps.apps.media=false \
  -Peapps.apps.productivity=false \
  -Peapps.apps.connectivity=false \
  -Peapps.apps.security=false \
  -Peapps.target.android=false \
  -Peapps.target.ios=false \
  -Peapps.target.wasm=false

# Build everything for Android only
./gradlew build \
  -Peapps.target.jvm=false \
  -Peapps.target.ios=false \
  -Peapps.target.wasm=false
```

## Responsive UI Breakpoints

| Window Size | Width | Navigation | Touch Targets | Use Case |
|-------------|-------|------------|---------------|----------|
| **COMPACT** | <600dp | Bottom nav bar | 48dp | Phones portrait |
| **MEDIUM** | 600-840dp | Navigation rail | 48dp | Phones landscape, small tablets |
| **EXPANDED** | 840-1200dp | Sidebar drawer | 40dp | Tablets, small desktop |
| **LARGE** | >1200dp | Sidebar drawer | 32dp | Desktop, large tablets |

## Platform Support Matrix

| App Category | Android | iOS | Windows/macOS/Linux | Web (WASM) |
|-------------|---------|-----|---------------------|------------|
| Productivity (13) | ✅ | ✅ | ✅ | ✅ |
| Media (4) | ✅ | ✅ | ✅ | ✅ |
| Games (11) | ✅ | ✅ | ✅ | ✅ |
| Connectivity (5) | ✅ | ✅ | ✅ | ⚠️ Limited |
| Security (2) | ✅ | ✅ | ✅ | ⚠️ Limited |
| Web (1) | ✅ | ✅ | ✅ | ✅ |

> ⚠️ Connectivity/Security apps that require raw sockets (eSSH, eTunnel, eVPN, eVNC) show "Not available on this platform" on Web/WASM.
# Platform Guide

Platform-specific instructions for building and deploying eApps apps.

---

## Android

### Requirements

- Android SDK 34 (compileSdk)
- Android SDK 24+ (minSdk)
- JDK 17

### Build Commands

```bash
# Debug APK
./gradlew :apps:ecal:assembleDebug

# Release APK
./gradlew :apps:ecal:assembleRelease

# Install on connected device
./gradlew :apps:ecal:installDebug

# Run all Android tests
./gradlew :apps:ecal:connectedAndroidTest
```

### Permissions

Add permissions in `src/androidMain/AndroidManifest.xml`:

```xml
<!-- Network access (for SSH, FTP, VPN, Chat, Browser) -->
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />

<!-- File access (for Files, ZIP, Cleaner, PDF, Converter) -->
<uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
<uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />
<uses-permission android:name="android.permission.MANAGE_EXTERNAL_STORAGE" />

<!-- Camera (for QR scanner in eTools) -->
<uses-permission android:name="android.permission.CAMERA" />

<!-- Audio (for Music, Video) -->
<uses-permission android:name="android.permission.RECORD_AUDIO" />

<!-- Keep screen on (for eGuard) -->
<uses-permission android:name="android.permission.WAKE_LOCK" />
```

### Signing

Create `keystore.properties` at project root (not committed):

```properties
storeFile=path/to/release.keystore
storePassword=****
keyAlias=eApps
keyPassword=****
```

Configure in `build.gradle.kts`:

```kotlin
android {
    signingConfigs {
        create("release") {
            val props = java.util.Properties().apply {
                load(rootProject.file("keystore.properties").inputStream())
            }
            storeFile = file(props["storeFile"] as String)
            storePassword = props["storePassword"] as String
            keyAlias = props["keyAlias"] as String
            keyPassword = props["keyPassword"] as String
        }
    }
    buildTypes {
        release {
            signingConfig = signingConfigs.getByName("release")
            isMinifyEnabled = true
        }
    }
}
```

---

## iOS

### Requirements

- macOS 13+
- Xcode 15+
- CocoaPods (`gem install cocoapods`)

### Project Setup

1. Generate the Xcode project framework:

```bash
./gradlew :apps:ecal:linkDebugFrameworkIosSimulatorArm64
```

2. Create an Xcode project in `apps/ecal/iosApp/`:

```
iosApp/
├── iosApp.xcodeproj
├── iosApp/
│   ├── AppDelegate.swift
│   ├── ContentView.swift
│   └── Info.plist
└── Podfile
```

3. `ContentView.swift`:

```swift
import SwiftUI
import ComposeApp

struct ContentView: View {
    var body: some View {
        ComposeView()
            .ignoresSafeArea()
    }
}

struct ComposeView: UIViewControllerRepresentable {
    func makeUIViewController(context: Context) -> UIViewController {
        MainViewControllerKt.MainViewController()
    }
    func updateUIViewController(_ uiViewController: UIViewController, context: Context) {}
}
```

### Signing

Configure in Xcode:
- Team → select your Apple Developer team
- Bundle Identifier → `com.eos.eapps.ecal`
- Signing Certificate → automatic or manual

---

## Desktop (JVM)

### Requirements

- JDK 17+
- OS: Windows 10+, macOS 12+, or Linux (X11/Wayland)

### Build Commands

```bash
# Run directly
./gradlew :apps:ecal:run

# Package uber JAR (all platforms from current OS)
./gradlew :apps:ecal:packageUberJarForCurrentOS

# Package native installer
./gradlew :apps:ecal:packageDistributionForCurrentOS
```

### Native Packaging

The Compose Desktop plugin can create native installers:

| OS | Format | Tool Required |
|----|--------|---------------|
| Windows | `.msi`, `.exe` | WiX Toolset 3.x |
| macOS | `.dmg`, `.pkg` | Xcode command-line tools |
| Linux | `.deb`, `.rpm` | `dpkg-deb` or `rpmbuild` |

Configure in `build.gradle.kts`:

```kotlin
compose.desktop {
    application {
        mainClass = "com.eos.eapps.apps.ecal.MainKt"
        nativeDistributions {
            targetFormats(
                TargetFormat.Dmg,   // macOS
                TargetFormat.Msi,   // Windows
                TargetFormat.Deb,   // Linux
            )
            packageName = "eCal"
            packageVersion = "1.0.0"
            description = "Scientific calculator"
            vendor = "eApps"

            windows {
                iconFile.set(project.file("icons/icon.ico"))
                menuGroup = "eApps"
            }
            macOS {
                iconFile.set(project.file("icons/icon.icns"))
                bundleID = "com.eos.eapps.ecal"
            }
            linux {
                iconFile.set(project.file("icons/icon.png"))
            }
        }
    }
}
```

### Native Dependencies

For apps requiring native access (serial ports, VPN tunnels):

```kotlin
// jvmMain dependencies
jvmMain.dependencies {
    implementation(compose.desktop.currentOs)
    // Serial port access
    implementation("com.fazecast:jSerialComm:2.10.4")
    // System tray / notifications
    implementation("com.dorkbox:SystemTray:4.4")
}
```

---

## Web (WASM)

### Requirements

- Kotlin/WASM support (experimental)
- Modern browser with WASM support

### Build Commands

```bash
# Development server
./gradlew :apps:ecal:wasmJsBrowserRun

# Production build
./gradlew :apps:ecal:wasmJsBrowserDistribution
```

Output goes to `build/dist/wasmJs/productionExecutable/`.

### Limitations

- No file system access (use File System Access API via `expect/actual`)
- No serial port access (`navigator.serial` requires JS interop)
- No native process execution
- WebSocket support available via Ktor JS client
- Limited to browser sandbox permissions
- Performance may vary for canvas-heavy games

### Web Entry Point

`src/wasmJsMain/kotlin/Main.kt`:

```kotlin
import androidx.compose.ui.ExperimentalComposeUiApi
import androidx.compose.ui.window.CanvasBasedWindow

@OptIn(ExperimentalComposeUiApi::class)
fun main() {
    CanvasBasedWindow(canvasElementId = "ComposeTarget") {
        App()
    }
}
```

---

## Expect/Actual Pattern Examples

### File System

```kotlin
// commonMain
expect class FileSystem() {
    fun readText(path: String): String
    fun writeText(path: String, content: String)
    fun listFiles(directory: String): List<String>
    fun exists(path: String): Boolean
}
```

```kotlin
// androidMain
actual class FileSystem {
    actual fun readText(path: String): String = File(path).readText()
    actual fun writeText(path: String, content: String) = File(path).writeText(content)
    actual fun listFiles(directory: String): List<String> =
        File(directory).listFiles()?.map { it.absolutePath } ?: emptyList()
    actual fun exists(path: String): Boolean = File(path).exists()
}
```

```kotlin
// jvmMain
actual class FileSystem {
    actual fun readText(path: String): String = java.io.File(path).readText()
    actual fun writeText(path: String, content: String) = java.io.File(path).writeText(content)
    actual fun listFiles(directory: String): List<String> =
        java.io.File(directory).listFiles()?.map { it.absolutePath } ?: emptyList()
    actual fun exists(path: String): Boolean = java.io.File(path).exists()
}
```

```kotlin
// iosMain
actual class FileSystem {
    actual fun readText(path: String): String =
        NSString.stringWithContentsOfFile(path, NSUTF8StringEncoding, null) ?: ""
    actual fun writeText(path: String, content: String) {
        (content as NSString).writeToFile(path, true, NSUTF8StringEncoding, null)
    }
    actual fun listFiles(directory: String): List<String> =
        NSFileManager.defaultManager.contentsOfDirectoryAtPath(directory, null)
            ?.map { it as String } ?: emptyList()
    actual fun exists(path: String): Boolean =
        NSFileManager.defaultManager.fileExistsAtPath(path)
}
```

### Clipboard

```kotlin
// commonMain
expect object Clipboard {
    fun copy(text: String)
    fun paste(): String?
}

// androidMain
actual object Clipboard {
    actual fun copy(text: String) {
        val manager = context.getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
        manager.setPrimaryClip(ClipData.newPlainText("text", text))
    }
    actual fun paste(): String? {
        val manager = context.getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
        return manager.primaryClip?.getItemAt(0)?.text?.toString()
    }
}

// jvmMain
actual object Clipboard {
    actual fun copy(text: String) {
        val selection = StringSelection(text)
        Toolkit.getDefaultToolkit().systemClipboard.setContents(selection, null)
    }
    actual fun paste(): String? {
        return Toolkit.getDefaultToolkit().systemClipboard
            .getData(DataFlavor.stringFlavor) as? String
    }
}
```

### Platform Info

```kotlin
// commonMain
expect fun getPlatformName(): String
expect fun isDesktop(): Boolean

// androidMain
actual fun getPlatformName(): String = "Android ${Build.VERSION.SDK_INT}"
actual fun isDesktop(): Boolean = false

// jvmMain
actual fun getPlatformName(): String = "Desktop (${System.getProperty("os.name")})"
actual fun isDesktop(): Boolean = true

// iosMain
actual fun getPlatformName(): String = "iOS ${UIDevice.currentDevice.systemVersion}"
actual fun isDesktop(): Boolean = false

// wasmJsMain
actual fun getPlatformName(): String = "Web (WASM)"
actual fun isDesktop(): Boolean = false
```
