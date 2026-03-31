package com.eos.eapps.core.common.utils

object StringUtils {
    fun truncate(text: String, maxLength: Int, suffix: String = "..."): String =
        if (text.length <= maxLength) text
        else text.take(maxLength - suffix.length) + suffix

    fun capitalize(text: String): String =
        text.replaceFirstChar { if (it.isLowerCase()) it.titlecase() else it.toString() }

    fun titleCase(text: String): String =
        text.split(" ").joinToString(" ") { capitalize(it) }

    fun camelToSnake(text: String): String =
        text.replace(Regex("([a-z])([A-Z])"), "$1_$2").lowercase()

    fun snakeToCamel(text: String): String =
        text.split("_").mapIndexed { i, w ->
            if (i == 0) w.lowercase() else capitalize(w.lowercase())
        }.joinToString("")

    fun slugify(text: String): String =
        text.lowercase()
            .replace(Regex("[^a-z0-9\\s-]"), "")
            .replace(Regex("[\\s]+"), "-")
            .trim('-')

    fun isValidEmail(email: String): Boolean =
        Regex("^[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$").matches(email)

    fun isValidUrl(url: String): Boolean =
        Regex("^https?://[\\w.-]+(:\\d+)?(/.*)?$").matches(url)

    fun isValidIpAddress(ip: String): Boolean =
        Regex("^(\\d{1,3}\\.){3}\\d{1,3}$").matches(ip) &&
            ip.split(".").all { it.toIntOrNull() in 0..255 }

    fun toHexString(bytes: ByteArray): String =
        bytes.joinToString("") { it.toUByte().toString(16).padStart(2, '0') }

    fun fromHexString(hex: String): ByteArray {
        require(hex.length % 2 == 0) { "Hex string must have even length" }
        return ByteArray(hex.length / 2) { i ->
            hex.substring(i * 2, i * 2 + 2).toInt(16).toByte()
        }
    }

    fun wordCount(text: String): Int =
        text.trim().split(Regex("\\s+")).filter { it.isNotEmpty() }.size

    fun lineCount(text: String): Int =
        if (text.isEmpty()) 0 else text.count { it == '\n' } + 1

    fun removeExtraWhitespace(text: String): String =
        text.replace(Regex("\\s+"), " ").trim()

    fun maskString(text: String, visibleChars: Int = 4, maskChar: Char = '*'): String =
        if (text.length <= visibleChars) text
        else maskChar.toString().repeat(text.length - visibleChars) + text.takeLast(visibleChars)

    fun extractNumbers(text: String): List<Double> =
        Regex("-?\\d+\\.?\\d*").findAll(text).map { it.value.toDouble() }.toList()
}
package com.eos.eapps.core.common.utils

object StringUtils {
    fun truncate(text: String, maxLength: Int, suffix: String = "..."): String =
        if (text.length <= maxLength) text
        else text.take(maxLength - suffix.length) + suffix

    fun capitalize(text: String): String =
        text.replaceFirstChar { if (it.isLowerCase()) it.titlecase() else it.toString() }

    fun toSlug(text: String): String =
        text.lowercase()
            .replace(Regex("[^a-z0-9\\s-]"), "")
            .replace(Regex("\\s+"), "-")
            .trim('-')

    fun countWords(text: String): Int =
        text.split(Regex("\\s+")).count { it.isNotBlank() }

    fun isValidEmail(email: String): Boolean =
        email.matches(Regex("^[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+$"))

    fun isValidUrl(url: String): Boolean =
        url.matches(Regex("^https?://[\\w.-]+(?:/[\\w./?%&=-]*)?$"))

    fun toHexDump(bytes: ByteArray, bytesPerLine: Int = 16): String = buildString {
        for (i in bytes.indices step bytesPerLine) {
            append("%08X: ".format(i))
            val chunk = bytes.sliceArray(i until minOf(i + bytesPerLine, bytes.size))
            for (b in chunk) append("%02X ".format(b.toInt() and 0xFF))
            repeat(bytesPerLine - chunk.size) { append("   ") }
            append(" |")
            for (b in chunk) {
                val c = b.toInt() and 0xFF
                append(if (c in 32..126) c.toChar() else '.')
            }
            appendLine("|")
        }
    }

    fun base64Encode(data: ByteArray): String {
        val chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
        return buildString {
            var i = 0
            while (i < data.size) {
                val b0 = data[i].toInt() and 0xFF
                val b1 = if (i + 1 < data.size) data[i + 1].toInt() and 0xFF else 0
                val b2 = if (i + 2 < data.size) data[i + 2].toInt() and 0xFF else 0
                append(chars[(b0 shr 2) and 0x3F])
                append(chars[((b0 shl 4) or (b1 shr 4)) and 0x3F])
                append(if (i + 1 < data.size) chars[((b1 shl 2) or (b2 shr 6)) and 0x3F] else '=')
                append(if (i + 2 < data.size) chars[b2 and 0x3F] else '=')
                i += 3
            }
        }
    }
}
