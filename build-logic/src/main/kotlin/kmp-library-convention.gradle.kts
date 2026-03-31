plugins {
    id("org.jetbrains.kotlin.multiplatform")
    id("org.jetbrains.kotlin.plugin.serialization")
    id("com.android.library")
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
        }
        commonTest.dependencies {
            implementation(libs.findLibrary("kotlin-test").get())
        }
    }
}

android {
    compileSdk = libs.findVersion("android-compileSdk").get().toString().toInt()
    defaultConfig {
        minSdk = libs.findVersion("android-minSdk").get().toString().toInt()
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}
