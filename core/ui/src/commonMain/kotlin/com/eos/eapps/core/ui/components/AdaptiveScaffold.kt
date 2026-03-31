package com.eos.eapps.core.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Menu
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

data class NavItem(
    val id: String,
    val label: String,
    val icon: String = "",
)

@Composable
fun AdaptiveScaffold(
    windowSize: WindowSize,
    navItems: List<NavItem>,
    selectedId: String,
    onNavSelected: (String) -> Unit,
    topBar: @Composable () -> Unit = {},
    content: @Composable (PaddingValues) -> Unit,
) {
    when (windowSize) {
        WindowSize.COMPACT -> CompactScaffold(navItems, selectedId, onNavSelected, topBar, content)
        WindowSize.MEDIUM -> MediumScaffold(navItems, selectedId, onNavSelected, topBar, content)
        WindowSize.EXPANDED, WindowSize.LARGE ->
            ExpandedScaffold(navItems, selectedId, onNavSelected, topBar, content)
    }
}

@Composable
private fun CompactScaffold(
    navItems: List<NavItem>,
    selectedId: String,
    onNavSelected: (String) -> Unit,
    topBar: @Composable () -> Unit,
    content: @Composable (PaddingValues) -> Unit,
) {
    Scaffold(
        topBar = topBar,
        bottomBar = {
            NavigationBar {
                navItems.take(5).forEach { item ->
                    NavigationBarItem(
                        selected = item.id == selectedId,
                        onClick = { onNavSelected(item.id) },
                        icon = { Text(item.icon.ifEmpty { item.label.take(1) }) },
                        label = { Text(item.label, maxLines = 1) },
                    )
                }
            }
        },
        content = content,
    )
}

@Composable
private fun MediumScaffold(
    navItems: List<NavItem>,
    selectedId: String,
    onNavSelected: (String) -> Unit,
    topBar: @Composable () -> Unit,
    content: @Composable (PaddingValues) -> Unit,
) {
    Row(modifier = Modifier.fillMaxSize()) {
        NavigationRail {
            Spacer(Modifier.height(8.dp))
            navItems.forEach { item ->
                NavigationRailItem(
                    selected = item.id == selectedId,
                    onClick = { onNavSelected(item.id) },
                    icon = { Text(item.icon.ifEmpty { item.label.take(1) }) },
                    label = { Text(item.label, maxLines = 1) },
                )
            }
        }
        Scaffold(topBar = topBar, content = content)
    }
}

@Composable
private fun ExpandedScaffold(
    navItems: List<NavItem>,
    selectedId: String,
    onNavSelected: (String) -> Unit,
    topBar: @Composable () -> Unit,
    content: @Composable (PaddingValues) -> Unit,
) {
    Row(modifier = Modifier.fillMaxSize()) {
        PermanentNavigationDrawer(
            drawerContent = {
                PermanentDrawerSheet(modifier = Modifier.width(240.dp)) {
                    Spacer(Modifier.height(16.dp))
                    Text(
                        "eApps",
                        style = MaterialTheme.typography.titleMedium,
                        modifier = Modifier.padding(horizontal = 16.dp, vertical = 8.dp),
                    )
                    HorizontalDivider(modifier = Modifier.padding(vertical = 8.dp))
                    navItems.forEach { item ->
                        NavigationDrawerItem(
                            label = { Text(item.label) },
                            icon = { Text(item.icon.ifEmpty { item.label.take(1) }) },
                            selected = item.id == selectedId,
                            onClick = { onNavSelected(item.id) },
                            modifier = Modifier.padding(horizontal = 12.dp),
                        )
                    }
                }
            },
            content = {
                Scaffold(topBar = topBar, content = content)
            },
        )
    }
}
