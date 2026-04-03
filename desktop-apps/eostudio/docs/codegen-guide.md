# EoStudio Code Generation Guide

> Generate production-ready code from visual designs across 30+ frameworks.

## How Code Generation Works

```
Design (visual editor)
  └→ Component Tree (JSON)
       └→ Framework Generator
            └→ Project Files (source code, configs, build scripts)
```

1. **Design** your UI, database, or 3D model in the visual editor
2. **Export** triggers the code generator for your chosen framework
3. **Output** is a complete project scaffold with routing, navigation, and data models

## CLI Usage

```bash
# Basic code generation
EoStudio codegen project.eostudio --framework react -o ./output

# Database schema generation
EoStudio dbgen schema.eostudio --dialect postgresql -o schema.sql

# UML to code
EoStudio uml-codegen diagram.json --language python -o ./output
```

## Framework Matrix

### Mobile (4 frameworks)

| Framework | CLI Flag | Output |
|-----------|----------|--------|
| Flutter | `mobile-flutter` | `pubspec.yaml`, `lib/main.dart`, screens, widgets |
| React Native | `mobile-react-native` | `package.json`, `App.tsx`, screens, navigation |
| Kotlin/Android | `mobile-kotlin` | `build.gradle.kts`, `MainActivity.kt`, Compose screens |
| Swift/SwiftUI | `mobile-swift` | Xcode project, `ContentView.swift`, navigation |

### Web Frontend (5 frameworks)

| Framework | CLI Flag | Output |
|-----------|----------|--------|
| React | `react` | `package.json`, `src/App.jsx`, screens, CSS modules |
| Vue | (via webapp) | `package.json`, `.vue` SFCs, Vuex store, router |
| Angular | (via webapp) | `angular.json`, components, services, routing module |
| Svelte | (via webapp) | `package.json`, `.svelte` components, stores |
| Next.js | (via webapp) | `next.config.js`, pages, API routes, SSR setup |

### Web Backend (4 frameworks)

| Framework | CLI Flag | Output |
|-----------|----------|--------|
| FastAPI | `webapp-react-fastapi` | `requirements.txt`, routes, models, Pydantic schemas |
| Flask | `webapp-vue-flask` | `requirements.txt`, blueprints, templates |
| Express.js | `webapp-angular-express` | `package.json`, routes, middleware, controllers |
| Django | (via webapp) | `manage.py`, models, views, templates, settings |

### Desktop (5 frameworks)

| Framework | CLI Flag | Output |
|-----------|----------|--------|
| Electron | `desktop-electron` | `package.json`, `main.js`, `preload.js`, renderer |
| Tauri | `desktop-tauri` | `Cargo.toml`, `tauri.conf.json`, Rust backend |
| tkinter | `desktop-tkinter` | Python script with tkinter widgets |
| Qt/PySide6 | `desktop-qt` | Python script with PySide6 widgets, `.ui` files |
| Compose Desktop | (via compose) | Kotlin/Compose Multiplatform project |

### Database (6 dialects)

| Dialect | CLI Flag | Output |
|---------|----------|--------|
| SQLite | `database-sql` | DDL with `CREATE TABLE`, indexes, triggers |
| PostgreSQL | `database-sql` | DDL with PG-specific types, sequences |
| MySQL | `database-sql` | DDL with MySQL-specific syntax |
| SQLAlchemy | `database-sqlalchemy` | Python models with relationships |
| Prisma | `database-prisma` | `schema.prisma` with models and relations |
| Django Models | `database-django` | `models.py` with Django ORM fields |

### 3D / CAD (1 framework)

| Framework | CLI Flag | Output |
|-----------|----------|--------|
| OpenSCAD | `openscad` | `.scad` file with primitives, transforms, CSG |

### Game Engines (3 frameworks)

| Framework | CLI Flag | Output |
|-----------|----------|--------|
| Godot | (via game_engine) | GDScript scenes, sprites, tilemaps |
| Unity | (via game_engine) | C# scripts, scene files, prefabs |
| Unreal | (via game_engine) | C++ actors, blueprints |

### Other (7 frameworks)

| Framework | Output |
|-----------|--------|
| .NET MAUI | XAML + C# for cross-platform mobile/desktop |
| WPF | XAML + C# for Windows desktop |
| WinUI 3 | XAML + C# for modern Windows |
| GTK (Python) | Python script with GTK4 widgets |
| GTK (C) | C source with GTK4 widgets |
| WASM (Rust) | `Cargo.toml`, Rust WASM bindings |
| WASM (AssemblyScript) | TypeScript-like WASM code |

## Output Structure

Each generator produces a complete, runnable project scaffold:

```
output/
├── package.json / pubspec.yaml / build.gradle.kts
├── src/
│   ├── App.jsx / main.dart / MainActivity.kt
│   ├── screens/
│   │   ├── HomeScreen.jsx
│   │   └── SettingsScreen.jsx
│   ├── components/           (shared widgets)
│   ├── navigation/           (router/nav setup)
│   └── styles/               (CSS/theme files)
├── .env                      (environment config)
├── Dockerfile               (containerisation)
└── README.md                (project-specific docs)
```

## Python API

```python
from eostudio.codegen import generate_code
from eostudio.codegen.react import ReactGenerator
from eostudio.codegen.flutter import FlutterGenerator

# Via dispatcher
generate_code("project.eostudio", "react", "./output")

# Direct generator usage
gen = ReactGenerator()
files = gen.generate(components, screens)
for filename, content in files.items():
    print(f"{filename}: {len(content)} bytes")
```

## Customising Generated Code

The generated code is intended as a starting point. Common customisations:

1. **Styling** — Replace generated CSS with your design system
2. **State Management** — Swap basic `useState` for Redux/Zustand/Riverpod
3. **API Layer** — Connect generated UI to your actual backend APIs
4. **Authentication** — Replace placeholder auth with your auth provider
5. **Testing** — Add component/widget tests to the generated scaffold
