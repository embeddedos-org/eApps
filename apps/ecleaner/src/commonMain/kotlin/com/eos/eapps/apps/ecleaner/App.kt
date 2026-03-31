package com.eos.eapps.apps.ecleaner

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.delay

@Composable
fun AppContent() {
    var scanning by remember { mutableStateOf(false) }
    var scanComplete by remember { mutableStateOf(false) }
    var progress by remember { mutableStateOf(0f) }
    val items = listOf("Temp files" to "128 MB", "Browser cache" to "256 MB", "Log files" to "45 MB", "Thumbnails" to "89 MB", "Old downloads" to "312 MB")

    LaunchedEffect(scanning) {
        if (scanning) { for (i in 0..100) { progress = i / 100f; delay(30) }; scanning = false; scanComplete = true }
    }

    Column(modifier = Modifier.fillMaxSize().padding(16.dp), horizontalAlignment = Alignment.CenterHorizontally) {
        Text("🧹 eCleaner", style = MaterialTheme.typography.headlineMedium)
        Spacer(Modifier.height(16.dp))
        if (scanning) {
            CircularProgressIndicator(); Spacer(Modifier.height(8.dp))
            LinearProgressIndicator(progress = { progress }, modifier = Modifier.fillMaxWidth())
            Text("Scanning... ${(progress * 100).toInt()}%")
        } else if (scanComplete) {
            Card(modifier = Modifier.fillMaxWidth()) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("Found ${items.size} cleanup targets", style = MaterialTheme.typography.titleMedium)
                    Text("Total: 830 MB can be freed", style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.primary)
                }
            }
            Spacer(Modifier.height(8.dp))
            items.forEach { (name, size) ->
                ListItem(headlineContent = { Text(name) }, trailingContent = { Text(size) }, leadingContent = { Checkbox(checked = true, onCheckedChange = {}) })
            }
            Spacer(Modifier.height(8.dp))
            Button(onClick = { scanComplete = false }) { Text("Clean Selected") }
        } else {
            Text("🧹", style = MaterialTheme.typography.displayLarge)
            Spacer(Modifier.height(16.dp))
            Text("Free up disk space by removing temp files, caches, and logs", style = MaterialTheme.typography.bodyLarge)
            Spacer(Modifier.height(16.dp))
            Button(onClick = { scanning = true; progress = 0f }) { Text("Scan Now") }
        }
    }
}
package com.eos.eapps.apps.ecleaner

import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.tween
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.unit.dp
import com.eos.eapps.core.ui.theme.AppTheme

