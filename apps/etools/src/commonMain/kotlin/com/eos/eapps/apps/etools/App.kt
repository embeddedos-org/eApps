package com.eos.eapps.apps.etools

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

data class ConversionCategory(val name: String, val units: List<String>, val factors: List<Double>)

val CATEGORIES = listOf(
    ConversionCategory("Length", listOf("Meters", "Feet", "Inches", "Centimeters", "Kilometers", "Miles"),
        listOf(1.0, 0.3048, 0.0254, 0.01, 1000.0, 1609.344)),
    ConversionCategory("Weight", listOf("Kilograms", "Pounds", "Ounces", "Grams", "Tons"),
        listOf(1.0, 0.453592, 0.0283495, 0.001, 907.185)),
    ConversionCategory("Temperature", listOf("Celsius", "Fahrenheit", "Kelvin"), listOf()),
)

@Composable
fun AppContent() {
    var categoryIdx by remember { mutableStateOf(0) }
    var fromIdx by remember { mutableStateOf(0) }
    var toIdx by remember { mutableStateOf(1) }
    var input by remember { mutableStateOf("1") }

    val cat = CATEGORIES[categoryIdx]
    val result = remember(input, categoryIdx, fromIdx, toIdx) {
        val value = input.toDoubleOrNull() ?: return@remember ""
        if (cat.name == "Temperature") {
            val celsius = when (fromIdx) { 1 -> (value - 32) * 5 / 9; 2 -> value - 273.15; else -> value }
            val out = when (toIdx) { 1 -> celsius * 9 / 5 + 32; 2 -> celsius + 273.15; else -> celsius }
            "%.4f".format(out)
        } else {
            val meters = value * cat.factors[fromIdx]
            val out = meters / cat.factors[toIdx]
            "%.6f".format(out)
        }
    }

    Column(modifier = Modifier.fillMaxSize().padding(16.dp), horizontalAlignment = Alignment.CenterHorizontally) {
        Text("🛠️ eTools", style = MaterialTheme.typography.headlineMedium)
        Spacer(Modifier.height(16.dp))
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            CATEGORIES.forEachIndexed { i, c ->
                FilterChip(selected = categoryIdx == i, onClick = { categoryIdx = i; fromIdx = 0; toIdx = 1 }, label = { Text(c.name) })
            }
        }
        Spacer(Modifier.height(16.dp))
        OutlinedTextField(value = input, onValueChange = { input = it }, label = { Text("Value") }, modifier = Modifier.fillMaxWidth(), singleLine = true)
        Spacer(Modifier.height(8.dp))
        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            Column(modifier = Modifier.weight(1f)) {
                Text("From:", style = MaterialTheme.typography.labelMedium)
                cat.units.forEachIndexed { i, u ->
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        RadioButton(selected = fromIdx == i, onClick = { fromIdx = i })
                        Text(u, style = MaterialTheme.typography.bodyMedium)
                    }
                }
            }
            Column(modifier = Modifier.weight(1f)) {
                Text("To:", style = MaterialTheme.typography.labelMedium)
                cat.units.forEachIndexed { i, u ->
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        RadioButton(selected = toIdx == i, onClick = { toIdx = i })
                        Text(u, style = MaterialTheme.typography.bodyMedium)
                    }
                }
            }
        }
        Spacer(Modifier.height(16.dp))
        Card(modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(16.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                Text("Result", style = MaterialTheme.typography.labelLarge)
                Text(result, style = MaterialTheme.typography.headlineSmall)
                Text("${cat.units.getOrElse(toIdx) { "" }}", style = MaterialTheme.typography.bodyMedium)
            }
        }
        Spacer(Modifier.height(8.dp))
        Button(onClick = { val t = fromIdx; fromIdx = toIdx; toIdx = t }) { Text("⇄ Swap") }
    }
}
package com.eos.eapps.apps.etools

import androidx.compose.animation.core.*
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
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
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.drawscope.rotate
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.drawText
import androidx.compose.ui.text.rememberTextMeasurer
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.eos.eapps.core.ui.theme.AppTheme
import kotlin.math.PI
import kotlin.math.cos
import kotlin.math.sin

