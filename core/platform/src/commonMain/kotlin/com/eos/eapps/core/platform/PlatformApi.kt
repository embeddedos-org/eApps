package com.eos.eapps.core.platform

expect object Clipboard {
    fun getText(): String?
    fun setText(text: String)
    fun hasText(): Boolean
}

expect object SystemInfo {
    fun osName(): String
    fun osVersion(): String
    fun cpuArch(): String
    fun totalMemoryMB(): Long
    fun isDesktop(): Boolean
    fun isMobile(): Boolean
}

expect object ScreenKeepAwake {
    fun enable()
    fun disable()
    fun isEnabled(): Boolean
}

expect object ProcessLauncher {
    fun launch(command: String, args: List<String> = emptyList()): Int
    fun launchAsync(command: String, args: List<String> = emptyList())
}
