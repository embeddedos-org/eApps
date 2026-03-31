package com.eos.eapps.apps.efiles

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

data class FileEntry(val name: String, val isDir: Boolean, val size: String = "", val icon: String = if (isDir) "📁" else "📄")

@Composable
fun AppContent() {
    var currentPath by remember { mutableStateOf("/") }
    val files = remember(currentPath) {
        if (currentPath == "/") listOf(
            FileEntry("Documents", true), FileEntry("Downloads", true), FileEntry("Pictures", true),
            FileEntry("Music", true), FileEntry("Videos", true), FileEntry("readme.txt", false, "2.1 KB"),
            FileEntry("config.json", false, "512 B"), FileEntry("notes.md", false, "8.3 KB"),
        ) else listOf(
            FileEntry("file1.txt", false, "1.2 KB"), FileEntry("file2.pdf", false, "256 KB"),
            FileEntry("subfolder", true), FileEntry("image.png", false, "1.5 MB"),
        )
    }

    Column(modifier = Modifier.fillMaxSize().padding(16.dp)) {
        Text("📁 eFiles", style = MaterialTheme.typography.headlineMedium, modifier = Modifier.align(Alignment.CenterHorizontally))
        Spacer(Modifier.height(8.dp))
        Row(verticalAlignment = Alignment.CenterVertically) {
            if (currentPath != "/") TextButton(onClick = { currentPath = "/" }) { Text("← Back") }
            Text("Path: $currentPath", style = MaterialTheme.typography.bodyMedium, modifier = Modifier.weight(1f))
        }
        HorizontalDivider()
        LazyColumn {
            items(files) { file ->
                ListItem(
                    headlineContent = { Text(file.name) },
                    supportingContent = { if (!file.isDir) Text(file.size) },
                    leadingContent = { Text(file.icon, style = MaterialTheme.typography.titleLarge) },
                    modifier = Modifier.clickable { if (file.isDir) currentPath = "$currentPath${file.name}/" },
                )
            }
        }
    }
}
