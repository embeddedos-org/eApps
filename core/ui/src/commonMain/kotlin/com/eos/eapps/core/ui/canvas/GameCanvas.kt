package com.eos.eapps.core.ui.canvas

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.gestures.detectDragGestures
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.input.pointer.pointerInput
import kotlin.math.sqrt

data class Vec2(val x: Float, val y: Float) {
    operator fun plus(other: Vec2) = Vec2(x + other.x, y + other.y)
    operator fun minus(other: Vec2) = Vec2(x - other.x, y - other.y)
    operator fun times(scalar: Float) = Vec2(x * scalar, y * scalar)
    fun length() = sqrt(x * x + y * y)
    fun distanceTo(other: Vec2) = (this - other).length()
    fun normalized(): Vec2 {
        val l = length()
        return if (l > 0f) Vec2(x / l, y / l) else Zero
    }

    companion object {
        val Zero = Vec2(0f, 0f)
        val Up = Vec2(0f, -1f)
        val Down = Vec2(0f, 1f)
        val Left = Vec2(-1f, 0f)
        val Right = Vec2(1f, 0f)
    }
}

open class GameObject(
    var position: Vec2 = Vec2.Zero,
    var velocity: Vec2 = Vec2.Zero,
    var size: Vec2 = Vec2(32f, 32f),
    var color: Color = Color.White,
    var active: Boolean = true,
) {
    val left get() = position.x
    val right get() = position.x + size.x
    val top get() = position.y
    val bottom get() = position.y + size.y
    val center get() = Vec2(position.x + size.x / 2, position.y + size.y / 2)

    open fun update(deltaTime: Float) {
        if (active) {
            position = position + velocity * deltaTime
        }
    }

    open fun DrawScope.render() {
        if (active) {
            drawRect(color, Offset(position.x, position.y), Size(size.x, size.y))
        }
    }

    fun intersects(other: GameObject): Boolean =
        active && other.active &&
            left < other.right && right > other.left &&
            top < other.bottom && bottom > other.top

    fun containsPoint(point: Vec2): Boolean =
        point.x in position.x..(position.x + size.x) &&
            point.y in position.y..(position.y + size.y)
}

object Physics2D {
    const val DEFAULT_GRAVITY = 980f

    fun applyGravity(obj: GameObject, gravity: Float = DEFAULT_GRAVITY, dt: Float) {
        obj.velocity = Vec2(obj.velocity.x, obj.velocity.y + gravity * dt)
    }

    fun applyFriction(obj: GameObject, friction: Float, dt: Float) {
        val speed = obj.velocity.length()
        if (speed > 0) {
            val newSpeed = (speed - friction * dt).coerceAtLeast(0f)
            obj.velocity = obj.velocity.normalized() * newSpeed
        }
    }

    fun move(obj: GameObject, dt: Float) {
        obj.position = obj.position + obj.velocity * dt
    }

    fun clampToBounds(obj: GameObject, minX: Float, minY: Float, maxX: Float, maxY: Float) {
        val x = obj.position.x.coerceIn(minX, maxX - obj.size.x)
        val y = obj.position.y.coerceIn(minY, maxY - obj.size.y)
        obj.position = Vec2(x, y)
    }

    fun circleCollision(a: Vec2, radiusA: Float, b: Vec2, radiusB: Float): Boolean =
        a.distanceTo(b) < radiusA + radiusB
}

@Composable
fun GameCanvas(
    modifier: Modifier = Modifier.fillMaxSize(),
    onUpdate: (deltaTime: Float) -> Unit = {},
    onTap: (Offset) -> Unit = {},
    onDragStart: (Offset) -> Unit = {},
    onDrag: (change: Offset, dragAmount: Offset) -> Unit = { _, _ -> },
    onDragEnd: () -> Unit = {},
    onDraw: DrawScope.() -> Unit,
) {
    var lastFrameTime by remember { mutableStateOf(0L) }

    LaunchedEffect(Unit) {
        while (true) {
            withFrameNanos { frameTime ->
                val dt = if (lastFrameTime > 0L)
                    ((frameTime - lastFrameTime) / 1_000_000_000f).coerceIn(0f, 0.05f)
                else 0.016f
                lastFrameTime = frameTime
                onUpdate(dt)
            }
        }
    }

    Canvas(
        modifier = modifier
            .pointerInput(Unit) {
                detectTapGestures { offset -> onTap(offset) }
            }
            .pointerInput(Unit) {
                detectDragGestures(
                    onDragStart = { onDragStart(it) },
                    onDrag = { change, dragAmount ->
                        change.consume()
                        onDrag(change.position, Offset(dragAmount.x, dragAmount.y))
                    },
                    onDragEnd = { onDragEnd() },
                )
            },
    ) {
        onDraw()
    }
}
