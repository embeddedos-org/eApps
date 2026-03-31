# Adding a New App

Step-by-step guide for adding a new application to the eApps monorepo.

## 1. Create the Module Directory

```
apps/
└── myapp/
    ├── build.gradle.kts
    └── src/
        └── commonMain/
            └── kotlin/
                └── com/eos/eapps/apps/myapp/
                    └── App.kt
```

## 2. Add `build.gradle.kts`

Apply the `compose-app-convention` plugin and declare your namespace:

```kotlin
plugins {
    id("compose-app-convention")
}

android {
    namespace = "com.eos.eapps.apps.myapp"
    defaultConfig {
        applicationId = "com.eos.eapps.myapp"
        versionCode = 1
        versionName = "1.0.0"
    }
}

kotlin {
    sourceSets {
        commonMain.dependencies {
            implementation(project(":core:common"))
            implementation(project(":core:ui"))
            // Add optional core deps as needed:
            // implementation(project(":core:storage"))
            // implementation(project(":core:network"))
            // implementation(project(":core:platform"))
        }
    }
}
```

## 3. Register in `settings.gradle.kts`

Add your module include at the root `settings.gradle.kts`:

```kotlin
// Apps — [Your Category]
include(":apps:myapp")
```

## 4. Implement `App.kt`

Create the main composable entry point:

```kotlin
package com.eos.eapps.apps.myapp

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.eos.eapps.core.ui.theme.AppTheme
import com.eos.eapps.core.ui.components.AppScaffold

@Composable
fun App() {
    AppTheme {
        AppScaffold(title = "My App") {
            MyAppContent()
        }
    }
}

@Composable
private fun MyAppContent() {
    Column(modifier = Modifier.fillMaxSize().padding(16.dp)) {
        Text(
            text = "Hello from My App!",
            style = MaterialTheme.typography.headlineMedium,
        )
    }
}
```

## 5. Register in AppRegistry

Add your app entry to `core/common/src/commonMain/kotlin/.../constants/AppRegistry.kt`:

```kotlin
AppInfo(
    id = "myapp",
    name = "MyApp",
    displayName = "My Application",
    category = AppCategory.PRODUCTIVITY, // or MEDIA, GAMES, CONNECTIVITY, SECURITY, WEB
    icon = "🔧",
    description = "Short description of what the app does"
),
```

### AppCategory Options

| Category | Use For |
|----------|---------|
| `PRODUCTIVITY` | Tools, editors, file managers, utilities |
| `MEDIA` | Music, video, gallery, media players |
| `GAMES` | All game apps |
| `CONNECTIVITY` | SSH, serial, chat, VPN, tunneling |
| `SECURITY` | Antivirus, remote desktop, encryption |
| `WEB` | Browser, web tools |

## 6. Add Platform Entry Points

### Android — `src/androidMain/kotlin/.../MainActivity.kt`

```kotlin
package com.eos.eapps.apps.myapp

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent { App() }
    }
}
```

### Desktop — `src/jvmMain/kotlin/.../Main.kt`

```kotlin
package com.eos.eapps.apps.myapp

import androidx.compose.ui.window.Window
import androidx.compose.ui.window.application

fun main() = application {
    Window(onCloseRequest = ::exitApplication, title = "MyApp") {
        App()
    }
}
```

### iOS — `src/iosMain/kotlin/.../MainViewController.kt`

```kotlin
package com.eos.eapps.apps.myapp

import androidx.compose.ui.window.ComposeUIViewController

fun MainViewController() = ComposeUIViewController { App() }
```

## 7. Add Android Manifest

Create `src/androidMain/AndroidManifest.xml`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <application
        android:label="MyApp"
        android:theme="@android:style/Theme.Material.Light.NoActionBar">
        <activity
            android:name=".MainActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
```

## 8. Build and Test

```bash
# Compile
./gradlew :apps:myapp:compileKotlin

# Run desktop
./gradlew :apps:myapp:run

# Run tests
./gradlew :apps:myapp:check

# Build Android APK
./gradlew :apps:myapp:assembleDebug
```

## Checklist

- [ ] Module directory created under `apps/`
- [ ] `build.gradle.kts` with `compose-app-convention` applied
- [ ] Module added to `settings.gradle.kts`
- [ ] `App.kt` composable implemented in `commonMain`
- [ ] Platform entry points added (Android, Desktop, iOS)
- [ ] Android manifest created
- [ ] App registered in `AppRegistry`
- [ ] Builds on at least 2 platforms
- [ ] Tests pass (`./gradlew :apps:myapp:check`)
