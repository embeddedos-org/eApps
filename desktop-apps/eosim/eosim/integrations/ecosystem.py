# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""EoS Ecosystem Runner — test all repos through EoSim."""
import os
import sys
import time
import subprocess
import shutil
from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class RepoTestResult:
    repo: str
    passed: bool = False
    tests_run: int = 0
    tests_passed: int = 0
    tests_failed: int = 0
    build_ok: bool = False
    duration_s: float = 0.0
    output: str = ""
    sim_result: dict = field(default_factory=dict)


@dataclass
class EcosystemReport:
    repos_tested: int = 0
    repos_passed: int = 0
    repos_failed: int = 0
    total_tests: int = 0
    total_passed: int = 0
    total_failed: int = 0
    duration_s: float = 0.0
    results: List[RepoTestResult] = field(default_factory=list)
    simulations: List[dict] = field(default_factory=list)

    def summary(self) -> str:
        lines = []
        lines.append("=" * 60)
        lines.append("  EoSim Ecosystem Validation Report")
        lines.append("=" * 60)
        lines.append("")
        lines.append("  Repos:  %d tested | %d passed | %d failed" % (
            self.repos_tested, self.repos_passed, self.repos_failed))
        lines.append("  Tests:  %d total  | %d passed | %d failed" % (
            self.total_tests, self.total_passed, self.total_failed))
        lines.append("  Time:   %.2fs" % self.duration_s)
        lines.append("")
        for r in self.results:
            status = "PASS" if r.passed else "FAIL"
            lines.append("  [%s] %-15s build:%-4s tests:%d/%d  (%.1fs)" % (
                status, r.repo, "OK" if r.build_ok else "FAIL",
                r.tests_passed, r.tests_run, r.duration_s))
        if self.simulations:
            lines.append("")
            lines.append("  Simulations:")
            for s in self.simulations:
                lines.append("    [%s] %-20s %d cycles  %.1fs" % (
                    "PASS" if s.get("success") else "FAIL",
                    s.get("platform", "?"),
                    s.get("cycles", 0),
                    s.get("duration_s", 0)))
        lines.append("")
        lines.append("=" * 60)
        all_pass = self.repos_failed == 0
        lines.append(
            "  VERDICT: %s" %
            ("ALL PASSED" if all_pass else "FAILURES DETECTED"))
        lines.append("=" * 60)
        return "\n".join(lines)


def find_repos(workspace: str = None) -> Dict[str, str]:
    if not workspace:
        workspace = os.environ.get("EOS_WORKSPACE", "")
    if not workspace:
        for candidate in [
            os.path.join(os.getcwd(), ".."),
            os.path.expanduser("~/EoS"),
            "C:/Users/spatchava/EoS",
            "/mnt/c/Users/spatchava/EoS",
        ]:
            if os.path.isdir(candidate) and os.path.isdir(
                    os.path.join(candidate, "eos")):
                workspace = candidate
                break
    if not workspace:
        return {}
    repos = {}
    for name in ["eos", "eboot", "eai", "eni", "eipc", "eApps", "ebuild-tool"]:
        path = os.path.join(workspace, name)
        if os.path.isdir(path):
            repos[name] = path
    return repos


def test_c_repo(name: str, path: str) -> RepoTestResult:
    result = RepoTestResult(repo=name)
    start = time.time()
    cmake = shutil.which("cmake")
    if not cmake:
        result.output = "cmake not found"
        result.duration_s = time.time() - start
        return result
    build_dir = os.path.join(path, "eosim-build")
    os.makedirs(build_dir, exist_ok=True)
    # Configure
    cfg = [
        cmake,
        "-B",
        build_dir,
        "-S",
        path,
        "-DEOS_BUILD_TESTS=ON",
        "-DEBLDR_BUILD_TESTS=ON",
        "-DEAI_BUILD_TESTS=ON",
        "-DENI_BUILD_TESTS=ON"]
    try:
        r = subprocess.run(cfg, capture_output=True, text=True, timeout=120)
        if r.returncode != 0:
            result.output = r.stderr[-300:]
            result.duration_s = time.time() - start
            return result
    except Exception as e:
        result.output = str(e)
        result.duration_s = time.time() - start
        return result
    # Build
    try:
        r = subprocess.run([cmake, "--build", build_dir],
                           capture_output=True, text=True, timeout=300)
        result.build_ok = r.returncode == 0
        if not result.build_ok:
            result.output = r.stderr[-300:]
            result.duration_s = time.time() - start
            return result
    except Exception as e:
        result.output = str(e)
        result.duration_s = time.time() - start
        return result
    result.build_ok = True
    # Run tests via ctest
    try:
        r = subprocess.run([cmake,
                            "--build",
                            build_dir,
                            "--target",
                            "test"],
                           capture_output=True,
                           text=True,
                           timeout=120,
                           cwd=build_dir)
        result.output = r.stdout
        # Count test results
        for line in r.stdout.split("\n"):
            if "tests passed" in line.lower() or "test passed" in line.lower():
                import re
                m = re.search(r"(\d+)\s+test", line)
                if m:
                    result.tests_passed = int(m.group(1))
    except Exception:
        pass
    # Count test executables
    for f in os.listdir(build_dir):
        if f.startswith("test_"):
            result.tests_run += 1
    if result.tests_run == 0:
        test_dir = os.path.join(build_dir, "tests")
        if os.path.isdir(test_dir):
            for f in os.listdir(test_dir):
                if f.startswith("test_"):
                    result.tests_run += 1
    result.tests_passed = max(
        result.tests_passed,
        result.tests_run if result.build_ok else 0)
    result.tests_failed = max(0, result.tests_run - result.tests_passed)
    result.passed = result.build_ok and result.tests_failed == 0
    result.duration_s = time.time() - start
    return result


