"""Built-in project templates for EoStudio.

Provides ready-to-use project templates that demonstrate real workflows
across different editor types.  Templates can be listed, inspected, and
used to scaffold new projects via the CLI (``EoStudio new --template ...``).
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ProjectTemplate:
    """A built-in project template."""

    name: str
    description: str
    category: str
    editor_type: str
    components: List[Dict[str, Any]] = field(default_factory=list)
    screens: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_project_dict(self) -> Dict[str, Any]:
        """Convert to an EoStudio project JSON structure."""
        return {
            "version": "0.1.0",
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "editor_type": self.editor_type,
            "components": self.components,
            "screens": self.screens,
            "metadata": self.metadata,
        }


# ------------------------------------------------------------------
# Built-in templates
# ------------------------------------------------------------------

BUILTIN_TEMPLATES: Dict[str, ProjectTemplate] = {
    "todo-app": ProjectTemplate(
        name="todo-app",
        description="Todo App — UI Designer → React/Flutter code → working app",
        category="ui",
        editor_type="ui",
        components=[
            {"type": "Heading", "label": "My Todo List", "style": {"fontSize": 24, "fontWeight": "bold"}},
            {"type": "Container", "direction": "row", "children": [
                {"type": "Input", "label": "New Task", "placeholder": "What needs to be done?",
                 "style": {"flex": 1}},
                {"type": "Button", "label": "Add", "style": {"marginLeft": 8}},
            ]},
            {"type": "Container", "direction": "row", "style": {"marginTop": 16}, "children": [
                {"type": "Button", "label": "All", "variant": "outlined"},
                {"type": "Button", "label": "Active", "variant": "outlined"},
                {"type": "Button", "label": "Completed", "variant": "outlined"},
            ]},
            {"type": "List", "label": "Tasks", "children": [
                {"type": "ListItem", "label": "Buy groceries", "children": [
                    {"type": "Checkbox", "label": "", "checked": False},
                    {"type": "Text", "label": "Buy groceries"},
                    {"type": "Button", "label": "×", "variant": "text"},
                ]},
                {"type": "ListItem", "label": "Read a book", "children": [
                    {"type": "Checkbox", "label": "", "checked": True},
                    {"type": "Text", "label": "Read a book", "style": {"textDecoration": "line-through"}},
                    {"type": "Button", "label": "×", "variant": "text"},
                ]},
            ]},
            {"type": "Text", "label": "2 items left",
             "style": {"color": "#888", "marginTop": 16}},
        ],
        screens=[
            {"name": "Home", "components": [
                {"type": "Navbar", "label": "Todo App", "children": [
                    {"type": "Link", "label": "Tasks", "href": "/"},
                    {"type": "Link", "label": "Settings", "href": "/settings"},
                ]},
            ]},
            {"name": "Settings", "components": [
                {"type": "Heading", "label": "Settings"},
                {"type": "Toggle", "label": "Dark Mode"},
                {"type": "Select", "label": "Sort By",
                 "options": ["Date Created", "Priority", "Alphabetical"]},
                {"type": "Button", "label": "Clear Completed Tasks", "variant": "outlined"},
            ]},
        ],
        metadata={
            "frameworks": ["react", "flutter", "html"],
            "difficulty": "beginner",
            "estimated_time": "15 minutes",
        },
    ),

    "mechanical-part": ProjectTemplate(
        name="mechanical-part",
        description="Parametric L-Bracket — CAD Designer → OpenSCAD → 3D printable STL",
        category="cad",
        editor_type="cad",
        components=[
            {"type": "cube", "size": [60, 40, 5], "position": [0, 0, 0], "color": "#A0A0A0",
             "label": "base_plate"},
            {"type": "cube", "size": [5, 40, 50], "position": [0, 0, 0], "color": "#A0A0A0",
             "label": "vertical_plate"},
            {"type": "cylinder", "radius": 3, "height": 5, "position": [15, 10, 0],
             "label": "mount_hole_1", "operation": "subtract"},
            {"type": "cylinder", "radius": 3, "height": 5, "position": [15, 30, 0],
             "label": "mount_hole_2", "operation": "subtract"},
            {"type": "cylinder", "radius": 3, "height": 5, "position": [45, 10, 0],
             "label": "mount_hole_3", "operation": "subtract"},
            {"type": "cylinder", "radius": 3, "height": 5, "position": [45, 30, 0],
             "label": "mount_hole_4", "operation": "subtract"},
            {"type": "fillet", "radius": 3, "edges": ["base_vertical_junction"],
             "label": "structural_fillet"},
        ],
        screens=[],
        metadata={
            "parameters": {
                "base_width": 60, "base_depth": 40, "plate_thickness": 5,
                "vertical_height": 50, "hole_radius": 3,
                "fillet_radius": 3, "material": "PLA",
            },
            "units": "mm",
            "export_formats": ["stl", "openscad", "dxf"],
            "frameworks": ["openscad"],
            "difficulty": "intermediate",
            "estimated_time": "20 minutes",
        },
    ),

    "game-platformer": ProjectTemplate(
        name="game-platformer",
        description="2D Platformer — Game Editor → Godot/Unity export",
        category="game",
        editor_type="game",
        components=[
            {"type": "tilemap", "name": "level_1", "tile_size": 32,
             "width": 40, "height": 15, "layers": [
                 {"name": "background", "tiles": "fill:sky_blue"},
                 {"name": "terrain", "tiles": "ground:row_14,platforms:scattered"},
             ]},
            {"type": "entity", "name": "player", "sprite": "hero_idle",
             "position": [64, 384], "components": {
                 "physics": {"gravity": 980, "max_speed": 200, "jump_force": 400},
                 "animation": {"idle": "hero_idle", "run": "hero_run",
                               "jump": "hero_jump", "fall": "hero_fall"},
                 "collision": {"shape": "rectangle", "size": [24, 32]},
                 "input": {"left": "A", "right": "D", "jump": "Space"},
             }},
            {"type": "entity", "name": "coin", "sprite": "coin_spin",
             "position": [256, 352], "components": {
                 "collectible": {"value": 10, "sound": "coin_pickup"},
                 "animation": {"idle": "coin_spin"},
                 "collision": {"shape": "circle", "radius": 12, "trigger": True},
             }},
            {"type": "entity", "name": "enemy_slime", "sprite": "slime_idle",
             "position": [512, 384], "components": {
                 "ai": {"type": "patrol", "speed": 60, "range": 128},
                 "health": {"max_hp": 1, "damage_on_touch": 1},
                 "animation": {"idle": "slime_idle", "move": "slime_move"},
                 "collision": {"shape": "rectangle", "size": [28, 20]},
             }},
            {"type": "entity", "name": "flag", "sprite": "flag_wave",
             "position": [1216, 352], "components": {
                 "goal": {"next_level": "level_2", "sound": "level_complete"},
                 "animation": {"idle": "flag_wave"},
             }},
        ],
        screens=[],
        metadata={
            "game_settings": {
                "resolution": [640, 480], "fps": 60,
                "gravity": 980, "camera_follow": "player",
            },
            "export_formats": ["godot", "unity"],
            "frameworks": ["godot", "unity"],
            "difficulty": "intermediate",
            "estimated_time": "30 minutes",
        },
    ),

    "iot-dashboard": ProjectTemplate(
        name="iot-dashboard",
        description="IoT Dashboard — Database + UI Designer → Full-stack webapp",
        category="webapp",
        editor_type="database",
        components=[
            {"type": "table", "name": "sensors", "columns": [
                {"name": "id", "type": "INTEGER", "primary_key": True, "auto_increment": True},
                {"name": "name", "type": "VARCHAR(100)", "not_null": True},
                {"name": "type", "type": "VARCHAR(50)", "not_null": True},
                {"name": "location", "type": "VARCHAR(200)"},
                {"name": "status", "type": "VARCHAR(20)", "default": "'active'"},
                {"name": "created_at", "type": "TIMESTAMP", "default": "CURRENT_TIMESTAMP"},
            ]},
            {"type": "table", "name": "readings", "columns": [
                {"name": "id", "type": "INTEGER", "primary_key": True, "auto_increment": True},
                {"name": "sensor_id", "type": "INTEGER", "foreign_key": "sensors.id"},
                {"name": "value", "type": "FLOAT", "not_null": True},
                {"name": "unit", "type": "VARCHAR(20)", "not_null": True},
                {"name": "timestamp", "type": "TIMESTAMP", "default": "CURRENT_TIMESTAMP"},
            ]},
            {"type": "table", "name": "alerts", "columns": [
                {"name": "id", "type": "INTEGER", "primary_key": True, "auto_increment": True},
                {"name": "sensor_id", "type": "INTEGER", "foreign_key": "sensors.id"},
                {"name": "rule", "type": "VARCHAR(200)", "not_null": True},
                {"name": "threshold", "type": "FLOAT", "not_null": True},
                {"name": "triggered_at", "type": "TIMESTAMP"},
                {"name": "acknowledged", "type": "BOOLEAN", "default": "FALSE"},
            ]},
        ],
        screens=[
            {"name": "Dashboard", "components": [
                {"type": "Navbar", "label": "IoT Dashboard"},
                {"type": "Container", "direction": "row", "children": [
                    {"type": "Card", "label": "Temperature", "children": [
                        {"type": "Chart", "chart_type": "line", "data_source": "readings",
                         "filter": "type=temperature"},
                        {"type": "Text", "label": "24.5°C", "style": {"fontSize": 32}},
                    ]},
                    {"type": "Card", "label": "Humidity", "children": [
                        {"type": "Chart", "chart_type": "gauge", "data_source": "readings",
                         "filter": "type=humidity"},
                        {"type": "Text", "label": "65%", "style": {"fontSize": 32}},
                    ]},
                    {"type": "Card", "label": "Active Alerts", "children": [
                        {"type": "Badge", "label": "3", "color": "red"},
                        {"type": "List", "label": "Recent Alerts"},
                    ]},
                ]},
                {"type": "Table", "label": "Sensor Readings", "data_source": "readings",
                 "columns": ["sensor", "value", "unit", "timestamp"]},
            ]},
            {"name": "Sensors", "components": [
                {"type": "Heading", "label": "Manage Sensors"},
                {"type": "Button", "label": "Add Sensor"},
                {"type": "Table", "label": "All Sensors", "data_source": "sensors"},
            ]},
        ],
        metadata={
            "frameworks": ["webapp-react-fastapi", "database-sqlalchemy"],
            "difficulty": "advanced",
            "estimated_time": "45 minutes",
        },
    ),

    "simulation-pid": ProjectTemplate(
        name="simulation-pid",
        description="PID Controller — Simulation Editor → analyse step response",
        category="simulation",
        editor_type="simulation",
        components=[
            {"type": "source", "id": "step_input", "name": "Step Input",
             "signal_type": "step", "amplitude": 1.0, "step_time": 1.0,
             "position": [50, 150]},
            {"type": "sum", "id": "error_sum", "name": "Error",
             "inputs": ["+", "-"], "position": [200, 150]},
            {"type": "pid", "id": "pid_controller", "name": "PID Controller",
             "Kp": 2.0, "Ki": 0.5, "Kd": 0.1,
             "position": [350, 150]},
            {"type": "gain", "id": "plant", "name": "Plant (1st order)",
             "gain": 1.0, "time_constant": 0.5,
             "position": [500, 150]},
            {"type": "scope", "id": "output_scope", "name": "Output",
             "position": [650, 150]},
            {"type": "scope", "id": "error_scope", "name": "Error Signal",
             "position": [200, 300]},
        ],
        screens=[],
        metadata={
            "connections": [
                {"from": "step_input", "to": "error_sum", "port": 0},
                {"from": "error_sum", "to": "pid_controller"},
                {"from": "pid_controller", "to": "plant"},
                {"from": "plant", "to": "output_scope"},
                {"from": "plant", "to": "error_sum", "port": 1, "feedback": True},
                {"from": "error_sum", "to": "error_scope"},
            ],
            "simulation": {
                "dt": 0.01, "duration": 10.0,
                "solver": "euler",
            },
            "frameworks": [],
            "difficulty": "intermediate",
            "estimated_time": "20 minutes",
        },
    ),
}


# ------------------------------------------------------------------
# Public API
# ------------------------------------------------------------------

def get_template(name: str) -> Optional[ProjectTemplate]:
    """Get a template by name."""
    return BUILTIN_TEMPLATES.get(name)


def list_templates(category: Optional[str] = None) -> List[ProjectTemplate]:
    """List all available templates, optionally filtered by category."""
    templates = list(BUILTIN_TEMPLATES.values())
    if category:
        templates = [t for t in templates if t.category == category]
    return templates


def create_project_from_template(template_name: str, output_dir: str) -> str:
    """Scaffold a new project from a template.

    Parameters
    ----------
    template_name : str
        Name of the built-in template.
    output_dir : str
        Directory where the project will be created.

    Returns
    -------
    str
        Path to the created project file.
    """
    template = get_template(template_name)
    if template is None:
        available = ", ".join(BUILTIN_TEMPLATES.keys())
        raise ValueError(
            f"Unknown template '{template_name}'. Available: {available}"
        )

    os.makedirs(output_dir, exist_ok=True)

    project_data = template.to_project_dict()
    project_file = os.path.join(output_dir, f"{template_name}.eostudio")
    with open(project_file, "w", encoding="utf-8") as f:
        json.dump(project_data, f, indent=2)

    readme_path = os.path.join(output_dir, "README.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(_generate_readme(template))

    return project_file


def _generate_readme(template: ProjectTemplate) -> str:
    """Generate a README.md for a scaffolded project."""
    frameworks = template.metadata.get("frameworks", [])
    framework_list = ", ".join(f"`{fw}`" for fw in frameworks) if frameworks else "N/A"
    difficulty = template.metadata.get("difficulty", "beginner")
    est_time = template.metadata.get("estimated_time", "unknown")

    return f"""# {template.name}

> {template.description}

## Quick Start

1. Open the project file in EoStudio:
   ```bash
   EoStudio launch --editor {template.editor_type}
   ```

2. Load the project:
   - File → Open → `{template.name}.eostudio`

3. Generate code (if applicable):
   ```bash
   EoStudio codegen {template.name}.eostudio --framework {frameworks[0] if frameworks else 'html'} -o ./output
   ```

## Template Details

| Property | Value |
|----------|-------|
| **Category** | {template.category} |
| **Editor** | {template.editor_type} |
| **Difficulty** | {difficulty} |
| **Est. Time** | {est_time} |
| **Frameworks** | {framework_list} |

## What's Included

- `{template.name}.eostudio` — Project file with pre-built design
- `README.md` — This file

## Workflow

1. **Open** the `.eostudio` project in the {template.editor_type} editor
2. **Modify** the design using the visual editor
3. **Generate** code for your target framework
4. **Export** the result and integrate into your build system

## Learn More

- [EoStudio Documentation](../../docs/getting-started.md)
- [Code Generation Guide](../../docs/codegen-guide.md)
- [Editor Guide](../../docs/editors-guide.md)
"""
