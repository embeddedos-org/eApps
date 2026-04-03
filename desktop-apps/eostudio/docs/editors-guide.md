# EoStudio Editors Guide

> Complete reference for all 12 editors in EoStudio.

## Editor Overview

| # | Editor | CLI Flag | Use Case |
|---|--------|----------|----------|
| 1 | 3D Modeler | `--editor 3d` | 3D mesh modelling, rendering, animation |
| 2 | CAD Designer | `--editor cad` | Parametric engineering design, assemblies |
| 3 | Image Editor | `--editor paint` | 2D raster/vector image editing |
| 4 | Game Editor | `--editor game` | 2D/3D game level design, ECS |
| 5 | UI/UX Designer | `--editor ui` | User interface prototyping, wireframes |
| 6 | Product Designer | `--editor product` | BOM generation, 3D-print validation |
| 7 | Interior Designer | `--editor interior` | Floor plans, furniture layout |
| 8 | UML Modeler | `--editor uml` | Class, sequence, state machine diagrams |
| 9 | Simulation Editor | `--editor simulation` | Block diagram simulation (MATLAB-style) |
| 10 | Database Designer | `--editor database` | ERD, schema design, SQL/ORM codegen |
| 11 | Hardware Editor | `--editor hardware` | PCB layout, schematics, Gerber export |
| 12 | IDE | `--editor ide` | Code editing, debugging, Git, terminal |

---

## 1. 3D Modeler (`--editor 3d`)

Design 3D scenes using primitives, meshes, materials, and lighting.

**Key Features:**
- Primitive creation: cube, sphere, cylinder, cone, torus, plane
- CSG boolean operations: union, difference, intersection
- Material editor with PBR properties
- Camera and lighting setup (point, directional, ambient)
- Animation timeline with keyframes
- UV mapping editor

**Component Types:** `cube`, `sphere`, `cylinder`, `cone`, `torus`, `plane`, `mesh`, `group`, `light`, `camera`

**Export Formats:** OBJ, STL, glTF, OpenSCAD

---

## 2. CAD Designer (`--editor cad`)

Parametric engineering design with constraints and assemblies.

**Key Features:**
- Parametric sketching with dimensions
- 3D features: extrude, revolve, fillet, chamfer, hole, pattern
- Assembly mode with mates and constraints
- BOM (Bill of Materials) generation
- Tolerance and GD&T annotation
- Manufacturing export (DXF, STL for 3D printing)

**Component Types:** `sketch`, `extrude`, `revolve`, `fillet`, `chamfer`, `hole`, `pattern`, `mirror`, `shell`, `loft`, `sweep`

**Export Formats:** DXF, STL, OpenSCAD

---

## 3. Image Editor (`--editor paint`)

Raster and vector image editing with layers and filters.

**Key Features:**
- Multi-layer canvas with blend modes
- Brush engine (pressure, opacity, size)
- Shape tools (rectangle, ellipse, polygon, line)
- Filters (blur, sharpen, colour adjust, noise)
- Selection tools (marquee, lasso, magic wand)
- Colour picker with palette management

**Export Formats:** SVG, PNG (requires Pillow)

---

## 4. Game Editor (`--editor game`)

2D/3D game level design using an entity-component system.

**Key Features:**
- Tilemap editor with multi-layer support
- Sprite sheet animation
- Entity-component system (physics, collision, AI, input)
- Scene hierarchy with nested entities
- Scripting support (visual and code)
- Game preview mode

**Component Types:** `tilemap`, `entity`, `sprite`, `light`, `camera`, `trigger`

**Code Generation:** Godot (GDScript), Unity (C#), Unreal (C++)

---

## 5. UI/UX Designer (`--editor ui`)

Visual interface design and prototyping.

**Key Features:**
- Drag-and-drop component palette
- Responsive layout with flex/grid
- Multi-screen flow design with navigation
- Design tokens (colours, spacing, typography)
- Accessibility checker (WCAG 2.1)
- Interactive prototyping with state management

**Component Types:** `Heading`, `Text`, `Button`, `Input`, `Card`, `Container`, `Image`, `List`, `Checkbox`, `Radio`, `Select`, `Slider`, `Toggle`, `Tabs`, `Modal`, `Navbar`, `Footer`, `Sidebar`, `Form`, `Table`, `Chart`

**Code Generation:** React, Flutter, Compose, HTML/CSS, Vue, Angular, Svelte, React Native, Swift, Kotlin

---

## 6. Product Designer (`--editor product`)

Physical product design with manufacturing workflows.

**Key Features:**
- 3D model import and annotation
- BOM (Bill of Materials) generation
- 3D-print validation (wall thickness, overhangs)
- Material selection database
- Cost estimation
- Manufacturing process selection

---

## 7. Interior Designer (`--editor interior`)

Architectural interior layout and visualisation.

**Key Features:**
- 2D floor plan editor
- Wall, door, window placement
- Furniture library with drag-and-drop
- Room dimension annotation
- Lighting simulation
- 3D walkthrough preview

---

## 8. UML Modeler (`--editor uml`)

Software architecture diagrams with code generation.

**Key Features:**
- Class diagrams with attributes, methods, relationships
- Sequence diagrams with lifelines and messages
- State machine diagrams
- Use case diagrams
- Activity diagrams
- Export to PlantUML and Mermaid syntax

**Code Generation:** Python, Java, Kotlin, TypeScript, C++, C#

---

## 9. Simulation Editor (`--editor simulation`)

MATLAB/Simulink-style block diagram simulation.

**Key Features:**
- Block palette: Source, Gain, Sum, PID, Scope, Transfer Function
- Signal wiring with feedback loops
- Real-time simulation with configurable dt
- Scope display with signal analysis
- PID auto-tuning (via AI assistant)
- Step/impulse/sine/ramp signal sources

**Block Types:** `source`, `gain`, `sum`, `pid`, `scope`, `transfer_function`, `delay`, `saturation`

---

## 10. Database Designer (`--editor database`)

Visual database schema design with code generation.

**Key Features:**
- Entity-Relationship Diagram (ERD) editor
- Table designer with columns, types, constraints
- Foreign key relationship editor
- Index designer
- Migration script generation
- Visual query builder

**Code Generation:** SQL (SQLite, PostgreSQL, MySQL), SQLAlchemy, Prisma, Django Models

---

## 11. Hardware Editor (`--editor hardware`)

Electronic schematic capture and PCB layout.

**Key Features:**
- Schematic editor with component library
- PCB layout with auto-router
- Component footprint editor
- Design rule checker (DRC)
- Gerber file export
- Bill of materials for procurement

**Export Formats:** Gerber, BOM CSV

---

## 12. IDE (`--editor ide`)

Integrated development environment for code editing.

**Key Features:**
- Syntax-highlighted code editor
- Language server protocol (LSP) support
- Integrated terminal
- Git version control (stage, commit, push, pull)
- Extension manager
- Debugger with breakpoints
- Project file explorer

---

## Launching Editors

```bash
# Launch specific editor
EoStudio launch --editor cad

# Launch with light theme
EoStudio launch --editor ui --theme light

# Launch all editors (default)
EoStudio launch

# Launch IDE
EoStudio ide
```

## AI Chat in Editors

Every editor has a built-in AI Smart Chat panel. See [AI Guide](ai-guide.md) for details on configuring LLM backends and using context-aware chat.
