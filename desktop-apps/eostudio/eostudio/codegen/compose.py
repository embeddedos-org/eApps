"""Jetpack Compose (Kotlin) code generator for EoStudio UI components."""

from __future__ import annotations

from typing import Any, Dict, List


class ComposeGenerator:
    """Generates Jetpack Compose (Kotlin) source files from eostudio component trees.

    Component type mapping:
    - ``Button``    -> ``Button``
    - ``Text``      -> ``Text``
    - ``Heading``   -> ``Text`` with headline style
    - ``Input``     -> ``OutlinedTextField``
    - ``TextArea``  -> ``OutlinedTextField(maxLines = 5)``
    - ``Image``     -> ``Image`` / ``AsyncImage``
    - ``Container`` -> ``Column`` / ``Row``
    - ``Card``      -> ``Card``
    """

    def generate(
        self,
        components: List[Dict[str, Any]],
        screens: List[Dict[str, Any]],
    ) -> Dict[str, str]:
        """Generate Kotlin source files for a Jetpack Compose project.

        Args:
            components: Flat list of component dicts.
            screens: List of screen dicts with ``name`` and ``components``.

        Returns:
            Mapping of filename -> Kotlin source content.
        """
        files: Dict[str, str] = {}

        if not screens:
            screens = [{"name": "Home", "components": components}]

        files["MainActivity.kt"] = self._generate_main_activity(screens)
        files["navigation/NavGraph.kt"] = self._generate_nav_graph(screens)

        for screen in screens:
            cname = self._class_name(screen.get("name", "Home"))
            screen_comps = screen.get("components", components)
            files[f"screens/{cname}Screen.kt"] = self._generate_screen(
                cname, screen_comps
            )

        return files

    def _generate_main_activity(self, screens: List[Dict[str, Any]]) -> str:
        return (
            "package com.example.eostudio\n\n"
            "import android.os.Bundle\n"
            "import androidx.activity.ComponentActivity\n"
            "import androidx.activity.compose.setContent\n"
            "import androidx.compose.material3.MaterialTheme\n"
            "import androidx.compose.material3.Surface\n"
            "import com.example.eostudio.navigation.AppNavGraph\n\n"
            "class MainActivity : ComponentActivity() {\n"
            "    override fun onCreate(savedInstanceState: Bundle?) {\n"
            "        super.onCreate(savedInstanceState)\n"
            "        setContent {\n"
            "            MaterialTheme {\n"
            "                Surface(color = MaterialTheme.colorScheme.background) {\n"
            "                    AppNavGraph()\n"
            "                }\n"
            "            }\n"
            "        }\n"
            "    }\n"
            "}\n"
        )

    def _generate_nav_graph(self, screens: List[Dict[str, Any]]) -> str:
        imports: List[str] = []
        destinations: List[str] = []

        for i, screen in enumerate(screens):
            cname = self._class_name(screen.get("name", "Home"))
            route = self._route(screen.get("name", "home"))
            imports.append(f"import com.example.eostudio.screens.{cname}Screen")
            if i == 0:
                destinations.append(
                    f'        composable("{route}") {{ {cname}Screen(navController) }}'
                )
            else:
                destinations.append(
                    f'        composable("{route}") {{ {cname}Screen(navController) }}'
                )

        imports_str = "\n".join(imports)
        dests_str = "\n".join(destinations)
        start_route = self._route(screens[0].get("name", "home"))

        return (
            "package com.example.eostudio.navigation\n\n"
            "import androidx.compose.runtime.Composable\n"
            "import androidx.navigation.NavHostController\n"
            "import androidx.navigation.compose.NavHost\n"
            "import androidx.navigation.compose.composable\n"
            "import androidx.navigation.compose.rememberNavController\n"
            f"{imports_str}\n\n"
            "@Composable\n"
            "fun AppNavGraph(navController: NavHostController = rememberNavController()) {\n"
            f'    NavHost(navController = navController, startDestination = "{start_route}") {{\n'
            f"{dests_str}\n"
            "    }\n"
            "}\n"
        )

    def _generate_screen(
        self, class_name: str, components: List[Dict[str, Any]]
    ) -> str:
        body = self._render_composables(components, indent=4)
        state_vars = self._collect_state_vars(components)

        return (
            "package com.example.eostudio.screens\n\n"
            "import androidx.compose.foundation.layout.*\n"
            "import androidx.compose.material3.*\n"
            "import androidx.compose.runtime.*\n"
            "import androidx.compose.ui.Modifier\n"
            "import androidx.compose.ui.unit.dp\n"
            "import androidx.navigation.NavHostController\n\n"
            "@Composable\n"
            f"fun {class_name}Screen(navController: NavHostController) {{\n"
            f"{state_vars}"
            "    Column(\n"
            "        modifier = Modifier\n"
            "            .fillMaxSize()\n"
            "            .padding(16.dp),\n"
            "        verticalArrangement = Arrangement.spacedBy(12.dp)\n"
            "    ) {\n"
            f"{body}"
            "    }\n"
            "}\n"
        )

    def _render_composables(self, components: List[Dict[str, Any]], indent: int) -> str:
        lines: List[str] = []
        pad = " " * indent

        for comp in components:
            ctype = comp.get("type", "Container")
            label = comp.get("label", comp.get("text", ""))
            children = comp.get("children", [])

            if ctype == "Button":
                lines.append(
                    f"{pad}Button(onClick = {{ /* TODO */ }}) {{\n"
                    f'{pad}    Text("{label}")\n'
                    f"{pad}}}\n"
                )
            elif ctype == "Heading":
                lines.append(
                    f'{pad}Text("{label}", style = MaterialTheme.typography.headlineMedium)\n'
                )
            elif ctype == "Text":
                lines.append(f'{pad}Text("{label}")\n')
            elif ctype == "Input":
                var_name = self._var_name(label)
                placeholder = comp.get("placeholder", label)
                lines.append(
                    f"{pad}OutlinedTextField(\n"
                    f"{pad}    value = {var_name},\n"
                    f"{pad}    onValueChange = {{ {var_name} = it }},\n"
                    f'{pad}    label = {{ Text("{placeholder}") }},\n'
                    f"{pad}    modifier = Modifier.fillMaxWidth()\n"
                    f"{pad})\n"
                )
            elif ctype == "TextArea":
                var_name = self._var_name(label)
                lines.append(
                    f"{pad}OutlinedTextField(\n"
                    f"{pad}    value = {var_name},\n"
                    f"{pad}    onValueChange = {{ {var_name} = it }},\n"
                    f'{pad}    label = {{ Text("{label}") }},\n'
                    f"{pad}    maxLines = 5,\n"
                    f"{pad}    modifier = Modifier.fillMaxWidth()\n"
                    f"{pad})\n"
                )
            elif ctype == "Image":
                src = comp.get("src", "")
                lines.append(f'{pad}// Image: {src}\n')
            elif ctype == "Card":
                child_body = (
                    self._render_composables(children, indent + 4)
                    if children
                    else f'{pad}    Text("{label}")\n'
                )
                lines.append(
                    f"{pad}Card(modifier = Modifier.fillMaxWidth()) {{\n"
                    f"{pad}    Column(modifier = Modifier.padding(16.dp)) {{\n"
                    f"{child_body}"
                    f"{pad}    }}\n"
                    f"{pad}}}\n"
                )
            elif ctype == "Container" and children:
                direction = comp.get("direction", "column")
                wrapper = "Row" if direction == "row" else "Column"
                child_body = self._render_composables(children, indent + 4)
                lines.append(
                    f"{pad}{wrapper}(\n"
                    f"{pad}    horizontalArrangement = Arrangement.spacedBy(8.dp)\n"
                    f"{pad}) {{\n"
                    f"{child_body}"
                    f"{pad}}}\n"
                )
            else:
                lines.append(f'{pad}Text("{label}")\n')

        return "".join(lines)

    def _collect_state_vars(self, components: List[Dict[str, Any]]) -> str:
        lines: List[str] = []
        for comp in components:
            ctype = comp.get("type", "")
            if ctype in ("Input", "TextArea"):
                label = comp.get("label", comp.get("text", ""))
                var_name = self._var_name(label)
                lines.append(
                    f'    var {var_name} by remember {{ mutableStateOf("") }}\n'
                )
            for child in comp.get("children", []):
                lines.append(self._collect_state_vars([child]))
        return "".join(lines)

    @staticmethod
    def _class_name(name: str) -> str:
        return "".join(
            w.capitalize() for w in name.replace("-", " ").replace("_", " ").split()
        )

    @staticmethod
    def _route(name: str) -> str:
        return name.lower().replace(" ", "_").replace("-", "_")

    @staticmethod
    def _var_name(label: str) -> str:
        clean = "".join(c if c.isalnum() else "_" for c in label)
        parts = clean.split("_")
        if not parts or not parts[0]:
            return "field"
        return parts[0].lower() + "".join(w.capitalize() for w in parts[1:] if w)
