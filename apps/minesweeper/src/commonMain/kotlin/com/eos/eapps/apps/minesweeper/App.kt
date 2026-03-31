package com.eos.eapps.apps.minesweeper

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
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

data class MineCell(val isMine: Boolean, var isRevealed: Boolean = false, var isFlagged: Boolean = false, var adjacentMines: Int = 0)

fun generateGrid(rows: Int, cols: Int, mines: Int): Array<Array<MineCell>> {
    val positions = (0 until rows * cols).shuffled().take(mines).toSet()
    val grid = Array(rows) { r -> Array(cols) { c -> MineCell(isMine = (r * cols + c) in positions) } }
    for (r in 0 until rows) for (c in 0 until cols) {
        var count = 0
        for (dr in -1..1) for (dc in -1..1) {
            val nr = r + dr; val nc = c + dc
            if (nr in 0 until rows && nc in 0 until cols && grid[nr][nc].isMine) count++
        }
        grid[r][c].adjacentMines = count
    }
    return grid
}

@Composable
fun AppContent() {
    val rows = 10; val cols = 10; val mineCount = 15
    var grid by remember { mutableStateOf(generateGrid(rows, cols, mineCount)) }
    var gameOver by remember { mutableStateOf(false) }
    var won by remember { mutableStateOf(false) }
    var tick by remember { mutableStateOf(0) }

    fun checkWin() {
        won = grid.flatten().all { it.isRevealed || it.isMine }
        if (won) gameOver = true
    }

    fun reveal(r: Int, c: Int) {
        if (gameOver || r !in 0 until rows || c !in 0 until cols) return
        val cell = grid[r][c]
        if (cell.isRevealed || cell.isFlagged) return
        cell.isRevealed = true
        if (cell.isMine) { gameOver = true; tick++; return }
        if (cell.adjacentMines == 0) {
            for (dr in -1..1) for (dc in -1..1) if (dr != 0 || dc != 0) reveal(r + dr, c + dc)
        }
        checkWin()
        tick++
    }

    fun reset() { grid = generateGrid(rows, cols, mineCount); gameOver = false; won = false; tick = 0 }

    Column(modifier = Modifier.fillMaxSize().padding(16.dp), horizontalAlignment = Alignment.CenterHorizontally) {
        Text("💣 Minesweeper", style = MaterialTheme.typography.headlineMedium)
        val _ = tick
        Text(
            if (won) "You Win! 🎉" else if (gameOver) "Game Over! 💥" else "Mines: $mineCount",
            style = MaterialTheme.typography.titleMedium,
        )
        Spacer(Modifier.height(8.dp))

        Box(modifier = Modifier.aspectRatio(1f).fillMaxWidth(0.9f)) {
            LazyVerticalGrid(columns = GridCells.Fixed(cols), modifier = Modifier.fillMaxSize(), userScrollEnabled = false) {
                items(rows * cols) { index ->
                    val r = index / cols; val c = index % cols
                    val cell = grid[r][c]
                    Box(
                        modifier = Modifier.aspectRatio(1f)
                            .background(
                                when {
                                    cell.isRevealed && cell.isMine -> Color.Red
                                    cell.isRevealed -> Color(0xFFE0E0E0)
                                    else -> Color(0xFFA0A0A0)
                                },
                            )
                            .border(0.5.dp, Color.Gray)
                            .clickable { reveal(r, c) },
                        contentAlignment = Alignment.Center,
                    ) {
                        when {
                            cell.isRevealed && cell.isMine -> Text("💣", fontSize = 14.sp)
                            cell.isRevealed && cell.adjacentMines > 0 -> Text(
                                "${cell.adjacentMines}", fontSize = 14.sp,
                                color = when (cell.adjacentMines) { 1 -> Color.Blue; 2 -> Color(0xFF388E3C); 3 -> Color.Red; else -> Color(0xFF7B1FA2) },
                            )
                            !cell.isRevealed && gameOver && cell.isMine -> Text("💣", fontSize = 14.sp)
                        }
                    }
                }
            }
        }

        Spacer(Modifier.height(12.dp))
        Button(onClick = { reset() }) { Text(if (gameOver) "Play Again" else "New Game") }
    }
}
package com.eos.eapps.apps.minesweeper

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
private enum class Difficulty(val cols: Int, val rows: Int, val mines: Int) {
    EASY(9, 9, 10), MEDIUM(16, 16, 40), HARD(16, 16, 60)
}

private enum class CellState { HIDDEN, REVEALED, FLAGGED }

private data class Cell(
    val hasMine: Boolean = false,
    val state: CellState = CellState.HIDDEN,
    val adjacentMines: Int = 0
)

private data class MineState(
    val grid: List<List<Cell>> = emptyList(),
    val cols: Int = 9,
    val rows: Int = 9,
    val totalMines: Int = 10,
    val flagCount: Int = 0,
    val gameOver: Boolean = false,
    val won: Boolean = false,
    val timer: Float = 0f,
    val started: Boolean = false
)

