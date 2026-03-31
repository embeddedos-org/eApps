package com.eos.eapps.apps.tetris

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.focusable
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.input.key.*
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.delay

val SHAPES = listOf(
    listOf(0 to 0, 1 to 0, 2 to 0, 3 to 0), // I
    listOf(0 to 0, 1 to 0, 0 to 1, 1 to 1), // O
    listOf(0 to 0, 1 to 0, 2 to 0, 1 to 1), // T
    listOf(0 to 0, 1 to 0, 1 to 1, 2 to 1), // S
    listOf(1 to 0, 2 to 0, 0 to 1, 1 to 1), // Z
    listOf(0 to 0, 0 to 1, 1 to 1, 2 to 1), // L
    listOf(2 to 0, 0 to 1, 1 to 1, 2 to 1), // J
)
val COLORS = listOf(Color.Cyan, Color.Yellow, Color(0xFF9C27B0), Color.Green, Color.Red, Color(0xFFFF9800), Color.Blue)

@Composable
fun AppContent() {
    val cols = 10; val rows = 20
    val grid = remember { Array(rows) { IntArray(cols) { 0 } } }
    var currentShape by remember { mutableStateOf(SHAPES.indices.random()) }
    var blocks by remember { mutableStateOf(SHAPES[currentShape].toMutableList()) }
    var posX by remember { mutableStateOf(3) }
    var posY by remember { mutableStateOf(0) }
    var score by remember { mutableStateOf(0) }
    var gameOver by remember { mutableStateOf(false) }
    var tick by remember { mutableStateOf(0) }

    fun canPlace(bx: Int, by: Int, shape: List<Pair<Int, Int>>): Boolean =
        shape.all { (dx, dy) ->
            val nx = bx + dx; val ny = by + dy
            nx in 0 until cols && ny in 0 until rows && grid[ny][nx] == 0
        }

    fun lockPiece() {
        blocks.forEach { (dx, dy) ->
            val nx = posX + dx; val ny = posY + dy
            if (ny in 0 until rows && nx in 0 until cols) grid[ny][nx] = currentShape + 1
        }
        var cleared = 0
        for (r in rows - 1 downTo 0) {
            if (grid[r].all { it != 0 }) {
                for (rr in r downTo 1) grid[rr] = grid[rr - 1].copyOf()
                grid[0] = IntArray(cols) { 0 }
                cleared++
            }
        }
        score += cleared * 100
        currentShape = SHAPES.indices.random()
        blocks = SHAPES[currentShape].toMutableList()
        posX = 3; posY = 0
        if (!canPlace(posX, posY, blocks)) gameOver = true
    }

    fun reset() {
        for (r in 0 until rows) for (c in 0 until cols) grid[r][c] = 0
        currentShape = SHAPES.indices.random()
        blocks = SHAPES[currentShape].toMutableList()
        posX = 3; posY = 0; score = 0; gameOver = false; tick = 0
    }

    LaunchedEffect(gameOver) {
        while (!gameOver) {
            delay(500)
            if (canPlace(posX, posY + 1, blocks)) posY++ else lockPiece()
            tick++
        }
    }

    Column(
        modifier = Modifier.fillMaxSize().padding(16.dp)
            .onKeyEvent { e ->
                if (e.type == KeyEventType.KeyDown && !gameOver) {
                    when (e.key) {
                        Key.DirectionLeft, Key.A -> if (canPlace(posX - 1, posY, blocks)) { posX--; tick++ }
                        Key.DirectionRight, Key.D -> if (canPlace(posX + 1, posY, blocks)) { posX++; tick++ }
                        Key.DirectionDown, Key.S -> if (canPlace(posX, posY + 1, blocks)) { posY++; tick++ }
                        Key.DirectionUp, Key.W -> {
                            val rotated = blocks.map { (x, y) -> -y to x }
                            if (canPlace(posX, posY, rotated)) { blocks = rotated.toMutableList(); tick++ }
                        }
                        Key.Spacebar -> { while (canPlace(posX, posY + 1, blocks)) posY++; lockPiece(); tick++ }
                    }
                    true
                } else false
            }.focusable(),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Text("🧱 Tetris", style = MaterialTheme.typography.headlineMedium)
        Text("Score: $score", style = MaterialTheme.typography.titleMedium)
        Spacer(Modifier.height(8.dp))

        val _ = tick
        Box(modifier = Modifier.aspectRatio(cols.toFloat() / rows).fillMaxWidth(0.5f).background(Color.Black)) {
            Canvas(modifier = Modifier.fillMaxSize()) {
                val cw = size.width / cols; val ch = size.height / rows
                for (r in 0 until rows) for (c in 0 until cols) {
                    if (grid[r][c] != 0) {
                        drawRect(COLORS[(grid[r][c] - 1) % COLORS.size], Offset(c * cw, r * ch), Size(cw - 1, ch - 1))
                    }
                }
                blocks.forEach { (dx, dy) ->
                    val x = (posX + dx) * cw; val y = (posY + dy) * ch
                    drawRect(COLORS[currentShape], Offset(x, y), Size(cw - 1, ch - 1))
                }
            }
        }
        Spacer(Modifier.height(8.dp))
        if (gameOver) {
            Text("Game Over!", color = MaterialTheme.colorScheme.error, style = MaterialTheme.typography.titleLarge)
            Button(onClick = { reset() }) { Text("Play Again") }
        }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            Button(onClick = { if (!gameOver && canPlace(posX - 1, posY, blocks)) { posX--; tick++ } }) { Text("◀") }
            Button(onClick = {
                if (!gameOver) { val rot = blocks.map { (x, y) -> -y to x }; if (canPlace(posX, posY, rot)) { blocks = rot.toMutableList(); tick++ } }
            }) { Text("↻") }
            Button(onClick = { if (!gameOver && canPlace(posX + 1, posY, blocks)) { posX++; tick++ } }) { Text("▶") }
            Button(onClick = { if (!gameOver) { while (canPlace(posX, posY + 1, blocks)) posY++; lockPiece(); tick++ } }) { Text("▼▼") }
        }
    }
}
