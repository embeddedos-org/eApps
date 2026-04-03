# EoStudio Plugin Development Guide

> Build extensions that add new tools, editors, and export formats to EoStudio.

## Architecture Overview

```
PluginManager
  ├── discover()    — Scan plugin directories for manifest.json
  ├── load()        — Import and instantiate Plugin subclass
  ├── activate()    — Call plugin.activate(), register hooks
  ├── fire_hook()   — Dispatch events to all active plugins
  └── deactivate()  — Clean up and unregister
```

## Creating a Plugin (Step-by-Step)

### 1. Create Plugin Directory

```
~/.EoStudio/plugins/my-exporter/
├── manifest.json
└── my_exporter.py
```

### 2. Write `manifest.json`

```json
{
  "id": "my-exporter",
  "name": "My Custom Exporter",
  "version": "1.0.0",
  "description": "Exports designs to custom format",
  "author": "Your Name",
  "plugin_type": "tool",
  "entry_point": "my_exporter",
  "dependencies": [],
  "min_EoStudio_version": "0.1.0",
  "config_schema": {
    "output_format": {"type": "string", "default": "json"},
    "compress": {"type": "boolean", "default": false}
  }
}
```

### 3. Implement Plugin Class

```python
from eostudio.plugins.plugin_base import Plugin, PluginManifest, PluginHook

class MyExporterPlugin(Plugin):
    manifest = PluginManifest(
        id="my-exporter",
        name="My Custom Exporter",
        version="1.0.0",
        description="Exports designs to custom format",
        entry_point="my_exporter",
    )

    def activate(self, context):
        self._hooks[PluginHook.ON_EXPORT] = self._handle_export
        self._hooks[PluginHook.POST_CODEGEN] = self._post_codegen
        return super().activate(context)

    def _handle_export(self, data):
        design = data.get("design", {})
        output_path = data.get("output_path", "output.json")
        # Custom export logic here
        return {"exported": True, "path": output_path}

    def _post_codegen(self, data):
        files = data.get("files", {})
        # Post-process generated files
        return {"processed": len(files)}

    def get_menu_items(self):
        return [
            {"label": "Export Custom Format", "action": "export_custom"},
        ]

    def get_toolbar_items(self):
        return [
            {"icon": "download", "tooltip": "Custom Export", "action": "export_custom"},
        ]
```

## Manifest Schema Reference

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | ✅ | Unique plugin identifier |
| `name` | string | ✅ | Display name |
| `version` | string | ✅ | Semantic version |
| `description` | string | | Short description |
| `author` | string | | Author name |
| `plugin_type` | string | | `"tool"`, `"editor"`, `"theme"`, `"exporter"` |
| `entry_point` | string | ✅ | Python module name |
| `dependencies` | string[] | | Other plugin IDs required |
| `min_EoStudio_version` | string | | Minimum EoStudio version |
| `config_schema` | object | | Configuration fields and defaults |

## Available Hooks

| Hook | Data Payload | When Fired |
|------|-------------|------------|
| `ON_DESIGN_CHANGE` | `{"design": dict, "editor": str}` | User modifies any design |
| `ON_EXPORT` | `{"design": dict, "format": str, "output_path": str}` | Export triggered |
| `ON_BUILD` | `{"project": dict, "target": str}` | Build/compile started |
| `ON_SIMULATE` | `{"model": dict, "params": dict}` | Simulation run started |
| `ON_SAVE` | `{"project": dict, "path": str}` | Project saved |
| `ON_LOAD` | `{"path": str}` | Project loaded |
| `PRE_CODEGEN` | `{"components": list, "framework": str}` | Before code generation |
| `POST_CODEGEN` | `{"files": dict, "framework": str}` | After code generation |
| `ON_ERROR` | `{"error": str, "context": dict}` | Error occurred |

## Installing Plugins

```python
from eostudio.plugins.plugin_base import PluginManager

manager = PluginManager()

# From local path
manager.install_from_path("/path/to/my-plugin/")

# From Git repository
manager.install_from_git("https://github.com/user/eostudio-plugin.git")

# Discover and activate
manifests = manager.discover()
for m in manifests:
    manager.load(m.id)
    manager.activate(m.id)
```

## Plugin Directories

Plugins are discovered in these directories:

1. `~/.EoStudio/plugins/` — User plugins
2. `./plugins/` — Project-local plugins

## Configuration

```python
manager.configure("my-exporter", {
    "output_format": "xml",
    "compress": True,
})

# Export/import all plugin configs
config = manager.export_config()
manager.import_config(config)
```

## Reference Plugin: EoSim

See `eostudio/plugins/eosim_plugin.py` for a complete reference implementation (~437 lines) demonstrating:

- Full hook integration (design validation, firmware build, simulation)
- Platform selection (22 boards)
- Domain simulation (14 domains)
- UI contributions (menus, toolbars, status panel)
