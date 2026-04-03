"""Integration tests — end-to-end project workflows, CLI smoke tests, template scaffolding."""

from __future__ import annotations

import json
import os
import tempfile
import unittest

from click.testing import CliRunner

from eostudio.cli.main import cli
from eostudio.templates.samples import (
    BUILTIN_TEMPLATES, get_template, list_templates, create_project_from_template,
)


class TestTemplateScaffolding(unittest.TestCase):
    def test_list_all_templates(self) -> None:
        templates = list_templates()
        self.assertEqual(len(templates), 5)

    def test_list_by_category(self) -> None:
        ui_templates = list_templates(category="ui")
        self.assertGreater(len(ui_templates), 0)
        for t in ui_templates:
            self.assertEqual(t.category, "ui")

    def test_get_template_exists(self) -> None:
        tmpl = get_template("todo-app")
        self.assertIsNotNone(tmpl)
        self.assertEqual(tmpl.name, "todo-app")

    def test_get_template_nonexistent(self) -> None:
        tmpl = get_template("nonexistent")
        self.assertIsNone(tmpl)

    def test_create_project_from_template(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = create_project_from_template("todo-app", tmpdir)
            self.assertTrue(os.path.exists(project_path))
            self.assertTrue(project_path.endswith(".eostudio"))
            readme = os.path.join(tmpdir, "README.md")
            self.assertTrue(os.path.exists(readme))
            with open(project_path) as f:
                data = json.load(f)
            self.assertEqual(data["name"], "todo-app")
            self.assertIn("components", data)

    def test_create_project_invalid_template(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaises(ValueError):
                create_project_from_template("nonexistent", tmpdir)

    def test_all_templates_scaffold(self) -> None:
        for name in BUILTIN_TEMPLATES:
            with tempfile.TemporaryDirectory() as tmpdir:
                path = create_project_from_template(name, tmpdir)
                self.assertTrue(os.path.exists(path))
                with open(path) as f:
                    data = json.load(f)
                self.assertIn("version", data)
                self.assertIn("components", data)

    def test_template_project_dict(self) -> None:
        tmpl = get_template("simulation-pid")
        data = tmpl.to_project_dict()
        self.assertEqual(data["version"], "0.1.0")
        self.assertEqual(data["editor_type"], "simulation")
        self.assertGreater(len(data["components"]), 0)


class TestCLISmokeTests(unittest.TestCase):
    def test_version(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("EoStudio", result.output)

    def test_help(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("launch", result.output)
        self.assertIn("export", result.output)
        self.assertIn("codegen", result.output)
        self.assertIn("ask", result.output)
        self.assertIn("new", result.output)

    def test_teach_help(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["teach", "--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("--lesson", result.output)

    def test_ask_help(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["ask", "--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("--provider", result.output)
        self.assertIn("--domain", result.output)

    def test_new_help(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["new", "--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("--template", result.output)

    def test_codegen_help(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["codegen", "--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("--framework", result.output)


class TestCodegenEndToEnd(unittest.TestCase):
    def test_html_codegen_from_components(self) -> None:
        from eostudio.codegen.html_css import HTMLCSSGenerator

        components = [
            {"type": "Heading", "label": "Hello"},
            {"type": "Button", "label": "Click Me"},
        ]
        gen = HTMLCSSGenerator()
        files = gen.generate(components, [])
        self.assertIn("index.html", files)
        self.assertIn("styles.css", files)
        self.assertIn("Hello", files["index.html"])

    def test_react_codegen_with_screens(self) -> None:
        from eostudio.codegen.react import ReactGenerator

        components = [{"type": "Button", "label": "OK"}]
        screens = [
            {"name": "Home", "components": components},
            {"name": "About", "components": [{"type": "Text", "label": "About page"}]},
        ]
        gen = ReactGenerator()
        files = gen.generate(components, screens)
        self.assertIn("src/App.jsx", files)
        self.assertIn("src/screens/Home.jsx", files)
        self.assertIn("src/screens/About.jsx", files)


if __name__ == "__main__":
    unittest.main()
