# eOffice Sync — Obsidian Plugin

> Bidirectional sync between Obsidian and eOffice eNotes, plus eBot AI for summarization and outline generation.

## ✨ Features

| Feature | Description |
|---------|-------------|
| **Sync vault → eNotes** | Push all Obsidian markdown files to eNotes |
| **Import from eNotes** | Pull notes from eNotes into your vault |
| **eBot: Summarize** | AI-powered summarization appended to current note |
| **eBot: Generate outline** | AI-generated structured outline from note content |
| **Auto-sync** | Configurable automatic sync interval |
| **Status bar** | Sync status indicator in the Obsidian status bar |
| **Ribbon icon** | Quick-access sync button in the sidebar ribbon |
| **Settings tab** | Configure backend URL, sync interval, auto-sync toggle |

## 📦 Installation

### Manual Install

1. Build the plugin:
   ```bash
   cd extensions/obsidian
   npm install
   npm run build
   ```

2. Copy to your vault's plugins directory:
   ```bash
   mkdir -p /path/to/vault/.obsidian/plugins/eoffice-sync
   cp main.js manifest.json styles.css /path/to/vault/.obsidian/plugins/eoffice-sync/
   ```

3. In Obsidian:
   - Open **Settings → Community Plugins**
   - Disable **Safe mode** (if not already)
   - Click **Reload plugins**
   - Enable **eOffice Sync**

### Install via BRAT

1. Install the [BRAT plugin](https://github.com/TfTHacker/obsidian42-brat)
2. In BRAT settings, add the repository: `nicheOS/eOffice`
3. BRAT will automatically install and update the plugin

### For Development

```bash
cd extensions/obsidian
npm install
npm run dev
```

This watches for changes and rebuilds automatically. Symlink the output to your vault:

```bash
# macOS / Linux
ln -s $(pwd) /path/to/vault/.obsidian/plugins/eoffice-sync

# Windows
mklink /D "C:\path\to\vault\.obsidian\plugins\eoffice-sync" "%CD%"
```

## 🚀 Commands

Open the **Command Palette** (`Ctrl/Cmd + P`) and type `eOffice`:

| Command | Description |
|---------|-------------|
| **eBot: Summarize current note** | Sends the note to eBot and appends an AI summary |
| **eBot: Generate outline from note** | Creates a structured outline from the note content |
| **Sync vault to eNotes** | Pushes all markdown files to eNotes |
| **Import from eNotes** | Pulls all eNotes into an "eNotes Import" folder |

## ⚙️ Settings

| Setting | Default | Description |
|---------|---------|-------------|
| **Backend URL** | `http://localhost:3001` | eOffice server address |
| **Sync interval** | 5 minutes | Auto-sync frequency (1–60 min) |
| **Auto-sync** | Off | Enable automatic background sync |

## 🤖 eBot Integration

eBot connects to the eOffice server's AI endpoint.

1. Start the eOffice server:
   ```bash
   npm run dev:server
   ```

2. The status bar shows connection status:
   - 📎 eOffice: Ready — Plugin loaded
   - 🔄 eOffice: Syncing... — Sync in progress
   - ✅ eOffice: Synced — Sync complete
   - ❌ eOffice: Error — Server unreachable

## 🗂️ Project Structure

```
extensions/obsidian/
├── main.ts           # Main plugin code
├── manifest.json     # Obsidian plugin manifest
├── styles.css        # eBot response styling
├── package.json      # Build dependencies
├── tsconfig.json     # TypeScript config
└── README.md         # This file
```

## 📄 License

MIT © embeddedos — Part of the EmbeddedOS project by nicheOS.
