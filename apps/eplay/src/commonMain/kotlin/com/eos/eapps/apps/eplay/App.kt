package com.eos.eapps.apps.eplay

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

@Composable
fun AppContent() {
    var playlist by remember { mutableStateOf(listOf("Track 1 - Artist A", "Track 2 - Artist B", "Track 3 - Artist C")) }
    var currentIdx by remember { mutableStateOf(0) }
    var playing by remember { mutableStateOf(false) }

    Column(modifier = Modifier.fillMaxSize().padding(16.dp), horizontalAlignment = Alignment.CenterHorizontally) {
        Text("▶️ ePlay", style = MaterialTheme.typography.headlineMedium)
        Spacer(Modifier.height(8.dp))
        Card(modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(16.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                Text(if (playlist.isNotEmpty()) playlist[currentIdx] else "No media", style = MaterialTheme.typography.titleMedium)
                Spacer(Modifier.height(8.dp))
                Slider(value = 0.4f, onValueChange = {}, modifier = Modifier.fillMaxWidth())
                Row(horizontalArrangement = Arrangement.spacedBy(16.dp)) {
                    IconButton(onClick = { if (currentIdx > 0) currentIdx-- }) { Text("⏮") }
                    Button(onClick = { playing = !playing }) { Text(if (playing) "⏸" else "▶") }
                    IconButton(onClick = { if (currentIdx < playlist.size - 1) currentIdx++ }) { Text("⏭") }
                }
            }
        }
        Spacer(Modifier.height(8.dp))
        Text("Playlist", style = MaterialTheme.typography.titleMedium)
        LazyColumn {
            itemsIndexed(playlist) { i, item ->
                ListItem(
                    headlineContent = { Text(item) },
                    leadingContent = { Text(if (i == currentIdx) "🔊" else "🎵") },
                )
            }
        }
    }
}
