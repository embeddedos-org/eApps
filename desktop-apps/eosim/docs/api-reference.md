# EoSim API Reference

EoSim can be used as a Python library for programmatic simulation, platform management, and test automation.

## Core Module (`eosim.core`)

### Platform

The central data model representing a simulation target.

```python
from eosim.core import Platform

platform = Platform.from_yaml("platforms/stm32f4/platform.yml")

print(platform.name)            # "stm32f4"
print(platform.arch)            # "arm"
print(platform.engine)          # "eosim"
print(platform.vendor)          # "ST"
print(platform.soc)             # "STM32F407"
print(platform.domain)          # "industrial"
print(platform.platform_class)  # "mcu"
print(platform.modeling)        # "deterministic"

# Nested configs
print(platform.runtime.memory_mb)   # 128
print(platform.runtime.timeout_s)   # 60
print(platform.boot.firmware)       # path to firmware binary
print(platform.qemu.machine)        # "virt"
```

#### Platform Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Platform identifier |
| `display_name` | `str` | Human-readable name |
| `arch` | `str` | CPU architecture |
| `engine` | `str` | Preferred simulation engine |
| `vendor` | `str` | Hardware vendor |
| `soc` | `str` | System-on-chip identifier |
| `platform_class` | `str` | Platform classification (mcu, sbc, soc, ...) |
| `domain` | `str` | Simulation domain (automotive, medical, ...) |
| `modeling` | `str` | Modeling method (deterministic, cfd, ...) |
| `boot` | `BootConfig` | Kernel, rootfs, DTB, firmware paths |
| `qemu` | `QemuConfig` | QEMU machine, CPU, extra args |
| `runtime` | `RuntimeConfig` | Memory, headless mode, UART, timeout |
| `artifacts` | `ArtifactConfig` | Output directories for logs, traces, reports |
| `checks` | `List[TestCheck]` | Test assertions to run |
| `source_dir` | `str` | Path to platform config directory |

#### Nested Config Types

**BootConfig:** `kernel`, `rootfs`, `dtb`, `firmware`, `initrd`, `append`

**QemuConfig:** `machine` (default: `"virt"`), `cpu`, `extra_args`, `gdb_port` (1234), `qmp_port` (4444), `qmp_socket`, `start_paused`

**RuntimeConfig:** `memory_mb` (512), `headless` (True), `uart` (`"sysbus.uart0"`), `timeout_s` (60)

**ArtifactConfig:** `log_dir` (`"out/logs"`), `trace_dir` (`"out/traces"`), `report_dir` (`"out/reports"`)

### discover_platforms()

Scan a directory for platform YAML configurations.

```python
from eosim.core import discover_platforms

platforms = discover_platforms("platforms/")
# Returns: Dict[str, Platform]

for name, platform in platforms.items():
    print(f"{name}: {platform.arch} ({platform.engine})")
```

### PlatformRegistry

Filterable, searchable catalog of platforms.

```python
from eosim.core import PlatformRegistry

# Create from a directory
registry = PlatformRegistry("platforms/")

# Or from a pre-loaded dict
registry = PlatformRegistry.from_dict(platforms)

# List all
all_platforms = registry.all()      # List[Platform]
count = registry.count()            # int

# Get by name
stm32 = registry.get("stm32f4")    # Optional[Platform]

# Filter by fields
arm_mcus = registry.filter(arch="arm", platform_class="mcu")
st_boards = registry.filter(vendor="ST")
auto_platforms = registry.filter(domain="automotive")

# Fuzzy search across name, vendor, soc, arch
results = registry.search("raspberry")

# Group by any field
by_arch = registry.group_by("arch")     # Dict[str, List[Platform]]
by_vendor = registry.group_by("vendor")

# Statistics
stats = registry.stats()
# Returns: {"arch": {"arm": 15, "arm64": 8, ...}, "vendor": {...}, ...}

# Unique values
registry.vendors()    # ["Espressif", "Nordic", "Raspberry Pi", "ST", ...]
registry.arches()     # ["arc", "arm", "arm64", "mipsel", "riscv64", ...]
registry.classes()    # ["automotive", "devboard", "mcu", "sbc", ...]
registry.engines()    # ["eosim", "hil", "qemu", "renode", ...]
registry.domains()    # ["automotive", "consumer", "industrial", ...]
```

---

## Schema Validation (`eosim.core.schema`)

### validate_platform()

Validate a platform configuration dictionary against the schema.

```python
from eosim.core.schema import validate_platform
import yaml

with open("platforms/stm32f4/platform.yml") as f:
    data = yaml.safe_load(f)

errors = validate_platform(data)
if errors:
    for err in errors:
        print(f"  ERROR: {err}")
else:
    print("Valid!")
```

### Valid Values

