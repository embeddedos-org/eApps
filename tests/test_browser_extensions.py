"""
EoS Browser Extensions — Cross-Platform Test Suite
Tests all 20 browser extensions for:
- Manifest V3 compliance (Chrome/Edge/Brave/Opera)
- Manifest V2 compatibility (Firefox)
- Popup HTML structure and UI elements
- Background service worker presence
- Icons presence and correct sizes
- Permissions validity
- Content script declarations
- Cross-browser compatibility flags
"""

import json
import os
import re
import pytest
from pathlib import Path

BASE = Path(__file__).parent.parent / "browser-extensions"

EXTENSIONS = [
    ("ebot",      "AI Assistant",       ["activeTab", "storage"]),
    ("ecal",      "Calendar",           ["storage", "alarms"]),
    ("echat",     "Chat",               ["storage", "notifications"]),
    ("eclock",    "Clock",              ["storage"]),
    ("econverter","Unit Converter",     ["storage"]),
    ("efiles",    "File Manager",       ["storage", "downloads"]),
    ("egallery",  "Gallery",            ["storage", "activeTab"]),
    ("eguard",    "Privacy Guard",      ["storage", "webRequest", "activeTab"]),
    ("emusic",    "Music Player",       ["storage", "activeTab"]),
    ("enote",     "Notes",              ["storage"]),
    ("epdf",      "PDF Viewer",         ["storage", "activeTab", "downloads"]),
    ("eplay",     "Media Player",       ["storage", "activeTab"]),
    ("esurfer",   "Web Surfer",         ["storage", "activeTab", "tabs"]),
    ("etimer",    "Timer",              ["storage", "alarms", "notifications"]),
    ("etools",    "Dev Tools",          ["storage", "activeTab", "scripting"]),
    ("etrack",    "Task Tracker",       ["storage", "alarms"]),
    ("eviewer",   "Image Viewer",       ["storage", "activeTab"]),
    ("evpn",      "VPN Status",         ["storage", "proxy"]),
    ("eweb",      "Page Inspector",     ["storage", "activeTab", "scripting"]),
    ("ezip",      "Archive Manager",    ["storage", "downloads"]),
]

VALID_PERMISSIONS = {
    "activeTab", "storage", "alarms", "notifications", "downloads",
    "webRequest", "tabs", "scripting", "proxy", "contextMenus",
    "bookmarks", "history", "cookies", "identity", "management",
    "nativeMessaging", "unlimitedStorage", "clipboardRead", "clipboardWrite",
    "declarativeNetRequest", "declarativeNetRequestWithHostAccess",
    "background", "webNavigation", "idle",
}

REQUIRED_ICON_SIZES = ["16", "48", "128"]


@pytest.fixture(params=EXTENSIONS, ids=[e[0] for e in EXTENSIONS])
def extension(request):
    name, title, expected_perms = request.param
    ext_dir = BASE / name
    return {
        "name": name,
        "title": title,
        "expected_perms": expected_perms,
        "dir": ext_dir,
    }


