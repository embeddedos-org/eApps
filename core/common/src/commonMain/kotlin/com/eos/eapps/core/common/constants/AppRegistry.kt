package com.eos.eapps.core.common.constants

import com.eos.eapps.core.common.models.AppCategory
import com.eos.eapps.core.common.models.AppInfo

object AppRegistry {
    val apps: List<AppInfo> = listOf(
        // Productivity
        AppInfo("ecal", "eCal", "Calculator", AppCategory.PRODUCTIVITY, icon = "🧮", description = "Scientific calculator with expression parser and tax calculator"),
        AppInfo("enote", "eNote", "Notepad", AppCategory.PRODUCTIVITY, icon = "📝", description = "Rich text editor with search and auto-save"),
        AppInfo("eftp", "eFTP", "File Transfer", AppCategory.PRODUCTIVITY, icon = "📂", description = "Dual-pane SFTP/SCP file transfer"),
        AppInfo("econverter", "eConverter", "Converter", AppCategory.PRODUCTIVITY, icon = "🔄", description = "18 format converters (PDF, image, text, hex)"),
        AppInfo("etools", "eTools", "Tools", AppCategory.PRODUCTIVITY, icon = "🛠️", description = "Unit converter, compass, level, QR scanner"),
        AppInfo("ebuffer", "eBuffer", "Clipboard", AppCategory.PRODUCTIVITY, icon = "📋", description = "Clipboard manager with 20-slot history"),
        AppInfo("ecleaner", "eCleaner", "Cleaner", AppCategory.PRODUCTIVITY, icon = "🧹", description = "Disk cleanup — temp files, caches, logs"),
        AppInfo("eclock", "eClock", "Clock", AppCategory.PRODUCTIVITY, icon = "🕐", description = "World clock, stopwatch, countdown timer"),
        AppInfo("efiles", "eFiles", "Files", AppCategory.PRODUCTIVITY, icon = "📁", description = "File browser with hex viewer"),
        AppInfo("ezip", "eZip", "Archive", AppCategory.PRODUCTIVITY, icon = "🗜️", description = "ZIP archive create/extract"),
        AppInfo("epaint", "ePaint", "Paint", AppCategory.PRODUCTIVITY, icon = "🎨", description = "Canvas drawing with brushes and shapes"),
        AppInfo("epdf", "ePDF", "PDF", AppCategory.PRODUCTIVITY, icon = "📄", description = "PDF viewer with sign/merge/split"),
        AppInfo("eguard", "eGuard", "Guard", AppCategory.PRODUCTIVITY, icon = "🛡️", description = "Keep-awake screen guard"),

        // Media
        AppInfo("emusic", "eMusic", "Music", AppCategory.MEDIA, icon = "🎵", description = "Local music player with playlists and equalizer"),
        AppInfo("evideo", "eVideo", "Video", AppCategory.MEDIA, icon = "🎬", description = "Video player with subtitles and PiP"),
        AppInfo("egallery", "eGallery", "Gallery", AppCategory.MEDIA, icon = "🖼️", description = "Photo/video gallery with albums"),
        AppInfo("eplay", "ePlay", "Player", AppCategory.MEDIA, icon = "▶️", description = "Universal media player wrapper"),

        // Games
        AppInfo("snake", "Snake", "Snake", AppCategory.GAMES, icon = "🐍", description = "Classic snake game"),
        AppInfo("tetris", "Tetris", "Tetris", AppCategory.GAMES, icon = "🧱", description = "Block stacking puzzle"),
        AppInfo("minesweeper", "Minesweeper", "Minesweeper", AppCategory.GAMES, icon = "💣", description = "Classic minesweeper"),
        AppInfo("dice", "Dice", "Dice", AppCategory.GAMES, icon = "🎲", description = "Dice roller with animation"),
        AppInfo("echess", "eChess", "Chess", AppCategory.GAMES, icon = "♟️", description = "Chess with minimax AI"),
        AppInfo("ebirds", "eBirds", "Birds", AppCategory.GAMES, icon = "🐦", description = "Physics-based slingshot game"),
        AppInfo("eslice", "eSlice", "Slice", AppCategory.GAMES, icon = "🍉", description = "Swipe-to-slice fruit game"),
        AppInfo("erunner", "eRunner", "Runner", AppCategory.GAMES, icon = "🏃", description = "Endless runner with obstacles"),
        AppInfo("eblocks", "eBlocks", "Blocks", AppCategory.GAMES, icon = "🟦", description = "Block placement puzzle"),
        AppInfo("ecrush", "eCrush", "Crush", AppCategory.GAMES, icon = "🍬", description = "Match-3 candy puzzle"),
        AppInfo("esurfer", "eSurfer", "Surfer", AppCategory.GAMES, icon = "🏄", description = "3-lane endless runner"),

        // Connectivity
        AppInfo("essh", "eSSH", "SSH", AppCategory.CONNECTIVITY, icon = "🔒", description = "SSH terminal client"),
        AppInfo("eserial", "eSerial", "Serial", AppCategory.CONNECTIVITY, icon = "🔌", description = "Serial port terminal"),
        AppInfo("echat", "eChat", "Chat", AppCategory.CONNECTIVITY, icon = "💬", description = "Peer-to-peer TCP chat"),
        AppInfo("etunnel", "eTunnel", "Tunnel", AppCategory.CONNECTIVITY, icon = "🚇", description = "SSH port forwarding"),
        AppInfo("evpn", "eVPN", "VPN", AppCategory.CONNECTIVITY, icon = "🌐", description = "WireGuard/OpenVPN client"),

        // Security
        AppInfo("evirustower", "eVirusTower", "Antivirus", AppCategory.SECURITY, icon = "🦠", description = "Hash-based malware scanner"),
        AppInfo("evnc", "eVNC", "VNC", AppCategory.SECURITY, icon = "🖥️", description = "VNC remote desktop viewer"),

        // Web
        AppInfo("eweb", "eWeb", "Browser", AppCategory.WEB, icon = "🌍", description = "Embedded web browser"),
    )

    val byId: Map<String, AppInfo> = apps.associateBy { it.id }
    val byCategory: Map<AppCategory, List<AppInfo>> = apps.groupBy { it.category }

    fun getApp(id: String): AppInfo? = byId[id]
    fun getAppsInCategory(category: AppCategory): List<AppInfo> = byCategory[category].orEmpty()
    fun search(query: String): List<AppInfo> {
        val q = query.lowercase()
        return apps.filter {
            it.name.lowercase().contains(q) ||
                it.displayName.lowercase().contains(q) ||
                it.description.lowercase().contains(q)
        }
    }
}
