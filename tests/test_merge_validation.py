"""
EoS eApps — Merge Validation Test Suite

Validates that all source repos (eOffice, EoStudio, EoSim, eServiceApps, eBrowser)
have been fully merged into eApps with correct structure and file integrity.

Usage:
    python tests/test_merge_validation.py
    python -m pytest tests/test_merge_validation.py -v
"""

import json
import os
import unittest

EAPPS_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def count_files(path):
    total = 0
    for root, dirs, files in os.walk(path):
        total += len(files)
    return total


def list_dirs(path):
    return sorted(
        [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
    )


def file_exists(rel_path):
    return os.path.isfile(os.path.join(EAPPS_ROOT, rel_path))


def dir_exists(rel_path):
    return os.path.isdir(os.path.join(EAPPS_ROOT, rel_path))


class TestMarketplaceStructure(unittest.TestCase):
    """Test that the marketplace website files exist and are valid."""

    def test_index_html_exists(self):
        self.assertTrue(file_exists("index.html"))

    def test_css_exists(self):
        self.assertTrue(file_exists("css/marketplace.css"))

    def test_js_exists(self):
        self.assertTrue(file_exists("js/marketplace.js"))

    def test_favicon_exists(self):
        self.assertTrue(file_exists("assets/favicon.svg"))


class TestAppsJson(unittest.TestCase):
    """Test that data/apps.json is valid and contains all expected apps."""

    @classmethod
    def setUpClass(cls):
        with open(os.path.join(EAPPS_ROOT, "data", "apps.json"), "r", encoding="utf-8") as f:
            cls.data = json.load(f)
        cls.apps = cls.data["apps"]
        cls.categories = cls.data["categories"]

    def test_json_has_meta(self):
        self.assertIn("meta", self.data)
        self.assertIn("version", self.data["meta"])
        self.assertIn("lastUpdated", self.data["meta"])

    def test_json_has_categories(self):
        self.assertGreaterEqual(len(self.categories), 6)
        cat_ids = [c["id"] for c in self.categories]
        for expected in ["extensions", "desktop", "mobile", "service", "native", "web"]:
            self.assertIn(expected, cat_ids)

    def test_json_has_apps(self):
        self.assertGreater(len(self.apps), 40)

    def test_all_apps_have_required_fields(self):
        required = ["id", "name", "description", "category", "platform", "version"]
        for app in self.apps:
            for field in required:
                self.assertIn(
                    field, app, f"App '{app.get('id', 'UNKNOWN')}' missing '{field}'"
                )

    def test_all_app_ids_unique(self):
        ids = [a["id"] for a in self.apps]
        self.assertEqual(len(ids), len(set(ids)), "Duplicate app IDs found")

    def test_extension_apps_present(self):
        ext_ids = [a["id"] for a in self.apps if a["category"] == "extensions"]
        self.assertGreaterEqual(len(ext_ids), 10)
        for expected in ["eoffice-chrome", "eoffice-firefox", "eoffice-vscode"]:
            self.assertIn(expected, ext_ids)

    def test_desktop_apps_present(self):
        desk_ids = [a["id"] for a in self.apps if a["category"] == "desktop"]
        self.assertGreaterEqual(len(desk_ids), 4)
        for expected in [
            "eoffice-desktop",
            "eostudio-desktop",
            "ebrowser-desktop",
            "eosim-desktop",
        ]:
            self.assertIn(expected, desk_ids)

    def test_mobile_apps_present(self):
        mob_ids = [a["id"] for a in self.apps if a["category"] == "mobile"]
        self.assertGreaterEqual(len(mob_ids), 4)
        for expected in ["eride", "esocial", "etrack", "etravel"]:
            self.assertIn(expected, mob_ids)

    def test_service_apps_present(self):
        svc_ids = [a["id"] for a in self.apps if a["category"] == "service"]
        self.assertGreaterEqual(len(svc_ids), 1)

    def test_native_apps_present(self):
        native_ids = [a["id"] for a in self.apps if a["category"] == "native"]
        self.assertGreaterEqual(len(native_ids), 20)

    def test_eosim_in_catalog(self):
        eosim = [a for a in self.apps if a["id"] == "eosim-desktop"]
        self.assertEqual(len(eosim), 1)
        self.assertIn("simulator", eosim[0]["tags"])


class TestEOfficeExtensionsMerge(unittest.TestCase):
    """Validate eOffice extensions are fully merged."""

    EXPECTED_EXTENSIONS = [
        "browser",
        "github",
        "google-workspace",
        "jetbrains",
        "obsidian",
        "office365",
        "raycast",
        "safari",
        "slack",
        "vscode",
    ]

    def test_all_extension_dirs_exist(self):
        for ext in self.EXPECTED_EXTENSIONS:
            self.assertTrue(
                dir_exists(f"extensions/{ext}"),
                f"Missing extension: extensions/{ext}",
            )

    def test_browser_extension_has_manifest(self):
        self.assertTrue(file_exists("extensions/browser/manifest.json"))

    def test_vscode_extension_has_package(self):
        self.assertTrue(file_exists("extensions/vscode/package.json"))

    def test_vscode_extension_has_source(self):
        self.assertTrue(file_exists("extensions/vscode/src/extension.ts"))

    def test_jetbrains_has_build_gradle(self):
        self.assertTrue(file_exists("extensions/jetbrains/build.gradle.kts"))

    def test_obsidian_has_main(self):
        self.assertTrue(file_exists("extensions/obsidian/main.ts"))

    def test_slack_has_manifest(self):
        self.assertTrue(file_exists("extensions/slack/manifest.yaml"))

    def test_safari_has_info_plist(self):
        self.assertTrue(file_exists("extensions/safari/Info.plist"))

    def test_google_workspace_has_appsscript(self):
        self.assertTrue(
            file_exists("extensions/google-workspace/appsscript.json")
        )

    def test_office365_has_manifest(self):
        self.assertTrue(file_exists("extensions/office365/manifest.xml"))

    def test_github_has_app_yml(self):
        self.assertTrue(file_exists("extensions/github/app.yml"))

    def test_raycast_has_package(self):
        self.assertTrue(file_exists("extensions/raycast/package.json"))

    def test_extensions_file_count(self):
        count = count_files(os.path.join(EAPPS_ROOT, "extensions"))
        self.assertGreaterEqual(count, 65)


class TestEOfficeDesktopMerge(unittest.TestCase):
    """Validate eOffice desktop/browser/packages/apps are fully merged."""

    def test_desktop_dir_exists(self):
        self.assertTrue(dir_exists("desktop-apps/eoffice/desktop"))

    def test_desktop_has_main_js(self):
        self.assertTrue(file_exists("desktop-apps/eoffice/desktop/main.js"))

    def test_desktop_has_package_json(self):
        self.assertTrue(
            file_exists("desktop-apps/eoffice/desktop/package.json")
        )

    def test_browser_web_apps_exist(self):
        self.assertTrue(dir_exists("desktop-apps/eoffice/browser"))
        self.assertTrue(file_exists("desktop-apps/eoffice/browser/index.html"))

    def test_packages_core_exists(self):
        self.assertTrue(dir_exists("desktop-apps/eoffice/packages/core"))

    def test_packages_server_exists(self):
        self.assertTrue(dir_exists("desktop-apps/eoffice/packages/server"))

    def test_packages_ebot_client_exists(self):
        self.assertTrue(
            dir_exists("desktop-apps/eoffice/packages/ebot-client")
        )

    def test_office_apps_all_present(self):
        expected = [
            "econnect", "edb", "edocs", "edrive", "eforms",
            "email", "enotes", "eplanner", "esheets", "eslides",
            "esway", "launcher",
        ]
        for app in expected:
            self.assertTrue(
                dir_exists(f"desktop-apps/eoffice/apps/{app}"),
                f"Missing office app: {app}",
            )

    def test_config_files_present(self):
        configs = [
            "package.json", "tsconfig.json", "pnpm-workspace.yaml",
            "Dockerfile", "docker-compose.yml", "build.yaml",
        ]
        for f in configs:
            self.assertTrue(
                file_exists(f"desktop-apps/eoffice/{f}"),
                f"Missing config: {f}",
            )


class TestEoStudioMerge(unittest.TestCase):
    """Validate EoStudio is fully merged."""

    def test_source_dir_exists(self):
        self.assertTrue(dir_exists("desktop-apps/eostudio/eostudio"))

    def test_has_init(self):
        self.assertTrue(
            file_exists("desktop-apps/eostudio/eostudio/__init__.py")
        )

    def test_cli_exists(self):
        self.assertTrue(
            file_exists("desktop-apps/eostudio/eostudio/cli/main.py")
        )

    def test_codegen_exists(self):
        self.assertTrue(dir_exists("desktop-apps/eostudio/eostudio/codegen"))
        codegen_files = os.listdir(
            os.path.join(EAPPS_ROOT, "desktop-apps/eostudio/eostudio/codegen")
        )
        self.assertGreater(len(codegen_files), 10)

    def test_core_modules_exist(self):
        expected = [
            "ai", "cad", "design", "design3d", "game",
            "geometry", "hardware", "ide", "image",
        ]
        for mod in expected:
            self.assertTrue(
                dir_exists(f"desktop-apps/eostudio/eostudio/core/{mod}"),
                f"Missing core module: {mod}",
            )

    def test_gui_exists(self):
        self.assertTrue(
            file_exists("desktop-apps/eostudio/eostudio/gui/app.py")
        )

    def test_plugins_exist(self):
        self.assertTrue(
            file_exists(
                "desktop-apps/eostudio/eostudio/plugins/plugin_base.py"
            )
        )

    def test_tests_exist(self):
        self.assertTrue(dir_exists("desktop-apps/eostudio/tests"))
        test_count = count_files(
            os.path.join(EAPPS_ROOT, "desktop-apps/eostudio/tests")
        )
        self.assertGreaterEqual(test_count, 8)

    def test_pyproject_toml_exists(self):
        self.assertTrue(file_exists("desktop-apps/eostudio/pyproject.toml"))

    def test_docs_exist(self):
        self.assertTrue(dir_exists("desktop-apps/eostudio/docs"))

    def test_source_file_count(self):
        count = count_files(
            os.path.join(EAPPS_ROOT, "desktop-apps/eostudio/eostudio")
        )
        self.assertGreaterEqual(count, 140)


class TestEoSimMerge(unittest.TestCase):
    """Validate EoSim is fully merged."""

    def test_source_dir_exists(self):
        self.assertTrue(dir_exists("desktop-apps/eosim/eosim"))

    def test_has_init(self):
        self.assertTrue(
            file_exists("desktop-apps/eosim/eosim/__init__.py")
        )

    def test_has_main(self):
        self.assertTrue(
            file_exists("desktop-apps/eosim/eosim/__main__.py")
        )

    def test_cli_exists(self):
        self.assertTrue(
            file_exists("desktop-apps/eosim/eosim/cli/main.py")
        )

    def test_engine_exists(self):
        self.assertTrue(dir_exists("desktop-apps/eosim/eosim/engine"))
        self.assertTrue(
            file_exists("desktop-apps/eosim/eosim/engine/backend.py")
        )

    def test_native_engine_exists(self):
        self.assertTrue(dir_exists("desktop-apps/eosim/eosim/engine/native"))
        for sub in ["bus", "cpu", "memory", "peripherals", "simulators"]:
            self.assertTrue(
                dir_exists(f"desktop-apps/eosim/eosim/engine/native/{sub}"),
                f"Missing native engine: {sub}",
            )

    def test_qemu_integration_exists(self):
        self.assertTrue(dir_exists("desktop-apps/eosim/eosim/engine/qemu"))
        self.assertTrue(
            file_exists("desktop-apps/eosim/eosim/engine/qemu/qmp_client.py")
        )

    def test_gui_renderers_exist(self):
        expected = [
            "vehicle", "drone", "satellite", "medical",
            "weather", "finance", "gaming", "robot",
        ]
        for renderer in expected:
            self.assertTrue(
                file_exists(
                    f"desktop-apps/eosim/eosim/gui/renderers/{renderer}.py"
                ),
                f"Missing renderer: {renderer}",
            )

    def test_platforms_count(self):
        plat_dir = os.path.join(EAPPS_ROOT, "desktop-apps/eosim/platforms")
        platforms = list_dirs(plat_dir)
        self.assertGreaterEqual(len(platforms), 60)

    def test_key_platforms_present(self):
        expected = [
            "stm32f4", "stm32h7", "esp32", "nrf52", "raspi4",
            "jetson-nano", "riscv64", "arm64", "x86_64", "rp2040",
        ]
        for plat in expected:
            self.assertTrue(
                dir_exists(f"desktop-apps/eosim/platforms/{plat}"),
                f"Missing platform: {plat}",
            )

    def test_integrations_exist(self):
        expected = ["gazebo", "openocd", "xplane", "openfoam", "eos_runner"]
        for integ in expected:
            self.assertTrue(
                file_exists(
                    f"desktop-apps/eosim/eosim/integrations/{integ}.py"
                ),
                f"Missing integration: {integ}",
            )

    def test_tests_exist(self):
        self.assertTrue(dir_exists("desktop-apps/eosim/tests"))
        test_count = count_files(
            os.path.join(EAPPS_ROOT, "desktop-apps/eosim/tests")
        )
        self.assertGreaterEqual(test_count, 10)

    def test_pyproject_toml_exists(self):
        self.assertTrue(file_exists("desktop-apps/eosim/pyproject.toml"))

    def test_dockerfile_exists(self):
        self.assertTrue(file_exists("desktop-apps/eosim/Dockerfile"))

    def test_source_file_count(self):
        count = count_files(
            os.path.join(EAPPS_ROOT, "desktop-apps/eosim/eosim")
        )
        self.assertGreaterEqual(count, 100)


class TestEServiceAppsMerge(unittest.TestCase):
    """Validate eServiceApps is fully merged."""

    def test_lib_dir_exists(self):
        self.assertTrue(dir_exists("service-apps/lib"))

    def test_main_dart_exists(self):
        self.assertTrue(file_exists("service-apps/lib/main.dart"))

    def test_app_dart_exists(self):
        self.assertTrue(file_exists("service-apps/lib/app.dart"))

    def test_feature_modules_present(self):
        expected = [
            "eride", "esocial", "etrack", "etravel",
            "home", "auth", "wallet", "settings",
            "notifications", "onboarding", "admin",
        ]
        for feat in expected:
            self.assertTrue(
                dir_exists(f"service-apps/lib/features/{feat}"),
                f"Missing feature: {feat}",
            )

    def test_core_modules_present(self):
        expected = [
            "models", "providers", "services",
            "router", "theme", "utils", "widgets",
        ]
        for mod in expected:
            self.assertTrue(
                dir_exists(f"service-apps/lib/core/{mod}"),
                f"Missing core module: {mod}",
            )

    def test_pubspec_exists(self):
        self.assertTrue(file_exists("service-apps/pubspec.yaml"))

    def test_firebase_config_exists(self):
        self.assertTrue(file_exists("service-apps/firebase.json"))
        self.assertTrue(file_exists("service-apps/firestore.rules"))
        self.assertTrue(file_exists("service-apps/firestore.indexes.json"))

    def test_tests_exist(self):
        self.assertTrue(dir_exists("service-apps/test"))
        test_count = count_files(
            os.path.join(EAPPS_ROOT, "service-apps/test")
        )
        self.assertGreaterEqual(test_count, 5)

    def test_assets_exist(self):
        self.assertTrue(dir_exists("service-apps/assets"))

    def test_lib_file_count(self):
        count = count_files(os.path.join(EAPPS_ROOT, "service-apps/lib"))
        self.assertGreaterEqual(count, 80)


class TestEBrowserMerge(unittest.TestCase):
    """Validate eBrowser is fully merged."""

    def test_src_dir_exists(self):
        self.assertTrue(dir_exists("desktop-apps/ebrowser/src"))

    def test_engine_modules_present(self):
        expected = [
            "browser", "engine", "input", "network",
            "plugin", "render", "security", "telemetry",
        ]
        for mod in expected:
            self.assertTrue(
                dir_exists(f"desktop-apps/ebrowser/src/{mod}"),
                f"Missing src module: {mod}",
            )

    def test_include_dir_exists(self):
        self.assertTrue(dir_exists("desktop-apps/ebrowser/include"))

    def test_ports_exist(self):
        self.assertTrue(dir_exists("desktop-apps/ebrowser/port"))
        for port in ["sdl2", "eos", "web"]:
            self.assertTrue(
                dir_exists(f"desktop-apps/ebrowser/port/{port}"),
                f"Missing port: {port}",
            )

    def test_cmake_toolchains_exist(self):
        self.assertTrue(dir_exists("desktop-apps/ebrowser/cmake"))
        for tc in ["emscripten.cmake", "eos.cmake", "linux.cmake", "windows.cmake"]:
            self.assertTrue(
                file_exists(f"desktop-apps/ebrowser/cmake/{tc}"),
                f"Missing toolchain: {tc}",
            )

    def test_cmakelists_exists(self):
        self.assertTrue(file_exists("desktop-apps/ebrowser/CMakeLists.txt"))

    def test_tests_exist(self):
        self.assertTrue(dir_exists("desktop-apps/ebrowser/tests"))
        expected_tests = [
            "test_html_parser.c", "test_css_parser.c",
            "test_dom.c", "test_url.c", "test_tls.c",
        ]
        for t in expected_tests:
            self.assertTrue(
                file_exists(f"desktop-apps/ebrowser/tests/{t}"),
                f"Missing test: {t}",
            )

    def test_src_file_count(self):
        count = count_files(
            os.path.join(EAPPS_ROOT, "desktop-apps/ebrowser/src")
        )
        self.assertGreaterEqual(count, 28)


class TestSharedCode(unittest.TestCase):
    """Validate shared code module exists."""

    def test_js_auth_exists(self):
        self.assertTrue(file_exists("shared/js/auth.js"))

    def test_js_api_exists(self):
        self.assertTrue(file_exists("shared/js/api.js"))

    def test_js_utils_exists(self):
        self.assertTrue(file_exists("shared/js/utils.js"))

    def test_shared_readme_exists(self):
        self.assertTrue(file_exists("shared/README.md"))


class TestCICD(unittest.TestCase):
    """Validate CI/CD workflows exist."""

    def test_deploy_marketplace_workflow(self):
        self.assertTrue(
            file_exists(".github/workflows/deploy-marketplace.yml")
        )

    def test_release_app_workflow(self):
        self.assertTrue(file_exists(".github/workflows/release-app.yml"))

    def test_ci_native_workflow(self):
        self.assertTrue(file_exists(".github/workflows/ci-native.yml"))


class TestNativeAppsIntact(unittest.TestCase):
    """Validate original eApps native apps are still intact."""

    EXPECTED_NATIVE_APPS = [
        "efiles", "emusic", "evideo", "egallery", "echat",
        "enote", "ecal", "eclock", "esettings", "ewifi",
        "evpn", "essh", "eftp", "epdf", "epaint",
        "econverter", "ezip", "eguard", "ecleaner", "eremote",
        "ebot", "etools", "eserial", "snake", "tetris",
        "minesweeper", "echess", "dice",
    ]

    def test_native_apps_dir_exists(self):
        self.assertTrue(dir_exists("apps"))

    def test_all_expected_native_apps_present(self):
        for app in self.EXPECTED_NATIVE_APPS:
            self.assertTrue(
                dir_exists(f"apps/{app}"), f"Missing native app: {app}"
            )

    def test_core_dir_exists(self):
        self.assertTrue(dir_exists("core"))

    def test_cmake_dir_exists(self):
        self.assertTrue(dir_exists("cmake"))

    def test_port_dir_exists(self):
        self.assertTrue(dir_exists("port"))

    def test_native_tests_exist(self):
        self.assertTrue(dir_exists("tests"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
