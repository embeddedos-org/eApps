"""SVG format exporter for EoStudio 2D shapes."""
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional


class SVGExporter:
    """Export 2D shapes to SVG format."""

    def export(
        self,
        shapes: List[Dict[str, Any]],
        width: int = 800,
        height: int = 600,
    ) -> str:
        """Export shapes to an SVG string."""
        lines = [
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}">'
        ]
        for shape in shapes:
            shape_type = shape.get("type", "")
            if shape_type == "rect":
                x = shape.get("x", 0)
                y = shape.get("y", 0)
                w = shape.get("width", 100)
                h = shape.get("height", 100)
                fill = shape.get("fill", "none")
                stroke = shape.get("stroke", "black")
                lines.append(
                    f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" '
                    f'fill="{fill}" stroke="{stroke}" />'
                )
            elif shape_type == "circle":
                cx = shape.get("cx", 0)
                cy = shape.get("cy", 0)
                r = shape.get("r", 50)
                fill = shape.get("fill", "none")
                stroke = shape.get("stroke", "black")
                lines.append(
                    f'  <circle cx="{cx}" cy="{cy}" r="{r}" '
                    f'fill="{fill}" stroke="{stroke}" />'
                )
            elif shape_type == "line":
                x1 = shape.get("x1", 0)
                y1 = shape.get("y1", 0)
                x2 = shape.get("x2", 100)
                y2 = shape.get("y2", 100)
                stroke = shape.get("stroke", "black")
                lines.append(
                    f'  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
                    f'stroke="{stroke}" />'
                )
            elif shape_type == "text":
                x = shape.get("x", 0)
                y = shape.get("y", 0)
                content = shape.get("content", "")
                fill = shape.get("fill", "black")
                lines.append(f'  <text x="{x}" y="{y}" fill="{fill}">{content}</text>')
        lines.append("</svg>")
        return "\n".join(lines)

    def export_to_file(
        self,
        shapes: List[Dict[str, Any]],
        filepath: str,
        width: int = 800,
        height: int = 600,
    ) -> None:
        """Export shapes to an SVG file."""
        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
        content = self.export(shapes, width=width, height=height)
        with open(filepath, "w", encoding="utf-8") as fh:
            fh.write(content)
