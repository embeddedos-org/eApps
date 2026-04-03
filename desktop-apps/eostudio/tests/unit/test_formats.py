"""Unit tests for file format modules — project, OBJ, STL, SVG, DXF."""

from __future__ import annotations

import json
import os
import tempfile
import unittest

from eostudio.formats.project import EoStudioProject
from eostudio.formats.obj import OBJExporter
from eostudio.formats.stl import STLExporter
from eostudio.formats.svg import SVGExporter
from eostudio.formats.dxf import DXFExporter
from eostudio.core.geometry.primitives import create_cube


class TestEoStudioProject(unittest.TestCase):
    def test_create_and_save(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project = EoStudioProject(name="Test Project")
            project.add_component({"type": "cube", "size": 2})
            path = os.path.join(tmpdir, "test.eostudio")
            project.save(path)
            self.assertTrue(os.path.exists(path))

    def test_save_load_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project = EoStudioProject(name="Roundtrip Test")
            project.add_component({"type": "sphere", "radius": 1.5})
            project.metadata["author"] = "test"
            path = os.path.join(tmpdir, "rt.eostudio")
            project.save(path)
            loaded = EoStudioProject.load(path)
            self.assertEqual(loaded.name, "Roundtrip Test")
            self.assertEqual(len(loaded.components), 1)
            self.assertEqual(loaded.components[0]["type"], "sphere")

    def test_project_json_structure(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project = EoStudioProject(name="Structure Test")
            project.add_component({"type": "Button", "label": "OK"})
            path = os.path.join(tmpdir, "struct.eostudio")
            project.save(path)
            with open(path) as f:
                data = json.load(f)
            self.assertIn("name", data)
            self.assertIn("components", data)
            self.assertIn("version", data)


class TestOBJExporter(unittest.TestCase):
    def test_export_cube(self) -> None:
        mesh = create_cube(2.0)
        exporter = OBJExporter()
        content = exporter.export(mesh)
        self.assertIn("v ", content)
        self.assertIn("f ", content)

    def test_export_to_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            mesh = create_cube(1.0)
            exporter = OBJExporter()
            path = os.path.join(tmpdir, "test.obj")
            exporter.export_to_file(mesh, path)
            self.assertTrue(os.path.exists(path))
            with open(path) as f:
                content = f.read()
            self.assertIn("v ", content)


class TestSTLExporter(unittest.TestCase):
    def test_export_ascii(self) -> None:
        mesh = create_cube(2.0)
        exporter = STLExporter()
        content = exporter.export_ascii(mesh)
        self.assertIn("solid", content)
        self.assertIn("facet normal", content)
        self.assertIn("endsolid", content)

    def test_export_binary_header(self) -> None:
        mesh = create_cube(1.0)
        exporter = STLExporter()
        data = exporter.export_binary(mesh)
        self.assertIsInstance(data, bytes)
        self.assertGreater(len(data), 84)


class TestSVGExporter(unittest.TestCase):
    def test_export_basic(self) -> None:
        exporter = SVGExporter()
        shapes = [
            {"type": "rect", "x": 10, "y": 10, "width": 100, "height": 50, "fill": "#ff0000"},
            {"type": "circle", "cx": 80, "cy": 80, "r": 30, "fill": "#00ff00"},
        ]
        svg = exporter.export(shapes, width=200, height=200)
        self.assertIn("<svg", svg)
        self.assertIn("viewBox", svg)
        self.assertIn("<rect", svg)
        self.assertIn("<circle", svg)

    def test_export_to_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = SVGExporter()
            shapes = [{"type": "rect", "x": 0, "y": 0, "width": 50, "height": 50}]
            path = os.path.join(tmpdir, "test.svg")
            exporter.export_to_file(shapes, path)
            self.assertTrue(os.path.exists(path))


class TestDXFExporter(unittest.TestCase):
    def test_export_basic(self) -> None:
        exporter = DXFExporter()
        entities = [
            {"type": "line", "start": [0, 0], "end": [100, 100]},
            {"type": "circle", "center": [50, 50], "radius": 25},
        ]
        dxf = exporter.export(entities)
        self.assertIn("SECTION", dxf)
        self.assertIn("ENTITIES", dxf)
        self.assertIn("LINE", dxf)
        self.assertIn("CIRCLE", dxf)
        self.assertIn("EOF", dxf)


if __name__ == "__main__":
    unittest.main()
