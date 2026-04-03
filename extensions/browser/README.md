# eOffice Browser Extension

Offline-capable browser extension for Chrome, Edge, and Firefox.

## Install (Development)

### Chrome / Edge
1. Open `chrome://extensions` (or `edge://extensions`)
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select the `extensions/browser/` directory

### Firefox
1. Open `about:debugging#/runtime/this-firefox`
2. Click "Load Temporary Add-on"
3. Select `extensions/browser/manifest.json`

## Features
- 📝 eDocs — Word processor (offline)
- 📒 eNotes — Digital notebooks (offline)
- 📊 eSheets — Spreadsheets (offline)
- 📽️ eSlides — Presentations (offline)
- ✉️ eMail — Email client (offline)
- 🗄️ eDB — Database manager (offline)
- ☁️ eDrive — Cloud file manager (offline)
- 💬 eConnect — Team messaging (offline)
- 📋 eForms — Form builder & surveys (offline)
- 🎨 eSway — Design canvas (offline)
- 📅 ePlanner — Project planning (offline)
- 🤖 eBot AI — When server available at localhost:3001
- Right-click context menu: Open in eDocs, Save to eNotes, Summarize with eBot
- All data stored in browser extension storage
- Dark/Light mode
- Works offline — no server required for basic editing

## Build for Distribution

### Chrome Web Store
```bash
cd extensions/browser
zip -r eoffice-chrome.zip . -x "*.md" "*.git*"
# Upload to Chrome Web Store Developer Dashboard
```

### Firefox Add-ons
```bash
cd extensions/browser
web-ext build
# Upload to addons.mozilla.org
```

## Project Structure
```
extensions/browser/
├── manifest.json       # Extension manifest (MV3)
├── popup.html          # Toolbar popup launcher
├── background.js       # Service worker
├── options.html        # Settings page
├── README.md           # This file
├── icons/
│   └── icon.svg        # Source icon (convert to PNG for production)
└── apps/
    ├── edocs.html      # Word processor
    └── enotes.html     # Digital notebooks
```

## Icon Generation

The extension ships with an SVG icon. For production, convert to PNG at required sizes:

```bash
# Using ImageMagick
for size in 16 32 48 128; do
  convert icons/icon.svg -resize ${size}x${size} icons/icon${size}.png
done
```

## License

Part of the EmbeddedOS project by nicheOS.
