package com.eos.eapps.core.common.models

import kotlinx.serialization.Serializable

@Serializable
enum class AppCategory(val displayName: String, val icon: String) {
    PRODUCTIVITY("Productivity", "🔧"),
    MEDIA("Media", "🎵"),
    GAMES("Games", "🎮"),
    CONNECTIVITY("Connectivity", "🔌"),
    SECURITY("Security", "🛡️"),
    WEB("Web", "🌐"),
    SUITE("Suite", "📦"),
}

@Serializable
data class AppInfo(
    val id: String,
    val name: String,
    val displayName: String,
    val category: AppCategory,
    val version: String = "1.0.0",
    val icon: String = "",
    val description: String = "",
    val platforms: Set<Platform> = Platform.ALL,
)

@Serializable
enum class Platform {
    ANDROID, IOS, WINDOWS, MACOS, LINUX, WEB;

    companion object {
        val ALL = entries.toSet()
        val MOBILE = setOf(ANDROID, IOS)
        val DESKTOP = setOf(WINDOWS, MACOS, LINUX)
    }
}

@Serializable
data class ThemeConfig(
    val isDarkMode: Boolean = true,
    val accentColor: Long = 0xFF2998FF,
    val fontSize: Float = 14f,
)

@Serializable
data class UserPrefs(
    val theme: ThemeConfig = ThemeConfig(),
    val locale: String = "en",
    val favoriteApps: List<String> = emptyList(),
    val recentApps: List<String> = emptyList(),
)
