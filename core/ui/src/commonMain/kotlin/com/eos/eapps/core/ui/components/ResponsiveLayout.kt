package com.eos.eapps.core.ui.components

import androidx.compose.foundation.layout.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.unit.dp

enum class WindowSize { COMPACT, MEDIUM, EXPANDED, LARGE }

@Composable
fun ResponsiveLayout(
    windowSize: WindowSize,
    compactContent: @Composable () -> Unit,
    mediumContent: (@Composable () -> Unit)? = null,
    expandedContent: (@Composable () -> Unit)? = null,
    largeContent: (@Composable () -> Unit)? = null,
) {
    when (windowSize) {
        WindowSize.COMPACT -> compactContent()
        WindowSize.MEDIUM -> (mediumContent ?: compactContent)()
        WindowSize.EXPANDED -> (expandedContent ?: mediumContent ?: compactContent)()
        WindowSize.LARGE -> (largeContent ?: expandedContent ?: mediumContent ?: compactContent)()
    }
}

fun calculateWindowSize(widthDp: Int): WindowSize = when {
    widthDp < 600 -> WindowSize.COMPACT
    widthDp < 840 -> WindowSize.MEDIUM
    widthDp < 1200 -> WindowSize.EXPANDED
    else -> WindowSize.LARGE
}

@Composable
fun rememberWindowSize(): WindowSize {
    return BoxWithConstraints {
        val widthDp = with(LocalDensity.current) { constraints.maxWidth.toDp() }
        calculateWindowSize(widthDp.value.toInt())
    }
}

@Composable
private fun BoxWithConstraints(content: @Composable BoxWithConstraintsScope.() -> WindowSize): WindowSize {
    var windowSize = WindowSize.COMPACT
    BoxWithConstraints {
        windowSize = content()
    }
    return windowSize
}
