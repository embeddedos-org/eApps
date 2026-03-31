plugins {
    id("compose-app-convention")
}

android {
    namespace = "com.eos.eappsuite.evpn"
    defaultConfig {
        applicationId = "com.eos.eappsuite.evpn"
        versionCode = 1
        versionName = "1.0.0"
    }
}

compose.desktop {
    application {
        mainClass = "com.eos.eappsuite.evpn.MainKt"
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
