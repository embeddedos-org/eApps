plugins {
    id("compose-app-convention")
}

android {
    namespace = "com.eos.eapps.apps.ebirds"
    defaultConfig {
        applicationId = "com.eos.eapps.apps.ebirds"
        versionCode = 1
        versionName = "1.0.0"
    }
}

compose.desktop {
    application {
        mainClass = "com.eos.eapps.apps.ebirds.MainKt"
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
