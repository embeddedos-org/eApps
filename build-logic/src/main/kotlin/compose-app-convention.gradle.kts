import org.jetbrains.compose.desktop.application.dsl.TargetFormat

plugins {
    id("org.jetbrains.kotlin.multiplatform")
    id("org.jetbrains.kotlin.plugin.serialization")
    id("org.jetbrains.compose")
    id("org.jetbrains.kotlin.plugin.compose")
    id("com.android.application")
}

fun prop(name: String, default: String = "true") =
    providers.gradleProperty(name).getOrElse(default)

kotlin {
    val enableAndroid = prop("eapps.target.android").toBoolean()
    val enableJvm = prop("eapps.target.jvm").toBoolean()
    val enableWasm = prop("eapps.target.wasm").toBoolean()
    val enableIos = prop("eapps.target.ios").toBoolean()

    if (enableAndroid) {
        androidTarget {
            compilations.all {
                compileTaskProvider.configure {
                    compilerOptions {
                        jvmTarget.set(org.jetbrains.kotlin.gradle.dsl.JvmTarget.JVM_17)
                    }
                }
            }
        }
    }
    if (enableJvm) {
        jvm()
    }
    if (enableIos) {
        iosArm64()
        iosSimulatorArm64()
        iosX64()
    }
    if (enableWasm) {
        @OptIn(org.jetbrains.kotlin.gradle.ExperimentalWasmDsl::class)
        wasmJs { browser() }
    }

    applyDefaultHierarchyTemplate()

    sourceSets {
        commonMain.dependencies {
            implementation(libs.findLibrary("kotlinx-coroutines-core").get())
            implementation(libs.findLibrary("kotlinx-serialization-json").get())
            implementation(libs.findLibrary("kotlinx-datetime").get())
            implementation(compose.runtime)
            implementation(compose.foundation)
            implementation(compose.material3)
            implementation(compose.ui)
            implementation(compose.components.resources)
        }
        commonTest.dependencies {
            implementation(libs.findLibrary("kotlin-test").get())
        }
        if (enableAndroid) {
            androidMain.dependencies {
                implementation(compose.preview)
            }
        }
        if (enableJvm) {
            jvmMain.dependencies {
                implementation(compose.desktop.currentOs)
            }
        }
    }
}

android {
    compileSdk = libs.findVersion("android-compileSdk").get().toString().toInt()
    defaultConfig {
        minSdk = libs.findVersion("android-minSdk").get().toString().toInt()
        targetSdk = libs.findVersion("android-targetSdk").get().toString().toInt()
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}
