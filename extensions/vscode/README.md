# eOffice Suite — VS Code Extension

> Open and edit Excel, CSV, database, and document files using eOffice tools directly in VS Code.

## ✨ Features

| Feature | Description |
|---------|-------------|
| **eDocs** | Rich document editing in a webview panel |
| **eNotes** | Digital notebooks for quick notes and ideas |
| **eSheets** | Spreadsheet viewer and CSV editor with inline cell editing |
| **eBot AI** | AI chat assistant — summarize, rewrite, and analyze text |
| **CSV Editor** | Custom editor for `.csv` and `.tsv` files with table UI |
| **Sidebar** | Activity bar with Apps, Recent Files, and eBot AI views |
| **Context Menu** | Right-click selected text to summarize or rewrite with eBot |

## 📦 Installation

### From VSIX

1. Build the extension:
   ```bash
   cd extensions/vscode
   npm install
   npm run compile
   npx @vscode/vsce package
   ```
2. Install the generated `.vsix` file in VS Code:
   - Open **Extensions** sidebar → `...` menu → **Install from VSIX...**
   - Select the `eoffice-vscode-0.1.0.vsix` file

### For Development

```bash
cd extensions/vscode
npm install
npm run watch
```

Then press `F5` in VS Code to launch the Extension Development Host.

## 🚀 Commands

Open the **Command Palette** (`Ctrl+Shift+P` / `Cmd+Shift+P`) and type `eOffice`:

| Command | Description |
|---------|-------------|
| `eOffice: Open eDocs` | Open the eDocs word processor |
| `eOffice: Open eNotes` | Open the eNotes notebook |
| `eOffice: Open eSheets` | Open the eSheets spreadsheet |
| `eOffice: Open Suite Launcher` | Open the full eOffice launcher |
| `eOffice: Open eBot AI Chat` | Open the eBot AI chat panel |
| `eOffice: Summarize Selection with eBot` | Summarize selected text using eBot |
| `eOffice: Rewrite Selection with eBot` | Rewrite selected text using eBot |

## ⌨️ Keyboard Shortcuts

| Shortcut | Command |
|----------|---------|
| `Ctrl+Shift+D` / `Cmd+Shift+D` | Open eDocs |
| `Ctrl+Shift+N` / `Cmd+Shift+N` | Open eNotes |
| `Ctrl+Shift+B` / `Cmd+Shift+B` | Open eBot AI Chat |

## 📊 CSV Editor

When you open a `.csv` or `.tsv` file, VS Code will offer to open it with the **eSheets CSV Editor**:

- Inline cell editing with contenteditable table cells
- Add rows and columns dynamically
- Auto-save on cell edits (1-second debounce)
- Manual save button
- Row/column count display

The CSV editor is registered with `"priority": "option"`, so VS Code will ask which editor to use. To always use it, right-click a CSV file → **Open With...** → **eSheets CSV Editor**.

## 🤖 eBot AI Integration

eBot connects to your local eOffice server for AI-powered features.

### Setup

1. Start the eOffice server:
   ```bash
   npm run dev:server
   ```
2. The extension connects to `http://localhost:3001/api/ebot/chat` by default.

### Configuration

Add to your VS Code `settings.json`:

```json
{
  "eoffice.ebotHost": "localhost",
  "eoffice.ebotPort": 3001
}
```

### Context Menu Actions

1. Select text in any editor
2. Right-click → choose:
   - **eOffice: Summarize Selection with eBot** — get a concise summary
   - **eOffice: Rewrite Selection with eBot** — get a clearer, more professional version
3. Choose to **Replace Selection**, **Copy to Clipboard**, or **Cancel**

### Chat Panel

- Click the 🤖 icon in the editor title bar, or use `Ctrl+Shift+B`
- Type messages to chat with eBot
- Click **📋 Insert to Editor** on any response to insert it at the cursor

## 🗂️ Sidebar

The extension adds an **eOffice** icon to the Activity Bar with three views:

1. **Apps** — Quick launch for all eOffice apps (eDocs, eNotes, eSheets, etc.)
2. **Recent Files** — Recently opened files tracked by the extension
3. **eBot AI** — Quick access to the AI assistant

## 📁 Project Structure

```
extensions/vscode/
├── assets/
│   └── sidebar-icon.svg       # Activity bar icon
├── src/
│   ├── extension.ts            # Main entry point
│   ├── apps-provider.ts        # Sidebar Apps tree view
│   ├── recent-provider.ts      # Sidebar Recent Files tree view
│   └── csv-editor.ts           # Custom CSV/TSV editor
├── webview/                    # HTML files for app webviews
├── package.json                # Extension manifest
├── tsconfig.json               # TypeScript config
├── .vscodeignore               # Files excluded from VSIX
└── README.md                   # This file
```

## 📄 License

MIT © embeddedos
