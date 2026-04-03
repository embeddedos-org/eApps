"""HTML/CSS code generator for EoStudio UI components."""

from __future__ import annotations

from typing import Any, Dict, List


class HTMLCSSGenerator:
    """Generates HTML + CSS source files from eostudio component trees.

    Component type mapping:
    - ``Button``    -> ``<button>``
    - ``Text``      -> ``<p>``
    - ``Heading``   -> ``<h1>``
    - ``Input``     -> ``<input>``
    - ``TextArea``  -> ``<textarea>``
    - ``Image``     -> ``<img>``
    - ``Container`` -> ``<div class="container">``
    - ``Card``      -> ``<div class="card">``
    - ``Link``      -> ``<a>``
    """

    def generate(
        self,
        components: List[Dict[str, Any]],
        screens: List[Dict[str, Any]],
    ) -> Dict[str, str]:
        """Generate HTML/CSS source files.

        Args:
            components: Flat list of component dicts.
            screens: List of screen dicts with ``name`` and ``components``.

        Returns:
            Mapping of filename -> HTML/CSS source content.
        """
        files: Dict[str, str] = {}

        files["styles.css"] = self._generate_css()
        files["index.html"] = self._generate_page("EoStudio App", components)

        if screens:
            for screen in screens:
                sname = screen.get("name", "Home")
                fname = sname.lower().replace(" ", "_").replace("-", "_")
                screen_comps = screen.get("components", components)
                files[f"{fname}.html"] = self._generate_page(sname, screen_comps)

        return files

    def _generate_page(self, title: str, components: List[Dict[str, Any]]) -> str:
        body = self._render_components(components, indent=3)
        return (
            "<!DOCTYPE html>\n"
            '<html lang="en">\n'
            "<head>\n"
            '  <meta charset="UTF-8">\n'
            '  <meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
            f"  <title>{title}</title>\n"
            '  <link rel="stylesheet" href="styles.css">\n'
            "</head>\n"
            "<body>\n"
            '  <div class="app">\n'
            f'    <h1 class="app-title">{title}</h1>\n'
            '    <main class="main-content">\n'
            f"{body}"
            "    </main>\n"
            "  </div>\n"
            "</body>\n"
            "</html>\n"
        )

    def _render_components(self, components: List[Dict[str, Any]], indent: int) -> str:
        lines: List[str] = []
        pad = "  " * indent

        for comp in components:
            ctype = comp.get("type", "Container")
            label = comp.get("label", comp.get("text", ""))
            children = comp.get("children", [])

            if ctype == "Button":
                lines.append(f'{pad}<button class="btn">{label}</button>\n')
            elif ctype == "Heading":
                level = comp.get("level", 1)
                lines.append(f"{pad}<h{level}>{label}</h{level}>\n")
            elif ctype == "Text":
                lines.append(f"{pad}<p>{label}</p>\n")
            elif ctype == "Input":
                placeholder = comp.get("placeholder", label)
                lines.append(
                    f'{pad}<input type="text" class="input" '
                    f'placeholder="{placeholder}" />\n'
                )
            elif ctype == "TextArea":
                lines.append(
                    f'{pad}<textarea class="textarea" '
                    f'placeholder="{label}"></textarea>\n'
                )
            elif ctype == "Image":
                src = comp.get("src", "")
                lines.append(f'{pad}<img src="{src}" alt="{label}" class="image" />\n')
            elif ctype == "Card":
                child_body = (
                    self._render_components(children, indent + 1)
                    if children
                    else f"{pad}  <p>{label}</p>\n"
                )
                lines.append(
                    f'{pad}<div class="card">\n'
                    f"{child_body}"
                    f"{pad}</div>\n"
                )
            elif ctype == "Container" and children:
                direction = comp.get("direction", "column")
                cls = "flex-row" if direction == "row" else "flex-col"
                child_body = self._render_components(children, indent + 1)
                lines.append(
                    f'{pad}<div class="container {cls}">\n'
                    f"{child_body}"
                    f"{pad}</div>\n"
                )
            elif ctype == "Link":
                href = comp.get("href", "#")
                lines.append(f'{pad}<a href="{href}" class="link">{label}</a>\n')
            else:
                lines.append(f"{pad}<p>{label}</p>\n")

        return "".join(lines)

    def _generate_css(self) -> str:
        return (
            "/* EoStudio Generated Styles */\n"
            "*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }\n\n"
            "body {\n"
            "  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;\n"
            "  line-height: 1.6;\n"
            "  color: #333;\n"
            "  background: #f5f5f5;\n"
            "}\n\n"
            ".app {\n"
            "  display: flex;\n"
            "  flex-direction: column;\n"
            "  min-height: 100vh;\n"
            "  max-width: 1200px;\n"
            "  margin: 0 auto;\n"
            "  padding: 24px;\n"
            "}\n\n"
            ".main-content {\n"
            "  display: flex;\n"
            "  flex-direction: column;\n"
            "  gap: 16px;\n"
            "}\n\n"
            ".flex-row { display: flex; flex-direction: row; gap: 12px; flex-wrap: wrap; }\n"
            ".flex-col { display: flex; flex-direction: column; gap: 12px; }\n\n"
            ".card {\n"
            "  background: #fff; border-radius: 8px; padding: 16px;\n"
            "  box-shadow: 0 2px 8px rgba(0,0,0,0.1);\n"
            "}\n\n"
            ".btn {\n"
            "  padding: 10px 20px; border: none; border-radius: 6px;\n"
            "  background: #2563eb; color: #fff; font-size: 14px; cursor: pointer;\n"
            "}\n"
            ".btn:hover { background: #1d4ed8; }\n\n"
            ".input, .textarea {\n"
            "  width: 100%; padding: 10px 12px;\n"
            "  border: 1px solid #d1d5db; border-radius: 6px; font-size: 14px;\n"
            "}\n"
            ".input:focus, .textarea:focus {\n"
            "  outline: none; border-color: #2563eb;\n"
            "  box-shadow: 0 0 0 3px rgba(37,99,235,0.1);\n"
            "}\n\n"
            ".image { max-width: 100%; border-radius: 8px; }\n\n"
            "@media (max-width: 768px) {\n"
            "  .app { padding: 12px; }\n"
            "  .flex-row { flex-direction: column; }\n"
            "}\n"
        )
