plugins {
    id("compose-app-convention")
}

android {
    namespace = "com.eos.eappsuite.eftp"
    defaultConfig {
        applicationId = "com.eos.eappsuite.eftp"
        versionCode = 1
        versionName = "1.0.0"
    }
}

compose.desktop {
    application {
        mainClass = "com.eos.eappsuite.eftp.MainKt"
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
