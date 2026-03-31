package com.eos.eappsuite.core.common.utils

import kotlinx.datetime.*

object DateUtils {
    fun now(): Instant = Clock.System.now()

    fun today(): LocalDate = now().toLocalDateTime(TimeZone.currentSystemDefault()).date

    fun nowLocal(): LocalDateTime = now().toLocalDateTime(TimeZone.currentSystemDefault())

    fun formatDate(instant: Instant, timeZone: TimeZone = TimeZone.currentSystemDefault()): String {
        val dt = instant.toLocalDateTime(timeZone)
        return "${dt.year}-${dt.monthNumber.pad()}-${dt.dayOfMonth.pad()}"
    }

    fun formatTime(instant: Instant, timeZone: TimeZone = TimeZone.currentSystemDefault()): String {
        val dt = instant.toLocalDateTime(timeZone)
        return "${dt.hour.pad()}:${dt.minute.pad()}:${dt.second.pad()}"
    }

    fun formatDateTime(instant: Instant, timeZone: TimeZone = TimeZone.currentSystemDefault()): String =
        "${formatDate(instant, timeZone)} ${formatTime(instant, timeZone)}"

    fun timeAgo(instant: Instant): String {
        val diff = now() - instant
        return when {
            diff.inWholeSeconds < 60 -> "just now"
            diff.inWholeMinutes < 60 -> "${diff.inWholeMinutes}m ago"
            diff.inWholeHours < 24 -> "${diff.inWholeHours}h ago"
            diff.inWholeDays < 30 -> "${diff.inWholeDays}d ago"
            diff.inWholeDays < 365 -> "${diff.inWholeDays / 30}mo ago"
            else -> "${diff.inWholeDays / 365}y ago"
        }
    }

    fun parseIso(isoString: String): Instant = Instant.parse(isoString)

    fun toEpochMillis(instant: Instant): Long = instant.toEpochMilliseconds()

    fun fromEpochMillis(millis: Long): Instant = Instant.fromEpochMilliseconds(millis)

    fun daysBetween(start: LocalDate, end: LocalDate): Int =
        end.toEpochDays() - start.toEpochDays()

    fun isToday(date: LocalDate): Boolean = date == today()

    fun getTimezoneOffset(timeZone: TimeZone): Int {
        val now = now()
        val utcDt = now.toLocalDateTime(TimeZone.UTC)
        val localDt = now.toLocalDateTime(timeZone)
        return (localDt.hour - utcDt.hour) * 60 + (localDt.minute - utcDt.minute)
    }

    val WORLD_CLOCK_CITIES = mapOf(
        "New York" to "America/New_York",
        "Los Angeles" to "America/Los_Angeles",
        "Chicago" to "America/Chicago",
        "London" to "Europe/London",
        "Paris" to "Europe/Paris",
        "Berlin" to "Europe/Berlin",
        "Moscow" to "Europe/Moscow",
        "Dubai" to "Asia/Dubai",
        "Mumbai" to "Asia/Kolkata",
        "Shanghai" to "Asia/Shanghai",
        "Tokyo" to "Asia/Tokyo",
        "Sydney" to "Australia/Sydney",
        "Auckland" to "Pacific/Auckland",
        "São Paulo" to "America/Sao_Paulo",
        "Cairo" to "Africa/Cairo",
        "Istanbul" to "Europe/Istanbul",
        "Singapore" to "Asia/Singapore",
        "Hong Kong" to "Asia/Hong_Kong",
        "Seoul" to "Asia/Seoul",
        "Bangkok" to "Asia/Bangkok",
        "Jakarta" to "Asia/Jakarta",
        "Nairobi" to "Africa/Nairobi",
        "Johannesburg" to "Africa/Johannesburg",
        "Toronto" to "America/Toronto",
        "Vancouver" to "America/Vancouver",
        "Mexico City" to "America/Mexico_City",
        "Lima" to "America/Lima",
        "Buenos Aires" to "America/Argentina/Buenos_Aires",
        "Honolulu" to "Pacific/Honolulu",
        "Anchorage" to "America/Anchorage"
    )

    private fun Int.pad(): String = toString().padStart(2, '0')
}
package com.eos.eappsuite.core.common.utils

import kotlinx.datetime.*

object DateUtils {
    fun now(): Instant = Clock.System.now()

    fun today(): LocalDate = now().toLocalDateTime(TimeZone.currentSystemDefault()).date

    fun formatDate(instant: Instant, pattern: String = "yyyy-MM-dd"): String {
        val dt = instant.toLocalDateTime(TimeZone.currentSystemDefault())
        return "${dt.year}-${dt.monthNumber.toString().padStart(2, '0')}-${dt.dayOfMonth.toString().padStart(2, '0')}"
    }

    fun formatTime(instant: Instant): String {
        val dt = instant.toLocalDateTime(TimeZone.currentSystemDefault())
        return "${dt.hour.toString().padStart(2, '0')}:${dt.minute.toString().padStart(2, '0')}:${dt.second.toString().padStart(2, '0')}"
    }

    fun formatDateTime(instant: Instant): String =
        "${formatDate(instant)} ${formatTime(instant)}"

    fun timeAgo(instant: Instant): String {
        val diff = now() - instant
        return when {
            diff.inWholeSeconds < 60 -> "just now"
            diff.inWholeMinutes < 60 -> "${diff.inWholeMinutes}m ago"
            diff.inWholeHours < 24 -> "${diff.inWholeHours}h ago"
            diff.inWholeDays < 7 -> "${diff.inWholeDays}d ago"
            diff.inWholeDays < 30 -> "${diff.inWholeDays / 7}w ago"
            diff.inWholeDays < 365 -> "${diff.inWholeDays / 30}mo ago"
            else -> "${diff.inWholeDays / 365}y ago"
        }
    }

    fun isToday(instant: Instant): Boolean {
        val dt = instant.toLocalDateTime(TimeZone.currentSystemDefault())
        return dt.date == today()
    }

    fun isYesterday(instant: Instant): Boolean {
        val dt = instant.toLocalDateTime(TimeZone.currentSystemDefault())
        val yesterday = now().minus(1, DateTimeUnit.DAY, TimeZone.currentSystemDefault())
            .toLocalDateTime(TimeZone.currentSystemDefault())
        return dt.date == yesterday.date
    }
}
