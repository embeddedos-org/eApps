"""
EoS Web Apps — Cross-Platform PWA Test Suite
Tests all 33 web apps for:
- PWA manifest completeness
- Service worker presence
- Real functional content (no empty shells)
- Responsive design meta tags
- Offline capability
- Accessibility basics
- Cross-platform compatibility
"""

import json
import re
import pytest
from pathlib import Path

BASE = Path(__file__).parent.parent / "web-apps"

APPS = [
    ("snake",       "Snake Game",         "game"),
    ("tetris",      "Tetris",             "game"),
    ("minesweeper", "Minesweeper",        "game"),
    ("echess",      "eChess",             "game"),
    ("eblocks",     "eBlocks",            "game"),
    ("dice",        "Dice",               "game"),
    ("ebirds",      "eBirds",             "game"),
    ("ecrush",      "eCrush",             "game"),
    ("evirustower", "eVirus Tower",       "game"),
    ("echat",       "eChat",              "productivity"),
    ("ecal",        "eCalendar",          "productivity"),
    ("enote",       "eNote",              "productivity"),
    ("etrack",      "eTrack",             "productivity"),
    ("etimer",      "eTimer",             "productivity"),
    ("econverter",  "eConverter",         "productivity"),
    ("eclock",      "eClock",             "productivity"),
    ("ebot",        "eBot",               "productivity"),
    ("etools",      "eTools",             "productivity"),
    ("efiles",      "eFiles",             "media"),
    ("egallery",    "eGallery",           "media"),
    ("emusic",      "eMusic",             "media"),
    ("eplay",       "ePlay",              "media"),
    ("epdf",        "ePDF",               "media"),
    ("eviewer",     "eViewer",            "media"),
    ("ezip",        "eZip",               "media"),
    ("evideo",      "eVideo",             "media"),
    ("epaint",      "ePaint",             "creative"),
    ("esurfer",     "eSurfer",            "utility"),
    ("eweb",        "eWeb",               "utility"),
    ("ebuffer",     "eBuffer",            "utility"),
    ("eride",       "eRide",              "utility"),
    ("esocial",     "eSocial",            "social"),
    ("etravel",     "eTravel",            "utility"),
]

GAME_APPS = {a[0] for a in APPS if a[2] == "game"}


@pytest.fixture(params=APPS, ids=[a[0] for a in APPS])
def app(request):
    name, title, category = request.param
    return {"name": name, "title": title, "category": category, "dir": BASE / name}


class TestPWAManifest:
    """TC-WEB-01: PWA manifest completeness and correctness."""

    def test_manifest_exists(self, app):
        assert (app["dir"] / "manifest.json").exists(), \
            f"{app['name']}: manifest.json missing"

    def test_manifest_valid_json(self, app):
        with open(app["dir"] / "manifest.json") as f:
            data = json.load(f)
        assert isinstance(data, dict)

    def test_manifest_has_name(self, app):
        with open(app["dir"] / "manifest.json") as f:
            data = json.load(f)
        assert "name" in data and len(data["name"]) > 0

    def test_manifest_has_short_name(self, app):
        with open(app["dir"] / "manifest.json") as f:
            data = json.load(f)
        assert "short_name" in data and len(data["short_name"]) <= 12, \
            f"{app['name']}: short_name missing or too long (max 12 chars)"

    def test_manifest_has_display(self, app):
        with open(app["dir"] / "manifest.json") as f:
            data = json.load(f)
        assert data.get("display") in ("standalone", "fullscreen", "minimal-ui", "browser"), \
            f"{app['name']}: invalid display mode"

    def test_manifest_has_theme_color(self, app):
        with open(app["dir"] / "manifest.json") as f:
            data = json.load(f)
        assert "theme_color" in data, f"{app['name']}: missing theme_color"
        assert re.match(r'^#[0-9a-fA-F]{6}$', data["theme_color"]), \
            f"{app['name']}: theme_color not valid hex"

    def test_manifest_has_background_color(self, app):
        with open(app["dir"] / "manifest.json") as f:
            data = json.load(f)
        assert "background_color" in data, f"{app['name']}: missing background_color"

    def test_manifest_has_icons(self, app):
        with open(app["dir"] / "manifest.json") as f:
            data = json.load(f)
        icons = data.get("icons", [])
        assert len(icons) >= 2, f"{app['name']}: need at least 2 icons in manifest"

    def test_manifest_has_start_url(self, app):
        with open(app["dir"] / "manifest.json") as f:
            data = json.load(f)
        assert "start_url" in data, f"{app['name']}: missing start_url"

    def test_manifest_has_description(self, app):
        with open(app["dir"] / "manifest.json") as f:
            data = json.load(f)
        assert "description" in data and len(data.get("description", "")) > 0, \
            f"{app['name']}: missing description"


