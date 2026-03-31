package com.eos.eapps.apps.suite

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.Search
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import com.eos.eapps.core.common.constants.AppRegistry
import com.eos.eapps.core.common.models.AppCategory
import com.eos.eapps.core.common.models.AppInfo

@Composable
fun AppContent() {
    var searchQuery by remember { mutableStateOf("") }
    var selectedCategory by remember { mutableStateOf<AppCategory?>(null) }
    var openTabs by remember { mutableStateOf(listOf<AppInfo>()) }
    var activeTabId by remember { mutableStateOf<String?>(null) }

    val filteredApps = remember(searchQuery, selectedCategory) {
        val apps = if (searchQuery.isNotBlank()) AppRegistry.search(searchQuery)
        else if (selectedCategory != null) AppRegistry.getAppsInCategory(selectedCategory!!)
        else AppRegistry.apps
        apps
    }

    Column(modifier = Modifier.fillMaxSize()) {
        // Tab bar
        if (openTabs.isNotEmpty()) {
            ScrollableTabRow(
                selectedTabIndex = openTabs.indexOfFirst { it.id == activeTabId }.coerceAtLeast(0),
                modifier = Modifier.fillMaxWidth(),
            ) {
                openTabs.forEach { app ->
                    Tab(
                        selected = app.id == activeTabId,
                        onClick = { activeTabId = app.id },
                        text = {
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Text("${app.icon} ${app.displayName}", maxLines = 1)
                                Spacer(Modifier.width(4.dp))
                                IconButton(
                                    onClick = {
                                        openTabs = openTabs.filter { it.id != app.id }
                                        if (activeTabId == app.id) {
                                            activeTabId = openTabs.lastOrNull()?.id
                                        }
                                    },
                                    modifier = Modifier.size(16.dp),
                                ) {
                                    Icon(Icons.Default.Close, "Close", modifier = Modifier.size(12.dp))
                                }
                            }
                        },
                    )
                }
            }
        }

        if (activeTabId != null && openTabs.any { it.id == activeTabId }) {
            val activeApp = openTabs.first { it.id == activeTabId }
            Box(modifier = Modifier.fillMaxSize().padding(16.dp)) {
                Column(horizontalAlignment = Alignment.CenterHorizontally, modifier = Modifier.align(Alignment.Center)) {
                    Text(activeApp.icon, style = MaterialTheme.typography.displayLarge)
                    Spacer(Modifier.height(8.dp))
                    Text(activeApp.name, style = MaterialTheme.typography.headlineMedium)
                    Text(activeApp.description, style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
                }
            }
        } else {
            // Launcher grid
            Column(modifier = Modifier.fillMaxSize()) {
                // Search bar
                OutlinedTextField(
                    value = searchQuery,
                    onValueChange = { searchQuery = it },
                    placeholder = { Text("Search apps...") },
                    leadingIcon = { Icon(Icons.Default.Search, "Search") },
                    modifier = Modifier.fillMaxWidth().padding(12.dp),
                    singleLine = true,
                )

                // Category chips
                Row(
                    modifier = Modifier.fillMaxWidth().padding(horizontal = 12.dp),
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                ) {
                    FilterChip(
                        selected = selectedCategory == null,
                        onClick = { selectedCategory = null },
                        label = { Text("All") },
                    )
                    AppCategory.entries.filter { it != AppCategory.SUITE }.forEach { category ->
                        FilterChip(
                            selected = selectedCategory == category,
                            onClick = { selectedCategory = if (selectedCategory == category) null else category },
                            label = { Text("${category.icon} ${category.displayName}") },
                        )
                    }
                }

                Spacer(Modifier.height(8.dp))

                // App grid
                LazyVerticalGrid(
                    columns = GridCells.Adaptive(100.dp),
                    contentPadding = PaddingValues(12.dp),
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp),
                ) {
                    items(filteredApps) { app ->
                        Card(
                            modifier = Modifier
                                .fillMaxWidth()
                                .clickable {
                                    if (openTabs.none { it.id == app.id }) {
                                        openTabs = openTabs + app
                                    }
                                    activeTabId = app.id
                                },
                        ) {
                            Column(
                                horizontalAlignment = Alignment.CenterHorizontally,
                                modifier = Modifier.padding(12.dp).fillMaxWidth(),
                            ) {
                                Text(app.icon, style = MaterialTheme.typography.headlineLarge)
                                Spacer(Modifier.height(4.dp))
                                Text(
                                    app.displayName,
                                    style = MaterialTheme.typography.labelMedium,
                                    textAlign = TextAlign.Center,
                                    maxLines = 1,
                                    overflow = TextOverflow.Ellipsis,
                                )
                            }
                        }
                    }
                }
            }
        }
    }
}
package com.eos.eapps.apps.suite

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.DarkMode
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.KeyboardArrowDown
import androidx.compose.material.icons.filled.KeyboardArrowRight
import androidx.compose.material.icons.filled.LightMode
import androidx.compose.material.icons.filled.Search
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.eos.eapps.core.common.constants.AppRegistry
import com.eos.eapps.core.common.models.AppCategory
import com.eos.eapps.core.common.models.AppInfo
import com.eos.eapps.core.ui.theme.AppTheme

