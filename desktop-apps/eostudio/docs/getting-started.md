# Getting Started with EoStudio

## Prerequisites

- **Python 3.10+** (3.11 or 3.12 recommended)
- **pip** (included with Python)
- **tkinter** (included with Python on Windows/macOS; on Ubuntu: `sudo apt install python3-tk`)

## Installation

```bash
# Clone the repository
git clone https://github.com/embeddedos-org/EoStudio.git
cd EoStudio

# Install with all features
pip install -e ".[all]"

# Or install specific feature sets:
pip install -e ".[gui]"   # GUI only (Pillow)
pip install -e ".[ai]"    # AI/LLM only (httpx, openai)
pip install -e ".[dev]"   # Development (pytest, flake8, mypy)
```

## Verify Installation

```bash
# Check CLI
EoStudio --version
# Output: EoStudio, version 0.1.0

# Check help
EoStudio --help
```

## Quick Start: Create a 3D Model

```python
from EoStudio.core.geometry.primitives import Mesh, Vec3
from EoStudio.formats.stl import export_stl_ascii

# Create a cube
cube = Mesh.create_cube(size=2.0)
print(f"Cube: {cube.vertex_count()} vertices, {cube.face_count()} faces")

# Create a sphere
sphere = Mesh.create_sphere(radius=1.0, segments=16, rings=12)
sphere.translate(Vec3(3, 0, 0))

# Export to STL
export_stl_ascii(cube, "cube.stl")
print("Exported cube.stl")
```

## Quick Start: Launch the GUI

```bash
# Launch with all editors
EoStudio launch

# Launch specific editor
EoStudio launch --editor 3d       # 3D Modeler
EoStudio launch --editor cad      # CAD Designer
EoStudio launch --editor paint    # Image Editor
EoStudio launch --editor game     # Game Editor
EoStudio launch --editor ui       # UI/UX Designer
EoStudio launch --editor product  # Product Designer

# Choose theme
EoStudio launch --theme dark      # Dark theme (default)
EoStudio launch --theme light     # Light theme
```

## Quick Start: Use the Smart Chat

The Smart Chat panel is available in every editor (right sidebar). It provides:

1. **Sample prompts** — click to auto-fill and send
2. **Sample designs** — click to insert pre-built designs
3. **LLM chat** — ask questions, generate designs

```bash
# CLI-based AI interaction
EoStudio ask "Design a gear with 20 teeth"
EoStudio ask "Create a simple house"
```

To configure the LLM backend:
```bash
# Use Ollama (default, runs locally)
EoStudio ask --endpoint http://localhost:11434 --model llama3 "Make a cube"

# Use OpenAI
EoStudio ask --endpoint https://api.openai.com --model gpt-4 "Make a cube"
```

## Quick Start: Kids Learning Mode

```bash
# Start a lesson
EoStudio teach --lesson shapes           # 2D shapes intro
EoStudio teach --lesson colors           # Color theory
EoStudio teach --lesson 3d-basics        # Cubes and spheres
EoStudio teach --lesson simple-game      # Make a simple game
EoStudio teach --lesson build-robot      # Build a 3D robot
EoStudio teach --lesson design-house     # Design a house

# Set difficulty
EoStudio teach --lesson shapes --difficulty beginner
EoStudio teach --lesson shapes --difficulty intermediate
EoStudio teach --lesson shapes --difficulty advanced
```

## Quick Start: Generate Code from UI Designs

```bash
# Generate Flutter code
EoStudio codegen project.EoStudio --framework flutter --output ./flutter_app/

# Generate HTML/CSS
EoStudio codegen project.EoStudio --framework html --output ./website/

# Generate React
EoStudio codegen project.EoStudio --framework react --output ./react_app/

# Generate Compose Multiplatform
EoStudio codegen project.EoStudio --framework compose --output ./compose_app/
```

## Quick Start: Export Designs

```bash
# Export to STL (3D printing)
EoStudio export project.EoStudio --format stl --output model.stl

# Export to OBJ (3D model)
EoStudio export project.EoStudio --format obj --output model.obj

# Export to SVG (2D vector)
EoStudio export project.EoStudio --format svg --output drawing.svg

# Export to glTF (3D web)
EoStudio export project.EoStudio --format gltf --output scene.gltf

# Export to DXF (CAD)
EoStudio export project.EoStudio --format dxf --output sketch.dxf
```

## Project Structure

```
EoStudio/
├── pyproject.toml          # Package configuration
├── README.md               # Project overview
├── LICENSE                  # MIT License
├── EoStudio/              # Main package
│   ├── cli/                # CLI commands (launch, export, codegen, teach, ask)
│   ├── core/               # Engine modules
│   │   ├── geometry/       # Vectors, matrices, meshes, curves, CSG
│   │   ├── rendering/      # Scene graph, camera, rasterizer, lighting
│   │   ├── physics/        # Rigid bodies, collision, particles
│   │   ├── image/          # Canvas, layers, brushes, filters
│   │   ├── cad/            # Parametric modeling, constraints, assembly
│   │   ├── ui_flow/        # UI components, flow graphs, code generation
│   │   ├── game/           # ECS, tilemap, sprites, visual scripting
│   │   └── ai/             # LLM agent, tutor, generator, smart chat
│   ├── gui/                # tkinter GUI
│   │   ├── editors/        # 6 editor panels
│   │   ├── widgets/        # 8 reusable widgets
│   │   └── dialogs/        # 3 dialog windows
│   ├── formats/            # File format handlers
│   ├── codegen/            # Code generators
│   └── templates/          # Sample design templates
├── tests/                  # Unit + integration tests
├── docs/                   # Documentation
└── .github/workflows/      # CI pipeline
```

## Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=EoStudio --cov-report=term-missing

# Run specific test file
pytest tests/unit/test_geometry.py -v
```

## Contributing

1. Fork the repository
2. Create a feature branch from `master`
3. Make your changes
4. Run tests: `pytest tests/ -v`
5. Run linter: `flake8 EoStudio/`
6. Submit a pull request to `master`

See [CONTRIBUTING.md](../CONTRIBUTING.md) for details.
