package com.eos.eapps.apps.esurfer

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import com.eos.eapps.core.ui.canvas.*
import kotlin.random.Random

@Composable
fun AppContent() {
    var lane by remember { mutableStateOf(1) }
    var obstacles by remember { mutableStateOf(listOf<Pair<Int, Float>>()) }
    var score by remember { mutableStateOf(0) }
    var gameOver by remember { mutableStateOf(false) }
    var spawnTimer by remember { mutableStateOf(0f) }
    val lanes = 3; val laneWidth = 80f

    fun reset() { lane = 1; obstacles = emptyList(); score = 0; gameOver = false; spawnTimer = 0f }

    Column(modifier = Modifier.fillMaxSize().padding(16.dp), horizontalAlignment = Alignment.CenterHorizontally) {
        Text("🏄 eSurfer", style = MaterialTheme.typography.headlineMedium)
        Text("Score: $score", style = MaterialTheme.typography.titleMedium)
        Spacer(Modifier.height(8.dp))
        Box(modifier = Modifier.fillMaxSize().weight(1f)) {
            GameCanvas(
                onUpdate = { dt ->
                    if (gameOver) return@GameCanvas
                    score++
                    spawnTimer += dt
                    if (spawnTimer > 0.8f) { spawnTimer = 0f; obstacles = obstacles + (Random.nextInt(lanes) to 0f) }
                    obstacles = obstacles.map { (l, y) -> l to (y + 400f * dt) }.filter { it.second < 700f }
                    obstacles.forEach { (ol, oy) -> if (ol == lane && oy > 500f && oy < 560f) gameOver = true }
                },
                onTap = { offset ->
                    if (gameOver) { reset() } else {
                        if (offset.x < 300f && lane > 0) lane-- else if (lane < 2) lane++
                    }
                },
                onDraw = {
                    val startX = (size.width - lanes * laneWidth) / 2
                    drawRect(Color(0xFF424242), Offset.Zero, size)
                    for (i in 0 until lanes) {
                        drawRect(Color(0xFF616161), Offset(startX + i * laneWidth, 0f), Size(laneWidth - 4f, size.height))
                    }
                    val px = startX + lane * laneWidth + 10f
                    drawRect(Color(0xFF2196F3), Offset(px, 520f), Size(laneWidth - 24f, 40f))
                    obstacles.forEach { (ol, oy) ->
                        drawRect(Color(0xFFF44336), Offset(startX + ol * laneWidth + 10f, oy), Size(laneWidth - 24f, 30f))
                    }
                },
            )
        }
        Row(horizontalArrangement = Arrangement.spacedBy(16.dp)) {
            Button(onClick = { if (!gameOver && lane > 0) lane-- }) { Text("◀") }
            Button(onClick = { if (!gameOver && lane < 2) lane++ }) { Text("▶") }
        }
    }
}
