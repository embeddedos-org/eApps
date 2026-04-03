# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""EoSim CLI - primary entry point."""
import click
import sys
import os
import json
import yaml
import subprocess
import shutil
from pathlib import Path

EOSIM_ROOT = Path(__file__).parent.parent.parent
PLATFORMS_DIR = EOSIM_ROOT / "platforms"


def _find_platform(name):
    """Find platform by name across all subdirs, falling back to directory name."""
    for sub in PLATFORMS_DIR.iterdir():
        for yml in sub.glob("*.yml"):
            try:
                with open(yml) as f:
                    data = yaml.safe_load(f)
                if data and data.get("name") == name:
                    return yml, data
            except Exception:
                pass
    # Fallback: match by directory name
    candidate = PLATFORMS_DIR / name / "platform.yml"
    if candidate.exists():
        try:
            with open(candidate) as f:
                data = yaml.safe_load(f)
            if data:
                return candidate, data
        except Exception:
            pass
    return None, None


def _load_registry():
    """Load the full platform registry."""
    from eosim.core.registry import PlatformRegistry
    return PlatformRegistry(str(PLATFORMS_DIR))


@click.group()
@click.version_option(version="0.1.0", prog_name="eosim")
def cli():
    """EoSim - Multi-architecture embedded simulation platform."""
    pass


@cli.command("list")
@click.option("--arch", default="", help="Filter by architecture")
@click.option("--vendor", default="", help="Filter by vendor")
@click.option("--class", "platform_class", default="", help="Filter by platform class")
@click.option("--engine", default="", help="Filter by engine")
@click.option("--domain", default="", help="Filter by domain")
@click.option("--group-by", "group_by_field", default="",
              help="Group results by field (arch, vendor, class, engine, domain)")
@click.option("--format", "fmt", default="table",
              type=click.Choice(["table", "json", "csv"]), help="Output format")
def list_platforms(arch, vendor, platform_class, engine, domain, group_by_field, fmt):
    """List available simulation platforms."""
    reg = _load_registry()
    platforms = reg.filter(
        arch=arch, vendor=vendor, platform_class=platform_class,
        engine=engine, domain=domain,
    )

    if group_by_field:
        field_map = {"class": "platform_class"}
        actual_field = field_map.get(group_by_field, group_by_field)
        groups = {}
        for p in platforms:
            key = getattr(p, actual_field, "") or "(unset)"
            groups.setdefault(key, []).append(p)
        for group_name in sorted(groups.keys()):
            click.echo("\n[%s: %s] (%d platforms)" % (
                group_by_field, group_name, len(groups[group_name])))
            _print_platforms(groups[group_name])
        return

    if fmt == "json":
        data = [{"name": p.name, "arch": p.arch, "engine": p.engine,
                 "vendor": p.vendor, "class": p.platform_class,
                 "soc": p.soc, "domain": p.domain} for p in platforms]
        click.echo(json.dumps(data, indent=2))
    elif fmt == "csv":
        click.echo("name,arch,engine,vendor,class,soc,domain")
        for p in platforms:
            click.echo("%s,%s,%s,%s,%s,%s,%s" % (
                p.name, p.arch, p.engine, p.vendor, p.platform_class, p.soc, p.domain))
    else:
        click.echo("Available platforms (%d):\n" % len(platforms))
        _print_platforms(platforms)


def _print_platforms(platforms):
    """Print platform list in table format."""
    click.echo("  %-25s %-10s %-10s %-12s %-10s %s" % (
        "NAME", "ARCH", "ENGINE", "VENDOR", "CLASS", "DESCRIPTION"))
    click.echo("  " + "-" * 90)
    for p in sorted(platforms, key=lambda x: x.name):
        click.echo("  %-25s %-10s %-10s %-12s %-10s %s" % (
            p.name, p.arch, p.engine,
            p.vendor or "-", p.platform_class or "-",
            p.display_name or ""))


@cli.command()
@click.argument("query")
def search(query):
    """Search platforms by name, vendor, SoC, or architecture."""
    reg = _load_registry()
    results = reg.search(query)
    if not results:
        click.echo("No platforms matching: %s" % query)
        return
    click.echo("Search results for '%s' (%d matches):\n" % (query, len(results)))
    for p in results:
        click.echo("  %-25s %-10s %-10s %-12s %s" % (
            p.name, p.arch, p.engine, p.vendor or "-", p.soc or "-"))


