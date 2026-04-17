"""Generate the expanded apps.json with 8 categories and all platform variants."""
import json, datetime

base = "https://github.com/embeddedos-org/eApps/releases/download"
repo = "https://github.com/embeddedos-org/eApps"

data = {
    "meta": {
        "version": "2.0.0",
        "lastUpdated": datetime.date.today().isoformat(),
        "org": "embeddedos-org",
        "hubUrl": "https://embeddedos-org.github.io/eApps/"
    },
    "categories": [
        {"id": "browser-ext", "name": "Browser Extensions", "icon": "\U0001f310", "description": "Chrome, Firefox, Safari, Edge, Opera, Brave browser extensions"},
        {"id": "ide-ext", "name": "IDE & Dev Tools", "icon": "\U0001f6e0\ufe0f", "description": "VS Code, JetBrains, Obsidian, Sublime, Vim/Neovim extensions"},
        {"id": "mobile-android", "name": "Android & TV", "icon": "\U0001f4f1", "description": "Android Phone, Tablet, Android TV, Wear OS apps"},
        {"id": "mobile-ios", "name": "iOS & iPadOS", "icon": "\U0001f34e", "description": "iPhone, iPad, Apple Watch, Apple TV apps"},
        {"id": "desktop", "name": "Desktop", "icon": "\U0001f5a5\ufe0f", "description": "Windows, macOS, Linux, EoS — x86_64, ARM64, Apple Silicon"},
        {"id": "native", "name": "Embedded / Native", "icon": "\u2699\ufe0f", "description": "C + LVGL apps for EoS and embedded platforms"},
        {"id": "service", "name": "Cloud & Services", "icon": "\u2601\ufe0f", "description": "Firebase, Docker, APIs, backend services"},
        {"id": "os-images", "name": "OS & VM Images", "icon": "\U0001f4bf", "description": "EoS ISO, VirtualBox OVA, VMware VMDK, QEMU qcow2"},
    ],
    "apps": []
}

apps = data["apps"]

# ── Helper ──
def add(id, name, desc, cat, platforms, tags, ver="1.0.0", dl_url=None, downloads=None, source=""):
    entry = {
        "id": id, "name": name, "description": desc,
        "category": cat, "platform": platforms,
        "icon": f"assets/icons/{id.split('-')[0]}.svg",
        "repo": repo, "source": source, "version": ver,
        "releaseUrl": f"{base}/{id}-v{ver}",
        "tags": tags,
    }
    if dl_url:
        entry["downloadUrl"] = dl_url
    elif downloads:
        entry["downloads"] = downloads
    else:
        entry["downloadUrl"] = f"{base}/{id}-v{ver}/{id}-{ver}.zip"
    apps.append(entry)

# ═══════════════════════════════════════════════════════════
# BROWSER EXTENSIONS
# ═══════════════════════════════════════════════════════════
browsers = [
    ("chrome", "Chrome", ".zip"),
    ("firefox", "Firefox", ".xpi"),
    ("safari", "Safari", ".zip"),
    ("edge", "Edge", ".zip"),
    ("opera", "Opera", ".zip"),
    ("brave", "Brave", ".zip"),
]
for bid, bname, ext in browsers:
    add(f"eoffice-{bid}", f"eOffice for {bname}",
        f"Full eOffice productivity suite as a {bname} extension — eDocs, eSheets, eSlides, ePlanner, eNotes.",
        "browser-ext", [bid], ["productivity", "office", "docs", "sheets"],
        source=f"extensions/browser/{bid}/")

# eBrowser extensions
for bid, bname, ext in browsers:
    add(f"ebrowser-ext-{bid}", f"eBrowser for {bname}",
        f"eBrowser privacy tools and ad-blocker for {bname}.",
        "browser-ext", [bid], ["privacy", "security", "adblocker", "browser"],
        source=f"extensions/browser/{bid}/")

# eBot AI browser extensions
for bid, bname, ext in [("chrome","Chrome",".zip"), ("firefox","Firefox",".xpi"), ("edge","Edge",".zip")]:
    add(f"ebot-{bid}", f"eBot AI for {bname}",
        f"AI assistant chatbot extension for {bname} — ask questions, summarize pages, translate.",
        "browser-ext", [bid], ["ai", "chatbot", "assistant", "productivity"],
        source=f"extensions/browser/{bid}/")

