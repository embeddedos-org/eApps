package com.eos.eapps.apps.eclock

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.delay
import kotlinx.datetime.Clock
import kotlinx.datetime.TimeZone
import kotlinx.datetime.toLocalDateTime

@Composable
fun AppContent() {
    var currentTime by remember { mutableStateOf("") }
    var stopwatchMs by remember { mutableStateOf(0L) }
    var stopwatchRunning by remember { mutableStateOf(false) }
    var selectedTab by remember { mutableStateOf(0) }

    LaunchedEffect(Unit) {
        while (true) { delay(1000); val now = Clock.System.now().toLocalDateTime(TimeZone.currentSystemDefault()); currentTime = "%02d:%02d:%02d".format(now.hour, now.minute, now.second) }
    }
    LaunchedEffect(stopwatchRunning) {
        while (stopwatchRunning) { delay(10); stopwatchMs += 10 }
    }

    Column(modifier = Modifier.fillMaxSize().padding(16.dp), horizontalAlignment = Alignment.CenterHorizontally) {
        Text("🕐 eClock", style = MaterialTheme.typography.headlineMedium)
        TabRow(selectedTabIndex = selectedTab) {
            Tab(selected = selectedTab == 0, onClick = { selectedTab = 0 }) { Text("Clock", modifier = Modifier.padding(12.dp)) }
            Tab(selected = selectedTab == 1, onClick = { selectedTab = 1 }) { Text("Stopwatch", modifier = Modifier.padding(12.dp)) }
        }
        Spacer(Modifier.height(32.dp))
        when (selectedTab) {
            0 -> {
                Text(currentTime, fontSize = 64.sp, style = MaterialTheme.typography.displayLarge)
                val now = Clock.System.now().toLocalDateTime(TimeZone.currentSystemDefault())
                Text("${now.dayOfWeek.name}, ${now.month.name} ${now.dayOfMonth}, ${now.year}", style = MaterialTheme.typography.titleMedium)
            }
            1 -> {
                val mins = stopwatchMs / 60000; val secs = (stopwatchMs % 60000) / 1000; val ms = (stopwatchMs % 1000) / 10
                Text("%02d:%02d.%02d".format(mins, secs, ms), fontSize = 64.sp, style = MaterialTheme.typography.displayLarge)
                Spacer(Modifier.height(16.dp))
                Row(horizontalArrangement = Arrangement.spacedBy(16.dp)) {
                    Button(onClick = { stopwatchRunning = !stopwatchRunning }) { Text(if (stopwatchRunning) "Stop" else "Start") }
                    OutlinedButton(onClick = { stopwatchRunning = false; stopwatchMs = 0 }) { Text("Reset") }
                }
            }
        }
    }
}
package com.eos.eapps.apps.eclock

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.eos.eapps.core.common.utils.DateUtils
import com.eos.eapps.core.ui.components.AppCard
import com.eos.eapps.core.ui.theme.AppTheme
import kotlinx.coroutines.delay
import kotlinx.datetime.TimeZone
import kotlinx.datetime.toLocalDateTime

@Composable
fun App() {
    AppTheme {
        var selectedTab by remember { mutableStateOf(0) }
        val tabs = listOf("World Clock", "Stopwatch", "Timer")

        Scaffold(
            topBar = {
                @OptIn(ExperimentalMaterial3Api::class)
                TopAppBar(title = { Text("eClock") })
            }
        ) { padding ->
            Column(modifier = Modifier.fillMaxSize().padding(padding)) {
                TabRow(selectedTabIndex = selectedTab) {
                    tabs.forEachIndexed { index, title ->
                        Tab(selected = selectedTab == index, onClick = { selectedTab = index }, text = { Text(title) })
                    }
                }
                when (selectedTab) {
                    0 -> WorldClockTab()
                    1 -> StopwatchTab()
                    2 -> TimerTab()
                }
            }
        }
    }
}

@Composable
private fun WorldClockTab() {
    var tick by remember { mutableStateOf(0L) }
    LaunchedEffect(Unit) {
        while (true) { delay(1000); tick++ }
    }

    val now = DateUtils.now()
    LazyColumn(modifier = Modifier.fillMaxSize().padding(vertical = 8.dp)) {
        items(DateUtils.WORLD_CLOCK_CITIES.entries.toList()) { (city, tzId) ->
            val tz = try { TimeZone.of(tzId) } catch (_: Exception) { TimeZone.UTC }
            val localTime = now.toLocalDateTime(tz)
            val timeStr = "%02d:%02d:%02d".format(localTime.hour, localTime.minute, localTime.second)
            val dateStr = "${localTime.year}-%02d-%02d".format(localTime.monthNumber, localTime.dayOfMonth)
            val offset = DateUtils.getTimezoneOffset(tz)
            val offsetHours = offset / 60
            val offsetStr = if (offsetHours >= 0) "UTC+$offsetHours" else "UTC$offsetHours"

            AppCard {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column {
                        Text(city, style = MaterialTheme.typography.titleMedium)
                        Text("$dateStr • $offsetStr", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    }
                    Text(timeStr, style = MaterialTheme.typography.headlineSmall, color = MaterialTheme.colorScheme.primary)
                }
            }
        }
    }
}

