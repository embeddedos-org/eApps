package com.eos.eapps.apps.enote

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

data class Note(val id: Int, var title: String, var content: String)

@Composable
fun AppContent() {
    var notes by remember { mutableStateOf(listOf<Note>()) }
    var editingNote by remember { mutableStateOf<Note?>(null) }
    var nextId by remember { mutableStateOf(1) }

    if (editingNote != null) {
        val note = editingNote!!
        var title by remember(note.id) { mutableStateOf(note.title) }
        var content by remember(note.id) { mutableStateOf(note.content) }
        Column(modifier = Modifier.fillMaxSize().padding(16.dp)) {
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                TextButton(onClick = {
                    notes = notes.map { if (it.id == note.id) it.copy(title = title, content = content) else it }
                    editingNote = null
                }) { Text("← Save") }
                Text("📝 Edit Note", style = MaterialTheme.typography.titleMedium)
                Spacer(Modifier.width(48.dp))
            }
            Spacer(Modifier.height(8.dp))
            OutlinedTextField(value = title, onValueChange = { title = it }, label = { Text("Title") }, modifier = Modifier.fillMaxWidth(), singleLine = true)
            Spacer(Modifier.height(8.dp))
            OutlinedTextField(value = content, onValueChange = { content = it }, label = { Text("Content") }, modifier = Modifier.fillMaxWidth().weight(1f))
        }
    } else {
        Column(modifier = Modifier.fillMaxSize().padding(16.dp)) {
            Row(modifier = Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.SpaceBetween) {
                Text("📝 eNote", style = MaterialTheme.typography.headlineMedium)
                FloatingActionButton(onClick = {
                    val note = Note(nextId++, "Untitled", "")
                    notes = notes + note
                    editingNote = note
                }) { Icon(Icons.Default.Add, "New Note") }
            }
            Spacer(Modifier.height(8.dp))
            if (notes.isEmpty()) {
                Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) { Text("No notes yet. Tap + to create one.") }
            } else {
                LazyColumn(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    items(notes) { note ->
                        Card(modifier = Modifier.fillMaxWidth()) {
                            Row(modifier = Modifier.padding(16.dp), verticalAlignment = Alignment.CenterVertically) {
                                Column(modifier = Modifier.weight(1f).padding(end = 8.dp)) {
                                    Text(note.title.ifBlank { "Untitled" }, style = MaterialTheme.typography.titleSmall)
                                    Text(note.content.take(100), style = MaterialTheme.typography.bodySmall, maxLines = 2)
                                }
                                IconButton(onClick = { editingNote = note }) { Text("✏️") }
                                IconButton(onClick = { notes = notes.filter { it.id != note.id } }) { Icon(Icons.Default.Delete, "Delete") }
                            }
                        }
                    }
                }
            }
        }
    }
}
package com.eos.eapps.apps.enote

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
import kotlinx.datetime.Clock

data class Note(
    val id: Long = Clock.System.now().toEpochMilliseconds(),
    val title: String = "",
    val body: String = "",
    val timestamp: Long = Clock.System.now().toEpochMilliseconds()
)

