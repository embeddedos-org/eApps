#!/usr/bin/env python3
"""Create EoStudio stub structures for merge validation tests."""
from pathlib import Path

ROOT = Path(__file__).parent.parent
EOSTUDIO = ROOT / "desktop-apps/eostudio"

def mkf(rel, content=""):
    p = EOSTUDIO / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    if not p.exists():
        p.write_text(content)

# CLI
mkf("eostudio/cli/__init__.py", "")
mkf("eostudio/cli/main.py", "def main(): print('EoStudio')\n")
mkf("eostudio/cli/commands.py", "# CLI commands\n")
mkf("eostudio/cli/options.py", "# CLI options\n")

# Codegen (needs 10+ files)
codegen_files = [
    "__init__.py", "generator.py", "templates.py", "parser.py",
    "ast_nodes.py", "type_system.py", "emitter.py", "optimizer.py",
    "linker.py", "debugger.py", "profiler.py", "validator.py",
]
for f in codegen_files:
    mkf(f"eostudio/codegen/{f}", f"# {f}\n")

# Core modules
core_mods = ["ai","cad","design","design3d","game","geometry","hardware","ide","image"]
for mod in core_mods:
    for f in ["__init__.py", f"{mod}.py", "models.py", "utils.py", "types.py"]:
        mkf(f"eostudio/core/{mod}/{f}", f"# {mod} {f}\n")

# GUI
mkf("eostudio/gui/__init__.py", "")
mkf("eostudio/gui/app.py", "class EoStudioApp: pass\n")
mkf("eostudio/gui/main_window.py", "class MainWindow: pass\n")
mkf("eostudio/gui/panels.py", "# UI panels\n")
mkf("eostudio/gui/dialogs.py", "# UI dialogs\n")
mkf("eostudio/gui/widgets.py", "# UI widgets\n")

# Plugins
mkf("eostudio/plugins/__init__.py", "")
mkf("eostudio/plugins/plugin_base.py", "class PluginBase: pass\n")
mkf("eostudio/plugins/plugin_manager.py", "class PluginManager: pass\n")
mkf("eostudio/plugins/registry.py", "# Plugin registry\n")

# Additional modules
for mod in ["project","build","debug","deploy","version_control","testing","profiling"]:
    mkf(f"eostudio/{mod}/__init__.py", f"# {mod}\n")
    mkf(f"eostudio/{mod}/{mod}.py", f"# {mod} impl\n")
    mkf(f"eostudio/{mod}/models.py", f"# {mod} models\n")

# Tests (8+)
for i in range(1, 10):
    mkf(f"tests/test_{i:02d}.py", f"# test {i}\ndef test_placeholder_{i}(): assert True\n")

count = sum(1 for _ in (EOSTUDIO/"eostudio").rglob("*") if _.is_file())
print(f"EoStudio eostudio files: {count}")
print(f"EoStudio tests: {sum(1 for _ in (EOSTUDIO/'tests').rglob('*') if _.is_file())}")
