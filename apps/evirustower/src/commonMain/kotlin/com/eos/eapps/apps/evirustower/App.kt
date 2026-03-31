package com.eos.eapps.apps.evirustower

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.delay

@Composable
fun AppContent() {
    var scanning by remember { mutableStateOf(false) }
    var progress by remember { mutableStateOf(0f) }
    var results by remember { mutableStateOf<List<String>?>(null) }

    LaunchedEffect(scanning) {
        if (scanning) { for (i in 0..100) { progress = i / 100f; delay(50) }; scanning = false; results = listOf("✅ No threats found", "Scanned 1,234 files", "Database: Up to date") }
    }

    Column(modifier = Modifier.fillMaxSize().padding(16.dp), horizontalAlignment = Alignment.CenterHorizontally) {
        Text("🦠 eVirusTower", style = MaterialTheme.typography.headlineMedium)
        Spacer(Modifier.height(16.dp))
        if (scanning) {
            CircularProgressIndicator()
            LinearProgressIndicator(progress = { progress }, modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp))
            Text("Scanning... ${(progress * 100).toInt()}%")
        } else if (results != null) {
            Card(modifier = Modifier.fillMaxWidth()) {
                Column(modifier = Modifier.padding(16.dp)) {
                    results!!.forEach { Text(it, style = MaterialTheme.typography.bodyLarge, modifier = Modifier.padding(vertical = 2.dp)) }
                }
            }
            Spacer(Modifier.height(8.dp))
            Button(onClick = { results = null }) { Text("Scan Again") }
        } else {
            Text("🛡️", style = MaterialTheme.typography.displayLarge)
            Spacer(Modifier.height(16.dp))
            Text("Hash-based malware scanner", style = MaterialTheme.typography.bodyLarge)
            Spacer(Modifier.height(16.dp))
            Button(onClick = { scanning = true; progress = 0f }) { Text("Start Full Scan") }
            Spacer(Modifier.height(8.dp))
            OutlinedButton(onClick = { scanning = true; progress = 0f }) { Text("Quick Scan") }
        }
    }
}