@Composable
fun App() {
    AppTheme {
        val notes = remember { mutableStateListOf<Note>() }
        var editingNote by remember { mutableStateOf<Note?>(null) }
        var searchQuery by remember { mutableStateOf("") }
        var showDeleteDialog by remember { mutableStateOf<Note?>(null) }

        if (editingNote != null) {
            NoteEditor(
                note = editingNote!!,
                onSave = { updated ->
                    val idx = notes.indexOfFirst { it.id == updated.id }
                    if (idx >= 0) notes[idx] = updated.copy(timestamp = Clock.System.now().toEpochMilliseconds())
                    else notes.add(0, updated.copy(timestamp = Clock.System.now().toEpochMilliseconds()))
                    editingNote = null
                },
                onBack = { editingNote = null }
            )
        } else {
            NoteList(
                notes = notes,
                searchQuery = searchQuery,
                onSearchChange = { searchQuery = it },
                onNoteClick = { editingNote = it },
                onNewNote = { editingNote = Note() },
                onDeleteRequest = { showDeleteDialog = it }
            )
        }

        showDeleteDialog?.let { note ->
            AlertDialog(
                onDismissRequest = { showDeleteDialog = null },
                title = { Text("Delete Note") },
                text = { Text("Delete \"${note.title.ifEmpty { "Untitled" }}\"?") },
                confirmButton = {
                    TextButton(onClick = {
                        notes.removeAll { it.id == note.id }
                        showDeleteDialog = null
                    }) { Text("Delete") }
                },
                dismissButton = {
                    TextButton(onClick = { showDeleteDialog = null }) { Text("Cancel") }
                }
            )
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun NoteList(
    notes: List<Note>,
    searchQuery: String,
    onSearchChange: (String) -> Unit,
    onNoteClick: (Note) -> Unit,
    onNewNote: () -> Unit,
    onDeleteRequest: (Note) -> Unit
) {
    val filtered = notes.filter {
        searchQuery.isEmpty() ||
                it.title.contains(searchQuery, ignoreCase = true) ||
                it.body.contains(searchQuery, ignoreCase = true)
    }.sortedByDescending { it.timestamp }

    Scaffold(
        topBar = {
            TopAppBar(title = { Text("eNote") })
        },
        floatingActionButton = {
            FloatingActionButton(onClick = onNewNote) {
                Icon(Icons.Default.Add, contentDescription = "New Note")
            }
        }
    ) { padding ->
        Column(modifier = Modifier.fillMaxSize().padding(padding)) {
            OutlinedTextField(
                value = searchQuery,
                onValueChange = onSearchChange,
                modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 8.dp),
                placeholder = { Text("Search notes...") },
                leadingIcon = { Icon(Icons.Default.Search, contentDescription = null) },
                trailingIcon = {
                    if (searchQuery.isNotEmpty()) {
                        IconButton(onClick = { onSearchChange("") }) {
                            Icon(Icons.Default.Clear, contentDescription = "Clear")
                        }
                    }
                },
                singleLine = true
            )

            if (filtered.isEmpty()) {
                Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                    Text(
                        if (notes.isEmpty()) "No notes yet. Tap + to create one."
                        else "No notes match your search.",
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            } else {
                LazyColumn(modifier = Modifier.fillMaxSize()) {
                    items(filtered, key = { it.id }) { note ->
                        AppCard(onClick = { onNoteClick(note) }) {
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.Top
                            ) {
                                Column(modifier = Modifier.weight(1f)) {
                                    Text(
                                        text = note.title.ifEmpty { "Untitled" },
                                        style = MaterialTheme.typography.titleMedium,
                                        maxLines = 1,
                                        overflow = TextOverflow.Ellipsis
                                    )
                                    Spacer(Modifier.height(4.dp))
                                    Text(
                                        text = note.body.take(100).ifEmpty { "No content" },
                                        style = MaterialTheme.typography.bodySmall,
                                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                                        maxLines = 2,
                                        overflow = TextOverflow.Ellipsis
                                    )
                                    Spacer(Modifier.height(4.dp))
                                    Text(
                                        text = formatTimestamp(note.timestamp),
                                        style = MaterialTheme.typography.labelSmall,
                                        color = MaterialTheme.colorScheme.outline
                                    )
                                }
                                IconButton(onClick = { onDeleteRequest(note) }) {
                                    Icon(
                                        Icons.Default.Delete,
                                        contentDescription = "Delete",
                                        tint = MaterialTheme.colorScheme.error
                                    )
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun NoteEditor(
    note: Note,
    onSave: (Note) -> Unit,
    onBack: () -> Unit
) {
    var title by remember { mutableStateOf(note.title) }
    var body by remember { mutableStateOf(note.body) }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(if (note.title.isEmpty() && note.body.isEmpty()) "New Note" else "Edit Note") },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back")
                    }
                },
                actions = {
                    IconButton(onClick = { onSave(note.copy(title = title, body = body)) }) {
                        Icon(Icons.Default.Check, contentDescription = "Save")
                    }
                }
            )
        }
    ) { padding ->
        Column(modifier = Modifier.fillMaxSize().padding(padding).padding(16.dp)) {
            OutlinedTextField(
                value = title,
                onValueChange = { title = it },
                modifier = Modifier.fillMaxWidth(),
                label = { Text("Title") },
                singleLine = true,
                textStyle = MaterialTheme.typography.titleLarge
            )
            Spacer(Modifier.height(12.dp))
            OutlinedTextField(
                value = body,
                onValueChange = { body = it },
                modifier = Modifier.fillMaxWidth().weight(1f),
                label = { Text("Note") },
                textStyle = MaterialTheme.typography.bodyLarge
            )
        }
    }
}

private fun formatTimestamp(millis: Long): String {
    val seconds = millis / 1000
    val minutes = seconds / 60
    val hours = minutes / 60
    val days = hours / 24
    val nowMillis = Clock.System.now().toEpochMilliseconds()
    val diffSec = (nowMillis - millis) / 1000
    return when {
        diffSec < 60 -> "just now"
        diffSec < 3600 -> "${diffSec / 60}m ago"
        diffSec < 86400 -> "${diffSec / 3600}h ago"
        else -> "${diffSec / 86400}d ago"
    }
}
