#!/usr/bin/env python3
"""Validate eApps data/apps.json against the marketplace metadata rules.

Stdlib-only so it runs in CI without extra dependencies. Mirrors
schemas/app-metadata.schema.json; the schema is the contract, this script
is the executable check (uniqueness and cross-references need code).

Usage: python3 scripts/validate_apps.py [path/to/apps.json] [path/to/registry.json]
Exit 0 when valid, 1 with a list of violations otherwise.

The ai-capabilities registry (schemas/ai-capabilities.registry.json) is the
curated vocabulary of capability names. Unknown names are rejected
(fail-closed); pass an explicit registry path for testing.
"""
import json
import re
import sys
from pathlib import Path

APP_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
AI_CAP_RE = re.compile(r"^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)*$")
AI_CAP_LEVELS = ("none", "read", "write", "readwrite")
VERSION_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+")


def default_registry_path():
    return (Path(__file__).resolve().parent.parent
            / "schemas" / "ai-capabilities.registry.json")


def load_registry(path=None):
    """Load the curated ai_capabilities vocabulary.

    Returns the name -> entry dict from the registry. Raises OSError when the
    file cannot be read and ValueError when it has no 'capabilities' object.
    """
    p = Path(path) if path else default_registry_path()
    with open(p, encoding="utf-8") as f:
        data = json.load(f)
    caps = data.get("capabilities")
    if not isinstance(caps, dict):
        raise ValueError(f"registry {p} has no 'capabilities' object")
    return caps


def _is_text(value):
    """A non-empty string: the schema's {"type": "string", "minLength": 1}."""
    return isinstance(value, str) and value != ""


def validate(data, registry=None):
    errors = []
    if not isinstance(data, dict):
        return ["top level must be an object"]

    if registry is None:
        try:
            registry = load_registry()
        except (OSError, ValueError) as e:
            errors.append(f"could not load ai-capabilities registry: {e}")
            registry = {}

    for key in ("meta", "categories", "apps"):
        if key not in data:
            errors.append(f"missing required top-level key: {key}")

    meta = data.get("meta")
    if not isinstance(meta, dict):
        if meta is not None:
            errors.append("meta must be an object")
        meta = {}
    if not isinstance(meta.get("total_apps"), int):
        errors.append("meta.total_apps must be an integer")

    categories = data.get("categories") or []
    cat_ids = set()
    for i, c in enumerate(categories):
        if not isinstance(c, dict):
            errors.append(f"categories[{i}] must be an object")
            continue
        if not c.get("id"):
            errors.append(f"categories[{i}] missing id")
        elif not isinstance(c["id"], str):
            errors.append(f"categories[{i}] id must be a string")
        elif c["id"] in cat_ids:
            errors.append(f"duplicate category id: {c['id']!r}")
        else:
            cat_ids.add(c["id"])
        if not c.get("name"):
            errors.append(f"categories[{i}] missing name")
        elif not isinstance(c["name"], str):
            errors.append(f"categories[{i}] name must be a string")

    apps = data.get("apps") or []
    seen_ids = set()
    for i, a in enumerate(apps):
        where = f"apps[{i}]"
        if not isinstance(a, dict):
            errors.append(f"{where} must be an object")
            continue
        aid = a.get("id")
        if not aid:
            errors.append(f"{where} missing id")
        elif not isinstance(aid, str) or not APP_ID_RE.fullmatch(aid):
            errors.append(f"{where} id {aid!r} must be lowercase slug")
        elif aid in seen_ids:
            errors.append(f"duplicate app id: {aid!r}")
        else:
            seen_ids.add(aid)
        if not a.get("name"):
            errors.append(f"{where} ({aid}) missing name")
        elif not isinstance(a["name"], str):
            errors.append(f"{where} ({aid}) name must be a string")
        cat = a.get("category")
        if not cat:
            errors.append(f"{where} ({aid}) missing category")
        elif not isinstance(cat, str):
            errors.append(f"{where} ({aid}) category must be a string")
        elif cat_ids and cat not in cat_ids:
            errors.append(f"{where} ({aid}) unknown category {cat!r}")
        ver = a.get("version")
        if ver is not None and not VERSION_RE.match(str(ver)):
            errors.append(f"{where} ({aid}) bad version {ver!r}")
        plats = a.get("platform")
        if plats is not None and (not isinstance(plats, list) or not plats):
            errors.append(f"{where} ({aid}) platform must be a non-empty list")
        elif plats is not None and not all(_is_text(p) for p in plats):
            errors.append(
                f"{where} ({aid}) platform entries must be non-empty strings")
        tags = a.get("tags")
        if tags is not None and not isinstance(tags, list):
            errors.append(f"{where} ({aid}) tags must be a list")
        elif tags is not None and not all(_is_text(t) for t in tags):
            errors.append(f"{where} ({aid}) tags must be non-empty strings")
        ts = a.get("test_status")
        if ts is not None and ts not in ("passing", "failing", "unknown"):
            errors.append(f"{where} ({aid}) bad test_status {ts!r}")
        caps = a.get("ai_capabilities")
        if caps is not None:
            if not isinstance(caps, dict):
                errors.append(f"{where} ({aid}) ai_capabilities must be an object")
            else:
                for k, v in caps.items():
                    if not AI_CAP_RE.match(k):
                        errors.append(f"{where} ({aid}) bad ai_capability name {k!r}")
                    elif k not in registry:
                        errors.append(
                            f"{where} ({aid}) unknown ai_capability {k!r} "
                            "(not in ai-capabilities.registry.json)")
                    if v not in AI_CAP_LEVELS:
                        errors.append(
                            f"{where} ({aid}) bad ai_capability level {v!r} for {k!r}")

    if isinstance(meta.get("total_apps"), int) and meta["total_apps"] != len(apps):
        errors.append(
            f"meta.total_apps={meta['total_apps']} != actual {len(apps)} apps"
        )
    return errors


def main(path="data/apps.json", registry_path=None):
    try:
        registry = load_registry(registry_path)
    except (OSError, ValueError) as e:
        print(f"registry error: {e}")
        return 1
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    errors = validate(data, registry)
    if errors:
        print(f"{len(errors)} violation(s) in {path}:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"OK: {path} — {len(data['apps'])} apps, "
          f"{len(data['categories'])} categories valid")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "data/apps.json",
                  sys.argv[2] if len(sys.argv) > 2 else None))
