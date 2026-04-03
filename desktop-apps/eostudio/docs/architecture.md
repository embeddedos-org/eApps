# EoStudio Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     EoStudio Application                       │
│                                                                 │
│  ┌──────────────────── GUI Layer (tkinter) ──────────────────┐  │
│  │                                                           │  │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌───────────────┐  │  │
│  │  │   3D    │ │  CAD    │ │  Image  │ │  Smart Chat   │  │  │
│  │  │ Modeler │ │ Editor  │ │ Editor  │ │  (AI Panel)   │  │  │
│  │  └────┬────┘ └────┬────┘ └────┬────┘ └───────┬───────┘  │  │
│  │  ┌────┴────┐ ┌────┴────┐ ┌────┴────┐ ┌───────┴───────┐  │  │
│  │  │  Game   │ │  UI/UX  │ │Product  │ │   AI Chat     │  │  │
│  │  │ Editor  │ │Designer │ │Designer │ │   Dialog      │  │  │
│  │  └────┬────┘ └────┬────┘ └────┬────┘ └───────┬───────┘  │  │
│  │       │           │           │               │          │  │
│  │  Widgets: Viewport3D, Canvas2D, Timeline,     │          │  │
│  │  Properties, Hierarchy, Toolbar, ColorPicker,  │          │  │
│  │  LayersPanel                                   │          │  │
│  └────────────────────┬──────────────────────────┘          │
│                       │                                      │
│  ┌──────────────── Core Engines ────────────────────────────┐  │
│  │                                                          │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐ │  │
│  │  │ Geometry │ │Rendering │ │ Physics  │ │   Image    │ │  │
│  │  │ Vec2/3/4 │ │ Scene    │ │ Rigid    │ │  Canvas    │ │  │
│  │  │ Matrix4  │ │ Camera   │ │ Body     │ │  Layers    │ │  │
│  │  │ Mesh     │ │ Material │ │ Collision│ │  Brushes   │ │  │
│  │  │ Bezier   │ │ Lighting │ │ Particle │ │  Filters   │ │  │
│  │  │ NURBS    │ │Rasterizer│ │          │ │  Tools     │ │  │
│  │  │ CSG      │ │          │ │          │ │            │ │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └────────────┘ │  │
│  │                                                          │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐ │  │
│  │  │   CAD    │ │ UI Flow  │ │   Game   │ │  AI / LLM  │ │  │
│  │  │ Sketch   │ │Component │ │  Entity  │ │  Agent     │ │  │
│  │  │ Feature  │ │  Flow    │ │  Tilemap │ │  Tutor     │ │  │
│  │  │ Assembly │ │Prototype │ │  Sprite  │ │  Generator │ │  │
│  │  │ Constrain│ │ CodeGen  │ │  Script  │ │  SmartChat │ │  │
│  │  │ Export   │ │          │ │          │ │  Simulator │ │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └────────────┘ │  │
│  └──────────────────────────────────────────────────────────┘  │
│                       │                                        │
│  ┌────────────── I/O Layer ─────────────────────────────────┐  │
│  │                                                          │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────────────────────┐ │  │
│  │  │ Formats  │ │ CodeGen  │ │      Templates           │ │  │
│  │  │.EoStudio│ │ HTML/CSS │ │  3D │ CAD │ UI │ Game    │ │  │
│  │  │ OBJ/STL  │ │ Flutter  │ │        Kids              │ │  │
│  │  │ SVG/glTF │ │ Compose  │ │                          │ │  │
│  │  │ DXF      │ │ React    │ │                          │ │  │
│  │  │          │ │ OpenSCAD │ │                          │ │  │
│  │  └──────────┘ └──────────┘ └──────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────────┘  │
│                       │                                        │
│  ┌────────────── CLI Layer (Click) ─────────────────────────┐  │
│  │  EoStudio launch | export | codegen | teach | ask       │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Module Relationships

### Core Dependencies

