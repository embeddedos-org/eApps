package com.eos.eapps.apps.ecrush

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.delay

val CANDY_COLORS = listOf(Color.Red, Color.Blue, Color.Green, Color.Yellow, Color(0xFFFF9800), Color(0xFF9C27B0))
val CANDY_ICONS = listOf("🍬", "🍭", "🍫", "🍩", "🍪", "🧁")

@Composable
fun AppContent() {
    val rows = 8; val cols = 8
    var grid by remember { mutableStateOf(Array(rows) { IntArray(cols) { CANDY_COLORS.indices.random() } }) }
    var selected by remember { mutableStateOf<Pair<Int, Int>?>(null) }
    var score by remember { mutableStateOf(0) }
    var tick by remember { mutableStateOf(0) }

    fun findMatches(): List<Pair<Int, Int>> {
        val matches = mutableSetOf<Pair<Int, Int>>()
        for (r in 0 until rows) for (c in 0 until cols - 2) {
            if (grid[r][c] == grid[r][c + 1] && grid[r][c] == grid[r][c + 2]) {
                matches.addAll(listOf(r to c, r to (c + 1), r to (c + 2)))
            }
        }
        for (r in 0 until rows - 2) for (c in 0 until cols) {
            if (grid[r][c] == grid[r + 1][c] && grid[r][c] == grid[r + 2][c]) {
                matches.addAll(listOf(r to c, (r + 1) to c, (r + 2) to c))
            }
        }
        return matches.toList()
    }

    fun clearAndDrop() {
        var matched = findMatches()
        while (matched.isNotEmpty()) {
            score += matched.size * 10
            matched.forEach { (r, c) -> grid[r][c] = -1 }
            for (c in 0 until cols) {
                val col = (0 until rows).map { grid[it][c] }.toMutableList()
                val nonEmpty = col.filter { it >= 0 }.toMutableList()
                while (nonEmpty.size < rows) nonEmpty.add(0, CANDY_COLORS.indices.random())
                for (r in 0 until rows) grid[r][c] = nonEmpty[r]
            }
            matched = findMatches()
        }
        tick++
    }

    fun swap(r1: Int, c1: Int, r2: Int, c2: Int) {
        val temp = grid[r1][c1]; grid[r1][c1] = grid[r2][c2]; grid[r2][c2] = temp
        if (findMatches().isEmpty()) {
            val t = grid[r1][c1]; grid[r1][c1] = grid[r2][c2]; grid[r2][c2] = t
        } else clearAndDrop()
    }

    LaunchedEffect(Unit) { clearAndDrop() }

    Column(modifier = Modifier.fillMaxSize().padding(16.dp), horizontalAlignment = Alignment.CenterHorizontally) {
        Text("🍬 eCrush", style = MaterialTheme.typography.headlineMedium)
        Text("Score: $score", style = MaterialTheme.typography.titleMedium)
        Spacer(Modifier.height(8.dp))
        val _ = tick
        Box(modifier = Modifier.aspectRatio(1f).fillMaxWidth(0.9f)) {
            LazyVerticalGrid(columns = GridCells.Fixed(cols), modifier = Modifier.fillMaxSize(), userScrollEnabled = false) {
                items(rows * cols) { idx ->
                    val r = idx / cols; val c = idx % cols; val candy = grid[r][c]
                    val isSelected = selected == (r to c)
                    Box(
                        modifier = Modifier.aspectRatio(1f)
                            .padding(1.dp)
                            .background(if (isSelected) Color(0xFFE0E0E0) else Color.Transparent)
                            .clickable {
                                if (selected == null) { selected = r to c }
                                else {
                                    val (sr, sc) = selected!!
                                    if ((kotlin.math.abs(sr - r) + kotlin.math.abs(sc - c)) == 1) swap(sr, sc, r, c)
                                    selected = null
                                }
                            },
                        contentAlignment = Alignment.Center,
                    ) {
                        if (candy in CANDY_ICONS.indices) Text(CANDY_ICONS[candy], fontSize = 24.sp)
                    }
                }
            }
        }
        Spacer(Modifier.height(8.dp))
        Button(onClick = { grid = Array(rows) { IntArray(cols) { CANDY_COLORS.indices.random() } }; score = 0; clearAndDrop() }) { Text("New Game") }
    }
}
package com.eos.eapps.apps.ecrush

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
private const val MAX_MOVES = 30

