# EoStudio

**Cross-Platform Design Suite with LLM Integration**

[![CI](https://github.com/embeddedos-org/EoStudio/actions/workflows/ci.yml/badge.svg?branch=master)](https://github.com/embeddedos-org/EoStudio/actions)
[![codecov](https://codecov.io/gh/embeddedos-org/EoStudio/branch/master/graph/badge.svg)](https://codecov.io/gh/embeddedos-org/EoStudio)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-0.1.0-blue)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

EoStudio is a unified design tool suite for the [EmbeddedOS](https://embeddedos-org.github.io) ecosystem — combining 3D modeling, CAD design, image editing, game design, UI/UX flow design, interior design, UML modeling, MATLAB-style simulation, multi-platform code generation, database design, and LLM-powered AI assistance — all running on **Windows**, **Ubuntu/Linux**, and **EoS**.

## Quick Start

```bash
# Clone & install
git clone https://github.com/embeddedos-org/EoStudio.git
cd EoStudio
pip install -e ".[all]"

# Launch the design suite
EoStudio launch

# Create a project from template
EoStudio new --template todo-app -o ./my-app

# Generate React code from a design
EoStudio codegen my-app/todo-app.eostudio --framework react -o ./output

# Ask the AI design agent
EoStudio ask "Design a responsive dashboard with charts"

# Kids learning mode
EoStudio teach --lesson shapes
```

## Features

### 12 Design Editors

| Editor | CLI Flag | Use Case |
|--------|----------|----------|
| 3D Modeler | `--editor 3d` | Mesh modeling, materials, lighting |
| CAD Designer | `--editor cad` | Parametric design, assemblies, constraints |
| Image Editor | `--editor paint` | Layers, brushes, filters |
| Game Editor | `--editor game` | ECS, tilemaps, sprites |
| UI/UX Designer | `--editor ui` | Components, flows, prototyping |
| Product Designer | `--editor product` | BOM, 3D-print validation |
| Interior Designer | `--editor interior` | Floor plans, furniture |
| UML Modeler | `--editor uml` | Class, sequence, state diagrams |
| Simulation Editor | `--editor simulation` | Block diagrams, PID, signals |
| Database Designer | `--editor database` | ERD, schema, SQL/ORM codegen |
| Hardware Editor | `--editor hardware` | PCB layout, schematics, Gerber |
| IDE | `--editor ide` | Code editing, debugging, Git |

### 30+ Code Generators

| Target | Frameworks |
|--------|-----------|
| **Mobile** | Flutter, React Native, Kotlin (Android), Swift (iOS) |
| **Desktop** | Electron, Tauri, tkinter, Qt, Compose Desktop |
| **Web (Full-Stack)** | React+FastAPI, Vue+Flask, Angular+Express, Svelte+Django |
| **Database** | SQLite, PostgreSQL, MySQL, SQLAlchemy, Prisma, Django Models |
| **UML → Code** | Python, Java, Kotlin, TypeScript, C++, C# |
| **3D/CAD** | OpenSCAD, STL, OBJ, glTF, DXF |
| **Game Engines** | Godot, Unity, Unreal |
| **Firmware** | EoS, Baremetal, FreeRTOS, Zephyr |

### AI & LLM Integration

| Feature | Description |
|---------|------------|
| **Design Agent** | Multi-domain Q&A, design brief generation, improvement suggestions |
| **Smart Chat** | Per-editor AI panel with context-aware prompts |
| **AI Generator** | Text-to-UI, text-to-3D, text-to-CAD design generation |
| **AI Simulator** | Parameter suggestion, instability detection, controller tuning |
| **Kids Tutor** | Interactive lessons with quizzes and encouragement |

**LLM Backends:** Ollama (local, default) + OpenAI API — see [AI Guide](docs/ai-guide.md)

## AI / LLM Quick Setup

```bash
# Option 1: Ollama (local, private)
ollama pull llama3
EoStudio ask "Design a login page"

# Option 2: OpenAI API
export EOSTUDIO_LLM_PROVIDER=openai
export OPENAI_API_KEY=sk-your-key
export EOSTUDIO_LLM_MODEL=gpt-4o
EoStudio ask --domain cad "Design an L-bracket with mounting holes"
```

## Example Projects

5 built-in templates demonstrating real workflows:

| Template | Workflow | Command |
|----------|----------|---------|
| `todo-app` | UI Designer → React/Flutter code | `EoStudio new --template todo-app -o ./app` |
| `mechanical-part` | CAD Designer → OpenSCAD → STL | `EoStudio new --template mechanical-part -o ./part` |
| `game-platformer` | Game Editor → Godot/Unity export | `EoStudio new --template game-platformer -o ./game` |
| `iot-dashboard` | Database + UI → Full-stack webapp | `EoStudio new --template iot-dashboard -o ./dash` |
| `simulation-pid` | Simulation Editor → PID analysis | `EoStudio new --template simulation-pid -o ./sim` |

## Documentation

| Guide | Description |
|-------|-------------|
| [Getting Started](docs/getting-started.md) | Installation, first project, basic usage |
| [Editors Guide](docs/editors-guide.md) | All 12 editors — features, components, shortcuts |
| [Code Generation Guide](docs/codegen-guide.md) | 30+ frameworks — usage, output structure |
| [AI & LLM Guide](docs/ai-guide.md) | LLM setup, Smart Chat, AI Generator, prompts |
| [Plugin Guide](docs/plugin-guide.md) | Plugin development — hooks, manifest, lifecycle |
| [Integration Guide](docs/integration-guide.md) | External tools, build systems, Git workflow |
| [API Reference](docs/api-reference.md) | Python API for all modules |
| [Architecture](docs/architecture.md) | System design, module relationships, data flow |

## Architecture

```
eostudio/
├── cli/               # Click CLI (10 commands)
├── core/
│   ├── ai/            # LLMClient, DesignAgent, SmartChat, AIGenerator, AISimulator, Tutor
│   ├── geometry/      # Vec2/3/4, Matrix4, Mesh, Bezier, NURBS, CSG
│   ├── rendering/     # Rasterizer, scene graph, camera, Phong lighting
│   ├── physics/       # Rigid body, collision, particles
│   ├── cad/           # Parametric design, constraints, assembly
│   ├── simulation/    # Block diagrams, PID, signals, ODE solver
│   ├── uml/           # 5 diagram types + code generation
│   ├── game/          # ECS, tilemap, sprites, scripting
│   ├── image/         # Layers, brushes, filters
│   ├── hardware/      # PCB, schematic, Gerber
│   ├── ui_flow/       # Component library, prototyping
│   └── interior/      # Floor plans, furniture
├── gui/
│   ├── editors/       # 12 visual editors
│   ├── widgets/       # Viewport, canvas, timeline, properties
│   └── dialogs/       # Export, settings, AI chat
├── codegen/           # 30+ framework code generators
├── formats/           # .EoStudio, OBJ, STL, SVG, glTF, DXF
├── plugins/           # Plugin system + EoSim integration
└── templates/         # 5 project templates
```

## Testing

```bash
# Install dev dependencies
pip install -e ".[dev,all]"

# Run all tests
pytest -v

# Run with coverage
pytest --cov=eostudio --cov-report=term-missing

# Lint
flake8 eostudio/ tests/ --max-line-length=120

# Type checking
mypy eostudio/ --ignore-missing-imports
```

**Test coverage:** 6 test files with 100+ test cases covering AI modules, geometry, codegen, plugins, simulation, formats, and integration.

## Plugin System

Extend EoStudio with custom tools, editors, and exporters:

```python
from eostudio.plugins.plugin_base import Plugin, PluginHook

class MyPlugin(Plugin):
    def activate(self, context):
        self._hooks[PluginHook.POST_CODEGEN] = self._on_codegen
        return super().activate(context)

    def _on_codegen(self, data):
        # Post-process generated code
        return {"processed": True}
```

See [Plugin Guide](docs/plugin-guide.md) for full documentation.

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Install dev dependencies: `pip install -e ".[dev,all]"`
4. Make your changes and add tests
5. Run tests: `pytest -v`
6. Submit a pull request

## Platform Support

| Platform | Status | Backend |
|----------|--------|---------|
| Windows 10/11 | ✅ | tkinter |
| Ubuntu 22.04+ | ✅ | tkinter |
| Linux (other) | ✅ | tkinter |
| macOS | ✅ | macOS native |
| EoS | ✅ | Framebuffer/SDL2 |
| Browser | 🔧 | Web backend |

## EoS Ecosystem

| Repo | Description |
|------|------------|
| [eos](https://github.com/embeddedos-org/eos) | Embedded OS — HAL, RTOS kernel, services |
| [eboot](https://github.com/embeddedos-org/eboot) | Bootloader — 24 board ports, secure boot |
| [ebuild](https://github.com/embeddedos-org/ebuild) | Build system — SDK generator, packaging |
| [eipc](https://github.com/embeddedos-org/eipc) | IPC framework — Go + C SDK, HMAC auth |
| [eai](https://github.com/embeddedos-org/eai) | AI layer — LLM inference, agent loop |
| [eApps](https://github.com/embeddedos-org/eApps) | Cross-platform apps — 38 C + LVGL apps |
| [eosim](https://github.com/embeddedos-org/eosim) | Multi-architecture simulator |
| **EoStudio** | **Design suite with LLM (this repo)** |

## License

MIT License — see [LICENSE](LICENSE) for details.