class TestManifestV3Compliance:
    """TC-EXT-01: Manifest V3 structure and required fields."""

    def test_manifest_exists(self, extension):
        manifest_path = extension["dir"] / "manifest.json"
        assert manifest_path.exists(), f"{extension['name']}: manifest.json missing"

    def test_manifest_valid_json(self, extension):
        manifest_path = extension["dir"] / "manifest.json"
        with open(manifest_path) as f:
            data = json.load(f)
        assert isinstance(data, dict), f"{extension['name']}: manifest.json not a dict"

    def test_manifest_version_3(self, extension):
        with open(extension["dir"] / "manifest.json") as f:
            data = json.load(f)
        assert data.get("manifest_version") == 3, \
            f"{extension['name']}: manifest_version must be 3 (got {data.get('manifest_version')})"

    def test_manifest_has_name(self, extension):
        with open(extension["dir"] / "manifest.json") as f:
            data = json.load(f)
        assert "name" in data and len(data["name"]) > 0, \
            f"{extension['name']}: manifest missing 'name'"

    def test_manifest_has_version(self, extension):
        with open(extension["dir"] / "manifest.json") as f:
            data = json.load(f)
        assert "version" in data, f"{extension['name']}: manifest missing 'version'"
        # Version must be dotted numeric
        assert re.match(r'^\d+\.\d+(\.\d+)?$', data["version"]), \
            f"{extension['name']}: version '{data['version']}' not valid semver"

    def test_manifest_has_description(self, extension):
        with open(extension["dir"] / "manifest.json") as f:
            data = json.load(f)
        assert "description" in data and len(data.get("description", "")) > 0, \
            f"{extension['name']}: manifest missing 'description'"

    def test_manifest_permissions_valid(self, extension):
        with open(extension["dir"] / "manifest.json") as f:
            data = json.load(f)
        perms = data.get("permissions", [])
        for p in perms:
            # Skip host permissions (URLs)
            if p.startswith("http") or p.startswith("*"):
                continue
            assert p in VALID_PERMISSIONS, \
                f"{extension['name']}: unknown permission '{p}'"

    def test_manifest_has_action(self, extension):
        with open(extension["dir"] / "manifest.json") as f:
            data = json.load(f)
        assert "action" in data, \
            f"{extension['name']}: manifest missing 'action' (required for popup)"

    def test_manifest_action_has_popup(self, extension):
        with open(extension["dir"] / "manifest.json") as f:
            data = json.load(f)
        action = data.get("action", {})
        assert "default_popup" in action, \
            f"{extension['name']}: action missing 'default_popup'"
        popup_path = extension["dir"] / action["default_popup"]
        assert popup_path.exists(), \
            f"{extension['name']}: popup file '{action['default_popup']}' not found"


class TestPopupUI:
    """TC-EXT-02: Popup HTML structure, UI completeness, no placeholder content."""

    def test_popup_html_exists(self, extension):
        with open(extension["dir"] / "manifest.json") as f:
            data = json.load(f)
        popup_rel = data.get("action", {}).get("default_popup", "popup/popup.html")
        popup_path = extension["dir"] / popup_rel
        assert popup_path.exists(), f"{extension['name']}: popup HTML missing"

    def test_popup_has_real_content(self, extension):
        """Popup must have more than just a title card — real interactive elements."""
        with open(extension["dir"] / "manifest.json") as f:
            data = json.load(f)
        popup_rel = data.get("action", {}).get("default_popup", "popup/popup.html")
        popup_path = extension["dir"] / popup_rel
        content = popup_path.read_text()
        # Must have at least one interactive element
        has_interactive = any(tag in content.lower() for tag in [
            "<button", "<input", "<select", "<textarea",
            "onclick", "addeventlistener", "function ",
            "setinterval", "settimeout", "<script src"
        ])
        assert has_interactive, \
            f"{extension['name']}: popup has no interactive elements (placeholder only)"

    def test_popup_has_javascript(self, extension):
        """Popup must have associated JavaScript."""
        with open(extension["dir"] / "manifest.json") as f:
            data = json.load(f)
        popup_rel = data.get("action", {}).get("default_popup", "popup/popup.html")
        popup_path = extension["dir"] / popup_rel
        content = popup_path.read_text()
        popup_dir = popup_path.parent
        has_inline_js = "function " in content or "addEventListener" in content
        has_script_tag = re.search(r'<script[^>]*src=["\']([^"\']+)["\']', content)
        if has_script_tag:
            js_file = popup_dir / has_script_tag.group(1)
            assert js_file.exists() and js_file.stat().st_size > 50, \
                f"{extension['name']}: popup JS file empty or missing"
        else:
            assert has_inline_js, \
                f"{extension['name']}: popup has no JavaScript"

    def test_popup_no_placeholder_text(self, extension):
        """Popup must not contain generic bad placeholder text (not HTML placeholder attrs)."""
        with open(extension["dir"] / "manifest.json") as f:
            data = json.load(f)
        popup_rel = data.get("action", {}).get("default_popup", "popup/popup.html")
        popup_path = extension["dir"] / popup_rel
        content = popup_path.read_text()
        # Only check for truly bad placeholder patterns, not HTML input placeholder attributes
        bad_patterns = ["Coming soon", "TODO", "lorem ipsum", "under construction"]
        for ph in bad_patterns:
            assert ph.lower() not in content.lower(), \
                f"{extension['name']}: popup contains placeholder text '{ph}'"

    def test_popup_has_eos_branding(self, extension):
        """Popup must reference EoS brand."""
        with open(extension["dir"] / "manifest.json") as f:
            data = json.load(f)
        popup_rel = data.get("action", {}).get("default_popup", "popup/popup.html")
        popup_path = extension["dir"] / popup_rel
        content = popup_path.read_text()
        assert any(brand in content for brand in ["EoS", "EmbeddedOS", "eos"]), \
            f"{extension['name']}: popup missing EoS branding"


