package com.eos.eapps.apps.eslice

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

data class Fruit(var obj: GameObject, val emoji: String, var sliced: Boolean = false, val isBomb: Boolean = false)

@Composable
fun AppContent() {
    val fruits = remember { mutableStateListOf<Fruit>() }
    var score by remember { mutableStateOf(0) }
    var lives by remember { mutableStateOf(3) }
    var spawnTimer by remember { mutableStateOf(0f) }
    val emojis = listOf("🍎", "🍊", "🍋", "🍉", "🍇", "🍓")

    fun reset() { fruits.clear(); score = 0; lives = 3; spawnTimer = 0f }

    Column(modifier = Modifier.fillMaxSize().padding(16.dp), horizontalAlignment = Alignment.CenterHorizontally) {
        Text("🍉 eSlice", style = MaterialTheme.typography.headlineMedium)
        Row(horizontalArrangement = Arrangement.spacedBy(16.dp)) {
            Text("Score: $score"); Text("Lives: ${"❤️".repeat(lives.coerceAtLeast(0))}")
        }
        Spacer(Modifier.height(8.dp))
        if (lives <= 0) {
            Text("Game Over!", style = MaterialTheme.typography.headlineLarge, color = MaterialTheme.colorScheme.error)
            Button(onClick = { reset() }) { Text("Play Again") }
        } else {
            Box(modifier = Modifier.fillMaxSize().weight(1f)) {
                GameCanvas(
                    onUpdate = { dt ->
                        spawnTimer += dt
                        if (spawnTimer > 1.2f) {
                            spawnTimer = 0f
                            val isBomb = Random.nextFloat() < 0.15f
                            fruits.add(Fruit(
                                obj = GameObject(
                                    position = Vec2(Random.nextFloat() * 600f + 50f, 700f),
                                    velocity = Vec2(Random.nextFloat() * 100f - 50f, -(Random.nextFloat() * 300f + 400f)),
                                    size = Vec2(40f, 40f),
                                    color = if (isBomb) Color.Black else Color.Red,
                                ),
                                emoji = if (isBomb) "💣" else emojis.random(),
                                isBomb = isBomb,
                            ))
                        }
                        fruits.forEach { f ->
                            Physics2D.applyGravity(f.obj, 500f, dt)
                            Physics2D.move(f.obj, dt)
                        }
                        val fallen = fruits.filter { it.obj.position.y > 800f && !it.sliced && !it.isBomb }
                        if (fallen.isNotEmpty()) lives -= fallen.size
                        fruits.removeAll { it.obj.position.y > 800f }
                    },
                    onDrag = { pos, _ ->
                        fruits.filter { !it.sliced }.forEach { f ->
                            if (f.obj.containsPoint(Vec2(pos.x, pos.y))) {
                                f.sliced = true
                                if (f.isBomb) lives = 0 else score += 10
                            }
                        }
                    },
                    onDraw = {
                        drawRect(Color(0xFFF5F5DC), Offset.Zero, size)
                        fruits.forEach { f ->
                            if (!f.sliced) {
                                drawCircle(f.obj.color, f.obj.size.x / 2, Offset(f.obj.center.x, f.obj.center.y))
                            }
                        }
                    },
                )
            }
        }
    }
}
package com.eos.eapps.apps.eslice

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
import com.eos.eapps.core.ui.canvas.Vec2
import com.eos.eapps.core.ui.theme.AppTheme
import kotlin.random.Random

private enum class Screen { HOME, GAME }

private data class Fruit(
    val position: Vec2,
    val velocity: Vec2,
    val radius: Float = 25f,
    val color: Color,
    val isBomb: Boolean = false,
    val sliced: Boolean = false,
    val active: Boolean = true
)

