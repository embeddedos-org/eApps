"""Full-stack web application code generator for EoStudio UI components."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional


class WebAppGenerator:
    """Generates full-stack web application source files from eostudio screens.

    Supported frontend frameworks:
    - ``react``  — React 18 + TypeScript + React Router
    - ``vue``    — Vue 3 + TypeScript + Vue Router
    - ``angular``— Angular standalone components
    - ``svelte`` — SvelteKit
    - ``nextjs`` — Next.js App Router

    Supported backend frameworks:
    - ``fastapi``— FastAPI + SQLAlchemy + Pydantic
    - ``flask``  — Flask + SQLAlchemy + Flask-CORS
    - ``express``— Express.js + TypeScript
    - ``django`` — Django REST Framework

    Component type mapping (frontend renderers):
    - ``Button``    → ``<button>``
    - ``Text``      → ``<p>``
    - ``Input``     → ``<input>``
    - ``Container`` → ``<div>``
    - ``Card``      → ``<div class="card">``
    - ``AppBar``    → ``<header>``
    - ``BottomNav`` → ``<nav>``
    - ``List``      → ``<ul>``
    - ``Grid``      → ``<div class="grid">``
    - ``Image``     → ``<img>``
    - ``Dialog``    → ``<dialog>``
    - ``TabBar``    → ``<div class="tabs">``
    """

    SUPPORTED_FRONTENDS = {"react", "vue", "angular", "svelte", "nextjs"}
    SUPPORTED_BACKENDS = {"fastapi", "flask", "express", "django"}

    def __init__(self, frontend: str = "react", backend: str = "fastapi") -> None:
        """Initialise the web-app generator.

        Args:
            frontend: Target frontend framework.
            backend: Target backend framework.

        Raises:
            ValueError: If *frontend* or *backend* is not supported.
        """
        if frontend not in self.SUPPORTED_FRONTENDS:
            raise ValueError(
                f"Unsupported frontend {frontend!r}. "
                f"Choose from: {', '.join(sorted(self.SUPPORTED_FRONTENDS))}"
            )
        if backend not in self.SUPPORTED_BACKENDS:
            raise ValueError(
                f"Unsupported backend {backend!r}. "
                f"Choose from: {', '.join(sorted(self.SUPPORTED_BACKENDS))}"
            )
        self.frontend = frontend
        self.backend = backend

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate(
        self,
        screens: List[Dict[str, Any]],
        app_name: str,
        models: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, str]:
        """Generate full-stack source files for a web application.

        Args:
            screens: List of screen dicts, each with ``name`` and
                ``components`` keys.
            app_name: Human-readable application name.
            models: Optional list of data-model dicts with ``name`` and
                ``fields`` keys used by backend generators.

        Returns:
            Mapping of relative filepath → generated source content.
        """
        if models is None:
            models = []

        frontend_dispatch = {
            "react": self._generate_react_frontend,
            "vue": self._generate_vue_frontend,
            "angular": self._generate_angular_frontend,
            "svelte": self._generate_svelte_frontend,
            "nextjs": self._generate_nextjs_frontend,
        }

        backend_dispatch = {
            "fastapi": self._generate_fastapi_backend,
            "flask": self._generate_flask_backend,
            "express": self._generate_express_backend,
            "django": self._generate_django_backend,
        }

        files: Dict[str, str] = {}
        files.update(frontend_dispatch[self.frontend](screens, app_name))
        files.update(backend_dispatch[self.backend](models, app_name))
        files["docker-compose.yml"] = self._generate_docker_compose(app_name)
        files[".env.example"] = self._generate_env_example(app_name)
        return files

    # ==================================================================
    # Frontend generators
    # ==================================================================

    def _generate_react_frontend(
        self,
        screens: List[Dict[str, Any]],
        app_name: str,
    ) -> Dict[str, str]:
        """Generate React 18 + TypeScript frontend files.

        Returns:
            Mapping of ``frontend/`` prefixed paths to source content.
        """
        files: Dict[str, str] = {}

        if not screens:
            screens = [{"name": "Home", "components": []}]

        # -- src/main.tsx ------------------------------------------------
        files["frontend/src/main.tsx"] = (
            "import React from 'react';\n"
            "import ReactDOM from 'react-dom/client';\n"
            "import { BrowserRouter } from 'react-router-dom';\n"
            "import App from './App';\n"
            "import './styles/globals.css';\n\n"
            "const root = ReactDOM.createRoot(\n"
            "  document.getElementById('root') as HTMLElement\n"
            ");\n\n"
            "root.render(\n"
            "  <React.StrictMode>\n"
            "    <BrowserRouter>\n"
            "      <App />\n"
            "    </BrowserRouter>\n"
            "  </React.StrictMode>\n"
            ");\n"
        )

        # -- src/App.tsx -------------------------------------------------
        imports: List[str] = []
        routes: List[str] = []
        nav_links: List[str] = []

        for i, screen in enumerate(screens):
            cname = self._pascal(screen.get("name", "Home"))
            screen_name = cname + "Screen"
            path = "/" if i == 0 else f"/{self._kebab(screen.get('name', 'home'))}"
            imports.append(
                f"import {screen_name} from './screens/{screen_name}';"
            )
            routes.append(
                f'          <Route path="{path}" element={{<{screen_name} />}} />'
            )
            nav_links.append(
                f'          <Link to="{path}">{screen.get("name", "Home")}</Link>'
            )

        files["frontend/src/App.tsx"] = (
            "import React from 'react';\n"
            "import { Routes, Route, Link } from 'react-router-dom';\n"
            + "\n".join(imports) + "\n\n"
            "const App: React.FC = () => {\n"
            "  return (\n"
            "    <div className=\"app\">\n"
            "      <nav className=\"app-nav\">\n"
            "        <span className=\"app-title\">" + app_name + "</span>\n"
            "        <div className=\"nav-links\">\n"
            + "\n".join(nav_links) + "\n"
            "        </div>\n"
            "      </nav>\n"
            "      <main className=\"app-main\">\n"
            "        <Routes>\n"
            + "\n".join(routes) + "\n"
            "        </Routes>\n"
            "      </main>\n"
            "    </div>\n"
            "  );\n"
            "};\n\n"
            "export default App;\n"
        )

        # -- src/api/client.ts -------------------------------------------
        files["frontend/src/api/client.ts"] = (
            "const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';\n\n"
            "interface RequestOptions {\n"
            "  method?: string;\n"
            "  body?: unknown;\n"
            "  headers?: Record<string, string>;\n"
            "}\n\n"
            "export async function apiClient<T>(\n"
            "  endpoint: string,\n"
            "  options: RequestOptions = {},\n"
            "): Promise<T> {\n"
            "  const { method = 'GET', body, headers = {} } = options;\n"
            "  const config: RequestInit = {\n"
            "    method,\n"
            "    headers: {\n"
            "      'Content-Type': 'application/json',\n"
            "      ...headers,\n"
            "    },\n"
            "  };\n"
            "  if (body) {\n"
            "    config.body = JSON.stringify(body);\n"
            "  }\n"
            "  const response = await fetch(`${API_BASE}${endpoint}`, config);\n"
            "  if (!response.ok) {\n"
            "    throw new Error(`API error: ${response.status} ${response.statusText}`);\n"
            "  }\n"
            "  return response.json();\n"
            "}\n\n"
            "export const api = {\n"
            "  get: <T>(url: string) => apiClient<T>(url),\n"
            "  post: <T>(url: string, body: unknown) =>\n"
            "    apiClient<T>(url, { method: 'POST', body }),\n"
            "  put: <T>(url: string, body: unknown) =>\n"
            "    apiClient<T>(url, { method: 'PUT', body }),\n"
            "  delete: <T>(url: string) =>\n"
            "    apiClient<T>(url, { method: 'DELETE' }),\n"
            "};\n"
        )

        # -- screen component files --------------------------------------
        for screen in screens:
            cname = self._pascal(screen.get("name", "Home"))
            screen_name = cname + "Screen"
            comps = screen.get("components", [])
            body = self._render_react_jsx(comps, indent=3)
            files[f"frontend/src/screens/{screen_name}.tsx"] = (
                "import React, { useState } from 'react';\n\n"
                f"const {screen_name}: React.FC = () => {{\n"
                + self._collect_react_hooks(comps)
                + "  return (\n"
                f"    <div className=\"screen\">\n"
                f"      <h1>{screen.get('name', 'Home')}</h1>\n"
                + body
                + "    </div>\n"
                "  );\n"
                "};\n\n"
                f"export default {screen_name};\n"
            )

        # -- src/styles/globals.css --------------------------------------
        files["frontend/src/styles/globals.css"] = (
            "/* EoStudio Generated Styles */\n"
            "*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }\n\n"
            "body {\n"
            "  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto,\n"
            "    'Helvetica Neue', Arial, sans-serif;\n"
            "  line-height: 1.6;\n"
            "  color: #1a1a2e;\n"
            "  background: #f0f2f5;\n"
            "}\n\n"
            ".app { display: flex; flex-direction: column; min-height: 100vh; }\n\n"
            ".app-nav {\n"
            "  display: flex; align-items: center; gap: 16px;\n"
            "  padding: 12px 24px; background: #fff;\n"
            "  border-bottom: 1px solid #e5e7eb; box-shadow: 0 1px 3px rgba(0,0,0,0.05);\n"
            "}\n"
            ".app-title { font-weight: 700; font-size: 18px; margin-right: auto; }\n"
            ".nav-links { display: flex; gap: 16px; }\n"
            ".nav-links a { text-decoration: none; color: #2563eb; font-weight: 500; }\n"
            ".nav-links a:hover { text-decoration: underline; }\n\n"
            ".app-main { flex: 1; padding: 24px; max-width: 1200px; margin: 0 auto; width: 100%; }\n\n"
            ".screen { display: flex; flex-direction: column; gap: 16px; }\n\n"
            "/* Component utilities */\n"
            "button {\n"
            "  padding: 10px 20px; border: none; border-radius: 6px;\n"
            "  background: #2563eb; color: #fff; font-size: 14px;\n"
            "  cursor: pointer; transition: background 0.2s;\n"
            "}\n"
            "button:hover { background: #1d4ed8; }\n\n"
            "input {\n"
            "  width: 100%; padding: 10px 12px;\n"
            "  border: 1px solid #d1d5db; border-radius: 6px; font-size: 14px;\n"
            "}\n"
            "input:focus {\n"
            "  outline: none; border-color: #2563eb;\n"
            "  box-shadow: 0 0 0 3px rgba(37,99,235,0.1);\n"
            "}\n\n"
            ".card {\n"
            "  background: #fff; border-radius: 8px; padding: 16px;\n"
            "  box-shadow: 0 2px 8px rgba(0,0,0,0.08);\n"
            "}\n\n"
            ".grid {\n"
            "  display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));\n"
            "  gap: 16px;\n"
            "}\n\n"
            ".tabs {\n"
            "  display: flex; border-bottom: 2px solid #e5e7eb;\n"
            "}\n"
            ".tabs > * {\n"
            "  padding: 8px 16px; cursor: pointer; border-bottom: 2px solid transparent;\n"
            "  margin-bottom: -2px; font-weight: 500;\n"
            "}\n"
            ".tabs > .active { border-bottom-color: #2563eb; color: #2563eb; }\n\n"
            "header.app-bar {\n"
            "  display: flex; align-items: center; padding: 12px 24px;\n"
            "  background: #2563eb; color: #fff;\n"
            "}\n\n"
            "nav.bottom-nav {\n"
            "  display: flex; justify-content: space-around; padding: 8px 0;\n"
            "  background: #fff; border-top: 1px solid #e5e7eb;\n"
            "  position: sticky; bottom: 0;\n"
            "}\n\n"
            "dialog {\n"
            "  border: none; border-radius: 12px; padding: 24px;\n"
            "  box-shadow: 0 8px 30px rgba(0,0,0,0.12);\n"
            "}\n"
            "dialog::backdrop { background: rgba(0,0,0,0.4); }\n\n"
            "img { max-width: 100%; height: auto; border-radius: 8px; }\n"
        )

        # -- package.json ------------------------------------------------
        pkg = {
            "name": self._kebab(app_name),
            "version": "0.1.0",
            "private": True,
            "type": "module",
            "scripts": {
                "dev": "vite",
                "build": "tsc && vite build",
                "preview": "vite preview",
            },
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "react-router-dom": "^6.20.0",
            },
            "devDependencies": {
                "@types/react": "^18.2.0",
                "@types/react-dom": "^18.2.0",
                "@vitejs/plugin-react": "^4.2.0",
                "typescript": "^5.3.0",
                "vite": "^5.0.0",
            },
        }
        files["frontend/package.json"] = json.dumps(pkg, indent=2) + "\n"

        return files

    def _render_react_jsx(
        self, components: List[Dict[str, Any]], indent: int
    ) -> str:
        """Render a list of EoStudio components as React JSX."""
        lines: List[str] = []
        pad = "  " * indent

        for comp in components:
            ctype = comp.get("type", "Container")
            label = comp.get("label", comp.get("text", ""))
            children = comp.get("children", [])

            if ctype == "Button":
                lines.append(f"{pad}<button>{label}</button>\n")
            elif ctype == "Text":
                lines.append(f"{pad}<p>{label}</p>\n")
            elif ctype == "Input":
                var = self._camel(label or "field")
                setter = "set" + var[0].upper() + var[1:]
                placeholder = comp.get("placeholder", label)
                lines.append(
                    f"{pad}<input\n"
                    f'{pad}  placeholder="{placeholder}"\n'
                    f"{pad}  value={{{var}}}\n"
                    f"{pad}  onChange={{(e) => {setter}(e.target.value)}}\n"
                    f"{pad}/>\n"
                )
            elif ctype == "Card":
                child_body = (
                    self._render_react_jsx(children, indent + 1)
                    if children
                    else f"{pad}  <p>{label}</p>\n"
                )
                lines.append(
                    f'{pad}<div className="card">\n'
                    f"{child_body}"
                    f"{pad}</div>\n"
                )
            elif ctype == "List":
                items = comp.get("items", [])
                li_lines = "".join(
                    f"{pad}    <li>{item}</li>\n" for item in items
                )
                if not li_lines:
                    li_lines = f"{pad}    <li>{label}</li>\n"
                lines.append(
                    f"{pad}<ul>\n"
                    f"{li_lines}"
                    f"{pad}</ul>\n"
                )
            elif ctype == "Grid":
                child_body = (
                    self._render_react_jsx(children, indent + 1)
                    if children
                    else f"{pad}  <p>{label}</p>\n"
                )
                lines.append(
                    f'{pad}<div className="grid">\n'
                    f"{child_body}"
                    f"{pad}</div>\n"
                )
            elif ctype == "Image":
                src = comp.get("src", "https://via.placeholder.com/400x300")
                alt = comp.get("alt", label)
                lines.append(f'{pad}<img src="{src}" alt="{alt}" />\n')
            elif ctype == "Dialog":
                child_body = (
                    self._render_react_jsx(children, indent + 1)
                    if children
                    else f"{pad}  <p>{label}</p>\n"
                )
                lines.append(
                    f"{pad}<dialog>\n"
                    f"{child_body}"
                    f"{pad}</dialog>\n"
                )
            elif ctype == "AppBar":
                title = comp.get("title", label)
                lines.append(
                    f'{pad}<header className="app-bar">\n'
                    f"{pad}  <h1>{title}</h1>\n"
                    f"{pad}</header>\n"
                )
            elif ctype == "BottomNav":
                nav_items = comp.get("items", [])
                item_lines = "".join(
                    f"{pad}  <a href=\"#\">{item}</a>\n" for item in nav_items
                )
                if not item_lines:
                    item_lines = f"{pad}  <a href=\"#\">{label}</a>\n"
                lines.append(
                    f'{pad}<nav className="bottom-nav">\n'
                    f"{item_lines}"
                    f"{pad}</nav>\n"
                )
            elif ctype == "TabBar":
                tabs = comp.get("tabs", comp.get("items", []))
                tab_lines = ""
                for j, tab in enumerate(tabs):
                    active = ' className="active"' if j == 0 else ""
                    tab_lines += f"{pad}  <span{active}>{tab}</span>\n"
                if not tab_lines:
                    tab_lines = f"{pad}  <span className=\"active\">{label}</span>\n"
                lines.append(
                    f'{pad}<div className="tabs">\n'
                    f"{tab_lines}"
                    f"{pad}</div>\n"
                )
            elif ctype == "Container":
                child_body = (
                    self._render_react_jsx(children, indent + 1)
                    if children
                    else f"{pad}  <p>{label}</p>\n"
                )
                lines.append(
                    f"{pad}<div>\n"
                    f"{child_body}"
                    f"{pad}</div>\n"
                )
            else:
                lines.append(f"{pad}<p>{label}</p>\n")

        return "".join(lines)

    def _collect_react_hooks(self, components: List[Dict[str, Any]]) -> str:
        """Collect ``useState`` hooks for input components."""
        hooks: List[str] = []
        for comp in components:
            ctype = comp.get("type", "")
            if ctype == "Input":
                label = comp.get("label", comp.get("text", ""))
                var = self._camel(label or "field")
                setter = "set" + var[0].upper() + var[1:]
                hooks.append(f"  const [{var}, {setter}] = useState('');\n")
            for child in comp.get("children", []):
                hooks.append(self._collect_react_hooks([child]))
        return "".join(hooks)

    # ------------------------------------------------------------------

    def _generate_vue_frontend(
        self,
        screens: List[Dict[str, Any]],
        app_name: str,
    ) -> Dict[str, str]:
        """Generate Vue 3 + TypeScript frontend files.

        Returns:
            Mapping of ``frontend/`` prefixed paths to source content.
        """
        files: Dict[str, str] = {}

        if not screens:
            screens = [{"name": "Home", "components": []}]

        # -- src/main.ts -------------------------------------------------
        files["frontend/src/main.ts"] = (
            "import { createApp } from 'vue';\n"
            "import App from './App.vue';\n"
            "import router from './router';\n\n"
            "const app = createApp(App);\n"
            "app.use(router);\n"
            "app.mount('#app');\n"
        )

        # -- src/App.vue -------------------------------------------------
        nav_items: List[str] = []
        for i, screen in enumerate(screens):
            path = "/" if i == 0 else f"/{self._kebab(screen.get('name', 'home'))}"
            label = screen.get("name", "Home")
            nav_items.append(
                f'      <router-link to="{path}">{label}</router-link>'
            )
        nav_str = "\n".join(nav_items)

        files["frontend/src/App.vue"] = (
            "<template>\n"
            "  <div id=\"app\">\n"
            "    <nav class=\"app-nav\">\n"
            f"      <span class=\"app-title\">{app_name}</span>\n"
            + nav_str + "\n"
            "    </nav>\n"
            "    <main class=\"app-main\">\n"
            "      <router-view />\n"
            "    </main>\n"
            "  </div>\n"
            "</template>\n\n"
            "<script setup lang=\"ts\">\n"
            "</script>\n\n"
            "<style>\n"
            ".app-nav {\n"
            "  display: flex; align-items: center; gap: 16px;\n"
            "  padding: 12px 24px; background: #fff;\n"
            "  border-bottom: 1px solid #e5e7eb;\n"
            "}\n"
            ".app-title { font-weight: 700; font-size: 18px; margin-right: auto; }\n"
            ".app-nav a { text-decoration: none; color: #2563eb; font-weight: 500; }\n"
            ".app-main { flex: 1; padding: 24px; max-width: 1200px; margin: 0 auto; width: 100%; }\n"
            "</style>\n"
        )

        # -- src/router/index.ts -----------------------------------------
        route_imports: List[str] = []
        route_defs: List[str] = []
        for i, screen in enumerate(screens):
            cname = self._pascal(screen.get("name", "Home"))
            screen_name = cname + "Screen"
            path = "/" if i == 0 else f"/{self._kebab(screen.get('name', 'home'))}"
            route_imports.append(
                f"import {screen_name} from '../screens/{screen_name}.vue';"
            )
            route_defs.append(
                f"  {{ path: '{path}', component: {screen_name} }},"
            )

        files["frontend/src/router/index.ts"] = (
            "import { createRouter, createWebHistory } from 'vue-router';\n"
            + "\n".join(route_imports) + "\n\n"
            "const routes = [\n"
            + "\n".join(route_defs) + "\n"
            "];\n\n"
            "const router = createRouter({\n"
            "  history: createWebHistory(),\n"
            "  routes,\n"
            "});\n\n"
            "export default router;\n"
        )

        # -- screen .vue SFC files --------------------------------------
        for screen in screens:
            cname = self._pascal(screen.get("name", "Home"))
            screen_name = cname + "Screen"
            comps = screen.get("components", [])
            template_body = self._render_vue_template(comps, indent=2)
            ref_decls = self._collect_vue_refs(comps)

            files[f"frontend/src/screens/{screen_name}.vue"] = (
                "<template>\n"
                "  <div class=\"screen\">\n"
                f"    <h1>{screen.get('name', 'Home')}</h1>\n"
                + template_body
                + "  </div>\n"
                "</template>\n\n"
                "<script setup lang=\"ts\">\n"
                "import { ref } from 'vue';\n"
                + ref_decls
                + "</script>\n\n"
                "<style scoped>\n"
                ".screen { display: flex; flex-direction: column; gap: 16px; }\n"
                ".card { background: #fff; border-radius: 8px; padding: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }\n"
                ".grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 16px; }\n"
                ".tabs { display: flex; border-bottom: 2px solid #e5e7eb; }\n"
                ".tabs > * { padding: 8px 16px; cursor: pointer; }\n"
                "button { padding: 10px 20px; border: none; border-radius: 6px; background: #2563eb; color: #fff; cursor: pointer; }\n"
                "input { width: 100%; padding: 10px 12px; border: 1px solid #d1d5db; border-radius: 6px; }\n"
                "</style>\n"
            )

        # -- package.json ------------------------------------------------
        pkg = {
            "name": self._kebab(app_name),
            "version": "0.1.0",
            "private": True,
            "type": "module",
            "scripts": {
                "dev": "vite",
                "build": "vue-tsc && vite build",
                "preview": "vite preview",
            },
            "dependencies": {
                "vue": "^3.4.0",
                "vue-router": "^4.2.0",
            },
            "devDependencies": {
                "@vitejs/plugin-vue": "^5.0.0",
                "typescript": "^5.3.0",
                "vite": "^5.0.0",
                "vue-tsc": "^1.8.0",
            },
        }
        files["frontend/package.json"] = json.dumps(pkg, indent=2) + "\n"

        return files

    def _render_vue_template(
        self, components: List[Dict[str, Any]], indent: int
    ) -> str:
        """Render EoStudio components as Vue template HTML."""
        lines: List[str] = []
        pad = "  " * indent

        for comp in components:
            ctype = comp.get("type", "Container")
            label = comp.get("label", comp.get("text", ""))
            children = comp.get("children", [])

            if ctype == "Button":
                lines.append(f"{pad}<button>{label}</button>\n")
            elif ctype == "Text":
                lines.append(f"{pad}<p>{label}</p>\n")
            elif ctype == "Input":
                var = self._camel(label or "field")
                placeholder = comp.get("placeholder", label)
                lines.append(
                    f'{pad}<input v-model="{var}" placeholder="{placeholder}" />\n'
                )
            elif ctype == "Card":
                child_body = (
                    self._render_vue_template(children, indent + 1)
                    if children
                    else f"{pad}  <p>{label}</p>\n"
                )
                lines.append(
                    f'{pad}<div class="card">\n'
                    f"{child_body}"
                    f"{pad}</div>\n"
                )
            elif ctype == "List":
                items = comp.get("items", [])
                li_lines = "".join(
                    f"{pad}    <li>{item}</li>\n" for item in items
                )
                if not li_lines:
                    li_lines = f"{pad}    <li>{label}</li>\n"
                lines.append(f"{pad}<ul>\n{li_lines}{pad}</ul>\n")
            elif ctype == "Grid":
                child_body = (
                    self._render_vue_template(children, indent + 1)
                    if children
                    else f"{pad}  <p>{label}</p>\n"
                )
                lines.append(
                    f'{pad}<div class="grid">\n{child_body}{pad}</div>\n'
                )
            elif ctype == "Image":
                src = comp.get("src", "https://via.placeholder.com/400x300")
                alt = comp.get("alt", label)
                lines.append(f'{pad}<img src="{src}" alt="{alt}" />\n')
            elif ctype == "Dialog":
                child_body = (
                    self._render_vue_template(children, indent + 1)
                    if children
                    else f"{pad}  <p>{label}</p>\n"
                )
                lines.append(
                    f"{pad}<dialog>\n{child_body}{pad}</dialog>\n"
                )
            elif ctype == "AppBar":
                title = comp.get("title", label)
                lines.append(
                    f'{pad}<header class="app-bar">\n'
                    f"{pad}  <h1>{title}</h1>\n"
                    f"{pad}</header>\n"
                )
            elif ctype == "BottomNav":
                nav_items = comp.get("items", [])
                item_lines = "".join(
                    f'{pad}  <a href="#">{item}</a>\n' for item in nav_items
                )
                if not item_lines:
                    item_lines = f'{pad}  <a href="#">{label}</a>\n'
                lines.append(
                    f'{pad}<nav class="bottom-nav">\n{item_lines}{pad}</nav>\n'
                )
            elif ctype == "TabBar":
                tabs = comp.get("tabs", comp.get("items", []))
                tab_lines = ""
                for j, tab in enumerate(tabs):
                    active = ' class="active"' if j == 0 else ""
                    tab_lines += f"{pad}  <span{active}>{tab}</span>\n"
                if not tab_lines:
                    tab_lines = f'{pad}  <span class="active">{label}</span>\n'
                lines.append(
                    f'{pad}<div class="tabs">\n{tab_lines}{pad}</div>\n'
                )
            elif ctype == "Container":
                child_body = (
                    self._render_vue_template(children, indent + 1)
                    if children
                    else f"{pad}  <p>{label}</p>\n"
                )
                lines.append(f"{pad}<div>\n{child_body}{pad}</div>\n")
            else:
                lines.append(f"{pad}<p>{label}</p>\n")

        return "".join(lines)

    def _collect_vue_refs(self, components: List[Dict[str, Any]]) -> str:
        """Collect ``ref()`` declarations for Vue input bindings."""
        refs: List[str] = []
        for comp in components:
            if comp.get("type") == "Input":
                label = comp.get("label", comp.get("text", ""))
                var = self._camel(label or "field")
                refs.append(f"const {var} = ref('');\n")
            for child in comp.get("children", []):
                refs.append(self._collect_vue_refs([child]))
        return "".join(refs)

    # ------------------------------------------------------------------
    # Stub frontends (Angular, Svelte, Next.js)
    # ------------------------------------------------------------------

    def _generate_angular_frontend(
        self,
        screens: List[Dict[str, Any]],
        app_name: str,
    ) -> Dict[str, str]:
        """Generate Angular standalone-component frontend files."""
        files: Dict[str, str] = {}
        if not screens:
            screens = [{"name": "Home", "components": []}]

        route_entries: List[str] = []
        for i, screen in enumerate(screens):
            cname = self._pascal(screen.get("name", "Home"))
            path = "" if i == 0 else self._kebab(screen.get("name", "home"))
            route_entries.append(
                f"  {{ path: '{path}', component: {cname}Component }},"
            )

        imports = "\n".join(
            f"import {{ {self._pascal(s.get('name', 'Home'))}Component }} from './screens/{self._kebab(s.get('name', 'home'))}.component';"
            for s in screens
        )

        files["frontend/src/app/app.routes.ts"] = (
            "import { Routes } from '@angular/router';\n"
            + imports + "\n\n"
            "export const routes: Routes = [\n"
            + "\n".join(route_entries) + "\n"
            "];\n"
        )

        for screen in screens:
            cname = self._pascal(screen.get("name", "Home"))
            kebab = self._kebab(screen.get("name", "home"))
            comps = screen.get("components", [])
            template_body = self._render_react_jsx(comps, indent=2)
            files[f"frontend/src/app/screens/{kebab}.component.ts"] = (
                "import { Component } from '@angular/core';\n"
                "import { CommonModule } from '@angular/common';\n"
                "import { FormsModule } from '@angular/forms';\n\n"
                "@Component({\n"
                "  standalone: true,\n"
                "  imports: [CommonModule, FormsModule],\n"
                f"  selector: 'app-{kebab}',\n"
                "  template: `\n"
                "    <div class=\"screen\">\n"
                f"      <h1>{screen.get('name', 'Home')}</h1>\n"
                + template_body
                + "    </div>\n"
                "  `,\n"
                "})\n"
                f"export class {cname}Component {{}}\n"
            )

        pkg = {
            "name": self._kebab(app_name),
            "version": "0.1.0",
            "private": True,
            "dependencies": {
                "@angular/core": "^17.0.0",
                "@angular/common": "^17.0.0",
                "@angular/router": "^17.0.0",
                "@angular/forms": "^17.0.0",
            },
            "devDependencies": {
                "@angular/cli": "^17.0.0",
                "typescript": "^5.3.0",
            },
        }
        files["frontend/package.json"] = json.dumps(pkg, indent=2) + "\n"
        return files

    def _generate_svelte_frontend(
        self,
        screens: List[Dict[str, Any]],
        app_name: str,
    ) -> Dict[str, str]:
        """Generate SvelteKit frontend files."""
        files: Dict[str, str] = {}
        if not screens:
            screens = [{"name": "Home", "components": []}]

        nav_items: List[str] = []
        for i, screen in enumerate(screens):
            path = "/" if i == 0 else f"/{self._kebab(screen.get('name', 'home'))}"
            nav_items.append(f'    <a href="{path}">{screen.get("name", "Home")}</a>')

        files["frontend/src/routes/+layout.svelte"] = (
            "<script>\n"
            "  import '../app.css';\n"
            "</script>\n\n"
            "<nav class=\"app-nav\">\n"
            f"  <span class=\"app-title\">{app_name}</span>\n"
            + "\n".join(nav_items) + "\n"
            "</nav>\n"
            "<main class=\"app-main\">\n"
            "  <slot />\n"
            "</main>\n"
        )

        for i, screen in enumerate(screens):
            route_dir = "" if i == 0 else self._kebab(screen.get("name", "home"))
            comps = screen.get("components", [])
            body = self._render_react_jsx(comps, indent=1)
            route_path = f"frontend/src/routes/{route_dir}/+page.svelte" if route_dir else "frontend/src/routes/+page.svelte"
            files[route_path] = (
                "<div class=\"screen\">\n"
                f"  <h1>{screen.get('name', 'Home')}</h1>\n"
                + body
                + "</div>\n"
            )

        pkg = {
            "name": self._kebab(app_name),
            "version": "0.1.0",
            "private": True,
            "type": "module",
            "scripts": {
                "dev": "vite dev",
                "build": "vite build",
            },
            "devDependencies": {
                "@sveltejs/kit": "^2.0.0",
                "svelte": "^4.2.0",
                "vite": "^5.0.0",
            },
        }
        files["frontend/package.json"] = json.dumps(pkg, indent=2) + "\n"
        return files

    def _generate_nextjs_frontend(
        self,
        screens: List[Dict[str, Any]],
        app_name: str,
    ) -> Dict[str, str]:
        """Generate Next.js App Router frontend files."""
        files: Dict[str, str] = {}
        if not screens:
            screens = [{"name": "Home", "components": []}]

        nav_items: List[str] = []
        for i, screen in enumerate(screens):
            path = "/" if i == 0 else f"/{self._kebab(screen.get('name', 'home'))}"
            nav_items.append(
                f'        <Link href="{path}">{screen.get("name", "Home")}</Link>'
            )

        files["frontend/src/app/layout.tsx"] = (
            "import React from 'react';\n"
            "import Link from 'next/link';\n"
            "import './globals.css';\n\n"
            "export const metadata = {\n"
            f"  title: '{app_name}',\n"
            "};\n\n"
            "export default function RootLayout({ children }: { children: React.ReactNode }) {\n"
            "  return (\n"
            "    <html lang=\"en\">\n"
            "      <body>\n"
            "        <nav className=\"app-nav\">\n"
            f"          <span className=\"app-title\">{app_name}</span>\n"
            + "\n".join(nav_items) + "\n"
            "        </nav>\n"
            "        <main className=\"app-main\">{children}</main>\n"
            "      </body>\n"
            "    </html>\n"
            "  );\n"
            "}\n"
        )

        for i, screen in enumerate(screens):
            comps = screen.get("components", [])
            body = self._render_react_jsx(comps, indent=2)
            if i == 0:
                page_path = "frontend/src/app/page.tsx"
            else:
                slug = self._kebab(screen.get("name", "home"))
                page_path = f"frontend/src/app/{slug}/page.tsx"

            files[page_path] = (
                "'use client';\n\n"
                "import React from 'react';\n\n"
                f"export default function {self._pascal(screen.get('name', 'Home'))}Page() {{\n"
                "  return (\n"
                "    <div className=\"screen\">\n"
                f"      <h1>{screen.get('name', 'Home')}</h1>\n"
                + body
                + "    </div>\n"
                "  );\n"
                "}\n"
            )

        pkg = {
            "name": self._kebab(app_name),
            "version": "0.1.0",
            "private": True,
            "scripts": {
                "dev": "next dev",
                "build": "next build",
                "start": "next start",
            },
            "dependencies": {
                "next": "^14.0.0",
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
            },
            "devDependencies": {
                "@types/react": "^18.2.0",
                "typescript": "^5.3.0",
            },
        }
        files["frontend/package.json"] = json.dumps(pkg, indent=2) + "\n"
        return files

    # ==================================================================
    # Backend generators
    # ==================================================================

    def _generate_fastapi_backend(
        self,
        models: List[Dict[str, Any]],
        app_name: str,
    ) -> Dict[str, str]:
        """Generate FastAPI + SQLAlchemy backend files.

        Returns:
            Mapping of ``backend/`` prefixed paths to source content.
        """
        files: Dict[str, str] = {}

        # -- app/main.py ------------------------------------------------
        router_imports: List[str] = []
        if models:
            router_imports.append("from app.routes import router")

        files["backend/app/main.py"] = (
            "from fastapi import FastAPI\n"
            "from fastapi.middleware.cors import CORSMiddleware\n"
            + ("from app.routes import router\n" if models else "")
            + "\n"
            f"app = FastAPI(title=\"{app_name} API\", version=\"0.1.0\")\n\n"
            "app.add_middleware(\n"
            "    CORSMiddleware,\n"
            "    allow_origins=[\"http://localhost:3000\", \"http://localhost:5173\"],\n"
            "    allow_credentials=True,\n"
            "    allow_methods=[\"*\"],\n"
            "    allow_headers=[\"*\"],\n"
            ")\n\n"
            + ("app.include_router(router, prefix=\"/api\")\n\n" if models else "")
            + "\n"
            "@app.get(\"/health\")\n"
            "async def health_check():\n"
            "    return {\"status\": \"ok\"}\n"
        )

        # -- app/routes.py ----------------------------------------------
        route_blocks: List[str] = []
        for model in models:
            mname = model.get("name", "Item")
            snake = self._snake(mname)
            pascal = self._pascal(mname)
            route_blocks.append(
                f"\n\n@router.get(\"/{snake}s\", response_model=list[{pascal}])\n"
                f"async def list_{snake}s():\n"
                f"    return []\n\n\n"
                f"@router.get(\"/{snake}s/{{item_id}}\", response_model={pascal})\n"
                f"async def get_{snake}(item_id: int):\n"
                '    return {"id": "item_id"}\n\n\n'
                f"@router.post(\"/{snake}s\", response_model={pascal}, status_code=201)\n"
                f"async def create_{snake}(item: {pascal}):\n"
                f"    return item\n\n\n"
                f"@router.put(\"/{snake}s/{{item_id}}\", response_model={pascal})\n"
                f"async def update_{snake}(item_id: int, item: {pascal}):\n"
                f"    return item\n\n\n"
                f"@router.delete(\"/{snake}s/{{item_id}}\", status_code=204)\n"
                f"async def delete_{snake}(item_id: int):\n"
                f"    return None\n"
            )

        model_imports = ", ".join(
            self._pascal(m.get("name", "Item")) for m in models
        )
        files["backend/app/routes.py"] = (
            "from fastapi import APIRouter\n"
            + (f"from app.models import {model_imports}\n" if models else "")
            + "\nrouter = APIRouter()\n"
            + "".join(route_blocks)
        )

        # -- app/models.py ----------------------------------------------
        model_classes: List[str] = []
        for model in models:
            mname = self._pascal(model.get("name", "Item"))
            fields = model.get("fields", [])
            field_lines: List[str] = []
            for field in fields:
                fname = field.get("name", "value")
                ftype = field.get("type", "str")
                field_lines.append(f"    {fname}: {ftype}")
            body = "\n".join(field_lines) if field_lines else "    pass"
            model_classes.append(
                f"\n\nclass {mname}(BaseModel):\n{body}\n"
            )

        files["backend/app/models.py"] = (
            "from pydantic import BaseModel\n"
            + "".join(model_classes)
            + ("\n\nclass Item(BaseModel):\n    id: int\n    name: str\n" if not models else "")
        )

        # -- app/database.py --------------------------------------------
        files["backend/app/database.py"] = (
            "import os\n\n"
            "from sqlalchemy import create_engine\n"
            "from sqlalchemy.ext.declarative import declarative_base\n"
            "from sqlalchemy.orm import sessionmaker\n\n"
            "DATABASE_URL = os.getenv(\n"
            "    \"DATABASE_URL\",\n"
            "    \"postgresql://postgres:postgres@localhost:5432/" + self._snake(app_name) + "\",\n"
            ")\n\n"
            "engine = create_engine(DATABASE_URL)\n"
            "SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)\n"
            "Base = declarative_base()\n\n\n"
            "def get_db():\n"
            "    db = SessionLocal()\n"
            "    try:\n"
            "        yield db\n"
            "    finally:\n"
            "        db.close()\n"
        )

        # -- app/auth.py ------------------------------------------------
        files["backend/app/auth.py"] = (
            "import os\n"
            "from datetime import datetime, timedelta\n"
            "from typing import Optional\n\n"
            "from fastapi import Depends, HTTPException, status\n"
            "from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer\n\n"
            "SECRET_KEY = os.getenv(\"SECRET_KEY\", \"change-me-in-production\")\n"
            "ALGORITHM = \"HS256\"\n"
            "ACCESS_TOKEN_EXPIRE_MINUTES = 30\n\n"
            "security = HTTPBearer()\n\n\n"
            "def create_access_token(\n"
            "    data: dict, expires_delta: Optional[timedelta] = None\n"
            ") -> str:\n"
            "    \"\"\"Create a JWT access token.\"\"\"\n"
            "    import jwt\n\n"
            "    to_encode = data.copy()\n"
            "    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))\n"
            "    to_encode.update({\"exp\": expire})\n"
            "    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)\n\n\n"
            "def verify_token(\n"
            "    credentials: HTTPAuthorizationCredentials = Depends(security),\n"
            ") -> dict:\n"
            "    \"\"\"Verify a JWT token from the Authorization header.\"\"\"\n"
            "    import jwt\n\n"
            "    try:\n"
            "        payload = jwt.decode(\n"
            "            credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM]\n"
            "        )\n"
            "        return payload\n"
            "    except jwt.PyJWTError:\n"
            "        raise HTTPException(\n"
            "            status_code=status.HTTP_401_UNAUTHORIZED,\n"
            "            detail=\"Invalid authentication credentials\",\n"
            "        )\n"
        )

        # -- requirements.txt -------------------------------------------
        files["backend/requirements.txt"] = (
            "fastapi>=0.104.0\n"
            "uvicorn[standard]>=0.24.0\n"
            "sqlalchemy>=2.0.0\n"
            "pydantic>=2.5.0\n"
            "python-dotenv>=1.0.0\n"
            "PyJWT>=2.8.0\n"
            "psycopg2-binary>=2.9.0\n"
        )

        return files

    # ------------------------------------------------------------------

    def _generate_flask_backend(
        self,
        models: List[Dict[str, Any]],
        app_name: str,
    ) -> Dict[str, str]:
        """Generate Flask + SQLAlchemy backend files.

        Returns:
            Mapping of ``backend/`` prefixed paths to source content.
        """
        files: Dict[str, str] = {}

        # -- app.py -----------------------------------------------------
        files["backend/app.py"] = (
            "import os\n\n"
            "from flask import Flask\n"
            "from flask_cors import CORS\n\n"
            "from routes import bp as routes_bp\n\n\n"
            "def create_app():\n"
            f"    app = Flask(__name__)\n"
            f"    app.config.from_object('config.Config')\n"
            "    CORS(app, origins=[\"http://localhost:3000\", \"http://localhost:5173\"])\n"
            "    app.register_blueprint(routes_bp, url_prefix=\"/api\")\n\n"
            "    @app.route(\"/health\")\n"
            "    def health_check():\n"
            "        return {\"status\": \"ok\"}\n\n"
            "    return app\n\n\n"
            "if __name__ == \"__main__\":\n"
            "    app = create_app()\n"
            "    app.run(debug=True, port=8000)\n"
        )

        # -- routes.py --------------------------------------------------
        route_blocks: List[str] = []
        for model in models:
            mname = model.get("name", "Item")
            snake = self._snake(mname)
            route_blocks.append(
                f"\n\n@bp.route(\"/{snake}s\", methods=[\"GET\"])\n"
                f"def list_{snake}s():\n"
                f"    return jsonify([])\n\n\n"
                f"@bp.route(\"/{snake}s/<int:item_id>\", methods=[\"GET\"])\n"
                f"def get_{snake}(item_id):\n"
                f"    return jsonify({{\"id\": item_id}})\n\n\n"
                f"@bp.route(\"/{snake}s\", methods=[\"POST\"])\n"
                f"def create_{snake}():\n"
                f"    data = request.get_json()\n"
                f"    return jsonify(data), 201\n\n\n"
                f"@bp.route(\"/{snake}s/<int:item_id>\", methods=[\"PUT\"])\n"
                f"def update_{snake}(item_id):\n"
                f"    data = request.get_json()\n"
                f"    return jsonify(data)\n\n\n"
                f"@bp.route(\"/{snake}s/<int:item_id>\", methods=[\"DELETE\"])\n"
                f"def delete_{snake}(item_id):\n"
                f"    return \"\", 204\n"
            )

        files["backend/routes.py"] = (
            "from flask import Blueprint, jsonify, request\n\n"
            "bp = Blueprint(\"api\", __name__)\n"
            + "".join(route_blocks)
        )

        # -- models.py --------------------------------------------------
        model_classes: List[str] = []
        for model in models:
            mname = self._pascal(model.get("name", "Item"))
            fields = model.get("fields", [])
            col_lines: List[str] = []
            type_map = {
                "str": "db.String(255)",
                "int": "db.Integer",
                "float": "db.Float",
                "bool": "db.Boolean",
            }
            for field in fields:
                fname = field.get("name", "value")
                ftype = field.get("type", "str")
                sa_type = type_map.get(ftype, "db.String(255)")
                col_lines.append(f"    {fname} = db.Column({sa_type})")
            body = "\n".join(col_lines) if col_lines else "    pass"
            model_classes.append(
                f"\n\nclass {mname}(db.Model):\n"
                f"    __tablename__ = \"{self._snake(mname)}s\"\n"
                f"    id = db.Column(db.Integer, primary_key=True)\n"
                f"{body}\n"
            )

        files["backend/models.py"] = (
            "from flask_sqlalchemy import SQLAlchemy\n\n"
            "db = SQLAlchemy()\n"
            + "".join(model_classes)
        )

        # -- config.py --------------------------------------------------
        files["backend/config.py"] = (
            "import os\n\n\n"
            "class Config:\n"
            f"    SECRET_KEY = os.getenv(\"SECRET_KEY\", \"change-me-in-production\")\n"
            f"    SQLALCHEMY_DATABASE_URI = os.getenv(\n"
            f"        \"DATABASE_URL\",\n"
            f"        \"postgresql://postgres:postgres@localhost:5432/{self._snake(app_name)}\",\n"
            f"    )\n"
            f"    SQLALCHEMY_TRACK_MODIFICATIONS = False\n"
        )

        # -- requirements.txt -------------------------------------------
        files["backend/requirements.txt"] = (
            "flask>=3.0.0\n"
            "flask-cors>=4.0.0\n"
            "flask-sqlalchemy>=3.1.0\n"
            "sqlalchemy>=2.0.0\n"
            "python-dotenv>=1.0.0\n"
            "psycopg2-binary>=2.9.0\n"
            "gunicorn>=21.2.0\n"
        )

        return files

    # ------------------------------------------------------------------
    # Stub backends (Express, Django)
    # ------------------------------------------------------------------

    def _generate_express_backend(
        self,
        models: List[Dict[str, Any]],
        app_name: str,
    ) -> Dict[str, str]:
        """Generate Express.js + TypeScript backend files."""
        files: Dict[str, str] = {}

        route_blocks: List[str] = []
        for model in models:
            snake = self._snake(model.get("name", "Item"))
            route_blocks.append(
                f"\nrouter.get('/{snake}s', (_req, res) => res.json([]));\n"
                f"router.get('/{snake}s/:id', (req, res) => res.json({{ id: req.params.id }}));\n"
                f"router.post('/{snake}s', (req, res) => res.status(201).json(req.body));\n"
                f"router.put('/{snake}s/:id', (req, res) => res.json(req.body));\n"
                f"router.delete('/{snake}s/:id', (_req, res) => res.sendStatus(204));\n"
            )

        files["backend/src/index.ts"] = (
            "import express from 'express';\n"
            "import cors from 'cors';\n\n"
            "const app = express();\n"
            "const PORT = process.env.PORT || 8000;\n\n"
            "app.use(cors({ origin: ['http://localhost:3000', 'http://localhost:5173'] }));\n"
            "app.use(express.json());\n\n"
            "const router = express.Router();\n"
            + "".join(route_blocks)
            + "\napp.use('/api', router);\n\n"
            "app.get('/health', (_req, res) => res.json({ status: 'ok' }));\n\n"
            "app.listen(PORT, () => {\n"
            f"  console.log(`{app_name} API running on port ${{PORT}}`);\n"
            "});\n"
        )

        pkg = {
            "name": self._kebab(app_name) + "-api",
            "version": "0.1.0",
            "private": True,
            "scripts": {
                "dev": "ts-node-dev src/index.ts",
                "build": "tsc",
                "start": "node dist/index.js",
            },
            "dependencies": {
                "cors": "^2.8.5",
                "express": "^4.18.0",
            },
            "devDependencies": {
                "@types/cors": "^2.8.0",
                "@types/express": "^4.17.0",
                "ts-node-dev": "^2.0.0",
                "typescript": "^5.3.0",
            },
        }
        files["backend/package.json"] = json.dumps(pkg, indent=2) + "\n"
        return files

    def _generate_django_backend(
        self,
        models: List[Dict[str, Any]],
        app_name: str,
    ) -> Dict[str, str]:
        """Generate Django REST Framework backend files."""
        files: Dict[str, str] = {}
        project_snake = self._snake(app_name)

        model_classes: List[str] = []
        for model in models:
            mname = self._pascal(model.get("name", "Item"))
            fields = model.get("fields", [])
            field_lines: List[str] = []
            dj_map = {
                "str": "models.CharField(max_length=255)",
                "int": "models.IntegerField(default=0)",
                "float": "models.FloatField(default=0.0)",
                "bool": "models.BooleanField(default=False)",
            }
            for field in fields:
                fname = field.get("name", "value")
                ftype = field.get("type", "str")
                dj_type = dj_map.get(ftype, "models.CharField(max_length=255)")
                field_lines.append(f"    {fname} = {dj_type}")
            body = "\n".join(field_lines) if field_lines else "    pass"
            model_classes.append(
                f"\n\nclass {mname}(models.Model):\n{body}\n\n"
                f"    def __str__(self):\n"
                f"        return str(self.pk)\n"
            )

        files[f"backend/{project_snake}/models.py"] = (
            "from django.db import models\n"
            + "".join(model_classes)
        )

        files[f"backend/{project_snake}/urls.py"] = (
            "from django.contrib import admin\n"
            "from django.urls import path\n"
            "from django.http import JsonResponse\n\n\n"
            "def health_check(request):\n"
            "    return JsonResponse({\"status\": \"ok\"})\n\n\n"
            "urlpatterns = [\n"
            "    path(\"admin/\", admin.site.urls),\n"
            "    path(\"health\", health_check),\n"
            "]\n"
        )

        files[f"backend/{project_snake}/settings.py"] = (
            "import os\n"
            "from pathlib import Path\n\n"
            "BASE_DIR = Path(__file__).resolve().parent.parent\n"
            f"SECRET_KEY = os.getenv('SECRET_KEY', 'change-me-in-production')\n"
            "DEBUG = True\n"
            "ALLOWED_HOSTS = ['*']\n\n"
            "INSTALLED_APPS = [\n"
            "    'django.contrib.admin',\n"
            "    'django.contrib.auth',\n"
            "    'django.contrib.contenttypes',\n"
            "    'django.contrib.sessions',\n"
            "    'rest_framework',\n"
            "    'corsheaders',\n"
            f"    '{project_snake}',\n"
            "]\n\n"
            "MIDDLEWARE = [\n"
            "    'corsheaders.middleware.CorsMiddleware',\n"
            "    'django.middleware.common.CommonMiddleware',\n"
            "]\n\n"
            f"ROOT_URLCONF = '{project_snake}.urls'\n"
            "CORS_ALLOWED_ORIGINS = [\n"
            "    'http://localhost:3000',\n"
            "    'http://localhost:5173',\n"
            "]\n\n"
            "DATABASES = {\n"
            "    'default': {\n"
            "        'ENGINE': 'django.db.backends.postgresql',\n"
            f"        'NAME': '{project_snake}',\n"
            "        'USER': 'postgres',\n"
            "        'PASSWORD': 'postgres',\n"
            "        'HOST': 'localhost',\n"
            "        'PORT': '5432',\n"
            "    }\n"
            "}\n"
        )

        files["backend/requirements.txt"] = (
            "django>=5.0.0\n"
            "djangorestframework>=3.14.0\n"
            "django-cors-headers>=4.3.0\n"
            "psycopg2-binary>=2.9.0\n"
        )

        files["backend/manage.py"] = (
            "#!/usr/bin/env python\n"
            "import os\n"
            "import sys\n\n\n"
            "def main():\n"
            f"    os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{project_snake}.settings')\n"
            "    from django.core.management import execute_from_command_line\n"
            "    execute_from_command_line(sys.argv)\n\n\n"
            "if __name__ == '__main__':\n"
            "    main()\n"
        )

        return files

    # ==================================================================
    # Infrastructure files
    # ==================================================================

    def _generate_docker_compose(self, app_name: str) -> str:
        """Generate a ``docker-compose.yml`` with frontend, backend, and Postgres."""
        db_name = self._snake(app_name)
        return (
            "version: '3.9'\n\n"
            "services:\n"
            "  frontend:\n"
            "    build: ./frontend\n"
            "    ports:\n"
            "      - '3000:3000'\n"
            "    environment:\n"
            "      - VITE_API_URL=http://localhost:8000\n"
            "    depends_on:\n"
            "      - backend\n\n"
            "  backend:\n"
            "    build: ./backend\n"
            "    ports:\n"
            "      - '8000:8000'\n"
            "    environment:\n"
            f"      - DATABASE_URL=postgresql://postgres:postgres@db:5432/{db_name}\n"
            "      - SECRET_KEY=${SECRET_KEY:-change-me-in-production}\n"
            "    depends_on:\n"
            "      - db\n\n"
            "  db:\n"
            "    image: postgres:16-alpine\n"
            "    ports:\n"
            "      - '5432:5432'\n"
            "    environment:\n"
            "      - POSTGRES_USER=postgres\n"
            "      - POSTGRES_PASSWORD=postgres\n"
            f"      - POSTGRES_DB={db_name}\n"
            "    volumes:\n"
            "      - pgdata:/var/lib/postgresql/data\n\n"
            "volumes:\n"
            "  pgdata:\n"
        )

    @staticmethod
    def _generate_env_example(app_name: str) -> str:
        """Generate a ``.env.example`` with placeholder variables."""
        return (
            "# Database\n"
            f"DATABASE_URL=postgresql://postgres:postgres@localhost:5432/{WebAppGenerator._snake(app_name)}\n\n"
            "# Auth\n"
            "SECRET_KEY=change-me-in-production\n\n"
            "# Frontend\n"
            "API_URL=http://localhost:8000\n"
            "VITE_API_URL=http://localhost:8000\n"
        )

    # ==================================================================
    # Naming helpers
    # ==================================================================

    @staticmethod
    def _pascal(name: str) -> str:
        """Convert a name to PascalCase.

        >>> WebAppGenerator._pascal("user profile")
        'UserProfile'
        """
        return "".join(
            w.capitalize()
            for w in name.replace("-", " ").replace("_", " ").split()
        )

    @staticmethod
    def _snake(name: str) -> str:
        """Convert a name to snake_case.

        >>> WebAppGenerator._snake("User Profile")
        'user_profile'
        """
        return name.lower().replace(" ", "_").replace("-", "_")

    @staticmethod
    def _kebab(name: str) -> str:
        """Convert a name to kebab-case.

        >>> WebAppGenerator._kebab("User Profile")
        'user-profile'
        """
        return name.lower().replace(" ", "-").replace("_", "-")

    @staticmethod
    def _camel(name: str) -> str:
        """Convert a name to camelCase.

        >>> WebAppGenerator._camel("user profile")
        'userProfile'
        """
        clean = "".join(c if c.isalnum() else "_" for c in name)
        parts = [p for p in clean.split("_") if p]
        if not parts:
            return "field"
        return parts[0].lower() + "".join(w.capitalize() for w in parts[1:])