# ═══════════════════════════════════════════════════════════
# IDE & DEV TOOLS EXTENSIONS
# ═══════════════════════════════════════════════════════════
ide_platforms = [
    ("vscode", "VS Code", "VS Code extension"),
    ("jetbrains", "JetBrains", "JetBrains IDE plugin"),
    ("obsidian", "Obsidian", "Obsidian plugin"),
    ("sublime", "Sublime Text", "Sublime Text package"),
    ("neovim", "Neovim", "Neovim/Vim plugin"),
]
for pid, pname, pdesc in ide_platforms:
    add(f"eoffice-{pid}", f"eOffice for {pname}",
        f"Access eOffice docs, sheets, and notes directly inside {pname}.",
        "ide-ext", [pid], ["productivity", "ide", "editor", "office"],
        source=f"extensions/{pid}/")

for pid, pname, pdesc in ide_platforms:
    add(f"eostudio-{pid}", f"EoStudio for {pname}",
        f"EoStudio code generation, UI preview, and hardware tools for {pname}.",
        "ide-ext", [pid], ["design", "ide", "codegen", "hardware"],
        source=f"extensions/{pid}/")

# Additional IDE integrations
ide_extras = [
    ("slack", "Slack", "Slack app"),
    ("raycast", "Raycast", "Raycast extension"),
    ("github", "GitHub", "GitHub App"),
    ("google-workspace", "Google Workspace", "Google Workspace add-on"),
    ("office365", "Office 365", "Office 365 add-in"),
]
for pid, pname, pdesc in ide_extras:
    add(f"eoffice-{pid}", f"eOffice for {pname}",
        f"eOffice integration for {pname} — collaborate on docs and sheets.",
        "ide-ext", [pid], ["productivity", "collaboration", "integration"],
        source=f"extensions/{pid}/")

# ═══════════════════════════════════════════════════════════
# MOBILE — ANDROID & TV
# ═══════════════════════════════════════════════════════════
mobile_apps_defs = [
    ("eride", "eRide", "Ride-sharing and transportation with real-time tracking, fare estimation.", ["transport", "ride-sharing", "maps"]),
    ("esocial", "eSocial", "Social networking with posts, feeds, messaging, and community features.", ["social", "messaging", "community"]),
    ("etrack", "eTrack", "Package and delivery tracking with real-time status updates.", ["logistics", "tracking", "delivery"]),
    ("etravel", "eTravel", "Travel planning and booking with itinerary management.", ["travel", "booking", "itinerary"]),
    ("ewallet", "eWallet", "Digital wallet with payments, transaction history, multi-currency.", ["fintech", "payments", "wallet"]),
]
for mid, mname, mdesc, mtags in mobile_apps_defs:
    add(f"{mid}-android", f"{mname} for Android",
        f"{mdesc} Available for Android Phone, Tablet, and Android TV.",
        "mobile-android", ["android", "android-tv", "android-tablet"],
        mtags + ["flutter", "android"],
        source=f"service-apps/lib/features/{mid}/")

# eOffice for Android
add("eoffice-android", "eOffice for Android",
    "Full eOffice suite on Android — eDocs, eSheets, eSlides, eNotes, ePlanner.",
    "mobile-android", ["android", "android-tablet", "android-tv"],
    ["productivity", "office", "android", "flutter"],
    source="desktop-apps/eoffice/")

# EoStudio for Android
add("eostudio-android", "EoStudio for Android",
    "Visual design IDE on Android tablet — UI design, code generation, preview.",
    "mobile-android", ["android", "android-tablet"],
    ["design", "ide", "codegen", "android"],
    source="desktop-apps/eostudio/")

# eBrowser for Android
add("ebrowser-android", "eBrowser for Android",
    "Privacy-first web browser for Android with ad-blocker and tracker protection.",
    "mobile-android", ["android", "android-tablet"],
    ["browser", "privacy", "android"],
    source="desktop-apps/ebrowser/")

# eBot AI for Android
add("ebot-android", "eBot AI for Android",
    "AI assistant chatbot with on-device and cloud LLM support.",
    "mobile-android", ["android", "android-tablet"],
    ["ai", "chatbot", "assistant", "android"],
    source="apps/ebot/")

