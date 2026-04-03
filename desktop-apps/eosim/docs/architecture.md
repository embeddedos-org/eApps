# EoSim Architecture

## Overview

EoSim is a multi-architecture embedded simulation platform that provides a unified interface for simulating firmware across 52+ hardware targets. It supports multiple simulation backends and can operate in fully offline mode using its native engine.

## Layer Diagram

```
┌─────────────────────────────────────────────────────────────┐
│  CLI Layer         eosim list | run | test | validate       │
│                    eosim domain | modeling | hil | bridge    │
├─────────────────────────────────────────────────────────────┤
│  GUI Layer         Tkinter dashboard, 3D renderers,         │
│                    CPU/memory/peripheral panels              │
├─────────────────────────────────────────────────────────────┤
│  Platform Layer    YAML configs → Platform dataclass        │
│                    PlatformRegistry (filter/search/group)    │
├─────────────────────────────────────────────────────────────┤
│  Engine Layer      EoSim native │ Renode │ QEMU │ HIL       │
│                    X-Plane │ Gazebo │ OpenFOAM               │
├─────────────────────────────────────────────────────────────┤
│  Test Layer        run_checks() │ run_scenario()            │
│                    8 check types │ YAML scenarios            │
├─────────────────────────────────────────────────────────────┤
│  Artifact Layer    logs │ traces │ reports │ JUnit XML       │
└─────────────────────────────────────────────────────────────┘
```

## Module Structure

```
eosim/
├── cli/              # Click-based CLI (entry point)
│   └── main.py       # All commands: list, run, test, validate, domain, hil, bridge
├── core/             # Data models and business logic
│   ├── platform.py   # Platform dataclass, BootConfig, discover_platforms()
│   ├── registry.py   # PlatformRegistry — filter, search, group, stats
│   ├── schema.py     # Validation rules (arches, engines, classes, domains)
│   ├── cluster.py    # Multi-node cluster definitions
│   ├── domains.py    # 15 domain profiles (automotive, medical, aerospace, ...)
│   ├── modeling.py   # 10 modeling methods (deterministic, CFD, monte-carlo, ...)
│   ├── host.py       # Host OS detection, QEMU/Renode binary resolution
│   └── jobs.py       # Persistent job queue (.eosim/jobs/)
├── engine/           # Simulation backends
│   ├── backend.py    # 7 engine classes: EoSim, Renode, QEMU, QemuLive, XPlane, Gazebo, OpenFOAM
│   └── native/       # EoSim native engine (zero dependencies)
│       ├── cpu/          # ARM instruction decoder, CPU state, breakpoints
│       ├── memory/       # MemoryBus, MemoryRegion, address-mapped I/O
│       ├── peripherals/  # UART, GPIO, Timer, SPI, I2C, NVIC + domain-specific
│       └── simulators/   # 19 domain simulators (vehicle, aircraft, robot, ...)
├── engine/qemu/      # QEMU integration
│   ├── qmp_client.py     # QMP (QEMU Machine Protocol) client
│   ├── gdb_client.py     # GDB remote protocol client
│   ├── elf_loader.py     # ELF binary parser
│   └── state_bridge.py   # QEMU ↔ EoSim state synchronization
├── gui/              # Tkinter-based dashboard
│   ├── tk_app.py         # Main application window
│   ├── simulator_app.py  # Simulator control interface
│   ├── product_templates.py  # Product-type rendering configs
│   ├── renderers/        # 14 domain-specific 3D renderers
│   └── widgets/          # CPU panel, GPIO, UART terminal, memory view, etc.
├── integrations/     # External tool bridges
│   ├── eos_runner.py     # EoS build/test integration
│   ├── ecosystem.py      # Full ecosystem validation
│   ├── hil_session.py    # Hardware-in-the-loop session management
│   ├── openocd.py        # OpenOCD debug probe interface
│   ├── serial_bridge.py  # Serial port bridge
│   ├── xplane.py         # X-Plane flight simulator bridge
│   ├── gazebo.py         # Gazebo robotics simulator bridge
│   └── openfoam.py       # OpenFOAM CFD solver bridge
├── artifacts/        # Output collection
│   └── collector.py      # Log collection, JUnit XML generation
├── platforms/        # Platform discovery helpers
├── tests/            # Runtime test framework (not pytest)
│   ├── runner.py         # CheckResult, run_checks()
│   └── scenarios.py      # Multi-step scenario runner
└── __main__.py       # python -m eosim entry point
```