private data class SliceState(
    val fruits: List<Fruit> = emptyList(),
    val score: Int = 0,
    val combo: Int = 0,
    val lives: Int = 3,
    val gameOver: Boolean = false,
    val spawnTimer: Float = 0f,
    val spawnInterval: Float = 1.2f,
    val canvasW: Float = 400f,
    val canvasH: Float = 600f,
    val sliceTrail: List<Vec2> = emptyList(),
    val slicing: Boolean = false
)

private val FRUIT_COLORS = listOf(
    Color(0xFFE53935), Color(0xFFFFA726), Color(0xFFFFEB3B),
    Color(0xFF66BB6A), Color(0xFF42A5F5), Color(0xFFAB47BC)
)

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
        modifier = Modifier.fillMaxSize().background(Color(0xFF1A237E)).padding(32.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text("\uD83C\uDF4E eSlice", fontSize = 48.sp, color = Color.White)
        Spacer(Modifier.height(16.dp))
        Text("Swipe to Slice Fruits", fontSize = 18.sp, color = Color(0xFF9FA8DA))
        Spacer(Modifier.height(32.dp))
        Button(
            onClick = onPlay,
            colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF3F51B5)),
            modifier = Modifier.width(200.dp).height(56.dp)
        ) { Text("Play", fontSize = 20.sp) }
        Spacer(Modifier.height(24.dp))
        Text("High Score: $highScore", fontSize = 20.sp, color = Color(0xFFC5CAE9))
    }
}