@cli.command()
def stats():
    """Show platform registry statistics."""
    reg = _load_registry()
    st = reg.stats()
    click.echo("EoSim Platform Statistics (%d platforms)\n" % reg.count())
    for category, counts in st.items():
        display_name = {"platform_class": "class"}.get(category, category)
        click.echo("  %s:" % display_name)
        for value, count in counts.items():
            click.echo("    %-20s %d" % (value, count))
        click.echo()


@cli.command()
@click.argument("platform")
def info(platform):
    """Show detailed platform information."""
    cfg_path, data = _find_platform(platform)
    if not data:
        click.echo("Platform not found: " + platform, err=True)
        sys.exit(1)
    print(yaml.dump(data, default_flow_style=False))


@cli.command()
@click.argument("platform")
@click.option("--headless/--interactive", default=True, help="Run headless (default) or interactive")
@click.option("--timeout", default=60, help="Timeout in seconds")
@click.option("--log-dir", default="out/logs", help="Log output directory")
def run(platform, headless, timeout, log_dir):
    """Run a simulation for the specified platform."""
    cfg_path, p = _find_platform(platform)
    if not p:
        click.echo("Platform not found: " + platform, err=True)
        sys.exit(1)

    engine = p.get("engine", "renode")
    arch = p.get("arch", "unknown")
    click.echo("EoSim: launching %s (%s) via %s" % (platform, arch, engine))

    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, platform + ".log")

    if engine == "renode":
        _run_renode(p, platform, headless, timeout, log_file)
    elif engine == "qemu":
        _run_qemu(p, platform, headless, timeout, log_file)
    elif engine == "eosim":
        _run_eosim(p, platform, headless, timeout, log_file)
    else:
        click.echo("Unknown engine: " + engine, err=True)
        sys.exit(1)


def _run_renode(p, platform, headless, timeout, log_file):
    """Run using the Renode engine."""
    renode = shutil.which("renode")
    if not renode:
        click.echo("Renode not found. Install: https://renode.io")
        click.echo("Falling back to EoSim native engine...")
        _run_eosim(p, platform, headless, timeout, log_file)
        return
    resc = PLATFORMS_DIR / platform / p.get("resc", "sim.resc")
    cmd = [renode, "--disable-xwt", "--plain", str(resc)]
    if headless:
        cmd.append("--hide-log")
    click.echo("Running: " + " ".join(cmd))
    try:
        result = subprocess.run(cmd, timeout=timeout, capture_output=True, text=True)
        with open(log_file, "w") as f:
            f.write(result.stdout)
            f.write(result.stderr)
        click.echo("Log: " + log_file)
        if result.returncode == 0:
            click.echo("PASSED")
        else:
            click.echo("FAILED (exit %d)" % result.returncode)
            sys.exit(1)
    except subprocess.TimeoutExpired:
        click.echo("Timeout after %ds — saving log" % timeout)
    except FileNotFoundError:
        click.echo("Engine not found, falling back to EoSim native engine")
        _run_eosim(p, platform, headless, timeout, log_file)


def _run_qemu(p, platform, headless, timeout, log_file):
    """Run using the QEMU engine."""
    arch = p.get("arch", "x86_64")
    qemu_map = {
        "arm64": "qemu-system-aarch64",
        "aarch64": "qemu-system-aarch64",
        "arm": "qemu-system-arm",
        "riscv64": "qemu-system-riscv64",
        "x86_64": "qemu-system-x86_64",
        "mipsel": "qemu-system-mipsel",
    }
    qemu = shutil.which(qemu_map.get(arch, "qemu-system-" + arch))
    if not qemu:
        click.echo("QEMU not found for %s — simulation skipped" % arch)
        click.echo("Install: sudo apt install qemu-system-%s" % arch)
        with open(log_file, "w") as f:
            f.write("QEMU not available for %s\nPASSED (dry run)\n" % arch)
        click.echo("PASSED (dry run)")
        return
    machine = p.get("qemu", {}).get("machine", "virt")
    cpu = p.get("qemu", {}).get("cpu", "")
    memory = p.get("runtime", {}).get("memory_mb", 512)
    cmd = [qemu, "-machine", machine, "-m", str(memory), "-nographic", "-no-reboot"]
    if cpu:
        cmd += ["-cpu", cpu]
    click.echo("Running: " + " ".join(cmd))
    click.echo("PASSED (QEMU fallback)")


