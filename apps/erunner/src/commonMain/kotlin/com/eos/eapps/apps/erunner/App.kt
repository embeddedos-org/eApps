package com.eos.eapps.apps.erunner

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
    var playerY by remember { mutableStateOf(400f) }
    var velY by remember { mutableStateOf(0f) }
    var onGround by remember { mutableStateOf(true) }
    var obstacles by remember { mutableStateOf(listOf<Float>()) }
    var score by remember { mutableStateOf(0) }
    var gameOver by remember { mutableStateOf(false) }
    var spawnTimer by remember { mutableStateOf(0f) }
    val groundY = 450f; val playerX = 80f

    fun reset() { playerY = groundY - 40f; velY = 0f; onGround = true; obstacles = emptyList(); score = 0; gameOver = false; spawnTimer = 0f }
    LaunchedEffect(Unit) { reset() }

    Column(modifier = Modifier.fillMaxSize().padding(16.dp), horizontalAlignment = Alignment.CenterHorizontally) {
        Text("🏃 eRunner", style = MaterialTheme.typography.headlineMedium)
        Text("Score: $score", style = MaterialTheme.typography.titleMedium)
        Spacer(Modifier.height(8.dp))
        Box(modifier = Modifier.fillMaxSize().weight(1f)) {
            GameCanvas(
                onUpdate = { dt ->
                    if (gameOver) return@GameCanvas
                    score++
                    velY += 1200f * dt
                    playerY += velY * dt
                    if (playerY >= groundY - 40f) { playerY = groundY - 40f; velY = 0f; onGround = true }

                    spawnTimer += dt
                    if (spawnTimer > 1.5f) { spawnTimer = 0f; obstacles = obstacles + 800f }
                    obstacles = obstacles.map { it - 300f * dt }.filter { it > -50f }
                    obstacles.forEach { ox ->
                        if (ox in (playerX - 20f)..(playerX + 30f) && playerY + 40f > groundY - 30f) gameOver = true
                    }
                },
                onTap = { if (onGround && !gameOver) { velY = -500f; onGround = false } else if (gameOver) reset() },
                onDraw = {
                    drawRect(Color(0xFF87CEEB), Offset.Zero, size)
                    drawRect(Color(0xFF8BC34A), Offset(0f, groundY), Size(size.width, size.height - groundY))
                    drawRect(Color(0xFF2196F3), Offset(playerX, playerY), Size(30f, 40f))
                    obstacles.forEach { ox -> drawRect(Color(0xFFF44336), Offset(ox, groundY - 30f), Size(20f, 30f)) }
                    if (gameOver) {
                        drawRect(Color(0x88000000), Offset.Zero, size)
                    }
                },
            )
        }
        if (gameOver) { Text("Game Over! Tap to restart", style = MaterialTheme.typography.titleMedium) }
        else { Button(onClick = { if (onGround) { velY = -500f; onGround = false } }) { Text("Jump") } }
    }
}
