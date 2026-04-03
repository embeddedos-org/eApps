"""Unit tests for EoStudio code generators."""

from __future__ import annotations

import unittest
from typing import Any, Dict, List

from eostudio.codegen.html_css import HTMLCSSGenerator
from eostudio.codegen.flutter import FlutterGenerator
from eostudio.codegen.compose import ComposeGenerator
from eostudio.codegen.react import ReactGenerator
from eostudio.codegen.openscad import OpenSCADGenerator


SAMPLE_COMPONENTS: List[Dict[str, Any]] = [
    {"type": "Heading", "label": "Welcome"},
    {"type": "Text", "label": "Hello from EoStudio"},
    {"type": "Input", "label": "Username", "placeholder": "Enter username"},
    {"type": "Button", "label": "Submit"},
    {
        "type": "Card",
        "label": "Info Card",
        "children": [
            {"type": "Text", "label": "Card content here"},
        ],
    },
    {
        "type": "Container",
        "direction": "row",
        "children": [
            {"type": "Button", "label": "OK"},
            {"type": "Button", "label": "Cancel"},
        ],
    },
]

SAMPLE_SCREENS: List[Dict[str, Any]] = [
    {"name": "Home", "components": SAMPLE_COMPONENTS},
    {
        "name": "Settings",
        "components": [
            {"type": "Heading", "label": "Settings"},
            {"type": "Input", "label": "API Key", "placeholder": "Enter key"},
            {"type": "Button", "label": "Save"},
        ],
    },
]

SAMPLE_3D_COMPONENTS: List[Dict[str, Any]] = [
    {"type": "cube", "size": 2, "position": [0, 0, 0], "color": "red"},
    {"type": "sphere", "radius": 1.0, "position": [3, 0, 0]},
    {"type": "cylinder", "radius": 0.5, "height": 2, "position": [0, 3, 0]},
    {
        "type": "difference",
        "children": [
            {"type": "cube", "size": 3},
            {"type": "sphere", "radius": 1.8},
        ],
    },
]


class TestHTMLCSSGenerator(unittest.TestCase):
    """Tests for HTML/CSS code generator."""

    def test_generates_index_html(self) -> None:
        gen = HTMLCSSGenerator()
        files = gen.generate(SAMPLE_COMPONENTS, [])
        self.assertIn("index.html", files)
        self.assertIn("styles.css", files)

    def test_html_contains_elements(self) -> None:
        gen = HTMLCSSGenerator()
        files = gen.generate(SAMPLE_COMPONENTS, [])
        html = files["index.html"]
        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn("<button", html)
        self.assertIn("<input", html)
        self.assertIn("Welcome", html)

    def test_screens_generate_multiple_pages(self) -> None:
        gen = HTMLCSSGenerator()
        files = gen.generate(SAMPLE_COMPONENTS, SAMPLE_SCREENS)
        self.assertIn("home.html", files)
        self.assertIn("settings.html", files)
        self.assertIn("index.html", files)

    def test_css_contains_responsive(self) -> None:
        gen = HTMLCSSGenerator()
        files = gen.generate(SAMPLE_COMPONENTS, [])
        css = files["styles.css"]
        self.assertIn("@media", css)
        self.assertIn("flex", css)


class TestFlutterGenerator(unittest.TestCase):
    """Tests for Flutter code generator."""

    def test_generates_main_dart(self) -> None:
        gen = FlutterGenerator()
        files = gen.generate(SAMPLE_COMPONENTS, SAMPLE_SCREENS)
        self.assertIn("lib/main.dart", files)

    def test_main_contains_material_app(self) -> None:
        gen = FlutterGenerator()
        files = gen.generate(SAMPLE_COMPONENTS, SAMPLE_SCREENS)
        main = files["lib/main.dart"]
        self.assertIn("MaterialApp", main)
        self.assertIn("flutter/material.dart", main)

    def test_screen_files_generated(self) -> None:
        gen = FlutterGenerator()
        files = gen.generate(SAMPLE_COMPONENTS, SAMPLE_SCREENS)
        self.assertIn("lib/screens/home_screen.dart", files)
        self.assertIn("lib/screens/settings_screen.dart", files)

    def test_screen_contains_widgets(self) -> None:
        gen = FlutterGenerator()
        files = gen.generate(SAMPLE_COMPONENTS, SAMPLE_SCREENS)
        home = files["lib/screens/home_screen.dart"]
        self.assertIn("ElevatedButton", home)
        self.assertIn("TextField", home)
        self.assertIn("Scaffold", home)