private val CANDY_COLORS = listOf(
    Color(0xFFE53935), Color(0xFFFFA726), Color(0xFFFFEB3B),
    Color(0xFF66BB6A), Color(0xFF42A5F5), Color(0xFFAB47BC)
)

private data class CrushState(
    val board: List<IntArray> = List(GRID) { IntArray(GRID) { Random.nextInt(CANDY_COLORS.size) } },
    val score: Int = 0,
    val movesLeft: Int = MAX_MOVES,
    val selectedCell: Pair<Int, Int>? = null,
    val gameOver: Boolean = false,
    val canvasW: Float = 400f,
    val canvasH: Float = 600f
)

private fun initBoard(): List<IntArray> {
    var board = List(GRID) { IntArray(GRID) { Random.nextInt(CANDY_COLORS.size) } }
    while (hasMatches(board)) {
        val (cleared, _) = clearMatches(board)
        board = fillBoard(cleared)
    }
    return board
}

private fun hasMatches(board: List<IntArray>): Boolean {
    for (r in 0 until GRID) for (c in 0 until GRID) {
        val v = board[r][c]
        if (v < 0) continue
        if (c + 2 < GRID && board[r][c + 1] == v && board[r][c + 2] == v) return true
        if (r + 2 < GRID && board[r + 1][c] == v && board[r + 2][c] == v) return true
    }
    return false
}

private fun clearMatches(board: List<IntArray>): Pair<List<IntArray>, Int> {
    val toRemove = Array(GRID) { BooleanArray(GRID) }
    var count = 0

    for (r in 0 until GRID) {
        var c = 0
        while (c < GRID) {
            val v = board[r][c]
            if (v < 0) { c++; continue }
            var end = c
            while (end + 1 < GRID && board[r][end + 1] == v) end++
            if (end - c >= 2) for (i in c..end) toRemove[r][i] = true
            c = end + 1
        }
    }

    for (c in 0 until GRID) {
        var r = 0
        while (r < GRID) {
            val v = board[r][c]
            if (v < 0) { r++; continue }
            var end = r
            while (end + 1 < GRID && board[end + 1][c] == v) end++
            if (end - r >= 2) for (i in r..end) toRemove[i][c] = true
            r = end + 1
        }
    }

    val result = board.map { it.copyOf() }
    for (r in 0 until GRID) for (c in 0 until GRID) {
        if (toRemove[r][c]) { result[r][c] = -1; count++ }
    }
    return result to count
}

private fun fillBoard(board: List<IntArray>): List<IntArray> {
    val result = board.map { it.copyOf() }
    for (c in 0 until GRID) {
        var writeRow = GRID - 1
        for (r in GRID - 1 downTo 0) {
            if (result[r][c] >= 0) {
                result[writeRow][c] = result[r][c]
                if (writeRow != r) result[r][c] = -1
                writeRow--
            }
        }
        for (r in writeRow downTo 0) {
            result[r][c] = Random.nextInt(CANDY_COLORS.size)
        }
    }
    return result
}

private fun swapAndProcess(board: List<IntArray>, r1: Int, c1: Int, r2: Int, c2: Int): Pair<List<IntArray>, Int> {
    val swapped = board.map { it.copyOf() }
    val tmp = swapped[r1][c1]
    swapped[r1][c1] = swapped[r2][c2]
    swapped[r2][c2] = tmp

    if (!hasMatches(swapped)) return board to 0

    var current = swapped
    var totalScore = 0
    var multiplier = 1
    while (hasMatches(current)) {
        val (cleared, count) = clearMatches(current)
        totalScore += count * 10 * multiplier
        multiplier++
        current = fillBoard(cleared)
    }
    return current to totalScore
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
        modifier = Modifier.fillMaxSize().background(Color(0xFF880E4F)).padding(32.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text("\uD83C\uDF6C eCrush", fontSize = 48.sp, color = Color.White)
        Spacer(Modifier.height(16.dp))
        Text("Match-3 Candy Game", fontSize = 18.sp, color = Color(0xFFF48FB1))
        Spacer(Modifier.height(32.dp))
        Button(
            onClick = onPlay,
            colors = ButtonDefaults.buttonColors(containerColor = Color(0xFFAD1457)),
            modifier = Modifier.width(200.dp).height(56.dp)
        ) { Text("Play", fontSize = 20.sp) }
        Spacer(Modifier.height(24.dp))
        Text("High Score: $highScore", fontSize = 20.sp, color = Color(0xFFF8BBD0))
    }
}

