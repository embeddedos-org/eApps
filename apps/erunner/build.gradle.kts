plugins {
    id("compose-app-convention")
}

android {
    namespace = "com.eos.eappsuite.erunner"
    defaultConfig {
        applicationId = "com.eos.eappsuite.erunner"
        versionCode = 1
        versionName = "1.0.0"
    }
}

compose.desktop {
    application {
        mainClass = "com.eos.eappsuite.erunner.MainKt"
    }
}

kotlin {
    sourceSets {
        commonMain.dependencies {
            implementation(project(":core:common"))
            implementation(project(":core:ui"))
            implementation(project(":core:storage"))
        }
    }
}