private val NUMBER_COLORS = listOf(
    Color.Transparent, Color.Blue, Color(0xFF388E3C), Color.Red,
    Color(0xFF1A237E), Color(0xFF880E4F), Color(0xFF00838F),
    Color.Black, Color.Gray
)

private fun createGrid(cols: Int, rows: Int, mines: Int, safeX: Int, safeY: Int): List<List<Cell>> {
    val cells = MutableList(rows) { MutableList(cols) { Cell() } }
    var placed = 0
    while (placed < mines) {
        val x = Random.nextInt(cols)
        val y = Random.nextInt(rows)
        if (!cells[y][x].hasMine && !(x == safeX && y == safeY)) {
            cells[y][x] = cells[y][x].copy(hasMine = true)
            placed++
        }
    }
    for (r in 0 until rows) {
        for (c in 0 until cols) {
            if (!cells[r][c].hasMine) {
                var count = 0
                for (dr in -1..1) for (dc in -1..1) {
                    val nr = r + dr; val nc = c + dc
                    if (nr in 0 until rows && nc in 0 until cols && cells[nr][nc].hasMine) count++
                }
                cells[r][c] = cells[r][c].copy(adjacentMines = count)
            }
        }
    }
    return cells
}

private fun floodReveal(grid: List<List<Cell>>, startX: Int, startY: Int): List<List<Cell>> {
    val rows = grid.size; val cols = grid[0].size
    val result = grid.map { it.toMutableList() }.toMutableList()
    val queue = ArrayDeque<Pair<Int, Int>>()
    queue.add(startX to startY)
    while (queue.isNotEmpty()) {
        val (x, y) = queue.removeFirst()
        if (y !in 0 until rows || x !in 0 until cols) continue
        if (result[y][x].state != CellState.HIDDEN) continue
        result[y][x] = result[y][x].copy(state = CellState.REVEALED)
        if (result[y][x].adjacentMines == 0 && !result[y][x].hasMine) {
            for (dr in -1..1) for (dc in -1..1) {
                if (dr != 0 || dc != 0) queue.add((x + dc) to (y + dr))
            }
        }
    }
    return result
}

private fun checkWin(grid: List<List<Cell>>): Boolean {
    return grid.all { row -> row.all { it.state == CellState.REVEALED || it.hasMine } }
}

@Composable
fun App() {
    AppTheme {
        var screen by remember { mutableStateOf(Screen.HOME) }
        var difficulty by remember { mutableStateOf(Difficulty.EASY) }
        when (screen) {
            Screen.HOME -> HomeScreen { diff -> difficulty = diff; screen = Screen.GAME }
            Screen.GAME -> GameScreen(difficulty) { screen = Screen.HOME }
        }
    }
}

@Composable
private fun HomeScreen(onPlay: (Difficulty) -> Unit) {
    Column(
        modifier = Modifier.fillMaxSize().background(Color(0xFF37474F)).padding(32.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text("\uD83D\uDCA3 Minesweeper", fontSize = 40.sp, color = Color.White)
        Spacer(Modifier.height(32.dp))
        Difficulty.entries.forEach { diff ->
            Button(
                onClick = { onPlay(diff) },
                modifier = Modifier.width(220.dp).height(52.dp).padding(vertical = 4.dp),
                colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF546E7A))
            ) { Text("${diff.name} (${diff.cols}\u00D7${diff.rows})", fontSize = 16.sp) }
        }
    }
}