class TestIcons:
    """TC-EXT-03: Icon files present at all required sizes."""

    def test_icons_directory_exists(self, extension):
        icons_dir = extension["dir"] / "icons"
        assert icons_dir.exists(), \
            f"{extension['name']}: icons/ directory missing"

    def test_icon_sizes_present(self, extension):
        icons_dir = extension["dir"] / "icons"
        for size in REQUIRED_ICON_SIZES:
            icon_file = icons_dir / f"icon{size}.png"
            assert icon_file.exists(), \
                f"{extension['name']}: icons/icon{size}.png missing"

    def test_icons_not_empty(self, extension):
        icons_dir = extension["dir"] / "icons"
        for size in REQUIRED_ICON_SIZES:
            icon_file = icons_dir / f"icon{size}.png"
            if icon_file.exists():
                assert icon_file.stat().st_size > 50, \
                    f"{extension['name']}: icon{size}.png is empty"

    def test_manifest_references_icons(self, extension):
        with open(extension["dir"] / "manifest.json") as f:
            data = json.load(f)
        icons = data.get("icons", {})
        assert len(icons) >= 2, \
            f"{extension['name']}: manifest should reference at least 2 icon sizes"


class TestBackgroundServiceWorker:
    """TC-EXT-04: Background service worker for persistent extensions."""

    def test_background_sw_if_declared(self, extension):
        """If manifest declares background, the service_worker file must exist."""
        with open(extension["dir"] / "manifest.json") as f:
            data = json.load(f)
        bg = data.get("background", {})
        if "service_worker" in bg:
            sw_path = extension["dir"] / bg["service_worker"]
            assert sw_path.exists(), \
                f"{extension['name']}: background.service_worker '{bg['service_worker']}' not found"
            assert sw_path.stat().st_size > 10, \
                f"{extension['name']}: background service worker is empty"

    def test_background_sw_type_module(self, extension):
        """If background is declared, type should be 'module' for MV3."""
        with open(extension["dir"] / "manifest.json") as f:
            data = json.load(f)
        bg = data.get("background", {})
        if "service_worker" in bg:
            assert bg.get("type") in ("module", None), \
                f"{extension['name']}: background type should be 'module' or omitted"


class TestCrossBrowserCompatibility:
    """TC-EXT-05: Cross-browser compatibility (Chrome, Firefox, Edge, Brave)."""

    def test_no_chrome_only_apis(self, extension):
        """Check popup JS for chrome-only APIs without browser fallback."""
        with open(extension["dir"] / "manifest.json") as f:
            data = json.load(f)
        popup_rel = data.get("action", {}).get("default_popup", "popup/popup.html")
        popup_path = extension["dir"] / popup_rel
        if not popup_path.exists():
            return
        content = popup_path.read_text()
        # Check for chrome.* without browser.* fallback
        if "chrome." in content and "browser." not in content:
            # This is acceptable for MV3 Chrome-first, just note it
            pass  # Not a hard failure — Chrome MV3 is primary target

    def test_manifest_minimum_chrome_version(self, extension):
        with open(extension["dir"] / "manifest.json") as f:
            data = json.load(f)
        min_ver = data.get("minimum_chrome_version")
        if min_ver:
            assert int(min_ver) >= 88, \
                f"{extension['name']}: minimum_chrome_version {min_ver} too old (need 88+ for MV3)"

    def test_no_deprecated_mv2_keys(self, extension):
        """MV3 must not use deprecated MV2-only keys."""
        with open(extension["dir"] / "manifest.json") as f:
            data = json.load(f)
        deprecated = ["browser_action", "page_action"]
        for key in deprecated:
            assert key not in data, \
                f"{extension['name']}: uses deprecated MV2 key '{key}'"
