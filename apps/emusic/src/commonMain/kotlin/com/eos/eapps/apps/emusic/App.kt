package com.eos.eapps.apps.emusic

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

data class Track(val title: String, val artist: String, val duration: String)

val DEMO_TRACKS = listOf(
    Track("Sunrise Melody", "eArtist", "3:45"), Track("Ocean Waves", "Ambient", "4:12"),
    Track("City Lights", "Electronic", "3:30"), Track("Mountain Echo", "Folk", "5:01"),
    Track("Midnight Jazz", "Jazz Trio", "4:33"), Track("Summer Breeze", "Pop", "3:15"),
)

@Composable
fun AppContent() {
    var currentTrack by remember { mutableStateOf(0) }
    var isPlaying by remember { mutableStateOf(false) }
    var progress by remember { mutableStateOf(0.3f) }

    Column(modifier = Modifier.fillMaxSize().padding(16.dp)) {
        Text("🎵 eMusic", style = MaterialTheme.typography.headlineMedium, modifier = Modifier.align(Alignment.CenterHorizontally))
        Spacer(Modifier.height(8.dp))
        Card(modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(16.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                Text("🎵", style = MaterialTheme.typography.displayMedium)
                Text(DEMO_TRACKS[currentTrack].title, style = MaterialTheme.typography.titleLarge)
                Text(DEMO_TRACKS[currentTrack].artist, style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
                Spacer(Modifier.height(8.dp))
                Slider(value = progress, onValueChange = { progress = it }, modifier = Modifier.fillMaxWidth())
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    Text("1:07", style = MaterialTheme.typography.bodySmall)
                    Text(DEMO_TRACKS[currentTrack].duration, style = MaterialTheme.typography.bodySmall)
                }
                Row(horizontalArrangement = Arrangement.spacedBy(16.dp), verticalAlignment = Alignment.CenterVertically) {
                    IconButton(onClick = { currentTrack = (currentTrack - 1 + DEMO_TRACKS.size) % DEMO_TRACKS.size }) { Text("⏮", style = MaterialTheme.typography.headlineSmall) }
                    Button(onClick = { isPlaying = !isPlaying }) { Text(if (isPlaying) "⏸" else "▶️") }
                    IconButton(onClick = { currentTrack = (currentTrack + 1) % DEMO_TRACKS.size }) { Text("⏭", style = MaterialTheme.typography.headlineSmall) }
                }
            }
        }
        Spacer(Modifier.height(8.dp))
        Text("Playlist", style = MaterialTheme.typography.titleMedium)
        LazyColumn {
            itemsIndexed(DEMO_TRACKS) { i, track ->
                ListItem(
                    headlineContent = { Text(track.title) },
                    supportingContent = { Text(track.artist) },
                    trailingContent = { Text(track.duration) },
                    leadingContent = { Text(if (i == currentTrack) "🔊" else "🎵") },
                    modifier = Modifier.fillMaxWidth(),
                )
            }
        }
    }
}