# ═══════════════════════════════════════════════════════════
# MOBILE — iOS & iPadOS
# ═══════════════════════════════════════════════════════════
for mid, mname, mdesc, mtags in mobile_apps_defs:
    add(f"{mid}-ios", f"{mname} for iOS",
        f"{mdesc} Available for iPhone and iPad via TestFlight.",
        "mobile-ios", ["ios", "ipados"],
        mtags + ["flutter", "ios"],
        source=f"service-apps/lib/features/{mid}/")

add("eoffice-ios", "eOffice for iOS",
    "Full eOffice suite on iPhone and iPad — eDocs, eSheets, eSlides, eNotes, ePlanner.",
    "mobile-ios", ["ios", "ipados"],
    ["productivity", "office", "ios", "flutter"],
    source="desktop-apps/eoffice/")

add("eostudio-ios", "EoStudio for iPadOS",
    "Visual design IDE on iPad — UI design, code generation, 3D preview.",
    "mobile-ios", ["ipados"],
    ["design", "ide", "codegen", "ipados"],
    source="desktop-apps/eostudio/")

add("ebrowser-ios", "eBrowser for iOS",
    "Privacy-first web browser for iPhone and iPad.",
    "mobile-ios", ["ios", "ipados"],
    ["browser", "privacy", "ios"],
    source="desktop-apps/ebrowser/")

add("ebot-ios", "eBot AI for iOS",
    "AI assistant chatbot for iPhone and iPad.",
    "mobile-ios", ["ios", "ipados"],
    ["ai", "chatbot", "assistant", "ios"],
    source="apps/ebot/")

# ═══════════════════════════════════════════════════════════
# DESKTOP — Windows / macOS / Linux / EoS / ARM
# ═══════════════════════════════════════════════════════════
desktop_apps = [
    ("eoffice-desktop", "eOffice Desktop", "Full office suite — eDocs, eSheets, eSlides, ePlanner, eNotes, eMail, eDrive, eConnect, eForms, eSway.",
     ["productivity", "office", "electron"], "desktop-apps/eoffice/"),
    ("eostudio-desktop", "EoStudio", "Visual design studio & IDE — UI, 3D, CAD, games, hardware, code generation, simulation.",
     ["design", "ide", "cad", "3d", "codegen", "python"], "desktop-apps/eostudio/"),
    ("eosim-desktop", "EoSim", "Hardware & platform simulator — 63+ boards (ARM, RISC-V, ESP32, STM32, RPi, Jetson), QEMU, native engine, GUI renderers.",
     ["simulator", "hardware", "qemu", "embedded", "python"], "desktop-apps/eosim/"),
    ("ebrowser-desktop", "eBrowser", "Privacy-first web browser with custom rendering engine, HTML5, CSS3, JS, SVG, TLS 1.3, plugins.",
     ["browser", "privacy", "security", "c", "lvgl"], "desktop-apps/ebrowser/"),
]
for did, dname, ddesc, dtags, dsrc in desktop_apps:
    add(did, dname, ddesc, "desktop",
        ["windows-x64", "windows-arm64", "macos-intel", "macos-apple-silicon", "linux-x64", "linux-arm64", "eos", "freebsd"],
        dtags, source=dsrc,
        downloads={
            "windows-x64": f"{base}/{did}-v1.0.0/{did}-1.0.0-win-x64.zip",
            "windows-arm64": f"{base}/{did}-v1.0.0/{did}-1.0.0-win-arm64.zip",
            "macos-intel": f"{base}/{did}-v1.0.0/{did}-1.0.0-macos-x64.zip",
            "macos-apple-silicon": f"{base}/{did}-v1.0.0/{did}-1.0.0-macos-arm64.zip",
            "linux-x64": f"{base}/{did}-v1.0.0/{did}-1.0.0-linux-x64.zip",
            "linux-arm64": f"{base}/{did}-v1.0.0/{did}-1.0.0-linux-arm64.zip",
        })

