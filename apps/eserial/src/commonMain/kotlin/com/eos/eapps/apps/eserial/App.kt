package com.eos.eapps.apps.eserial

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
    var port by remember { mutableStateOf("COM1") }
    var baud by remember { mutableStateOf("115200") }
    var connected by remember { mutableStateOf(false) }
    var log by remember { mutableStateOf("") }

    Column(modifier = Modifier.fillMaxSize().padding(16.dp)) {
        Text("🔌 eSerial", style = MaterialTheme.typography.headlineMedium, modifier = Modifier.align(Alignment.CenterHorizontally))
        if (!connected) {
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                OutlinedTextField(value = port, onValueChange = { port = it }, label = { Text("Port") }, modifier = Modifier.weight(1f), singleLine = true)
                OutlinedTextField(value = baud, onValueChange = { baud = it }, label = { Text("Baud Rate") }, modifier = Modifier.weight(1f), singleLine = true)
            }
            Spacer(Modifier.height(8.dp))
            Button(onClick = { connected = true; log = "Opened $port at $baud baud\n" }, modifier = Modifier.fillMaxWidth()) { Text("Open Port") }
        } else {
            Row(horizontalArrangement = Arrangement.SpaceBetween, modifier = Modifier.fillMaxWidth()) {
                Text("$port @ $baud", style = MaterialTheme.typography.bodyMedium)
                TextButton(onClick = { connected = false }) { Text("Close") }
            }
            Box(modifier = Modifier.fillMaxSize().background(Color.Black).padding(8.dp)) {
                Text(log, color = Color.Green, style = MaterialTheme.typography.bodySmall)
            }
        }
    }
}
