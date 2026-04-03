# EoStudio Integration Guide

> Connect EoStudio with external tools, build systems, and workflows.

## EoSim Integration

EoStudio integrates with [EoSim](https://github.com/embeddedos-org/EoSim) for hardware simulation:

```python
from eostudio.plugins.eosim_plugin import EoSimPlugin
from eostudio.plugins.plugin_base import PluginManager

manager = PluginManager()
plugin = EoSimPlugin()
manager.plugins["eosim"] = plugin
manager.activate("eosim", {"eosim_path": "/path/to/eosim"})

# Fire simulation hook
results = manager.fire_hook(PluginHook.ON_SIMULATE, {
    "model": model_dict,
    "platform": "stm32f407",
})
```

**Supported platforms:** 22 boards (STM32, ESP32, Raspberry Pi, Arduino, etc.)
**Simulation domains:** 14 domains (GPIO, ADC, PWM, SPI, I2C, UART, Timer, etc.)

---

## Using Generated Code in IDEs

### Visual Studio Code

```bash
# Generate React project
EoStudio codegen design.eostudio --framework react -o ./my-app
cd my-app
code .
npm install && npm start
```

### Xcode (Swift/SwiftUI)

```bash
EoStudio codegen design.eostudio --framework mobile-swift -o ./ios-app
open ios-app/MyApp.xcodeproj
```

### Android Studio (Kotlin/Compose)

```bash
EoStudio codegen design.eostudio --framework mobile-kotlin -o ./android-app
# Open android-app/ in Android Studio
```

---

## Build System Integration

### npm / Node.js (React, Vue, Angular, Svelte, Next.js, Electron)

```bash
EoStudio codegen design.eostudio --framework react -o ./output
cd output
npm install
npm run dev     # Development
npm run build   # Production
```

### Flutter / Dart

```bash
EoStudio codegen design.eostudio --framework flutter -o ./output
cd output
flutter pub get
flutter run
```

### Gradle (Kotlin/Compose)

```bash
EoStudio codegen design.eostudio --framework compose -o ./output
cd output
./gradlew assembleDebug
```

### pip / Python (FastAPI, Flask, Django, tkinter, Qt)

```bash
EoStudio codegen design.eostudio --framework webapp-react-fastapi -o ./output
cd output
pip install -r requirements.txt
uvicorn main:app --reload
```

### Cargo / Rust (Tauri, WASM)

```bash
EoStudio codegen design.eostudio --framework desktop-tauri -o ./output
cd output
cargo tauri dev
```

### CMake (for firmware/hardware projects)

```bash
EoStudio codegen design.eostudio --framework firmware-eos -o ./output
cd output
mkdir build && cd build
cmake .. -DBOARD=stm32f407
make
```

### OpenSCAD (3D printing)

```bash
EoStudio codegen design.eostudio --framework openscad -o ./output
openscad output/design.scad    # Preview
openscad -o output.stl output/design.scad  # Export STL
```

---

## Git Workflow for EoStudio Projects

`.eostudio` project files are JSON — they work well with Git:

```bash
# Initialise
git init
git add my-project.eostudio README.md
git commit -m "Initial design"

# Track changes
git diff my-project.eostudio   # See what changed in the design

# Branching for design iterations
git checkout -b experiment-dark-theme
# ... modify design ...
git commit -am "Try dark theme variant"
```

### Recommended `.gitignore`

```gitignore
# Generated output
output/
build/
dist/
node_modules/

# OS files
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
```

---

## Import/Export Format Reference

| Format | Extension | Use Case | Direction |
|--------|-----------|----------|-----------|
| EoStudio Project | `.eostudio` | Native project format | Read/Write |
| Wavefront OBJ | `.obj` | 3D mesh interchange | Export |
| STL | `.stl` | 3D printing | Export (ASCII + Binary) |
| SVG | `.svg` | 2D vector graphics | Export |
| glTF | `.gltf` | 3D web interchange | Export |
| DXF | `.dxf` | CAD 2D sketching | Export |

### Export via CLI

```bash
EoStudio export project.eostudio --format stl -o output.stl
EoStudio export project.eostudio --format svg -o output.svg
EoStudio export project.eostudio --format obj -o output.obj
```

### Export via Python API

```python
from eostudio.formats.project import EoStudioProject
from eostudio.formats.stl import STLExporter
from eostudio.core.geometry.primitives import create_cube

project = EoStudioProject.load("design.eostudio")
mesh = create_cube(10.0)
exporter = STLExporter()
exporter.export_to_file(mesh, "output.stl")
```