data class CleanCategory(
    val name: String,
    val icon: ImageVector,
    val sizeMB: Double,
    val description: String,
    val color: Color,
    var isSelected: Boolean = true
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun App() {
    AppTheme {
        var scanState by remember { mutableStateOf("idle") }
        var scanProgress by remember { mutableStateOf(0f) }
        val animatedProgress by animateFloatAsState(targetValue = scanProgress, animationSpec = tween(300))

        val categories = remember {
            mutableStateListOf(
                CleanCategory("Temporary Files", Icons.Default.Description, 245.8, "System and app temp files", Color(0xFFE53935)),
                CleanCategory("Cache Data", Icons.Default.Cached, 512.3, "Cached data from applications", Color(0xFFFF6F00)),
                CleanCategory("Log Files", Icons.Default.List, 87.4, "System and application logs", Color(0xFF7B1FA2)),
                CleanCategory("Downloads", Icons.Default.Download, 1024.6, "Old files in Downloads folder", Color(0xFF1976D2)),
                CleanCategory("Thumbnails", Icons.Default.Image, 156.2, "Cached image thumbnails", Color(0xFF388E3C)),
                CleanCategory("Old Files", Icons.Default.History, 328.9, "Files not accessed in 90+ days", Color(0xFF00838F))
            )
        }

        val totalSelected = categories.filter { it.isSelected }.sumOf { it.sizeMB }

        Scaffold(
            topBar = {
                TopAppBar(
                    title = { Text("eCleaner") },
                    actions = {
                        if (scanState == "idle") {
                            TextButton(onClick = {
                                scanState = "scanning"
                                scanProgress = 1f
                            }) { Text("Scan") }
                        }
                    }
                )
            }
        ) { padding ->
            Column(modifier = Modifier.fillMaxSize().padding(padding)) {
                Card(
                    modifier = Modifier.fillMaxWidth().padding(16.dp),
                    colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.primaryContainer)
                ) {
                    Column(
                        modifier = Modifier.padding(24.dp).fillMaxWidth(),
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        when (scanState) {
                            "idle" -> {
                                Icon(Icons.Default.Search, contentDescription = null, modifier = Modifier.size(48.dp), tint = MaterialTheme.colorScheme.primary)
                                Spacer(Modifier.height(8.dp))
                                Text("Ready to Scan", style = MaterialTheme.typography.titleLarge)
                                Text("Tap Scan to analyze disk usage", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                            }
                            "scanning" -> {
                                CircularProgressIndicator(modifier = Modifier.size(48.dp))
                                Spacer(Modifier.height(8.dp))
                                Text("Scanning...", style = MaterialTheme.typography.titleLarge)
                                Spacer(Modifier.height(8.dp))
                                LinearProgressIndicator(
                                    progress = { animatedProgress },
                                    modifier = Modifier.fillMaxWidth()
                                )
                                LaunchedEffect(Unit) {
                                    kotlinx.coroutines.delay(1500)
                                    scanState = "results"
                                }
                            }
                            "results" -> {
                                Icon(Icons.Default.CheckCircle, contentDescription = null, modifier = Modifier.size(48.dp), tint = MaterialTheme.colorScheme.primary)
                                Spacer(Modifier.height(8.dp))
                                Text("Scan Complete", style = MaterialTheme.typography.titleLarge)
                                Spacer(Modifier.height(4.dp))
                                Text(
                                    "Found ${formatSize(categories.sumOf { it.sizeMB })} to clean",
                                    style = MaterialTheme.typography.bodyMedium,
                                    color = MaterialTheme.colorScheme.onSurfaceVariant
                                )
                            }
                            "cleaned" -> {
                                Icon(Icons.Default.Done, contentDescription = null, modifier = Modifier.size(48.dp), tint = Color(0xFF4CAF50))
                                Spacer(Modifier.height(8.dp))
                                Text("Cleaned!", style = MaterialTheme.typography.titleLarge, color = Color(0xFF4CAF50))
                                Text("Disk space recovered", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                            }
                        }
                    }
                }

                if (scanState == "results" || scanState == "cleaned") {
                    LazyColumn(modifier = Modifier.weight(1f)) {
                        items(categories) { category ->
                            Card(
                                modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 4.dp),
                                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)
                            ) {
                                Row(
                                    modifier = Modifier.padding(16.dp).fillMaxWidth(),
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Icon(category.icon, contentDescription = null, tint = category.color, modifier = Modifier.size(32.dp))
                                    Spacer(Modifier.width(12.dp))
                                    Column(modifier = Modifier.weight(1f)) {
                                        Text(category.name, style = MaterialTheme.typography.titleSmall)
                                        Text(category.description, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                                        Text(formatSize(category.sizeMB), style = MaterialTheme.typography.labelMedium, color = category.color)
                                    }
                                    if (scanState == "results") {
                                        Checkbox(
                                            checked = category.isSelected,
                                            onCheckedChange = { checked ->
                                                val idx = categories.indexOf(category)
                                                categories[idx] = category.copy(isSelected = checked)
                                            }
                                        )
                                    } else {
                                        Icon(Icons.Default.Done, contentDescription = null, tint = Color(0xFF4CAF50))
                                    }
                                }
                            }
                        }
                    }

                    if (scanState == "results") {
                        Surface(tonalElevation = 3.dp) {
                            Row(
                                modifier = Modifier.fillMaxWidth().padding(16.dp),
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Text("Selected: ${formatSize(totalSelected)}", style = MaterialTheme.typography.titleSmall)
                                Button(
                                    onClick = { scanState = "cleaned" },
                                    enabled = totalSelected > 0
                                ) {
                                    Icon(Icons.Default.Delete, contentDescription = null, modifier = Modifier.size(18.dp))
                                    Spacer(Modifier.width(8.dp))
                                    Text("Clean Now")
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

private fun formatSize(mb: Double): String = when {
    mb >= 1024 -> "%.1f GB".format(mb / 1024)
    mb >= 1 -> "%.1f MB".format(mb)
    else -> "%.0f KB".format(mb * 1024)
}
