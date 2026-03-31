package com.eos.eapps.core.common.utils

import kotlin.math.abs
import kotlin.math.ln
import kotlin.math.log10
import kotlin.math.pow
import kotlin.math.round

object MathUtils {
    fun clamp(value: Double, min: Double, max: Double): Double =
        value.coerceIn(min, max)

    fun clamp(value: Float, min: Float, max: Float): Float =
        value.coerceIn(min, max)

    fun clamp(value: Int, min: Int, max: Int): Int =
        value.coerceIn(min, max)

    fun lerp(start: Double, end: Double, fraction: Double): Double =
        start + (end - start) * fraction

    fun lerp(start: Float, end: Float, fraction: Float): Float =
        start + (end - start) * fraction

    fun inverseLerp(start: Double, end: Double, value: Double): Double =
        if (start == end) 0.0 else (value - start) / (end - start)

    fun map(value: Double, inMin: Double, inMax: Double, outMin: Double, outMax: Double): Double =
        lerp(outMin, outMax, inverseLerp(inMin, inMax, value))

    fun formatFileSize(bytes: Long): String = when {
        bytes < 1024 -> "$bytes B"
        bytes < 1024 * 1024 -> "${roundTo(bytes / 1024.0, 1)} KB"
        bytes < 1024 * 1024 * 1024 -> "${roundTo(bytes / (1024.0 * 1024.0), 1)} MB"
        else -> "${roundTo(bytes / (1024.0 * 1024.0 * 1024.0), 2)} GB"
    }

    fun formatDuration(totalSeconds: Long): String {
        val hours = totalSeconds / 3600
        val minutes = (totalSeconds % 3600) / 60
        val seconds = totalSeconds % 60
        return if (hours > 0) "%d:%02d:%02d".format(hours, minutes, seconds)
        else "%d:%02d".format(minutes, seconds)
    }

    fun formatDurationMillis(millis: Long): String {
        val totalSeconds = millis / 1000
        val ms = millis % 1000
        val minutes = totalSeconds / 60
        val seconds = totalSeconds % 60
        return if (minutes > 0) "%d:%02d.%03d".format(minutes, seconds, ms)
        else "%d.%03d".format(seconds, ms)
    }

    fun roundTo(value: Double, decimals: Int): Double {
        val factor = 10.0.pow(decimals)
        return round(value * factor) / factor
    }

    fun percentage(part: Double, total: Double): Double =
        if (total == 0.0) 0.0 else (part / total) * 100.0

    fun isApproximatelyEqual(a: Double, b: Double, epsilon: Double = 1e-9): Boolean =
        abs(a - b) < epsilon

    private fun String.format(vararg args: Any?): String {
        var result = this
        var argIdx = 0
        val regex = Regex("%[-+]?\\d*\\.?\\d*[dfsxo%]")
        result = regex.replace(result) { match ->
            if (match.value == "%%") "%"
            else {
                val arg = args.getOrNull(argIdx++) ?: return@replace match.value
                formatArg(match.value, arg)
            }
        }
        return result
    }

    private fun formatArg(fmt: String, arg: Any?): String {
        val spec = fmt.last()
        return when (spec) {
            'd' -> (arg as Number).toLong().toString().let { padResult(fmt, it) }
            'f' -> {
                val precision = Regex("\\.(\\d+)").find(fmt)?.groupValues?.get(1)?.toIntOrNull() ?: 6
                val value = (arg as Number).toDouble()
                val s = roundTo(value, precision).toString()
                val dotIdx = s.indexOf('.')
                val currentDecimals = if (dotIdx >= 0) s.length - dotIdx - 1 else 0
                val padded = if (currentDecimals < precision) s + "0".repeat(precision - currentDecimals) else s
                padResult(fmt, padded)
            }
            's' -> padResult(fmt, arg.toString())
            else -> arg.toString()
        }
    }

    private fun padResult(fmt: String, value: String): String {
        val width = Regex("%([-+])?(\\d+)").find(fmt)
        if (width != null) {
            val w = width.groupValues[2].toIntOrNull() ?: return value
            val leftAlign = width.groupValues[1] == "-"
            val padChar = if (fmt.contains("0") && !leftAlign) '0' else ' '
            return if (leftAlign) value.padEnd(w, padChar) else value.padStart(w, padChar)
        }
        return value
    }
}
package com.eos.eapps.core.common.utils

import kotlin.math.*

object MathUtils {
    fun clamp(value: Double, min: Double, max: Double): Double =
        value.coerceIn(min, max)

    fun clamp(value: Float, min: Float, max: Float): Float =
        value.coerceIn(min, max)

    fun clamp(value: Int, min: Int, max: Int): Int =
        value.coerceIn(min, max)

    fun lerp(start: Double, end: Double, t: Double): Double =
        start + (end - start) * t

    fun map(value: Double, inMin: Double, inMax: Double, outMin: Double, outMax: Double): Double =
        outMin + (value - inMin) * (outMax - outMin) / (inMax - inMin)

    fun degToRad(degrees: Double): Double = degrees * PI / 180.0
    fun radToDeg(radians: Double): Double = radians * 180.0 / PI

    fun distance2D(x1: Double, y1: Double, x2: Double, y2: Double): Double =
        sqrt((x2 - x1).pow(2) + (y2 - y1).pow(2))

    fun formatFileSize(bytes: Long): String = when {
        bytes < 1024 -> "$bytes B"
        bytes < 1024 * 1024 -> "${bytes / 1024} KB"
        bytes < 1024 * 1024 * 1024 -> "${"%.1f".format(bytes / (1024.0 * 1024.0))} MB"
        else -> "${"%.2f".format(bytes / (1024.0 * 1024.0 * 1024.0))} GB"
    }

    fun formatDuration(seconds: Long): String {
        val h = seconds / 3600
        val m = (seconds % 3600) / 60
        val s = seconds % 60
        return if (h > 0) "%d:%02d:%02d".format(h, m, s)
        else "%d:%02d".format(m, s)
    }

    fun formatDurationMs(millis: Long): String {
        val totalSeconds = millis / 1000
        val ms = millis % 1000
        val h = totalSeconds / 3600
        val m = (totalSeconds % 3600) / 60
        val s = totalSeconds % 60
        return if (h > 0) "%d:%02d:%02d.%03d".format(h, m, s, ms)
        else "%d:%02d.%03d".format(m, s, ms)
    }
}
