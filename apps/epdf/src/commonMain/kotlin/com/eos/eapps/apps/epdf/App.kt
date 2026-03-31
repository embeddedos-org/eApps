package com.eos.eapps.apps.epdf

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
    var currentPage by remember { mutableStateOf(1) }
    val totalPages = 10
    Column(modifier = Modifier.fillMaxSize().padding(16.dp)) {
        Text("📄 ePDF", style = MaterialTheme.typography.headlineMedium, modifier = Modifier.align(Alignment.CenterHorizontally))
        Spacer(Modifier.height(8.dp))
        Box(modifier = Modifier.fillMaxWidth().weight(1f).background(Color(0xFFFAFAFA)), contentAlignment = Alignment.Center) {
            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                Text("📄", style = MaterialTheme.typography.displayLarge)
                Text("Page $currentPage of $totalPages", style = MaterialTheme.typography.titleMedium)
                Text("Select a PDF file to view", style = MaterialTheme.typography.bodyMedium)
            }
        }
        Row(modifier = Modifier.fillMaxWidth().padding(8.dp), horizontalArrangement = Arrangement.Center, verticalAlignment = Alignment.CenterVertically) {
            Button(onClick = { if (currentPage > 1) currentPage-- }, enabled = currentPage > 1) { Text("◀") }
            Text("  $currentPage / $totalPages  ", style = MaterialTheme.typography.bodyLarge)
            Button(onClick = { if (currentPage < totalPages) currentPage++ }, enabled = currentPage < totalPages) { Text("▶") }
        }
        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.Center) {
            Button(onClick = {}) { Text("Open PDF") }
        }
    }
}
