package com.eos.eapps.core.storage

import com.russhwolf.settings.Settings

class AppPreferences(private val appId: String) {
    private val settings: Settings = Settings()

    private fun key(name: String) = "${appId}_$name"

    fun getString(name: String, default: String = ""): String =
        settings.getString(key(name), default)

    fun putString(name: String, value: String) =
        settings.putString(key(name), value)

    fun getInt(name: String, default: Int = 0): Int =
        settings.getInt(key(name), default)

    fun putInt(name: String, value: Int) =
        settings.putInt(key(name), value)

    fun getBoolean(name: String, default: Boolean = false): Boolean =
        settings.getBoolean(key(name), default)

    fun putBoolean(name: String, value: Boolean) =
        settings.putBoolean(key(name), value)

    fun getFloat(name: String, default: Float = 0f): Float =
        settings.getFloat(key(name), default)

    fun putFloat(name: String, value: Float) =
        settings.putFloat(key(name), value)

    fun getLong(name: String, default: Long = 0L): Long =
        settings.getLong(key(name), default)

    fun putLong(name: String, value: Long) =
        settings.putLong(key(name), value)

    fun remove(name: String) = settings.remove(key(name))
    fun clear() = settings.clear()
    fun hasKey(name: String): Boolean = settings.hasKey(key(name))

    var isDarkMode: Boolean
        get() = getBoolean("darkMode", true)
        set(value) = putBoolean("darkMode", value)

    var locale: String
        get() = getString("locale", "en")
        set(value) = putString("locale", value)

    var isFirstLaunch: Boolean
        get() = getBoolean("firstLaunch", true)
        set(value) = putBoolean("firstLaunch", value)
}
