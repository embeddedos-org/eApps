plugins {
    id("compose-app-convention")
}

android {
    namespace = "com.eos.eappsuite.ebuffer"
    defaultConfig {
        applicationId = "com.eos.eappsuite.ebuffer"
        versionCode = 1
        versionName = "1.0.0"
    }
}

compose.desktop {
    application {
        mainClass = "com.eos.eappsuite.ebuffer.MainKt"
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