enum class ToolTab(val label: String) { CONVERTER("Converter"), COMPASS("Compass"), LEVEL("Level"), RULER("Ruler") }

@Composable
fun App() {
    AppTheme {
        var selectedTab by remember { mutableStateOf(ToolTab.CONVERTER) }

        Scaffold(
            bottomBar = {
                NavigationBar {
                    ToolTab.entries.forEach { tab ->
                        NavigationBarItem(
                            icon = {
                                Icon(
                                    when (tab) {
                                        ToolTab.CONVERTER -> Icons.Default.Build
                                        ToolTab.COMPASS -> Icons.Default.Explore
                                        ToolTab.LEVEL -> Icons.Default.Straighten
                                        ToolTab.RULER -> Icons.Default.Square
                                    },
                                    contentDescription = tab.label
                                )
                            },
                            label = { Text(tab.label) },
                            selected = selectedTab == tab,
                            onClick = { selectedTab = tab }
                        )
                    }
                }
            }
        ) { padding ->
            Box(modifier = Modifier.fillMaxSize().padding(padding)) {
                when (selectedTab) {
                    ToolTab.CONVERTER -> ConverterTool()
                    ToolTab.COMPASS -> CompassTool()
                    ToolTab.LEVEL -> LevelTool()
                    ToolTab.RULER -> RulerTool()
                }
            }
        }
    }
}

@Composable
private fun ConverterTool() {
    var inputValue by remember { mutableStateOf("1") }
    var fromUnit by remember { mutableStateOf("Meters") }
    var toUnit by remember { mutableStateOf("Feet") }
    val units = listOf("Meters", "Feet", "Inches", "Centimeters", "Kilometers", "Miles", "Yards")
    val toMeters = mapOf(
        "Meters" to 1.0, "Feet" to 0.3048, "Inches" to 0.0254,
        "Centimeters" to 0.01, "Kilometers" to 1000.0, "Miles" to 1609.344, "Yards" to 0.9144
    )
    val input = inputValue.toDoubleOrNull() ?: 0.0
    val meters = input * (toMeters[fromUnit] ?: 1.0)
    val result = meters / (toMeters[toUnit] ?: 1.0)

    Column(
        modifier = Modifier.fillMaxSize().padding(24.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text("Unit Converter", style = MaterialTheme.typography.headlineSmall)
        OutlinedTextField(value = inputValue, onValueChange = { inputValue = it }, label = { Text("Value") }, singleLine = true, modifier = Modifier.fillMaxWidth())
        var fromExp by remember { mutableStateOf(false) }
        Box(Modifier.fillMaxWidth()) {
            OutlinedTextField(value = fromUnit, onValueChange = {}, readOnly = true, label = { Text("From") }, modifier = Modifier.fillMaxWidth())
            DropdownMenu(expanded = fromExp, onDismissRequest = { fromExp = false }) {
                units.forEach { u -> DropdownMenuItem(text = { Text(u) }, onClick = { fromUnit = u; fromExp = false }) }
            }
            Box(Modifier.matchParentSize().padding(end = 48.dp)) {
                IconButton(onClick = { fromExp = true }, modifier = Modifier.align(Alignment.CenterEnd)) {
                    Icon(Icons.Default.ArrowDropDown, null)
                }
            }
        }
        var toExp by remember { mutableStateOf(false) }
        Box(Modifier.fillMaxWidth()) {
            OutlinedTextField(value = toUnit, onValueChange = {}, readOnly = true, label = { Text("To") }, modifier = Modifier.fillMaxWidth())
            DropdownMenu(expanded = toExp, onDismissRequest = { toExp = false }) {
                units.forEach { u -> DropdownMenuItem(text = { Text(u) }, onClick = { toUnit = u; toExp = false }) }
            }
            Box(Modifier.matchParentSize().padding(end = 48.dp)) {
                IconButton(onClick = { toExp = true }, modifier = Modifier.align(Alignment.CenterEnd)) {
                    Icon(Icons.Default.ArrowDropDown, null)
                }
            }
        }
        Card(modifier = Modifier.fillMaxWidth(), colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.primaryContainer)) {
            Text(
                "%.4g $toUnit".format(result),
                style = MaterialTheme.typography.headlineMedium,
                modifier = Modifier.padding(24.dp).fillMaxWidth()
            )
        }
    }
}

