package com.eos.eapps.core.ui.components

import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier

@Composable
fun AppButton(
    text: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    enabled: Boolean = true,
    type: AppButtonType = AppButtonType.PRIMARY
) {
    when (type) {
        AppButtonType.PRIMARY -> Button(onClick = onClick, modifier = modifier, enabled = enabled) {
            Text(text)
        }
        AppButtonType.SECONDARY -> OutlinedButton(onClick = onClick, modifier = modifier, enabled = enabled) {
            Text(text)
        }
        AppButtonType.TEXT -> TextButton(onClick = onClick, modifier = modifier, enabled = enabled) {
            Text(text)
        }
    }
}

enum class AppButtonType { PRIMARY, SECONDARY, TEXT }