class TestServiceWorker:
    """TC-WEB-02: Service worker for offline capability."""

    def test_sw_exists(self, app):
        assert (app["dir"] / "service-worker.js").exists(), \
            f"{app['name']}: service-worker.js missing"

    def test_sw_not_empty(self, app):
        sw = (app["dir"] / "service-worker.js").read_text()
        assert len(sw) > 50, f"{app['name']}: service-worker.js is empty"

    def test_sw_has_install_handler(self, app):
        sw = (app["dir"] / "service-worker.js").read_text()
        assert "install" in sw, f"{app['name']}: SW missing install event handler"

    def test_sw_has_fetch_handler(self, app):
        sw = (app["dir"] / "service-worker.js").read_text()
        assert "fetch" in sw, f"{app['name']}: SW missing fetch event handler"

    def test_sw_has_cache_name(self, app):
        sw = (app["dir"] / "service-worker.js").read_text()
        assert "CACHE" in sw or "cache" in sw.lower(), \
            f"{app['name']}: SW missing cache name"

    def test_sw_registered_in_html(self, app):
        html = (app["dir"] / "index.html").read_text()
        assert "serviceWorker" in html, \
            f"{app['name']}: index.html does not register service worker"


class TestHTMLStructure:
    """TC-WEB-03: HTML structure, meta tags, and accessibility."""

    def test_index_exists(self, app):
        assert (app["dir"] / "index.html").exists(), \
            f"{app['name']}: index.html missing"

    def test_html_has_lang(self, app):
        html = (app["dir"] / "index.html").read_text()
        assert 'lang=' in html, f"{app['name']}: <html> missing lang attribute"

    def test_html_has_charset(self, app):
        html = (app["dir"] / "index.html").read_text()
        assert "charset" in html.lower(), f"{app['name']}: missing charset meta"

    def test_html_has_viewport(self, app):
        html = (app["dir"] / "index.html").read_text()
        assert "viewport" in html, f"{app['name']}: missing viewport meta tag"

    def test_html_has_title(self, app):
        html = (app["dir"] / "index.html").read_text()
        assert re.search(r'<title>.+</title>', html), \
            f"{app['name']}: missing <title>"

    def test_html_has_theme_color_meta(self, app):
        html = (app["dir"] / "index.html").read_text()
        assert 'theme-color' in html, \
            f"{app['name']}: missing theme-color meta tag"

    def test_html_links_manifest(self, app):
        html = (app["dir"] / "index.html").read_text()
        assert 'manifest' in html, \
            f"{app['name']}: index.html does not link to manifest.json"

    def test_html_has_header(self, app):
        html = (app["dir"] / "index.html").read_text()
        assert '<header' in html.lower(), \
            f"{app['name']}: missing <header> element"

    def test_html_has_eos_branding(self, app):
        html = (app["dir"] / "index.html").read_text()
        assert any(brand in html for brand in ["EoS", "EmbeddedOS", "eos"]), \
            f"{app['name']}: missing EoS branding in HTML"


