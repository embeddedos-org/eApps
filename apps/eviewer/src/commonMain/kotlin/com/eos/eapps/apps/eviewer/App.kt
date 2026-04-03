package com.eos.eapps.apps.eviewer

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
        ViewerScreen()
    }
}

@Composable
fun ViewerScreen() {
    var currentPath by remember { mutableStateOf("") }
    var fileContent by remember { mutableStateOf("No file selected") }
    var fileType by remember { mutableStateOf("text") }
    var zoom by remember { mutableStateOf(1.0f) }

    Scaffold(
        topBar = {
            CenterAlignedTopAppBar(
                title = { Text("eViewer") },
                actions = {
                    IconButton(onClick = { zoom = (zoom + 0.1f).coerceAtMost(5.0f) }) { Text("+") }
                    Text("${(zoom * 100).toInt()}%")
                    IconButton(onClick = { zoom = (zoom - 0.1f).coerceAtLeast(0.1f) }) { Text("-") }
                }
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier.fillMaxSize().padding(padding),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            OutlinedTextField(
                value = currentPath,
                onValueChange = { currentPath = it },
                label = { Text("File path") },
                modifier = Modifier.fillMaxWidth().padding(8.dp),
                singleLine = true,
            )

            Row(
                modifier = Modifier.fillMaxWidth().padding(horizontal = 8.dp),
                horizontalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                FilterChip(selected = fileType == "text", onClick = { fileType = "text" }, label = { Text("Text") })
                FilterChip(selected = fileType == "image", onClick = { fileType = "image" }, label = { Text("Image") })
                FilterChip(selected = fileType == "hex", onClick = { fileType = "hex" }, label = { Text("Hex") })
                FilterChip(selected = fileType == "markdown", onClick = { fileType = "markdown" }, label = { Text("Markdown") })
            }

            Spacer(Modifier.height(8.dp))

            Card(
                modifier = Modifier.fillMaxSize().padding(8.dp),
            ) {
                Box(modifier = Modifier.fillMaxSize().padding(16.dp)) {
                    Text(
                        text = fileContent,
                        style = MaterialTheme.typography.bodyMedium,
                    )
                }
            }
        }
    }
}
