package com.eos.eapps.apps.etunnel

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

@Composable
fun AppContent() {
    var localPort by remember { mutableStateOf("8080") }
    var remoteHost by remember { mutableStateOf("") }
    var remotePort by remember { mutableStateOf("80") }
    var active by remember { mutableStateOf(false) }

    Column(modifier = Modifier.fillMaxSize().padding(16.dp), horizontalAlignment = Alignment.CenterHorizontally) {
        Text("🚇 eTunnel", style = MaterialTheme.typography.headlineMedium)
        Spacer(Modifier.height(16.dp))
        Card(modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("SSH Port Forwarding", style = MaterialTheme.typography.titleMedium)
                Spacer(Modifier.height(8.dp))
                OutlinedTextField(value = localPort, onValueChange = { localPort = it }, label = { Text("Local Port") }, modifier = Modifier.fillMaxWidth(), singleLine = true)
                OutlinedTextField(value = remoteHost, onValueChange = { remoteHost = it }, label = { Text("Remote Host") }, modifier = Modifier.fillMaxWidth(), singleLine = true)
                OutlinedTextField(value = remotePort, onValueChange = { remotePort = it }, label = { Text("Remote Port") }, modifier = Modifier.fillMaxWidth(), singleLine = true)
                Spacer(Modifier.height(8.dp))
                Button(onClick = { active = !active }, modifier = Modifier.fillMaxWidth()) {
                    Text(if (active) "Stop Tunnel" else "Start Tunnel")
                }
            }
        }
        if (active) {
            Spacer(Modifier.height(8.dp))
            Text("🟢 Tunnel active: localhost:$localPort → $remoteHost:$remotePort", style = MaterialTheme.typography.bodyMedium)
        }
    }
}
package com.eos.eapps.apps.etunnel

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.eos.eapps.core.ui.components.AppButton
import com.eos.eapps.core.ui.components.AppButtonType
import com.eos.eapps.core.ui.components.AppCard
import com.eos.eapps.core.ui.components.AppScaffold
import com.eos.eapps.core.ui.theme.AppTheme

private data class Tunnel(
    val id: Int,
    val type: String,
    val localPort: Int,
    val remoteHost: String,
    val remotePort: Int,
    val active: Boolean
)

private data class SshConfig(
    val host: String = "192.168.1.100",
    val port: String = "22",
    val username: String = "admin",
    val password: String = ""
)

private val tunnelTypes = listOf("Local", "Remote", "Dynamic")

