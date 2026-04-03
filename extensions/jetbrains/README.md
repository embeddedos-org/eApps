# eOffice Suite — JetBrains Plugin

> Access eDocs, eNotes, eSheets, and eBot AI directly from IntelliJ IDEA, WebStorm, PyCharm, and other JetBrains IDEs.

## ✨ Features

| Feature | Description |
|---------|-------------|
| **Sidebar Tool Window** | Apps, Recent Files, and eBot AI chat tabs |
| **Menu Actions** | Tools → eOffice → Open eDocs / eNotes / eSheets / eBot Chat |
| **Context Menu** | Right-click selected text → Summarize with eBot / Rewrite with eBot |
| **File Types** | Associations for `.edoc`, `.enote`, `.esheet` files |
| **eBot Chat** | Interactive AI chat in the sidebar tool window |

## 📦 Build & Install

### Prerequisites

- JDK 17+
- Gradle 8+ (or use the Gradle wrapper)
- IntelliJ IDEA 2023.1+

### Build

```bash
cd extensions/jetbrains
./gradlew buildPlugin
```

The plugin ZIP will be in `build/distributions/`.

### Install

1. Open your JetBrains IDE
2. Go to **Settings → Plugins → ⚙️ → Install Plugin from Disk...**
3. Select the ZIP from `build/distributions/`
4. Restart the IDE

### For Development

1. Open the `extensions/jetbrains/` directory in IntelliJ IDEA
2. The Gradle project will auto-import
3. Run → **Run Plugin** (or use the `runIde` Gradle task)
4. A sandboxed IDE instance launches with the plugin installed

```bash
./gradlew runIde
```

## 🚀 Usage

### Sidebar Tool Window

Click the **eOffice** tab on the right sidebar:

- **Apps** — Click any app name to open it in the browser
- **Recent Files** — Shows recently opened eOffice files
- **eBot** — Interactive AI chat panel

### Menu Actions

Go to **Tools → eOffice**:

| Action | Description |
|--------|-------------|
| Open eDocs | Opens eDocs word processor in browser |
| Open eNotes | Opens eNotes notebooks in browser |
| Open eSheets | Opens eSheets spreadsheets in browser |
| eBot Chat | Opens eBot AI chat in browser |

### Context Menu Actions

1. Select text in any editor
2. Right-click → **eOffice** → choose:
   - **Summarize with eBot** — Get an AI summary
   - **Rewrite with eBot** — Get a clearer version
3. Choose **Replace Selection**, **Copy to Clipboard**, or **Cancel**

## 🤖 eBot Integration

The plugin connects to the eOffice backend at `http://localhost:3001`.

1. Start the eOffice server:
   ```bash
   npm run dev:server
   ```

2. eBot features will automatically connect to the server.

## 🗂️ Project Structure

```
extensions/jetbrains/
├── plugin.xml                                    # Plugin descriptor (reference copy)
├── build.gradle.kts                              # Gradle build config
├── src/main/kotlin/org/embeddedos/eoffice/
│   ├── EOfficePlugin.kt                          # Service, open app actions
│   ├── EBotAction.kt                             # Summarize & rewrite actions
│   └── EOfficeToolWindow.kt                      # Sidebar tool window
├── src/main/resources/META-INF/
│   └── plugin.xml                                # Plugin descriptor (canonical)
└── README.md                                     # This file
```

## 📄 License

MIT © embeddedos — Part of the EmbeddedOS project by nicheOS.
