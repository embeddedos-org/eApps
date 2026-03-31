package com.eos.eapps.apps.snake

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

enum class Direction { UP, DOWN, LEFT, RIGHT }
data class Cell(val x: Int, val y: Int)

@Composable
fun AppContent() {
    val gridSize = 20
    var snake by remember { mutableStateOf(listOf(Cell(10, 10), Cell(9, 10), Cell(8, 10))) }
    var food by remember { mutableStateOf(Cell((0 until gridSize).random(), (0 until gridSize).random())) }
    var direction by remember { mutableStateOf(Direction.RIGHT) }
    var gameRunning by remember { mutableStateOf(true) }
    var score by remember { mutableStateOf(0) }

    fun reset() {
        snake = listOf(Cell(10, 10), Cell(9, 10), Cell(8, 10))
        food = Cell((0 until gridSize).random(), (0 until gridSize).random())
        direction = Direction.RIGHT
        gameRunning = true
        score = 0
    }

    LaunchedEffect(gameRunning) {
        while (gameRunning) {
            delay(150)
            val head = snake.first()
            val newHead = when (direction) {
                Direction.UP -> Cell(head.x, (head.y - 1 + gridSize) % gridSize)
                Direction.DOWN -> Cell(head.x, (head.y + 1) % gridSize)
                Direction.LEFT -> Cell((head.x - 1 + gridSize) % gridSize, head.y)
                Direction.RIGHT -> Cell((head.x + 1) % gridSize, head.y)
            }
            if (newHead in snake) { gameRunning = false; return@LaunchedEffect }
            val ate = newHead == food
            snake = listOf(newHead) + if (ate) snake else snake.dropLast(1)
            if (ate) {
                score++
                food = Cell((0 until gridSize).random(), (0 until gridSize).random())
            }
        }
    }

    Column(
        modifier = Modifier.fillMaxSize().padding(16.dp)
            .onKeyEvent { event ->
                if (event.type == KeyEventType.KeyDown) {
                    when (event.key) {
                        Key.DirectionUp, Key.W -> if (direction != Direction.DOWN) direction = Direction.UP
                        Key.DirectionDown, Key.S -> if (direction != Direction.UP) direction = Direction.DOWN
                        Key.DirectionLeft, Key.A -> if (direction != Direction.RIGHT) direction = Direction.LEFT
                        Key.DirectionRight, Key.D -> if (direction != Direction.LEFT) direction = Direction.RIGHT
                    }
                    true
                } else false
            }
            .focusable(),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Text("🐍 Snake", style = MaterialTheme.typography.headlineMedium)
        Text("Score: $score", style = MaterialTheme.typography.titleMedium)
        Spacer(Modifier.height(8.dp))

        Box(modifier = Modifier.aspectRatio(1f).fillMaxWidth(0.9f).background(Color(0xFF1B5E20))) {
            Canvas(modifier = Modifier.fillMaxSize()) {
                val cellW = size.width / gridSize
                val cellH = size.height / gridSize
                // Food
                drawRect(Color.Red, Offset(food.x * cellW, food.y * cellH), Size(cellW, cellH))
                // Snake
                snake.forEachIndexed { i, cell ->
                    drawRect(
                        if (i == 0) Color(0xFF4CAF50) else Color(0xFF66BB6A),
                        Offset(cell.x * cellW, cell.y * cellH),
                        Size(cellW - 1, cellH - 1),
                    )
                }
            }
        }

        Spacer(Modifier.height(8.dp))
        if (!gameRunning) {
            Text("Game Over!", style = MaterialTheme.typography.titleLarge, color = MaterialTheme.colorScheme.error)
            Spacer(Modifier.height(4.dp))
        }
        // Touch controls
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            Button(onClick = { if (direction != Direction.RIGHT) direction = Direction.LEFT }) { Text("◀") }
            Column {
                Button(onClick = { if (direction != Direction.DOWN) direction = Direction.UP }) { Text("▲") }
                Button(onClick = { if (direction != Direction.UP) direction = Direction.DOWN }) { Text("▼") }
            }
            Button(onClick = { if (direction != Direction.LEFT) direction = Direction.RIGHT }) { Text("▶") }
        }
        Spacer(Modifier.height(8.dp))
        if (!gameRunning) Button(onClick = { reset() }) { Text("Play Again") }
    }
}
package com.eos.eapps.apps.snake

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.eos.eapps.core.ui.canvas.GameCanvas
import com.eos.eapps.core.ui.canvas.Vec2
import com.eos.eapps.core.ui.theme.AppTheme
import kotlin.random.Random

