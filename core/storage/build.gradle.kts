plugins {
    id("kmp-library-convention")
}

android {
    namespace = "com.eos.eapps.core.storage"
}

kotlin {
    sourceSets {
        commonMain.dependencies {
            api(project(":core:common"))
            implementation(libs.multiplatform.settings)
            implementation(libs.multiplatform.settings.coroutines)
        }
    }
}
