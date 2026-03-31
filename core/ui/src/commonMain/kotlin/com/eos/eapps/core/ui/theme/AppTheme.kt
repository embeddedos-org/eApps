package com.eos.eapps.core.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

private val LightColorScheme = lightColorScheme(
    primary = AppColors.Primary,
    onPrimary = Color.White,
    primaryContainer = AppColors.PrimaryLight,
    secondary = AppColors.Accent,
    onSecondary = Color.White,
    background = AppColors.BackgroundLight,
    onBackground = AppColors.TextDark,
    surface = AppColors.SurfaceLight,
    onSurface = AppColors.TextDark,
    error = AppColors.Error,
    onError = Color.White
)

private val DarkColorScheme = darkColorScheme(
    primary = AppColors.PrimaryLight,
    onPrimary = AppColors.PrimaryDark,
    primaryContainer = AppColors.PrimaryDark,
    secondary = AppColors.AccentLight,
    onSecondary = Color.Black,
    background = AppColors.BackgroundDark,
    onBackground = AppColors.TextLight,
    surface = AppColors.SurfaceDark,
    onSurface = AppColors.TextLight,
    error = AppColors.ErrorLight,
    onError = Color.Black
)

@Composable
fun AppTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit
) {
    val colorScheme = if (darkTheme) DarkColorScheme else LightColorScheme
    MaterialTheme(
        colorScheme = colorScheme,
        typography = AppTypography.Typography,
        content = content
    )
}
