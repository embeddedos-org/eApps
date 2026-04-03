"""Desktop application code generator for EoStudio UI components."""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List


class DesktopAppGenerator:
    """Generates desktop application source files from eostudio component trees.

    Supported targets: ``electron``, ``tauri``, ``tkinter``, ``qt``,
    ``compose_desktop``.
    """

    COMPONENT_MAPS: Dict[str, Dict[str, str]] = {
        "electron": {
            "Button": "button", "Text": "p", "Input": "input",
            "Container": "div", "Card": "div.card", "AppBar": "header",
            "BottomNav": "nav", "List": "ul", "Grid": "div.grid",
            "Image": "img", "Dialog": "dialog", "TabBar": "div.tabs",
        },
        "tauri": {
            "Button": "button", "Text": "p", "Input": "input",
            "Container": "div", "Card": "div.card", "AppBar": "header",
            "BottomNav": "nav", "List": "ul", "Grid": "div.grid",
            "Image": "img", "Dialog": "dialog", "TabBar": "div.tabs",
        },
        "tkinter": {
            "Button": "ttk.Button", "Text": "ttk.Label", "Input": "ttk.Entry",
            "Container": "ttk.Frame", "Card": "ttk.LabelFrame",
            "AppBar": "tk.Menu", "BottomNav": "ttk.Frame",
            "List": "tk.Listbox", "Grid": "ttk.Frame", "Image": "tk.Label",
            "Dialog": "tk.Toplevel", "TabBar": "ttk.Notebook",
        },
        "qt": {
            "Button": "QPushButton", "Text": "QLabel", "Input": "QLineEdit",
            "Container": "QWidget", "Card": "QGroupBox", "AppBar": "QMenuBar",
            "BottomNav": "QToolBar", "List": "QListWidget",
            "Grid": "QGridLayout", "Image": "QLabel", "Dialog": "QDialog",
            "TabBar": "QTabWidget",
        },
        "compose_desktop": {
            "Button": "Button", "Text": "Text", "Input": "OutlinedTextField",
            "Container": "Column", "Card": "Card", "AppBar": "TopAppBar",
            "BottomNav": "NavigationBar", "List": "LazyColumn",
            "Grid": "LazyVerticalGrid", "Image": "Image",
            "Dialog": "AlertDialog", "TabBar": "TabRow",
        },
    }

    SUPPORTED_TARGETS = ("electron", "tauri", "tkinter", "qt", "compose_desktop")

    def __init__(self, target: str = "electron") -> None:
        """Initialise the generator for *target*.

        Raises:
            ValueError: If *target* is not supported.
        """
        if target not in self.SUPPORTED_TARGETS:
            raise ValueError(
                f"Unknown target {target!r}. "
                f"Supported: {', '.join(self.SUPPORTED_TARGETS)}"
            )
        self._target = target

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate(
        self,
        screens: List[Dict[str, Any]],
        app_name: str = "EoStudioApp",
    ) -> Dict[str, str]:
        """Generate a full desktop-app project for the configured target.

        Args:
            screens: Screen dicts with ``name`` and ``components``.
            app_name: Application display name.

        Returns:
            Mapping of relative filename to source content.
        """
        dispatch = {
            "electron": self._generate_electron,
            "tauri": self._generate_tauri,
            "tkinter": self._generate_tkinter,
            "qt": self._generate_qt,
            "compose_desktop": self._generate_compose_desktop,
        }
        return dispatch[self._target](screens, app_name)

    def _map_component(self, component_dict: Dict[str, Any], target: str) -> str:
        """Map a UI component type to its platform widget name."""
        ctype = component_dict.get("type", "Container")
        mapping = self.COMPONENT_MAPS.get(target, {})
        return mapping.get(ctype, mapping.get("Container", "div"))

    # ------------------------------------------------------------------
    # Electron
    # ------------------------------------------------------------------

    def _generate_electron(self, screens: List[Dict[str, Any]], app_name: str) -> Dict[str, str]:
        if not screens:
            screens = [{"name": "Home", "components": []}]
        return {
            "main.js": self._electron_main_js(screens, app_name),
            "preload.js": self._electron_preload_js(),
            "index.html": self._electron_index_html(screens, app_name),
            "renderer.js": self._electron_renderer_js(screens),
            "styles.css": self._electron_styles_css(),
            "package.json": self._electron_package_json(app_name),
        }

    def _electron_main_js(self, screens: List[Dict[str, Any]], app_name: str) -> str:
        menu = []
        for s in screens:
            n = s.get("name", "Home")
            menu.append(f"        {{ label: '{n}', click: () => mainWindow.webContents.send('navigate', '{self._kebab(n)}') }}")
        ipc = []
        for s in screens:
            n = s.get("name", "Home")
            h = self._kebab(n)
            ipc.append(
                f"  ipcMain.handle('get-{h}-data', async () => {{\n"
                f"    return {{ screen: '{n}', timestamp: Date.now() }};\n"
                "  });"
            )
        return (
            "const { app, BrowserWindow, Menu, Tray, ipcMain } = require('electron');\n"
            "const path = require('path');\n\n"
            "let mainWindow = null;\nlet tray = null;\n\n"
            "function createWindow() {\n"
            "  mainWindow = new BrowserWindow({\n"
            f"    title: '{app_name}', width: 1200, height: 800,\n"
            "    minWidth: 800, minHeight: 600,\n"
            "    webPreferences: {\n"
            "      preload: path.join(__dirname, 'preload.js'),\n"
            "      contextIsolation: true, nodeIntegration: false,\n"
            "    },\n  });\n"
            "  mainWindow.loadFile('index.html');\n"
            "  mainWindow.on('closed', () => { mainWindow = null; });\n}\n\n"
            "function createMenu() {\n"
            "  const template = [\n"
            "    { label: 'File', submenu: [\n"
            "      { label: 'New Window', accelerator: 'CmdOrCtrl+N', click: createWindow },\n"
            "      { type: 'separator' }, { role: 'quit' },\n"
            "    ]},\n"
            "    { label: 'View', submenu: [\n"
            + ",\n".join(menu) + "\n"
            "    ]},\n"
            "    { label: 'Help', submenu: [\n"
            f"      {{ label: 'About {app_name}', click: () => {{}} }},\n"
            "    ]},\n  ];\n"
            "  Menu.setApplicationMenu(Menu.buildFromTemplate(template));\n}\n\n"
            "function createTray() {\n"
            "  tray = new Tray(path.join(__dirname, 'icon.png'));\n"
            f"  tray.setToolTip('{app_name}');\n"
            "  tray.on('click', () => {\n"
            "    if (mainWindow) mainWindow.isVisible() ? mainWindow.hide() : mainWindow.show();\n"
            "  });\n}\n\n"
            + "\n".join(ipc) + "\n\n"
            "app.whenReady().then(() => {\n"
            "  createWindow(); createMenu(); createTray();\n"
            "  app.on('activate', () => {\n"
            "    if (BrowserWindow.getAllWindows().length === 0) createWindow();\n"
            "  });\n});\n\n"
            "app.on('window-all-closed', () => {\n"
            "  if (process.platform !== 'darwin') app.quit();\n});\n"
        )

    def _electron_preload_js(self) -> str:
        return (
            "const { contextBridge, ipcRenderer } = require('electron');\n\n"
            "contextBridge.exposeInMainWorld('electronAPI', {\n"
            "  invoke: (channel, ...args) => ipcRenderer.invoke(channel, ...args),\n"
            "  send: (channel, ...args) => ipcRenderer.send(channel, ...args),\n"
            "  on: (channel, callback) => {\n"
            "    const sub = (_event, ...args) => callback(...args);\n"
            "    ipcRenderer.on(channel, sub);\n"
            "    return () => ipcRenderer.removeListener(channel, sub);\n"
            "  },\n});\n"
        )

    def _electron_index_html(self, screens: List[Dict[str, Any]], app_name: str) -> str:
        nav = []
        secs = []
        for i, s in enumerate(screens):
            n = s.get("name", "Home")
            sid = self._kebab(n)
            ac = ' class="active"' if i == 0 else ""
            nav.append(f'      <button data-screen="{sid}"{ac}>{n}</button>')
            disp = "block" if i == 0 else "none"
            body = self._render_html_components(s.get("components", []), 4)
            secs.append(
                f'    <section id="{sid}" style="display:{disp}">\n'
                f"      <h2>{n}</h2>\n{body}    </section>"
            )
        return (
            "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n"
            "  <meta charset=\"UTF-8\" />\n"
            "  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />\n"
            f"  <title>{app_name}</title>\n"
            "  <link rel=\"stylesheet\" href=\"styles.css\" />\n"
            "</head>\n<body>\n"
            "  <header class=\"app-bar\">\n"
            f"    <h1>{app_name}</h1>\n    <nav>\n"
            + "\n".join(nav) + "\n    </nav>\n  </header>\n"
            "  <main id=\"app-content\">\n"
            + "\n".join(secs) + "\n  </main>\n"
            "  <footer class=\"bottom-nav\" id=\"bottom-nav\"></footer>\n"
            "  <script src=\"renderer.js\"></script>\n"
            "</body>\n</html>\n"
        )

    def _render_html_components(self, components: List[Dict[str, Any]], indent: int) -> str:
        lines: List[str] = []
        pad = "  " * indent
        for c in components:
            ct = c.get("type", "Container")
            lb = c.get("label", c.get("text", ""))
            ch = c.get("children", [])
            src = c.get("src", "")
            if ct == "Button":
                lines.append(f'{pad}<button class="btn">{lb}</button>\n')
            elif ct == "Text":
                lines.append(f"{pad}<p>{lb}</p>\n")
            elif ct == "Input":
                ph = c.get("placeholder", lb)
                lines.append(f'{pad}<input type="text" class="input" placeholder="{ph}" />\n')
            elif ct == "Container":
                d = c.get("direction", "column")
                cls = "container-row" if d == "row" else "container"
                lines.append(f'{pad}<div class="{cls}">\n{self._render_html_components(ch, indent + 1)}{pad}</div>\n')
            elif ct == "Card":
                inner = self._render_html_components(ch, indent + 1) if ch else f"{pad}  <p>{lb}</p>\n"
                lines.append(f'{pad}<div class="card">\n{inner}{pad}</div>\n')
            elif ct == "AppBar":
                lines.append(f'{pad}<header class="app-bar"><h1>{lb}</h1></header>\n')
            elif ct == "BottomNav":
                lines.append(f'{pad}<nav class="bottom-nav">\n{self._render_html_components(ch, indent + 1)}{pad}</nav>\n')
            elif ct == "List":
                items = c.get("items", [lb] if lb else ["Item"])
                li = "".join(f"{pad}  <li>{it}</li>\n" for it in items)
                lines.append(f"{pad}<ul>\n{li}{pad}</ul>\n")
            elif ct == "Grid":
                cols = c.get("columns", 3)
                lines.append(f'{pad}<div class="grid" style="grid-template-columns:repeat({cols},1fr)">\n{self._render_html_components(ch, indent + 1)}{pad}</div>\n')
            elif ct == "Image":
                lines.append(f'{pad}<img src="{src}" alt="{lb}" class="image" />\n')
            elif ct == "Dialog":
                did = self._kebab(lb or "dialog")
                inner = self._render_html_components(ch, indent + 1) if ch else f"{pad}  <p>{lb}</p>\n"
                lines.append(f'{pad}<dialog id="{did}">\n{inner}{pad}  <button class="btn" onclick="this.closest(\'dialog\').close()">Close</button>\n{pad}</dialog>\n')
            elif ct == "TabBar":
                tabs = c.get("tabs", ch)
                btns = ""
                panels = ""
                for ti, t in enumerate(tabs):
                    tn = t.get("label", t.get("name", f"Tab {ti + 1}"))
                    tid = self._kebab(tn)
                    ac = " active" if ti == 0 else ""
                    btns += f'{pad}    <button class="tab-btn{ac}" data-tab="{tid}">{tn}</button>\n'
                    disp = "block" if ti == 0 else "none"
                    tc = self._render_html_components(t.get("children", t.get("components", [])), indent + 2)
                    if not tc.strip():
                        tc = f"{pad}      <p>{tn} content</p>\n"
                    panels += f'{pad}    <div class="tab-panel" id="tab-{tid}" style="display:{disp}">\n{tc}{pad}    </div>\n'
                lines.append(f'{pad}<div class="tabs">\n{pad}  <div class="tab-bar">\n{btns}{pad}  </div>\n{panels}{pad}</div>\n')
            else:
                lines.append(f"{pad}<p>{lb}</p>\n")
        return "".join(lines)

    def _electron_renderer_js(self, screens: List[Dict[str, Any]]) -> str:
        ids = [self._kebab(s.get("name", "home")) for s in screens]
        arr = ", ".join(f"'{s}'" for s in ids)
        return (
            "document.addEventListener('DOMContentLoaded', () => {\n"
            f"  const screens = [{arr}];\n\n"
            "  document.querySelectorAll('nav button[data-screen]').forEach(btn => {\n"
            "    btn.addEventListener('click', () => showScreen(btn.dataset.screen));\n"
            "  });\n\n"
            "  document.querySelectorAll('.tab-btn').forEach(btn => {\n"
            "    btn.addEventListener('click', () => {\n"
            "      const parent = btn.closest('.tabs');\n"
            "      parent.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));\n"
            "      parent.querySelectorAll('.tab-panel').forEach(p => p.style.display = 'none');\n"
            "      btn.classList.add('active');\n"
            "      const panel = parent.querySelector(`#tab-${btn.dataset.tab}`);\n"
            "      if (panel) panel.style.display = 'block';\n"
            "    });\n  });\n\n"
            "  if (window.electronAPI) {\n"
            "    window.electronAPI.on('navigate', id => showScreen(id));\n"
            "  }\n\n"
            "  function showScreen(id) {\n"
            "    screens.forEach(s => {\n"
            "      const el = document.getElementById(s);\n"
            "      if (el) el.style.display = s === id ? 'block' : 'none';\n"
            "    });\n"
            "    document.querySelectorAll('nav button[data-screen]').forEach(b => {\n"
            "      b.classList.toggle('active', b.dataset.screen === id);\n"
            "    });\n  }\n\n"
            "  async function fetchScreenData(screenId) {\n"
            "    if (!window.electronAPI) return null;\n"
            "    return window.electronAPI.invoke(`get-${screenId}-data`);\n"
            "  }\n});\n"
        )

    def _electron_styles_css(self) -> str:
        return (
            "*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }\n"
            "body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;\n"
            "  line-height: 1.6; color: #1a1a2e; background: #f8f9fa; }\n"
            ".app-bar { display: flex; align-items: center; gap: 24px; padding: 12px 24px;\n"
            "  background: #2563eb; color: #fff; }\n"
            ".app-bar h1 { font-size: 18px; font-weight: 600; }\n"
            ".app-bar nav { display: flex; gap: 8px; }\n"
            ".app-bar nav button { background: rgba(255,255,255,0.15); border: none; color: #fff;\n"
            "  padding: 6px 14px; border-radius: 4px; cursor: pointer; font-size: 13px; }\n"
            ".app-bar nav button.active, .app-bar nav button:hover { background: rgba(255,255,255,0.3); }\n"
            "#app-content { padding: 24px; max-width: 1200px; margin: 0 auto; }\n"
            ".container { display: flex; flex-direction: column; gap: 12px; }\n"
            ".container-row { display: flex; flex-direction: row; gap: 12px; flex-wrap: wrap; }\n"
            ".card { background: #fff; border-radius: 8px; padding: 16px;\n"
            "  box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin-bottom: 12px; }\n"
            ".btn { padding: 10px 20px; border: none; border-radius: 6px;\n"
            "  background: #2563eb; color: #fff; font-size: 14px; cursor: pointer; }\n"
            ".btn:hover { background: #1d4ed8; }\n"
            ".input { width: 100%; padding: 10px 12px; border: 1px solid #d1d5db;\n"
            "  border-radius: 6px; font-size: 14px; }\n"
            ".input:focus { outline: none; border-color: #2563eb; }\n"
            ".image { max-width: 100%; border-radius: 8px; }\n"
            ".grid { display: grid; gap: 12px; }\n"
            ".bottom-nav { position: fixed; bottom: 0; left: 0; right: 0; display: flex;\n"
            "  justify-content: space-around; padding: 8px; background: #fff;\n"
            "  border-top: 1px solid #e5e7eb; }\n"
            "ul { list-style: none; }\n"
            "ul li { padding: 10px 16px; border-bottom: 1px solid #e5e7eb; }\n"
            "dialog { border: none; border-radius: 12px; padding: 24px;\n"
            "  box-shadow: 0 8px 32px rgba(0,0,0,0.15); }\n"
            "dialog::backdrop { background: rgba(0,0,0,0.4); }\n"
            ".tabs { margin-bottom: 16px; }\n"
            ".tab-bar { display: flex; border-bottom: 2px solid #e5e7eb; }\n"
            ".tab-btn { padding: 10px 20px; border: none; background: none; cursor: pointer;\n"
            "  font-size: 14px; color: #6b7280; border-bottom: 2px solid transparent; margin-bottom: -2px; }\n"
            ".tab-btn.active { color: #2563eb; border-bottom-color: #2563eb; }\n"
            ".tab-panel { padding: 16px 0; }\n"
        )

    def _electron_package_json(self, app_name: str) -> str:
        return json.dumps({
            "name": self._kebab(app_name), "version": "1.0.0",
            "description": f"{app_name} â€” built with EoStudio", "main": "main.js",
            "scripts": {"start": "electron .", "dev": "electron . --enable-logging",
                        "build": "electron-builder --dir", "dist": "electron-builder"},
            "devDependencies": {"electron": "^28.0.0", "electron-builder": "^24.0.0"},
        }, indent=2) + "\n"

    # ------------------------------------------------------------------
    # Tauri
    # ------------------------------------------------------------------

    def _generate_tauri(self, screens: List[Dict[str, Any]], app_name: str) -> Dict[str, str]:
        if not screens:
            screens = [{"name": "Home", "components": []}]
        return {
            "src-tauri/src/main.rs": self._tauri_main_rs(screens, app_name),
            "src-tauri/Cargo.toml": self._tauri_cargo_toml(app_name),
            "src-tauri/tauri.conf.json": self._tauri_conf_json(app_name),
            "src/App.tsx": self._tauri_app_tsx(screens, app_name),
            "src/main.tsx": self._tauri_main_tsx(),
            "package.json": self._tauri_package_json(app_name),
        }

    def _tauri_main_rs(self, screens: List[Dict[str, Any]], app_name: str) -> str:
        cmds = []
        names = []
        for s in screens:
            fn = self._snake(s.get("name", "Home"))
            n = s.get("name", "Home")
            cmds.append(
                "#[tauri::command]\n"
                f'fn get_{fn}_data() -> String {{\n'
                f'    format!("{{\\"screen\\": \\"{n}\\", \\"ts\\": {{}}}}", '
                "std::time::SystemTime::now()\n"
                "        .duration_since(std::time::UNIX_EPOCH).unwrap_or_default().as_millis())\n}"
            )
            names.append(f"get_{fn}_data")
        return (
            '#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]\n\n'
            + "\n\n".join(cmds) + "\n\n"
            "fn main() {\n"
            "    tauri::Builder::default()\n"
            f"        .invoke_handler(tauri::generate_handler![{', '.join(names)}])\n"
            "        .run(tauri::generate_context!())\n"
            f'        .expect("error while running {app_name}");\n'
            "}\n"
        )

    def _tauri_cargo_toml(self, app_name: str) -> str:
        return (
            "[package]\n"
            f'name = "{self._kebab(app_name)}"\nversion = "1.0.0"\nedition = "2021"\n\n'
            "[dependencies]\n"
            'tauri = { version = "1", features = ["shell-open"] }\n'
            'serde = { version = "1", features = ["derive"] }\n'
            'serde_json = "1"\n\n'
            "[build-dependencies]\n"
            'tauri-build = { version = "1", features = [] }\n'
        )

    def _tauri_conf_json(self, app_name: str) -> str:
        return json.dumps({
            "build": {"beforeDevCommand": "npm run dev", "beforeBuildCommand": "npm run build",
                      "devPath": "http://localhost:5173", "distDir": "../dist"},
            "package": {"productName": app_name, "version": "1.0.0"},
            "tauri": {
                "allowlist": {"all": False, "shell": {"all": False, "open": True}},
                "bundle": {"active": True, "identifier": f"com.EoStudio.{self._kebab(app_name)}", "targets": "all"},
                "windows": [{"fullscreen": False, "height": 800, "width": 1200, "resizable": True, "title": app_name}],
            },
        }, indent=2) + "\n"

    def _tauri_app_tsx(self, screens: List[Dict[str, Any]], app_name: str) -> str:
        state = "  const [activeScreen, setActiveScreen] = useState(0);\n"
        fetchers = []
        for s in screens:
            fn = self._snake(s.get("name", "Home"))
            p = self._pascal(s.get("name", "Home"))
            state += f"  const [{self._camel(s.get('name', 'Home'))}Data, set{p}Data] = useState<string | null>(null);\n"
            fetchers.append(
                f"  async function fetch{p}() {{\n"
                f"    const r = await invoke<string>('get_{fn}_data');\n"
                f"    set{p}Data(r);\n  }}"
            )
        nav = []
        panels = []
        for i, s in enumerate(screens):
            n = s.get("name", "Home")
            nav.append(f'          <button className={{activeScreen === {i} ? "active" : ""}} onClick={{() => setActiveScreen({i})}}>{n}</button>')
            body = self._render_html_components(s.get("components", []), 6)
            panels.append(f"        {{activeScreen === {i} && (\n          <section>\n            <h2>{n}</h2>\n{body}          </section>\n        )}}")
        return (
            "import { useState } from 'react';\nimport { invoke } from '@tauri-apps/api/tauri';\nimport './App.css';\n\n"
            "function App() {\n" + state + "\n" + "\n\n".join(fetchers) + "\n\n"
            "  return (\n    <div className=\"app\">\n"
            f"      <header className=\"app-bar\"><h1>{app_name}</h1>\n        <nav>\n"
            + "\n".join(nav) + "\n        </nav>\n      </header>\n"
            "      <main>\n" + "\n".join(panels) + "\n      </main>\n"
            "    </div>\n  );\n}\n\nexport default App;\n"
        )

    def _tauri_main_tsx(self) -> str:
        return (
            "import React from 'react';\nimport ReactDOM from 'react-dom/client';\nimport App from './App';\n\n"
            "ReactDOM.createRoot(document.getElementById('root')!).render(\n"
            "  <React.StrictMode><App /></React.StrictMode>\n);\n"
        )

    def _tauri_package_json(self, app_name: str) -> str:
        return json.dumps({
            "name": self._kebab(app_name), "version": "1.0.0", "private": True, "type": "module",
            "scripts": {"dev": "vite", "build": "tsc && vite build", "preview": "vite preview", "tauri": "tauri"},
            "dependencies": {"@tauri-apps/api": "^1.5.0", "react": "^18.2.0", "react-dom": "^18.2.0"},
            "devDependencies": {"@tauri-apps/cli": "^1.5.0", "@types/react": "^18.2.0",
                                "@types/react-dom": "^18.2.0", "@vitejs/plugin-react": "^4.0.0",
                                "typescript": "^5.0.0", "vite": "^5.0.0"},
        }, indent=2) + "\n"

    # ------------------------------------------------------------------
    # tkinter
    # ------------------------------------------------------------------

    def _generate_tkinter(self, screens: List[Dict[str, Any]], app_name: str) -> Dict[str, str]:
        if not screens:
            screens = [{"name": "Home", "components": []}]
        return {"app.py": self._tkinter_app_py(screens, app_name)}

    def _tkinter_app_py(self, screens: List[Dict[str, Any]], app_name: str) -> str:
        screen_methods: List[str] = []
        for s in screens:
            mname = self._snake(s.get("name", "Home"))
            label = s.get("name", "Home")
            body = self._tkinter_render_components(s.get("components", []), "frame", 2)
            screen_methods.append(
                f"    def _build_{mname}(self, parent):\n"
                f"        frame = ttk.Frame(parent)\n"
                f"        ttk.Label(frame, text='{label}', font=('Helvetica', 18, 'bold')).grid(\n"
                f"            row=0, column=0, columnspan=2, pady=(0, 12), sticky='w')\n"
                f"{body}"
                f"        return frame\n"
            )

        nav_btns: List[str] = []
        for i, s in enumerate(screens):
            n = s.get("name", "Home")
            sn = self._snake(n)
            nav_btns.append(
                f"        ttk.Button(nav, text='{n}',\n"
                f"                  command=lambda s='{sn}': self._show_screen(s)).pack(side='left', padx=4)"
            )

        screen_build: List[str] = []
        for s in screens:
            sn = self._snake(s.get("name", "Home"))
            screen_build.append(
                f"        self._screens['{sn}'] = self._build_{sn}(self._container)"
            )

        return (
            "\"\"\"" + app_name + " â€” tkinter desktop application.\"\"\"\n\n"
            "import tkinter as tk\n"
            "from tkinter import ttk, messagebox\n\n\n"
            "class App(tk.Tk):\n"
            f"    def __init__(self):\n"
            "        super().__init__()\n"
            f"        self.title('{app_name}')\n"
            "        self.geometry('1000x700')\n"
            "        self.minsize(800, 600)\n\n"
            "        self._build_menubar()\n"
            "        self._build_navbar()\n"
            "        self._build_statusbar()\n\n"
            "        self._container = ttk.Frame(self)\n"
            "        self._container.pack(fill='both', expand=True, padx=16, pady=8)\n\n"
            "        self._screens = {}\n"
            + "\n".join(screen_build) + "\n\n"
            "        self._current = None\n"
            f"        self._show_screen('{self._snake(screens[0].get('name', 'Home'))}')\n\n"
            "    def _build_menubar(self):\n"
            "        menubar = tk.Menu(self)\n"
            "        file_menu = tk.Menu(menubar, tearoff=0)\n"
            "        file_menu.add_command(label='New', accelerator='Ctrl+N')\n"
            "        file_menu.add_command(label='Open', accelerator='Ctrl+O')\n"
            "        file_menu.add_command(label='Save', accelerator='Ctrl+S')\n"
            "        file_menu.add_separator()\n"
            "        file_menu.add_command(label='Exit', command=self.quit)\n"
            "        menubar.add_cascade(label='File', menu=file_menu)\n"
            "        edit_menu = tk.Menu(menubar, tearoff=0)\n"
            "        edit_menu.add_command(label='Undo', accelerator='Ctrl+Z')\n"
            "        edit_menu.add_command(label='Redo', accelerator='Ctrl+Y')\n"
            "        edit_menu.add_separator()\n"
            "        edit_menu.add_command(label='Preferences')\n"
            "        menubar.add_cascade(label='Edit', menu=edit_menu)\n"
            "        help_menu = tk.Menu(menubar, tearoff=0)\n"
            f"        help_menu.add_command(label='About {app_name}',\n"
            f"                             command=lambda: messagebox.showinfo('About', '{app_name}'))\n"
            "        menubar.add_cascade(label='Help', menu=help_menu)\n"
            "        self.config(menu=menubar)\n\n"
            "    def _build_navbar(self):\n"
            "        nav = ttk.Frame(self)\n"
            "        nav.pack(fill='x', padx=8, pady=(8, 0))\n"
            + "\n".join(nav_btns) + "\n\n"
            "    def _build_statusbar(self):\n"
            "        self._status_var = tk.StringVar(value='Ready')\n"
            "        status = ttk.Label(self, textvariable=self._status_var, relief='sunken', anchor='w')\n"
            "        status.pack(fill='x', side='bottom', padx=2, pady=2)\n\n"
            "    def _show_screen(self, name):\n"
            "        if self._current:\n"
            "            self._current.pack_forget()\n"
            "        self._current = self._screens.get(name)\n"
            "        if self._current:\n"
            "            self._current.pack(fill='both', expand=True)\n"
            "        self._status_var.set(f'Screen: {name}')\n\n"
            + "\n\n".join(screen_methods) + "\n\n"
            "if __name__ == '__main__':\n"
            "    app = App()\n"
            "    app.mainloop()\n"
        )

    def _tkinter_render_components(self, components: List[Dict[str, Any]], parent: str, indent: int) -> str:
        lines: List[str] = []
        pad = "    " * indent
        row = 1
        for c in components:
            ct = c.get("type", "Container")
            lb = c.get("label", c.get("text", ""))
            ch = c.get("children", [])
            if ct == "Button":
                lines.append(f"{pad}ttk.Button({parent}, text='{lb}', command=lambda: None).grid(row={row}, column=0, pady=4, sticky='w')\n")
            elif ct == "Text":
                lines.append(f"{pad}ttk.Label({parent}, text='{lb}').grid(row={row}, column=0, pady=2, sticky='w')\n")
            elif ct == "Input":
                ph = c.get("placeholder", lb)
                var = self._snake(lb or "entry") + "_var"
                lines.append(f"{pad}{var} = tk.StringVar()\n")
                lines.append(f"{pad}ttk.Entry({parent}, textvariable={var}, width=40).grid(row={row}, column=0, pady=4, sticky='ew')\n")
            elif ct == "Container":
                fname = f"cont_{row}"
                lines.append(f"{pad}{fname} = ttk.Frame({parent})\n")
                lines.append(f"{pad}{fname}.grid(row={row}, column=0, columnspan=2, sticky='ew', pady=4)\n")
                lines.append(self._tkinter_render_components(ch, fname, indent))
            elif ct == "Card":
                fname = f"card_{row}"
                lines.append(f"{pad}{fname} = ttk.LabelFrame({parent}, text='{lb}', padding=10)\n")
                lines.append(f"{pad}{fname}.grid(row={row}, column=0, columnspan=2, sticky='ew', pady=4)\n")
                if ch:
                    lines.append(self._tkinter_render_components(ch, fname, indent))
                else:
                    lines.append(f"{pad}ttk.Label({fname}, text='{lb}').pack(anchor='w')\n")
            elif ct == "AppBar":
                lines.append(f"{pad}ttk.Label({parent}, text='{lb}', font=('Helvetica', 16, 'bold')).grid(row={row}, column=0, pady=4, sticky='w')\n")
            elif ct == "BottomNav":
                fname = f"bnav_{row}"
                lines.append(f"{pad}{fname} = ttk.Frame({parent})\n")
                lines.append(f"{pad}{fname}.grid(row=999, column=0, columnspan=2, sticky='ew', pady=8)\n")
                for bi, bc in enumerate(ch):
                    bl = bc.get("label", bc.get("text", f"Nav{bi}"))
                    lines.append(f"{pad}ttk.Button({fname}, text='{bl}', command=lambda: None).pack(side='left', padx=4)\n")
            elif ct == "List":
                items = c.get("items", [lb] if lb else ["Item 1"])
                lname = f"lst_{row}"
                lines.append(f"{pad}{lname} = tk.Listbox({parent}, height={min(len(items) + 2, 10)})\n")
                lines.append(f"{pad}{lname}.grid(row={row}, column=0, sticky='ew', pady=4)\n")
                for it in items:
                    lines.append(f"{pad}{lname}.insert('end', '{it}')\n")
            elif ct == "Grid":
                fname = f"grid_{row}"
                cols = c.get("columns", 3)
                lines.append(f"{pad}{fname} = ttk.Frame({parent})\n")
                lines.append(f"{pad}{fname}.grid(row={row}, column=0, columnspan=2, sticky='ew', pady=4)\n")
                for gi, gc in enumerate(ch):
                    gl = gc.get("label", gc.get("text", f"Cell{gi}"))
                    gr = gi // cols
                    gc_col = gi % cols
                    lines.append(f"{pad}ttk.Label({fname}, text='{gl}', relief='groove', padding=8).grid(row={gr}, column={gc_col}, padx=2, pady=2, sticky='ew')\n")
            elif ct == "Image":
                lines.append(f"{pad}tk.Label({parent}, text='[Image: {lb}]', bg='#ddd', width=30, height=5).grid(row={row}, column=0, pady=4, sticky='w')\n")
            elif ct == "Dialog":
                dname = f"dlg_{row}"
                lines.append(
                    f"{pad}def _open_{dname}():\n"
                    f"{pad}    dlg = tk.Toplevel(self)\n"
                    f"{pad}    dlg.title('{lb}')\n"
                    f"{pad}    dlg.geometry('400x300')\n"
                    f"{pad}    ttk.Label(dlg, text='{lb}').pack(pady=12)\n"
                    f"{pad}    ttk.Button(dlg, text='Close', command=dlg.destroy).pack(pady=8)\n"
                )
                lines.append(f"{pad}ttk.Button({parent}, text='Open {lb}', command=_open_{dname}).grid(row={row}, column=0, pady=4, sticky='w')\n")
            elif ct == "TabBar":
                tabs = c.get("tabs", ch)
                nbname = f"nb_{row}"
                lines.append(f"{pad}{nbname} = ttk.Notebook({parent})\n")
                lines.append(f"{pad}{nbname}.grid(row={row}, column=0, columnspan=2, sticky='nsew', pady=4)\n")
                for ti, t in enumerate(tabs):
                    tn = t.get("label", t.get("name", f"Tab {ti + 1}"))
                    tfname = f"tab_{row}_{ti}"
                    lines.append(f"{pad}{tfname} = ttk.Frame({nbname}, padding=8)\n")
                    lines.append(f"{pad}{nbname}.add({tfname}, text='{tn}')\n")
                    tc = t.get("children", t.get("components", []))
                    if tc:
                        lines.append(self._tkinter_render_components(tc, tfname, indent))
                    else:
                        lines.append(f"{pad}ttk.Label({tfname}, text='{tn} content').pack(anchor='w')\n")
            else:
                lines.append(f"{pad}ttk.Label({parent}, text='{lb}').grid(row={row}, column=0, pady=2, sticky='w')\n")
            row += 1
        return "".join(lines)

    # ------------------------------------------------------------------
    # Qt
    # ------------------------------------------------------------------

    def _generate_qt(self, screens: List[Dict[str, Any]], app_name: str) -> Dict[str, str]:
        if not screens:
            screens = [{"name": "Home", "components": []}]
        return {"main.py": self._qt_main_py(screens, app_name)}

    def _qt_main_py(self, screens: List[Dict[str, Any]], app_name: str) -> str:
        screen_methods: List[str] = []
        for s in screens:
            mname = self._snake(s.get("name", "Home"))
            label = s.get("name", "Home")
            body = self._qt_render_components(s.get("components", []), "layout", 2)
            screen_methods.append(
                f"    def _build_{mname}(self):\n"
                f"        widget = QWidget()\n"
                f"        layout = QVBoxLayout(widget)\n"
                f"        layout.addWidget(QLabel('<h2>{label}</h2>'))\n"
                f"{body}"
                f"        layout.addStretch()\n"
                f"        return widget\n"
            )

        nav_btns: List[str] = []
        for s in screens:
            n = s.get("name", "Home")
            sn = self._snake(n)
            nav_btns.append(
                f"        btn = QPushButton('{n}')\n"
                f"        btn.clicked.connect(lambda checked, s='{sn}': self._show_screen(s))\n"
                f"        nav_layout.addWidget(btn)"
            )

        stack_adds: List[str] = []
        for s in screens:
            sn = self._snake(s.get("name", "Home"))
            stack_adds.append(
                f"        self._screen_map['{sn}'] = self._stack.count()\n"
                f"        self._stack.addWidget(self._build_{sn}())"
            )

        return (
            '"""' + app_name + ' â€” Qt desktop application."""\n\n'
            "import sys\n"
            "from PySide6.QtWidgets import (\n"
            "    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,\n"
            "    QPushButton, QLabel, QLineEdit, QListWidget, QGroupBox,\n"
            "    QGridLayout, QTabWidget, QDialog, QDialogButtonBox,\n"
            "    QStackedWidget, QToolBar, QMenuBar, QStatusBar, QFrame,\n"
            ")\n"
            "from PySide6.QtCore import Qt\n\n\n"
            "class MainWindow(QMainWindow):\n"
            "    def __init__(self):\n"
            "        super().__init__()\n"
            f"        self.setWindowTitle('{app_name}')\n"
            "        self.resize(1000, 700)\n"
            "        self.setMinimumSize(800, 600)\n\n"
            "        self._build_menubar()\n"
            "        self._build_toolbar()\n"
            "        self._build_statusbar()\n\n"
            "        central = QWidget()\n"
            "        main_layout = QVBoxLayout(central)\n\n"
            "        nav = QWidget()\n"
            "        nav_layout = QHBoxLayout(nav)\n"
            "        nav_layout.setContentsMargins(0, 0, 0, 0)\n"
            + "\n".join(nav_btns) + "\n"
            "        nav_layout.addStretch()\n"
            "        main_layout.addWidget(nav)\n\n"
            "        self._stack = QStackedWidget()\n"
            "        self._screen_map = {}\n"
            + "\n".join(stack_adds) + "\n\n"
            "        main_layout.addWidget(self._stack)\n"
            "        self.setCentralWidget(central)\n"
            f"        self._show_screen('{self._snake(screens[0].get('name', 'Home'))}')\n\n"
            "    def _build_menubar(self):\n"
            "        mb = self.menuBar()\n"
            "        file_m = mb.addMenu('&File')\n"
            "        file_m.addAction('New')\n"
            "        file_m.addAction('Open')\n"
            "        file_m.addAction('Save')\n"
            "        file_m.addSeparator()\n"
            "        file_m.addAction('Exit', self.close)\n"
            "        edit_m = mb.addMenu('&Edit')\n"
            "        edit_m.addAction('Undo')\n"
            "        edit_m.addAction('Redo')\n"
            "        edit_m.addSeparator()\n"
            "        edit_m.addAction('Preferences')\n"
            "        help_m = mb.addMenu('&Help')\n"
            f"        help_m.addAction('About {app_name}')\n\n"
            "    def _build_toolbar(self):\n"
            "        tb = QToolBar('Navigation')\n"
            "        tb.setMovable(False)\n"
            "        self.addToolBar(tb)\n\n"
            "    def _build_statusbar(self):\n"
            "        self.statusBar().showMessage('Ready')\n\n"
            "    def _show_screen(self, name):\n"
            "        idx = self._screen_map.get(name, 0)\n"
            "        self._stack.setCurrentIndex(idx)\n"
            "        self.statusBar().showMessage(f'Screen: {name}')\n\n"
            + "\n\n".join(screen_methods) + "\n\n"
            "if __name__ == '__main__':\n"
            "    app = QApplication(sys.argv)\n"
            "    window = MainWindow()\n"
            "    window.show()\n"
            "    sys.exit(app.exec())\n"
        )

    def _qt_render_components(self, components: List[Dict[str, Any]], parent_layout: str, indent: int) -> str:
        lines: List[str] = []
        pad = "    " * indent
        idx = 0
        for c in components:
            ct = c.get("type", "Container")
            lb = c.get("label", c.get("text", ""))
            ch = c.get("children", [])
            if ct == "Button":
                bname = f"btn_{idx}"
                lines.append(f"{pad}{bname} = QPushButton('{lb}')\n")
                lines.append(f"{pad}{bname}.clicked.connect(lambda: None)\n")
                lines.append(f"{pad}{parent_layout}.addWidget({bname})\n")
            elif ct == "Text":
                lines.append(f"{pad}{parent_layout}.addWidget(QLabel('{lb}'))\n")
            elif ct == "Input":
                ename = f"edit_{idx}"
                ph = c.get("placeholder", lb)
                lines.append(f"{pad}{ename} = QLineEdit()\n")
                lines.append(f"{pad}{ename}.setPlaceholderText('{ph}')\n")
                lines.append(f"{pad}{parent_layout}.addWidget({ename})\n")
            elif ct == "Container":
                d = c.get("direction", "column")
                wname = f"cont_{idx}"
                lname = f"cont_l_{idx}"
                layout_cls = "QHBoxLayout" if d == "row" else "QVBoxLayout"
                lines.append(f"{pad}{wname} = QWidget()\n")
                lines.append(f"{pad}{lname} = {layout_cls}({wname})\n")
                lines.append(self._qt_render_components(ch, lname, indent))
                lines.append(f"{pad}{parent_layout}.addWidget({wname})\n")
            elif ct == "Card":
                gname = f"grp_{idx}"
                glname = f"grp_l_{idx}"
                lines.append(f"{pad}{gname} = QGroupBox('{lb}')\n")
                lines.append(f"{pad}{glname} = QVBoxLayout({gname})\n")
                if ch:
                    lines.append(self._qt_render_components(ch, glname, indent))
                else:
                    lines.append(f"{pad}{glname}.addWidget(QLabel('{lb}'))\n")
                lines.append(f"{pad}{parent_layout}.addWidget({gname})\n")
            elif ct == "AppBar":
                lines.append(f"{pad}{parent_layout}.addWidget(QLabel('<h1>{lb}</h1>'))\n")
            elif ct == "BottomNav":
                tbname = f"bnav_{idx}"
                lines.append(f"{pad}{tbname} = QToolBar()\n")
                for bi, bc in enumerate(ch):
                    bl = bc.get("label", bc.get("text", f"Nav{bi}"))
                    lines.append(f"{pad}{tbname}.addAction('{bl}')\n")
                lines.append(f"{pad}{parent_layout}.addWidget({tbname})\n")
            elif ct == "List":
                items = c.get("items", [lb] if lb else ["Item 1"])
                lw = f"list_{idx}"
                lines.append(f"{pad}{lw} = QListWidget()\n")
                for it in items:
                    lines.append(f"{pad}{lw}.addItem('{it}')\n")
                lines.append(f"{pad}{parent_layout}.addWidget({lw})\n")
            elif ct == "Grid":
                cols = c.get("columns", 3)
                gwname = f"gridw_{idx}"
                glname = f"gridl_{idx}"
                lines.append(f"{pad}{gwname} = QWidget()\n")
                lines.append(f"{pad}{glname} = QGridLayout({gwname})\n")
                for gi, gc in enumerate(ch):
                    gl = gc.get("label", gc.get("text", f"Cell{gi}"))
                    gr = gi // cols
                    gc_col = gi % cols
                    lines.append(f"{pad}{glname}.addWidget(QLabel('{gl}'), {gr}, {gc_col})\n")
                lines.append(f"{pad}{parent_layout}.addWidget({gwname})\n")
            elif ct == "Image":
                lines.append(f"{pad}{parent_layout}.addWidget(QLabel('[Image: {lb}]'))\n")
            elif ct == "Dialog":
                dname = f"dlgfn_{idx}"
                lines.append(
                    f"{pad}def {dname}():\n"
                    f"{pad}    dlg = QDialog(self)\n"
                    f"{pad}    dlg.setWindowTitle('{lb}')\n"
                    f"{pad}    dl = QVBoxLayout(dlg)\n"
                    f"{pad}    dl.addWidget(QLabel('{lb}'))\n"
                    f"{pad}    bb = QDialogButtonBox(QDialogButtonBox.Close)\n"
                    f"{pad}    bb.rejected.connect(dlg.reject)\n"
                    f"{pad}    dl.addWidget(bb)\n"
                    f"{pad}    dlg.exec()\n"
                )
                lines.append(f"{pad}btn_d_{idx} = QPushButton('Open {lb}')\n")
                lines.append(f"{pad}btn_d_{idx}.clicked.connect({dname})\n")
                lines.append(f"{pad}{parent_layout}.addWidget(btn_d_{idx})\n")
            elif ct == "TabBar":
                tabs = c.get("tabs", ch)
                twname = f"tabs_{idx}"
                lines.append(f"{pad}{twname} = QTabWidget()\n")
                for ti, t in enumerate(tabs):
                    tn = t.get("label", t.get("name", f"Tab {ti + 1}"))
                    tpname = f"tab_{idx}_{ti}"
                    tlname = f"tabl_{idx}_{ti}"
                    lines.append(f"{pad}{tpname} = QWidget()\n")
                    lines.append(f"{pad}{tlname} = QVBoxLayout({tpname})\n")
                    tc = t.get("children", t.get("components", []))
                    if tc:
                        lines.append(self._qt_render_components(tc, tlname, indent))
                    else:
                        lines.append(f"{pad}{tlname}.addWidget(QLabel('{tn} content'))\n")
                    lines.append(f"{pad}{twname}.addTab({tpname}, '{tn}')\n")
                lines.append(f"{pad}{parent_layout}.addWidget({twname})\n")
            else:
                lines.append(f"{pad}{parent_layout}.addWidget(QLabel('{lb}'))\n")
            idx += 1
        return "".join(lines)

    # ------------------------------------------------------------------
    # Compose Desktop
    # ------------------------------------------------------------------

    def _generate_compose_desktop(self, screens: List[Dict[str, Any]], app_name: str) -> Dict[str, str]:
        if not screens:
            screens = [{"name": "Home", "components": []}]
        return {
            "src/main/kotlin/Main.kt": self._compose_main_kt(screens, app_name),
            "build.gradle.kts": self._compose_build_gradle(app_name),
        }

    def _compose_main_kt(self, screens: List[Dict[str, Any]], app_name: str) -> str:
        screen_fns: List[str] = []
        for s in screens:
            fname = self._pascal(s.get("name", "Home"))
            body = self._compose_render_components(s.get("components", []), 3)
            screen_fns.append(
                f"@Composable\nfun {fname}Screen() {{\n"
                f"    Column(\n"
                f"        modifier = Modifier.fillMaxSize().padding(16.dp).verticalScroll(rememberScrollState()),\n"
                f"        verticalArrangement = Arrangement.spacedBy(12.dp)\n"
                f"    ) {{\n"
                f"        Text(\"{fname}\", style = MaterialTheme.typography.headlineMedium)\n"
                f"{body}"
                "    }\n}\n"
            )

        nav_items: List[str] = []
        for i, s in enumerate(screens):
            n = s.get("name", "Home")
            idx = str(i)
            nav_items.append(
                f"                NavigationBarItem(\n"
                f"                    selected = currentScreen == {idx},\n"
                f"                    onClick = {{ currentScreen = {idx} }},\n"
                f"                    icon = {{ Icon(Icons.Default.Home, contentDescription = \"{n}\") }},\n"
                f"                    label = {{ Text(\"{n}\") }}\n"
                "                )"
            )

        when_branches: List[str] = []
        for i, s in enumerate(screens):
            fname = self._pascal(s.get("name", "Home"))
            when_branches.append(f"                    {i} -> {fname}Screen()")

        return (
            "import androidx.compose.desktop.ui.tooling.preview.Preview\n"
            "import androidx.compose.foundation.*\n"
            "import androidx.compose.foundation.layout.*\n"
            "import androidx.compose.material.icons.Icons\n"
            "import androidx.compose.material.icons.filled.*\n"
            "import androidx.compose.material3.*\n"
            "import androidx.compose.runtime.*\n"
            "import androidx.compose.ui.Alignment\n"
            "import androidx.compose.ui.Modifier\n"
            "import androidx.compose.ui.unit.dp\n"
            "import androidx.compose.ui.window.Window\n"
            "import androidx.compose.ui.window.application\n\n"
            "fun main() = application {\n"
            f"    Window(onCloseRequest = ::exitApplication, title = \"{app_name}\") {{\n"
            "        MaterialTheme {\n"
            "            App()\n"
            "        }\n"
            "    }\n}\n\n"
            "@OptIn(ExperimentalMaterial3Api::class)\n"
            "@Preview\n@Composable\nfun App() {\n"
            "    var currentScreen by remember { mutableStateOf(0) }\n\n"
            "    Scaffold(\n"
            "        topBar = {\n"
            f"            TopAppBar(title = {{ Text(\"{app_name}\") }})\n"
            "        },\n"
            "        bottomBar = {\n"
            "            NavigationBar {\n"
            + "\n".join(nav_items) + "\n"
            "            }\n"
            "        }\n"
            "    ) { padding ->\n"
            "        Box(modifier = Modifier.padding(padding)) {\n"
            "            when (currentScreen) {\n"
            + "\n".join(when_branches) + "\n"
            "            }\n"
            "        }\n"
            "    }\n}\n\n"
            + "\n\n".join(screen_fns)
        )

    def _compose_render_components(self, components: List[Dict[str, Any]], indent: int) -> str:
        lines: List[str] = []
        pad = "    " * indent
        for c in components:
            ct = c.get("type", "Container")
            lb = c.get("label", c.get("text", ""))
            ch = c.get("children", [])
            if ct == "Button":
                lines.append(f"{pad}Button(onClick = {{ }}) {{ Text(\"{lb}\") }}\n")
            elif ct == "Text":
                lines.append(f"{pad}Text(\"{lb}\")\n")
            elif ct == "Input":
                var = self._camel(lb or "field")
                lines.append(f"{pad}var {var} by remember {{ mutableStateOf(\"\") }}\n")
                lines.append(
                    f"{pad}OutlinedTextField(value = {var}, onValueChange = {{ {var} = it }},\n"
                    f"{pad}    label = {{ Text(\"{lb}\") }}, modifier = Modifier.fillMaxWidth())\n"
                )
            elif ct == "Container":
                d = c.get("direction", "column")
                wrapper = "Row" if d == "row" else "Column"
                arr = "horizontalArrangement" if d == "row" else "verticalArrangement"
                inner = self._compose_render_components(ch, indent + 1)
                lines.append(
                    f"{pad}{wrapper}({arr} = Arrangement.spacedBy(8.dp)) {{\n"
                    f"{inner}{pad}}}\n"
                )
            elif ct == "Card":
                inner = self._compose_render_components(ch, indent + 2) if ch else f"{pad}        Text(\"{lb}\")\n"
                lines.append(
                    f"{pad}Card(modifier = Modifier.fillMaxWidth()) {{\n"
                    f"{pad}    Column(modifier = Modifier.padding(16.dp)) {{\n"
                    f"{inner}"
                    f"{pad}    }}\n{pad}}}\n"
                )
            elif ct == "AppBar":
                lines.append(f"{pad}Text(\"{lb}\", style = MaterialTheme.typography.headlineMedium)\n")
            elif ct == "BottomNav":
                lines.append(f"{pad}NavigationBar {{\n")
                for bi, bc in enumerate(ch):
                    bl = bc.get("label", bc.get("text", f"Nav{bi}"))
                    lines.append(
                        f"{pad}    NavigationBarItem(selected = false, onClick = {{ }},\n"
                        f"{pad}        icon = {{ Icon(Icons.Default.Home, \"{bl}\") }},\n"
                        f"{pad}        label = {{ Text(\"{bl}\") }})\n"
                    )
                lines.append(f"{pad}}}\n")
            elif ct == "List":
                items = c.get("items", [lb] if lb else ["Item 1"])
                lines.append(f"{pad}Column {{\n")
                for it in items:
                    lines.append(
                        f"{pad}    Text(\"{it}\", modifier = Modifier.fillMaxWidth()\n"
                        f"{pad}        .padding(vertical = 8.dp))\n"
                        f"{pad}    Divider()\n"
                    )
                lines.append(f"{pad}}}\n")
            elif ct == "Grid":
                cols = c.get("columns", 3)
                lines.append(f"{pad}// Grid with {cols} columns\n")
                lines.append(f"{pad}Column {{\n")
                for gi in range(0, len(ch), cols):
                    lines.append(f"{pad}    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {{\n")
                    for gc in ch[gi:gi + cols]:
                        gl = gc.get("label", gc.get("text", "Cell"))
                        lines.append(
                            f"{pad}        Card(modifier = Modifier.weight(1f)) {{\n"
                            f"{pad}            Text(\"{gl}\", modifier = Modifier.padding(8.dp))\n"
                            f"{pad}        }}\n"
                        )
                    lines.append(f"{pad}    }}\n")
                lines.append(f"{pad}}}\n")
            elif ct == "Image":
                lines.append(
                    f"{pad}Box(modifier = Modifier.fillMaxWidth().height(200.dp)\n"
                    f"{pad}    .background(MaterialTheme.colorScheme.surfaceVariant),\n"
                    f"{pad}    contentAlignment = Alignment.Center) {{\n"
                    f"{pad}    Text(\"[Image: {lb}]\")\n{pad}}}\n"
                )
            elif ct == "Dialog":
                var = f"show{self._pascal(lb or 'Dialog')}"
                lines.append(
                    f"{pad}var {var} by remember {{ mutableStateOf(false) }}\n"
                    f"{pad}Button(onClick = {{ {var} = true }}) {{ Text(\"Open {lb}\") }}\n"
                    f"{pad}if ({var}) {{\n"
                    f"{pad}    AlertDialog(\n"
                    f"{pad}        onDismissRequest = {{ {var} = false }},\n"
                    f"{pad}        title = {{ Text(\"{lb}\") }},\n"
                    f"{pad}        text = {{ Text(\"{lb} content\") }},\n"
                    f"{pad}        confirmButton = {{ TextButton(onClick = {{ {var} = false }}) {{ Text(\"OK\") }} }},\n"
                    f"{pad}        dismissButton = {{ TextButton(onClick = {{ {var} = false }}) {{ Text(\"Cancel\") }} }}\n"
                    f"{pad}    )\n{pad}}}\n"
                )
            elif ct == "TabBar":
                tabs = c.get("tabs", ch)
                lines.append(f"{pad}var selectedTab by remember {{ mutableStateOf(0) }}\n")
                lines.append(f"{pad}TabRow(selectedTabIndex = selectedTab) {{\n")
                for ti, t in enumerate(tabs):
                    tn = t.get("label", t.get("name", f"Tab {ti + 1}"))
                    lines.append(
                        f"{pad}    Tab(selected = selectedTab == {ti},\n"
                        f"{pad}        onClick = {{ selectedTab = {ti} }},\n"
                        f"{pad}        text = {{ Text(\"{tn}\") }})\n"
                    )
                lines.append(f"{pad}}}\n")
                for ti, t in enumerate(tabs):
                    tn = t.get("label", t.get("name", f"Tab {ti + 1}"))
                    tc = t.get("children", t.get("components", []))
                    inner = self._compose_render_components(tc, indent + 1) if tc else f"{pad}    Text(\"{tn} content\")\n"
                    lines.append(
                        f"{pad}if (selectedTab == {ti}) {{\n"
                        f"{inner}{pad}}}\n"
                    )
            else:
                lines.append(f"{pad}Text(\"{lb}\")\n")
        return "".join(lines)

    def _compose_build_gradle(self, app_name: str) -> str:
        pkg_name = self._snake(app_name).replace("_", ".")
        return (
            "import org.jetbrains.compose.desktop.application.dsl.TargetFormat\n\n"
            "plugins {\n"
            "    kotlin(\"jvm\")\n"
            "    id(\"org.jetbrains.compose\")\n"
            "    id(\"org.jetbrains.kotlin.plugin.compose\")\n"
            "}\n\n"
            "group = \"com.EoStudio\"\nversion = \"1.0.0\"\n\n"
            "repositories {\n    mavenCentral()\n"
            "    maven(\"https://maven.pkg.jetbrains.space/public/p/compose/dev\")\n"
            "    google()\n}\n\n"
            "dependencies {\n"
            "    implementation(compose.desktop.currentOs)\n"
            "    implementation(compose.material3)\n"
            "    implementation(compose.materialIconsExtended)\n"
            "}\n\n"
            "compose.desktop {\n"
            "    application {\n"
            f"        mainClass = \"MainKt\"\n"
            "        nativeDistributions {\n"
            "            targetFormats(TargetFormat.Dmg, TargetFormat.Msi, TargetFormat.Deb)\n"
            f"            packageName = \"{self._kebab(app_name)}\"\n"
            "            packageVersion = \"1.0.0\"\n"
            "        }\n    }\n}\n"
        )

    # ------------------------------------------------------------------
    # Naming helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _pascal(name: str) -> str:
        """Convert *name* to PascalCase."""
        return "".join(w.capitalize() for w in re.split(r"[\s_\-]+", name) if w)

    @staticmethod
    def _snake(name: str) -> str:
        """Convert *name* to snake_case."""
        return re.sub(r"[\s\-]+", "_", name).lower()

    @staticmethod
    def _kebab(name: str) -> str:
        """Convert *name* to kebab-case."""
        return re.sub(r"[\s_]+", "-", name).lower()

    @staticmethod
    def _camel(name: str) -> str:
        """Convert *name* to camelCase."""
        parts = re.split(r"[\s_\-]+", name)
        if not parts:
            return "field"
        return parts[0].lower() + "".join(w.capitalize() for w in parts[1:])
