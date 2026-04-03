"""WebAssembly code generator for EoStudio UI components.

Supported targets: wasm-rust (Rust + wasm-bindgen),
wasm-assemblyscript (AssemblyScript).
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List


class WasmGenerator:
    """Generates WASM application source files from EoStudio screens."""

    SUPPORTED_TARGETS = ("wasm-rust", "wasm-assemblyscript")

    def __init__(self, target: str = "wasm-rust") -> None:
        if target not in self.SUPPORTED_TARGETS:
            raise ValueError(f"Unknown target {target!r}")
        self._target = target

    def generate(self, screens: List[Dict[str, Any]],
                 app_name: str = "EoStudioApp") -> Dict[str, str]:
        if not screens:
            screens = [{"name": "Home", "components": []}]
        if self._target == "wasm-rust":
            return self._gen_rust(screens, app_name)
        return self._gen_assemblyscript(screens, app_name)

    def _gen_rust(self, screens: List[Dict[str, Any]],
                  app_name: str) -> Dict[str, str]:
        files: Dict[str, str] = {}
        snake = self._snake(app_name)

        files["Cargo.toml"] = (
            f'[package]\nname = "{snake}"\nversion = "0.1.0"\n'
            'edition = "2021"\n\n'
            '[lib]\ncrate-type = ["cdylib"]\n\n'
            '[dependencies]\n'
            'wasm-bindgen = "0.2"\n'
            'web-sys = { version = "0.3", features = [\n'
            '    "Document", "Element", "HtmlElement",\n'
            '    "HtmlInputElement", "HtmlButtonElement",\n'
            '    "Window", "Node", "Event",\n'
            '] }\n')

        render_fns: List[str] = []
        for s in screens:
            name = self._snake(s.get("name", "Home"))
            label = s.get("name", "Home")
            body = self._rust_elements(s.get("components", []), 1)
            render_fns.append(
                f'fn render_{name}(doc: &Document, container: &Element) {{\n'
                f'    let h = doc.create_element("h2").unwrap();\n'
                f'    h.set_text_content(Some("{label}"));\n'
                f'    container.append_child(&h).unwrap();\n'
                f'{body}}}\n')

        first = self._snake(screens[0].get("name", "Home"))
        files["src/lib.rs"] = (
            'use wasm_bindgen::prelude::*;\n'
            'use web_sys::Document;\n\n'
            '#[wasm_bindgen(start)]\n'
            'pub fn main() {\n'
            '    let window = web_sys::window().unwrap();\n'
            '    let doc = window.document().unwrap();\n'
            '    let body = doc.body().unwrap();\n'
            '    let container = doc.create_element("div").unwrap();\n'
            '    container.set_attribute("class", "app").unwrap();\n'
            f'    render_{first}(&doc, &container);\n'
            '    body.append_child(&container).unwrap();\n'
            '}\n\n'
            + "\n".join(render_fns))

        files["index.html"] = (
            '<!DOCTYPE html>\n<html><head><meta charset="UTF-8">\n'
            f'<title>{app_name}</title>\n'
            '<style>body{font-family:sans-serif;margin:0;padding:16px}'
            '.app{max-width:800px;margin:0 auto}'
            'button{padding:8px 16px;margin:4px;cursor:pointer}'
            'input{padding:8px;margin:4px;width:100%;box-sizing:border-box}'
            '</style></head><body>\n'
            '<script type="module">\n'
            f"import init from './{snake}.js';\n"
            'init();\n</script></body></html>\n')
        return files

    def _rust_elements(self, components: List[Dict[str, Any]],
                       indent: int) -> str:
        lines: List[str] = []
        pad = "    " * indent
        for i, c in enumerate(components):
            ct = c.get("type", "Container")
            lb = c.get("label", c.get("text", ""))
            vn = f"el{i}"
            if ct == "Button":
                lines.append(
                    f'{pad}let {vn} = doc.create_element("button").unwrap();\n'
                    f'{pad}{vn}.set_text_content(Some("{lb}"));\n'
                    f'{pad}container.append_child(&{vn}).unwrap();\n')
            elif ct == "Text":
                lines.append(
                    f'{pad}let {vn} = doc.create_element("p").unwrap();\n'
                    f'{pad}{vn}.set_text_content(Some("{lb}"));\n'
                    f'{pad}container.append_child(&{vn}).unwrap();\n')
            elif ct == "Input":
                lines.append(
                    f'{pad}let {vn} = doc.create_element("input").unwrap();\n'
                    f'{pad}{vn}.set_attribute("placeholder", "{lb}").unwrap();\n'
                    f'{pad}container.append_child(&{vn}).unwrap();\n')
            elif ct == "Card":
                lines.append(
                    f'{pad}let {vn} = doc.create_element("div").unwrap();\n'
                    f'{pad}{vn}.set_attribute("class", "card").unwrap();\n'
                    f'{pad}container.append_child(&{vn}).unwrap();\n')
            else:
                lines.append(
                    f'{pad}let {vn} = doc.create_element("div").unwrap();\n'
                    f'{pad}{vn}.set_text_content(Some("{lb}"));\n'
                    f'{pad}container.append_child(&{vn}).unwrap();\n')
        return "".join(lines)

    def _gen_assemblyscript(self, screens: List[Dict[str, Any]],
                            app_name: str) -> Dict[str, str]:
        files: Dict[str, str] = {}
        snake = self._snake(app_name)

        files["package.json"] = json.dumps({
            "name": snake, "version": "0.1.0",
            "scripts": {"asbuild": "asc assembly/index.ts -o build/app.wasm"},
            "devDependencies": {"assemblyscript": "^0.27.0"},
        }, indent=2) + "\n"

        body_lines: List[str] = []
        for s in screens:
            label = s.get("name", "Home")
            body_lines.append(f'  trace("{label} screen loaded");')
            for c in s.get("components", []):
                ct = c.get("type", "Container")
                lb = c.get("label", c.get("text", ""))
                if ct == "Button":
                    body_lines.append(f'  trace("Button: {lb}");')
                elif ct == "Text":
                    body_lines.append(f'  trace("Text: {lb}");')
                elif ct == "Input":
                    body_lines.append(f'  trace("Input: {lb}");')

        files["assembly/index.ts"] = (
            'export function main(): void {\n'
            + "\n".join(body_lines) + "\n"
            '}\n\nmain();\n')

        files["index.html"] = (
            '<!DOCTYPE html>\n<html><head><meta charset="UTF-8">\n'
            f'<title>{app_name}</title></head><body>\n'
            '<script>\n'
            'fetch("build/app.wasm")\n'
            '  .then(r => r.arrayBuffer())\n'
            '  .then(b => WebAssembly.instantiate(b, {\n'
            '    env: { trace: (msg) => console.log(msg) }\n'
            '  }))\n'
            '  .then(m => m.instance.exports.main());\n'
            '</script></body></html>\n')
        return files

    @staticmethod
    def _snake(name: str) -> str:
        return re.sub(r"[\s\-]+", "_", name).lower()

    @staticmethod
    def _pascal(name: str) -> str:
        return "".join(w.capitalize() for w in re.split(r"[\s_\-]+", name) if w)
