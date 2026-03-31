package com.eos.eapps.apps.eftp

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

@Composable
fun AppContent() {
    var host by remember { mutableStateOf("") }
    var port by remember { mutableStateOf("22") }
    var user by remember { mutableStateOf("") }
    var connected by remember { mutableStateOf(false) }

    Column(modifier = Modifier.fillMaxSize().padding(16.dp)) {
        Text("📂 eFTP", style = MaterialTheme.typography.headlineMedium, modifier = Modifier.align(Alignment.CenterHorizontally))
        Spacer(Modifier.height(16.dp))
        if (!connected) {
            Card(modifier = Modifier.fillMaxWidth()) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("Connect to Server", style = MaterialTheme.typography.titleMedium)
                    Spacer(Modifier.height(8.dp))
                    OutlinedTextField(value = host, onValueChange = { host = it }, label = { Text("Host") }, modifier = Modifier.fillMaxWidth(), singleLine = true)
                    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        OutlinedTextField(value = port, onValueChange = { port = it }, label = { Text("Port") }, modifier = Modifier.weight(0.3f), singleLine = true)
                        OutlinedTextField(value = user, onValueChange = { user = it }, label = { Text("Username") }, modifier = Modifier.weight(0.7f), singleLine = true)
                    }
                    Spacer(Modifier.height(8.dp))
                    Button(onClick = { connected = true }, modifier = Modifier.fillMaxWidth()) { Text("Connect") }
                }
            }
        } else {
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                Text("Connected to $host", style = MaterialTheme.typography.bodyMedium)
                TextButton(onClick = { connected = false }) { Text("Disconnect") }
            }
            HorizontalDivider()
            Row(modifier = Modifier.fillMaxSize()) {
                Column(modifier = Modifier.weight(1f).padding(4.dp)) {
                    Text("Local", style = MaterialTheme.typography.titleSmall)
                    listOf("📁 Documents", "📁 Downloads", "📄 file.txt").forEach { Text(it, modifier = Modifier.padding(4.dp)) }
                }
                Column(modifier = Modifier.weight(1f).padding(4.dp)) {
                    Text("Remote", style = MaterialTheme.typography.titleSmall)
                    listOf("📁 home", "📁 var", "📄 config").forEach { Text(it, modifier = Modifier.padding(4.dp)) }
                }
            }
        }
    }
}
package com.eos.eapps.apps.eftp

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import com.eos.eapps.core.ui.components.AppCard
import com.eos.eapps.core.ui.theme.AppTheme

data class RemoteFile(
    val name: String,
    val size: String,
    val isDirectory: Boolean,
    val modified: String = ""
)