| Constant | Values |
|----------|--------|
| `VALID_ARCHES` | `arm64`, `aarch64`, `arm`, `riscv64`, `riscv32`, `x86_64`, `mipsel`, `powerpc`, `xtensa`, `tricore`, `arc`, `microblaze`, `mips` |
| `VALID_ENGINES` | `renode`, `qemu`, `eosim`, `qemu-live`, `hil`, `xplane`, `gazebo`, `openfoam` |
| `VALID_CLASSES` | `mcu`, `mpu`, `soc`, `sbc`, `fpga`, `virtual`, `desktop`, `server`, `devboard`, `automotive`, `safety`, `industrial`, `medical`, `aerospace` |
| `VALID_DOMAINS` | `automotive`, `medical`, `industrial`, `consumer`, `aerospace`, `iot`, `robotics`, `defense`, `energy`, `telecom`, `aerodynamics`, `physiology`, `finance`, `weather`, `gaming` |
| `VALID_MODELING` | `hybrid`, `agent-based`, `cfd`, `monte-carlo`, `finite-element`, `particle-based`, `deterministic`, `continuous`, `discrete-event`, `stochastic` |

---

## Engine Layer (`eosim.engine`)

### SimResult

Result of a simulation run.

```python
from eosim.engine import SimResult

result = SimResult(
    platform="stm32f4",
    engine="eosim",
    success=True,
    exit_code=0,
    serial_output="Booting EoS...\nReady.\n",
    duration_s=2.5,
    log_file="out/logs/stm32f4.log",
)
```

### get_engine()

Select the best available engine for a platform.

```python
from eosim.core import Platform
from eosim.engine import get_engine

platform = Platform.from_yaml("platforms/stm32f4/platform.yml")
engine = get_engine(platform)

result = engine.run(platform)
print(result.success)
print(result.serial_output)
```

### Engine Classes

All engines share a common interface:

| Engine | Import | Description |
|--------|--------|-------------|
| `EoSimEngine` | `from eosim.engine import EoSimEngine` | Native Python VM (always available) |
| `RenodeEngine` | `from eosim.engine import RenodeEngine` | Renode simulation backend |
| `QemuEngine` | `from eosim.engine import QemuEngine` | QEMU system emulation |

```python
engine.available()            # bool — is this engine installed?
engine.run(platform)          # SimResult
```

---

## Native Engine (`eosim.engine.native`)

### VirtualMachine

The EoSim native simulation VM.

```python
from eosim.engine.native import VirtualMachine

vm = VirtualMachine()
vm.load_firmware("firmware.bin")
vm.run(max_cycles=100000, timeout=30)

state = vm.dump_state()
print(state["cpu"])       # CPU register state
print(state["memory"])    # Memory region summary
print(state["uart"])      # UART output buffer
```

---

## Cluster Module (`eosim.core.cluster`)

Multi-node simulation with inter-node communication.

```python
from eosim.core.cluster import Cluster

cluster = Cluster.from_yaml("examples/cluster-demo/cluster.yml")

print(cluster.name)
for node in cluster.nodes:
    print(f"  {node.name}: {node.platform} ({node.role})")

for link in cluster.links:
    print(f"  {link.from_node} --[{link.type}]--> {link.to_node}")

# Validate against platform registry
errors = cluster.validate(platforms)
```

---

## Domain Profiles (`eosim.core.domains`)

```python
from eosim.core.domains import get_domain, list_domains, suggest_platforms

domains = list_domains()

auto = get_domain("automotive")
print(auto.safety_level)
print(auto.standards)
print(auto.typical_arches)
```

---

## Modeling Methods (`eosim.core.modeling`)

```python
from eosim.core.modeling import get_modeling, list_modeling_methods, validate_modeling_for_engine

methods = list_modeling_methods()

cfd = get_modeling("cfd")
print(cfd.description)
print(cfd.compatible_engines)
print(cfd.parameters)

is_valid = validate_modeling_for_engine("cfd", "openfoam")  # True
```

---

## Test Framework (`eosim.tests`)

### run_checks()

Validate a `SimResult` against a list of test checks.

```python
from eosim.tests import run_checks, CheckResult

checks = [
    {"type": "serial_contains", "value": "Booting EoS"},
    {"type": "exit_code", "value": "0"},
    {"type": "timeout", "seconds": 60},
]

results = run_checks(sim_result, checks)
for r in results:
    print(f"  {'PASS' if r.passed else 'FAIL'}: {r.check_type} — {r.message}")
```

---

## Artifacts (`eosim.artifacts`)

```python
from eosim.artifacts import collect_artifacts, generate_junit

# Collect simulation logs and traces
artifacts = collect_artifacts(sim_result)

# Generate JUnit XML for CI integration
generate_junit(check_results, output_path="out/reports/junit.xml")
```

---

## Job Queue (`eosim.core.jobs`)

Persistent job queue for batch simulation management.

```python
from eosim.core.jobs import JobQueue

queue = JobQueue()
job_id = queue.submit(platform="stm32f4", engine="eosim")

job = queue.get(job_id)
print(job.status)

pending = queue.list_jobs(status="pending")
queue.update(job_id, status="completed")
```

---

## Host Environment (`eosim.core.host`)

Detect host OS capabilities and resolve tool paths.

```python
from eosim.core.host import HostEnvironment

host = HostEnvironment()
print(host.os_name)          # "Linux", "Windows", "macOS"
print(host.is_ci)            # True if running in CI
print(host.is_wsl)           # True if running in WSL

qemu = host.resolve_qemu("arm")     # Path to qemu-system-arm
renode = host.resolve_renode()        # Path to renode binary
arches = host.supported_arches()      # List of QEMU-supported arches
```
