package com.eos.eapps.apps.ezip

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

@Composable
fun AppContent() {
    var selectedTab by remember { mutableStateOf(0) }
    Column(modifier = Modifier.fillMaxSize().padding(16.dp), horizontalAlignment = Alignment.CenterHorizontally) {
        Text("🗜️ eZip", style = MaterialTheme.typography.headlineMedium)
        TabRow(selectedTabIndex = selectedTab) {
            Tab(selected = selectedTab == 0, onClick = { selectedTab = 0 }) { Text("Create", modifier = Modifier.padding(12.dp)) }
            Tab(selected = selectedTab == 1, onClick = { selectedTab = 1 }) { Text("Extract", modifier = Modifier.padding(12.dp)) }
        }
        Spacer(Modifier.height(16.dp))
        when (selectedTab) {
            0 -> Column(horizontalAlignment = Alignment.CenterHorizontally) {
                Text("📦", style = MaterialTheme.typography.displayLarge)
                Spacer(Modifier.height(8.dp))
                Text("Drag files here or tap to select", style = MaterialTheme.typography.bodyLarge)
                Spacer(Modifier.height(16.dp))
                Button(onClick = {}) { Text("Select Files") }
                Spacer(Modifier.height(8.dp))
                Button(onClick = {}) { Text("Create Archive") }
            }
            1 -> Column(horizontalAlignment = Alignment.CenterHorizontally) {
                Text("📂", style = MaterialTheme.typography.displayLarge)
                Spacer(Modifier.height(8.dp))
                Text("Select a ZIP file to extract", style = MaterialTheme.typography.bodyLarge)
                Spacer(Modifier.height(16.dp))
                Button(onClick = {}) { Text("Select Archive") }
                Spacer(Modifier.height(8.dp))
                Button(onClick = {}) { Text("Extract All") }
            }
        }
    }
}
