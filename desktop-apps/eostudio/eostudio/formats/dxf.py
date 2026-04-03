"""DXF format handler for CAD sketch entities in EoStudio.

Supports LINE, CIRCLE, ARC, and POINT entities in a minimal
DXF R12-compatible format with HEADER and ENTITIES sections.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List


def export_dxf(entities: List[Dict[str, Any]], filepath: str) -> None:
    """Export a list of CAD entity dicts to a minimal DXF file.

    Supported entity types and their required keys:

    - ``LINE``:   ``x1, y1, z1, x2, y2, z2``
    - ``CIRCLE``: ``cx, cy, cz, radius``
    - ``ARC``:    ``cx, cy, cz, radius, start_angle, end_angle`` (degrees)
    - ``POINT``:  ``x, y, z``

    Args:
        entities: Ordered list of entity dictionaries.
        filepath: Destination ``.dxf`` file path.
    """
    os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
    lines: List[str] = []

    # HEADER section
    lines.extend([
        "0", "SECTION",
        "2", "HEADER",
        "9", "$ACADVER",
        "1", "AC1009",
        "0", "ENDSEC",
    ])

    # TABLES section (minimal layer table)
    lines.extend([
        "0", "SECTION",
        "2", "TABLES",
        "0", "TABLE",
        "2", "LAYER",
        "70", "1",
        "0", "LAYER",
        "2", "0",
        "70", "0",
        "62", "7",
        "6", "CONTINUOUS",
        "0", "ENDTAB",
        "0", "ENDSEC",
    ])

    # ENTITIES section
    lines.extend(["0", "SECTION", "2", "ENTITIES"])

    for ent in entities:
        etype = ent.get("type", "").upper()

        if etype == "LINE":
            lines.extend([
                "0", "LINE",
                "8", ent.get("layer", "0"),
                "10", str(float(ent.get("x1", 0))),
                "20", str(float(ent.get("y1", 0))),
                "30", str(float(ent.get("z1", 0))),
                "11", str(float(ent.get("x2", 0))),
                "21", str(float(ent.get("y2", 0))),
                "31", str(float(ent.get("z2", 0))),
            ])

        elif etype == "CIRCLE":
            lines.extend([
                "0", "CIRCLE",
                "8", ent.get("layer", "0"),
                "10", str(float(ent.get("cx", 0))),
                "20", str(float(ent.get("cy", 0))),
                "30", str(float(ent.get("cz", 0))),
                "40", str(float(ent.get("radius", 1))),
            ])

        elif etype == "ARC":
            lines.extend([
                "0", "ARC",
                "8", ent.get("layer", "0"),
                "10", str(float(ent.get("cx", 0))),
                "20", str(float(ent.get("cy", 0))),
                "30", str(float(ent.get("cz", 0))),
                "40", str(float(ent.get("radius", 1))),
                "50", str(float(ent.get("start_angle", 0))),
                "51", str(float(ent.get("end_angle", 360))),
            ])

        elif etype == "POINT":
            lines.extend([
                "0", "POINT",
                "8", ent.get("layer", "0"),
                "10", str(float(ent.get("x", 0))),
                "20", str(float(ent.get("y", 0))),
                "30", str(float(ent.get("z", 0))),
            ])

    lines.extend(["0", "ENDSEC"])

    # EOF
    lines.extend(["0", "EOF"])

    with open(filepath, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


def import_dxf(filepath: str) -> List[Dict[str, Any]]:
    """Import entities from a minimal DXF file.

    Parses the ENTITIES section and returns dicts for LINE, CIRCLE,
    ARC, and POINT entities.

    Args:
        filepath: Path to the ``.dxf`` file.

    Returns:
        A list of entity dictionaries.
    """
    with open(filepath, "r", encoding="utf-8") as fh:
        raw_lines = [line.strip() for line in fh.readlines()]

    entities: List[Dict[str, Any]] = []
    in_entities = False
    i = 0

    while i < len(raw_lines) - 1:
        code = raw_lines[i]
        value = raw_lines[i + 1]

        if code == "2" and value == "ENTITIES":
            in_entities = True
            i += 2
            continue

        if in_entities and code == "0" and value == "ENDSEC":
            break

        if in_entities and code == "0" and value in ("LINE", "CIRCLE", "ARC", "POINT"):
            entity = _parse_entity(raw_lines, i)
            if entity:
                entities.append(entity)
            i = _skip_entity(raw_lines, i + 2)
            continue

        i += 2

    return entities


def _parse_entity(lines: List[str], start: int) -> Dict[str, Any]:
    """Parse a single entity starting at *start*."""
    etype = lines[start + 1]
    result: Dict[str, Any] = {"type": etype}
    i = start + 2
    group_map: Dict[str, float] = {}

    while i < len(lines) - 1:
        code = lines[i]
        value = lines[i + 1]

        if code == "0":
            break

        if code == "8":
            result["layer"] = value
        else:
            try:
                group_map[code] = float(value)
            except ValueError:
                pass

        i += 2

    if etype == "LINE":
        result.update({
            "x1": group_map.get("10", 0.0),
            "y1": group_map.get("20", 0.0),
            "z1": group_map.get("30", 0.0),
            "x2": group_map.get("11", 0.0),
            "y2": group_map.get("21", 0.0),
            "z2": group_map.get("31", 0.0),
        })
    elif etype == "CIRCLE":
        result.update({
            "cx": group_map.get("10", 0.0),
            "cy": group_map.get("20", 0.0),
            "cz": group_map.get("30", 0.0),
            "radius": group_map.get("40", 1.0),
        })
    elif etype == "ARC":
        result.update({
            "cx": group_map.get("10", 0.0),
            "cy": group_map.get("20", 0.0),
            "cz": group_map.get("30", 0.0),
            "radius": group_map.get("40", 1.0),
            "start_angle": group_map.get("50", 0.0),
            "end_angle": group_map.get("51", 360.0),
        })
    elif etype == "POINT":
        result.update({
            "x": group_map.get("10", 0.0),
            "y": group_map.get("20", 0.0),
            "z": group_map.get("30", 0.0),
        })

    return result


def _skip_entity(lines: List[str], start: int) -> int:
    """Advance past group codes until the next entity (code 0)."""
    i = start
    while i < len(lines) - 1:
        if lines[i] == "0":
            return i
        i += 2
    return i


class DXFExporter:
    """Class-based wrapper for DXF export operations."""

    def export(self, entities: List[Dict[str, Any]]) -> str:
        """Export entities to a DXF-formatted string."""
        lines: List[str] = []
        lines.extend([
            "0", "SECTION",
            "2", "HEADER",
            "9", "$ACADVER",
            "1", "AC1009",
            "0", "ENDSEC",
        ])
        lines.extend(["0", "SECTION", "2", "ENTITIES"])
        for ent in entities:
            etype = ent.get("type", "").upper()
            if etype == "LINE":
                start = ent.get("start", [0, 0])
                end = ent.get("end", [0, 0])
                x1 = float(start[0]) if len(start) > 0 else 0.0
                y1 = float(start[1]) if len(start) > 1 else 0.0
                x2 = float(end[0]) if len(end) > 0 else 0.0
                y2 = float(end[1]) if len(end) > 1 else 0.0
                lines.extend([
                    "0", "LINE",
                    "8", ent.get("layer", "0"),
                    "10", str(x1), "20", str(y1), "30", "0.0",
                    "11", str(x2), "21", str(y2), "31", "0.0",
                ])
            elif etype == "CIRCLE":
                center = ent.get("center", [0, 0])
                cx = float(center[0]) if len(center) > 0 else 0.0
                cy = float(center[1]) if len(center) > 1 else 0.0
                radius = float(ent.get("radius", 1))
                lines.extend([
                    "0", "CIRCLE",
                    "8", ent.get("layer", "0"),
                    "10", str(cx), "20", str(cy), "30", "0.0",
                    "40", str(radius),
                ])
            elif etype == "ARC":
                center = ent.get("center", [0, 0])
                cx = float(center[0]) if len(center) > 0 else 0.0
                cy = float(center[1]) if len(center) > 1 else 0.0
                radius = float(ent.get("radius", 1))
                lines.extend([
                    "0", "ARC",
                    "8", ent.get("layer", "0"),
                    "10", str(cx), "20", str(cy), "30", "0.0",
                    "40", str(radius),
                    "50", str(float(ent.get("start_angle", 0))),
                    "51", str(float(ent.get("end_angle", 360))),
                ])
        lines.extend(["0", "ENDSEC"])
        lines.extend(["0", "EOF"])
        return "\n".join(lines)
