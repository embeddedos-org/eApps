package com.eos.eapps.core.ui.canvas

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.gestures.detectDragGestures
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.StrokeJoin
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.input.pointer.pointerInput

data class DrawPoint(val x: Float, val y: Float)
data class DrawStroke(
    val points: List<DrawPoint>,
    val color: Color = Color.Black,
    val width: Float = 4f
)

enum class DrawTool { PEN, LINE, RECTANGLE, CIRCLE, ERASER }

@Composable
fun DrawCanvas(
    strokes: List<DrawStroke>,
    currentStroke: DrawStroke?,
    onDragStart: (Offset) -> Unit,
    onDrag: (Offset) -> Unit,
    onDragEnd: () -> Unit,
    modifier: Modifier = Modifier.fillMaxSize()
) {
    Canvas(
        modifier = modifier.pointerInput(Unit) {
            detectDragGestures(
                onDragStart = { onDragStart(it) },
                onDrag = { change, _ ->
                    change.consume()
                    onDrag(change.position)
                },
                onDragEnd = { onDragEnd() }
            )
        }
    ) {
        strokes.forEach { stroke -> drawStroke(stroke) }
        currentStroke?.let { drawStroke(it) }
    }
}

private fun DrawScope.drawStroke(stroke: DrawStroke) {
    if (stroke.points.size < 2) return
    val path = Path().apply {
        moveTo(stroke.points.first().x, stroke.points.first().y)
        for (i in 1 until stroke.points.size) {
            lineTo(stroke.points[i].x, stroke.points[i].y)
        }
    }
    drawPath(
        path = path,
        color = stroke.color,
        style = Stroke(width = stroke.width, cap = StrokeCap.Round, join = StrokeJoin.Round)
    )
}
