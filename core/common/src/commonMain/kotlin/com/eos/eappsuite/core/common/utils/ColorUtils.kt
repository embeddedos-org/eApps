package com.eos.eappsuite.core.common.utils

object ColorUtils {
    fun hexToRgb(hex: String): Triple<Int, Int, Int> {
        val clean = hex.removePrefix("#")
        require(clean.length == 6) { "Invalid hex color: $hex" }
        val r = clean.substring(0, 2).toInt(16)
        val g = clean.substring(2, 4).toInt(16)
        val b = clean.substring(4, 6).toInt(16)
        return Triple(r, g, b)
    }

    fun rgbToHex(r: Int, g: Int, b: Int): String =
        "#${r.toByte().toHexPad()}${g.toByte().toHexPad()}${b.toByte().toHexPad()}"

    fun darken(hex: String, factor: Float = 0.2f): String {
        val (r, g, b) = hexToRgb(hex)
        val f = (1f - factor).coerceIn(0f, 1f)
        return rgbToHex((r * f).toInt(), (g * f).toInt(), (b * f).toInt())
    }

    fun lighten(hex: String, factor: Float = 0.2f): String {
        val (r, g, b) = hexToRgb(hex)
        return rgbToHex(
            (r + (255 - r) * factor).toInt().coerceIn(0, 255),
            (g + (255 - g) * factor).toInt().coerceIn(0, 255),
            (b + (255 - b) * factor).toInt().coerceIn(0, 255)
        )
    }

    fun withAlpha(hex: String, alpha: Float): String {
        val clean = hex.removePrefix("#")
        val a = (alpha * 255).toInt().coerceIn(0, 255)
        return "#${a.toByte().toHexPad()}$clean"
    }

    private fun Byte.toHexPad(): String =
        toUByte().toString(16).padStart(2, '0')
}
