# EoStudio API Reference

> Python API reference for all EoStudio modules.

## Core AI

### `LLMClient`

```python
from eostudio.core.ai.llm_client import LLMClient, LLMConfig

config = LLMConfig(
    provider="ollama",       # "ollama" or "openai"
    endpoint="",             # Auto-detected from provider
    model="llama3",          # Model name
    api_key="",              # Required for OpenAI
    temperature=0.7,         # 0.0–1.0
    max_tokens=2048,         # Max generation length
    system_prompt="",        # Prepended to all requests
)

client = LLMClient(config)
client = LLMClient.from_env()     # From environment variables
client.is_available() -> bool
client.chat(messages) -> str
client.stream_chat(messages) -> Iterator[str]
client.chat_json(messages) -> dict
```

### `DesignAgent`

```python
from eostudio.core.ai.agent import DesignAgent

agent = DesignAgent(
    endpoint="http://localhost:11434",
    model="llama3",
    provider="ollama",
    api_key="",
    domain="general",    # general|cad|ui|3d|game|hardware|simulation|database|uml
)

agent.ask(prompt: str) -> str
agent.suggest_improvements(design: dict) -> list[str]
agent.explain_component(component_type: str) -> str
agent.generate_design_brief(description: str) -> dict
agent.set_domain(domain: str) -> None
agent.clear_history() -> None
```

### `SmartChat`

```python
from eostudio.core.ai.smart_chat import SmartChat, EditorContext, ChatResponse

chat = SmartChat(editor_type="cad", llm_client=None)

ctx = EditorContext(
    editor_type="cad",
    current_design={"components": [...]},
    selected_components=[...],
    project_name="My Project",
)

response: ChatResponse = chat.send_message("Help me", context=ctx)
# response.content: str
# response.suggestions: list[str]
# response.context_used: bool

chat.get_suggestions(context=ctx) -> list[str]
chat.get_sample_prompts(editor_type=None) -> list[str]
chat.get_history() -> list[dict]
chat.clear_history() -> None
chat.message_count -> int
```

### `AIDesignGenerator`

```python
from eostudio.core.ai.generator import AIDesignGenerator

gen = AIDesignGenerator(llm_client=None)

gen.text_to_ui(description: str) -> dict
gen.text_to_3d(description: str) -> dict
gen.text_to_cad(description: str) -> dict
gen.refine_design(design: dict, feedback: str) -> dict
```

### `AISimulator`

```python
from eostudio.core.ai.simulator import AISimulator

sim = AISimulator(llm_client=None)

sim.suggest_parameters(model: dict) -> dict
sim.analyze_results(signals: dict[str, list[float]]) -> str
sim.detect_instability(signals: dict[str, list[float]]) -> list[str]
sim.recommend_controller(plant_description: str) -> dict
```

---

## Geometry

### Primitives

```python
from eostudio.core.geometry.primitives import (
    Vec2, Vec3, Vec4, Matrix4, BoundingBox, Face, Mesh,
    create_cube, create_sphere, create_cylinder, create_cone,
    create_torus, create_plane,
)

# Vectors
v = Vec3(1.0, 2.0, 3.0)
v.length() -> float
v.normalized() -> Vec3
v.dot(other) -> float
v.cross(other) -> Vec3    # Vec3 only
v + other, v - other, v * scalar

# Matrix
m = Matrix4.identity()
m = Matrix4.translation(x, y, z)
m = Matrix4.scaling(x, y, z)
m = Matrix4.rotation_x(angle)
m * other_matrix

# BoundingBox
bb = BoundingBox(min_point: Vec3, max_point: Vec3)
bb.contains(point: Vec3) -> bool
bb.size() -> Vec3
bb.center() -> Vec3

# Mesh creation
mesh = create_cube(size=1.0)
mesh = create_sphere(radius=1.0, segments=16, rings=12)
mesh = create_cylinder(radius=1.0, height=2.0, segments=16)
mesh = create_cone(radius=1.0, height=2.0, segments=16)
mesh = create_torus(major_radius=2.0, minor_radius=0.5)
mesh = create_plane(width=1.0, height=1.0)
```

### Transforms