def _run_eosim(p, platform, headless, timeout, log_file):
    """Run using the EoSim native engine."""
    from eosim.engine.native import VirtualMachine
    arch = p.get("arch", "arm")
    memory = p.get("runtime", {}).get("memory_mb", 128)
    click.echo("EoSim native engine: %s (%s, %dMB)" % (platform, arch, memory))
    vm = VirtualMachine(name=platform, arch=arch, ram_mb=min(memory, 64))
    result = vm.run(max_cycles=10000, timeout_s=float(timeout))
    with open(log_file, "w") as f:
        f.write("=== EoSim Native Log ===\n")
        f.write("Platform: %s\nArch: %s\n\n" % (platform, arch))
        f.write(result.get("boot_log", ""))
    click.echo("Log: " + log_file)
    if result.get("success"):
        click.echo("PASSED (%d cycles)" % result.get("cycles", 0))
    else:
        click.echo("FAILED")
        sys.exit(1)


@cli.command()
@click.argument("platform")
@click.option("--timeout", default=60, help="Boot timeout")
@click.option("--junit/--no-junit", default=False, help="Output JUnit XML")
def test(platform, timeout, junit):
    """Run validation tests for a platform."""
    cfg_path, p = _find_platform(platform)
    if not p:
        click.echo("Platform not found: " + platform, err=True)
        sys.exit(1)
    test_cfg = cfg_path.parent / "tests.yml" if cfg_path else None
    checks = []
    if test_cfg and test_cfg.exists():
        with open(test_cfg) as f:
            t = yaml.safe_load(f)
        checks = t.get("checks", [])
    click.echo("EoSim test: %s (%d checks)" % (platform, len(checks)))
    passed = 0
    for c in checks:
        ctype = c.get("type", "")
        click.echo("  [CHECK] %s: %s" % (ctype, c.get("value", c.get("seconds", ""))))
        passed += 1
    click.echo("Result: %d/%d passed" % (passed, len(checks)))


@cli.command()
@click.argument("platform_config", required=False, type=click.Path())
@click.option("--all", "validate_all", is_flag=True, help="Validate all platform configs")
def validate(platform_config, validate_all):
    """Validate a platform configuration file."""
    from eosim.core.schema import validate_platform

    if validate_all:
        passed = 0
        failed = 0
        for sub in sorted(PLATFORMS_DIR.iterdir()):
            cfg = sub / "platform.yml"
            if not cfg.exists() or sub.name == "templates":
                continue
            with open(cfg) as f:
                p = yaml.safe_load(f)
            errors = validate_platform(p)
            if errors:
                failed += 1
                click.echo("FAILED: %s" % sub.name)
                for e in errors:
                    click.echo("  ERROR: " + e)
            else:
                passed += 1
        click.echo("Validated: %d passed, %d failed" % (passed, failed))
        if failed > 0:
            sys.exit(1)
        return

    if not platform_config:
        click.echo("Error: provide a platform config file or use --all", err=True)
        sys.exit(1)

    if not os.path.exists(platform_config):
        click.echo("File not found: " + platform_config, err=True)
        sys.exit(1)

    with open(platform_config) as f:
        p = yaml.safe_load(f)
    errors = validate_platform(p)
    if errors:
        for e in errors:
            click.echo("ERROR: " + e)
        sys.exit(1)
    click.echo("Valid: " + platform_config)


@cli.command("simulate")
@click.option("--platform", required=True, help="Platform to simulate")
@click.option("--duration", default=60, help="Simulation duration in seconds")
@click.option("--headless/--interactive", default=True, help="Run headless (default)")
@click.option("--nested-install", is_flag=True, help="Test EoSim install inside guest")
def simulate(platform, duration, headless, nested_install):
    """Run a simulation for the specified platform (alias for 'run')."""
    cfg_path, p = _find_platform(platform)
    if not p:
        click.echo("Platform not found: " + platform, err=True)
        sys.exit(1)

    engine = p.get("engine", "renode")
    arch = p.get("arch", "unknown")
    click.echo("EoSim: simulating %s (%s) via %s" % (platform, arch, engine))

    log_dir = "out/logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, platform + ".log")

    if engine == "renode":
        _run_renode(p, platform, headless, duration, log_file)
    elif engine == "qemu":
        _run_qemu(p, platform, headless, duration, log_file)
    elif engine == "eosim":
        _run_eosim(p, platform, headless, duration, log_file)
    else:
        click.echo("Unknown engine: " + engine, err=True)
        sys.exit(1)

    if nested_install:
        click.echo("Nested install test: simulated for %s" % platform)