class TestRealContent:
    """TC-WEB-04: Real functional content — no empty shells."""

    def test_html_has_real_javascript(self, app):
        html = (app["dir"] / "index.html").read_text()
        js_indicators = [
            "function ", "addEventListener", "const ", "let ", "var ",
            "document.getElementById", "querySelector", "setInterval",
            "localStorage", "canvas", "fetch("
        ]
        has_js = any(ind in html for ind in js_indicators)
        assert has_js, \
            f"{app['name']}: index.html has no real JavaScript (empty shell)"

    def test_html_not_placeholder(self, app):
        html = (app["dir"] / "index.html").read_text()
        bad = ["Coming soon", "Under construction", "TODO", "lorem ipsum"]
        for ph in bad:
            assert ph.lower() not in html.lower(), \
                f"{app['name']}: contains placeholder text '{ph}'"

    def test_html_has_interactive_elements(self, app):
        html = (app["dir"] / "index.html").read_text()
        interactive = ["<button", "<input", "<canvas", "<select", "<textarea"]
        has_interactive = any(el in html.lower() for el in interactive)
        assert has_interactive, \
            f"{app['name']}: no interactive elements found"

    def test_html_has_css_styling(self, app):
        html = (app["dir"] / "index.html").read_text()
        assert "<style" in html or '<link rel="stylesheet"' in html, \
            f"{app['name']}: no CSS styling found"

    def test_game_has_canvas_or_grid(self, app):
        """Game apps must have a canvas or game grid."""
        if app["category"] != "game":
            pytest.skip("Not a game app")
        html = (app["dir"] / "index.html").read_text()
        assert "<canvas" in html or 'id="board"' in html or 'id="grid"' in html, \
            f"{app['name']}: game app missing canvas or grid element"

    def test_game_has_score_display(self, app):
        """Game apps must show a score or status."""
        if app["category"] != "game":
            pytest.skip("Not a game app")
        html = (app["dir"] / "index.html").read_text()
        assert any(kw in html.lower() for kw in ["score", "lives", "level", "time", "points"]), \
            f"{app['name']}: game app missing score/status display"


class TestCrossPlatform:
    """TC-WEB-05: Cross-platform compatibility (mobile, desktop, tablet)."""

    def test_responsive_viewport(self, app):
        html = (app["dir"] / "index.html").read_text()
        assert "width=device-width" in html, \
            f"{app['name']}: missing responsive viewport"

    def test_no_fixed_pixel_width_only(self, app):
        html = (app["dir"] / "index.html").read_text()
        # Should use % or vw/vh or max-width, not just fixed px for body
        has_responsive = any(unit in html for unit in [
            "100%", "100vw", "100vh", "max-width", "min-width",
            "flex", "grid", "auto"
        ])
        assert has_responsive, \
            f"{app['name']}: no responsive layout units found"

    def test_touch_events_for_games(self, app):
        """Game apps should support touch for mobile."""
        if app["category"] != "game":
            pytest.skip("Not a game app")
        html = (app["dir"] / "index.html").read_text()
        has_touch = any(ev in html for ev in [
            "touchstart", "touchmove", "touchend",
            "onclick", "ctrl-btn", "mobile"
        ])
        assert has_touch, \
            f"{app['name']}: game app missing touch/mobile controls"

    def test_html_valid_doctype(self, app):
        html = (app["dir"] / "index.html").read_text()
        assert html.strip().lower().startswith("<!doctype html"), \
            f"{app['name']}: missing or invalid DOCTYPE"

    def test_no_http_resources(self, app):
        """Should not load resources over insecure HTTP."""
        html = (app["dir"] / "index.html").read_text()
        http_resources = re.findall(r'src=["\']http://', html)
        assert len(http_resources) == 0, \
            f"{app['name']}: loads resources over HTTP (not HTTPS)"


class TestAccessibility:
    """TC-WEB-06: Basic accessibility compliance."""

    def test_buttons_have_text(self, app):
        html = (app["dir"] / "index.html").read_text()
        # Find buttons with empty content (no text, no aria-label)
        empty_btns = re.findall(r'<button[^>]*>\s*</button>', html)
        assert len(empty_btns) == 0, \
            f"{app['name']}: {len(empty_btns)} empty button(s) found"

    def test_inputs_have_placeholder_or_label(self, app):
        html = (app["dir"] / "index.html").read_text()
        inputs = re.findall(r'<input[^>]+>', html)
        for inp in inputs:
            if 'type="hidden"' in inp or 'type="color"' in inp or 'type="range"' in inp:
                continue
            has_label = any(attr in inp for attr in [
                "placeholder", "aria-label", "id=", "title="
            ])
            assert has_label, \
                f"{app['name']}: input missing placeholder/label: {inp[:80]}"

    def test_html_has_lang_attribute(self, app):
        html = (app["dir"] / "index.html").read_text()
        assert re.search(r'<html[^>]+lang=', html), \
            f"{app['name']}: <html> missing lang attribute"
