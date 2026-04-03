"""Code generation module for EoStudio.

Translates design components and screens into framework-specific source code
for HTML/CSS, Flutter, Jetpack Compose, React, OpenSCAD, mobile apps,
desktop apps, full-stack web apps, and database schemas.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from eostudio.codegen.database import DatabaseSchema


def generate_code(
    project_file: str,
    framework: str,
    output_dir: str,
) -> Dict[str, str]:
    """Dispatch code generation to the appropriate framework generator.

    Args:
        project_file: Path to the ``.EoStudio`` project file.
        framework: Target framework identifier. Supported values:

            **Original generators:**
            ``html``, ``flutter``, ``compose``, ``react``, ``openscad``

            **Mobile generators:**
            ``mobile-flutter``, ``mobile-react-native``,
            ``mobile-kotlin``, ``mobile-swift``

            **Desktop generators:**
            ``desktop-electron``, ``desktop-tauri``,
            ``desktop-tkinter``, ``desktop-qt``,
            ``desktop-compose-desktop``

            **Web-app generators:**
            ``webapp-react-fastapi``, ``webapp-react-flask``,
            ``webapp-vue-fastapi``, ``webapp-vue-flask``

            **Database generators:**
            ``database-sql``, ``database-sqlalchemy``,
            ``database-prisma``, ``database-django``

        output_dir: Directory where generated files will be written.

    Returns:
        A dict mapping relative filenames to their generated source content.
    """
    from eostudio.formats.project import EoStudioProject

    project = EoStudioProject.load(project_file)
    scene_data = project.scenes.get(project.active_scene, {})
    components = scene_data.get("components", scene_data.get("objects", []))
    screens = scene_data.get("screens", [])
    models = scene_data.get("models", [])
    app_name = getattr(project, "name", "MyApp") or "MyApp"
    package_name = getattr(project, "package_name", "com.example.app") or "com.example.app"

    generators = {
        # Original generators
        "html": lambda: _generate_html(components, screens),
        "flutter": lambda: _generate_flutter(components, screens),
        "compose": lambda: _generate_compose(components, screens),
        "react": lambda: _generate_react(components, screens),
        "openscad": lambda: _generate_openscad(components, screens),
        # Mobile generators
        "mobile-flutter": lambda: _generate_mobile(
            "flutter", screens, app_name, package_name
        ),
        "mobile-react-native": lambda: _generate_mobile(
            "react_native", screens, app_name, package_name
        ),
        "mobile-kotlin": lambda: _generate_mobile(
            "kotlin", screens, app_name, package_name
        ),
        "mobile-swift": lambda: _generate_mobile(
            "swift", screens, app_name, package_name
        ),
        # Desktop generators
        "desktop-electron": lambda: _generate_desktop(
            "electron", screens, app_name
        ),
        "desktop-tauri": lambda: _generate_desktop(
            "tauri", screens, app_name
        ),
        "desktop-tkinter": lambda: _generate_desktop(
            "tkinter", screens, app_name
        ),
        "desktop-qt": lambda: _generate_desktop(
            "qt", screens, app_name
        ),
        "desktop-compose-desktop": lambda: _generate_desktop(
            "compose_desktop", screens, app_name
        ),
        # Web-app generators
        "webapp-react-fastapi": lambda: _generate_webapp(
            "react", "fastapi", screens, app_name, models
        ),
        "webapp-react-flask": lambda: _generate_webapp(
            "react", "flask", screens, app_name, models
        ),
        "webapp-vue-fastapi": lambda: _generate_webapp(
            "vue", "fastapi", screens, app_name, models
        ),
        "webapp-vue-flask": lambda: _generate_webapp(
            "vue", "flask", screens, app_name, models
        ),
        # Database generators
        "database-sql": lambda: _generate_database(
            "sql", scene_data, app_name
        ),
        "database-sqlalchemy": lambda: _generate_database(
            "sqlalchemy", scene_data, app_name
        ),
        "database-prisma": lambda: _generate_database(
            "prisma", scene_data, app_name
        ),
        "database-django": lambda: _generate_database(
            "django", scene_data, app_name
        ),
        # .NET generators
        "desktop-maui": lambda: _generate_dotnet("maui", screens, app_name),
        "desktop-wpf": lambda: _generate_dotnet("wpf", screens, app_name),
        "desktop-winui": lambda: _generate_dotnet("winui", screens, app_name),
        # GTK generators
        "desktop-gtk-python": lambda: _generate_gtk("gtk-python", screens, app_name),
        "desktop-gtk-c": lambda: _generate_gtk("gtk-c", screens, app_name),
        # Game engine generators
        "game-godot": lambda: _generate_game_engine("godot", screens, app_name),
        "game-unity": lambda: _generate_game_engine("unity", screens, app_name),
        "game-unreal": lambda: _generate_game_engine("unreal", screens, app_name),
        # WASM generators
        "wasm-rust": lambda: _generate_wasm("wasm-rust", screens, app_name),
        "wasm-assemblyscript": lambda: _generate_wasm("wasm-assemblyscript", screens, app_name),
        # Firmware generators
        "firmware-eos": lambda: _generate_firmware("eos", scene_data, app_name),
        "firmware-baremetal": lambda: _generate_firmware("baremetal", scene_data, app_name),
        "firmware-freertos": lambda: _generate_firmware("freertos", scene_data, app_name),
        "firmware-zephyr": lambda: _generate_firmware("zephyr", scene_data, app_name),
        "firmware-linux": lambda: _generate_firmware("linux", scene_data, app_name),
    }

    gen_fn = generators.get(framework)
    if gen_fn is None:
        raise ValueError(
            f"Unknown framework {framework!r}. "
            f"Supported: {', '.join(sorted(generators))}"
        )

    files = gen_fn()

    import os
    os.makedirs(output_dir, exist_ok=True)
    for fname, content in files.items():
        path = os.path.join(output_dir, fname)
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(content)

    return files


# ------------------------------------------------------------------
# Original generator dispatchers
# ------------------------------------------------------------------


def _generate_html(
    components: List[Dict[str, Any]], screens: List[Dict[str, Any]]
) -> Dict[str, str]:
    from eostudio.codegen.html_css import HTMLCSSGenerator
    return HTMLCSSGenerator().generate(components, screens)


def _generate_flutter(
    components: List[Dict[str, Any]], screens: List[Dict[str, Any]]
) -> Dict[str, str]:
    from eostudio.codegen.flutter import FlutterGenerator
    return FlutterGenerator().generate(components, screens)


def _generate_compose(
    components: List[Dict[str, Any]], screens: List[Dict[str, Any]]
) -> Dict[str, str]:
    from eostudio.codegen.compose import ComposeGenerator
    return ComposeGenerator().generate(components, screens)


def _generate_react(
    components: List[Dict[str, Any]], screens: List[Dict[str, Any]]
) -> Dict[str, str]:
    from eostudio.codegen.react import ReactGenerator
    return ReactGenerator().generate(components, screens)


def _generate_openscad(
    components: List[Dict[str, Any]], screens: List[Dict[str, Any]]
) -> Dict[str, str]:
    from eostudio.codegen.openscad import OpenSCADGenerator
    code = OpenSCADGenerator().generate(components)
    return {"model.scad": code}


# ------------------------------------------------------------------
# New generator dispatchers
# ------------------------------------------------------------------


def _generate_mobile(
    target: str,
    screens: List[Dict[str, Any]],
    app_name: str,
    package_name: str,
) -> Dict[str, str]:
    from eostudio.codegen.mobile import MobileAppGenerator
    return MobileAppGenerator(target=target).generate(
        screens, app_name=app_name, package_name=package_name
    )


def _generate_desktop(
    target: str,
    screens: List[Dict[str, Any]],
    app_name: str,
) -> Dict[str, str]:
    from eostudio.codegen.desktop import DesktopAppGenerator
    return DesktopAppGenerator(target=target).generate(screens, app_name=app_name)


def _generate_webapp(
    frontend: str,
    backend: str,
    screens: List[Dict[str, Any]],
    app_name: str,
    models: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, str]:
    from eostudio.codegen.webapp import WebAppGenerator
    return WebAppGenerator(frontend=frontend, backend=backend).generate(
        screens, app_name=app_name, models=models
    )


def _generate_database(
    mode: str,
    scene_data: Dict[str, Any],
    app_name: str,
) -> Dict[str, str]:
    from eostudio.codegen.database import (
        DatabaseSchema,
        generate_sql,
        generate_sqlalchemy,
        generate_prisma,
        generate_django_models,
    )

    schema_data = scene_data.get("database_schema")
    if schema_data:
        schema = DatabaseSchema.from_dict(schema_data)
    else:
        schema = _schema_from_models(
            scene_data.get("models", []), app_name
        )

    dispatch = {
        "sql": lambda s: {"schema.sql": generate_sql(s, dialect="postgresql")},
        "sqlalchemy": lambda s: {"models.py": generate_sqlalchemy(s)},
        "prisma": lambda s: {"schema.prisma": generate_prisma(s)},
        "django": lambda s: {"models.py": generate_django_models(s)},
    }

    gen = dispatch.get(mode)
    if gen is None:
        raise ValueError(f"Unknown database mode {mode!r}.")

    return gen(schema)


def _schema_from_models(
    models: List[Dict[str, Any]], app_name: str
) -> "DatabaseSchema":
    """Build a DatabaseSchema from a simple models list.

    Each model dict is expected to have ``name`` and ``fields``, where
    each field has ``name`` and ``type``.
    """
    from eostudio.codegen.database import (
        DatabaseColumn,
        DatabaseSchema,
        DatabaseTable,
    )

    tables = []
    for model in models:
        mname = model.get("name", "item")
        snake = mname.lower().replace(" ", "_").replace("-", "_")
        columns = [
            DatabaseColumn(
                name="id",
                type_str="SERIAL",
                primary_key=True,
                nullable=False,
            )
        ]
        for f in model.get("fields", []):
            ftype = f.get("type", "str")
            type_map = {
                "str": "VARCHAR",
                "int": "INTEGER",
                "float": "FLOAT",
                "bool": "BOOLEAN",
                "date": "DATE",
                "datetime": "DATETIME",
                "text": "TEXT",
            }
            columns.append(
                DatabaseColumn(
                    name=f.get("name", "value"),
                    type_str=type_map.get(ftype, "VARCHAR"),
                    nullable=True,
                )
            )
        tables.append(DatabaseTable(name=snake, columns=columns))

    return DatabaseSchema(name=app_name, tables=tables)


# ------------------------------------------------------------------
# New codegen dispatchers (Phase 5)
# ------------------------------------------------------------------


def _generate_dotnet(
    target: str, screens: List[Dict[str, Any]], app_name: str,
) -> Dict[str, str]:
    from eostudio.codegen.dotnet import DotNetAppGenerator
    return DotNetAppGenerator(target=target).generate(screens, app_name=app_name)


def _generate_gtk(
    target: str, screens: List[Dict[str, Any]], app_name: str,
) -> Dict[str, str]:
    from eostudio.codegen.gtk import GTKAppGenerator
    return GTKAppGenerator(target=target).generate(screens, app_name=app_name)


def _generate_game_engine(
    target: str, screens: List[Dict[str, Any]], app_name: str,
) -> Dict[str, str]:
    from eostudio.codegen.game_engine import GameEngineExporter
    return GameEngineExporter(target=target).generate(screens, app_name=app_name)


def _generate_wasm(
    target: str, screens: List[Dict[str, Any]], app_name: str,
) -> Dict[str, str]:
    from eostudio.codegen.wasm import WasmGenerator
    return WasmGenerator(target=target).generate(screens, app_name=app_name)


def _generate_firmware(
    target_os: str, scene_data: Dict[str, Any], app_name: str,
) -> Dict[str, str]:
    from eostudio.codegen.hardware import FirmwareGenerator
    board_config = scene_data.get("board_config", {
        "name": app_name.lower(), "platform": "stm32f4",
        "arch": "arm-cortex-m", "clock_mhz": 168,
        "memory": [], "peripherals": [],
    })
    gen = FirmwareGenerator(board_config, target_os=target_os)
    return gen.generate(app_name=app_name)
