# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""EoS Integration — build and test EoS apps through EoSim."""
import os
import sys
import subprocess
import shutil
import time
from typing import Optional, List
from dataclasses import dataclass, field


@dataclass
class EosTestResult:
    name: str
    passed: bool
    output: str = ""
    duration_s: float = 0.0
    return_code: int = 0


@dataclass
class EosTestSuite:
    platform: str
    total: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    results: List[EosTestResult] = field(default_factory=list)
    duration_s: float = 0.0
    build_log: str = ""

    def summary(self) -> str:
        lines = ["EoSim Test Suite: %s" % self.platform]
        lines.append("  Total: %d | Passed: %d | Failed: %d | Skipped: %d" % (
            self.total, self.passed, self.failed, self.skipped))
        lines.append("  Duration: %.2fs" % self.duration_s)
        lines.append("")
        for r in self.results:
            status = "PASS" if r.passed else "FAIL"
            lines.append(
                "  [%s] %-30s (%.2fs)" %
                (status, r.name, r.duration_s))
        return "\n".join(lines)


def find_eos_source() -> Optional[str]:
    """Find EoS source code — check multiple locations."""
    candidates = [
        os.environ.get("EOS_SOURCE", ""),
        os.path.join(os.getcwd(), "eos"),
        os.path.join(os.getcwd(), "..", "eos"),
        os.path.join(os.getcwd(), "..", "eos-platform", "core", "eos"),
        os.path.expanduser("~/EoS/eos"),
        "C:/Users/spatchava/EoS/eos",
        "/mnt/c/Users/spatchava/EoS/eos",
    ]
    for c in candidates:
        if c and os.path.isfile(os.path.join(c, "CMakeLists.txt")):
            return os.path.abspath(c)
    return None


def find_cmake() -> Optional[str]:
    """Find cmake binary."""
    cmake = shutil.which("cmake")
    if cmake:
        return cmake
    # Try common locations
    for p in ["/usr/bin/cmake", "/usr/local/bin/cmake",
              "C:/Program Files/CMake/bin/cmake.exe"]:
        if os.path.exists(p):
            return p
    return None


def build_eos(source_dir: str, build_dir: str = None,
              tests: bool = True) -> tuple:
    """Build EoS from source with tests enabled."""
    if not build_dir:
        build_dir = os.path.join(source_dir, "eosim-build")

    cmake = find_cmake()
    if not cmake:
        return False, "cmake not found — install CMake to build EoS"

    os.makedirs(build_dir, exist_ok=True)
    log_lines = []

    # Configure
    cfg_cmd = [cmake, "-B", build_dir, "-S", source_dir]
    if tests:
        cfg_cmd.append("-DEOS_BUILD_TESTS=ON")

    log_lines.append("$ " + " ".join(cfg_cmd))
    try:
        r = subprocess.run(
            cfg_cmd,
            capture_output=True,
            text=True,
            timeout=120)
        log_lines.append(r.stdout)
        if r.returncode != 0:
            log_lines.append(r.stderr)
            return False, "\n".join(log_lines)
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        return False, "Build configure failed: %s" % str(e)

    # Build
    build_cmd = [cmake, "--build", build_dir]
    log_lines.append("$ " + " ".join(build_cmd))
    try:
        r = subprocess.run(
            build_cmd,
            capture_output=True,
            text=True,
            timeout=300)
        log_lines.append(r.stdout)
        if r.returncode != 0:
            log_lines.append(r.stderr)
            return False, "\n".join(log_lines)
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        return False, "Build failed: %s" % str(e)

    return True, "\n".join(log_lines)


