# eOffice Suite — Safari Web Extension

> Access eDocs, eNotes, eSheets, and all eOffice apps from Safari. Includes right-click "Summarize with eBot" on any webpage.

## ✨ Features

| Feature | Description |
|---------|-------------|
| **Popup Launcher** | Quick access to all 9 eOffice apps |
| **Context Menu** | Right-click → Open in eDocs, Save to eNotes, Summarize with eBot |
| **eBot Overlay** | AI summary displayed in a floating overlay on any webpage |
| **eBot Status** | Popup badge shows eBot server connectivity |
| **Storage Sync** | Recent apps tracked via browser storage |

## 📦 Installation

Safari Web Extensions require an Xcode wrapper app. Follow these steps:

### Prerequisites

- macOS 12+ (Monterey or later)
- Xcode 14+
- Safari 16.4+

### Build & Install

1. **Create the Xcode project wrapper:**
   ```bash
   xcrun safari-web-extension-converter extensions/safari/ \
     --project-location ./build/safari-extension \
     --app-name "eOffice Suite" \
     --bundle-identifier org.embeddedos.eoffice.safari
   ```

2. **Open in Xcode:**
   ```bash
   open build/safari-extension/eOffice\ Suite.xcodeproj
   ```

3. **Build & Run** (`⌘R`) in Xcode to install the extension.

4. **Enable in Safari:**
   - Open **Safari → Settings → Extensions**
   - Check **eOffice Suite** to enable
   - Grant permissions when prompted

### Enable Developer Settings (if needed)

1. Open **Safari → Settings → Advanced**
2. Check **"Show features for web developers"**
3. Open **Safari → Develop** menu → **Allow Unsigned Extensions**

## 🗂️ Project Structure

```
extensions/safari/
├── manifest.json     # WebExtension manifest (MV3)
├── popup.html        # Toolbar popup UI
├── popup.js          # Popup logic
├── background.js     # Service worker (eBot API, context menus)
├── content.js        # Content script (summary overlay)
├── Info.plist        # Safari extension metadata
├── icons/            # Extension icons (generate from SVG)
└── README.md         # This file
```

## 🤖 eBot Integration

The extension connects to the eOffice backend at `http://localhost:3001`.

1. Start the eOffice server:
   ```bash
   npm run dev:server
   ```

2. The popup badge shows connection status:
   - 🤖 eBot ✓ — Server connected
   - 🤖 eBot ✗ — Server unreachable

### Context Menu Actions

1. Select text on any webpage
2. Right-click → choose:
   - **Open in eDocs** — Opens the text in the eDocs word processor
   - **Save to eNotes** — Saves the selection as a new note
   - **Summarize with eBot** — Displays an AI summary overlay

## 🖼️ Icon Generation

```bash
# Using ImageMagick
for size in 16 32 48 128; do
  convert icons/icon.svg -resize ${size}x${size} icons/icon${size}.png
done
```

## 📄 License

MIT © embeddedos — Part of the EmbeddedOS project by nicheOS.
