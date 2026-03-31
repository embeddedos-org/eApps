plugins {
    `kotlin-dsl`
}

dependencies {
    compileOnly(libs.plugins.kotlin.multiplatform.get().pluginArtifact())
    compileOnly(libs.plugins.compose.multiplatform.get().pluginArtifact())
    compileOnly(libs.plugins.compose.compiler.get().pluginArtifact())
    compileOnly(libs.plugins.android.library.get().pluginArtifact())
    compileOnly(libs.plugins.android.application.get().pluginArtifact())
    compileOnly(libs.plugins.kotlin.serialization.get().pluginArtifact())
}

fun Provider<PluginDependency>.pluginArtifact() =
    map { "${it.pluginId}:${it.pluginId}.gradle.plugin:${it.version}" }
