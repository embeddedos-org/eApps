# 🛠️ Dev Tools & Extensions — EoS Developer Integrations

[![VSCode](https://img.shields.io/badge/VS_Code-Extension-blue?logo=visualstudiocode)]()
[![JetBrains](https://img.shields.io/badge/JetBrains-Plugin-purple?logo=jetbrains)]()
[![Vim](https://img.shields.io/badge/Vim-Plugin-green?logo=vim)]()

**IDE extensions, editor plugins, and developer tool integrations for the EoS ecosystem.**

Bring EoS tools directly into your development workflow across VS Code, JetBrains, Vim/Neovim, and more.

---

## 📦 Dev Tools (14 Developer Extensions)

| Tool | Description | VS Code | JetBrains | Vim/Neovim | Status |
|------|-------------|---------|-----------|------------|--------|
| **ebot** | AI coding assistant | ✅ Sidebar + inline | ✅ Tool window | ✅ Plugin | 🔲 Planned |
| **enote** | Code notes & snippets | ✅ Panel | ✅ Tool window | ✅ Buffer | 🔲 Planned |
| **epdf** | PDF/doc viewer in IDE | ✅ Custom editor | ✅ Tab | — | 🔲 Planned |
| **efiles** | Advanced file explorer | ✅ Tree view | ✅ Tool window | ✅ NERDTree-like | 🔲 Planned |
| **eviewer** | Binary/hex viewer | ✅ Custom editor | ✅ Tab | ✅ xxd integration | 🔲 Planned |
| **eserial** | Serial port monitor | ✅ Terminal panel | ✅ Tool window | — | 🔲 Planned |
| **etools** | Dev utility toolkit | ✅ Command palette | ✅ Actions | ✅ Commands | 🔲 Planned |
| **essh** | SSH manager in IDE | ✅ Remote SSH ext | ✅ Remote dev | — | 🔲 Planned |
| **eftp** | FTP/SFTP file transfer | ✅ Explorer panel | ✅ Tool window | — | 🔲 Planned |
| **erunner** | Task/script runner | ✅ Task provider | ✅ Run configs | ✅ :make | 🔲 Planned |
| **eslice** | Image slicer for assets | ✅ Custom editor | ✅ Tool window | — | 🔲 Planned |
| **ezip** | Archive browser in IDE | ✅ Custom editor | ✅ Tab | — | 🔲 Planned |
| **econverter** | Data format converter | ✅ Command palette | ✅ Actions | ✅ Commands | 🔲 Planned |
| **etimer** | Pomodoro/focus timer | ✅ Status bar | ✅ Widget | ✅ Status line | 🔲 Planned |

---

## 🏗️ Architecture

```
dev-tools/
├── README.md
├── shared/                        # Shared dev tool code
│   ├── protocol/                  # Common IPC/LSP protocol
│   ├── icons/                     # Shared icon assets
│   └── test-utils/                # Shared test utilities
├── ebot/
│   ├── vscode/                    # VS Code extension
│   │   ├── package.json
│   │   ├── tsconfig.json
│   │   └── src/
│   │       ├── extension.ts
│   │       ├── sidebar-provider.ts
│   │       └── inline-completion.ts
│   ├── jetbrains/                 # JetBrains plugin
│   │   ├── build.gradle.kts
│   │   ├── plugin.xml
│   │   └── src/main/kotlin/
│   └── vim/                       # Vim/Neovim plugin
│       ├── plugin/ebot.vim
│       └── lua/ebot/init.lua
└── [tool]/
    ├── vscode/
    ├── jetbrains/
    └── vim/
```

## 🚀 Quick Start

```bash
# VS Code extension development
cd dev-tools/ebot/vscode
npm install && npm run compile
# Press F5 in VS Code to launch Extension Development Host

# JetBrains plugin development
cd dev-tools/ebot/jetbrains
./gradlew buildPlugin
# Install via IDE → Settings → Plugins → Install from Disk

# Vim plugin (Neovim with lazy.nvim)
# Add to init.lua: { dir = "path/to/dev-tools/ebot/vim" }
```

## 📤 Distribution

| IDE | Format | Store |
|-----|--------|-------|
| VS Code | `.vsix` | VS Code Marketplace / Open VSX |
| JetBrains | `.jar` / `.zip` | JetBrains Marketplace |
| Vim/Neovim | Git repo | vim-plug / lazy.nvim / packer |
| Sublime Text | `.sublime-package` | Package Control |

## 📄 License

[Apache License 2.0](../LICENSE)
