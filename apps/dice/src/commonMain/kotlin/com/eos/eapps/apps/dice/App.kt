package com.eos.eapps.apps.dice

import androidx.compose.animation.core.*
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.delay

val DICE_FACES = listOf("⚀", "⚁", "⚂", "⚃", "⚄", "⚅")

@Composable
fun AppContent() {
    var diceCount by remember { mutableStateOf(2) }
    var results by remember { mutableStateOf(List(2) { (1..6).random() }) }
    var rolling by remember { mutableStateOf(false) }
    var total by remember { mutableStateOf(results.sum()) }

    LaunchedEffect(rolling) {
        if (rolling) {
            repeat(10) {
                results = List(diceCount) { (1..6).random() }
                delay(80)
            }
            total = results.sum()
            rolling = false
        }
    }

    Column(
        modifier = Modifier.fillMaxSize().padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center,
    ) {
        Text("🎲 Dice", style = MaterialTheme.typography.headlineMedium)
        Spacer(Modifier.height(24.dp))

        Row(horizontalArrangement = Arrangement.spacedBy(16.dp)) {
            results.forEach { value ->
                Card(modifier = Modifier.size(80.dp)) {
                    Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                        Text(DICE_FACES[value - 1], fontSize = 48.sp, textAlign = TextAlign.Center)
                    }
                }
            }
        }

        Spacer(Modifier.height(16.dp))
        Text("Total: $total", style = MaterialTheme.typography.headlineSmall)

        Spacer(Modifier.height(24.dp))
        Button(onClick = { rolling = true }, enabled = !rolling) {
            Text(if (rolling) "Rolling..." else "Roll Dice")
        }

        Spacer(Modifier.height(16.dp))
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp), verticalAlignment = Alignment.CenterVertically) {
            Text("Dice count:")
            (1..4).forEach { count ->
                FilterChip(
                    selected = diceCount == count,
                    onClick = { diceCount = count; results = List(count) { (1..6).random() }; total = results.sum() },
                    label = { Text("$count") },
                )
            }
        }
    }
}
