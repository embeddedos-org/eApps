package com.eos.eapps.apps.eblocks

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp

val BLOCK_COLORS = listOf(Color(0xFF2196F3), Color(0xFF4CAF50), Color(0xFFFF9800), Color(0xFF9C27B0), Color(0xFFF44336))

@Composable
fun AppContent() {
    val size = 10
    var grid by remember { mutableStateOf(Array(size) { IntArray(size) { 0 } }) }
    var score by remember { mutableStateOf(0) }
    var tick by remember { mutableStateOf(0) }

    fun clearFullLines() {
        var cleared = 0
        for (r in 0 until size) if (grid[r].all { it != 0 }) { grid[r] = IntArray(size) { 0 }; cleared++ }
        for (c in 0 until size) if ((0 until size).all { grid[it][c] != 0 }) { for (r in 0 until size) grid[r][c] = 0; cleared++ }
        score += cleared * 100
    }

    Column(modifier = Modifier.fillMaxSize().padding(16.dp), horizontalAlignment = Alignment.CenterHorizontally) {
        Text("🟦 eBlocks", style = MaterialTheme.typography.headlineMedium)
        Text("Score: $score", style = MaterialTheme.typography.titleMedium)
        Spacer(Modifier.height(8.dp))
        val _ = tick
        Box(modifier = Modifier.aspectRatio(1f).fillMaxWidth(0.9f)) {
            LazyVerticalGrid(columns = GridCells.Fixed(size), modifier = Modifier.fillMaxSize(), userScrollEnabled = false) {
                items(size * size) { idx ->
                    val r = idx / size; val c = idx % size
                    Box(
                        modifier = Modifier.aspectRatio(1f).padding(0.5.dp)
                            .background(if (grid[r][c] != 0) BLOCK_COLORS[(grid[r][c] - 1) % BLOCK_COLORS.size] else Color(0xFFEEEEEE))
                            .border(0.5.dp, Color.LightGray)
                            .clickable {
                                if (grid[r][c] == 0) {
                                    grid[r][c] = (BLOCK_COLORS.indices.random()) + 1
                                    clearFullLines(); tick++
                                }
                            },
                    )
                }
            }
        }
        Spacer(Modifier.height(8.dp))
        Button(onClick = { grid = Array(size) { IntArray(size) { 0 } }; score = 0; tick++ }) { Text("New Game") }
    }
}
package com.eos.eapps.apps.eblocks

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.eos.eapps.core.ui.canvas.GameCanvas
import com.eos.eapps.core.ui.theme.AppTheme
import kotlin.random.Random

private enum class Screen { HOME, GAME }
private const val GRID = 8

private val BLOCK_COLORS = listOf(
    Color(0xFFE53935), Color(0xFF43A047), Color(0xFF1E88E5),
    Color(0xFFFDD835), Color(0xFF8E24AA), Color(0xFFFF7043)
)

private data class BlockPiece(
    val cells: List<Pair<Int, Int>>,
    val color: Color
)

private data class BlocksState(
    val grid: List<IntArray> = List(GRID) { IntArray(GRID) },
    val pieces: List<BlockPiece?> = List(3) { randomPiece() },
    val score: Int = 0,
    val gameOver: Boolean = false,
    val selectedPiece: Int = -1,
    val canvasW: Float = 400f,
    val canvasH: Float = 600f
)

private val PIECE_SHAPES = listOf(
    listOf(0 to 0),
    listOf(0 to 0, 1 to 0),
    listOf(0 to 0, 0 to 1),
    listOf(0 to 0, 1 to 0, 0 to 1),
    listOf(0 to 0, 1 to 0, 2 to 0),
    listOf(0 to 0, 0 to 1, 0 to 2),
    listOf(0 to 0, 1 to 0, 1 to 1),
    listOf(0 to 0, 1 to 0, 0 to 1, 1 to 1),
    listOf(0 to 0, 1 to 0, 2 to 0, 3 to 0),
    listOf(0 to 0, 0 to 1, 1 to 1, 1 to 2),
    listOf(0 to 0, 1 to 0, 2 to 0, 2 to 1),
)

