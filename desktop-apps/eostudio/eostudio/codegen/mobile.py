"""Mobile application code generator for EoStudio.

Generates mobile app source code from UI screen definitions
for Flutter, React Native, Kotlin (Android), and Swift (iOS).
"""

from __future__ import annotations

from typing import Any, Dict, List


class MobileAppGenerator:
    """Generates mobile application source files from eostudio screens.

    Supported targets:
    - ``flutter``: Dart / Flutter with MaterialApp + GoRouter
    - ``react_native``: TypeScript / React Native with @react-navigation
    - ``kotlin``: Kotlin / Android with Jetpack ViewModel + XML layouts
    - ``swift``: Swift / SwiftUI with MVVM pattern
    """

    SUPPORTED_TARGETS = ("flutter", "react_native", "kotlin", "swift")

    COMPONENT_MAP: Dict[str, Dict[str, str]] = {
        "flutter": {
            "Button": "ElevatedButton",
            "Text": "Text",
            "Heading": "Text",
            "Input": "TextField",
            "TextArea": "TextField",
            "Image": "Image.network",
            "Container": "Column",
            "Card": "Card",
            "List": "ListView",
            "Link": "TextButton",
            "Switch": "Switch",
            "Checkbox": "Checkbox",
            "Slider": "Slider",
            "Dropdown": "DropdownButton",
        },
        "react_native": {
            "Button": "TouchableOpacity",
            "Text": "Text",
            "Heading": "Text",
            "Input": "TextInput",
            "TextArea": "TextInput",
            "Image": "Image",
            "Container": "View",
            "Card": "View",
            "List": "FlatList",
            "Link": "TouchableOpacity",
            "Switch": "Switch",
            "Checkbox": "Switch",
            "Slider": "Slider",
            "Dropdown": "Picker",
        },
        "kotlin": {
            "Button": "Button",
            "Text": "TextView",
            "Heading": "TextView",
            "Input": "EditText",
            "TextArea": "EditText",
            "Image": "ImageView",
            "Container": "LinearLayout",
            "Card": "CardView",
            "List": "RecyclerView",
            "Link": "TextView",
            "Switch": "Switch",
            "Checkbox": "CheckBox",
            "Slider": "SeekBar",
            "Dropdown": "Spinner",
        },
        "swift": {
            "Button": "Button",
            "Text": "Text",
            "Heading": "Text",
            "Input": "TextField",
            "TextArea": "TextEditor",
            "Image": "AsyncImage",
            "Container": "VStack",
            "Card": "GroupBox",
            "List": "List",
            "Link": "Link",
            "Switch": "Toggle",
            "Checkbox": "Toggle",
            "Slider": "Slider",
            "Dropdown": "Picker",
        },
    }

    def __init__(self, target: str = "flutter") -> None:
        if target not in self.SUPPORTED_TARGETS:
            raise ValueError(
                f"Unsupported target {target!r}. "
                f"Supported: {', '.join(self.SUPPORTED_TARGETS)}"
            )
        self.target = target

    def generate(
        self,
        screens: List[Dict[str, Any]],
        app_name: str = "MyApp",
        package_name: str = "com.example.app",
    ) -> Dict[str, str]:
        """Generate mobile app source files.

        Args:
            screens: List of screen dicts with ``name`` and ``components``.
            app_name: Application display name.
            package_name: Java/Kotlin/Swift bundle identifier.

        Returns:
            Mapping of relative filename to source content.
        """
        if not screens:
            screens = [{"name": "Home", "components": []}]

        dispatch = {
            "flutter": self._gen_flutter,
            "react_native": self._gen_react_native,
            "kotlin": self._gen_kotlin,
            "swift": self._gen_swift,
        }
        return dispatch[self.target](screens, app_name, package_name)

    def _map_component(self, component: Dict[str, Any], target: str) -> str:
        """Map an EoStudio UIComponent type to a target-framework widget name."""
        ctype = component.get("type", "Container")
        mapping = self.COMPONENT_MAP.get(target, {})
        return mapping.get(ctype, ctype)

    # ------------------------------------------------------------------
    # Flutter
    # ------------------------------------------------------------------

    def _gen_flutter(
        self,
        screens: List[Dict[str, Any]],
        app_name: str,
        package_name: str,
    ) -> Dict[str, str]:
        files: Dict[str, str] = {}
        snake_app = self._snake(app_name)

        route_entries: List[str] = []
        import_lines: List[str] = []
        for screen in screens:
            sname = self._pascal(screen.get("name", "Home"))
            fname = self._snake(screen.get("name", "home"))
            import_lines.append(
                f"import 'screens/{fname}_screen.dart';"
            )
            path = "/" if screen is screens[0] else f"/{fname}"
            route_entries.append(
                f"      GoRoute(\n"
                f"        path: '{path}',\n"
                f"        builder: (context, state) => const {sname}Screen(),\n"
                f"      ),"
            )

        imports_str = "\n".join(import_lines)
        routes_str = "\n".join(route_entries)

        files["lib/main.dart"] = (
            "import 'package:flutter/material.dart';\n"
            "import 'package:go_router/go_router.dart';\n"
            f"{imports_str}\n\n"
            "void main() => runApp(const MyApp());\n\n"
            "class MyApp extends StatelessWidget {\n"
            "  const MyApp({super.key});\n\n"
            "  @override\n"
            "  Widget build(BuildContext context) {\n"
            "    final router = GoRouter(\n"
            "      routes: [\n"
            f"{routes_str}\n"
            "      ],\n"
            "    );\n\n"
            "    return MaterialApp.router(\n"
            f"      title: '{app_name}',\n"
            "      debugShowCheckedModeBanner: false,\n"
            "      theme: ThemeData(\n"
            "        colorSchemeSeed: Colors.blue,\n"
            "        useMaterial3: true,\n"
            "      ),\n"
            "      routerConfig: router,\n"
            "    );\n"
            "  }\n"
            "}\n"
        )

        deps: List[str] = [
            "  flutter:\n    sdk: flutter\n",
            "  go_router: ^14.0.0\n",
        ]
        files["pubspec.yaml"] = (
            f"name: {snake_app}\n"
            f"description: {app_name} — generated by EoStudio\n"
            "version: 1.0.0\n\n"
            "environment:\n"
            "  sdk: '>=3.2.0 <4.0.0'\n\n"
            "dependencies:\n"
            + "".join(deps)
            + "\ndev_dependencies:\n"
            "  flutter_test:\n    sdk: flutter\n"
            "  flutter_lints: ^4.0.0\n\n"
            "flutter:\n  uses-material-design: true\n"
        )

        for screen in screens:
            sname = self._pascal(screen.get("name", "Home"))
            fname = self._snake(screen.get("name", "home"))
            comps = screen.get("components", [])
            body = self._flutter_widgets(comps, indent=12)
            files[f"lib/screens/{fname}_screen.dart"] = (
                "import 'package:flutter/material.dart';\n\n"
                f"class {sname}Screen extends StatelessWidget {{\n"
                f"  const {sname}Screen({{super.key}});\n\n"
                "  @override\n"
                "  Widget build(BuildContext context) {\n"
                "    return Scaffold(\n"
                f"      appBar: AppBar(title: const Text('{sname}')),\n"
                "      body: SingleChildScrollView(\n"
                "        padding: const EdgeInsets.all(16),\n"
                "        child: Column(\n"
                "          crossAxisAlignment: CrossAxisAlignment.stretch,\n"
                "          children: [\n"
                f"{body}"
                "          ],\n"
                "        ),\n"
                "      ),\n"
                "    );\n"
                "  }\n"
                "}\n"
            )

        return files

    def _flutter_widgets(
        self, components: List[Dict[str, Any]], indent: int
    ) -> str:
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
            elif ctype == "Heading":
                lines.append(
                    f"{pad}Text('{label}', "
                    f"style: Theme.of(context).textTheme.headlineMedium),\n"
                )
            elif ctype == "Text":
                lines.append(f"{pad}Text('{label}'),\n")
            elif ctype == "Input":
                ph = comp.get("placeholder", label)
                lines.append(
                    f"{pad}TextField(\n"
                    f"{pad}  decoration: InputDecoration(\n"
                    f"{pad}    labelText: '{ph}',\n"
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
                child_body = (
                    self._flutter_widgets(children, indent + 4)
                    if children
                    else f"{pad}    Text('{label}'),\n"
                )
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
                child_body = self._flutter_widgets(children, indent + 2)
                lines.append(
                    f"{pad}{widget}(\n"
                    f"{pad}  children: [\n"
                    f"{child_body}"
                    f"{pad}  ],\n"
                    f"{pad}),\n"
                )
            elif ctype == "Switch":
                lines.append(
                    f"{pad}Switch(value: false, onChanged: (v) {{}}),\n"
                )
            else:
                lines.append(f"{pad}Text('{label}'),\n")

            lines.append(f"{pad}const SizedBox(height: 12),\n")
        return "".join(lines)

    # ------------------------------------------------------------------
    # React Native
    # ------------------------------------------------------------------

    def _gen_react_native(
        self,
        screens: List[Dict[str, Any]],
        app_name: str,
        package_name: str,
    ) -> Dict[str, str]:
        files: Dict[str, str] = {}

        screen_imports: List[str] = []
        stack_screens: List[str] = []
        for screen in screens:
            sname = self._pascal(screen.get("name", "Home"))
            screen_imports.append(
                f"import {{ {sname}Screen }} from './screens/{sname}Screen';"
            )
            stack_screens.append(
                f'        <Stack.Screen name="{sname}" '
                f'component={{{sname}Screen}} />'
            )

        files["App.tsx"] = (
            "import React from 'react';\n"
            "import { NavigationContainer } from '@react-navigation/native';\n"
            "import { createNativeStackNavigator } from "
            "'@react-navigation/native-stack';\n"
            + "\n".join(screen_imports)
            + "\n\n"
            "const Stack = createNativeStackNavigator();\n\n"
            f"export default function App() {{\n"
            "  return (\n"
            "    <NavigationContainer>\n"
            f'      <Stack.Navigator initialRouteName="{self._pascal(screens[0].get("name", "Home"))}">\n'
            + "\n".join(stack_screens)
            + "\n"
            "      </Stack.Navigator>\n"
            "    </NavigationContainer>\n"
            "  );\n"
            "}\n"
        )

        files["package.json"] = (
            "{\n"
            f'  "name": "{self._snake(app_name)}",\n'
            '  "version": "1.0.0",\n'
            '  "main": "index.js",\n'
            '  "scripts": {\n'
            '    "start": "expo start",\n'
            '    "android": "expo start --android",\n'
            '    "ios": "expo start --ios"\n'
            "  },\n"
            '  "dependencies": {\n'
            '    "react": "18.2.0",\n'
            '    "react-native": "0.74.0",\n'
            '    "@react-navigation/native": "^6.1.0",\n'
            '    "@react-navigation/native-stack": "^6.9.0",\n'
            '    "react-native-screens": "^3.30.0",\n'
            '    "react-native-safe-area-context": "^4.9.0"\n'
            "  },\n"
            '  "devDependencies": {\n'
            '    "@types/react": "^18.2.0",\n'
            '    "typescript": "^5.3.0"\n'
            "  }\n"
            "}\n"
        )

        for screen in screens:
            sname = self._pascal(screen.get("name", "Home"))
            comps = screen.get("components", [])
            body = self._rn_components(comps, indent=8)
            other_screens = [
                s for s in screens if s.get("name") != screen.get("name")
            ]
            nav_buttons = ""
            for other in other_screens:
                oname = self._pascal(other.get("name", ""))
                nav_buttons += (
                    f"        <TouchableOpacity\n"
                    f"          style={{styles.navButton}}\n"
                    f"          onPress={{() => navigation.navigate('{oname}')}}\n"
                    f"        >\n"
                    f"          <Text style={{styles.navText}}>Go to {oname}</Text>\n"
                    f"        </TouchableOpacity>\n"
                )

            files[f"screens/{sname}Screen.tsx"] = (
                "import React, { useState } from 'react';\n"
                "import {\n"
                "  View,\n"
                "  Text,\n"
                "  TextInput,\n"
                "  TouchableOpacity,\n"
                "  ScrollView,\n"
                "  StyleSheet,\n"
                "  Image,\n"
                "  Switch,\n"
                "} from 'react-native';\n"
                "import type { NativeStackScreenProps } from "
                "'@react-navigation/native-stack';\n\n"
                "type Props = NativeStackScreenProps<any>;\n\n"
                f"export function {sname}Screen({{ navigation }}: Props) {{\n"
                "  return (\n"
                "    <ScrollView style={styles.container}>\n"
                f"{body}"
                f"{nav_buttons}"
                "    </ScrollView>\n"
                "  );\n"
                "}\n\n"
                "const styles = StyleSheet.create({\n"
                "  container: { flex: 1, padding: 16, backgroundColor: '#fff' },\n"
                "  text: { fontSize: 16, marginBottom: 8 },\n"
                "  heading: { fontSize: 24, fontWeight: 'bold', marginBottom: 12 },\n"
                "  input: {\n"
                "    borderWidth: 1,\n"
                "    borderColor: '#ccc',\n"
                "    borderRadius: 8,\n"
                "    padding: 12,\n"
                "    marginBottom: 12,\n"
                "    fontSize: 16,\n"
                "  },\n"
                "  button: {\n"
                "    backgroundColor: '#2196F3',\n"
                "    padding: 14,\n"
                "    borderRadius: 8,\n"
                "    alignItems: 'center',\n"
                "    marginBottom: 12,\n"
                "  },\n"
                "  buttonText: { color: '#fff', fontSize: 16, fontWeight: '600' },\n"
                "  card: {\n"
                "    backgroundColor: '#f5f5f5',\n"
                "    borderRadius: 12,\n"
                "    padding: 16,\n"
                "    marginBottom: 12,\n"
                "    elevation: 2,\n"
                "  },\n"
                "  navButton: {\n"
                "    padding: 12,\n"
                "    alignItems: 'center',\n"
                "    marginBottom: 8,\n"
                "  },\n"
                "  navText: { color: '#2196F3', fontSize: 16 },\n"
                "  image: { width: '100%', height: 200, borderRadius: 8, marginBottom: 12 },\n"
                "});\n"
            )

        return files

    def _rn_components(
        self, components: List[Dict[str, Any]], indent: int
    ) -> str:
        lines: List[str] = []
        pad = " " * indent
        for comp in components:
            ctype = comp.get("type", "Container")
            label = comp.get("label", comp.get("text", ""))
            children = comp.get("children", [])

            if ctype == "Button":
                lines.append(
                    f"{pad}<TouchableOpacity style={{styles.button}} "
                    f"onPress={{() => {{}}}}>\n"
                    f"{pad}  <Text style={{styles.buttonText}}>{label}</Text>\n"
                    f"{pad}</TouchableOpacity>\n"
                )
            elif ctype == "Heading":
                lines.append(
                    f"{pad}<Text style={{styles.heading}}>{label}</Text>\n"
                )
            elif ctype == "Text":
                lines.append(
                    f"{pad}<Text style={{styles.text}}>{label}</Text>\n"
                )
            elif ctype in ("Input", "TextArea"):
                ph = comp.get("placeholder", label)
                multi = (
                    " multiline numberOfLines={5}" if ctype == "TextArea" else ""
                )
                lines.append(
                    f'{pad}<TextInput style={{styles.input}} '
                    f'placeholder="{ph}"{multi} />\n'
                )
            elif ctype == "Image":
                src = comp.get("src", "https://via.placeholder.com/150")
                lines.append(
                    f"{pad}<Image style={{styles.image}} "
                    f"source={{{{ uri: '{src}' }}}} />\n"
                )
            elif ctype == "Card":
                child_body = (
                    self._rn_components(children, indent + 2)
                    if children
                    else f"{pad}  <Text>{label}</Text>\n"
                )
                lines.append(
                    f"{pad}<View style={{styles.card}}>\n"
                    f"{child_body}"
                    f"{pad}</View>\n"
                )
            elif ctype == "Switch":
                lines.append(
                    f"{pad}<Switch value={{false}} onValueChange={{() => {{}}}} />\n"
                )
            elif ctype == "Container" and children:
                child_body = self._rn_components(children, indent + 2)
                lines.append(
                    f"{pad}<View>\n{child_body}{pad}</View>\n"
                )
            else:
                lines.append(
                    f"{pad}<Text style={{styles.text}}>{label}</Text>\n"
                )
        return "".join(lines)

    # ------------------------------------------------------------------
    # Kotlin (Android)
    # ------------------------------------------------------------------

    def _gen_kotlin(
        self,
        screens: List[Dict[str, Any]],
        app_name: str,
        package_name: str,
    ) -> Dict[str, str]:
        files: Dict[str, str] = {}
        pkg_path = package_name.replace(".", "/")

        nav_cases: List[str] = []
        for i, screen in enumerate(screens):
            sname = self._pascal(screen.get("name", "Home"))
            fname = self._snake(screen.get("name", "home"))
            nav_cases.append(
                f'            "{fname}" -> {{\n'
                f"                supportFragmentManager.beginTransaction()\n"
                f"                    .replace(R.id.container, {sname}Fragment())\n"
                f"                    .addToBackStack(null)\n"
                f"                    .commit()\n"
                f"            }}"
            )

        first_screen = self._pascal(screens[0].get("name", "Home"))
        nav_body = "\n".join(nav_cases)

        files[f"app/src/main/java/{pkg_path}/MainActivity.kt"] = (
            f"package {package_name}\n\n"
            "import android.os.Bundle\n"
            "import androidx.appcompat.app.AppCompatActivity\n\n"
            "class MainActivity : AppCompatActivity() {\n\n"
            "    override fun onCreate(savedInstanceState: Bundle?) {\n"
            "        super.onCreate(savedInstanceState)\n"
            "        setContentView(R.layout.activity_main)\n\n"
            "        if (savedInstanceState == null) {\n"
            "            supportFragmentManager.beginTransaction()\n"
            f"                .replace(R.id.container, {first_screen}Fragment())\n"
            "                .commit()\n"
            "        }\n"
            "    }\n\n"
            "    fun navigateTo(screen: String) {\n"
            "        when (screen) {\n"
            f"{nav_body}\n"
            "        }\n"
            "    }\n"
            "}\n"
        )

        files["app/src/main/res/layout/activity_main.xml"] = (
            '<?xml version="1.0" encoding="utf-8"?>\n'
            "<FrameLayout\n"
            '    xmlns:android="http://schemas.android.com/apk/res/android"\n'
            '    android:id="@+id/container"\n'
            '    android:layout_width="match_parent"\n'
            '    android:layout_height="match_parent" />\n'
        )

        for screen in screens:
            sname = self._pascal(screen.get("name", "Home"))
            fname = self._snake(screen.get("name", "home"))
            comps = screen.get("components", [])

            xml_widgets = self._kotlin_xml_widgets(comps, indent=8)
            files[f"app/src/main/res/layout/fragment_{fname}.xml"] = (
                '<?xml version="1.0" encoding="utf-8"?>\n'
                "<ScrollView\n"
                '    xmlns:android="http://schemas.android.com/apk/res/android"\n'
                '    android:layout_width="match_parent"\n'
                '    android:layout_height="match_parent">\n\n'
                "    <LinearLayout\n"
                '        android:layout_width="match_parent"\n'
                '        android:layout_height="wrap_content"\n'
                '        android:orientation="vertical"\n'
                '        android:padding="16dp">\n\n'
                f"{xml_widgets}"
                "    </LinearLayout>\n"
                "</ScrollView>\n"
            )

            files[f"app/src/main/java/{pkg_path}/{sname}Fragment.kt"] = (
                f"package {package_name}\n\n"
                "import android.os.Bundle\n"
                "import android.view.LayoutInflater\n"
                "import android.view.View\n"
                "import android.view.ViewGroup\n"
                "import androidx.fragment.app.Fragment\n"
                "import androidx.fragment.app.viewModels\n\n"
                f"class {sname}Fragment : Fragment() {{\n\n"
                f"    private val viewModel: {sname}ViewModel by viewModels()\n\n"
                "    override fun onCreateView(\n"
                "        inflater: LayoutInflater,\n"
                "        container: ViewGroup?,\n"
                "        savedInstanceState: Bundle?,\n"
                "    ): View? {\n"
                f"        return inflater.inflate(R.layout.fragment_{fname}, container, false)\n"
                "    }\n\n"
                "    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {\n"
                "        super.onViewCreated(view, savedInstanceState)\n"
                "        viewModel.state.observe(viewLifecycleOwner) { state ->\n"
                "            // Update UI from ViewModel state\n"
                "        }\n"
                "    }\n"
                "}\n"
            )

            files[f"app/src/main/java/{pkg_path}/{sname}ViewModel.kt"] = (
                f"package {package_name}\n\n"
                "import androidx.lifecycle.LiveData\n"
                "import androidx.lifecycle.MutableLiveData\n"
                "import androidx.lifecycle.ViewModel\n\n"
                f"class {sname}ViewModel : ViewModel() {{\n\n"
                f"    data class UiState(\n"
                f"        val title: String = \"{sname}\",\n"
                f"        val isLoading: Boolean = false,\n"
                f"    )\n\n"
                f"    private val _state = MutableLiveData(UiState())\n"
                f"    val state: LiveData<UiState> = _state\n\n"
                f"    fun updateTitle(title: String) {{\n"
                f"        _state.value = _state.value?.copy(title = title)\n"
                f"    }}\n"
                "}\n"
            )

        return files

    def _kotlin_xml_widgets(
        self, components: List[Dict[str, Any]], indent: int
    ) -> str:
        lines: List[str] = []
        pad = " " * indent
        for comp in components:
            ctype = comp.get("type", "Container")
            label = comp.get("label", comp.get("text", ""))
            children = comp.get("children", [])

            if ctype == "Button":
                lines.append(
                    f'{pad}<Button\n'
                    f'{pad}    android:layout_width="match_parent"\n'
                    f'{pad}    android:layout_height="wrap_content"\n'
                    f'{pad}    android:text="{label}"\n'
                    f'{pad}    android:layout_marginBottom="12dp" />\n\n'
                )
            elif ctype == "Heading":
                lines.append(
                    f'{pad}<TextView\n'
                    f'{pad}    android:layout_width="match_parent"\n'
                    f'{pad}    android:layout_height="wrap_content"\n'
                    f'{pad}    android:text="{label}"\n'
                    f'{pad}    android:textSize="24sp"\n'
                    f'{pad}    android:textStyle="bold"\n'
                    f'{pad}    android:layout_marginBottom="12dp" />\n\n'
                )
            elif ctype == "Text":
                lines.append(
                    f'{pad}<TextView\n'
                    f'{pad}    android:layout_width="match_parent"\n'
                    f'{pad}    android:layout_height="wrap_content"\n'
                    f'{pad}    android:text="{label}"\n'
                    f'{pad}    android:layout_marginBottom="8dp" />\n\n'
                )
            elif ctype in ("Input", "TextArea"):
                input_type = (
                    'android:inputType="textMultiLine"\n'
                    f'{pad}    android:minLines="5"'
                    if ctype == "TextArea"
                    else 'android:inputType="text"'
                )
                lines.append(
                    f'{pad}<EditText\n'
                    f'{pad}    android:layout_width="match_parent"\n'
                    f'{pad}    android:layout_height="wrap_content"\n'
                    f'{pad}    android:hint="{label}"\n'
                    f'{pad}    {input_type}\n'
                    f'{pad}    android:layout_marginBottom="12dp" />\n\n'
                )
            elif ctype == "Image":
                lines.append(
                    f'{pad}<ImageView\n'
                    f'{pad}    android:layout_width="match_parent"\n'
                    f'{pad}    android:layout_height="200dp"\n'
                    f'{pad}    android:scaleType="centerCrop"\n'
                    f'{pad}    android:layout_marginBottom="12dp" />\n\n'
                )
            elif ctype == "Card" or (ctype == "Container" and children):
                child_body = self._kotlin_xml_widgets(children, indent + 4)
                lines.append(
                    f'{pad}<LinearLayout\n'
                    f'{pad}    android:layout_width="match_parent"\n'
                    f'{pad}    android:layout_height="wrap_content"\n'
                    f'{pad}    android:orientation="vertical"\n'
                    f'{pad}    android:padding="12dp"\n'
                    f'{pad}    android:layout_marginBottom="12dp">\n\n'
                    f'{child_body}'
                    f'{pad}</LinearLayout>\n\n'
                )
            else:
                lines.append(
                    f'{pad}<TextView\n'
                    f'{pad}    android:layout_width="match_parent"\n'
                    f'{pad}    android:layout_height="wrap_content"\n'
                    f'{pad}    android:text="{label}"\n'
                    f'{pad}    android:layout_marginBottom="8dp" />\n\n'
                )
        return "".join(lines)

    # ------------------------------------------------------------------
    # Swift (SwiftUI)
    # ------------------------------------------------------------------

    def _gen_swift(
        self,
        screens: List[Dict[str, Any]],
        app_name: str,
        package_name: str,
    ) -> Dict[str, str]:
        files: Dict[str, str] = {}
        bundle_id = package_name

        nav_links: List[str] = []
        for screen in screens[1:]:
            sname = self._pascal(screen.get("name", "Home"))
            nav_links.append(
                f'                NavigationLink("{sname}") {{\n'
                f"                    {sname}View()\n"
                f"                }}"
            )
        nav_str = "\n".join(nav_links)
        first = self._pascal(screens[0].get("name", "Home"))

        files["ContentView.swift"] = (
            "import SwiftUI\n\n"
            "struct ContentView: View {\n"
            "    var body: some View {\n"
            "        NavigationStack {\n"
            f"            {first}View()\n"
            "        }\n"
            "    }\n"
            "}\n\n"
            "#Preview {\n"
            "    ContentView()\n"
            "}\n"
        )

        files[f"{app_name}App.swift"] = (
            "import SwiftUI\n\n"
            "@main\n"
            f"struct {self._pascal(app_name)}App: App {{\n"
            "    var body: some Scene {\n"
            "        WindowGroup {\n"
            "            ContentView()\n"
            "        }\n"
            "    }\n"
            "}\n"
        )

        for screen in screens:
            sname = self._pascal(screen.get("name", "Home"))
            comps = screen.get("components", [])
            body = self._swift_views(comps, indent=12)
            other_screens = [
                s for s in screens if s.get("name") != screen.get("name")
            ]
            nav_links_inner = ""
            for other in other_screens:
                oname = self._pascal(other.get("name", ""))
                nav_links_inner += (
                    f'            NavigationLink("{oname}") {{\n'
                    f"                {oname}View()\n"
                    f"            }}\n"
                )

            files[f"Views/{sname}View.swift"] = (
                "import SwiftUI\n\n"
                f"struct {sname}View: View {{\n"
                f"    @StateObject private var viewModel = {sname}ViewModel()\n\n"
                "    var body: some View {\n"
                "        ScrollView {\n"
                "            VStack(alignment: .leading, spacing: 12) {\n"
                f"{body}"
                f"{nav_links_inner}"
                "            }\n"
                "            .padding()\n"
                "        }\n"
                f'        .navigationTitle("{sname}")\n'
                "    }\n"
                "}\n\n"
                f"#Preview {{\n"
                f"    NavigationStack {{\n"
                f"        {sname}View()\n"
                f"    }}\n"
                f"}}\n"
            )

            files[f"ViewModels/{sname}ViewModel.swift"] = (
                "import Foundation\n"
                "import SwiftUI\n\n"
                f"class {sname}ViewModel: ObservableObject {{\n"
                f'    @Published var title: String = "{sname}"\n'
                f"    @Published var isLoading: Bool = false\n\n"
                f"    func loadData() {{\n"
                f"        isLoading = true\n"
                f"        // Load data here\n"
                f"        isLoading = false\n"
                f"    }}\n"
                "}\n"
            )

        return files

    def _swift_views(
        self, components: List[Dict[str, Any]], indent: int
    ) -> str:
        lines: List[str] = []
        pad = " " * indent
        for comp in components:
            ctype = comp.get("type", "Container")
            label = comp.get("label", comp.get("text", ""))
            children = comp.get("children", [])

            if ctype == "Button":
                lines.append(
                    f'{pad}Button("{label}") {{\n'
                    f"{pad}    // action\n"
                    f"{pad}}}\n"
                    f"{pad}.buttonStyle(.borderedProminent)\n"
                )
            elif ctype == "Heading":
                lines.append(
                    f'{pad}Text("{label}")\n'
                    f"{pad}    .font(.title)\n"
                    f"{pad}    .bold()\n"
                )
            elif ctype == "Text":
                lines.append(f'{pad}Text("{label}")\n')
            elif ctype == "Input":
                ph = comp.get("placeholder", label)
                lines.append(
                    f'{pad}TextField("{ph}", text: .constant(""))\n'
                    f"{pad}    .textFieldStyle(.roundedBorder)\n"
                )
            elif ctype == "TextArea":
                lines.append(
                    f'{pad}TextEditor(text: .constant(""))\n'
                    f"{pad}    .frame(minHeight: 120)\n"
                    f"{pad}    .border(Color.gray.opacity(0.3))\n"
                )
            elif ctype == "Image":
                src = comp.get("src", "https://via.placeholder.com/150")
                lines.append(
                    f'{pad}AsyncImage(url: URL(string: "{src}")) {{ image in\n'
                    f"{pad}    image.resizable().aspectRatio(contentMode: .fit)\n"
                    f"{pad}}} placeholder: {{\n"
                    f"{pad}    ProgressView()\n"
                    f"{pad}}}\n"
                )
            elif ctype == "Card":
                child_body = (
                    self._swift_views(children, indent + 4)
                    if children
                    else f'{pad}    Text("{label}")\n'
                )
                lines.append(
                    f"{pad}GroupBox {{\n"
                    f"{child_body}"
                    f"{pad}}}\n"
                )
            elif ctype == "Switch":
                lines.append(
                    f'{pad}Toggle("{label}", isOn: .constant(false))\n'
                )
            elif ctype == "Container" and children:
                direction = comp.get("direction", "column")
                stack = "HStack" if direction == "row" else "VStack"
                child_body = self._swift_views(children, indent + 4)
                lines.append(
                    f"{pad}{stack} {{\n"
                    f"{child_body}"
                    f"{pad}}}\n"
                )
            else:
                lines.append(f'{pad}Text("{label}")\n')
        return "".join(lines)

    # ------------------------------------------------------------------
    # Naming helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _pascal(name: str) -> str:
        return "".join(
            w.capitalize()
            for w in name.replace("-", " ").replace("_", " ").split()
        )

    @staticmethod
    def _snake(name: str) -> str:
        return name.lower().replace(" ", "_").replace("-", "_")
