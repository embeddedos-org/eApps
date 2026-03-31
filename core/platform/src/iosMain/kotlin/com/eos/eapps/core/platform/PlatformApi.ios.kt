package com.eos.eapps.core.platform

import platform.Foundation.NSProcessInfo
import platform.UIKit.UIScreen
import platform.UIKit.UIApplication
import platform.UIKit.UIPasteboard

actual object Clipboard {
    actual fun getText(): String? = UIPasteboard.generalPasteboard.string
    actual fun setText(text: String) { UIPasteboard.generalPasteboard.string = text }
    actual fun hasText(): Boolean = UIPasteboard.generalPasteboard.hasStrings
}

actual object SystemInfo {
    actual fun osName(): String = "iOS"
    actual fun osVersion(): String = NSProcessInfo.processInfo.operatingSystemVersionString
    actual fun cpuArch(): String = "arm64"
    actual fun totalMemoryMB(): Long = (NSProcessInfo.processInfo.physicalMemory / (1024uL * 1024uL)).toLong()
    actual fun isDesktop(): Boolean = false
    actual fun isMobile(): Boolean = true
}

actual object ScreenKeepAwake {
    actual fun enable() { UIApplication.sharedApplication.idleTimerDisabled = true }
    actual fun disable() { UIApplication.sharedApplication.idleTimerDisabled = false }
    actual fun isEnabled(): Boolean = UIApplication.sharedApplication.isIdleTimerDisabled()
}

actual object ProcessLauncher {
    actual fun launch(command: String, args: List<String>): Int = -1
    actual fun launchAsync(command: String, args: List<String>) {}
}