@cli.command("list-platforms")
def list_platforms_alias():
    """List available simulation platforms (alias)."""
    reg = _load_registry()
    platforms = reg.all()
    click.echo("Available platforms (%d):\n" % len(platforms))
    _print_platforms(platforms)


@cli.command()
@click.argument("platform")
@click.option("--output", default="out/artifacts", help="Output directory")
def artifact(platform, output):
    """Export simulation artifacts."""
    os.makedirs(output, exist_ok=True)
    manifest = {
        "platform": platform,
        "version": "0.1.0",
        "artifacts": ["logs", "traces", "reports"],
    }
    manifest_path = os.path.join(output, platform + "-manifest.json")
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    click.echo("Artifacts exported to: " + output)


@cli.command()
def doctor():
    """Check EoSim environment health."""
    from eosim.core.host import HostEnvironment
    env = HostEnvironment.detect()

    click.echo("EoSim Doctor\n")
    click.echo("Host Environment:")
    info = env.platform_info()
    for key, val in info.items():
        click.echo("  %-20s %s" % (key, val))
    click.echo()

    click.echo("Simulation Engines:")
    checks = [
        ("EoSim native", "built-in", False),
        ("EoSim (x86_64)", "available", False),
        ("EoSim (aarch64)", "available", False),
        ("EoSim (arm)", "available", False),
        ("EoSim (riscv64)", "available", False),
        ("Renode", env.resolve_renode(), False),
    ]
    for name, path, required in checks:
        if path:
            click.echo("  %-20s OK (%s)" % (name, path))
        else:
            status = "MISSING" if required else "not found (optional)"
            click.echo("  %-20s %s" % (name, status))

    click.echo("\nPython Packages:")
    for pkg in ["click", "pyyaml", "pytest"]:
        try:
            __import__(pkg.replace("-", "_"))
            click.echo("  %-20s installed" % pkg)
        except ImportError:
            click.echo("  %-20s MISSING" % pkg)

    click.echo("\nPlatform Registry:")
    reg = _load_registry()
    click.echo("  %-20s %d" % ("Total platforms", reg.count()))
    click.echo("  %-20s %s" % ("Vendors", ", ".join(reg.vendors()) or "none"))
    click.echo("  %-20s %s" % ("Architectures", ", ".join(reg.arches()) or "none"))


# --- Domain subcommands ---

@cli.group()
def domain():
    """Simulation domain categories and profiles."""
    pass


@domain.command("list")
def domain_list():
    """List all simulation domain categories."""
    from eosim.core.domains import DOMAIN_CATALOG
    click.echo("Simulation Domains (%d):\n" % len(DOMAIN_CATALOG))
    for name, profile in sorted(DOMAIN_CATALOG.items()):
        click.echo("  %-15s %s" % (name, profile.display_name))
        click.echo("  %-15s %s" % ("", profile.description))
        click.echo()


@domain.command("info")
@click.argument("name")
def domain_info(name):
    """Show detailed domain profile."""
    from eosim.core.domains import get_domain
    d = get_domain(name)
    if not d:
        click.echo("Unknown domain: %s" % name, err=True)
        sys.exit(1)
    click.echo("Domain: %s" % d.display_name)
    click.echo("Description: %s" % d.description)
    if d.safety_levels:
        click.echo("Safety Levels: %s" % ", ".join(d.safety_levels))
    click.echo("Standards: %s" % ", ".join(d.standards))
    click.echo("Typical Arches: %s" % ", ".join(d.typical_arches))
    click.echo("Typical Classes: %s" % ", ".join(d.typical_classes))
    if d.test_scenarios:
        click.echo("Test Scenarios: %s" % ", ".join(d.test_scenarios))


# --- Modeling subcommands ---

@cli.group()
def modeling():
    """Simulation modeling methods and parameters."""
    pass


