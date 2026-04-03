"""React (JSX) code generator for EoStudio UI components."""

from __future__ import annotations

from typing import Any, Dict, List


class ReactGenerator:
    """Generates React JSX + CSS source files from eostudio component trees.

    Component type mapping:
    - ``Button``    -> ``<button>``
    - ``Text``      -> ``<p>`` / ``<h1>``
    - ``Input``     -> ``<input>``
    - ``TextArea``  -> ``<textarea>``
    - ``Image``     -> ``<img>``
    - ``Container`` -> ``<div className="container">``
    - ``Card``      -> ``<div className="card">``
    - ``Link``      -> ``<Link>`` (React Router)
    """

    def generate(
        self,
        components: List[Dict[str, Any]],
        screens: List[Dict[str, Any]],
    ) -> Dict[str, str]:
        """Generate React source files.

        Args:
            components: Flat list of component dicts.
            screens: List of screen dicts with ``name`` and ``components``.

        Returns:
            Mapping of filename -> JSX/CSS source content.
        """
        files: Dict[str, str] = {}

        if not screens:
            screens = [{"name": "Home", "components": components}]

        files["src/App.jsx"] = self._generate_app(screens)
        files["src/index.jsx"] = self._generate_index()
        files["src/index.css"] = self._generate_css()

        for screen in screens:
            cname = self._component_name(screen.get("name", "Home"))
            fname = self._kebab(screen.get("name", "home"))
            screen_comps = screen.get("components", components)
            files[f"src/screens/{cname}.jsx"] = self._generate_screen(cname, screen_comps)
            files[f"src/screens/{cname}.module.css"] = self._generate_screen_css(cname)

        return files

    def _generate_index(self) -> str:
        return (
            "import React from 'react';\n"
            "import ReactDOM from 'react-dom/client';\n"
            "import { BrowserRouter } from 'react-router-dom';\n"
            "import App from './App';\n"
            "import './index.css';\n\n"
            "const root = ReactDOM.createRoot(document.getElementById('root'));\n"
            "root.render(\n"
            "  <React.StrictMode>\n"
            "    <BrowserRouter>\n"
            "      <App />\n"
            "    </BrowserRouter>\n"
            "  </React.StrictMode>\n"
            ");\n"
        )

    def _generate_app(self, screens: List[Dict[str, Any]]) -> str:
        imports: List[str] = []
        routes: List[str] = []

        for i, screen in enumerate(screens):
            cname = self._component_name(screen.get("name", "Home"))
            path = "/" if i == 0 else f"/{self._kebab(screen.get('name', 'home'))}"
            imports.append(f"import {cname} from './screens/{cname}';")
            routes.append(f'        <Route path="{path}" element={{<{cname} />}} />')

        imports_str = "\n".join(imports)
        routes_str = "\n".join(routes)

        nav_links: List[str] = []
        for i, screen in enumerate(screens):
            path = "/" if i == 0 else f"/{self._kebab(screen.get('name', 'home'))}"
            label = screen.get("name", "Home")
            nav_links.append(f'        <Link to="{path}">{label}</Link>')
        nav_str = "\n".join(nav_links)

        return (
            "import React from 'react';\n"
            "import { Routes, Route, Link } from 'react-router-dom';\n"
            f"{imports_str}\n\n"
            "function App() {\n"
            "  return (\n"
            "    <div className=\"app\">\n"
            "      <nav className=\"app-nav\">\n"
            f"{nav_str}\n"
            "      </nav>\n"
            "      <main className=\"app-main\">\n"
            "        <Routes>\n"
            f"{routes_str}\n"
            "        </Routes>\n"
            "      </main>\n"
            "    </div>\n"
            "  );\n"
            "}\n\n"
            "export default App;\n"
        )

    def _generate_screen(self, class_name: str, components: List[Dict[str, Any]]) -> str:
        body = self._render_jsx(components, indent=3)
        state_hooks = self._collect_state_hooks(components)

        return (
            "import React, { useState } from 'react';\n"
            f"import styles from './{class_name}.module.css';\n\n"
            f"function {class_name}() {{\n"
            f"{state_hooks}"
            "  return (\n"
            f"    <div className={{styles.screen}}>\n"
            f"      <h1>{class_name}</h1>\n"
            f"{body}"
            "    </div>\n"
            "  );\n"
            "}\n\n"
            f"export default {class_name};\n"
        )

    def _render_jsx(self, components: List[Dict[str, Any]], indent: int) -> str:
        lines: List[str] = []
        pad = "  " * indent

        for comp in components:
            ctype = comp.get("type", "Container")
            label = comp.get("label", comp.get("text", ""))
            children = comp.get("children", [])

            if ctype == "Button":
                lines.append(f"{pad}<button className={{styles.button}}>{label}</button>\n")
            elif ctype == "Heading":
                level = comp.get("level", 2)
                lines.append(f"{pad}<h{level}>{label}</h{level}>\n")
            elif ctype == "Text":
                lines.append(f"{pad}<p>{label}</p>\n")
            elif ctype == "Input":
                var_name = self._var_name(label)
                placeholder = comp.get("placeholder", label)
                lines.append(
                    f"{pad}<input\n"
                    f"{pad}  className={{styles.input}}\n"
                    f'{pad}  placeholder="{placeholder}"\n'
                    f"{pad}  value={{{var_name}}}\n"
                    f"{pad}  onChange={{(e) => set{var_name[0].upper()}{var_name[1:]}(e.target.value)}}\n"
                    f"{pad}/>\n"
                )
            elif ctype == "TextArea":
                var_name = self._var_name(label)
                lines.append(
                    f"{pad}<textarea\n"
                    f"{pad}  className={{styles.textarea}}\n"
                    f'{pad}  placeholder="{label}"\n'
                    f"{pad}  value={{{var_name}}}\n"
                    f"{pad}  onChange={{(e) => set{var_name[0].upper()}{var_name[1:]}(e.target.value)}}\n"
                    f"{pad}/>\n"
                )
            elif ctype == "Image":
                src = comp.get("src", "")
                lines.append(f'{pad}<img src="{src}" alt="{label}" className={{styles.image}} />\n')
            elif ctype == "Card":
                child_body = self._render_jsx(children, indent + 1) if children else f"{pad}  <p>{label}</p>\n"
                lines.append(
                    f"{pad}<div className={{styles.card}}>\n"
                    f"{child_body}"
                    f"{pad}</div>\n"
                )
            elif ctype == "Container" and children:
                direction = comp.get("direction", "column")
                cls = "containerRow" if direction == "row" else "container"
                child_body = self._render_jsx(children, indent + 1)
                lines.append(
                    f"{pad}<div className={{styles.{cls}}}>\n"
                    f"{child_body}"
                    f"{pad}</div>\n"
                )
            else:
                lines.append(f"{pad}<p>{label}</p>\n")

        return "".join(lines)

    def _collect_state_hooks(self, components: List[Dict[str, Any]]) -> str:
        hooks: List[str] = []
        for comp in components:
            ctype = comp.get("type", "")
            if ctype in ("Input", "TextArea"):
                label = comp.get("label", comp.get("text", ""))
                var_name = self._var_name(label)
                setter = f"set{var_name[0].upper()}{var_name[1:]}"
                hooks.append(f"  const [{var_name}, {setter}] = useState('');\n")
            for child in comp.get("children", []):
                hooks.append(self._collect_state_hooks([child]))
        return "".join(hooks)

    def _generate_css(self) -> str:
        return (
            "/* EoStudio React App - Global Styles */\n"
            "*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }\n\n"
            "body {\n"
            "  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;\n"
            "  line-height: 1.6;\n"
            "  color: #333;\n"
            "  background: #f5f5f5;\n"
            "}\n\n"
            ".app { display: flex; flex-direction: column; min-height: 100vh; }\n"
            ".app-nav {\n"
            "  display: flex; gap: 16px; padding: 12px 24px;\n"
            "  background: #fff; border-bottom: 1px solid #e5e7eb;\n"
            "}\n"
            ".app-nav a { text-decoration: none; color: #2563eb; font-weight: 500; }\n"
            ".app-nav a:hover { text-decoration: underline; }\n"
            ".app-main { flex: 1; padding: 24px; max-width: 1200px; margin: 0 auto; width: 100%; }\n"
        )

    def _generate_screen_css(self, class_name: str) -> str:
        return (
            f"/* {class_name} screen styles */\n"
            ".screen { display: flex; flex-direction: column; gap: 16px; }\n"
            ".container { display: flex; flex-direction: column; gap: 12px; }\n"
            ".containerRow { display: flex; flex-direction: row; gap: 12px; flex-wrap: wrap; }\n"
            ".card {\n"
            "  background: #fff; border-radius: 8px; padding: 16px;\n"
            "  box-shadow: 0 2px 8px rgba(0,0,0,0.1);\n"
            "}\n"
            ".button {\n"
            "  padding: 10px 20px; border: none; border-radius: 6px;\n"
            "  background: #2563eb; color: #fff; font-size: 14px; cursor: pointer;\n"
            "}\n"
            ".button:hover { background: #1d4ed8; }\n"
            ".input, .textarea {\n"
            "  width: 100%; padding: 10px 12px;\n"
            "  border: 1px solid #d1d5db; border-radius: 6px; font-size: 14px;\n"
            "}\n"
            ".input:focus, .textarea:focus {\n"
            "  outline: none; border-color: #2563eb;\n"
            "  box-shadow: 0 0 0 3px rgba(37,99,235,0.1);\n"
            "}\n"
            ".image { max-width: 100%; border-radius: 8px; }\n"
        )

    @staticmethod
    def _component_name(name: str) -> str:
        return "".join(w.capitalize() for w in name.replace("-", " ").replace("_", " ").split())

    @staticmethod
    def _kebab(name: str) -> str:
        return name.lower().replace(" ", "-").replace("_", "-")

    @staticmethod
    def _var_name(label: str) -> str:
        clean = "".join(c if c.isalnum() else "_" for c in label)
        parts = clean.split("_")
        if not parts or not parts[0]:
            return "field"
        return parts[0].lower() + "".join(w.capitalize() for w in parts[1:] if w)
