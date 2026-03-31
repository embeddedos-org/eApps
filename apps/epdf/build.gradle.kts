plugins {
    id("compose-app-convention")
}

android {
    namespace = "com.eos.eapps.apps.epdf"
    defaultConfig {
        applicationId = "com.eos.eapps.apps.epdf"
        versionCode = 1
        versionName = "1.0.0"
    }
}

compose.desktop {
    application {
        mainClass = "com.eos.eapps.apps.epdf.MainKt"
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