data class TabItem(
    val id: String,
    val title: String,
    val icon: String,
    val isHome: Boolean = false,
)

@Composable
fun App() {
    var isDarkTheme by remember { mutableStateOf(true) }

    AppTheme(darkTheme = isDarkTheme) {
        SuiteLauncher(
            isDarkTheme = isDarkTheme,
            onToggleTheme = { isDarkTheme = !isDarkTheme },
        )
    }
}

@Composable
fun SuiteLauncher(
    isDarkTheme: Boolean,
    onToggleTheme: () -> Unit,
) {
    val homeTab = TabItem(id = "home", title = "Home", icon = "🏠", isHome = true)
    var openTabs by remember { mutableStateOf(listOf(homeTab)) }
    var activeTabId by remember { mutableStateOf("home") }
    var searchQuery by remember { mutableStateOf("") }

    Column(modifier = Modifier.fillMaxSize()) {
        Row(modifier = Modifier.weight(1f)) {
            Sidebar(
                searchQuery = searchQuery,
                onSearchChange = { searchQuery = it },
                onAppClick = { app ->
                    val existing = openTabs.find { it.id == app.id }
                    if (existing != null) {
                        activeTabId = existing.id
                    } else if (openTabs.size < 10) {
                        val tab = TabItem(id = app.id, title = app.name, icon = app.icon)
                        openTabs = openTabs + tab
                        activeTabId = tab.id
                    }
                },
                isDarkTheme = isDarkTheme,
                onToggleTheme = onToggleTheme,
            )

            VerticalDivider(
                modifier = Modifier.fillMaxHeight(),
                color = MaterialTheme.colorScheme.outlineVariant,
            )

            Column(modifier = Modifier.weight(1f)) {
                TabBar(
                    tabs = openTabs,
                    activeTabId = activeTabId,
                    onTabClick = { activeTabId = it },
                    onTabClose = { tabId ->
                        val tab = openTabs.find { it.id == tabId }
                        if (tab != null && !tab.isHome) {
                            openTabs = openTabs.filter { it.id != tabId }
                            if (activeTabId == tabId) {
                                activeTabId = openTabs.lastOrNull()?.id ?: "home"
                            }
                        }
                    },
                )

                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background,
                ) {
                    val activeTab = openTabs.find { it.id == activeTabId }
                    if (activeTab == null || activeTab.isHome) {
                        HomeScreen(
                            onAppClick = { app ->
                                val existing = openTabs.find { it.id == app.id }
                                if (existing != null) {
                                    activeTabId = existing.id
                                } else if (openTabs.size < 10) {
                                    val tab = TabItem(id = app.id, title = app.name, icon = app.icon)
                                    openTabs = openTabs + tab
                                    activeTabId = tab.id
                                }
                            },
                        )
                    } else {
                        AppPlaceholder(appId = activeTab.id)
                    }
                }
            }
        }

        StatusBar(
            isDarkTheme = isDarkTheme,
            tabCount = openTabs.size,
        )
    }
}

