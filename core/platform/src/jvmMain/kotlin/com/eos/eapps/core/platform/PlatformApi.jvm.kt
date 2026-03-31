package com.eos.eapps.core.platform

actual object Clipboard {
    actual fun getText(): String? = try {
        val toolkit = java.awt.Toolkit.getDefaultToolkit()
        val contents = toolkit.systemClipboard.getContents(null)
        if (contents?.isDataFlavorSupported(java.awt.datatransfer.DataFlavor.stringFlavor) == true)
            contents.getTransferData(java.awt.datatransfer.DataFlavor.stringFlavor) as String
        else null
    } catch (_: Exception) { null }

    actual fun setText(text: String) {
        val toolkit = java.awt.Toolkit.getDefaultToolkit()
        val selection = java.awt.datatransfer.StringSelection(text)
        toolkit.systemClipboard.setContents(selection, null)
    }

    actual fun hasText(): Boolean = getText() != null
}

actual object SystemInfo {
    actual fun osName(): String = System.getProperty("os.name", "Unknown")
    actual fun osVersion(): String = System.getProperty("os.version", "Unknown")
    actual fun cpuArch(): String = System.getProperty("os.arch", "Unknown")
    actual fun totalMemoryMB(): Long = Runtime.getRuntime().maxMemory() / (1024 * 1024)
    actual fun isDesktop(): Boolean = true
    actual fun isMobile(): Boolean = false
}

actual object ScreenKeepAwake {
    private var enabled = false
    actual fun enable() { enabled = true }
    actual fun disable() { enabled = false }
    actual fun isEnabled(): Boolean = enabled
}

actual object ProcessLauncher {
    actual fun launch(command: String, args: List<String>): Int {
        val pb = ProcessBuilder(listOf(command) + args)
        pb.inheritIO()
        val process = pb.start()
        return process.waitFor()
    }

    actual fun launchAsync(command: String, args: List<String>) {
        val pb = ProcessBuilder(listOf(command) + args)
        pb.inheritIO()
        pb.start()
    }
}