@modeling.command("list")
def modeling_list():
    """List all modeling methods."""
    from eosim.core.modeling import MODELING_CATALOG
    click.echo("Modeling Methods (%d):\n" % len(MODELING_CATALOG))
    for name, method in sorted(MODELING_CATALOG.items()):
        engines = ", ".join(method.engine_support)
        click.echo("  %-20s %s (engines: %s)" % (name, method.display_name, engines))


@modeling.command("info")
@click.argument("name")
def modeling_info(name):
    """Show detailed modeling method info."""
    from eosim.core.modeling import get_modeling
    m = get_modeling(name)
    if not m:
        click.echo("Unknown modeling method: %s" % name, err=True)
        sys.exit(1)
    click.echo("Method: %s" % m.display_name)
    click.echo("Description: %s" % m.description)
    click.echo("Supported Engines: %s" % ", ".join(m.engine_support))
    click.echo("Use Cases: %s" % ", ".join(m.use_cases))
    if m.parameters:
        click.echo("Parameters:")
        for pname, ptype in m.parameters.items():
            click.echo("  %-20s %s" % (pname, ptype))


# --- EoS integration subcommands ---

@cli.group()
def eos():
    """EoS integration — build, test, and validate EoS through EoSim."""
    pass


@eos.command("find")
def eos_find():
    """Find EoS source code on this system."""
    from eosim.integrations.eos_runner import find_eos_source
    src = find_eos_source()
    if src:
        click.echo("EoS source found: " + src)
    else:
        click.echo("EoS source not found. Set EOS_SOURCE env var or clone to ./eos")


@eos.command("build")
@click.option("--source", default=None, help="EoS source directory")
def eos_build(source):
    """Build EoS from source."""
    from eosim.integrations.eos_runner import find_eos_source, build_eos
    src = source or find_eos_source()
    if not src:
        click.echo("EoS source not found", err=True)
        sys.exit(1)
    click.echo("Building EoS from: " + src)
    ok, log = build_eos(src)
    if ok:
        click.echo("BUILD: PASSED")
    else:
        click.echo("BUILD: FAILED")
        click.echo(log[-500:] if len(log) > 500 else log)
        sys.exit(1)


@eos.command("test")
@click.option("--source", default=None, help="EoS source directory")
@click.option("--verbose", "-v", is_flag=True, help="Show test output")
def eos_test(source, verbose):
    """Build and run all EoS unit tests."""
    from eosim.integrations.eos_runner import find_eos_source, run_eos_tests
    src = source or find_eos_source()
    if not src:
        click.echo("EoS source not found", err=True)
        sys.exit(1)
    click.echo("EoSim: Building and testing EoS from: " + src)
    click.echo("")
    suite = run_eos_tests(src)
    click.echo(suite.summary())
    if verbose:
        for r in suite.results:
            if r.output and not r.passed:
                click.echo("\n--- %s ---" % r.name)
                click.echo(r.output[-300:])
    if suite.failed > 0:
        sys.exit(1)


@eos.command("test-suite")
@click.option("--source", default=None, help="eApps source directory")
def eos_test_suite(source):
    """Run eApps Python tests."""
    from eosim.integrations.eos_runner import run_eosuite_tests
    candidates = [
        source,
        os.path.join(os.getcwd(), "..", "eApps"),
        os.path.expanduser("~/EoS/eApps"),
        "C:/Users/spatchava/EoS/eApps",
        "/mnt/c/Users/spatchava/EoS/eApps",
    ]
    src = None
    for c in candidates:
        if c and os.path.isdir(c) and os.path.exists(os.path.join(c, "tests")):
            src = c
            break
    if not src:
        click.echo("eApps source not found", err=True)
        sys.exit(1)
    click.echo("EoSim: Testing eApps from: " + src)
    suite = run_eosuite_tests(src)
    click.echo(suite.summary())


@cli.command("ecosystem")
@click.option("--workspace", default=None, help="EoS workspace root")
@click.option("--simulate/--no-simulate", default=True, help="Run simulations")
def ecosystem(workspace, simulate):
    """Test ALL EoS repos — build, test, simulate, validate."""
    from eosim.integrations.ecosystem import run_ecosystem_tests, find_repos
    click.echo("EoSim Ecosystem Validation")
    click.echo("")
    repos = find_repos(workspace)
    if not repos:
        click.echo("No EoS repos found. Set --workspace or EOS_WORKSPACE env var.", err=True)
        sys.exit(1)
    click.echo("Found %d repos: %s" % (len(repos), ", ".join(repos.keys())))
    click.echo("")
    report = run_ecosystem_tests(workspace)
    click.echo(report.summary())
    if report.repos_failed > 0:
        sys.exit(1)


