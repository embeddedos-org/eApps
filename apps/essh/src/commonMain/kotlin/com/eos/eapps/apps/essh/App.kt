package com.eos.eapps.apps.essh

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
    var port by remember { mutableStateOf("22") }
    var user by remember { mutableStateOf("") }
    var connected by remember { mutableStateOf(false) }
    var terminal by remember { mutableStateOf("$ ") }

    Column(modifier = Modifier.fillMaxSize().padding(16.dp)) {
        Text("🔒 eSSH", style = MaterialTheme.typography.headlineMedium, modifier = Modifier.align(Alignment.CenterHorizontally))
        if (!connected) {
            Card(modifier = Modifier.fillMaxWidth()) {
                Column(modifier = Modifier.padding(16.dp)) {
                    OutlinedTextField(value = host, onValueChange = { host = it }, label = { Text("Host") }, modifier = Modifier.fillMaxWidth(), singleLine = true)
                    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        OutlinedTextField(value = port, onValueChange = { port = it }, label = { Text("Port") }, modifier = Modifier.weight(0.3f), singleLine = true)
                        OutlinedTextField(value = user, onValueChange = { user = it }, label = { Text("User") }, modifier = Modifier.weight(0.7f), singleLine = true)
                    }
                    Spacer(Modifier.height(8.dp))
                    Button(onClick = { connected = true; terminal = "Connected to $user@$host:$port\n$ " }, modifier = Modifier.fillMaxWidth()) { Text("Connect") }
                }
            }
        } else {
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                Text("$user@$host", style = MaterialTheme.typography.bodyMedium)
                TextButton(onClick = { connected = false }) { Text("Disconnect") }
            }
            Box(modifier = Modifier.fillMaxSize().background(Color.Black).padding(8.dp)) {
                Text(terminal, color = Color.Green, style = MaterialTheme.typography.bodySmall)
            }
        }
    }
}
