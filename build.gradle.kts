plugins {
    alias(libs.plugins.kotlin.multiplatform) apply false
    alias(libs.plugins.kotlin.serialization) apply false
    alias(libs.plugins.compose.multiplatform) apply false
    alias(libs.plugins.compose.compiler) apply false
    alias(libs.plugins.android.application) apply false
    alias(libs.plugins.android.library) apply false
    alias(libs.plugins.sqldelight) apply false
}

allprojects {
    group = property("eapps.group").toString()
    version = property("eapps.version").toString()
}

fun prop(name: String, default: String = "true") =
    (extra.properties[name] as? String) ?: providers.gradleProperty(name).getOrElse(default)

val enableAndroid = prop("eapps.target.android").toBoolean()
val enableJvm = prop("eapps.target.jvm").toBoolean()
val enableWasm = prop("eapps.target.wasm").toBoolean()

tasks.register("buildSuite") {
    group = "eApps"
    description = "Builds the suite launcher for all enabled platforms"
    if (enableAndroid) dependsOn(":apps:suite:assembleDebug")
    if (enableJvm) dependsOn(":apps:suite:jvmJar")
    if (enableWasm) dependsOn(":apps:suite:wasmJsBrowserDistribution")
}

tasks.register("buildAllApps") {
    group = "eApps"
    description = "Builds every app standalone"
    subprojects {
        if (path.startsWith(":apps:")) {
            this@register.dependsOn("$path:build")
        }
    }
}

tasks.register("buildAndroid") {
    group = "eApps"
    description = "Builds all apps as Android APKs"
    subprojects {
        if (path.startsWith(":apps:")) {
            this@register.dependsOn("$path:assembleDebug")
        }
    }
}

tasks.register("buildDesktop") {
    group = "eApps"
    description = "Builds all apps as JVM desktop executables"
    subprojects {
        if (path.startsWith(":apps:")) {
            this@register.dependsOn("$path:jvmJar")
        }
    }
}

tasks.register("buildWeb") {
    group = "eApps"
    description = "Builds all apps as WASM bundles"
    subprojects {
        if (path.startsWith(":apps:")) {
            this@register.dependsOn("$path:wasmJsBrowserDistribution")
        }
    }
}

tasks.register("buildIos") {
    group = "eApps"
    description = "Builds all apps as iOS frameworks"
    subprojects {
        if (path.startsWith(":apps:")) {
            this@register.dependsOn("$path:linkReleaseFrameworkIosArm64")
        }
    }
}
