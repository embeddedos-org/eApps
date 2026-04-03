# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""Advanced test scenarios — boot, peripheral, networking."""
import yaml
from typing import List
from eosim.tests.runner import CheckResult


def load_scenario(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f) or {}


def run_scenario(
        scenario: dict,
        sim_stdout: str,
        duration: float) -> List[CheckResult]:
    results = []
    for step in scenario.get("steps", []):
        stype = step.get("type", "")
        if stype == "wait_for":
            pattern = step.get("pattern", "")
            passed = pattern in sim_stdout
            results.append(
                CheckResult(
                    name="wait_for: %s" %
                    pattern,
                    passed=passed,
                    message="found" if passed else "not found"))
        elif stype == "assert_no":
            pattern = step.get("pattern", "")
            passed = pattern not in sim_stdout
            results.append(
                CheckResult(
                    name="assert_no: %s" %
                    pattern,
                    passed=passed,
                    message="absent" if passed else "found (unexpected)"))
        elif stype == "timing":
            max_s = step.get("max_seconds", 60)
            passed = duration <= max_s
            results.append(
                CheckResult(
                    name="timing <= %ds" %
                    max_s,
                    passed=passed,
                    message="%.1fs" %
                    duration))
        elif stype == "count_matches":
            pattern = step.get("pattern", "")
            expected = step.get("min_count", 1)
            count = sim_stdout.count(pattern)
            passed = count >= expected
            results.append(
                CheckResult(
                    name="count(%s) >= %d" %
                    (pattern,
                     expected),
                    passed=passed,
                    message="got %d" %
                    count))
    return results