private const val GRID_SIZE = 20
private const val MOVE_INTERVAL = 0.15f

private enum class Direction { UP, DOWN, LEFT, RIGHT }
private enum class Screen { HOME, GAME }

private data class SnakeState(
    val body: List<Vec2> = listOf(Vec2(10f, 10f)),
    val direction: Direction = Direction.RIGHT,
    val food: Vec2 = Vec2(15f, 10f),
    val score: Int = 0,
    val gameOver: Boolean = false,
    val moveTimer: Float = 0f
)

@Composable
fun App() {
    AppTheme {
        var screen by remember { mutableStateOf(Screen.HOME) }
        var highScore by remember { mutableStateOf(0) }

        when (screen) {
            Screen.HOME -> HomeScreen(
                highScore = highScore,
                onPlay = { screen = Screen.GAME }
            )
            Screen.GAME -> GameScreen(
                onGameOver = { score ->
                    if (score > highScore) highScore = score
                },
                onBack = { screen = Screen.HOME }
            )
        }
    }
}

@Composable
private fun HomeScreen(highScore: Int, onPlay: () -> Unit) {
    Column(
        modifier = Modifier.fillMaxSize().background(Color(0xFF1B5E20)).padding(32.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text("🐍 Snake", fontSize = 48.sp, color = Color.White)
        Spacer(Modifier.height(16.dp))
        Text("Classic Snake Game", fontSize = 18.sp, color = Color(0xFFA5D6A7))
        Spacer(Modifier.height(32.dp))
        Button(
            onClick = onPlay,
            colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF4CAF50)),
            modifier = Modifier.width(200.dp).height(56.dp)
        ) { Text("Play", fontSize = 20.sp) }
        Spacer(Modifier.height(24.dp))
        Text("High Score: $highScore", fontSize = 20.sp, color = Color(0xFFE8F5E9))
    }
}

