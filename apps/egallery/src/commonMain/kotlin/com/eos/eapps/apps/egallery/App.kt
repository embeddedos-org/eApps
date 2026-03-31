package com.eos.eapps.apps.egallery

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp

val DEMO_IMAGES = listOf("🌅", "🏔️", "🌊", "🌸", "🌆", "🐕", "🎨", "🍕", "🚀", "🦋", "🌺", "🏖️")

@Composable
fun AppContent() {
    var selectedImage by remember { mutableStateOf<Int?>(null) }

    if (selectedImage != null) {
        Column(modifier = Modifier.fillMaxSize().padding(16.dp), horizontalAlignment = Alignment.CenterHorizontally) {
            TextButton(onClick = { selectedImage = null }) { Text("← Back to Gallery") }
            Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                Text(DEMO_IMAGES[selectedImage!!], style = MaterialTheme.typography.displayLarge)
            }
        }
    } else {
        Column(modifier = Modifier.fillMaxSize().padding(16.dp)) {
            Text("🖼️ eGallery", style = MaterialTheme.typography.headlineMedium, modifier = Modifier.align(Alignment.CenterHorizontally))
            Text("${DEMO_IMAGES.size} photos", style = MaterialTheme.typography.bodyMedium, modifier = Modifier.align(Alignment.CenterHorizontally))
            Spacer(Modifier.height(8.dp))
            LazyVerticalGrid(columns = GridCells.Adaptive(100.dp), horizontalArrangement = Arrangement.spacedBy(4.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                items(DEMO_IMAGES.size) { i ->
                    Card(modifier = Modifier.aspectRatio(1f).clickable { selectedImage = i }) {
                        Box(modifier = Modifier.fillMaxSize().background(Color(0xFFF5F5F5)), contentAlignment = Alignment.Center) {
                            Text(DEMO_IMAGES[i], style = MaterialTheme.typography.headlineLarge)
                        }
                    }
                }
            }
        }
    }
}