@Composable
private fun Sidebar(
    searchQuery: String,
    onSearchChange: (String) -> Unit,
    onAppClick: (AppInfo) -> Unit,
    isDarkTheme: Boolean,
    onToggleTheme: () -> Unit,
) {
    val expandedCategories = remember { mutableStateMapOf<AppCategory, Boolean>() }
    val filteredApps = if (searchQuery.isBlank()) {
        AppRegistry.byCategory
    } else {
        AppRegistry.search(searchQuery).groupBy { it.category }
    }

    Column(
        modifier = Modifier
            .width(250.dp)
            .fillMaxHeight()
            .background(MaterialTheme.colorScheme.surfaceVariant),
    ) {
        // Header
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(12.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.SpaceBetween,
        ) {
            Text(
                text = "📦 eApps",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            IconButton(onClick = onToggleTheme, modifier = Modifier.size(32.dp)) {
                Icon(
                    imageVector = if (isDarkTheme) Icons.Default.LightMode else Icons.Default.DarkMode,
                    contentDescription = "Toggle theme",
                    tint = MaterialTheme.colorScheme.onSurfaceVariant,
                    modifier = Modifier.size(20.dp),
                )
            }
        }

        // Search
        OutlinedTextField(
            value = searchQuery,
            onValueChange = onSearchChange,
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 12.dp, vertical = 4.dp),
            placeholder = { Text("Search apps…", fontSize = 13.sp) },
            leadingIcon = {
                Icon(Icons.Default.Search, contentDescription = null, modifier = Modifier.size(18.dp))
            },
            singleLine = true,
            textStyle = LocalTextStyle.current.copy(fontSize = 13.sp),
        )

        Spacer(modifier = Modifier.height(4.dp))

        // Category sections
        LazyColumn(modifier = Modifier.weight(1f)) {
            filteredApps.forEach { (category, apps) ->
                val isExpanded = expandedCategories.getOrDefault(category, true)

                item(key = "header_${category.name}") {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .clickable { expandedCategories[category] = !isExpanded }
                            .padding(horizontal = 12.dp, vertical = 8.dp),
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        Icon(
                            imageVector = if (isExpanded) Icons.Default.KeyboardArrowDown
                            else Icons.Default.KeyboardArrowRight,
                            contentDescription = null,
                            modifier = Modifier.size(18.dp),
                            tint = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                        Spacer(modifier = Modifier.width(4.dp))
                        Text(
                            text = "${category.icon} ${category.displayName}",
                            style = MaterialTheme.typography.labelLarge,
                            fontWeight = FontWeight.SemiBold,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                        Spacer(modifier = Modifier.weight(1f))
                        Text(
                            text = "${apps.size}",
                            style = MaterialTheme.typography.labelSmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.6f),
                        )
                    }
                }

                if (isExpanded) {
                    items(apps, key = { it.id }) { app ->
                        SidebarAppItem(app = app, onClick = { onAppClick(app) })
                    }
                }
            }
        }
    }
}

@Composable
private fun SidebarAppItem(
    app: AppInfo,
    onClick: () -> Unit,
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick)
            .padding(start = 36.dp, end = 12.dp, top = 4.dp, bottom = 4.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Text(text = app.icon, fontSize = 16.sp)
        Spacer(modifier = Modifier.width(8.dp))
        Column {
            Text(
                text = app.name,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            Text(
                text = app.displayName,
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.6f),
            )
        }
    }
}

