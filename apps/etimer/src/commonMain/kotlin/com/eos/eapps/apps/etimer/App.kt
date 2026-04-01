package com.eos.eapps.apps.etimer

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
        TimerScreen()
    }
}

@Composable
fun TimerScreen() {
    var elapsedMs by remember { mutableStateOf(0L) }
    var running by remember { mutableStateOf(false) }
    var mode by remember { mutableStateOf("stopwatch") } // stopwatch or timer
    var timerTargetMs by remember { mutableStateOf(60_000L) } // 1 minute default

    LaunchedEffect(running) {
        if (running) {
            val start = System.currentTimeMillis() - elapsedMs
            while (running) {
                elapsedMs = System.currentTimeMillis() - start
                kotlinx.coroutines.delay(10)
                if (mode == "timer" && elapsedMs >= timerTargetMs) {
                    running = false
                }
            }
        }
    }

    val displayMs = if (mode == "timer") maxOf(0, timerTargetMs - elapsedMs) else elapsedMs
    val minutes = (displayMs / 60_000) % 60
    val seconds = (displayMs / 1_000) % 60
    val centis = (displayMs / 10) % 100

    Scaffold(
        topBar = { CenterAlignedTopAppBar(title = { Text("eTimer") }) }
    ) { padding ->
        Column(
            modifier = Modifier.fillMaxSize().padding(padding),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center,
        ) {
            // Mode toggle
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                FilterChip(selected = mode == "stopwatch", onClick = { mode = "stopwatch"; elapsedMs = 0; running = false }, label = { Text("Stopwatch") })
                FilterChip(selected = mode == "timer", onClick = { mode = "timer"; elapsedMs = 0; running = false }, label = { Text("Timer") })
            }

            Spacer(Modifier.height(48.dp))

            // Time display
            Text(
                text = "%02d:%02d.%02d".format(minutes, seconds, centis),
                fontSize = 64.sp,
                style = MaterialTheme.typography.displayLarge,
            )

            Spacer(Modifier.height(32.dp))

            // Controls
            Row(horizontalArrangement = Arrangement.spacedBy(16.dp)) {
                Button(onClick = { running = !running }) {
                    Text(if (running) "Pause" else "Start")
                }
                OutlinedButton(onClick = { running = false; elapsedMs = 0 }) {
                    Text("Reset")
                }
            }

            if (mode == "timer") {
                Spacer(Modifier.height(24.dp))
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    listOf(30_000L to "30s", 60_000L to "1m", 180_000L to "3m", 300_000L to "5m", 600_000L to "10m").forEach { (ms, label) ->
                        AssistChip(onClick = { timerTargetMs = ms; elapsedMs = 0; running = false }, label = { Text(label) })
                    }
                }
            }
        }
    }
}