@Composable
private fun GameScreen(onGameOver: (Int) -> Unit, onBack: () -> Unit) {
    var state by remember { mutableStateOf(CrushState(board = initBoard())) }
    var showDialog by remember { mutableStateOf(false) }

    fun resetGame() {
        state = CrushState(board = initBoard(), canvasW = state.canvasW, canvasH = state.canvasH)
        showDialog = false
    }

    Column(modifier = Modifier.fillMaxSize().background(Color(0xFF1A1A2E))) {
        Row(
            modifier = Modifier.fillMaxWidth().padding(8.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            TextButton(onClick = onBack) { Text("\u2190 Back", color = Color.White) }
            Text("Score: ${state.score}", color = Color.White, fontSize = 18.sp)
            Text("Moves: ${state.movesLeft}", color = Color.White, fontSize = 18.sp)
        }

        Box(modifier = Modifier.weight(1f).fillMaxWidth(), contentAlignment = Alignment.Center) {
            GameCanvas(
                modifier = Modifier.fillMaxSize().padding(8.dp),
                onTap = { offset ->
                    if (state.gameOver) return@GameCanvas
                    val cellSize = minOf(state.canvasW, state.canvasH) / GRID
                    val offX = (state.canvasW - cellSize * GRID) / 2f
                    val offY = (state.canvasH - cellSize * GRID) / 2f
                    val col = ((offset.x - offX) / cellSize).toInt()
                    val row = ((offset.y - offY) / cellSize).toInt()
                    if (row !in 0 until GRID || col !in 0 until GRID) return@GameCanvas

                    val sel = state.selectedCell
                    if (sel != null) {
                        val (sr, sc) = sel
                        val adjacent = (kotlin.math.abs(sr - row) + kotlin.math.abs(sc - col)) == 1
                        if (adjacent) {
                            val (newBoard, addScore) = swapAndProcess(state.board, sr, sc, row, col)
                            val newMoves = state.movesLeft - 1
                            if (newMoves <= 0) {
                                onGameOver(state.score + addScore)
                                showDialog = true
                                state = state.copy(board = newBoard, score = state.score + addScore, movesLeft = 0, selectedCell = null, gameOver = true)
                            } else {
                                state = state.copy(board = newBoard, score = state.score + addScore, movesLeft = newMoves, selectedCell = null)
                            }
                        } else {
                            state = state.copy(selectedCell = row to col)
                        }
                    } else {
                        state = state.copy(selectedCell = row to col)
                    }
                },
                onDraw = {
                    state = state.copy(canvasW = size.width, canvasH = size.height)
                    val cellSize = minOf(size.width, size.height) / GRID
                    val offX = (size.width - cellSize * GRID) / 2f
                    val offY = (size.height - cellSize * GRID) / 2f

                    drawRect(Color(0xFF1A1A2E), Offset.Zero, size)

                    for (r in 0 until GRID) for (c in 0 until GRID) {
                        val x = offX + c * cellSize
                        val y = offY + r * cellSize
                        val isSelected = state.selectedCell == (r to c)

                        drawRect(
                            if (isSelected) Color.White.copy(alpha = 0.3f) else Color(0xFF2A2A4A),
                            Offset(x + 1, y + 1), Size(cellSize - 2, cellSize - 2)
                        )

                        val v = state.board[r][c]
                        if (v in CANDY_COLORS.indices) {
                            val padding = cellSize * 0.1f
                            drawRoundRect(
                                CANDY_COLORS[v],
                                Offset(x + padding, y + padding),
                                Size(cellSize - padding * 2, cellSize - padding * 2),
                                cornerRadius = androidx.compose.ui.geometry.CornerRadius(cellSize * 0.15f)
                            )
                            drawCircle(
                                Color.White.copy(alpha = 0.3f),
                                cellSize * 0.12f,
                                Offset(x + cellSize * 0.35f, y + cellSize * 0.35f)
                            )
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
