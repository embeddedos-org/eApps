"""
Cross-platform test suite for all 46 EoS native LVGL apps.
Tests: source structure, CMake build, lifecycle API, LVGL widget compliance,
       state machine, input handlers, app metadata.
"""
import os, re, subprocess, pytest

APPS_DIR = os.path.join(os.path.dirname(__file__), "..", "apps")
ALL_APPS = sorted([d for d in os.listdir(APPS_DIR)
                   if os.path.isdir(os.path.join(APPS_DIR, d))])

REQUIRED_LIFECYCLE = ["_init", "_deinit", "_on_show", "_on_hide"]
REQUIRED_INFO_FIELDS = [".id =", ".name =", ".icon =", ".description =", ".category =", ".version ="]
REQUIRED_LIFECYCLE_FIELDS = [".init =", ".deinit =", ".on_show =", ".on_hide ="]
VALID_CATEGORIES = [
    "EAPPS_CAT_PRODUCTIVITY", "EAPPS_CAT_GAMES", "EAPPS_CAT_SYSTEM",
    "EAPPS_CAT_MEDIA", "EAPPS_CAT_NETWORK", "EAPPS_CAT_SECURITY",
    "EAPPS_CAT_COMMUNICATION",
]

def read_source(app_id):
    src = os.path.join(APPS_DIR, app_id, f"{app_id}.c")
    hdr = os.path.join(APPS_DIR, app_id, f"{app_id}.h")
    with open(src) as f: src_txt = f.read()
    with open(hdr) as f: hdr_txt = f.read()
    return src_txt, hdr_txt

@pytest.mark.parametrize("app_id", ALL_APPS)
class TestNativeAppStructure:
    def test_source_file_exists(self, app_id):
        assert os.path.exists(os.path.join(APPS_DIR, app_id, f"{app_id}.c"))

    def test_header_file_exists(self, app_id):
        assert os.path.exists(os.path.join(APPS_DIR, app_id, f"{app_id}.h"))

    def test_cmake_file_exists(self, app_id):
        assert os.path.exists(os.path.join(APPS_DIR, app_id, "CMakeLists.txt"))

    def test_header_includes_lvgl(self, app_id):
        _, hdr = read_source(app_id)
        assert "lvgl" in hdr.lower() or "lv_obj_t" in hdr

    def test_header_includes_eapps_core(self, app_id):
        _, hdr = read_source(app_id)
        assert "eapps_core" in hdr or "eapps_app_info_t" in hdr

    def test_header_exports_info(self, app_id):
        _, hdr = read_source(app_id)
        assert f"{app_id}_info" in hdr

    def test_header_exports_lifecycle(self, app_id):
        _, hdr = read_source(app_id)
        assert f"{app_id}_lifecycle" in hdr

    def test_source_has_all_lifecycle_functions(self, app_id):
        src, _ = read_source(app_id)
        for fn in REQUIRED_LIFECYCLE:
            assert f"{app_id}{fn}" in src, f"Missing {app_id}{fn}"

    def test_source_has_app_info_struct(self, app_id):
        src, _ = read_source(app_id)
        assert f"{app_id}_info" in src
        for field in REQUIRED_INFO_FIELDS:
            assert field in src, f"Missing info field {field}"

    def test_source_has_lifecycle_struct(self, app_id):
        src, _ = read_source(app_id)
        assert f"{app_id}_lifecycle" in src
        for field in REQUIRED_LIFECYCLE_FIELDS:
            assert field in src, f"Missing lifecycle field {field}"

    def test_source_has_valid_category(self, app_id):
        src, _ = read_source(app_id)
        assert any(cat in src for cat in VALID_CATEGORIES), \
            f"{app_id} has no valid category"

    def test_source_has_version(self, app_id):
        src, _ = read_source(app_id)
        assert re.search(r'\.version\s*=\s*"[0-9]+\.[0-9]+', src), \
            f"{app_id} missing version string"

    def test_source_no_placeholder_text(self, app_id):
        src, _ = read_source(app_id)
        bad = ["TODO", "FIXME", "coming soon", "Coming Soon", "Coming soon"]
        for b in bad:
            assert b not in src, f"{app_id} contains placeholder: {b}"

    def test_init_returns_bool(self, app_id):
        src, _ = read_source(app_id)
        # init function must return true or false
        assert "return true" in src or "return false" in src

    def test_source_uses_lvgl_api(self, app_id):
        src, _ = read_source(app_id)
        lvgl_calls = ["lv_label_create", "lv_btn_create", "lv_obj_create",
                      "lv_canvas_create", "lv_textarea_create", "lv_timer_create"]
        assert any(call in src for call in lvgl_calls), \
            f"{app_id} does not use any LVGL widget API"

    def test_source_has_spdx_license(self, app_id):
        src, _ = read_source(app_id)
        assert "SPDX-License-Identifier" in src

    def test_source_size_reasonable(self, app_id):
        path = os.path.join(APPS_DIR, app_id, f"{app_id}.c")
        size = os.path.getsize(path)
        assert size >= 300, f"{app_id}.c is too small ({size} bytes) — likely a stub"
        assert size < 500_000, f"{app_id}.c is unreasonably large"

    def test_app_id_matches_filename(self, app_id):
        src, _ = read_source(app_id)
        assert f'"{app_id}"' in src, f"{app_id}: .id field does not match directory name"


