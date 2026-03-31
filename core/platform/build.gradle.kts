plugins {
    id("kmp-library-convention")
}

android {
    namespace = "com.eos.eappsuite.core.platform"
}

kotlin {
    sourceSets {
        commonMain.dependencies {
            api(project(":core:common"))
        }
    }
}
plugins {
    id("kmp-library-convention")
}

android {
    namespace = "com.eos.eappsuite.core.platform"
}

kotlin {
    sourceSets {
        commonMain.dependencies {
            api(project(":core:common"))
        }
    }
}