private fun randomPiece(): BlockPiece {
    val shape = PIECE_SHAPES.random()
    return BlockPiece(cells = shape, color = BLOCK_COLORS.random())
}

private fun canPlace(grid: List<IntArray>, piece: BlockPiece, row: Int, col: Int): Boolean {
    return piece.cells.all { (dc, dr) ->
        val r = row + dr; val c = col + dc
        r in 0 until GRID && c in 0 until GRID && grid[r][c] == 0
    }
}

private fun placePiece(grid: List<IntArray>, piece: BlockPiece, row: Int, col: Int, colorIdx: Int): List<IntArray> {
    val newGrid = grid.map { it.copyOf() }
    piece.cells.forEach { (dc, dr) -> newGrid[row + dr][col + dc] = colorIdx + 1 }
    return newGrid
}

private fun clearLines(grid: List<IntArray>): Pair<List<IntArray>, Int> {
    val newGrid = grid.map { it.copyOf() }
    var cleared = 0
    for (r in 0 until GRID) {
        if (newGrid[r].all { it != 0 }) { newGrid[r].fill(0); cleared++ }
    }
    for (c in 0 until GRID) {
        if ((0 until GRID).all { newGrid[it][c] != 0 }) {
            for (r in 0 until GRID) newGrid[r][c] = 0
            cleared++
        }
    }
    return newGrid to cleared
}

private fun anyPieceFits(grid: List<IntArray>, pieces: List<BlockPiece?>): Boolean {
    return pieces.filterNotNull().any { piece ->
        (0 until GRID).any { r -> (0 until GRID).any { c -> canPlace(grid, piece, r, c) } }
    }
}

@Composable
fun App() {
    AppTheme {
        var screen by remember { mutableStateOf(Screen.HOME) }
        var highScore by remember { mutableStateOf(0) }
        when (screen) {
            Screen.HOME -> HomeScreen(highScore) { screen = Screen.GAME }
            Screen.GAME -> GameScreen(
                onGameOver = { s -> if (s > highScore) highScore = s },
                onBack = { screen = Screen.HOME }
            )
        }
    }
}

@Composable
private fun HomeScreen(highScore: Int, onPlay: () -> Unit) {
    Column(
        modifier = Modifier.fillMaxSize().background(Color(0xFF263238)).padding(32.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text("\uD83E\uDDF1 eBlocks", fontSize = 48.sp, color = Color.White)
        Spacer(Modifier.height(16.dp))
        Text("Block Puzzle", fontSize = 18.sp, color = Color(0xFF90A4AE))
        Spacer(Modifier.height(32.dp))
        Button(
            onClick = onPlay,
            colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF455A64)),
            modifier = Modifier.width(200.dp).height(56.dp)
        ) { Text("Play", fontSize = 20.sp) }
        Spacer(Modifier.height(24.dp))
        Text("High Score: $highScore", fontSize = 20.sp, color = Color(0xFFB0BEC5))
    }
}

