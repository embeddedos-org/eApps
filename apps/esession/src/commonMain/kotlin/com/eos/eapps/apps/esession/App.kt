package com.eos.eapps.apps.esession

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.eos.eapps.core.ui.theme.AppTheme

@Composable
fun App() {
    AppTheme {
        SessionManagerScreen()
    }
}

@Composable
fun SessionManagerScreen() {
    var sessions by remember { mutableStateOf(listOf("Local Terminal", "SSH: server1", "SSH: server2")) }
    var activeSession by remember { mutableStateOf(0) }
    var newSessionName by remember { mutableStateOf("") }

    Scaffold(
        topBar = { CenterAlignedTopAppBar(title = { Text("eSession Manager") }) }
    ) { padding ->
        Row(modifier = Modifier.fillMaxSize().padding(padding)) {
            // Session list sidebar
            Card(
                modifier = Modifier.width(250.dp).fillMaxHeight().padding(8.dp),
            ) {
                Column(modifier = Modifier.fillMaxSize().padding(8.dp)) {
                    Text("Sessions", style = MaterialTheme.typography.titleMedium)
                    Spacer(Modifier.height(8.dp))

                    sessions.forEachIndexed { index, name ->
                        val isActive = index == activeSession
                        Surface(
                            onClick = { activeSession = index },
                            color = if (isActive) MaterialTheme.colorScheme.primaryContainer else MaterialTheme.colorScheme.surface,
                            shape = MaterialTheme.shapes.small,
                            modifier = Modifier.fillMaxWidth().padding(vertical = 2.dp),
                        ) {
                            Row(
                                modifier = Modifier.padding(12.dp),
                                verticalAlignment = Alignment.CenterVertically,
                            ) {
                                Text(
                                    text = if (isActive) "▶ $name" else "  $name",
                                    style = MaterialTheme.typography.bodyMedium,
                                    modifier = Modifier.weight(1f),
                                )
                                IconButton(
                                    onClick = {
                                        sessions = sessions.toMutableList().also { it.removeAt(index) }
                                        if (activeSession >= sessions.size - 1) activeSession = maxOf(0, sessions.size - 2)
                                    },
                                    modifier = Modifier.size(24.dp),
                                ) { Text("✕", style = MaterialTheme.typography.labelSmall) }
                            }
                        }
                    }

                    Spacer(Modifier.height(16.dp))
                    HorizontalDivider()
                    Spacer(Modifier.height(8.dp))

                    OutlinedTextField(
                        value = newSessionName,
                        onValueChange = { newSessionName = it },
                        label = { Text("New session") },
                        singleLine = true,
                        modifier = Modifier.fillMaxWidth(),
                    )
                    Spacer(Modifier.height(4.dp))
                    Row(horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                        Button(
                            onClick = {
                                if (newSessionName.isNotBlank()) {
                                    sessions = sessions + newSessionName
                                    activeSession = sessions.size
                                    newSessionName = ""
                                }
                            },
                            modifier = Modifier.weight(1f),
                        ) { Text("Add") }
                        OutlinedButton(
                            onClick = {
                                sessions = sessions + "SSH: ${newSessionName.ifBlank { "new-host" }}"
                                activeSession = sessions.size
                                newSessionName = ""
                            },
                            modifier = Modifier.weight(1f),
                        ) { Text("SSH") }
                    }
                }
            }

            // Terminal area
            Card(
                modifier = Modifier.weight(1f).fillMaxHeight().padding(8.dp),
            ) {
                Column(modifier = Modifier.fillMaxSize().padding(16.dp)) {
                    if (sessions.isNotEmpty() && activeSession < sessions.size) {
                        Text(
                            text = sessions[activeSession],
                            style = MaterialTheme.typography.titleMedium,
                        )
                        Spacer(Modifier.height(8.dp))
                        Text(
                            text = "$ ",
                            style = MaterialTheme.typography.bodyMedium,
                            color = MaterialTheme.colorScheme.primary,
                        )
                    } else {
                        Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                            Text("No active session", style = MaterialTheme.typography.bodyLarge)
                        }
                    }
                }
            }
        }
    }
}