@Composable
private fun StopwatchTab() {
    var isRunning by remember { mutableStateOf(false) }
    var elapsedMs by remember { mutableStateOf(0L) }
    val laps = remember { mutableStateListOf<Long>() }

    LaunchedEffect(isRunning) {
        if (isRunning) {
            val start = kotlinx.datetime.Clock.System.now().toEpochMilliseconds() - elapsedMs
            while (isRunning) {
                elapsedMs = kotlinx.datetime.Clock.System.now().toEpochMilliseconds() - start
                delay(10)
            }
        }
    }

    Column(
        modifier = Modifier.fillMaxSize().padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Spacer(Modifier.height(32.dp))
        Text(
            formatStopwatch(elapsedMs),
            style = MaterialTheme.typography.displayLarge.copy(fontSize = 48.sp),
            color = MaterialTheme.colorScheme.primary
        )
        Spacer(Modifier.height(32.dp))
        Row(horizontalArrangement = Arrangement.spacedBy(16.dp)) {
            if (isRunning) {
                FilledTonalButton(onClick = { laps.add(0, elapsedMs) }) { Text("Lap") }
                Button(onClick = { isRunning = false }) { Text("Stop") }
            } else {
                if (elapsedMs > 0) {
                    FilledTonalButton(onClick = { elapsedMs = 0; laps.clear() }) { Text("Reset") }
                }
                Button(onClick = { isRunning = true }) { Text(if (elapsedMs > 0) "Resume" else "Start") }
            }
        }
        Spacer(Modifier.height(24.dp))
        if (laps.isNotEmpty()) {
            HorizontalDivider()
            LazyColumn(modifier = Modifier.fillMaxSize()) {
                items(laps.size) { index ->
                    Row(
                        modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp, horizontal = 8.dp),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Text("Lap ${laps.size - index}", style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
                        Text(formatStopwatch(laps[index]), style = MaterialTheme.typography.bodyMedium)
                    }
                    HorizontalDivider()
                }
            }
        }
    }
}

@Composable
private fun TimerTab() {
    var hours by remember { mutableStateOf(0) }
    var minutes by remember { mutableStateOf(5) }
    var seconds by remember { mutableStateOf(0) }
    var isRunning by remember { mutableStateOf(false) }
    var remainingMs by remember { mutableStateOf(0L) }
    var isAlarm by remember { mutableStateOf(false) }

    LaunchedEffect(isRunning) {
        if (isRunning && remainingMs > 0) {
            val start = kotlinx.datetime.Clock.System.now().toEpochMilliseconds()
            val initial = remainingMs
            while (isRunning && remainingMs > 0) {
                val elapsed = kotlinx.datetime.Clock.System.now().toEpochMilliseconds() - start
                remainingMs = (initial - elapsed).coerceAtLeast(0)
                if (remainingMs == 0L) { isRunning = false; isAlarm = true }
                delay(100)
            }
        }
    }

    Column(
        modifier = Modifier.fillMaxSize().padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        if (isAlarm) {
            Text("TIME'S UP!", style = MaterialTheme.typography.displaySmall, color = MaterialTheme.colorScheme.error)
            Spacer(Modifier.height(24.dp))
            Button(onClick = { isAlarm = false; remainingMs = 0 }) { Text("Dismiss") }
        } else if (isRunning || remainingMs > 0) {
            val totalSec = remainingMs / 1000
            val h = totalSec / 3600; val m = (totalSec % 3600) / 60; val s = totalSec % 60
            Text(
                "%02d:%02d:%02d".format(h, m, s),
                style = MaterialTheme.typography.displayLarge.copy(fontSize = 56.sp),
                color = MaterialTheme.colorScheme.primary
            )
            Spacer(Modifier.height(32.dp))
            Row(horizontalArrangement = Arrangement.spacedBy(16.dp)) {
                FilledTonalButton(onClick = { isRunning = false; remainingMs = 0 }) { Text("Cancel") }
                Button(onClick = { isRunning = !isRunning }) { Text(if (isRunning) "Pause" else "Resume") }
            }
        } else {
            Text("Set Timer", style = MaterialTheme.typography.headlineSmall)
            Spacer(Modifier.height(24.dp))
            Row(
                horizontalArrangement = Arrangement.spacedBy(8.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                TimerPicker("H", hours, 0..23) { hours = it }
                Text(":", style = MaterialTheme.typography.headlineMedium)
                TimerPicker("M", minutes, 0..59) { minutes = it }
                Text(":", style = MaterialTheme.typography.headlineMedium)
                TimerPicker("S", seconds, 0..59) { seconds = it }
            }
            Spacer(Modifier.height(32.dp))
            Button(
                onClick = {
                    remainingMs = ((hours * 3600L) + (minutes * 60L) + seconds) * 1000L
                    if (remainingMs > 0) isRunning = true
                },
                enabled = hours > 0 || minutes > 0 || seconds > 0
            ) { Text("Start") }
        }
    }
}

@Composable
private fun TimerPicker(label: String, value: Int, range: IntRange, onChange: (Int) -> Unit) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        IconButton(onClick = { if (value < range.last) onChange(value + 1) }) {
            Icon(Icons.Default.KeyboardArrowUp, contentDescription = "Increase $label")
        }
        Text("%02d".format(value), style = MaterialTheme.typography.displaySmall)
        Text(label, style = MaterialTheme.typography.labelSmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
        IconButton(onClick = { if (value > range.first) onChange(value - 1) }) {
            Icon(Icons.Default.KeyboardArrowDown, contentDescription = "Decrease $label")
        }
    }
}

private fun formatStopwatch(ms: Long): String {
    val totalSec = ms / 1000
    val min = totalSec / 60; val sec = totalSec % 60; val centis = (ms % 1000) / 10
    return "%02d:%02d.%02d".format(min, sec, centis)
}
