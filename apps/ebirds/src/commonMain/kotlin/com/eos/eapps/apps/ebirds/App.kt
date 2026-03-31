package com.eos.eapps.apps.ebirds

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
import com.eos.eapps.core.ui.canvas.GameObject
import com.eos.eapps.core.ui.canvas.Physics2D
import com.eos.eapps.core.ui.theme.AppTheme
import kotlin.random.Random

private enum class Screen { HOME, GAME }

private data class Target(
    val obj: GameObject,
    val isPig: Boolean = false,
    val color: Color = Color.Gray,
    val health: Int = 1
)

private data class BirdsState(
    val bird: GameObject = GameObject(position = Vec2(80f, 400f), size = Vec2(30f, 30f)),
    val targets: List<Target> = emptyList(),
    val launched: Boolean = false,
    val dragging: Boolean = false,
    val dragStart: Vec2 = Vec2.Zero,
    val dragCurrent: Vec2 = Vec2.Zero,
    val birdsLeft: Int = 3,
    val score: Int = 0,
    val gameOver: Boolean = false,
    val levelComplete: Boolean = false,
    val slingshotPos: Vec2 = Vec2(100f, 420f),
    val canvasW: Float = 800f,
    val canvasH: Float = 600f
)

private fun createLevel(canvasW: Float, canvasH: Float): List<Target> {
    val ground = canvasH - 60f
    val targets = mutableListOf<Target>()
    val blockColors = listOf(Color(0xFF8D6E63), Color(0xFF795548), Color(0xFFA1887F))
    for (i in 0..3) {
        targets.add(Target(
            obj = GameObject(
                position = Vec2(canvasW * 0.6f + i * 50f, ground - 40f),
                size = Vec2(40f, 40f)
            ),
            color = blockColors[i % blockColors.size]
        ))
    }
    targets.add(Target(
        obj = GameObject(
            position = Vec2(canvasW * 0.6f + 25f, ground - 80f),
            size = Vec2(40f, 40f)
        ),
        color = blockColors[1]
    ))
    targets.add(Target(
        obj = GameObject(
            position = Vec2(canvasW * 0.6f + 75f, ground - 80f),
            size = Vec2(40f, 40f)
        ),
        color = blockColors[2]
    ))
    targets.add(Target(
        obj = GameObject(
            position = Vec2(canvasW * 0.65f + 20f, ground - 120f),
            size = Vec2(30f, 30f)
        ),
        isPig = true, color = Color(0xFF4CAF50)
    ))
    targets.add(Target(
        obj = GameObject(
            position = Vec2(canvasW * 0.75f, ground - 40f),
            size = Vec2(30f, 30f)
        ),
        isPig = true, color = Color(0xFF4CAF50)
    ))
    return targets
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
        modifier = Modifier.fillMaxSize().background(Color(0xFF03A9F4)).padding(32.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text("\uD83D\uDC26 eBirds", fontSize = 48.sp, color = Color.White)
        Spacer(Modifier.height(16.dp))
        Text("Slingshot Launcher", fontSize = 18.sp, color = Color(0xFFB3E5FC))
        Spacer(Modifier.height(32.dp))
        Button(
            onClick = onPlay,
            colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF0288D1)),
            modifier = Modifier.width(200.dp).height(56.dp)
        ) { Text("Play", fontSize = 20.sp) }
        Spacer(Modifier.height(24.dp))
        Text("High Score: $highScore", fontSize = 20.sp, color = Color(0xFFE1F5FE))
    }
}