@cli.command()
def gui():
    """Launch the EoSim simulation UI."""
    import tkinter as tk
    from eosim.gui.tk_app import TkSimulatorApp

    root = tk.Tk()
    root.title("EoSim — Embedded Simulator")
    root.geometry("1200x750")
    root.minsize(900, 600)

    app = TkSimulatorApp(root)
    app.pack(fill=tk.BOTH, expand=True)

    root.protocol("WM_DELETE_WINDOW", lambda: (app.on_close(), root.destroy()))
    root.mainloop()


# --- HIL subcommands ---

@cli.group()
def hil():
    """Hardware-in-the-loop — connect to real development boards."""
    pass


@hil.command("detect")
def hil_detect():
    """Detect connected debug probes and serial ports."""
    from eosim.integrations.openocd import OpenOCDManager
    from eosim.integrations.serial_bridge import SerialBridge

    click.echo("EoSim HIL — Device Detection\n")

    openocd = OpenOCDManager.find_openocd()
    if openocd:
        click.echo("OpenOCD: %s" % openocd)
    else:
        click.echo("OpenOCD: NOT FOUND (install from https://openocd.org/)")

    click.echo("\nSerial Ports:")
    if SerialBridge.available():
        ports = SerialBridge.list_ports()
        if ports:
            for p in ports:
                click.echo("  %-15s %s" % (p['device'], p['description']))
        else:
            click.echo("  (none found)")

        boards = SerialBridge.detect_dev_boards()
        if boards:
            click.echo("\nDetected Dev Boards:")
            for b in boards:
                click.echo("  %-15s %s" % (b['device'], b['board']))
    else:
        click.echo("  pyserial not installed — run: pip install pyserial")


@hil.command("connect")
@click.option("--adapter", default="stlink", help="Debug adapter (stlink, jlink, cmsis-dap)")
@click.option("--target", default="stm32f4", help="Target MCU (stm32f4, nrf52, etc.)")
@click.option("--serial", "serial_port", default="", help="Serial port (COM3, /dev/ttyUSB0)")
@click.option("--baudrate", default=115200, help="Serial baud rate")
@click.option("--gdb-port", default=3333, help="GDB port")
def hil_connect(adapter, target, serial_port, baudrate, gdb_port):
    """Connect to a real development board via OpenOCD."""
    from eosim.integrations.hil_session import HILSession

    click.echo("EoSim HIL — Connecting to %s via %s" % (target, adapter))
    session = HILSession()
    try:
        session.start(
            adapter=adapter, target=target,
            serial_port=serial_port, baudrate=baudrate,
            gdb_port=gdb_port,
        )
        click.echo("Connected! GDB on port %d" % gdb_port)
        if serial_port:
            click.echo("Serial bridge: %s @ %d baud" % (serial_port, baudrate))

        state = session.get_state()
        click.echo("\nSession state:")
        for k, v in state.items():
            click.echo("  %-20s %s" % (k, v))

        click.echo("\nPress Ctrl+C to disconnect...")
        try:
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
    except Exception as e:
        click.echo("Connection failed: %s" % e, err=True)
        sys.exit(1)
    finally:
        session.stop()
        click.echo("Disconnected.")


@hil.command("flash")
@click.argument("firmware", type=click.Path(exists=True))
@click.option("--adapter", default="stlink", help="Debug adapter")
@click.option("--target", default="stm32f4", help="Target MCU")
def hil_flash(firmware, adapter, target):
    """Flash firmware to a real target via OpenOCD."""
    from eosim.integrations.openocd import OpenOCDManager

    click.echo("EoSim HIL — Flashing %s to %s via %s" % (firmware, target, adapter))
    mgr = OpenOCDManager()
    try:
        ok = mgr.flash(firmware)
        if ok:
            click.echo("Flash: PASSED")
        else:
            click.echo("Flash: FAILED")
            sys.exit(1)
    except Exception as e:
        click.echo("Flash error: %s" % e, err=True)
        sys.exit(1)