@Composable
fun App() {
    AppTheme {
        var isConnected by remember { mutableStateOf(false) }
        var showConnectDialog by remember { mutableStateOf(false) }
        var host by remember { mutableStateOf("") }
        var port by remember { mutableStateOf("21") }
        var username by remember { mutableStateOf("") }
        var password by remember { mutableStateOf("") }
        var statusMessage by remember { mutableStateOf("Disconnected") }
        var selectedLocalFiles by remember { mutableStateOf(setOf<String>()) }
        var selectedRemoteFiles by remember { mutableStateOf(setOf<String>()) }

        val localFiles = remember {
            mutableStateListOf(
                RemoteFile("Documents", "—", true, "2025-01-15"),
                RemoteFile("Downloads", "—", true, "2025-01-20"),
                RemoteFile("Pictures", "—", true, "2025-01-18"),
                RemoteFile("report.pdf", "2.4 MB", false, "2025-01-22"),
                RemoteFile("notes.txt", "12 KB", false, "2025-01-21"),
                RemoteFile("backup.zip", "156 MB", false, "2025-01-19"),
                RemoteFile("config.json", "4 KB", false, "2025-01-20"),
                RemoteFile("presentation.pptx", "8.7 MB", false, "2025-01-17")
            )
        }

        val remoteFiles = remember {
            mutableStateListOf(
                RemoteFile("public_html", "—", true, "2025-01-10"),
                RemoteFile("logs", "—", true, "2025-01-22"),
                RemoteFile("backups", "—", true, "2025-01-15"),
                RemoteFile("index.html", "45 KB", false, "2025-01-20"),
                RemoteFile("style.css", "18 KB", false, "2025-01-18"),
                RemoteFile("app.js", "234 KB", false, "2025-01-22"),
                RemoteFile("database.sql", "12.8 MB", false, "2025-01-14")
            )
        }

        @OptIn(ExperimentalMaterial3Api::class)
        Scaffold(
            topBar = {
                TopAppBar(
                    title = { Text("eFTP") },
                    actions = {
                        IconButton(onClick = {
                            if (isConnected) {
                                isConnected = false
                                statusMessage = "Disconnected"
                            } else {
                                showConnectDialog = true
                            }
                        }) {
                            Icon(
                                if (isConnected) Icons.Default.Close else Icons.Default.Settings,
                                contentDescription = if (isConnected) "Disconnect" else "Connect"
                            )
                        }
                    }
                )
            },
            bottomBar = {
                Surface(tonalElevation = 3.dp) {
                    Row(
                        modifier = Modifier.fillMaxWidth().padding(8.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(
                                if (isConnected) Icons.Default.CheckCircle else Icons.Default.Info,
                                contentDescription = null,
                                tint = if (isConnected) MaterialTheme.colorScheme.primary
                                else MaterialTheme.colorScheme.outline,
                                modifier = Modifier.size(16.dp)
                            )
                            Spacer(Modifier.width(8.dp))
                            Text(statusMessage, style = MaterialTheme.typography.bodySmall)
                        }
                        Row {
                            FilledTonalButton(
                                onClick = { statusMessage = "Uploading ${selectedLocalFiles.size} file(s)..." },
                                enabled = isConnected && selectedLocalFiles.isNotEmpty()
                            ) {
                                Icon(Icons.Default.KeyboardArrowRight, contentDescription = null, modifier = Modifier.size(18.dp))
                                Spacer(Modifier.width(4.dp))
                                Text("Upload")
                            }
                            Spacer(Modifier.width(8.dp))
                            FilledTonalButton(
                                onClick = { statusMessage = "Downloading ${selectedRemoteFiles.size} file(s)..." },
                                enabled = isConnected && selectedRemoteFiles.isNotEmpty()
                            ) {
                                Icon(Icons.Default.KeyboardArrowLeft, contentDescription = null, modifier = Modifier.size(18.dp))
                                Spacer(Modifier.width(4.dp))
                                Text("Download")
                            }
                        }
                    }
                }
            }
        ) { padding ->
            Row(modifier = Modifier.fillMaxSize().padding(padding)) {
                FilePanel(
                    title = "Local",
                    files = localFiles,
                    selectedFiles = selectedLocalFiles,
                    onSelectionChange = { selectedLocalFiles = it },
                    modifier = Modifier.weight(1f)
                )

                VerticalDivider(modifier = Modifier.fillMaxHeight())

                FilePanel(
                    title = if (isConnected) "Remote ($host)" else "Remote (not connected)",
                    files = if (isConnected) remoteFiles else emptyList(),
                    selectedFiles = selectedRemoteFiles,
                    onSelectionChange = { selectedRemoteFiles = it },
                    modifier = Modifier.weight(1f),
                    emptyMessage = if (!isConnected) "Connect to a server" else "Empty directory"
                )
            }
        }

        if (showConnectDialog) {
            AlertDialog(
                onDismissRequest = { showConnectDialog = false },
                title = { Text("Connect to Server") },
                text = {
                    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        OutlinedTextField(
                            value = host,
                            onValueChange = { host = it },
                            label = { Text("Host") },
                            placeholder = { Text("ftp.example.com") },
                            singleLine = true,
                            modifier = Modifier.fillMaxWidth()
                        )
                        OutlinedTextField(
                            value = port,
                            onValueChange = { port = it },
                            label = { Text("Port") },
                            singleLine = true,
                            modifier = Modifier.fillMaxWidth()
                        )
                        OutlinedTextField(
                            value = username,
                            onValueChange = { username = it },
                            label = { Text("Username") },
                            singleLine = true,
                            modifier = Modifier.fillMaxWidth()
                        )
                        OutlinedTextField(
                            value = password,
                            onValueChange = { password = it },
                            label = { Text("Password") },
                            singleLine = true,
                            modifier = Modifier.fillMaxWidth()
                        )
                    }
                },
                confirmButton = {
                    TextButton(onClick = {
                        if (host.isNotBlank()) {
                            isConnected = true
                            statusMessage = "Connected to $host:$port"
                            showConnectDialog = false
                        }
                    }) { Text("Connect") }
                },
                dismissButton = {
                    TextButton(onClick = { showConnectDialog = false }) { Text("Cancel") }
                }
            )
        }
    }
}

@Composable
private fun FilePanel(
    title: String,
    files: List<RemoteFile>,
    selectedFiles: Set<String>,
    onSelectionChange: (Set<String>) -> Unit,
    modifier: Modifier = Modifier,
    emptyMessage: String = "No files"
) {
    Column(modifier = modifier.fillMaxHeight()) {
        Surface(tonalElevation = 2.dp) {
            Text(
                text = title,
                style = MaterialTheme.typography.titleSmall,
                modifier = Modifier.fillMaxWidth().padding(12.dp)
            )
        }
        if (files.isEmpty()) {
            Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                Text(emptyMessage, color = MaterialTheme.colorScheme.onSurfaceVariant)
            }
        } else {
            LazyColumn(modifier = Modifier.fillMaxSize()) {
                items(files) { file ->
                    val isSelected = file.name in selectedFiles
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .clickable {
                                onSelectionChange(
                                    if (isSelected) selectedFiles - file.name
                                    else selectedFiles + file.name
                                )
                            }
                            .background(
                                if (isSelected) MaterialTheme.colorScheme.primaryContainer
                                else MaterialTheme.colorScheme.surface
                            )
                            .padding(horizontal = 12.dp, vertical = 8.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(
                            imageVector = if (file.isDirectory) Icons.Default.Folder else Icons.Default.Description,
                            contentDescription = null,
                            tint = if (file.isDirectory) MaterialTheme.colorScheme.primary
                            else MaterialTheme.colorScheme.onSurfaceVariant,
                            modifier = Modifier.size(20.dp)
                        )
                        Spacer(Modifier.width(8.dp))
                        Column(modifier = Modifier.weight(1f)) {
                            Text(
                                file.name,
                                style = MaterialTheme.typography.bodyMedium,
                                maxLines = 1,
                                overflow = TextOverflow.Ellipsis
                            )
                            Text(
                                "${file.size} • ${file.modified}",
                                style = MaterialTheme.typography.labelSmall,
                                color = MaterialTheme.colorScheme.outline
                            )
                        }
                    }
                    HorizontalDivider()
                }
            }
        }
    }
}
