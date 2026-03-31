package com.eos.eapps.apps.epaint

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.gestures.detectDragGestures
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.unit.dp

data class DrawLine(val start: Offset, val end: Offset, val color: Color, val width: Float)

@Composable
fun AppContent() {
    var lines by remember { mutableStateOf(listOf<DrawLine>()) }
    var currentColor by remember { mutableStateOf(Color.Black) }
    var brushSize by remember { mutableStateOf(4f) }
    val colors = listOf(Color.Black, Color.Red, Color.Blue, Color.Green, Color(0xFFFF9800), Color(0xFF9C27B0), Color.White)

    Column(modifier = Modifier.fillMaxSize().padding(8.dp)) {
        Text("🎨 ePaint", style = MaterialTheme.typography.headlineMedium, modifier = Modifier.align(Alignment.CenterHorizontally))
        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(4.dp), verticalAlignment = Alignment.CenterVertically) {
            colors.forEach { c ->
                Button(onClick = { currentColor = c }, modifier = Modifier.size(36.dp), colors = ButtonDefaults.buttonColors(containerColor = c), contentPadding = PaddingValues(0.dp)) {}
            }
            Spacer(Modifier.weight(1f))
            Slider(value = brushSize, onValueChange = { brushSize = it }, valueRange = 1f..20f, modifier = Modifier.width(120.dp))
            Button(onClick = { lines = emptyList() }) { Text("Clear") }
        }
        Canvas(
            modifier = Modifier.fillMaxSize().background(Color.White)
                .pointerInput(Unit) {
                    detectDragGestures { change, _ ->
                        change.consume()
                        val prev = change.previousPosition
                        lines = lines + DrawLine(prev, change.position, currentColor, brushSize)
                    }
                },
        ) {
            lines.forEach { line -> drawLine(line.color, line.start, line.end, strokeWidth = line.width, cap = StrokeCap.Round) }
        }
    }
}
package com.eos.eapps.apps.epaint

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import com.eos.eapps.core.ui.canvas.DrawCanvas
import com.eos.eapps.core.ui.canvas.DrawPoint
import com.eos.eapps.core.ui.canvas.DrawStroke
import com.eos.eapps.core.ui.canvas.DrawTool
import com.eos.eapps.core.ui.theme.AppTheme

private val presetColors = listOf(
    Color.Black, Color.White, Color.Red, Color(0xFFE91E63),
    Color(0xFF9C27B0), Color(0xFF3F51B5), Color(0xFF2196F3), Color(0xFF00BCD4),
    Color(0xFF4CAF50), Color(0xFF8BC34A), Color(0xFFFFEB3B), Color(0xFFFF9800)
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun App() {
    AppTheme {
        val strokes = remember { mutableStateListOf<DrawStroke>() }
        val undoneStrokes = remember { mutableStateListOf<DrawStroke>() }
        var currentStroke by remember { mutableStateOf<DrawStroke?>(null) }
        var selectedTool by remember { mutableStateOf(DrawTool.PEN) }
        var selectedColor by remember { mutableStateOf(Color.Black) }
        var strokeWidth by remember { mutableStateOf(4f) }

        val drawColor = if (selectedTool == DrawTool.ERASER) Color.White else selectedColor

        Scaffold(
            topBar = {
                TopAppBar(
                    title = { Text("ePaint") },
                    actions = {
                        IconButton(
                            onClick = {
                                if (strokes.isNotEmpty()) {
                                    undoneStrokes.add(strokes.removeLast())
                                }
                            },
                            enabled = strokes.isNotEmpty()
                        ) {
                            Icon(Icons.Default.Undo, contentDescription = "Undo")
                        }
                        IconButton(
                            onClick = {
                                if (undoneStrokes.isNotEmpty()) {
                                    strokes.add(undoneStrokes.removeLast())
                                }
                            },
                            enabled = undoneStrokes.isNotEmpty()
                        ) {
                            Icon(Icons.Default.Redo, contentDescription = "Redo")
                        }
                        IconButton(onClick = { strokes.clear(); undoneStrokes.clear() }) {
                            Icon(Icons.Default.Delete, contentDescription = "Clear")
                        }
                    }
                )
            },
            bottomBar = {
                Surface(tonalElevation = 3.dp) {
                    Column(modifier = Modifier.fillMaxWidth().padding(8.dp)) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceEvenly,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            DrawTool.entries.forEach { tool ->
                                FilterChip(
                                    selected = selectedTool == tool,
                                    onClick = { selectedTool = tool },
                                    label = {
                                        Text(
                                            when (tool) {
                                                DrawTool.PEN -> "Pen"
                                                DrawTool.LINE -> "Line"
                                                DrawTool.RECTANGLE -> "Rect"
                                                DrawTool.CIRCLE -> "Circle"
                                                DrawTool.ERASER -> "Eraser"
                                            }
                                        )
                                    },
                                    leadingIcon = {
                                        Icon(
                                            when (tool) {
                                                DrawTool.PEN -> Icons.Default.Edit
                                                DrawTool.LINE -> Icons.Default.HorizontalRule
                                                DrawTool.RECTANGLE -> Icons.Default.CropSquare
                                                DrawTool.CIRCLE -> Icons.Default.Circle
                                                DrawTool.ERASER -> Icons.Default.AutoFixOff
                                            },
                                            contentDescription = null,
                                            modifier = Modifier.size(16.dp)
                                        )
                                    }
                                )
                            }
                        }

                        Spacer(Modifier.height(8.dp))

                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceEvenly
                        ) {
                            presetColors.forEach { color ->
                                Box(
                                    modifier = Modifier
                                        .size(28.dp)
                                        .clip(CircleShape)
                                        .background(color)
                                        .border(
                                            width = if (selectedColor == color) 3.dp else 1.dp,
                                            color = if (selectedColor == color) MaterialTheme.colorScheme.primary
                                            else Color.Gray,
                                            shape = CircleShape
                                        )
                                        .clickable { selectedColor = color }
                                )
                            }
                        }

                        Spacer(Modifier.height(4.dp))

                        Row(
                            modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text("Width", style = MaterialTheme.typography.labelSmall)
                            Spacer(Modifier.width(8.dp))
                            Slider(
                                value = strokeWidth,
                                onValueChange = { strokeWidth = it },
                                valueRange = 1f..20f,
                                modifier = Modifier.weight(1f)
                            )
                            Text("${strokeWidth.toInt()}px", style = MaterialTheme.typography.labelSmall)
                        }
                    }
                }
            }
        ) { padding ->
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding)
                    .background(Color.White)
            ) {
                DrawCanvas(
                    strokes = strokes,
                    currentStroke = currentStroke,
                    onDragStart = { offset ->
                        currentStroke = DrawStroke(
                            points = listOf(DrawPoint(offset.x, offset.y)),
                            color = drawColor,
                            width = strokeWidth
                        )
                    },
                    onDrag = { offset ->
                        currentStroke?.let { stroke ->
                            currentStroke = stroke.copy(
                                points = stroke.points + DrawPoint(offset.x, offset.y)
                            )
                        }
                    },
                    onDragEnd = {
                        currentStroke?.let { stroke ->
                            strokes.add(stroke)
                            undoneStrokes.clear()
                        }
                        currentStroke = null
                    }
                )
            }
        }
    }
}
