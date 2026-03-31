package com.eos.eapps.apps.ecal

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

@Composable
fun AppContent() {
    var display by remember { mutableStateOf("0") }
    var expression by remember { mutableStateOf("") }
    var lastOp by remember { mutableStateOf("") }
    var accumulator by remember { mutableStateOf(0.0) }
    var newNumber by remember { mutableStateOf(true) }

    fun handleNumber(n: String) {
        display = if (newNumber) n else if (display == "0" && n != ".") n else display + n
        newNumber = false
    }

    fun handleOp(op: String) {
        val current = display.toDoubleOrNull() ?: return
        if (lastOp.isNotEmpty()) {
            accumulator = when (lastOp) {
                "+" -> accumulator + current
                "-" -> accumulator - current
                "×" -> accumulator * current
                "÷" -> if (current != 0.0) accumulator / current else Double.NaN
                else -> current
            }
        } else accumulator = current
        display = if (accumulator == accumulator.toLong().toDouble()) accumulator.toLong().toString() else accumulator.toString()
        expression = "$display $op"
        lastOp = op
        newNumber = true
    }

    fun handleEquals() {
        handleOp("")
        lastOp = ""
        expression = ""
    }

    fun handleClear() { display = "0"; expression = ""; lastOp = ""; accumulator = 0.0; newNumber = true }

    Column(modifier = Modifier.fillMaxSize().padding(16.dp)) {
        Text("🧮 eCalc", style = MaterialTheme.typography.headlineMedium, modifier = Modifier.align(Alignment.CenterHorizontally))
        Spacer(Modifier.height(16.dp))

        Card(modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(expression, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant, modifier = Modifier.fillMaxWidth(), textAlign = TextAlign.End)
                Text(display, style = MaterialTheme.typography.displaySmall, modifier = Modifier.fillMaxWidth(), textAlign = TextAlign.End, maxLines = 1)
            }
        }

        Spacer(Modifier.weight(1f))

        val buttons = listOf(
            listOf("C", "±", "%", "÷"),
            listOf("7", "8", "9", "×"),
            listOf("4", "5", "6", "-"),
            listOf("1", "2", "3", "+"),
            listOf("0", ".", "="),
        )

        buttons.forEach { row ->
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                row.forEach { btn ->
                    val isOp = btn in listOf("÷", "×", "-", "+", "=")
                    val weight = if (btn == "0") 2f else 1f
                    Button(
                        onClick = {
                            when (btn) {
                                "C" -> handleClear()
                                "±" -> { display = if (display.startsWith("-")) display.drop(1) else "-$display" }
                                "%" -> { display = ((display.toDoubleOrNull() ?: 0.0) / 100).toString(); newNumber = true }
                                "=" -> handleEquals()
                                in listOf("÷", "×", "-", "+") -> handleOp(btn)
                                else -> handleNumber(btn)
                            }
                        },
                        modifier = Modifier.weight(weight).height(64.dp).padding(vertical = 4.dp),
                        shape = RoundedCornerShape(12.dp),
                        colors = if (isOp) ButtonDefaults.buttonColors(containerColor = MaterialTheme.colorScheme.tertiary) else ButtonDefaults.buttonColors(),
                    ) {
                        Text(btn, fontSize = 24.sp)
                    }
                }
            }
        }
    }
}
package com.eos.eapps.apps.ecal

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.eos.eapps.core.common.utils.ExpressionParser
import com.eos.eapps.core.ui.theme.AppTheme

data class HistoryEntry(val expression: String, val result: String)

