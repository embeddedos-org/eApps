package com.eos.eapps.apps.eguard

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.delay

@Composable
fun AppContent() {
    var keepAwake by remember { mutableStateOf(false) }
    var elapsedSec by remember { mutableStateOf(0) }

    LaunchedEffect(keepAwake) {
        if (keepAwake) { while (keepAwake) { delay(1000); elapsedSec++ } }
        else elapsedSec = 0
    }

    Column(modifier = Modifier.fillMaxSize().padding(16.dp), horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.Center) {
        Text("🛡️ eGuard", style = MaterialTheme.typography.headlineMedium)
        Spacer(Modifier.height(24.dp))
        Text(if (keepAwake) "🟢 Screen Guard Active" else "🔴 Screen Guard Off", style = MaterialTheme.typography.headlineSmall)
        if (keepAwake) { Spacer(Modifier.height(8.dp)); Text("Active for: ${elapsedSec / 60}m ${elapsedSec % 60}s", style = MaterialTheme.typography.bodyLarge) }
        Spacer(Modifier.height(24.dp))
        Button(onClick = { keepAwake = !keepAwake }) { Text(if (keepAwake) "Disable Guard" else "Enable Guard") }
        Spacer(Modifier.height(8.dp))
        Text("Prevents screen from turning off", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
    }
}
package com.eos.eapps.apps.eguard

import androidx.compose.animation.core.*
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.scale
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.eos.eapps.core.platform.ScreenKeepAwake
import com.eos.eapps.core.ui.theme.AppTheme
import kotlinx.coroutines.delay

data class TimerOption(val label: String, val minutes: Int)

private val timerOptions = listOf(
    TimerOption("15 min", 15),
    TimerOption("30 min", 30),
    TimerOption("1 hour", 60),
    TimerOption("2 hours", 120),
    TimerOption("Indefinite", 0)
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun App() {
    AppTheme {
        var isEnabled by remember { mutableStateOf(false) }
        var selectedTimer by remember { mutableStateOf(timerOptions.last()) }
        var elapsedSeconds by remember { mutableStateOf(0L) }
        var showTimerMenu by remember { mutableStateOf(false) }

        val pulseAnim = rememberInfiniteTransition(label = "pulse")
        val pulseScale by pulseAnim.animateFloat(
            initialValue = 1f,
            targetValue = 1.08f,
            animationSpec = infiniteRepeatable(
                animation = tween(1000),
                repeatMode = RepeatMode.Reverse
            ),
            label = "pulseScale"
        )

        LaunchedEffect(isEnabled) {
            if (isEnabled) {
                elapsedSeconds = 0
                while (isEnabled) {
                    delay(1000)
                    elapsedSeconds++
                    if (selectedTimer.minutes > 0 && elapsedSeconds >= selectedTimer.minutes * 60L) {
                        isEnabled = false
                        try { ScreenKeepAwake.disable() } catch (_: Exception) {}
                    }
                }
            }
        }

        Scaffold(
            topBar = {
                TopAppBar(
                    title = { Text("eGuard") },
                    actions = {
                        IconButton(onClick = { showTimerMenu = true }, enabled = !isEnabled) {
                            Icon(Icons.Default.Timer, contentDescription = "Timer")
                        }
                        DropdownMenu(expanded = showTimerMenu, onDismissRequest = { showTimerMenu = false }) {
                            timerOptions.forEach { option ->
                                DropdownMenuItem(
                                    text = { Text(option.label) },
                                    onClick = { selectedTimer = option; showTimerMenu = false },
                                    leadingIcon = {
                                        if (selectedTimer == option) {
                                            Icon(Icons.Default.Check, contentDescription = null, modifier = Modifier.size(18.dp))
                                        }
                                    }
                                )
                            }
                        }
                    }
                )
            }
        ) { padding ->
            Column(
                modifier = Modifier.fillMaxSize().padding(padding),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.Center
            ) {
                Box(
                    modifier = Modifier
                        .size(200.dp)
                        .scale(if (isEnabled) pulseScale else 1f)
                        .clip(CircleShape)
                        .background(
                            if (isEnabled) MaterialTheme.colorScheme.primary
                            else MaterialTheme.colorScheme.surfaceVariant
                        ),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(
                        if (isEnabled) Icons.Default.Visibility else Icons.Default.VisibilityOff,
                        contentDescription = null,
                        modifier = Modifier.size(80.dp),
                        tint = if (isEnabled) MaterialTheme.colorScheme.onPrimary
                        else MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }

                Spacer(Modifier.height(32.dp))

                Text(
                    if (isEnabled) "Screen Guard Active" else "Screen Guard Off",
                    style = MaterialTheme.typography.headlineSmall,
                    color = if (isEnabled) MaterialTheme.colorScheme.primary
                    else MaterialTheme.colorScheme.onSurfaceVariant
                )

                Spacer(Modifier.height(8.dp))

                if (isEnabled) {
                    Text(
                        formatDuration(elapsedSeconds),
                        style = MaterialTheme.typography.displaySmall.copy(fontSize = 36.sp),
                        color = MaterialTheme.colorScheme.primary
                    )
                    Spacer(Modifier.height(4.dp))
                    Text(
                        if (selectedTimer.minutes > 0) {
                            val remaining = (selectedTimer.minutes * 60L) - elapsedSeconds
                            "${formatDuration(remaining)} remaining"
                        } else {
                            "Running indefinitely"
                        },
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                } else {
                    Text(
                        "Keep your screen awake",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }

                Spacer(Modifier.height(8.dp))

                Card(
                    modifier = Modifier.padding(horizontal = 48.dp),
                    colors = CardDefaults.cardColors(
                        containerColor = MaterialTheme.colorScheme.surfaceVariant
                    )
                ) {
                    Row(
                        modifier = Modifier.padding(12.dp).fillMaxWidth(),
                        horizontalArrangement = Arrangement.Center,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(Icons.Default.Timer, contentDescription = null, modifier = Modifier.size(16.dp))
                        Spacer(Modifier.width(8.dp))
                        Text("Duration: ${selectedTimer.label}", style = MaterialTheme.typography.bodySmall)
                    }
                }

                Spacer(Modifier.height(32.dp))

                Switch(
                    checked = isEnabled,
                    onCheckedChange = { enabled ->
                        isEnabled = enabled
                        try {
                            if (enabled) ScreenKeepAwake.enable()
                            else ScreenKeepAwake.disable()
                        } catch (_: Exception) {}
                    },
                    modifier = Modifier.size(width = 64.dp, height = 36.dp)
                )

                Spacer(Modifier.height(8.dp))

                Text(
                    if (isEnabled) "Tap to disable" else "Tap to enable",
                    style = MaterialTheme.typography.labelMedium,
                    color = MaterialTheme.colorScheme.outline
                )

                Spacer(Modifier.height(32.dp))

                Card(
                    modifier = Modifier.fillMaxWidth().padding(horizontal = 32.dp),
                    colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
                ) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Text("How it works", style = MaterialTheme.typography.titleSmall)
                        Spacer(Modifier.height(8.dp))
                        InfoRow(Icons.Default.Visibility, "Prevents screen from turning off")
                        InfoRow(Icons.Default.Timer, "Auto-stops after selected duration")
                        InfoRow(Icons.Default.BatteryAlert, "Uses more battery while active")
                    }
                }
            }
        }
    }
}

@Composable
private fun InfoRow(icon: androidx.compose.ui.graphics.vector.ImageVector, text: String) {
    Row(
        modifier = Modifier.padding(vertical = 4.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Icon(icon, contentDescription = null, modifier = Modifier.size(16.dp), tint = MaterialTheme.colorScheme.onSurfaceVariant)
        Spacer(Modifier.width(8.dp))
        Text(text, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
    }
}

private fun formatDuration(totalSeconds: Long): String {
    val h = totalSeconds / 3600
    val m = (totalSeconds % 3600) / 60
    val s = totalSeconds % 60
    return if (h > 0) "%d:%02d:%02d".format(h, m, s) else "%02d:%02d".format(m, s)
}