def run_eos_tests(source_dir: str, build_dir: str = None) -> EosTestSuite:
    """Build EoS and run all unit tests through EoSim."""
    suite = EosTestSuite(platform="eos-native")
    start = time.time()

    if not build_dir:
        build_dir = os.path.join(source_dir, "eosim-build")

    # Build first
    ok, log = build_eos(source_dir, build_dir, tests=True)
    suite.build_log = log
    if not ok:
        suite.results.append(
            EosTestResult(
                name="build",
                passed=False,
                output=log,
                duration_s=time.time() -
                start))
        suite.total = 1
        suite.failed = 1
        suite.duration_s = time.time() - start
        return suite

    suite.results.append(EosTestResult(
        name="build", passed=True, output="Build successful",
        duration_s=time.time() - start))
    suite.passed += 1
    suite.total += 1

    # Discover test executables
    test_dir = build_dir
    if os.name == 'nt':
        # Windows: tests may be in Release/ or Debug/ subdirectory
        for sub in ["", "tests", "tests/Release", "tests/Debug",
                    "Release", "Debug"]:
            check = os.path.join(build_dir, sub)
            if os.path.isdir(check):
                exes = [f for f in os.listdir(check) if f.startswith(
                    "test_") and (f.endswith(".exe") or "." not in f)]
                if exes:
                    test_dir = check
                    break
    else:
        for sub in ["", "tests"]:
            check = os.path.join(build_dir, sub)
            if os.path.isdir(check):
                exes = [f for f in os.listdir(check) if f.startswith(
                    "test_") and os.access(os.path.join(check, f), os.X_OK)]
                if exes:
                    test_dir = check
                    break

    # Run each test
    test_files = sorted([f for f in os.listdir(test_dir)
                         if f.startswith("test_")])

    for tf in test_files:
        test_path = os.path.join(test_dir, tf)
        if not os.access(test_path, os.X_OK) and not tf.endswith(".exe"):
            continue

        t_start = time.time()
        try:
            r = subprocess.run([test_path], capture_output=True, text=True,
                               timeout=30, cwd=build_dir)
            passed = r.returncode == 0
            output = r.stdout + r.stderr
        except subprocess.TimeoutExpired:
            passed = False
            output = "Timeout after 30s"
        except (FileNotFoundError, PermissionError) as e:
            passed = False
            output = str(e)

        t_name = tf.replace(".exe", "")
        result = EosTestResult(
            name=t_name,
            passed=passed,
            output=output,
            duration_s=time.time() - t_start,
            return_code=r.returncode if 'r' in dir() else -1)
        suite.results.append(result)
        suite.total += 1
        if passed:
            suite.passed += 1
        else:
            suite.failed += 1

    suite.duration_s = time.time() - start
    return suite


def run_eosuite_tests(eosuite_dir: str) -> EosTestSuite:
    """Run eApps Python tests through EoSim."""
    suite = EosTestSuite(platform="eapps")
    start = time.time()

    pytest = shutil.which("pytest") or shutil.which("python3")
    if not pytest:
        pytest = sys.executable

    cmd = [sys.executable, "-m", "pytest", os.path.join(eosuite_dir, "tests"),
           "-q", "--tb=line"]

    try:
        r = subprocess.run(cmd, capture_output=True, text=True,
                           timeout=120, cwd=eosuite_dir)
        output = r.stdout + r.stderr

        # Parse pytest output
        for line in output.split("\n"):
            if " passed" in line:
                import re
                m = re.search(r"(\d+) passed", line)
                if m:
                    suite.passed = int(m.group(1))
                m = re.search(r"(\d+) failed", line)
                if m:
                    suite.failed = int(m.group(1))
                m = re.search(r"(\d+) skipped", line)
                if m:
                    suite.skipped = int(m.group(1))

        suite.total = suite.passed + suite.failed
        suite.results.append(EosTestResult(
            name="pytest", passed=(suite.failed == 0),
            output=output, duration_s=time.time() - start,
            return_code=r.returncode))
    except Exception as e:
        suite.results.append(EosTestResult(
            name="pytest", passed=False, output=str(e)))
        suite.total = 1
        suite.failed = 1

    suite.duration_s = time.time() - start
    return suite