@Composable
fun App() {
    AppTheme {
        val tunnels = remember { mutableStateListOf(
            Tunnel(1, "Local", 8080, "localhost", 80, true),
            Tunnel(2, "Remote", 3306, "db.internal", 3306, false),
            Tunnel(3, "Dynamic", 1080, "—", 0, true),
        ) }
        var showAddDialog by remember { mutableStateOf(false) }
        var showSshConfig by remember { mutableStateOf(false) }
        var sshConfig by remember { mutableStateOf(SshConfig()) }
        var nextId by remember { mutableIntStateOf(4) }

        AppScaffold(
            title = "eTunnel",
            actions = {
                IconButton(onClick = { showSshConfig = true }) { Icon(Icons.Default.Settings, "SSH Config") }
            },
            floatingActionButton = {
                FloatingActionButton(onClick = { showAddDialog = true }) {
                    Icon(Icons.Default.Add, "Add Tunnel")
                }
            }
        ) { padding ->
            Column(Modifier.padding(padding).fillMaxSize()) {
                Surface(tonalElevation = 2.dp, modifier = Modifier.fillMaxWidth()) {
                    Row(Modifier.padding(16.dp), verticalAlignment = Alignment.CenterVertically) {
                        Box(Modifier.size(12.dp).clip(CircleShape).background(MaterialTheme.colorScheme.primary))
                        Spacer(Modifier.width(8.dp))
                        Text("SSH: ${sshConfig.username}@${sshConfig.host}:${sshConfig.port}", style = MaterialTheme.typography.bodyMedium)
                        Spacer(Modifier.weight(1f))
                        Text("${tunnels.count { it.active }} active", style = MaterialTheme.typography.labelMedium, color = MaterialTheme.colorScheme.primary)
                    }
                }

                if (tunnels.isEmpty()) {
                    Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                        Column(horizontalAlignment = Alignment.CenterHorizontally) {
                            Icon(Icons.Default.Lock, null, Modifier.size(64.dp), tint = MaterialTheme.colorScheme.onSurfaceVariant)
                            Spacer(Modifier.height(8.dp))
                            Text("No tunnels configured")
                            Spacer(Modifier.height(16.dp))
                            AppButton(text = "Add Tunnel", onClick = { showAddDialog = true })
                        }
                    }
                } else {
                    LazyColumn(Modifier.fillMaxSize()) {
                        item {
                            Text("Active Tunnels", style = MaterialTheme.typography.titleSmall, modifier = Modifier.padding(16.dp, 12.dp, 16.dp, 4.dp))
                        }
                        items(tunnels.toList()) { tunnel ->
                            AppCard {
                                Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
                                    Surface(
                                        shape = MaterialTheme.shapes.small,
                                        color = when (tunnel.type) {
                                            "Local" -> MaterialTheme.colorScheme.primaryContainer
                                            "Remote" -> MaterialTheme.colorScheme.secondaryContainer
                                            else -> MaterialTheme.colorScheme.tertiaryContainer
                                        },
                                        modifier = Modifier.size(48.dp)
                                    ) {
                                        Box(contentAlignment = Alignment.Center) {
                                            Text(tunnel.type.first().toString(), fontWeight = FontWeight.Bold, style = MaterialTheme.typography.titleMedium)
                                        }
                                    }
                                    Spacer(Modifier.width(12.dp))
                                    Column(Modifier.weight(1f)) {
                                        Text("${tunnel.type} Forward", fontWeight = FontWeight.Bold)
                                        if (tunnel.type == "Dynamic") {
                                            Text("SOCKS5 proxy on port ${tunnel.localPort}", style = MaterialTheme.typography.bodySmall)
                                        } else {
                                            Text("localhost:${tunnel.localPort} → ${tunnel.remoteHost}:${tunnel.remotePort}", style = MaterialTheme.typography.bodySmall)
                                        }
                                    }
                                    Switch(
                                        checked = tunnel.active,
                                        onCheckedChange = { checked ->
                                            val idx = tunnels.indexOf(tunnel)
                                            if (idx >= 0) tunnels[idx] = tunnel.copy(active = checked)
                                        }
                                    )
                                    IconButton(onClick = { tunnels.remove(tunnel) }) {
                                        Icon(Icons.Default.Delete, "Delete")
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

        if (showAddDialog) {
            var type by remember { mutableStateOf("Local") }
            var localPort by remember { mutableStateOf("8080") }
            var remoteHost by remember { mutableStateOf("localhost") }
            var remotePort by remember { mutableStateOf("80") }
            var typeExpanded by remember { mutableStateOf(false) }

            AlertDialog(
                onDismissRequest = { showAddDialog = false },
                title = { Text("Add Tunnel") },
                text = {
                    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        Box {
                            OutlinedTextField(value = type, onValueChange = {}, readOnly = true, label = { Text("Type") }, modifier = Modifier.fillMaxWidth(), trailingIcon = { IconButton(onClick = { typeExpanded = true }) { Icon(Icons.Default.ArrowDropDown, null) } })
                            DropdownMenu(expanded = typeExpanded, onDismissRequest = { typeExpanded = false }) {
                                tunnelTypes.forEach { t -> DropdownMenuItem(text = { Text(t) }, onClick = { type = t; typeExpanded = false }) }
                            }
                        }
                        OutlinedTextField(value = localPort, onValueChange = { localPort = it }, label = { Text("Local Port") }, singleLine = true, modifier = Modifier.fillMaxWidth())
                        if (type != "Dynamic") {
                            OutlinedTextField(value = remoteHost, onValueChange = { remoteHost = it }, label = { Text("Remote Host") }, singleLine = true, modifier = Modifier.fillMaxWidth())
                            OutlinedTextField(value = remotePort, onValueChange = { remotePort = it }, label = { Text("Remote Port") }, singleLine = true, modifier = Modifier.fillMaxWidth())
                        }
                    }
                },
                confirmButton = {
                    TextButton(onClick = {
                        tunnels.add(Tunnel(nextId++, type, localPort.toIntOrNull() ?: 8080, if (type == "Dynamic") "—" else remoteHost, if (type == "Dynamic") 0 else (remotePort.toIntOrNull() ?: 80), true))
                        showAddDialog = false
                    }) { Text("Add") }
                },
                dismissButton = { TextButton(onClick = { showAddDialog = false }) { Text("Cancel") } }
            )
        }

        if (showSshConfig) {
            var h by remember { mutableStateOf(sshConfig.host) }
            var p by remember { mutableStateOf(sshConfig.port) }
            var u by remember { mutableStateOf(sshConfig.username) }
            var pw by remember { mutableStateOf(sshConfig.password) }

            AlertDialog(
                onDismissRequest = { showSshConfig = false },
                title = { Text("SSH Configuration") },
                text = {
                    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        OutlinedTextField(value = h, onValueChange = { h = it }, label = { Text("Host") }, singleLine = true, modifier = Modifier.fillMaxWidth())
                        OutlinedTextField(value = p, onValueChange = { p = it }, label = { Text("Port") }, singleLine = true, modifier = Modifier.fillMaxWidth())
                        OutlinedTextField(value = u, onValueChange = { u = it }, label = { Text("Username") }, singleLine = true, modifier = Modifier.fillMaxWidth())
                        OutlinedTextField(value = pw, onValueChange = { pw = it }, label = { Text("Password") }, singleLine = true, modifier = Modifier.fillMaxWidth())
                    }
                },
                confirmButton = {
                    TextButton(onClick = { sshConfig = SshConfig(h, p, u, pw); showSshConfig = false }) { Text("Save") }
                },
                dismissButton = { TextButton(onClick = { showSshConfig = false }) { Text("Cancel") } }
            )
        }
    }
}
