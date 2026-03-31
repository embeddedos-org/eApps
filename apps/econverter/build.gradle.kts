plugins {
    id("compose-app-convention")
}

android {
    namespace = "com.eos.eapps.apps.econverter"
    defaultConfig {
        applicationId = "com.eos.eapps.apps.econverter"
        versionCode = 1
        versionName = "1.0.0"
    }
}

kotlin {
    sourceSets {
        commonMain.dependencies {
            implementation(project(":core:common"))
            implementation(project(":core:ui"))
        }
    }
}