@Composable
private fun CompassTool() {
    val heading by remember { mutableStateOf(0f) }
    val animatedHeading by animateFloatAsState(targetValue = heading, animationSpec = tween(500))
    val textMeasurer = rememberTextMeasurer()

    Column(
        modifier = Modifier.fillMaxSize(),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text("Compass", style = MaterialTheme.typography.headlineSmall)
        Spacer(Modifier.height(16.dp))
        Text("${animatedHeading.toInt()}°", style = MaterialTheme.typography.displayMedium, color = MaterialTheme.colorScheme.primary)
        Spacer(Modifier.height(16.dp))

        Canvas(modifier = Modifier.size(280.dp)) {
            val cx = size.width / 2
            val cy = size.height / 2
            val radius = size.minDimension / 2 - 20f

            drawCircle(color = Color.LightGray, radius = radius, center = Offset(cx, cy), style = Stroke(4f))
            drawCircle(color = Color.DarkGray, radius = radius - 30f, center = Offset(cx, cy), style = Stroke(1f))

            val directions = listOf("N" to 0f, "E" to 90f, "S" to 180f, "W" to 270f)
            directions.forEach { (label, angle) ->
                val rad = (angle - 90) * PI.toFloat() / 180f
                val textResult = textMeasurer.measure(label, TextStyle(fontSize = 18.sp, color = if (label == "N") Color.Red else Color.DarkGray))
                val tx = cx + (radius - 50f) * cos(rad) - textResult.size.width / 2
                val ty = cy + (radius - 50f) * sin(rad) - textResult.size.height / 2
                drawText(textResult, topLeft = Offset(tx, ty))
            }

            for (i in 0 until 360 step 10) {
                val rad = (i - 90) * PI.toFloat() / 180f
                val inner = if (i % 30 == 0) radius - 25f else radius - 15f
                drawLine(
                    color = if (i % 30 == 0) Color.DarkGray else Color.Gray,
                    start = Offset(cx + inner * cos(rad), cy + inner * sin(rad)),
                    end = Offset(cx + radius * cos(rad), cy + radius * sin(rad)),
                    strokeWidth = if (i % 30 == 0) 3f else 1f
                )
            }

            rotate(-animatedHeading, pivot = Offset(cx, cy)) {
                drawLine(Color.Red, Offset(cx, cy - radius + 60f), Offset(cx, cy - 10f), strokeWidth = 4f, cap = StrokeCap.Round)
                drawLine(Color.Gray, Offset(cx, cy + 10f), Offset(cx, cy + radius - 60f), strokeWidth = 4f, cap = StrokeCap.Round)
            }
            drawCircle(Color.DarkGray, 8f, Offset(cx, cy))
        }
    }
}

