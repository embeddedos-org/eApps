package com.eos.eapps.apps.econverter

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

@Composable
fun AppContent() {
    var input by remember { mutableStateOf("") }
    var selectedConversion by remember { mutableStateOf(0) }
    val conversions = listOf("Text → Base64", "Base64 → Text", "Text → Hex", "Hex → Text", "Uppercase", "Lowercase")

    val result = remember(input, selectedConversion) {
        if (input.isBlank()) return@remember ""
        try {
            when (selectedConversion) {
                0 -> input.encodeToByteArray().joinToString("") { "%02x".format(it.toInt() and 0xFF) }
                1 -> input
                2 -> input.encodeToByteArray().joinToString(" ") { "%02X".format(it.toInt() and 0xFF) }
                3 -> input.split(" ").filter { it.isNotBlank() }.map { it.toInt(16).toChar() }.joinToString("")
                4 -> input.uppercase()
                5 -> input.lowercase()
                else -> ""
            }
        } catch (_: Exception) { "Invalid input" }
    }

    Column(modifier = Modifier.fillMaxSize().padding(16.dp), horizontalAlignment = Alignment.CenterHorizontally) {
        Text("🔄 eConverter", style = MaterialTheme.typography.headlineMedium)
        Spacer(Modifier.height(16.dp))
        Row(horizontalArrangement = Arrangement.spacedBy(4.dp)) {
            conversions.forEachIndexed { i, c ->
                FilterChip(selected = selectedConversion == i, onClick = { selectedConversion = i }, label = { Text(c, style = MaterialTheme.typography.bodySmall) })
            }
        }
        Spacer(Modifier.height(16.dp))
        OutlinedTextField(value = input, onValueChange = { input = it }, label = { Text("Input") }, modifier = Modifier.fillMaxWidth().height(120.dp))
        Spacer(Modifier.height(8.dp))
        Card(modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("Result:", style = MaterialTheme.typography.labelLarge)
                Text(result, style = MaterialTheme.typography.bodyLarge)
            }
        }
    }
}
