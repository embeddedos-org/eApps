package com.eos.eapps.core.platform

actual object Clipboard {
    actual fun getText(): String? = null
    actual fun setText(text: String) {}
    actual fun hasText(): Boolean = false
}

actual object SystemInfo {
    actual fun osName(): String = "Android"
    actual fun osVersion(): String = android.os.Build.VERSION.RELEASE
    actual fun cpuArch(): String = android.os.Build.SUPPORTED_ABIS.firstOrNull() ?: "unknown"
    actual fun totalMemoryMB(): Long {
        val rt = Runtime.getRuntime()
        return rt.maxMemory() / (1024 * 1024)
    }
    actual fun isDesktop(): Boolean = false
    actual fun isMobile(): Boolean = true
}

actual object ScreenKeepAwake {
    private var enabled = false
    actual fun enable() { enabled = true }
    actual fun disable() { enabled = false }
    actual fun isEnabled(): Boolean = enabled
}

actual object ProcessLauncher {
    actual fun launch(command: String, args: List<String>): Int = try {
        val process = Runtime.getRuntime().exec((listOf(command) + args).toTypedArray())
        process.waitFor()
    } catch (_: Exception) { -1 }

    actual fun launchAsync(command: String, args: List<String>) {
        try {
            Runtime.getRuntime().exec((listOf(command) + args).toTypedArray())
        } catch (_: Exception) {}
    }
}
package com.eos.eapps.core.platform

import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.os.Build
import android.view.WindowManager

object AndroidContextHolder {
    lateinit var context: Context
}

actual object Clipboard {
    actual fun getText(): String? {
        val cm = AndroidContextHolder.context.getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
        return cm.primaryClip?.getItemAt(0)?.text?.toString()
    }

    actual fun setText(text: String) {
        val cm = AndroidContextHolder.context.getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
        cm.setPrimaryClip(ClipData.newPlainText("eApps", text))
    }

    actual fun hasText(): Boolean {
        val cm = AndroidContextHolder.context.getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
        return cm.hasPrimaryClip()
    }
}

actual object SystemInfo {
    actual fun osName(): String = "Android"
    actual fun osVersion(): String = "API ${Build.VERSION.SDK_INT}"
    actual fun cpuArch(): String = Build.SUPPORTED_ABIS.firstOrNull() ?: "unknown"
    actual fun totalMemoryMB(): Long = Runtime.getRuntime().maxMemory() / (1024 * 1024)
    actual fun isDesktop(): Boolean = false
    actual fun isMobile(): Boolean = true
}

actual object ScreenKeepAwake {
    private var enabled = false
    actual fun enable() { enabled = true }
    actual fun disable() { enabled = false }
    actual fun isEnabled(): Boolean = enabled
}

actual object ProcessLauncher {
    actual fun launch(command: String, args: List<String>): Int = -1
    actual fun launchAsync(command: String, args: List<String>) {}
}
