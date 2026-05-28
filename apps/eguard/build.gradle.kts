plugins {
    id("compose-app-convention")
}

kotlin {
    sourceSets {
        commonMain.dependencies {
            implementation(project(":core:common"))
            implementation(project(":core:ui"))
        }
    }
}

android {
    namespace = "com.eos.eapps.apps.eguard"
}

compose.desktop {
    application {
        mainClass = "com.eos.eapps.apps.eguard.AppKt"
    }
}
