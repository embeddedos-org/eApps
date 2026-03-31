plugins {
    id("kmp-library-convention")
}

android {
    namespace = "com.eos.eapps.core.platform"
}

kotlin {
    sourceSets {
        commonMain.dependencies {
            api(project(":core:common"))
        }
    }
}
