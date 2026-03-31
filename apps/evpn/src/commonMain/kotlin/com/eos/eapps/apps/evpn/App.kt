package com.eos.eapps.apps.evpn

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

@Composable
fun AppContent() {
    var connected by remember { mutableStateOf(false) }
    var selectedServer by remember { mutableStateOf(0) }
    val servers = listOf("US East" to "us-east.vpn", "US West" to "us-west.vpn", "Europe" to "eu.vpn", "Asia" to "asia.vpn")

    Column(modifier = Modifier.fillMaxSize().padding(16.dp), horizontalAlignment = Alignment.CenterHorizontally) {
        Text("🌐 eVPN", style = MaterialTheme.typography.headlineMedium)
        Spacer(Modifier.height(16.dp))
        Text(if (connected) "🟢 Connected" else "🔴 Disconnected", style = MaterialTheme.typography.headlineSmall)
        if (connected) Text("Server: ${servers[selectedServer].first}", style = MaterialTheme.typography.bodyMedium)
        Spacer(Modifier.height(16.dp))
        Text("Select Server:", style = MaterialTheme.typography.titleMedium)
        servers.forEachIndexed { i, (name, addr) ->
            ListItem(
                headlineContent = { Text(name) },
                supportingContent = { Text(addr) },
                leadingContent = { RadioButton(selected = selectedServer == i, onClick = { selectedServer = i }) },
            )
        }
        Spacer(Modifier.height(16.dp))
        Button(onClick = { connected = !connected }, modifier = Modifier.fillMaxWidth()) {
            Text(if (connected) "Disconnect" else "Connect")
        }
    }
}