@Composable
private fun TabBar(
    tabs: List<TabItem>,
    activeTabId: String,
    onTabClick: (String) -> Unit,
    onTabClose: (String) -> Unit,
) {
    ScrollableTabRow(
        selectedTabIndex = tabs.indexOfFirst { it.id == activeTabId }.coerceAtLeast(0),
        modifier = Modifier.fillMaxWidth(),
        edgePadding = 0.dp,
        containerColor = MaterialTheme.colorScheme.surfaceVariant,
        contentColor = MaterialTheme.colorScheme.onSurfaceVariant,
        divider = { HorizontalDivider(color = MaterialTheme.colorScheme.outlineVariant) },
    ) {
        tabs.forEach { tab ->
            val isActive = tab.id == activeTabId
            Tab(
                selected = isActive,
                onClick = { onTabClick(tab.id) },
                modifier = Modifier.height(40.dp),
            ) {
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    modifier = Modifier.padding(horizontal = 12.dp),
                ) {
                    if (tab.isHome) {
                        Icon(
                            Icons.Default.Home,
                            contentDescription = "Home",
                            modifier = Modifier.size(16.dp),
                        )
                    } else {
                        Text(text = tab.icon, fontSize = 14.sp)
                    }
                    Spacer(modifier = Modifier.width(6.dp))
                    Text(
                        text = tab.title,
                        fontSize = 13.sp,
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis,
                        fontWeight = if (isActive) FontWeight.SemiBold else FontWeight.Normal,
                    )
                    if (!tab.isHome) {
                        Spacer(modifier = Modifier.width(6.dp))
                        Icon(
                            Icons.Default.Close,
                            contentDescription = "Close tab",
                            modifier = Modifier
                                .size(16.dp)
                                .clickable { onTabClose(tab.id) },
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun HomeScreen(onAppClick: (AppInfo) -> Unit) {
    Column(
        modifier = Modifier.fillMaxSize().padding(24.dp),
    ) {
        Text(
            text = "Welcome to eApps",
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.Bold,
            color = MaterialTheme.colorScheme.onBackground,
        )
        Text(
            text = "38 cross-platform apps • Kotlin Multiplatform • Compose",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onBackground.copy(alpha = 0.7f),
        )
        Spacer(modifier = Modifier.height(20.dp))

        LazyVerticalGrid(
            columns = GridCells.Adaptive(140.dp),
            horizontalArrangement = Arrangement.spacedBy(12.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            items(AppRegistry.apps) { app ->
                AppGridCard(app = app, onClick = { onAppClick(app) })
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun AppGridCard(
    app: AppInfo,
    onClick: () -> Unit,
) {
    Card(
        onClick = onClick,
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
    ) {
        Column(
            modifier = Modifier.padding(12.dp).fillMaxWidth(),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            Text(text = app.icon, fontSize = 32.sp)
            Spacer(modifier = Modifier.height(6.dp))
            Text(
                text = app.name,
                style = MaterialTheme.typography.bodyMedium,
                fontWeight = FontWeight.SemiBold,
                textAlign = TextAlign.Center,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis,
            )
            Text(
                text = app.displayName,
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f),
                textAlign = TextAlign.Center,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis,
            )
        }
    }
}

@Composable
private fun AppPlaceholder(appId: String) {
    val app = AppRegistry.getApp(appId)
    Box(
        modifier = Modifier.fillMaxSize(),
        contentAlignment = Alignment.Center,
    ) {
        Column(horizontalAlignment = Alignment.CenterHorizontally) {
            Text(text = app?.icon ?: "📦", fontSize = 64.sp)
            Spacer(modifier = Modifier.height(16.dp))
            Text(
                text = app?.name ?: appId,
                style = MaterialTheme.typography.headlineMedium,
                fontWeight = FontWeight.Bold,
            )
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = app?.description ?: "",
                style = MaterialTheme.typography.bodyLarge,
                color = MaterialTheme.colorScheme.onBackground.copy(alpha = 0.7f),
            )
            Spacer(modifier = Modifier.height(24.dp))
            Text(
                text = "App module will render here when integrated.",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onBackground.copy(alpha = 0.4f),
            )
        }
    }
}

@Composable
private fun StatusBar(
    isDarkTheme: Boolean,
    tabCount: Int,
) {
    Surface(
        modifier = Modifier.fillMaxWidth(),
        color = MaterialTheme.colorScheme.surfaceVariant,
        tonalElevation = 2.dp,
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 16.dp, vertical = 4.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Text(
                text = "eApps v1.0 | ${AppRegistry.apps.size} Apps | ${if (isDarkTheme) "Dark" else "Light"}",
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.8f),
            )
            Text(
                text = "$tabCount tab${if (tabCount != 1) "s" else ""} open",
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.6f),
            )
        }
    }
}
