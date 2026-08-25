package com.eos.eapps.apps.eguard

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.eos.eapps.core.ui.theme.AppTheme

@Composable
fun App() {
    AppTheme {
        GuardScreen()
    }
}

@Composable
fun GuardScreen() {
    var guarding by remember { mutableStateOf(false) }
    var elapsedMs by remember { mutableStateOf(0L) }
    var intervalSec by remember { mutableStateOf(60) }

    LaunchedEffect(guarding) {
        if (guarding) {
            val start = System.currentTimeMillis() - elapsedMs
            while (guarding) {
                elapsedMs = System.currentTimeMillis() - start
                kotlinx.coroutines.delay(100)
            }
        }
    }

    val hours = (elapsedMs / 3_600_000) % 24
    val minutes = (elapsedMs / 60_000) % 60
    val seconds = (elapsedMs / 1_000) % 60

    Scaffold(
        topBar = { CenterAlignedTopAppBar(title = { Text("eGuard") }) }
    ) { padding ->
        Column(
            modifier = Modifier.fillMaxSize().padding(padding),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center,
        ) {
            Card(
                colors = CardDefaults.cardColors(
                    containerColor = if (guarding)
                        MaterialTheme.colorScheme.primaryContainer
                    else
                        MaterialTheme.colorScheme.surfaceVariant
                ),
                modifier = Modifier.padding(16.dp),
            ) {
                Column(
                    horizontalAlignment = Alignment.CenterHorizontally,
                    modifier = Modifier.padding(32.dp),
                ) {
                    Text(
                        text = if (guarding) "\uD83D\uDEE1\uFE0F" else "\uD83D\uDCA4",
                        fontSize = 48.sp,
                    )
                    Spacer(Modifier.height(8.dp))
                    Text(
                        text = if (guarding) "GUARDING" else "PAUSED",
                        style = MaterialTheme.typography.headlineMedium,
                        color = if (guarding)
                            MaterialTheme.colorScheme.primary
                        else
                            MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }
            }

            Spacer(Modifier.height(16.dp))

            Text(
                text = "%02d:%02d:%02d".format(hours, minutes, seconds),
                fontSize = 56.sp,
                style = MaterialTheme.typography.displayLarge,
            )
            Text(
                text = "Session uptime",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )

            Spacer(Modifier.height(32.dp))

            Button(
                onClick = {
                    guarding = !guarding
                    if (!guarding) elapsedMs = 0
                },
                colors = ButtonDefaults.buttonColors(
                    containerColor = if (guarding)
                        MaterialTheme.colorScheme.error
                    else
                        MaterialTheme.colorScheme.primary
                ),
            ) {
                Text(if (guarding) "\u23F9 Stop Guard" else "\u25B6\uFE0F Start Guard")
            }

            Spacer(Modifier.height(24.dp))

            Text("Jiggle Interval", style = MaterialTheme.typography.titleSmall)
            Spacer(Modifier.height(8.dp))
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                listOf(30 to "30s", 60 to "1m", 120 to "2m", 300 to "5m").forEach { (sec, label) ->
                    FilterChip(
                        selected = intervalSec == sec,
                        onClick = { intervalSec = sec },
                        label = { Text(label) },
                    )
                }
            }

            Spacer(Modifier.height(24.dp))

            Card(modifier = Modifier.padding(horizontal = 32.dp)) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("How it works", style = MaterialTheme.typography.titleSmall)
                    Spacer(Modifier.height(4.dp))
                    Text("\u2022 Prevents system sleep", style = MaterialTheme.typography.bodySmall)
                    Text("\u2022 Prevents screen lock (mouse jiggle)", style = MaterialTheme.typography.bodySmall)
                    Text("\u2022 Prevents idle timeout", style = MaterialTheme.typography.bodySmall)
                    Text("\u2022 Works on macOS, Windows & Linux", style = MaterialTheme.typography.bodySmall)
                }
            }
        }
    }
}