```
geometry ──> rendering (scene graph uses Transform, Mesh)
geometry ──> physics   (rigid bodies use Vec3, BoundingBox)
geometry ──> cad       (parametric uses Mesh, curves)
geometry ──> image     (canvas coordinates use Vec2)
geometry ──> game      (entities use Vec2, Vec3)

rendering ──> gui/widgets/viewport_3d (renders to canvas)
physics   ──> game/entities           (rigid body component)
image     ──> gui/editors/image_editor
cad       ──> gui/editors/cad_editor
ui_flow   ──> gui/editors/ui_designer
game      ──> gui/editors/game_editor

ai/agent     ──> all editors (smart chat integration)
ai/tutor     ──> cli/teach command
ai/generator ──> geometry (text-to-3D mesh generation)
ai/smart_chat ──> gui/dialogs/ai_chat (UI panel)

formats   ──> geometry (Mesh import/export)
codegen   ──> ui_flow  (component tree to framework code)
templates ──> ai/smart_chat (sample designs for chatbot)
```

### Data Flow

```
User Input ──> Editor (GUI) ──> Core Engine ──> State Update
                                    │
                                    ├──> Renderer ──> Display
                                    ├──> Smart Chat ──> LLM ──> Response
                                    └──> Export ──> File / Code
```

## LLM Integration Architecture

The Smart Chat system integrates with every editor through a unified architecture:

```
┌────────────────┐    ┌───────────────┐    ┌──────────────────┐
│  AI Chat Panel │───>│  SmartChat    │───>│   DesignAgent    │
│  (gui/dialog)  │    │  (core/ai)    │    │   (core/ai)      │
│                │    │               │    │                  │
│  - Messages    │    │ - Prompts     │    │ - Ollama backend │
│  - Suggestions │    │ - Samples     │    │ - OpenAI backend │
│  - Gallery     │    │ - Tutorials   │    │ - Custom backend │
└────────────────┘    │ - Context     │    └──────────────────┘
                      └───────┬───────┘
                              │
                 ┌────────────┼────────────┐
                 │            │            │
          ┌──────▼──────┐ ┌──▼─────┐ ┌────▼──────┐
          │AIDesignGen  │ │KidsTutor│ │AISimulator│
          │text-to-3D   │ │Lessons  │ │Physics    │
          │text-to-UI   │ │Quizzes  │ │What-if    │
          │text-to-CAD  │ │Progress │ │Improve    │
          └─────────────┘ └────────┘ └───────────┘
```

## File Format Pipeline

```
                    ┌──────────────┐
                    │  .EoStudio  │  (JSON project file)
                    │   Project    │
                    └──────┬───────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
   ┌──────▼──────┐  ┌─────▼─────┐  ┌───────▼───────┐
   │  3D Export  │  │ 2D Export │  │  Code Export  │
   │  STL / OBJ │  │  SVG / PNG│  │  HTML / Dart  │
   │  glTF / DXF│  │  DXF      │  │  Kotlin / JSX │
   └─────────────┘  └───────────┘  │  OpenSCAD     │
                                   └───────────────┘
```

## Platform Support

| Platform | GUI | CLI | Headless Export |
|----------|-----|-----|-----------------|
| Windows  | ✅ tkinter | ✅ Click | ✅ |
| Ubuntu   | ✅ tkinter | ✅ Click | ✅ |
| Linux    | ✅ tkinter | ✅ Click | ✅ |
| EoS      | ✅ EoS Display HAL | ✅ Click | ✅ |

## Branch Strategy

- **`master`** — Stable release branch
- Feature branches merged via pull requests
- CI runs on every push/PR to `master`
# EoStudio Architecture

## System Overview