@Composable
private fun GameScreen(onGameOver: (Int) -> Unit, onBack: () -> Unit) {
    var state by remember { mutableStateOf(BirdsState()) }
    var showDialog by remember { mutableStateOf(false) }
    var initialized by remember { mutableStateOf(false) }

    fun resetBird(s: BirdsState): BirdsState {
        return s.copy(
            bird = GameObject(position = s.slingshotPos - Vec2(15f, 15f), size = Vec2(30f, 30f)),
            launched = false, dragging = false
        )
    }

    fun resetGame() {
        val targets = createLevel(state.canvasW, state.canvasH)
        state = resetBird(BirdsState(targets = targets, canvasW = state.canvasW, canvasH = state.canvasH))
        showDialog = false
        initialized = true
    }

    Column(modifier = Modifier.fillMaxSize().background(Color(0xFF81D4FA))) {
        Row(
            modifier = Modifier.fillMaxWidth().padding(8.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            TextButton(onClick = onBack) { Text("\u2190 Back", color = Color.White) }
            Text("Score: ${state.score}  Birds: ${state.birdsLeft}", color = Color.White, fontSize = 18.sp)
        }

        Box(modifier = Modifier.weight(1f).fillMaxWidth()) {
            GameCanvas(
                modifier = Modifier.fillMaxSize(),
                onUpdate = { dt ->
                    if (!initialized) return@GameCanvas
                    if (!state.launched || state.gameOver) return@GameCanvas
                    val bird = state.bird.copy()
                    Physics2D.applyGravity(bird, 400f, dt)
                    Physics2D.move(bird, dt)

                    val newTargets = state.targets.toMutableList()
                    var addScore = 0
                    newTargets.forEachIndexed { i, target ->
                        if (target.obj.active && bird.overlaps(target.obj)) {
                            newTargets[i] = target.copy(
                                obj = target.obj.copy().apply { active = false },
                                health = 0
                            )
                            addScore += if (target.isPig) 500 else 100
                        }
                    }

                    val outOfBounds = bird.position.x > state.canvasW || bird.position.y > state.canvasH + 50f
                    if (outOfBounds) {
                        val newBirdsLeft = state.birdsLeft - 1
                        val pigsAlive = newTargets.any { it.isPig && it.obj.active }
                        if (!pigsAlive) {
                            state = state.copy(score = state.score + addScore, targets = newTargets, levelComplete = true, gameOver = true)
                            onGameOver(state.score + addScore)
                            showDialog = true
                        } else if (newBirdsLeft <= 0) {
                            state = state.copy(score = state.score + addScore, targets = newTargets, birdsLeft = 0, gameOver = true)
                            onGameOver(state.score + addScore)
                            showDialog = true
                        } else {
                            state = resetBird(state.copy(score = state.score + addScore, targets = newTargets, birdsLeft = newBirdsLeft))
                        }
                    } else {
                        state = state.copy(bird = bird, score = state.score + addScore, targets = newTargets)
                    }
                },
                onDragStart = { offset ->
                    if (state.launched || state.gameOver || !initialized) return@GameCanvas
                    val dist = kotlin.math.sqrt(
                        (offset.x - state.slingshotPos.x).let { it * it } +
                            (offset.y - state.slingshotPos.y).let { it * it }
                    )
                    if (dist < 60f) {
                        state = state.copy(dragging = true, dragStart = Vec2(offset.x, offset.y), dragCurrent = Vec2(offset.x, offset.y))
                    }
                },
                onDrag = { pos, _ ->
                    if (state.dragging) {
                        val maxDrag = 80f
                        val dx = pos.x - state.slingshotPos.x
                        val dy = pos.y - state.slingshotPos.y
                        val dist = kotlin.math.sqrt(dx * dx + dy * dy)
                        val factor = if (dist > maxDrag) maxDrag / dist else 1f
                        val clampedX = state.slingshotPos.x + dx * factor
                        val clampedY = state.slingshotPos.y + dy * factor
                        state = state.copy(
                            dragCurrent = Vec2(clampedX, clampedY),
                            bird = state.bird.copy().apply { position = Vec2(clampedX - 15f, clampedY - 15f) }
                        )
                    }
                },
                onDragEnd = {
                    if (state.dragging) {
                        val power = 6f
                        val vx = (state.slingshotPos.x - state.dragCurrent.x) * power
                        val vy = (state.slingshotPos.y - state.dragCurrent.y) * power
                        val bird = state.bird.copy()
                        bird.velocity = Vec2(vx, vy)
                        state = state.copy(bird = bird, launched = true, dragging = false)
                    }
                },
                onDraw = {
                    if (!initialized) {
                        state = state.copy(canvasW = size.width, canvasH = size.height)
                        resetGame()
                        return@GameCanvas
                    }

                    drawRect(Color(0xFF87CEEB), Offset.Zero, size)
                    drawRect(Color(0xFF4CAF50), Offset(0f, size.height - 60f), Size(size.width, 60f))

                    // Slingshot
                    drawRect(Color(0xFF5D4037), Offset(state.slingshotPos.x - 5, state.slingshotPos.y - 40), Size(10f, 50f))
                    drawRect(Color(0xFF5D4037), Offset(state.slingshotPos.x - 20, state.slingshotPos.y - 45), Size(40f, 8f))

                    if (state.dragging) {
                        drawLine(
                            Color(0xFF3E2723),
                            Offset(state.slingshotPos.x - 15, state.slingshotPos.y - 40),
                            Offset(state.dragCurrent.x, state.dragCurrent.y),
                            strokeWidth = 3f
                        )
                        drawLine(
                            Color(0xFF3E2723),
                            Offset(state.slingshotPos.x + 15, state.slingshotPos.y - 40),
                            Offset(state.dragCurrent.x, state.dragCurrent.y),
                            strokeWidth = 3f
                        )
                    }

                    state.targets.forEach { target ->
                        if (!target.obj.active) return@forEach
                        if (target.isPig) {
                            drawCircle(
                                target.color,
                                target.obj.size.x / 2,
                                Offset(target.obj.position.x + target.obj.size.x / 2, target.obj.position.y + target.obj.size.y / 2)
                            )
                            drawCircle(Color.White, 4f, Offset(target.obj.position.x + target.obj.size.x * 0.35f, target.obj.position.y + target.obj.size.y * 0.4f))
                            drawCircle(Color.White, 4f, Offset(target.obj.position.x + target.obj.size.x * 0.65f, target.obj.position.y + target.obj.size.y * 0.4f))
                        } else {
                            drawRect(
                                target.color,
                                Offset(target.obj.position.x, target.obj.position.y),
                                Size(target.obj.size.x, target.obj.size.y)
                            )
                        }
                    }

                    drawCircle(
                        Color.Red,
                        state.bird.size.x / 2,
                        Offset(state.bird.position.x + state.bird.size.x / 2, state.bird.position.y + state.bird.size.y / 2)
                    )

                    for (i in 0 until state.birdsLeft - 1) {
                        drawCircle(Color(0xFFE57373), 10f, Offset(30f + i * 25f, size.height - 30f))
                    }
                }
            )
        }
    }

    if (showDialog) {
        AlertDialog(
            onDismissRequest = {},
            title = { Text(if (state.levelComplete) "Level Complete!" else "Game Over") },
            text = { Text("Score: ${state.score}") },
            confirmButton = { TextButton(onClick = { resetGame() }) { Text("Play Again") } },
            dismissButton = { TextButton(onClick = onBack) { Text("Home") } }
        )
    }
}