class TestComposeGenerator(unittest.TestCase):
    """Tests for Jetpack Compose code generator."""

    def test_generates_main_activity(self) -> None:
        gen = ComposeGenerator()
        files = gen.generate(SAMPLE_COMPONENTS, SAMPLE_SCREENS)
        self.assertIn("MainActivity.kt", files)

    def test_main_activity_content(self) -> None:
        gen = ComposeGenerator()
        files = gen.generate(SAMPLE_COMPONENTS, SAMPLE_SCREENS)
        main = files["MainActivity.kt"]
        self.assertIn("MaterialTheme", main)
        self.assertIn("ComponentActivity", main)

    def test_screen_files_generated(self) -> None:
        gen = ComposeGenerator()
        files = gen.generate(SAMPLE_COMPONENTS, SAMPLE_SCREENS)
        self.assertIn("screens/HomeScreen.kt", files)
        self.assertIn("screens/SettingsScreen.kt", files)

    def test_nav_graph_generated(self) -> None:
        gen = ComposeGenerator()
        files = gen.generate(SAMPLE_COMPONENTS, SAMPLE_SCREENS)
        self.assertIn("navigation/NavGraph.kt", files)
        nav = files["navigation/NavGraph.kt"]
        self.assertIn("NavHost", nav)

    def test_screen_contains_composables(self) -> None:
        gen = ComposeGenerator()
        files = gen.generate(SAMPLE_COMPONENTS, SAMPLE_SCREENS)
        home = files["screens/HomeScreen.kt"]
        self.assertIn("Button", home)
        self.assertIn("OutlinedTextField", home)
        self.assertIn("@Composable", home)


class TestReactGenerator(unittest.TestCase):
    """Tests for React code generator."""

    def test_generates_app_jsx(self) -> None:
        gen = ReactGenerator()
        files = gen.generate(SAMPLE_COMPONENTS, SAMPLE_SCREENS)
        self.assertIn("src/App.jsx", files)
        self.assertIn("src/index.jsx", files)
        self.assertIn("src/index.css", files)

    def test_app_contains_router(self) -> None:
        gen = ReactGenerator()
        files = gen.generate(SAMPLE_COMPONENTS, SAMPLE_SCREENS)
        app = files["src/App.jsx"]
        self.assertIn("Routes", app)
        self.assertIn("Route", app)
        self.assertIn("Link", app)

    def test_screen_files_generated(self) -> None:
        gen = ReactGenerator()
        files = gen.generate(SAMPLE_COMPONENTS, SAMPLE_SCREENS)
        self.assertIn("src/screens/Home.jsx", files)
        self.assertIn("src/screens/Settings.jsx", files)
        self.assertIn("src/screens/Home.module.css", files)

    def test_screen_contains_jsx(self) -> None:
        gen = ReactGenerator()
        files = gen.generate(SAMPLE_COMPONENTS, SAMPLE_SCREENS)
        home = files["src/screens/Home.jsx"]
        self.assertIn("useState", home)
        self.assertIn("<button", home)
        self.assertIn("<input", home)


class TestOpenSCADGenerator(unittest.TestCase):
    """Tests for OpenSCAD code generator."""

    def test_generates_scad(self) -> None:
        gen = OpenSCADGenerator()
        code = gen.generate(SAMPLE_3D_COMPONENTS)
        self.assertIn("$fn", code)
        self.assertIn("cube(", code)
        self.assertIn("sphere(", code)
        self.assertIn("cylinder(", code)

    def test_csg_operations(self) -> None:
        gen = OpenSCADGenerator()
        code = gen.generate(SAMPLE_3D_COMPONENTS)
        self.assertIn("difference()", code)

    def test_transforms(self) -> None:
        gen = OpenSCADGenerator()
        comps = [{"type": "cube", "size": 1, "position": [5, 0, 0]}]
        code = gen.generate(comps)
        self.assertIn("translate(", code)

    def test_colors(self) -> None:
        gen = OpenSCADGenerator()
        comps = [{"type": "sphere", "radius": 1, "color": "blue"}]
        code = gen.generate(comps)
        self.assertIn('color("blue")', code)

    def test_empty_scene(self) -> None:
        gen = OpenSCADGenerator()
        code = gen.generate([])
        self.assertIn("cube(", code)


if __name__ == "__main__":
    unittest.main()