# ═══════════════════════════════════════════════════════════
# NATIVE / EMBEDDED APPS (40+ LVGL apps)
# ═══════════════════════════════════════════════════════════
native_apps = [
    ("efiles", "eFiles", "File manager with dual-pane view, archive support, and network browsing."),
    ("emusic", "eMusic", "Music player with playlist management, equalizer, and format support."),
    ("evideo", "eVideo", "Video player supporting multiple codecs and subtitle formats."),
    ("egallery", "eGallery", "Image gallery and viewer with album management and slideshow."),
    ("echat", "eChat", "Instant messaging with end-to-end encryption, group chats, and file sharing."),
    ("enote", "eNote", "Quick notes and to-do lists with Markdown support."),
    ("ecal", "eCal", "Calendar with event management, reminders, and multi-calendar sync."),
    ("eclock", "eClock", "World clock, alarms, stopwatch, and countdown timer."),
    ("esettings", "eSettings", "System settings and preferences manager."),
    ("ewifi", "eWifi", "Wi-Fi network manager with scanning and diagnostics."),
    ("evpn", "eVPN", "VPN client with WireGuard and OpenVPN support."),
    ("essh", "eSSH", "SSH terminal client with key management and session bookmarks."),
    ("eftp", "eFTP", "FTP/SFTP client for file transfers."),
    ("epdf", "ePDF", "PDF viewer and annotator."),
    ("epaint", "ePaint", "Drawing and image editing application."),
    ("econverter", "eConverter", "Unit converter for length, weight, temperature, currency."),
    ("ezip", "eZip", "Archive manager supporting ZIP, TAR, GZIP, 7z."),
    ("eguard", "eGuard", "Security suite — antivirus, firewall, privacy protection."),
    ("ecleaner", "eCleaner", "System cleaner and optimizer."),
    ("eremote", "eRemote", "Remote desktop client with RDP and VNC support."),
    ("evnc", "eVNC", "VNC server and viewer for remote access."),
    ("eserial", "eSerial", "Serial port terminal and debugger for embedded development."),
    ("ebot", "eBot", "AI assistant chatbot with local and cloud model support."),
    ("etools", "eTools", "Developer and system utility toolbox."),
    ("etunnel", "eTunnel", "Secure tunneling and port forwarding utility."),
    ("snake", "Snake", "Classic snake game with modern visuals."),
    ("tetris", "Tetris", "Classic block-stacking puzzle game."),
    ("minesweeper", "Minesweeper", "Classic minesweeper with multiple difficulty levels."),
    ("echess", "eChess", "Chess game with AI opponent and online multiplayer."),
    ("dice", "Dice", "Dice rolling simulator for board games."),
    ("eplay", "ePlay", "Game launcher and media hub."),
    ("ehmi", "eHMI", "Human-Machine Interface designer for IoT/automotive."),
    ("esurfer", "eSurfer", "Lightweight web surfer for quick searches."),
    ("etimer", "eTimer", "Pomodoro timer and productivity tracker."),
    ("erunner", "eRunner", "Application launcher and command runner."),
    ("eviewer", "eViewer", "Universal file viewer for images, documents, and code."),
    ("ebuffer", "eBuffer", "Text and clipboard buffer manager."),
    ("eslice", "eSlice", "Screen capture and screenshot annotation tool."),
    ("esession", "eSession", "Session and window manager for EoS desktop."),
    ("suite", "EoS Suite Launcher", "Unified launcher for all EoS applications."),
    ("ecrush", "eCrush", "Match-3 puzzle game with combos and power-ups."),
    ("ebirds", "eBirds", "Physics-based launcher game with destructible environments."),
    ("eblocks", "eBlocks", "Block-breaker game with paddle and power-ups."),
    ("evirustower", "eVirusTower", "Tower defense game with virus waves and upgrades."),
    ("eweb", "eWeb", "Lightweight embedded web browser component."),
    ("eplay", "ePlay", "Game launcher and media hub."),
]
seen_native = set()
for nid, nname, ndesc in native_apps:
    if nid in seen_native:
        continue
    seen_native.add(nid)
    add(nid, nname, ndesc, "native",
        ["eos", "windows", "linux", "macos", "android", "ios", "web", "freebsd"],
        ["native", "lvgl", "c", "embedded"],
        source=f"apps/{nid}/")

# ═══════════════════════════════════════════════════════════
# CLOUD & SERVICES
# ═══════════════════════════════════════════════════════════
add("eserviceapps-backend", "eServiceApps Backend",
    "Firebase-powered backend — auth, Firestore, notifications, wallet APIs.",
    "service", ["firebase", "cloud"], ["backend", "firebase", "api", "auth"],
    source="service-apps/")