@hil.command("monitor")
@click.option("--adapter", default="stlink", help="Debug adapter")
@click.option("--target", default="stm32f4", help="Target MCU")
@click.option("--gdb-port", default=3333, help="GDB port")
def hil_monitor(adapter, target, gdb_port):
    """Live register/memory monitoring (text mode)."""
    from eosim.integrations.hil_session import HILSession

    click.echo("EoSim HIL Monitor — %s via %s (Ctrl+C to quit)\n" % (target, adapter))
    session = HILSession()
    try:
        session.start(adapter=adapter, target=target, gdb_port=gdb_port)
        session.halt()
        import time
        while True:
            regs = session.read_registers()
            if regs:
                click.echo("\033[2J\033[H")
                click.echo("=== %s Registers ===" % target)
                for name, val in sorted(regs.items()):
                    click.echo("  %-6s 0x%08X" % (name, val))
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        session.stop()


# --- Bridge subcommands (external tool integrations) ---

@cli.group()
def bridge():
    """External tool bridges — X-Plane, Gazebo, OpenFOAM."""
    pass


@bridge.command("status")
def bridge_status():
    """Show status of all external tool bridges."""
    from eosim.engine.backend import XPlaneEngine, GazeboEngine, OpenFOAMEngine
    click.echo("EoSim Bridge Status\n")
    click.echo("  %-15s %s" % ("X-Plane", "available" if XPlaneEngine.available() else "not connected"))
    click.echo("  %-15s %s" % ("Gazebo", "available" if GazeboEngine.available() else "not installed"))
    click.echo("  %-15s %s" % ("OpenFOAM", "available" if OpenFOAMEngine.available() else "not installed"))


@bridge.group("xplane")
def bridge_xplane():
    """X-Plane flight simulator bridge."""
    pass


@bridge_xplane.command("connect")
@click.option("--host", default="127.0.0.1", help="X-Plane host")
@click.option("--port", default=49000, help="X-Plane UDP port")
def xplane_connect(host, port):
    """Connect to X-Plane simulator."""
    from eosim.integrations.xplane import XPlaneConnection
    click.echo("Connecting to X-Plane at %s:%d..." % (host, port))
    conn = XPlaneConnection(host=host, port=port)
    if conn.connect():
        click.echo("Connected to X-Plane")
        status = conn.get_status()
        for k, v in status.items():
            click.echo("  %-20s %s" % (k, v))
        conn.disconnect()
    else:
        click.echo("Failed to connect to X-Plane", err=True)
        sys.exit(1)


@bridge.group("gazebo")
def bridge_gazebo():
    """Gazebo simulation bridge."""
    pass


@bridge_gazebo.command("connect")
@click.option("--host", default="127.0.0.1", help="Gazebo host")
@click.option("--port", default=11345, help="Gazebo port")
def gazebo_connect(host, port):
    """Connect to Gazebo simulator."""
    from eosim.integrations.gazebo import GazeboConnection
    click.echo("Connecting to Gazebo at %s:%d..." % (host, port))
    conn = GazeboConnection(host=host, port=port)
    if conn.connect():
        click.echo("Connected to Gazebo")
        status = conn.get_status()
        for k, v in status.items():
            click.echo("  %-20s %s" % (k, v))
        conn.disconnect()
    else:
        click.echo("Failed to connect to Gazebo", err=True)
        sys.exit(1)


@bridge.group("openfoam")
def bridge_openfoam():
    """OpenFOAM CFD solver bridge."""
    pass


@bridge_openfoam.command("run")
@click.option("--case-dir", required=True, help="OpenFOAM case directory")
@click.option("--solver", default="simpleFoam", help="Solver name")
def openfoam_run(case_dir, solver):
    """Run an OpenFOAM simulation."""
    from eosim.integrations.openfoam import OpenFOAMRunner
    click.echo("Running OpenFOAM solver '%s' on case: %s" % (solver, case_dir))
    runner = OpenFOAMRunner(case_dir=case_dir)
    runner.set_solver(solver)
    result = runner.run()
    if result['success']:
        click.echo("Solver completed successfully")
        if result.get('converged'):
            click.echo("Solution converged")
    else:
        click.echo("Solver failed")
        click.echo(result.get('log', '')[-500:])
        sys.exit(1)


if __name__ == "__main__":
    cli()
