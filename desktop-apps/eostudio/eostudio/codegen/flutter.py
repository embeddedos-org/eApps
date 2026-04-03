"""Flutter / Dart code generator for EoStudio UI components."""

from __future__ import annotations

from typing import Any, Dict, List


class FlutterGenerator:
    """Generates Flutter (Dart) source files from eostudio component trees.

    Component type mapping:
    - ``Button``    → ``ElevatedButton``
    - ``Text``      → ``Text``
    - ``Heading``   → ``Text`` with headline style
    - ``Input``     → ``TextField``
    - ``TextArea``  → ``TextField(maxLines: 5)``
    - ``Image``     → ``Image.network`` / ``Image.asset``
    - ``Container`` → ``Column`` / ``Row``
    - ``Card``      → ``Card``
    - ``List``      → ``ListView``
    """

    WIDGET_MAP: Dict[str, str] = {
        "Button": "ElevatedButton",
        "Text": "Text",
        "Heading": "Text",
        "Input": "TextField",
        "TextArea": "TextField",
        "Image": "Image",
        "Container": "Column",
        "Card": "Card",
        "List": "ListView",
        "Link": "TextButton",
    }

    def generate(
        self,
        components: List[Dict[str, Any]],
        screens: List[Dict[str, Any]],
    ) -> Dict[str, str]:
        """Generate Dart source files for a Flutter project.

        Args:
            components: Flat list of component dicts.
            screens: List of screen dicts with ``name`` and ``components``.

        Returns:
            Mapping of filename → Dart source content.
        """
        files: Dict[str, str] = {}

        if not screens:
            screens = [{"name": "Home", "components": components}]

        files["lib/main.dart"] = self._generate_main(screens)

        for screen in screens:
            sname = self._dart_class(screen.get("name", "Home"))
            fname = self._snake(screen.get("name", "home"))
            screen_comps = screen.get("components", components)
            files[f"lib/screens/{fname}_screen.dart"] = self._generate_screen(
                sname, screen_comps, screens
            )

        return files

    # ------------------------------------------------------------------
    # main.dart
    # ------------------------------------------------------------------

    def _generate_main(self, screens: List[Dict[str, Any]]) -> str:
        imports = []
        routes = []
        for screen in screens:
            fname = self._snake(screen.get("name", "home"))
            cname = self._dart_class(screen.get("name", "Home"))
            imports.append(f"import 'screens/{fname}_screen.dart';")
            route_path = f"/{fname}" if fname != self._snake(screens[0].get("name", "home")) else "/"
            routes.append(f"        '{route_path}': (context) => const {cname}Screen(),")

        imports_str = "\n".join(imports)
        routes_str = "\n".join(routes)
        home = self._dart_class(screens[0].get("name", "Home"))

        return (
            "import 'package:flutter/material.dart';\n"
            f"{imports_str}\n\n"
            "void main() => runApp(const EoStudioApp());\n\n"
            "class EoStudioApp extends StatelessWidget {\n"
            "  const EoStudioApp({super.key});\n\n"
            "  @override\n"
            "  Widget build(BuildContext context) {\n"
            "    return MaterialApp(\n"
            "      title: 'EoStudio App',\n"
            "      debugShowCheckedModeBanner: false,\n"
            "      theme: ThemeData(\n"
            "        colorSchemeSeed: Colors.blue,\n"
            "        useMaterial3: true,\n"
            "      ),\n"
            f"      home: const {home}Screen(),\n"
            "      routes: {{\n"
            f"{routes_str}\n"
            "      }},\n"
            "    );\n"
            "  }\n"
            "}\n"
        )

    # ------------------------------------------------------------------
    # Screen files
    # ------------------------------------------------------------------

    def _generate_screen(
        self, class_name: str, components: List[Dict[str, Any]], all_screens: List[Dict[str, Any]]
    ) -> str:
        body = self._render_widgets(components, indent=6)
        nav_buttons = self._nav_buttons(all_screens, class_name, indent=6)

        return (
            "import 'package:flutter/material.dart';\n\n"
            f"class {class_name}Screen extends StatelessWidget {{\n"
            f"  const {class_name}Screen({{super.key}});\n\n"
            "  @override\n"
            "  Widget build(BuildContext context) {\n"
            "    return Scaffold(\n"
            f"      appBar: AppBar(title: const Text('{class_name}')),\n"
            "      body: SingleChildScrollView(\n"
            "        padding: const EdgeInsets.all(16),\n"
            "        child: Column(\n"
            "          crossAxisAlignment: CrossAxisAlignment.stretch,\n"
            "          children: [\n"
            f"{body}"
            f"{nav_buttons}"
            "          ],\n"
            "        ),\n"
            "      ),\n"
            "    );\n"
            "  }\n"
            "}\n"
        )

    def _render_widgets(self, components: List[Dict[str, Any]], indent: int) -> str:
        lines: List[str] = []
        pad = " " * indent

        for comp in components:
            ctype = comp.get("type", "Container")
            label = comp.get("label", comp.get("text", ""))
            children = comp.get("children", [])

            if ctype == "Button":
                lines.append(
                    f"{pad}ElevatedButton(\n"
                    f"{pad}  onPressed: () {{}},\n"
                    f"{pad}  child: Text('{label}'),\n"
                    f"{pad}),\n"
                )
            elif ctype in ("Text", "Heading"):
                style = "Theme.of(context).textTheme.headlineMedium" if ctype == "Heading" else "null"
                lines.append(f"{pad}Text('{label}', style: {style}),\n")
            elif ctype == "Input":
                placeholder = comp.get("placeholder", label)
                lines.append(
                    f"{pad}TextField(\n"
                    f"{pad}  decoration: InputDecoration(\n"
                    f"{pad}    labelText: '{placeholder}',\n"
                    f"{pad}    border: const OutlineInputBorder(),\n"
                    f"{pad}  ),\n"
                    f"{pad}),\n"
                )
            elif ctype == "TextArea":
                lines.append(
                    f"{pad}TextField(\n"
                    f"{pad}  maxLines: 5,\n"
                    f"{pad}  decoration: InputDecoration(\n"
                    f"{pad}    labelText: '{label}',\n"
                    f"{pad}    border: const OutlineInputBorder(),\n"
                    f"{pad}  ),\n"
                    f"{pad}),\n"
                )
            elif ctype == "Image":
                src = comp.get("src", "https://via.placeholder.com/150")
                lines.append(f"{pad}Image.network('{src}'),\n")
            elif ctype == "Card":
                child_body = self._render_widgets(children, indent + 4) if children else f"{pad}    Text('{label}'),\n"
                lines.append(
                    f"{pad}Card(\n"
                    f"{pad}  child: Padding(\n"
                    f"{pad}    padding: const EdgeInsets.all(16),\n"
                    f"{pad}    child: Column(children: [\n"
                    f"{child_body}"
                    f"{pad}    ]),\n"
                    f"{pad}  ),\n"
                    f"{pad}),\n"
                )
            elif ctype == "Container" and children:
                direction = comp.get("direction", "column")
                widget = "Row" if direction == "row" else "Column"
                child_body = self._render_widgets(children, indent + 2)
                lines.append(
                    f"{pad}{widget}(\n"
                    f"{pad}  children: [\n"
                    f"{child_body}"
                    f"{pad}  ],\n"
                    f"{pad}),\n"
                )
            else:
                lines.append(f"{pad}Text('{label}'),\n")

            lines.append(f"{pad}const SizedBox(height: 12),\n")

        return "".join(lines)

    def _nav_buttons(self, screens: List[Dict[str, Any]], current: str, indent: int) -> str:
        lines: List[str] = []
        pad = " " * indent
        for screen in screens:
            target = self._dart_class(screen.get("name", "Home"))
            if target == current:
                continue
            route = f"/{self._snake(screen.get('name', 'home'))}"
            lines.append(
                f"{pad}TextButton(\n"
                f"{pad}  onPressed: () => Navigator.pushNamed(context, '{route}'),\n"
                f"{pad}  child: Text('Go to {target}'),\n"
                f"{pad}),\n"
            )
        return "".join(lines)

    # ------------------------------------------------------------------
    # Naming helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _dart_class(name: str) -> str:
        return "".join(w.capitalize() for w in name.replace("-", " ").replace("_", " ").split())

    @staticmethod
    def _snake(name: str) -> str:
        return name.lower().replace(" ", "_").replace("-", "_")