@Composable
private fun GameScreen(onGameOver: (Int) -> Unit, onBack: () -> Unit) {
    var state by remember { mutableStateOf(SliceState()) }
    var showDialog by remember { mutableStateOf(false) }

    fun spawnFruit(s: SliceState): Fruit {
        val isBomb = Random.nextFloat() < 0.15f
        val x = Random.nextFloat() * (s.canvasW - 60f) + 30f
        val vx = (Random.nextFloat() - 0.5f) * 200f
        val vy = -(Random.nextFloat() * 300f + 400f)
        return Fruit(
            position = Vec2(x, s.canvasH + 30f),
            velocity = Vec2(vx, vy),
            color = if (isBomb) Color.DarkGray else FRUIT_COLORS.random(),
            isBomb = isBomb
        )
    }

    fun resetGame() {
        state = SliceState(canvasW = state.canvasW, canvasH = state.canvasH)
        showDialog = false
    }

    Column(modifier = Modifier.fillMaxSize().background(Color(0xFF0D1B2A))) {
        Row(
            modifier = Modifier.fillMaxWidth().padding(8.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            TextButton(onClick = onBack) { Text("\u2190 Back", color = Color.White) }
            Text("Score: ${state.score}", color = Color.White, fontSize = 18.sp)
            Row {
                repeat(state.lives) {
                    Text("\u2764", fontSize = 16.sp, color = Color.Red, modifier = Modifier.padding(2.dp))
                }
            }
        }

        Box(modifier = Modifier.weight(1f).fillMaxWidth()) {
            GameCanvas(
                modifier = Modifier.fillMaxSize(),
                onUpdate = { dt ->
                    if (state.gameOver) return@GameCanvas
                    var s = state

                    val newTimer = s.spawnTimer + dt
                    val fruits = s.fruits.toMutableList()
                    if (newTimer >= s.spawnInterval) {
                        val count = Random.nextInt(1, 4)
                        repeat(count) { fruits.add(spawnFruit(s)) }
                        s = s.copy(spawnTimer = 0f, spawnInterval = (s.spawnInterval - 0.01f).coerceAtLeast(0.4f))
                    } else {
                        s = s.copy(spawnTimer = newTimer)
                    }

                    var missedLives = 0
                    val updated = fruits.mapNotNull { f ->
                        if (!f.active || f.sliced) {
                            if (f.sliced) {
                                val newPos = Vec2(f.position.x + f.velocity.x * dt, f.position.y + f.velocity.y * dt + 300f * dt)
                                if (newPos.y > s.canvasH + 60f) null
                                else f.copy(position = newPos)
                            } else null
                        } else {
                            val newPos = Vec2(f.position.x + f.velocity.x * dt, f.position.y + f.velocity.y * dt)
                            val newVel = Vec2(f.velocity.x, f.velocity.y + 600f * dt)
                            if (newPos.y > s.canvasH + 60f && !f.isBomb) {
                                missedLives++
                                null
                            } else if (newPos.y > s.canvasH + 60f) {
                                null
                            } else {
                                f.copy(position = newPos, velocity = newVel)
                            }
                        }
                    }

                    val newLives = (s.lives - missedLives).coerceAtLeast(0)
                    if (newLives <= 0) {
                        onGameOver(s.score)
                        showDialog = true
                        state = s.copy(fruits = updated, lives = 0, gameOver = true)
                    } else {
                        state = s.copy(fruits = updated, lives = newLives)
                    }
                },
                onDragStart = { offset ->
                    if (state.gameOver) return@GameCanvas
                    state = state.copy(slicing = true, sliceTrail = listOf(Vec2(offset.x, offset.y)), combo = 0)
                },
                onDrag = { pos, _ ->
                    if (!state.slicing || state.gameOver) return@GameCanvas
                    val slicePos = Vec2(pos.x, pos.y)
                    val newTrail = (state.sliceTrail + slicePos).takeLast(15)
                    var addScore = 0
                    var hitBomb = false

                    val newFruits = state.fruits.map { fruit ->
                        if (fruit.sliced || !fruit.active) return@map fruit
                        val dist = (slicePos - fruit.position).length()
                        if (dist < fruit.radius + 15f) {
                            if (fruit.isBomb) { hitBomb = true; fruit }
                            else { addScore += 10; fruit.copy(sliced = true) }
                        } else fruit
                    }

                    if (hitBomb) {
                        onGameOver(state.score + addScore)
                        showDialog = true
                        state = state.copy(fruits = newFruits, gameOver = true, score = state.score + addScore, sliceTrail = newTrail)
                    } else {
                        state = state.copy(fruits = newFruits, sliceTrail = newTrail, score = state.score + addScore)
                    }
                },
                onDragEnd = {
                    state = state.copy(slicing = false, sliceTrail = emptyList())
                },
                onDraw = {
                    if (state.canvasW != size.width || state.canvasH != size.height) {
                        state = state.copy(canvasW = size.width, canvasH = size.height)
                    }
                    drawRect(Color(0xFF0D1B2A), Offset.Zero, size)

                    state.fruits.forEach { fruit ->
                        if (fruit.sliced) {
                            drawCircle(fruit.color.copy(alpha = 0.4f), fruit.radius * 0.6f, Offset(fruit.position.x - 10f, fruit.position.y))
                            drawCircle(fruit.color.copy(alpha = 0.4f), fruit.radius * 0.6f, Offset(fruit.position.x + 10f, fruit.position.y))
                        } else {
                            drawCircle(fruit.color, fruit.radius, Offset(fruit.position.x, fruit.position.y))
                            if (fruit.isBomb) {
                                drawCircle(Color.Red, fruit.radius * 0.4f, Offset(fruit.position.x, fruit.position.y))
                                drawRect(Color(0xFF5D4037), Offset(fruit.position.x - 2f, fruit.position.y - fruit.radius - 8f), Size(4f, 10f))
                            } else {
                                drawCircle(fruit.color.copy(alpha = 0.6f), fruit.radius * 0.4f, Offset(fruit.position.x - 5f, fruit.position.y - 5f))
                            }
                        }
                    }

                    if (state.sliceTrail.size >= 2) {
                        for (i in 1 until state.sliceTrail.size) {
                            val a = state.sliceTrail[i - 1]
                            val b = state.sliceTrail[i]
                            val alpha = i.toFloat() / state.sliceTrail.size
                            drawLine(Color.White.copy(alpha = alpha), Offset(a.x, a.y), Offset(b.x, b.y), strokeWidth = 4f)
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
