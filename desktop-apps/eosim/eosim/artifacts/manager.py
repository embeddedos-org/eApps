# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""Artifact collection and export."""
import os, json, shutil
from datetime import datetime, timezone
from pathlib import Path
from eosim.engine.backend import SimResult

def collect_artifacts(result: SimResult, output_dir: str = "out/artifacts") -> dict:
    os.makedirs(output_dir, exist_ok=True)
    manifest = {
        "platform": result.platform,
        "engine": result.engine,
        "success": result.success,
        "boot_detected": result.boot_detected,
        "duration_s": round(result.duration_s, 2),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "artifacts": [],
    }
    if result.log_file and os.path.exists(result.log_file):
        dst = os.path.join(output_dir, os.path.basename(result.log_file))
        shutil.copy2(result.log_file, dst)
        manifest["artifacts"].append(dst)
    report = os.path.join(output_dir, result.platform + "-report.json")
    with open(report, "w") as f:
        json.dump(manifest, f, indent=2)
    manifest["artifacts"].append(report)
    return manifest

def generate_junit(results: list, output: str = "out/reports/junit.xml") -> str:
    os.makedirs(os.path.dirname(output), exist_ok=True)
    tests = len(results)
    failures = sum(1 for r in results if not r.get("success", False))
    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    lines.append('<testsuite name="eosim" tests="%d" failures="%d">' % (tests, failures))
    for r in results:
        name = r.get("platform", "unknown")
        t = r.get("duration_s", 0)
        lines.append('  <testcase name="%s" time="%.2f">' % (name, t))
        if not r.get("success", False):
            lines.append('    <failure>Simulation failed</failure>')
        lines.append('  </testcase>')
    lines.append('</testsuite>')
    with open(output, "w") as f:
        f.write("\n".join(lines))
    return output