```
┌────────────────────────────────────────────────────────────────────┐
│                        EoStudio Application                       │
├──────────────┬──────────────┬──────────────┬───────────────────────┤
│   GUI Layer  │  CLI Layer   │  Codegen     │  Templates            │
│  (Tkinter)   │  (argparse)  │  (html/flutter│ (sample scenes)      │
│              │              │   compose/    │                       │
│              │              │   react/scad) │                       │
├──────────────┴──────────────┴──────────────┴───────────────────────┤
│                         Core Engine                                │
├──────────┬──────────┬──────────┬──────────┬──────────┬─────────────┤
│ Geometry │ Rendering│   CAD    │  Image   │  UI Flow │   Game      │
│ ──────── │ ──────── │ ──────── │ ──────── │ ──────── │ ──────────  │
│ Vec2/3/4 │ Camera   │ Constr-  │ Canvas   │ Compo-   │ Entities    │
│ Matrix4  │ Material │ aints    │ Layers   │ nents    │ Sprites     │
│ Mesh     │ Lighting │ Paramet- │ Brushes  │ Flow     │ Tilemap     │
│ Curves   │ Scene    │ ric      │ Filters  │ Graph    │ Scripting   │
│ Boolean  │ Raster-  │ Assembly │ Tools    │ Proto-   │             │
│ Ops      │ izer     │ Export   │          │ typing   │             │
├──────────┴──────────┴──────────┴──────────┴──────────┴─────────────┤
│                        AI Integration                              │
│  Agent  │  Generator  │  Tutor (Kids Mode)  │  Simulator           │
├──────────────────────────────────────────────────────────────────── │
│                        Physics Engine                              │
│  Rigid Body  │  Collision Detection  │  Particle System            │
├────────────────────────────────────────────────────────────────────┤
│                      File Formats I/O                              │
│  .EoStudio (JSON)  │ OBJ │ STL │ SVG │ glTF │ DXF                │
└────────────────────────────────────────────────────────────────────┘
```

## Module Relationships

### Core Geometry (`EoStudio.core.geometry`)
The mathematical foundation of the entire system.

- **primitives.py** — `Vec2`, `Vec3`, `Vec4`, `Matrix4`, `BoundingBox`, `Face`, `Mesh`
  - Provides all vector/matrix math, mesh construction (cube, sphere, cylinder, cone, torus, plane)
  - Used by every other module that deals with spatial data

- **transforms.py** — `Quaternion`, `Transform`
  - TRS (Translation-Rotation-Scale) system built on top of `Matrix4` and `Vec3`
  - Used by rendering, CAD, physics, and game engines

- **curves.py** — `BezierCurve`, `BSpline`, `NURBSCurve`
  - Parametric curve evaluation for CAD and animation paths

- **boolean_ops.py** — CSG operations (`union`, `difference`, `intersection`)
  - Operates on `Mesh` instances for constructive solid geometry

### Rendering (`EoStudio.core.rendering`)
Transforms scene graphs into pixel output.

```
Scene ─────┬──→ Camera (view/projection matrices)
           ├──→ Lighting (point, directional, spot, ambient)
           ├──→ Material (PBR properties, textures)
           └──→ Rasterizer (triangle rasterisation, depth buffer)
```

### CAD Engine (`EoStudio.core.cad`)
Precision engineering tools.

- **constraints.py** — Geometric constraint solver (distance, angle, coincident, parallel)
- **parametric.py** — Parametric modelling with named parameters and rebuild
- **assembly.py** — Multi-part assembly management with joints
- **export.py** — CAD-specific export (STEP-like, DXF)

### Image Editor (`EoStudio.core.image`)
2D raster editing pipeline.

```
Canvas ──→ Layers ──→ Brushes ──→ Filters ──→ Tools
```

### UI Flow Designer (`EoStudio.core.ui_flow`)
Screen/component-based UI design for app prototyping.

```
Components ──→ FlowGraph ──→ Prototyping ──→ CodeGen
```

### AI Integration (`EoStudio.core.ai`)
LLM-powered features.

- **agent.py** — Chat interface that interprets natural language commands
- **generator.py** — Generates 3D scenes, UI layouts, and CAD models from text descriptions
- **tutor.py** — Kid-friendly guided tutorials with step-by-step instructions
- **simulator.py** — Runs physics and game simulations with AI-controlled entities

### Physics Engine (`EoStudio.core.physics`)

- **rigid_body.py** — Newtonian rigid body dynamics (mass, force, torque, integration)
- **collision.py** — AABB and sphere collision detection + response
- **particles.py** — Particle system with emitters, forces, and lifetime management

### Game Engine (`EoStudio.core.game`)