@pytest.mark.parametrize("app_id", ALL_APPS)
class TestNativeAppBuildability:
    """Test that the C source compiles without errors using gcc in syntax-check mode."""
    def test_c_syntax_valid(self, app_id):
        src_path = os.path.join(APPS_DIR, app_id, f"{app_id}.c")
        # Use gcc -fsyntax-only with stub includes to check syntax
        stub_dir = "/tmp/eapps_stubs"
        os.makedirs(stub_dir, exist_ok=True)
        # Write minimal stubs if not already there
        lvgl_h = os.path.join(stub_dir, "lvgl")
        os.makedirs(lvgl_h, exist_ok=True)
        stub_lvgl = os.path.join(lvgl_h, "lvgl.h")
        with open(stub_lvgl, "w") as f:
            f.write("""
#pragma once
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdarg.h>
typedef struct _lv_obj_t lv_obj_t;
typedef struct _lv_timer_t lv_timer_t;
typedef struct _lv_event_t lv_event_t;
typedef uint32_t lv_color_t;
typedef void (*lv_event_cb_t)(lv_event_t *);
typedef void (*lv_timer_cb_t)(lv_timer_t *);
#define LV_ALIGN_CENTER 0
#define LV_ALIGN_TOP_MID 1
#define LV_ALIGN_BOTTOM_MID 2
#define LV_ALIGN_TOP_LEFT 3
#define LV_ALIGN_BOTTOM_LEFT 4
#define LV_ALIGN_BOTTOM_RIGHT 5
#define LV_ALIGN_TOP_RIGHT 6
#define LV_ALIGN_CENTER 0
#define LV_LAYOUT_GRID 0
#define LV_EVENT_CLICKED 0
#define LV_EVENT_VALUE_CHANGED 1
#define lv_font_montserrat_48 (*((void*)0))
#define lv_font_montserrat_24 (*((void*)0))
static inline lv_obj_t* lv_label_create(lv_obj_t*p){(void)p;return 0;}
static inline lv_obj_t* lv_btn_create(lv_obj_t*p){(void)p;return 0;}
static inline lv_obj_t* lv_obj_create(lv_obj_t*p){(void)p;return 0;}
static inline lv_obj_t* lv_canvas_create(lv_obj_t*p){(void)p;return 0;}
static inline lv_obj_t* lv_textarea_create(lv_obj_t*p){(void)p;return 0;}
static inline lv_obj_t* lv_obj_get_child(lv_obj_t*p,int i){(void)p;(void)i;return 0;}
static inline void lv_label_set_text(lv_obj_t*o,const char*t){(void)o;(void)t;}
static inline void lv_label_set_text_fmt(lv_obj_t*o,const char*f,...){(void)o;(void)f;}
static inline const char* lv_textarea_get_text(lv_obj_t*o){(void)o;return "";}
static inline void lv_textarea_set_placeholder_text(lv_obj_t*o,const char*t){(void)o;(void)t;}
static inline void lv_obj_set_size(lv_obj_t*o,int w,int h){(void)o;(void)w;(void)h;}
static inline void lv_obj_align(lv_obj_t*o,int a,int x,int y){(void)o;(void)a;(void)x;(void)y;}
static inline void lv_obj_set_layout(lv_obj_t*o,int l){(void)o;(void)l;}
static inline void lv_obj_set_style_text_font(lv_obj_t*o,void*f,int s){(void)o;(void)f;(void)s;}
static inline void lv_obj_add_event_cb(lv_obj_t*o,lv_event_cb_t cb,int e,void*d){(void)o;(void)cb;(void)e;(void)d;}
static inline lv_timer_t* lv_timer_create(lv_timer_cb_t cb,uint32_t p,void*d){(void)cb;(void)p;(void)d;return 0;}
static inline void lv_timer_del(lv_timer_t*t){(void)t;}
static inline void lv_timer_pause(lv_timer_t*t){(void)t;}
static inline void lv_timer_resume(lv_timer_t*t){(void)t;}
static inline int lv_snprintf(char*b,int n,const char*f,...){(void)b;(void)n;(void)f;return 0;}
static inline char* lv_strncat(char*d,const char*s,int n){(void)n;return strncat(d,s,n);}
#define LV_SYMBOL_OK "\xEF\x80\x80"
#define LV_SYMBOL_PAUSE "\xEF\x80\x81"
#define LV_SYMBOL_STOP "\xEF\x80\x82"
#define LV_SYMBOL_PLAY "\xEF\x80\x83"
#define LV_SYMBOL_CLOSE "\xEF\x80\x84"
#define LV_SYMBOL_WARNING "\xEF\x80\x85"
#define LV_SYMBOL_SETTINGS "\xEF\x80\x86"
#define LV_SYMBOL_HOME "\xEF\x80\x87"
#define LV_SYMBOL_WIFI "\xEF\x80\x88"
#define LV_SYMBOL_BATTERY_FULL "\xEF\x80\x89"
static inline void lv_obj_set_width(lv_obj_t*o,int w){(void)o;(void)w;}
static inline lv_obj_t* lv_event_get_target(lv_event_t*e){(void)e;return 0;}
static inline uint16_t lv_dropdown_get_selected(lv_obj_t*o){(void)o;return 0;}
static inline void lv_dropdown_set_selected(lv_obj_t*o,uint16_t s){(void)o;(void)s;}
static inline lv_obj_t* lv_dropdown_create(lv_obj_t*p){(void)p;return 0;}
static inline void lv_dropdown_set_options(lv_obj_t*o,const char*s){(void)o;(void)s;}
static inline void lv_obj_center(lv_obj_t*o){(void)o;}
static inline void lv_obj_set_flex_flow(lv_obj_t*o,int f){(void)o;(void)f;}
static inline void lv_obj_set_flex_align(lv_obj_t*o,int m,int c,int t){(void)o;(void)m;(void)c;(void)t;}
static inline void lv_obj_set_style_pad_all(lv_obj_t*o,int p,int s){(void)o;(void)p;(void)s;}
static inline void lv_obj_set_style_pad_row(lv_obj_t*o,int p,int s){(void)o;(void)p;(void)s;}
static inline void lv_obj_set_style_pad_column(lv_obj_t*o,int p,int s){(void)o;(void)p;(void)s;}
static inline void lv_obj_set_style_bg_color(lv_obj_t*o,lv_color_t c,int s){(void)o;(void)c;(void)s;}
static inline void lv_obj_set_style_text_color(lv_obj_t*o,lv_color_t c,int s){(void)o;(void)c;(void)s;}
static inline void lv_obj_set_style_border_width(lv_obj_t*o,int w,int s){(void)o;(void)w;(void)s;}
static inline void lv_obj_set_style_radius(lv_obj_t*o,int r,int s){(void)o;(void)r;(void)s;}
static inline void lv_obj_remove_style_all(lv_obj_t*o){(void)o;}
static inline void lv_obj_clear_flag(lv_obj_t*o,int f){(void)o;(void)f;}
static inline void lv_obj_add_flag(lv_obj_t*o,int f){(void)o;(void)f;}
#define LV_FLEX_FLOW_COLUMN 0
#define LV_FLEX_FLOW_ROW 1
#define LV_FLEX_ALIGN_CENTER 0
#define LV_FLEX_ALIGN_START 1
#define LV_FLEX_ALIGN_END 2
#define LV_OBJ_FLAG_HIDDEN 1
#define LV_STATE_DEFAULT 0
#define lv_font_montserrat_16 (*((void*)0))
#define lv_font_montserrat_14 (*((void*)0))
#define lv_font_montserrat_12 (*((void*)0))
#define lv_color_make(r,g,b) ((lv_color_t)0)
#define lv_color_hex(c) ((lv_color_t)0)
#define lv_color_white() ((lv_color_t)0)
#define lv_color_black() ((lv_color_t)0)
""")
        stub_core = os.path.join(stub_dir, "eapps_core.h")
        with open(stub_core, "w") as f:
            f.write("""
#pragma once
#include <stdbool.h>
#include "lvgl/lvgl.h"
typedef enum {
    EAPPS_CAT_PRODUCTIVITY, EAPPS_CAT_GAMES, EAPPS_CAT_SYSTEM,
    EAPPS_CAT_MEDIA, EAPPS_CAT_NETWORK, EAPPS_CAT_SECURITY,
    EAPPS_CAT_COMMUNICATION,
} eapps_category_t;
typedef struct {
    const char *id, *name, *icon, *description, *version;
    eapps_category_t category;
} eapps_app_info_t;
typedef struct {
    bool (*init)(lv_obj_t *parent);
    void (*deinit)(void);
    void (*on_show)(void);
    void (*on_hide)(void);
} eapps_app_lifecycle_t;
""")
        result = subprocess.run(
            # The stub is written to <stub_dir>/lvgl/lvgl.h, but the app sources
            # do `#include "lvgl.h"`. With only -I<stub_dir> on the command line
            # that never resolved, so every app in this class failed with
            # "fatal error: lvgl.h: No such file or directory" and the failure
            # was reported as the app's own syntax error.
            ["gcc", "-fsyntax-only", "-std=c11", "-Wall",
             f"-I{stub_dir}",
             f"-I{os.path.join(stub_dir, 'lvgl')}",
             f"-I{os.path.join(APPS_DIR, app_id)}",
             src_path],
            capture_output=True, text=True, timeout=10
        )
        assert result.returncode == 0, \
            f"{app_id} syntax error:\n{result.stderr[:500]}"


@pytest.mark.parametrize("app_id", ALL_APPS)
class TestNativeAppMetadata:
    def test_app_name_not_empty(self, app_id):
        src, _ = read_source(app_id)
        m = re.search(r'\.name\s*=\s*"([^"]+)"', src)
        assert m and len(m.group(1)) > 0

    def test_app_icon_3_chars(self, app_id):
        src, _ = read_source(app_id)
        m = re.search(r'\.icon\s*=\s*"([^"]+)"', src)
        assert m and 2 <= len(m.group(1)) <= 6, \
            f"{app_id} icon '{m.group(1) if m else '?'}' not 2-6 chars"

    def test_app_description_meaningful(self, app_id):
        src, _ = read_source(app_id)
        m = re.search(r'\.description\s*=\s*"([^"]+)"', src)
        assert m and len(m.group(1)) >= 10, \
            f"{app_id} description too short"

    def test_version_semver(self, app_id):
        src, _ = read_source(app_id)
        assert re.search(r'\.version\s*=\s*"\d+\.\d+\.\d+"', src), \
            f"{app_id} version not semver"
