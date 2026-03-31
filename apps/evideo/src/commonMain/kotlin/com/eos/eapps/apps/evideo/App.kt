package com.eos.eapps.apps.evideo

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp

@Composable
fun AppContent() {
    var isPlaying by remember { mutableStateOf(false) }
    var progress by remember { mutableStateOf(0.25f) }
    var speed by remember { mutableStateOf(1.0f) }

    Column(modifier = Modifier.fillMaxSize().padding(16.dp)) {
        Text("🎬 eVideo", style = MaterialTheme.typography.headlineMedium, modifier = Modifier.align(Alignment.CenterHorizontally))
        Spacer(Modifier.height(8.dp))
        Box(modifier = Modifier.fillMaxWidth().aspectRatio(16f / 9f).background(Color.Black), contentAlignment = Alignment.Center) {
            Text("🎬", style = MaterialTheme.typography.displayLarge, color = Color.White)
            if (!isPlaying) Button(onClick = { isPlaying = true }, modifier = Modifier.align(Alignment.Center)) { Text("▶ Play") }
        }
        Spacer(Modifier.height(8.dp))
        Slider(value = progress, onValueChange = { progress = it }, modifier = Modifier.fillMaxWidth())
        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
            Text("05:23", style = MaterialTheme.typography.bodySmall); Text("21:45", style = MaterialTheme.typography.bodySmall)
        }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.align(Alignment.CenterHorizontally)) {
            IconButton(onClick = { progress = (progress - 0.05f).coerceAtLeast(0f) }) { Text("⏪") }
            Button(onClick = { isPlaying = !isPlaying }) { Text(if (isPlaying) "⏸" else "▶️") }
            IconButton(onClick = { progress = (progress + 0.05f).coerceAtMost(1f) }) { Text("⏩") }
        }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.align(Alignment.CenterHorizontally)) {
            listOf(0.5f, 1.0f, 1.5f, 2.0f).forEach { s ->
                FilterChip(selected = speed == s, onClick = { speed = s }, label = { Text("${s}x") })
            }
        }
    }
}
