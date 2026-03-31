package com.eos.eapps.core.ui.components

import androidx.compose.runtime.Composable
import androidx.compose.runtime.compositionLocalOf
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.TextUnit
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

data class PlatformScale(
    val minTouchTarget: Dp = 48.dp,
    val bodyTextSize: TextUnit = 16.sp,
    val titleTextSize: TextUnit = 22.sp,
    val captionTextSize: TextUnit = 12.sp,
    val horizontalPadding: Dp = 16.dp,
    val verticalPadding: Dp = 8.dp,
    val itemSpacing: Dp = 8.dp,
    val cardElevation: Dp = 2.dp,
    val maxContentWidth: Dp = Dp.Unspecified,
)

object PlatformScaling {
    fun forWindowSize(windowSize: WindowSize): PlatformScale = when (windowSize) {
        WindowSize.COMPACT -> PlatformScale(
            minTouchTarget = 48.dp,
            bodyTextSize = 16.sp,
            titleTextSize = 22.sp,
            captionTextSize = 12.sp,
            horizontalPadding = 16.dp,
            verticalPadding = 8.dp,
            itemSpacing = 8.dp,
        )
        WindowSize.MEDIUM -> PlatformScale(
            minTouchTarget = 48.dp,
            bodyTextSize = 16.sp,
            titleTextSize = 24.sp,
            captionTextSize = 12.sp,
            horizontalPadding = 24.dp,
            verticalPadding = 12.dp,
            itemSpacing = 12.dp,
        )
        WindowSize.EXPANDED -> PlatformScale(
            minTouchTarget = 40.dp,
            bodyTextSize = 14.sp,
            titleTextSize = 20.sp,
            captionTextSize = 11.sp,
            horizontalPadding = 24.dp,
            verticalPadding = 8.dp,
            itemSpacing = 8.dp,
            maxContentWidth = 960.dp,
        )
        WindowSize.LARGE -> PlatformScale(
            minTouchTarget = 32.dp,
            bodyTextSize = 14.sp,
            titleTextSize = 20.sp,
            captionTextSize = 11.sp,
            horizontalPadding = 32.dp,
            verticalPadding = 8.dp,
            itemSpacing = 8.dp,
            maxContentWidth = 1200.dp,
        )
    }
}

val LocalPlatformScale = compositionLocalOf { PlatformScale() }