@Composable
private fun GameScreen(onGameOver: (Int) -> Unit, onBack: () -> Unit) {
    var state by remember { mutableStateOf(BlocksState()) }
    var showDialog by remember { mutableStateOf(false) }

    fun resetGame() {
        state = BlocksState(canvasW = state.canvasW, canvasH = state.canvasH)
        showDialog = false
    }

    Column(modifier = Modifier.fillMaxSize().background(Color(0xFF1A1A2E))) {
        Row(
            modifier = Modifier.fillMaxWidth().padding(8.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            TextButton(onClick = onBack) { Text("\u2190 Back", color = Color.White) }
            Text("Score: ${state.score}", color = Color.White, fontSize = 20.sp)
        }

        Box(modifier = Modifier.weight(1f).fillMaxWidth(), contentAlignment = Alignment.Center) {
            GameCanvas(
                modifier = Modifier.fillMaxSize().padding(8.dp),
                onTap = { offset ->
                    if (state.gameOver) return@GameCanvas
                    val cellSize = minOf(state.canvasW, state.canvasH * 0.7f) / GRID
                    val offX = (state.canvasW - cellSize * GRID) / 2f
                    val offY = 20f
                    val col = ((offset.x - offX) / cellSize).toInt()
                    val row = ((offset.y - offY) / cellSize).toInt()

                    if (row in 0 until GRID && col in 0 until GRID && state.selectedPiece >= 0) {
                        val piece = state.pieces[state.selectedPiece]
                        if (piece != null && canPlace(state.grid, piece, row, col)) {
                            val colorIdx = BLOCK_COLORS.indexOf(piece.color).coerceAtLeast(0)
                            val placed = placePiece(state.grid, piece, row, col, colorIdx)
                            val (cleared, linesCleared) = clearLines(placed)
                            val newPieces = state.pieces.toMutableList()
                            newPieces[state.selectedPiece] = null

                            if (newPieces.all { it == null }) {
                                for (i in newPieces.indices) newPieces[i] = randomPiece()
                            }

                            val newScore = state.score + linesCleared * 100 + piece.cells.size * 5
                            val newState = state.copy(
                                grid = cleared, pieces = newPieces, score = newScore, selectedPiece = -1
                            )

                            if (!anyPieceFits(cleared, newPieces)) {
                                onGameOver(newScore)
                                showDialog = true
                                state = newState.copy(gameOver = true)
                            } else {
                                state = newState
                            }
                        }
                    } else {
                        val pieceAreaY = state.canvasH * 0.75f
                        val pieceW = state.canvasW / 3f
                        if (offset.y > pieceAreaY) {
                            val pieceIdx = (offset.x / pieceW).toInt().coerceIn(0, 2)
                            if (state.pieces[pieceIdx] != null) {
                                state = state.copy(selectedPiece = pieceIdx)
                            }
                        }
                    }
                },
                onDraw = {
                    state = state.copy(canvasW = size.width, canvasH = size.height)
                    val cellSize = minOf(size.width, size.height * 0.7f) / GRID
                    val offX = (size.width - cellSize * GRID) / 2f
                    val offY = 20f

                    drawRect(Color(0xFF1A1A2E), Offset.Zero, size)
                    drawRect(Color(0xFF263238), Offset(offX, offY), Size(cellSize * GRID, cellSize * GRID))

                    for (r in 0 until GRID) for (c in 0 until GRID) {
                        val x = offX + c * cellSize; val y = offY + r * cellSize
                        drawRect(Color(0xFF37474F), Offset(x + 1, y + 1), Size(cellSize - 2, cellSize - 2))
                        val v = state.grid[r][c]
                        if (v > 0) {
                            drawRect(BLOCK_COLORS[(v - 1) % BLOCK_COLORS.size], Offset(x + 2, y + 2), Size(cellSize - 4, cellSize - 4))
                        }
                    }

                    val pieceAreaY = size.height * 0.75f
                    val pieceW = size.width / 3f
                    state.pieces.forEachIndexed { i, piece ->
                        if (piece == null) return@forEachIndexed
                        val baseX = i * pieceW + pieceW * 0.2f
                        val baseY = pieceAreaY + 20f
                        val pCellSize = cellSize * 0.6f
                        val selected = state.selectedPiece == i

                        if (selected) {
                            drawRect(Color.White.copy(alpha = 0.2f), Offset(i * pieceW, pieceAreaY), Size(pieceW, size.height - pieceAreaY))
                        }

                        piece.cells.forEach { (dc, dr) ->
                            drawRect(piece.color, Offset(baseX + dc * pCellSize + 1, baseY + dr * pCellSize + 1), Size(pCellSize - 2, pCellSize - 2))
                        }
                    }
                }
            )
        }
    }

    if (showDialog) {
        AlertDialog(
            onDismissRequest = {},
            title = { Text("Game Over") },
            text = { Text("Score: ${state.score}") },
            confirmButton = { TextButton(onClick = { resetGame() }) { Text("Play Again") } },
            dismissButton = { TextButton(onClick = onBack) { Text("Home") } }
        )
    }
}
