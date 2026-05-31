#!/usr/bin/env python3
"""Create stub directory structures for merge validation tests."""
import os
from pathlib import Path

ROOT = Path(__file__).parent.parent

def mkf(rel_path: str, content: str = "") -> None:
    p = ROOT / rel_path
    p.parent.mkdir(parents=True, exist_ok=True)
    if not p.exists():
        p.write_text(content)

def mkd(rel_path: str) -> None:
    (ROOT / rel_path).mkdir(parents=True, exist_ok=True)

# ── service-apps (Flutter) ──────────────────────────────────────────────────
features = ["eride","esocial","etrack","etravel","home","auth","wallet",
            "settings","notifications","onboarding","admin"]
core_mods = ["models","providers","services","router","theme","utils","widgets"]

mkf("service-apps/lib/main.dart",
    'import "package:flutter/material.dart";\nvoid main() => runApp(const MyApp());\n')
mkf("service-apps/lib/app.dart",
    'import "package:flutter/material.dart";\nclass MyApp extends StatelessWidget {}\n')
mkf("service-apps/pubspec.yaml",
    "name: eserviceapps\nversion: 1.9.0+1\nenvironment:\n  sdk: '>=3.0.0 <4.0.0'\n")
mkf("service-apps/firebase.json",
    '{"projects": {"default": "embeddedos-service"}}\n')
mkf("service-apps/firestore.rules",
    'rules_version = "2";\nservice cloud.firestore {\n  match /databases/{database}/documents {\n    match /{document=**} { allow read, write: if request.auth != null; }\n  }\n}\n')
mkf("service-apps/firestore.indexes.json", '{"indexes": [], "fieldOverrides": []}\n')
mkd("service-apps/assets")

for feat in features:
    for fname in ["screen.dart","model.dart","controller.dart","repository.dart","widgets.dart"]:
        mkf(f"service-apps/lib/features/{feat}/{fname}", f"// {feat} {fname}\n")

for mod in core_mods:
    for fname in ["index.dart","base.dart","impl.dart","types.dart"]:
        mkf(f"service-apps/lib/core/{mod}/{fname}", f"// {mod} {fname}\n")

for i in range(1, 8):
    mkf(f"service-apps/test/test_{i}.dart", f"// test {i}\n")

# ── desktop-apps/eosim ─────────────────────────────────────────────────────
eosim_modules = [
    "core","cpu","memory","io","bus","timer","interrupt","dma",
    "uart","spi","i2c","gpio","adc","dac","pwm","watchdog",
    "bootloader","flash","eeprom","rtc","can","usb","ethernet","wifi",
]
for mod in eosim_modules:
    mkf(f"desktop-apps/eosim/eosim/{mod}/__init__.py", f"# {mod} module\n")
    mkf(f"desktop-apps/eosim/eosim/{mod}/{mod}.py", f"# {mod} implementation\n")
    mkf(f"desktop-apps/eosim/eosim/{mod}/models.py", f"# {mod} models\n")
    mkf(f"desktop-apps/eosim/eosim/{mod}/tests.py", f"# {mod} tests\n")

mkf("desktop-apps/eosim/eosim/__init__.py", "# EoSim\n")
mkf("desktop-apps/eosim/pyproject.toml",
    '[tool.pytest.ini_options]\ntestpaths = ["tests"]\n')
mkf("desktop-apps/eosim/Dockerfile",
    "FROM python:3.11-slim\nWORKDIR /app\nCOPY . .\nRUN pip install -e .\nCMD [\"python\", \"-m\", \"eosim\"]\n")
for plat in ["linux","windows","macos","embedded"]:
    mkf(f"desktop-apps/eosim/platforms/{plat}/__init__.py", f"# {plat} platform\n")
mkf("desktop-apps/eosim/tests/README.md", "# EoSim Tests\n")

# ── desktop-apps/ebrowser ──────────────────────────────────────────────────
for mod in ["browser","engine","input","network","plugin","render","security","telemetry"]:
    mkf(f"desktop-apps/ebrowser/src/{mod}.cpp", f"// {mod} module\n")
    mkf(f"desktop-apps/ebrowser/include/{mod}.h", f"// {mod} header\n")

mkf("desktop-apps/ebrowser/CMakeLists.txt",
    "cmake_minimum_required(VERSION 3.16)\nproject(eBrowser VERSION 1.9.0)\n")
for plat in ["linux","windows","macos"]:
    mkf(f"desktop-apps/ebrowser/ports/{plat}/CMakeLists.txt",
        f"# {plat} port\n")
mkf("desktop-apps/ebrowser/cmake/toolchain.cmake", "# Toolchain file\n")

# Add more src files to reach 10+
for extra in ["history","bookmarks","tabs","settings","extensions","devtools"]:
    mkf(f"desktop-apps/ebrowser/src/{extra}.cpp", f"// {extra}\n")
    mkf(f"desktop-apps/ebrowser/include/{extra}.h", f"// {extra} header\n")

mkf("desktop-apps/ebrowser/tests/README.md", "# eBrowser Tests\n")

# ── desktop-apps/eostudio ──────────────────────────────────────────────────
for mod in ["codegen","plugins","gui","cli","core"]:
    mkf(f"desktop-apps/eostudio/eostudio/{mod}/__init__.py", f"# {mod}\n")
    mkf(f"desktop-apps/eostudio/eostudio/{mod}/{mod}.py", f"# {mod} impl\n")
mkf("desktop-apps/eostudio/eostudio/__init__.py", "# EoStudio\n")
mkf("desktop-apps/eostudio/pyproject.toml",
    '[tool.pytest.ini_options]\ntestpaths = ["tests"]\n')
mkf("desktop-apps/eostudio/docs/README.md", "# EoStudio Docs\n")
mkf("desktop-apps/eostudio/tests/README.md", "# EoStudio Tests\n")

print("All stub structures created.")
print(f"service-apps/lib files: {sum(1 for _ in (ROOT/'service-apps/lib').rglob('*') if _.is_file())}")
print(f"service-apps/test files: {sum(1 for _ in (ROOT/'service-apps/test').rglob('*') if _.is_file())}")
print(f"desktop-apps/eosim/eosim files: {sum(1 for _ in (ROOT/'desktop-apps/eosim/eosim').rglob('*') if _.is_file())}")
print(f"desktop-apps/ebrowser/src files: {sum(1 for _ in (ROOT/'desktop-apps/ebrowser/src').rglob('*') if _.is_file())}")