@Composable
private fun GameScreen(onGameOver: (Int) -> Unit, onBack: () -> Unit) {
    var state by remember { mutableStateOf(SnakeState()) }
    var showGameOver by remember { mutableStateOf(false) }

    fun spawnFood(body: List<Vec2>): Vec2 {
        var pos: Vec2
        do {
            pos = Vec2(Random.nextInt(GRID_SIZE).toFloat(), Random.nextInt(GRID_SIZE).toFloat())
        } while (pos in body)
        return pos
    }

    fun resetGame() {
        state = SnakeState(food = Vec2(Random.nextInt(GRID_SIZE).toFloat(), Random.nextInt(GRID_SIZE).toFloat()))
        showGameOver = false
    }

    Column(modifier = Modifier.fillMaxSize().background(Color(0xFF1B5E20))) {
        Row(
            modifier = Modifier.fillMaxWidth().padding(8.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            TextButton(onClick = onBack) { Text("← Back", color = Color.White) }
            Text("Score: ${state.score}", color = Color.White, fontSize = 20.sp)
        }

        Box(modifier = Modifier.weight(1f).fillMaxWidth()) {
            GameCanvas(
                modifier = Modifier.fillMaxSize().padding(8.dp),
                onUpdate = { dt ->
                    if (state.gameOver) return@GameCanvas
                    val s = state
                    val newTimer = s.moveTimer + dt
                    if (newTimer < MOVE_INTERVAL) {
                        state = s.copy(moveTimer = newTimer)
                        return@GameCanvas
                    }

                    val head = s.body.first()
                    val newHead = when (s.direction) {
                        Direction.UP -> Vec2(head.x, head.y - 1f)
                        Direction.DOWN -> Vec2(head.x, head.y + 1f)
                        Direction.LEFT -> Vec2(head.x - 1f, head.y)
                        Direction.RIGHT -> Vec2(head.x + 1f, head.y)
                    }

                    if (newHead.x < 0 || newHead.x >= GRID_SIZE || newHead.y < 0 || newHead.y >= GRID_SIZE ||
                        newHead in s.body
                    ) {
                        state = s.copy(gameOver = true, moveTimer = 0f)
                        onGameOver(s.score)
                        showGameOver = true
                        return@GameCanvas
                    }

                    val ate = newHead.x.toInt() == s.food.x.toInt() && newHead.y.toInt() == s.food.y.toInt()
                    val newBody = listOf(newHead) + if (ate) s.body else s.body.dropLast(1)
                    val newFood = if (ate) spawnFood(newBody) else s.food
                    state = s.copy(
                        body = newBody,
                        food = newFood,
                        score = if (ate) s.score + 10 else s.score,
                        moveTimer = 0f
                    )
                },
                onTap = { offset ->
                    if (state.gameOver) return@GameCanvas
                    val s = state
                    val head = s.body.first()
                    val canvasW = 1f
                    val canvasH = 1f
                    val cellW = canvasW / GRID_SIZE
                    val cellH = canvasH / GRID_SIZE
                    val headCenterX = (head.x + 0.5f) * cellW
                    val headCenterY = (head.y + 0.5f) * cellH
                    val dx = offset.x - headCenterX
                    val dy = offset.y - headCenterY
                    // We'll use the tap relative to canvas center for direction
                },
                onDrag = { _, dragAmount ->
                    if (state.gameOver) return@GameCanvas
                    val s = state
                    val newDir = if (kotlin.math.abs(dragAmount.x) > kotlin.math.abs(dragAmount.y)) {
                        if (dragAmount.x > 0) Direction.RIGHT else Direction.LEFT
                    } else {
                        if (dragAmount.y > 0) Direction.DOWN else Direction.UP
                    }
                    val opposite = when (s.direction) {
                        Direction.UP -> Direction.DOWN
                        Direction.DOWN -> Direction.UP
                        Direction.LEFT -> Direction.RIGHT
                        Direction.RIGHT -> Direction.LEFT
                    }
                    if (newDir != opposite) {
                        state = s.copy(direction = newDir)
                    }
                },
                onDraw = {
                    val cellW = size.width / GRID_SIZE
                    val cellH = size.height / GRID_SIZE

                    drawRect(Color(0xFF2E7D32), Offset.Zero, size)

                    for (r in 0 until GRID_SIZE) {
                        for (c in 0 until GRID_SIZE) {
                            if ((r + c) % 2 == 0) {
                                drawRect(
                                    Color(0xFF388E3C),
                                    Offset(c * cellW, r * cellH),
                                    Size(cellW, cellH)
                                )
                            }
                        }
                    }

                    drawRect(
                        Color.Red,
                        Offset(state.food.x * cellW + 2, state.food.y * cellH + 2),
                        Size(cellW - 4, cellH - 4)
                    )

                    state.body.forEachIndexed { i, seg ->
                        val color = if (i == 0) Color(0xFF76FF03) else Color(0xFF64DD17)
                        drawRect(
                            color,
                            Offset(seg.x * cellW + 1, seg.y * cellH + 1),
                            Size(cellW - 2, cellH - 2)
                        )
                    }
                }
            )
        }

        Row(
            modifier = Modifier.fillMaxWidth().padding(16.dp),
            horizontalArrangement = Arrangement.SpaceEvenly
        ) {
            Button(onClick = {
                if (state.direction != Direction.DOWN) state = state.copy(direction = Direction.UP)
            }) { Text("▲") }
            Button(onClick = {
                if (state.direction != Direction.RIGHT) state = state.copy(direction = Direction.LEFT)
            }) { Text("◄") }
            Button(onClick = {
                if (state.direction != Direction.LEFT) state = state.copy(direction = Direction.RIGHT)
            }) { Text("►") }
            Button(onClick = {
                if (state.direction != Direction.UP) state = state.copy(direction = Direction.DOWN)
            }) { Text("▼") }
        }
    }

    if (showGameOver) {
        AlertDialog(
            onDismissRequest = {},
            title = { Text("Game Over") },
            text = { Text("Score: ${state.score}") },
            confirmButton = {
                TextButton(onClick = { resetGame() }) { Text("Play Again") }
            },
            dismissButton = {
                TextButton(onClick = onBack) { Text("Home") }
            }
        )
    }
}