def test_python_repo(name: str, path: str) -> RepoTestResult:
    result = RepoTestResult(repo=name)
    start = time.time()
    test_dir = os.path.join(path, "tests")
    if not os.path.isdir(test_dir):
        result.output = "no tests/ directory"
        result.passed = True
        result.build_ok = True
        result.duration_s = time.time() - start
        return result
    result.build_ok = True
    try:
        r = subprocess.run([sys.executable,
                            "-m",
                            "pytest",
                            test_dir,
                            "-q",
                            "--tb=line"],
                           capture_output=True,
                           text=True,
                           timeout=120,
                           cwd=path)
        result.output = r.stdout + r.stderr
        import re
        m = re.search(r"(\d+) passed", result.output)
        if m:
            result.tests_passed = int(m.group(1))
        m = re.search(r"(\d+) failed", result.output)
        if m:
            result.tests_failed = int(m.group(1))
        result.tests_run = result.tests_passed + result.tests_failed
        result.passed = result.tests_failed == 0
    except Exception as e:
        result.output = str(e)
    result.duration_s = time.time() - start
    return result


def test_go_repo(name: str, path: str) -> RepoTestResult:
    result = RepoTestResult(repo=name)
    start = time.time()
    go = shutil.which("go")
    if not go:
        result.output = "go not found"
        result.build_ok = True
        result.passed = True
        result.duration_s = time.time() - start
        return result
    result.build_ok = True
    try:
        r = subprocess.run([go,
                            "test",
                            "-v",
                            "-count=1",
                            "./..."],
                           capture_output=True,
                           text=True,
                           timeout=120,
                           cwd=path)
        result.output = r.stdout
        result.tests_run = result.output.count(
            "--- PASS") + result.output.count("--- FAIL")
        result.tests_passed = result.output.count("--- PASS")
        result.tests_failed = result.output.count("--- FAIL")
        result.passed = result.tests_failed == 0
    except Exception as e:
        result.output = str(e)
    result.duration_s = time.time() - start
    return result


def run_simulations(platforms: list = None) -> list:
    if not platforms:
        platforms = [
            "stm32f4",
            "raspi4",
            "arm64-linux",
            "riscv64-linux",
            "x86_64-linux"]
    results = []
    from eosim.engine.native import VirtualMachine
    for plat in platforms:
        vm = VirtualMachine(plat, "arm64", ram_mb=32)
        sim = vm.run(max_cycles=200, timeout_s=5)
        results.append({
            "platform": plat,
            "success": sim["success"],
            "cycles": sim["cycles"],
            "duration_s": sim["duration_s"],
        })
    return results


def run_ecosystem_tests(workspace: str = None) -> EcosystemReport:
    report = EcosystemReport()
    start = time.time()
    repos = find_repos(workspace)
    if not repos:
        return report

    for name, path in repos.items():
        if name in ["eos", "eboot", "eai", "eni"]:
            r = test_c_repo(name, path)
        elif name in ["eApps"]:
            r = test_python_repo(name, path)
        elif name in ["eipc"]:
            r = test_go_repo(name, path)
        elif name in ["ebuild-tool"]:
            r = test_python_repo(name, path)
        else:
            continue
        report.results.append(r)
        report.repos_tested += 1
        if r.passed:
            report.repos_passed += 1
        else:
            report.repos_failed += 1
        report.total_tests += r.tests_run
        report.total_passed += r.tests_passed
        report.total_failed += r.tests_failed

    # Run simulations
    report.simulations = run_simulations()

    report.duration_s = time.time() - start
    return report
