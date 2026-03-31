plugins {
    id("compose-app-convention")
}

android {
    namespace = "com.eos.eappsuite.evideo"
    defaultConfig {
        applicationId = "com.eos.eappsuite.evideo"
        versionCode = 1
        versionName = "1.0.0"
    }
}

compose.desktop {
    application {
        mainClass = "com.eos.eappsuite.evideo.MainKt"
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
