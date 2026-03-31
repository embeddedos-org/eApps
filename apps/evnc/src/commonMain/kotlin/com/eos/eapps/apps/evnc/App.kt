package com.eos.eapps.apps.evnc

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
    var host by remember { mutableStateOf("") }
    var port by remember { mutableStateOf("5900") }
    var connected by remember { mutableStateOf(false) }

    Column(modifier = Modifier.fillMaxSize().padding(16.dp)) {
        Text("🖥️ eVNC", style = MaterialTheme.typography.headlineMedium, modifier = Modifier.align(Alignment.CenterHorizontally))
        if (!connected) {
            Card(modifier = Modifier.fillMaxWidth()) {
                Column(modifier = Modifier.padding(16.dp)) {
                    OutlinedTextField(value = host, onValueChange = { host = it }, label = { Text("Host") }, modifier = Modifier.fillMaxWidth(), singleLine = true)
                    OutlinedTextField(value = port, onValueChange = { port = it }, label = { Text("Port") }, modifier = Modifier.fillMaxWidth(), singleLine = true)
                    Spacer(Modifier.height(8.dp))
                    Button(onClick = { connected = true }, modifier = Modifier.fillMaxWidth()) { Text("Connect") }
                }
            }
        } else {
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                Text("VNC: $host:$port", style = MaterialTheme.typography.bodyMedium)
                TextButton(onClick = { connected = false }) { Text("Disconnect") }
            }
            Box(modifier = Modifier.fillMaxSize().background(Color(0xFF2B2B2B)), contentAlignment = Alignment.Center) {
                Text("🖥️ Remote Desktop View", color = Color.White, style = MaterialTheme.typography.titleLarge)
            }
        }
    }
}
