"""Unit tests for the plugin system — Plugin, PluginManager, PluginManifest."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from typing import Any, Dict

from eostudio.plugins.plugin_base import (
    Plugin, PluginManager, PluginManifest, PluginHook, PluginState,
)


class TestPluginManifest(unittest.TestCase):
    def test_from_dict(self) -> None:
        data = {
            "id": "test-plugin",
            "name": "Test Plugin",
            "version": "1.0.0",
            "description": "A test plugin",
            "entry_point": "test_plugin",
        }
        manifest = PluginManifest.from_dict(data)
        self.assertEqual(manifest.id, "test-plugin")
        self.assertEqual(manifest.name, "Test Plugin")
        self.assertEqual(manifest.version, "1.0.0")

    def test_to_dict_roundtrip(self) -> None:
        data = {
            "id": "roundtrip",
            "name": "Roundtrip Test",
            "version": "2.0.0",
            "description": "Testing round-trip",
            "entry_point": "roundtrip_mod",
            "dependencies": ["dep1"],
        }
        manifest = PluginManifest.from_dict(data)
        result = manifest.to_dict()
        self.assertEqual(result["id"], "roundtrip")
        self.assertEqual(result["dependencies"], ["dep1"])

    def test_defaults(self) -> None:
        data = {"id": "minimal", "name": "Minimal"}
        manifest = PluginManifest.from_dict(data)
        self.assertEqual(manifest.version, "0.1.0")
        self.assertEqual(manifest.plugin_type, "tool")
        self.assertEqual(manifest.dependencies, [])


class TestPlugin(unittest.TestCase):
    def test_default_manifest(self) -> None:
        plugin = Plugin()
        self.assertEqual(plugin.manifest.id, "unknown")
        self.assertEqual(plugin.state, PluginState.DISCOVERED)

    def test_activate(self) -> None:
        plugin = Plugin()
        result = plugin.activate({})
        self.assertTrue(result)
        self.assertEqual(plugin.state, PluginState.ACTIVE)

    def test_deactivate(self) -> None:
        plugin = Plugin()
        plugin.activate({})
        plugin.deactivate()
        self.assertEqual(plugin.state, PluginState.DISABLED)

    def test_get_status(self) -> None:
        manifest = PluginManifest(id="test", name="Test", version="1.0")
        plugin = Plugin(manifest)
        status = plugin.get_status()
        self.assertEqual(status["id"], "test")
        self.assertEqual(status["state"], "DISCOVERED")

    def test_hook_dispatch(self) -> None:
        plugin = Plugin()
        called = {"value": False}

        def handler(data: Dict[str, Any]) -> Dict[str, Any]:
            called["value"] = True
            return {"handled": True}

        plugin._hooks[PluginHook.ON_SAVE] = handler
        result = plugin.on_hook(PluginHook.ON_SAVE, {})
        self.assertTrue(called["value"])
        self.assertEqual(result["handled"], True)

    def test_hook_no_handler(self) -> None:
        plugin = Plugin()
        result = plugin.on_hook(PluginHook.ON_SAVE, {})
        self.assertEqual(result, {})

    def test_ui_contributions_empty(self) -> None:
        plugin = Plugin()
        self.assertEqual(plugin.get_menu_items(), [])
        self.assertEqual(plugin.get_toolbar_items(), [])
        self.assertIsNone(plugin.get_panel())


class TestPluginManager(unittest.TestCase):
    def test_discover_empty_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = PluginManager(plugin_dirs=[tmpdir])
            discovered = manager.discover()
            self.assertEqual(len(discovered), 0)

    def test_discover_finds_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            plugin_dir = os.path.join(tmpdir, "my_plugin")
            os.makedirs(plugin_dir)
            manifest_data = {
                "id": "my-plugin",
                "name": "My Plugin",
                "version": "1.0.0",
                "entry_point": "my_plugin_mod",
            }
            with open(os.path.join(plugin_dir, "manifest.json"), "w") as f:
                json.dump(manifest_data, f)

            manager = PluginManager(plugin_dirs=[tmpdir])
            discovered = manager.discover()
            self.assertEqual(len(discovered), 1)
            self.assertEqual(discovered[0].id, "my-plugin")

    def test_fire_hook_no_plugins(self) -> None:
        manager = PluginManager(plugin_dirs=[])
        results = manager.fire_hook(PluginHook.ON_SAVE, {"file": "test.eos"})
        self.assertEqual(results, [])

    def test_get_active_plugins_empty(self) -> None:
        manager = PluginManager(plugin_dirs=[])
        self.assertEqual(manager.get_active_plugins(), [])

    def test_list_plugins_empty(self) -> None:
        manager = PluginManager(plugin_dirs=[])
        self.assertEqual(manager.list_plugins(), [])

    def test_configure_nonexistent(self) -> None:
        manager = PluginManager(plugin_dirs=[])
        manager.configure("nonexistent", {"key": "value"})

    def test_export_config(self) -> None:
        manager = PluginManager(plugin_dirs=[])
        config = manager.export_config()
        self.assertEqual(config, {})

    def test_unload_nonexistent(self) -> None:
        manager = PluginManager(plugin_dirs=[])
        manager.unload("nonexistent")


if __name__ == "__main__":
    unittest.main()
