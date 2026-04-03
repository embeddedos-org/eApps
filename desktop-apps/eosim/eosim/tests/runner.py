# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""Test runner — validates simulation output against checks."""
import yaml
import os
from dataclasses import dataclass
from typing import List
from eosim.engine.backend import SimResult


@dataclass
class CheckResult:
    name: str
    passed: bool
    message: str = ""


def load_checks(platform_dir: str) -> list:
    test_file = os.path.join(platform_dir, "tests.yml")
    if not os.path.exists(test_file):
        return []
    with open(test_file) as f:
        data = yaml.safe_load(f) or {}
    return data.get("checks", [])


def run_checks(sim_result: SimResult, checks: list) -> List[CheckResult]:
    results = []
    for check in checks:
        ctype = check.get("type", "")
        if ctype == "serial_contains":
            value = check.get("value", "")
            passed = value in sim_result.stdout
            results.append(CheckResult(
                name="serial_contains: %s" % value,
                passed=passed,
                message="found" if passed else "not found in output"))
        elif ctype == "exit_code":
            expected = check.get("value", 0)
            passed = sim_result.exit_code == int(expected)
            results.append(CheckResult(
                name="exit_code == %s" % expected,
                passed=passed,
                message="got %d" % sim_result.exit_code))
        elif ctype == "timeout":
            seconds = check.get("seconds", 60)
            passed = sim_result.duration_s <= seconds
            results.append(CheckResult(
                name="timeout <= %ds" % seconds,
                passed=passed,
                message="took %.1fs" % sim_result.duration_s))
        elif ctype == "boot_success":
            passed = sim_result.boot_detected
            results.append(
                CheckResult(
                    name="boot_success",
                    passed=passed,
                    message="boot %s" %
                    ("detected" if passed else "not detected")))
        else:
            results.append(
                CheckResult(
                    name=ctype,
                    passed=False,
                    message="unknown check type"))
    return results
