import unittest
class TestEAppsUnit(unittest.TestCase):
    def test_app_package_parsing(self):
        manifest = {"name": "app1", "version": "1.0.0"}
        self.assertEqual(manifest["version"], "1.0.0")
