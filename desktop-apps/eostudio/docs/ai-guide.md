# EoStudio AI & LLM Guide

> Configure and use AI-powered features across all EoStudio editors.

## LLM Backend Setup

EoStudio supports two LLM backends: **Ollama** (local, default) and **OpenAI API**.

### Option 1: Ollama (Local — Recommended for Privacy)

1. Install Ollama: https://ollama.ai
2. Pull a model:
   ```bash
   ollama pull llama3
   ```
3. Ollama runs on `http://localhost:11434` by default — EoStudio uses this automatically.

### Option 2: OpenAI API

Set environment variables:
```bash
export EOSTUDIO_LLM_PROVIDER=openai
export OPENAI_API_KEY=sk-your-key-here
export EOSTUDIO_LLM_MODEL=gpt-4o
```

### Environment Variable Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `EOSTUDIO_LLM_PROVIDER` | `ollama` | `"ollama"` or `"openai"` |
| `EOSTUDIO_LLM_MODEL` | `llama3` | Model name |
| `EOSTUDIO_LLM_ENDPOINT` | Auto | API base URL |
| `OPENAI_API_KEY` | (none) | Required for OpenAI |
| `EOSTUDIO_LLM_TEMPERATURE` | `0.7` | Sampling temperature (0.0–1.0) |
| `EOSTUDIO_LLM_MAX_TOKENS` | `2048` | Max tokens to generate |

---

## AI Features Overview

### 1. Design Agent (`ask` command)

Ask free-form design questions from the CLI:

```bash
# General design question
EoStudio ask "How do I design a responsive dashboard?"

# Domain-specific (CAD context)
EoStudio ask --domain cad "Design a bracket with 4 mounting holes"

# Using OpenAI
EoStudio ask --provider openai --api-key sk-... "Explain PID controllers"
```

**Domain options:** `general`, `cad`, `ui`, `3d`, `game`, `hardware`, `simulation`, `database`, `uml`

### 2. Smart Chat (Per-Editor AI Panel)

Each editor has a context-aware AI chat panel:

- **CAD Editor** → Knows about constraints, tolerances, manufacturing
- **UI Designer** → Knows about WCAG accessibility, responsive layout
- **Game Editor** → Knows about ECS, tilemaps, game loops
- **Simulation Editor** → Knows about PID, transfer functions, stability

The chat panel injects the current design context (selected components, project metadata) into prompts for better answers.

#### Sample Prompts by Editor

| Editor | Sample Prompts |
|--------|---------------|
| CAD | "Design a bracket with mounting holes", "Check manufacturability" |
| UI | "Design a responsive login form", "Check accessibility issues" |
| Game | "Set up a 2D platformer level", "Create enemy patrol AI" |
| Simulation | "Set up a PID controller", "Why is my simulation oscillating?" |
| Database | "Design a schema for e-commerce", "Normalise this table to 3NF" |
| Hardware | "Design an LED blink circuit", "Choose a voltage regulator for 3.3V" |

### 3. AI Design Generator

Generate designs from natural language:

```python
from eostudio.core.ai.generator import AIDesignGenerator

gen = AIDesignGenerator()

# Text to UI
ui_design = gen.text_to_ui("A login page with email, password, and remember me checkbox")

# Text to 3D
scene = gen.text_to_3d("A snowman with three stacked spheres and a carrot nose")

# Text to CAD
cad_part = gen.text_to_cad("An L-bracket with 4 mounting holes, 60mm wide")

# Iterative refinement
updated = gen.refine_design(ui_design, "Add a forgot password link")
```

### 4. AI Simulator

Get intelligent assistance for simulation workflows:

```python
from eostudio.core.ai.simulator import AISimulator

sim = AISimulator()

# Suggest parameters
params = sim.suggest_parameters(model_dict)

# Detect instability (no LLM needed — runs locally)
warnings = sim.detect_instability({"output": signal_values})

# Recommend controller
controller = sim.recommend_controller("A DC motor with 0.5s time constant")

# Analyse results
analysis = sim.analyze_results({"output": values, "error": error_values})
```

### 5. Kids Tutor

Interactive learning mode for children:

```bash
EoStudio teach --lesson shapes --difficulty beginner
```

**Available lessons:** `shapes`, `colors`, `3d-basics`, `simple-game`, `build-robot`, `design-house`

---

## Prompt Engineering Tips

1. **Be specific:** "Design a login form with email and password" > "Design a form"
2. **Specify framework:** Include the target framework for code-relevant questions
3. **Use domain mode:** `--domain cad` gives CAD-specific vocabulary and constraints
4. **Iterate:** Use `refine_design()` to progressively improve AI-generated designs
5. **Provide context:** In Smart Chat, keep the editor open — the AI sees your current design

---

## Python API

```python
from eostudio.core.ai import (
    LLMClient, LLMConfig,
    DesignAgent, SmartChat,
    AIDesignGenerator, AISimulator,
)

# Create a client from environment
client = LLMClient.from_env()
if client.is_available():
    reply = client.chat([{"role": "user", "content": "Hello"}])

# Create an agent with specific config
agent = DesignAgent(
    provider="openai",
    model="gpt-4o",
    api_key="sk-...",
    domain="cad",
)
answer = agent.ask("What's the best fillet radius for 3D printing?")

# Smart Chat with context
from eostudio.core.ai.smart_chat import EditorContext
chat = SmartChat(editor_type="ui")
ctx = EditorContext(
    current_design={"components": [{"type": "Button", "label": "OK"}]},
)
response = chat.send_message("How can I improve this design?", ctx)
print(response.content)
print(response.suggestions)
```