@Composable
private fun GameScreen(difficulty: Difficulty, onBack: () -> Unit) {
    var state by remember {
        mutableStateOf(MineState(cols = difficulty.cols, rows = difficulty.rows, totalMines = difficulty.mines))
    }
    var showDialog by remember { mutableStateOf(false) }
    var flagMode by remember { mutableStateOf(false) }
    var canvasWidth by remember { mutableStateOf(1f) }
    var canvasHeight by remember { mutableStateOf(1f) }

    fun resetGame() {
        state = MineState(cols = difficulty.cols, rows = difficulty.rows, totalMines = difficulty.mines)
        showDialog = false
        flagMode = false
    }

    Column(modifier = Modifier.fillMaxSize().background(Color(0xFF263238))) {
        Row(
            modifier = Modifier.fillMaxWidth().padding(8.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            TextButton(onClick = onBack) { Text("\u2190 Back", color = Color.White) }
            Text("\uD83D\uDCA3 ${state.totalMines - state.flagCount}", color = Color.White, fontSize = 18.sp)
            Text("\u23F1 ${state.timer.toInt()}s", color = Color.White, fontSize = 18.sp)
        }

        Row(
            modifier = Modifier.fillMaxWidth().padding(horizontal = 8.dp),
            horizontalArrangement = Arrangement.Center
        ) {
            FilterChip(selected = !flagMode, onClick = { flagMode = false }, label = { Text("Reveal") })
            Spacer(Modifier.width(8.dp))
            FilterChip(selected = flagMode, onClick = { flagMode = true }, label = { Text("\uD83D\uDEA9 Flag") })
        }

        Box(modifier = Modifier.weight(1f).fillMaxWidth(), contentAlignment = Alignment.Center) {
            GameCanvas(
                modifier = Modifier.fillMaxSize().padding(8.dp),
                onUpdate = { dt ->
                    if (state.started && !state.gameOver && !state.won) {
                        state = state.copy(timer = state.timer + dt)
                    }
                },
                onTap = { offset ->
                    if (state.gameOver || state.won) return@GameCanvas
                    val cellSize = minOf(canvasWidth / state.cols, canvasHeight / state.rows)
                    val offX = (canvasWidth - cellSize * state.cols) / 2f
                    val offY = (canvasHeight - cellSize * state.rows) / 2f
                    val col = ((offset.x - offX) / cellSize).toInt()
                    val row = ((offset.y - offY) / cellSize).toInt()
                    if (col !in 0 until state.cols || row !in 0 until state.rows) return@GameCanvas

                    var s = state
                    if (!s.started) {
                        val grid = createGrid(s.cols, s.rows, s.totalMines, col, row)
                        s = s.copy(grid = grid, started = true)
                    }

                    val cell = s.grid[row][col]
                    if (flagMode) {
                        if (cell.state == CellState.HIDDEN) {
                            val newGrid = s.grid.map { it.toMutableList() }.toMutableList()
                            newGrid[row][col] = cell.copy(state = CellState.FLAGGED)
                            state = s.copy(grid = newGrid, flagCount = s.flagCount + 1)
                        } else if (cell.state == CellState.FLAGGED) {
                            val newGrid = s.grid.map { it.toMutableList() }.toMutableList()
                            newGrid[row][col] = cell.copy(state = CellState.HIDDEN)
                            state = s.copy(grid = newGrid, flagCount = s.flagCount - 1)
                        }
                    } else {
                        if (cell.state != CellState.HIDDEN) return@GameCanvas
                        if (cell.hasMine) {
                            val newGrid = s.grid.map { r -> r.map { it.copy(state = CellState.REVEALED) } }
                            state = s.copy(grid = newGrid, gameOver = true)
                            showDialog = true
                        } else {
                            val newGrid = floodReveal(s.grid, col, row)
                            val won = checkWin(newGrid)
                            state = s.copy(grid = newGrid, won = won)
                            if (won) showDialog = true
                        }
                    }
                },
                onDraw = {
                    canvasWidth = size.width
                    canvasHeight = size.height
                    val cellSize = minOf(size.width / state.cols, size.height / state.rows)
                    val offX = (size.width - cellSize * state.cols) / 2f
                    val offY = (size.height - cellSize * state.rows) / 2f

                    drawRect(Color(0xFF37474F), Offset.Zero, size)

                    for (r in 0 until state.rows) {
                        for (c in 0 until state.cols) {
                            val x = offX + c * cellSize
                            val y = offY + r * cellSize
                            val cell = state.grid.getOrNull(r)?.getOrNull(c) ?: Cell()

                            when (cell.state) {
                                CellState.HIDDEN -> {
                                    drawRect(Color(0xFF78909C), Offset(x + 1, y + 1), Size(cellSize - 2, cellSize - 2))
                                }
                                CellState.FLAGGED -> {
                                    drawRect(Color(0xFF78909C), Offset(x + 1, y + 1), Size(cellSize - 2, cellSize - 2))
                                    drawRect(Color.Red, Offset(x + cellSize * 0.3f, y + cellSize * 0.2f), Size(cellSize * 0.4f, cellSize * 0.6f))
                                }
                                CellState.REVEALED -> {
                                    drawRect(Color(0xFFCFD8DC), Offset(x + 1, y + 1), Size(cellSize - 2, cellSize - 2))
                                    if (cell.hasMine) {
                                        drawCircle(Color.Black, cellSize * 0.3f, Offset(x + cellSize / 2, y + cellSize / 2))
                                    } else if (cell.adjacentMines > 0) {
                                        val numColor = NUMBER_COLORS.getOrElse(cell.adjacentMines) { Color.Black }
                                        val dotSize = cellSize * 0.15f
                                        val cx = x + cellSize / 2
                                        val cy = y + cellSize / 2
                                        for (i in 0 until cell.adjacentMines.coerceAtMost(8)) {
                                            val angle = (i * 45f) * (kotlin.math.PI.toFloat() / 180f)
                                            val dx = kotlin.math.cos(angle) * cellSize * 0.25f
                                            val dy = kotlin.math.sin(angle) * cellSize * 0.25f
                                            drawCircle(numColor, dotSize, Offset(cx + dx, cy + dy))
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            )
        }
    }

    if (showDialog) {
        AlertDialog(
            onDismissRequest = {},
            title = { Text(if (state.won) "You Win!" else "Game Over") },
            text = { Text("Time: ${state.timer.toInt()}s") },
            confirmButton = { TextButton(onClick = { resetGame() }) { Text("Play Again") } },
            dismissButton = { TextButton(onClick = onBack) { Text("Home") } }
        )
    }
}