- **entities.py** — Entity-Component-System (ECS) architecture
- **sprite.py** — 2D sprite management (atlas, animation, rendering)
- **tilemap.py** — Grid-based tile maps for 2D games
- **scripting.py** — Sandboxed scripting environment for game logic

## Data Flow

```
User Input (mouse/keyboard/touch/voice)
    │
    ▼
┌─────────────────┐
│   GUI / CLI     │  ← Tkinter widgets, argparse commands
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Core Engine    │  ← Geometry, CAD, Image, UI Flow, Game
│  (Scene Graph)  │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐ ┌────────────┐
│Renderer│ │ File Export │
│(Screen)│ │ (OBJ/STL/  │
│        │ │  SVG/glTF/ │
│        │ │  DXF)      │
└────────┘ └────────────┘
```

## LLM Integration Points

1. **Smart Chat** (`EoStudio.core.ai.agent`)
   - User describes what they want in natural language
   - Agent parses intent → calls core engine APIs → returns result
   - Supports: "Create a cube", "Make it blue", "Export to STL"

2. **AI Generator** (`EoStudio.core.ai.generator`)
   - Text-to-3D: "Generate a house with a red roof"
   - Text-to-UI: "Create a login screen with email and password"
   - Text-to-CAD: "Design a bracket with two mounting holes"

3. **Kids Tutor** (`EoStudio.core.ai.tutor`)
   - Step-by-step guided projects
   - Explains concepts at age-appropriate level
   - "Let's learn about shapes!" → interactive 3D shape builder

4. **AI Simulator** (`EoStudio.core.ai.simulator`)
   - AI-controlled NPCs and physics interactions
   - "Make the ball bounce off the walls"

## File Format Pipeline

```
EoStudioProject (.EoStudio JSON)
    │
    ├──→ OBJ Export  (Wavefront — vertices, normals, faces)
    ├──→ STL Export  (ASCII or Binary — triangulated mesh)
    ├──→ SVG Export  (2D vector — rect, circle, line, path, text)
    ├──→ glTF Export (3D interchange — embedded base64 binary buffer)
    ├──→ DXF Export  (CAD sketch — LINE, CIRCLE, ARC entities)
    │
    └──→ Code Generation
         ├──→ HTML/CSS (responsive flexbox/grid)
         ├──→ Flutter  (Dart + Material widgets)
         ├──→ Compose  (Kotlin + Jetpack Compose)
         ├──→ React    (JSX + CSS modules + React Router)
         └──→ OpenSCAD (parametric 3D printing)
```

## Directory Structure

```
EoStudio/
├── EoStudio/
│   ├── __init__.py
│   ├── cli/                    # Command-line interface
│   ├── core/
│   │   ├── geometry/           # Vec, Matrix, Mesh, Curves, CSG
│   │   ├── rendering/          # Camera, Material, Lighting, Rasterizer, Scene
│   │   ├── cad/                # Constraints, Parametric, Assembly
│   │   ├── image/              # Canvas, Layers, Brushes, Filters, Tools
│   │   ├── ui_flow/            # Components, FlowGraph, Prototyping, CodeGen
│   │   ├── game/               # Entities, Sprite, Tilemap, Scripting
│   │   ├── physics/            # RigidBody, Collision, Particles
│   │   └── ai/                 # Agent, Generator, Tutor, Simulator
│   ├── gui/
│   │   ├── editors/            # 3D Modeler, CAD, Image, UI Designer, Game
│   │   ├── widgets/            # Viewport, Canvas, Properties, Timeline, etc.
│   │   └── dialogs/            # Modal dialogs
│   ├── formats/                # OBJ, STL, SVG, glTF, DXF, Project
│   ├── codegen/                # HTML/CSS, Flutter, Compose, React, OpenSCAD
│   └── templates/              # Sample project templates
├── tests/
│   ├── unit/                   # test_geometry, test_codegen
│   └── integration/            # test_project (save/load/export round-trips)
├── docs/                       # architecture.md, getting-started.md
├── .github/workflows/ci.yml   # GitHub Actions CI
└── pyproject.toml              # Project metadata + dependencies
```
