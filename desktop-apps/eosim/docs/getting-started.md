# Getting Started with EoSim

This guide walks you through installing EoSim, running your first simulation, and understanding the output.

## Prerequisites

- **Python 3.9+** (3.11 or 3.12 recommended)
- **pip** (comes with Python)
- **Optional:** [QEMU](https://www.qemu.org/) for hardware emulation
- **Optional:** [Renode](https://renode.io/) for advanced peripheral simulation
- **Optional:** [OpenOCD](https://openocd.org/) for hardware-in-the-loop (HIL) testing

> **Note:** EoSim's native engine requires zero external dependencies. You can simulate firmware using only Python.

## Installation

### From GitHub (latest)

```bash
pip install git+https://github.com/embeddedos-org/eosim.git
```

### From source (development)

```bash
git clone https://github.com/embeddedos-org/eosim.git
cd eosim
pip install -e ".[all]"
```

### Install extras

| Extra | What it adds |
|-------|-------------|
| `dev` | pytest, pytest-cov, ruff (for development) |
| `viz` | matplotlib (for visualization) |
| `elf` | pyelftools (for ELF binary loading) |
| `hil` | pyserial (for serial port communication) |
| `all` | Everything above |

```bash
pip install -e ".[dev,viz]"    # specific extras
pip install -e ".[all]"        # everything
```

## Verify Installation

Check that EoSim is installed and your environment is healthy:

```bash
eosim doctor
```

This reports:
- Python version
- Available simulation engines (Renode, QEMU)
- Detected debug probes
- Platform configuration status

## Your First Simulation

### Step 1: List available platforms

```bash
eosim list
```

This shows all 52+ supported platforms organized by architecture. Use filters to narrow down:

```bash
eosim list --arch arm          # ARM Cortex-M/A platforms only
eosim list --vendor ST         # STMicroelectronics boards only
eosim list --domain automotive # Automotive-grade platforms
eosim list --engine eosim      # Platforms with native engine support
```

### Step 2: Inspect a platform

```bash
eosim info stm32f4
```

This shows the platform's architecture, engine, memory, boot configuration, vendor, SoC, domain classification, and available test checks.

### Step 3: Run a simulation

```bash
eosim run stm32f4
```

EoSim will:
1. Load `platforms/stm32f4/platform.yml`
2. Select the best available engine (EoSim native → Renode → QEMU → dry-run)
3. Initialize the virtual machine (CPU, memory, peripherals)
4. Run the simulation
5. Capture serial (UART) output
6. Save logs to `out/logs/`

### Step 4: Run validation tests

```bash
eosim test stm32f4
```

This runs the test checks defined in `platforms/stm32f4/tests.yml` against the simulation output:
- Serial output pattern matching
- Exit code verification
- Boot timeout enforcement
- Boot success detection

### Step 5: Export artifacts

```bash
eosim artifact stm32f4
```

Generates test reports, JUnit XML files, and collects simulation logs.

## Understanding SimResult

Every simulation produces a `SimResult` with:

| Field | Description |
|-------|-------------|
| `platform` | Platform name that was simulated |
| `engine` | Engine used (eosim, renode, qemu, dry-run) |
| `success` | Whether the simulation completed successfully |
| `exit_code` | Process exit code (0 = success) |
| `serial_output` | Captured UART serial output |
| `duration_s` | Simulation duration in seconds |
| `log_file` | Path to the simulation log file |

## Validating Platform Configs

Check a single platform configuration:

```bash
eosim validate platforms/stm32f4/platform.yml
```

Validate all platforms at once:

```bash
eosim validate --all
```

This checks for:
- Required fields (`name`, `arch`, `engine`)
- Valid architecture, engine, class, domain, and modeling values
- Correct data types for runtime configuration

## Using the GUI

Launch the interactive simulation dashboard:

```bash
eosim gui
```

The GUI provides:
- Platform browser with filtering
- Real-time CPU register display
- Memory hex viewer
- UART terminal emulator
- GPIO pin state visualization
- 3D product renderers (14 domain-specific models)
- Peripheral status panels

> **Requires:** A display (X11, Wayland, or Windows desktop). Not available in headless/SSH environments.

## Exploring Domains & Modeling

EoSim categorizes platforms into 15 simulation domains and 10 modeling methods:

```bash
eosim domain list              # List all domains
eosim domain info automotive   # Automotive domain details
eosim modeling list            # List modeling methods
eosim modeling info cfd        # CFD modeling details
```

## Next Steps

- **[Platform Authoring Guide](platform-authoring.md)** — Create your own platform configurations
- **[API Reference](api-reference.md)** — Use EoSim as a Python library
- **[CLI Reference](cli-reference.md)** — Complete CLI command documentation
- **[HIL Guide](hil-guide.md)** — Connect to real hardware
- **[Architecture](architecture.md)** — Understand EoSim's internal design