add("eoffice-server", "eOffice Server",
    "Self-hosted eOffice backend for document collaboration, real-time sync, storage. Docker deployable.",
    "service", ["docker", "cloud"], ["backend", "docker", "collaboration", "self-hosted"],
    source="desktop-apps/eoffice/packages/server/")

add("eoffice-web", "eOffice Web",
    "Full eOffice suite in the browser — eDocs, eSheets, eSlides, ePlanner, eNotes.",
    "service", ["web", "pwa"], ["productivity", "office", "web", "pwa"],
    dl_url="https://embeddedos-org.github.io/eApps/",
    source="desktop-apps/eoffice/browser/")

add("ebrowser-wasm", "eBrowser WASM",
    "eBrowser running in the browser via WebAssembly — no install required.",
    "service", ["web", "wasm"], ["browser", "wasm", "web"],
    source="desktop-apps/ebrowser/")

# ═══════════════════════════════════════════════════════════
# OS & VM IMAGES
# ═══════════════════════════════════════════════════════════
os_images = [
    ("eos-desktop-x64", "EoS Desktop (x86_64)", "EoS Desktop operating system ISO for x86_64 PCs and laptops.",
     ["x86_64", "iso"], ["os", "desktop", "x86_64", "iso"]),
    ("eos-desktop-arm64", "EoS Desktop (ARM64)", "EoS Desktop operating system ISO for ARM64 devices (Raspberry Pi, Apple Silicon VMs).",
     ["arm64", "iso"], ["os", "desktop", "arm64", "iso"]),
    ("eos-server-x64", "EoS Server (x86_64)", "EoS Server operating system ISO for headless servers and cloud VMs.",
     ["x86_64", "iso"], ["os", "server", "x86_64", "iso"]),
    ("eos-server-arm64", "EoS Server (ARM64)", "EoS Server operating system ISO for ARM64 servers.",
     ["arm64", "iso"], ["os", "server", "arm64", "iso"]),
    ("eos-embedded-stm32", "EoS Embedded (STM32)", "EoS firmware image for STM32 microcontrollers.",
     ["stm32", "firmware"], ["os", "embedded", "stm32", "firmware"]),
    ("eos-embedded-esp32", "EoS Embedded (ESP32)", "EoS firmware image for ESP32 microcontrollers.",
     ["esp32", "firmware"], ["os", "embedded", "esp32", "firmware"]),
    ("eos-embedded-rpi", "EoS Embedded (Raspberry Pi)", "EoS image for Raspberry Pi (Zero, 3, 4, 5).",
     ["rpi", "arm64", "img"], ["os", "embedded", "raspberry-pi", "img"]),
    ("eos-embedded-riscv", "EoS Embedded (RISC-V)", "EoS firmware for RISC-V development boards.",
     ["riscv", "firmware"], ["os", "embedded", "riscv", "firmware"]),
    ("eosim-virtualbox", "EoSim VirtualBox (OVA)", "Pre-configured EoSim development environment for VirtualBox. Import and run.",
     ["virtualbox", "ova"], ["simulator", "virtualbox", "vm", "ova"]),
    ("eosim-vmware", "EoSim VMware (VMDK)", "Pre-configured EoSim development environment for VMware Workstation/Fusion.",
     ["vmware", "vmdk"], ["simulator", "vmware", "vm", "vmdk"]),
    ("eosim-qemu", "EoSim QEMU (qcow2)", "EoSim disk image for QEMU — run with qemu-system-x86_64.",
     ["qemu", "qcow2"], ["simulator", "qemu", "vm", "qcow2"]),
    ("eosim-docker", "EoSim Docker", "EoSim as a Docker container — docker pull embeddedos/eosim.",
     ["docker"], ["simulator", "docker", "container"]),
    ("eos-liveusb", "EoS Live USB", "Bootable EoS Live USB image — try EoS without installing.",
     ["x86_64", "arm64", "iso"], ["os", "live", "usb", "iso"]),
]
for oid, oname, odesc, oplat, otags in os_images:
    add(oid, oname, odesc, "os-images", oplat, otags, source="")

# ═══════════════════════════════════════════════════════════
# WRITE
# ═══════════════════════════════════════════════════════════
with open("data/apps.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Generated {len(apps)} apps across {len(data['categories'])} categories")
for cat in data["categories"]:
    count = sum(1 for a in apps if a["category"] == cat["id"])
    print(f"  {cat['icon']} {cat['name']}: {count}")