```python
from eostudio.core.geometry.transforms import Quaternion, Transform

q = Quaternion(x, y, z, w)
q = Quaternion.from_axis_angle(axis: Vec3, angle: float)
q.length() -> float
q * other_quaternion

t = Transform(position=Vec3(), rotation=Quaternion(), scale=Vec3(1,1,1))
t.apply_to_point(point: Vec3) -> Vec3
t.to_matrix() -> Matrix4
```

---

## Code Generation

### Dispatcher

```python
from eostudio.codegen import generate_code

generate_code(project_file: str, framework: str, output_dir: str)
```

### Individual Generators

```python
from eostudio.codegen.html_css import HTMLCSSGenerator
from eostudio.codegen.react import ReactGenerator
from eostudio.codegen.flutter import FlutterGenerator
from eostudio.codegen.compose import ComposeGenerator
from eostudio.codegen.openscad import OpenSCADGenerator

gen = ReactGenerator()
files: dict[str, str] = gen.generate(components: list, screens: list)
# Returns {filename: content} dict
```

---

## Formats

### Project

```python
from eostudio.formats.project import EoStudioProject

project = EoStudioProject(name="My Project")
project.add_component({"type": "cube", "size": 2})
project.save("output.eostudio")

loaded = EoStudioProject.load("output.eostudio")
loaded.export("stl", "output.stl")
```

### Exporters

```python
from eostudio.formats.obj import OBJExporter
from eostudio.formats.stl import STLExporter
from eostudio.formats.svg import SVGExporter
from eostudio.formats.dxf import DXFExporter
from eostudio.formats.gltf import GLTFExporter

exporter = STLExporter()
ascii_str = exporter.export_ascii(mesh)
binary_bytes = exporter.export_binary(mesh)
exporter.export_to_file(mesh, "output.stl")
```

---

## Simulation

```python
from eostudio.core.simulation.engine import (
    SimulationModel, Signal,
    SourceBlock, GainBlock, SumBlock, PIDBlock, ScopeBlock,
)

model = SimulationModel()
model.dt = 0.01
model.duration = 10.0

src = SourceBlock(block_id="src", name="Step", signal_type="step",
                  amplitude=1.0, frequency=0.0)
pid = PIDBlock(block_id="pid", name="PID", Kp=2.0, Ki=0.5, Kd=0.1)
scope = ScopeBlock(block_id="scope", name="Output")

model.add_block(src)
model.add_block(pid)
model.add_block(scope)
model.connect("src", "pid")
model.connect("pid", "scope")

results: dict[str, Signal] = model.run()
signal = results["Output"]
signal.num_samples() -> int
signal.mean() -> float
signal.rms() -> float
```

---

## Plugins

```python
from eostudio.plugins.plugin_base import (
    Plugin, PluginManager, PluginManifest, PluginHook, PluginState,
)

manager = PluginManager(plugin_dirs=["~/.EoStudio/plugins"])
manifests = manager.discover()
manager.load(plugin_id)
manager.activate(plugin_id, context={})
manager.fire_hook(PluginHook.ON_SAVE, {"path": "file.eos"})
manager.deactivate(plugin_id)
manager.unload(plugin_id)
manager.get_active_plugins() -> list[Plugin]
manager.configure(plugin_id, config_dict)
manager.export_config() -> dict
```

---

## Templates

```python
from eostudio.templates.samples import (
    get_template, list_templates, create_project_from_template,
    ProjectTemplate, BUILTIN_TEMPLATES,
)

templates = list_templates(category="ui")
template = get_template("todo-app")
project_path = create_project_from_template("todo-app", "./output")
```

---

## CLI Commands

| Command | Description |
|---------|-------------|
| `EoStudio launch --editor cad` | Launch GUI |
| `EoStudio export project.eos --format stl -o out.stl` | Export format |
| `EoStudio codegen project.eos --framework react -o ./out` | Generate code |
| `EoStudio teach --lesson shapes` | Kids tutor |
| `EoStudio ask --domain cad "Design a bracket"` | AI Q&A |
| `EoStudio uml-codegen diagram.json --language python -o ./out` | UML→code |
| `EoStudio simulate model.json --dt 0.01 --duration 10` | Run simulation |
| `EoStudio dbgen schema.json --dialect postgresql -o schema.sql` | DB codegen |
| `EoStudio ide` | Launch IDE |
| `EoStudio new --template todo-app -o ./my-project` | New from template |