@Composable
private fun LevelTool() {
    val offsetX by remember { mutableStateOf(0f) }
    val offsetY by remember { mutableStateOf(0f) }
    val animX by animateFloatAsState(targetValue = offsetX, animationSpec = spring())
    val animY by animateFloatAsState(targetValue = offsetY, animationSpec = spring())

    Column(
        modifier = Modifier.fillMaxSize(),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text("Spirit Level", style = MaterialTheme.typography.headlineSmall)
        Spacer(Modifier.height(8.dp))
        Text("Tilt: X=${animX.toInt()}° Y=${animY.toInt()}°", style = MaterialTheme.typography.bodyMedium)
        Spacer(Modifier.height(24.dp))

        Canvas(modifier = Modifier.size(280.dp)) {
            val cx = size.width / 2
            val cy = size.height / 2

            drawCircle(Color(0xFFE0E0E0), radius = 130f, center = Offset(cx, cy))
            drawCircle(Color(0xFFBDBDBD), radius = 130f, center = Offset(cx, cy), style = Stroke(2f))
            drawCircle(Color(0xFFE0E0E0), radius = 60f, center = Offset(cx, cy), style = Stroke(1f))
            drawCircle(Color(0xFFE0E0E0), radius = 30f, center = Offset(cx, cy), style = Stroke(1f))
            drawLine(Color(0xFFBDBDBD), Offset(cx - 130f, cy), Offset(cx + 130f, cy), strokeWidth = 1f)
            drawLine(Color(0xFFBDBDBD), Offset(cx, cy - 130f), Offset(cx, cy + 130f), strokeWidth = 1f)

            val bubbleX = cx + animX * 2f
            val bubbleY = cy + animY * 2f
            val isLevel = kotlin.math.abs(animX) < 2f && kotlin.math.abs(animY) < 2f
            drawCircle(
                color = if (isLevel) Color(0xFF4CAF50) else Color(0xFFFF9800),
                radius = 20f,
                center = Offset(bubbleX, bubbleY)
            )
            drawCircle(
                color = if (isLevel) Color(0xFF388E3C) else Color(0xFFE65100),
                radius = 20f,
                center = Offset(bubbleX, bubbleY),
                style = Stroke(2f)
            )
        }

        Spacer(Modifier.height(16.dp))
        val isLevel = kotlin.math.abs(animX) < 2f && kotlin.math.abs(animY) < 2f
        Text(
            if (isLevel) "LEVEL ✓" else "NOT LEVEL",
            style = MaterialTheme.typography.titleLarge,
            color = if (isLevel) Color(0xFF4CAF50) else Color(0xFFFF9800)
        )
    }
}

@Composable
private fun RulerTool() {
    val density = LocalDensity.current
    Column(
        modifier = Modifier.fillMaxSize(),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text("Ruler", style = MaterialTheme.typography.headlineSmall, modifier = Modifier.padding(16.dp))
        val textMeasurer = rememberTextMeasurer()

        Canvas(modifier = Modifier.fillMaxWidth().height(120.dp).padding(horizontal = 16.dp)) {
            val w = size.width
            val pxPerCm = with(density) { 10.dp.toPx() } * 2.54f
            val cmCount = (w / pxPerCm).toInt()

            drawLine(Color.DarkGray, Offset(0f, 80f), Offset(w, 80f), strokeWidth = 2f)

            for (i in 0..cmCount) {
                val x = i * pxPerCm
                drawLine(Color.DarkGray, Offset(x, 40f), Offset(x, 80f), strokeWidth = 2f)
                val textResult = textMeasurer.measure("$i", TextStyle(fontSize = 12.sp, color = Color.DarkGray))
                drawText(textResult, topLeft = Offset(x - textResult.size.width / 2, 22f))

                for (mm in 1..9) {
                    val mx = x + mm * pxPerCm / 10f
                    if (mx <= w) {
                        val h = if (mm == 5) 25f else 15f
                        drawLine(Color.Gray, Offset(mx, 80f - h), Offset(mx, 80f), strokeWidth = 1f)
                    }
                }
            }
        }

        Text("cm", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
        Spacer(Modifier.height(24.dp))

        Canvas(modifier = Modifier.fillMaxWidth().height(120.dp).padding(horizontal = 16.dp)) {
            val w = size.width
            val pxPerInch = with(density) { 10.dp.toPx() } * 2.54f * 2.54f / 2.54f
            val inchCount = (w / pxPerInch).toInt()

            drawLine(Color.DarkGray, Offset(0f, 80f), Offset(w, 80f), strokeWidth = 2f)

            for (i in 0..inchCount) {
                val x = i * pxPerInch
                drawLine(Color.DarkGray, Offset(x, 40f), Offset(x, 80f), strokeWidth = 2f)
                val textResult = textMeasurer.measure("$i", TextStyle(fontSize = 12.sp, color = Color.DarkGray))
                drawText(textResult, topLeft = Offset(x - textResult.size.width / 2, 22f))

                for (eighth in 1..7) {
                    val ex = x + eighth * pxPerInch / 8f
                    if (ex <= w) {
                        val h = when {
                            eighth == 4 -> 30f
                            eighth % 2 == 0 -> 20f
                            else -> 12f
                        }
                        drawLine(Color.Gray, Offset(ex, 80f - h), Offset(ex, 80f), strokeWidth = 1f)
                    }
                }
            }
        }

        Text("inches", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
    }
}