@Composable
fun App() {
    AppTheme {
        var display by remember { mutableStateOf("0") }
        var expression by remember { mutableStateOf("") }
        var memory by remember { mutableStateOf(0.0) }
        var showScientific by remember { mutableStateOf(false) }
        var showHistory by remember { mutableStateOf(false) }
        val history = remember { mutableStateListOf<HistoryEntry>() }

        fun appendToExpression(value: String) {
            if (display == "0" && value != ".") {
                display = value
                expression = value
            } else {
                display += value
                expression += value
            }
        }

        fun calculate() {
            try {
                val result = ExpressionParser.evaluate(expression)
                val resultStr = if (result == result.toLong().toDouble()) {
                    result.toLong().toString()
                } else {
                    result.toString()
                }
                history.add(0, HistoryEntry(expression, resultStr))
                display = resultStr
                expression = resultStr
            } catch (_: Exception) {
                display = "Error"
                expression = ""
            }
        }

        fun clear() {
            display = "0"
            expression = ""
        }

        fun backspace() {
            if (display.length > 1) {
                display = display.dropLast(1)
                expression = expression.dropLast(1)
            } else {
                clear()
            }
        }

        fun appendFunction(func: String) {
            display += "$func("
            expression += "$func("
        }

        Scaffold(
            topBar = {
                @OptIn(ExperimentalMaterial3Api::class)
                TopAppBar(
                    title = { Text("eCalc") },
                    actions = {
                        TextButton(onClick = { showScientific = !showScientific }) {
                            Text(if (showScientific) "Basic" else "Sci")
                        }
                        TextButton(onClick = { showHistory = !showHistory }) {
                            Text("History")
                        }
                    }
                )
            }
        ) { padding ->
            Column(
                modifier = Modifier.fillMaxSize().padding(padding)
            ) {
                if (showHistory) {
                    LazyColumn(
                        modifier = Modifier.weight(1f).fillMaxWidth().padding(horizontal = 16.dp)
                    ) {
                        if (history.isEmpty()) {
                            item {
                                Text(
                                    "No history yet",
                                    modifier = Modifier.fillMaxWidth().padding(32.dp),
                                    textAlign = TextAlign.Center,
                                    color = MaterialTheme.colorScheme.onSurfaceVariant
                                )
                            }
                        }
                        items(history) { entry ->
                            Column(modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp)) {
                                Text(
                                    entry.expression,
                                    style = MaterialTheme.typography.bodyMedium,
                                    color = MaterialTheme.colorScheme.onSurfaceVariant
                                )
                                Text(
                                    "= ${entry.result}",
                                    style = MaterialTheme.typography.titleMedium,
                                    color = MaterialTheme.colorScheme.primary
                                )
                                HorizontalDivider()
                            }
                        }
                    }
                } else {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .weight(0.25f)
                            .background(MaterialTheme.colorScheme.surfaceVariant)
                            .padding(16.dp),
                        verticalArrangement = Arrangement.Bottom,
                        horizontalAlignment = Alignment.End
                    ) {
                        Text(
                            text = expression,
                            style = MaterialTheme.typography.bodyMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                            maxLines = 1
                        )
                        Spacer(Modifier.height(4.dp))
                        Text(
                            text = display,
                            style = MaterialTheme.typography.headlineLarge.copy(fontSize = 40.sp),
                            color = MaterialTheme.colorScheme.onSurface,
                            maxLines = 1
                        )
                    }

                    if (showScientific) {
                        Row(
                            modifier = Modifier.fillMaxWidth().padding(horizontal = 4.dp, vertical = 2.dp),
                            horizontalArrangement = Arrangement.SpaceEvenly
                        ) {
                            listOf("sin", "cos", "tan", "log").forEach { func ->
                                CalcButton(func, Modifier.weight(1f)) { appendFunction(func) }
                            }
                        }
                        Row(
                            modifier = Modifier.fillMaxWidth().padding(horizontal = 4.dp, vertical = 2.dp),
                            horizontalArrangement = Arrangement.SpaceEvenly
                        ) {
                            listOf("sqrt", "abs", "exp", "^").forEach { func ->
                                CalcButton(func, Modifier.weight(1f)) {
                                    if (func == "^") appendToExpression("^")
                                    else appendFunction(func)
                                }
                            }
                        }
                        Row(
                            modifier = Modifier.fillMaxWidth().padding(horizontal = 4.dp, vertical = 2.dp),
                            horizontalArrangement = Arrangement.SpaceEvenly
                        ) {
                            CalcButton("π", Modifier.weight(1f)) { appendToExpression("pi") }
                            CalcButton("e", Modifier.weight(1f)) { appendToExpression("e") }
                            CalcButton("(", Modifier.weight(1f)) { appendToExpression("(") }
                            CalcButton(")", Modifier.weight(1f)) { appendToExpression(")") }
                        }
                    }

                    Row(
                        modifier = Modifier.fillMaxWidth().padding(horizontal = 4.dp, vertical = 2.dp),
                        horizontalArrangement = Arrangement.SpaceEvenly
                    ) {
                        CalcButton("MC", Modifier.weight(1f)) { memory = 0.0 }
                        CalcButton("MR", Modifier.weight(1f)) {
                            val mStr = if (memory == memory.toLong().toDouble()) memory.toLong().toString() else memory.toString()
                            display = mStr; expression = mStr
                        }
                        CalcButton("M+", Modifier.weight(1f)) { memory += display.toDoubleOrNull() ?: 0.0 }
                        CalcButton("M−", Modifier.weight(1f)) { memory -= display.toDoubleOrNull() ?: 0.0 }
                    }

                    Row(
                        modifier = Modifier.fillMaxWidth().padding(horizontal = 4.dp, vertical = 2.dp),
                        horizontalArrangement = Arrangement.SpaceEvenly
                    ) {
                        CalcButton("C", Modifier.weight(1f), containerColor = MaterialTheme.colorScheme.error) { clear() }
                        CalcButton("⌫", Modifier.weight(1f)) { backspace() }
                        CalcButton("%", Modifier.weight(1f)) { appendToExpression("%") }
                        CalcButton("÷", Modifier.weight(1f), containerColor = MaterialTheme.colorScheme.primary) { appendToExpression("/") }
                    }

                    val numberRows = listOf(
                        listOf("7", "8", "9", "×"),
                        listOf("4", "5", "6", "−"),
                        listOf("1", "2", "3", "+")
                    )
                    numberRows.forEach { row ->
                        Row(
                            modifier = Modifier.fillMaxWidth().padding(horizontal = 4.dp, vertical = 2.dp),
                            horizontalArrangement = Arrangement.SpaceEvenly
                        ) {
                            row.forEach { label ->
                                val isOp = label in listOf("×", "−", "+")
                                CalcButton(
                                    label,
                                    Modifier.weight(1f),
                                    containerColor = if (isOp) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.surfaceVariant
                                ) {
                                    when (label) {
                                        "×" -> appendToExpression("*")
                                        "−" -> appendToExpression("-")
                                        "+" -> appendToExpression("+")
                                        else -> appendToExpression(label)
                                    }
                                }
                            }
                        }
                    }

                    Row(
                        modifier = Modifier.fillMaxWidth().padding(horizontal = 4.dp, vertical = 2.dp),
                        horizontalArrangement = Arrangement.SpaceEvenly
                    ) {
                        CalcButton("±", Modifier.weight(1f)) {
                            if (display.startsWith("-")) {
                                display = display.drop(1)
                                expression = expression.drop(1)
                            } else {
                                display = "-$display"
                                expression = "-$expression"
                            }
                        }
                        CalcButton("0", Modifier.weight(1f)) { appendToExpression("0") }
                        CalcButton(".", Modifier.weight(1f)) { appendToExpression(".") }
                        CalcButton("=", Modifier.weight(1f), containerColor = MaterialTheme.colorScheme.primary) { calculate() }
                    }

                    Spacer(Modifier.height(8.dp))
                }
            }
        }
    }
}

@Composable
private fun CalcButton(
    label: String,
    modifier: Modifier = Modifier,
    containerColor: androidx.compose.ui.graphics.Color = MaterialTheme.colorScheme.surfaceVariant,
    onClick: () -> Unit
) {
    Button(
        onClick = onClick,
        modifier = modifier.padding(2.dp).height(56.dp),
        shape = RoundedCornerShape(12.dp),
        colors = ButtonDefaults.buttonColors(containerColor = containerColor)
    ) {
        Text(
            text = label,
            fontSize = 18.sp,
            maxLines = 1
        )
    }
}