## Platform Discovery

EoSim scans `platforms/*/platform.yml` for available simulation targets. Each platform YAML defines:

- **Identity:** `name`, `display_name`, `vendor`, `soc`
- **Architecture:** `arch` (one of 13 supported architectures)
- **Engine:** `engine` (preferred backend: `eosim`, `renode`, `qemu`, `hil`, etc.)
- **Boot assets:** `kernel`, `rootfs`, `dtb`, `firmware`
- **Runtime:** `memory_mb`, `headless`, `uart`, `timeout_s`
- **Classification:** `class` (mcu/sbc/soc/...), `domain` (automotive/medical/...), `modeling` (deterministic/stochastic/...)

Platforms are loaded into a `PlatformRegistry` for filtering, searching, and grouping.

## Engine Selection Cascade

When running a simulation, EoSim selects an engine using this priority:

1. **Explicit:** If the platform specifies `engine: renode` and Renode is installed → use Renode
2. **EoSim Native:** If no external engine is available → use the built-in Python VM
3. **Renode fallback:** If Renode is available → use Renode
4. **QEMU fallback:** If QEMU is available for the target arch → use QEMU
5. **Dry run:** If nothing is available → simulate a successful run (CI-safe)

The `get_engine(platform)` function implements this cascade.

## Native Engine Architecture

The EoSim native engine is a cycle-based ARM simulator written in pure Python:

- **CPUSimulator:** Decodes and executes ARM instructions (NOP, BX, SVC, MOV, LDR, STR, B). Supports breakpoints, watchpoints, and instruction tracing.
- **MemoryBus:** Address-mapped memory regions with I/O handler registration for peripheral access.
- **Peripherals:** UART (serial I/O), GPIO (pin state), Timer (countdown/interrupt), SPI, I2C, NVIC (interrupt controller), plus domain-specific sensors and actuators.
- **VirtualMachine:** Orchestrates CPU + memory + peripherals. Loads firmware binaries, runs simulation cycles, produces `SimResult`.

## Test Check Types

EoSim supports 8 types of test assertions:

| Type | Description |
|------|-------------|
| `serial_contains` | Match a string in UART serial output |
| `exit_code` | Verify process return code |
| `timeout` | Boot completes within time limit |
| `boot_success` | Detect login prompt or boot marker |
| `wait_for` | Wait for a pattern to appear in output |
| `assert_no` | Verify a pattern is absent from output |
| `timing` | Assert duration is within bounds |
| `count_matches` | Count pattern occurrences in output |

## Multi-Node Clusters

Cluster simulations are defined in YAML files with:

- **Nodes:** Each references a platform name and has a role (gateway, sensor, controller, etc.)
- **Links:** Define inter-node communication channels (UART, SPI, network) with baud rate and other config

The `Cluster.from_yaml()` loader validates referential integrity against the platform registry.

## Data Flow

```
platform.yml ──→ Platform.from_yaml() ──→ PlatformRegistry
                                              │
                    ┌─────────────────────────┘
                    ▼
              get_engine(platform) ──→ Engine.run()
                                          │
                                          ▼
                                     SimResult
                                          │
                    ┌─────────────────────┘
                    ▼
              run_checks(result, checks) ──→ CheckResult[]
                                                  │
                                                  ▼
                                         generate_junit()
                                         collect_artifacts()
```

## Extension Points

- **New platforms:** Add a `platforms/<name>/platform.yml` file
- **New engines:** Subclass the engine interface in `engine/backend.py`
- **New peripherals:** Add to `engine/native/peripherals/`
- **New simulators:** Add to `engine/native/simulators/`
- **New GUI renderers:** Add to `gui/renderers/`
- **New integrations:** Add to `integrations/`
