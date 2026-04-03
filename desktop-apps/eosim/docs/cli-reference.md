# EoSim CLI Reference

Complete command reference for the `eosim` command-line interface.

## Global Usage

```bash
eosim [OPTIONS] COMMAND [ARGS]...
```

---

## Core Commands

### `eosim list`

List available simulation platforms.

```bash
eosim list [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--arch TEXT` | Filter by architecture |
| `--vendor TEXT` | Filter by vendor |
| `--class TEXT` | Filter by platform class |
| `--engine TEXT` | Filter by engine |
| `--domain TEXT` | Filter by domain |
| `--group-by TEXT` | Group results by field |
| `--format TEXT` | Output format (table, json, csv) |

```bash
eosim list --arch arm --class mcu
eosim list --domain automotive --group-by vendor
```

### `eosim search QUERY`

Search platforms by name, vendor, SoC, or architecture.

```bash
eosim search raspberry
eosim search stm32
```

### `eosim info PLATFORM`

Show detailed platform information.

```bash
eosim info stm32f4
eosim info raspi4
```

### `eosim stats`

Show platform registry statistics.

### `eosim run PLATFORM`

Run a simulation for the specified platform.

| Option | Description |
|--------|-------------|
| `--headless / --interactive` | Display mode (default: headless) |
| `--timeout INTEGER` | Simulation timeout in seconds |
| `--log-dir TEXT` | Directory for simulation logs |

```bash
eosim run stm32f4
eosim run raspi4 --timeout 120
```

### `eosim test PLATFORM`

Run validation tests for a platform.

| Option | Description |
|--------|-------------|
| `--timeout INTEGER` | Test timeout in seconds |
| `--junit / --no-junit` | Generate JUnit XML (default: enabled) |

### `eosim validate [CONFIG]`

Validate a platform configuration file.

| Option | Description |
|--------|-------------|
| `--all` | Validate all platform configurations |

```bash
eosim validate platforms/stm32f4/platform.yml
eosim validate --all
```

### `eosim artifact PLATFORM`

Export simulation artifacts (logs, traces, JUnit XML).

### `eosim doctor`

Check EoSim environment health (Python, engines, probes, platforms).

### `eosim gui`

Launch the EoSim simulation UI (requires display).

---

## Domain Commands

| Command | Description |
|---------|-------------|
| `eosim domain list` | List all simulation domain categories |
| `eosim domain info NAME` | Show detailed domain profile |

```bash
eosim domain info automotive
eosim domain info aerospace
```

---

## Modeling Commands

| Command | Description |
|---------|-------------|
| `eosim modeling list` | List all modeling methods |
| `eosim modeling info NAME` | Show detailed modeling method info |

```bash
eosim modeling info cfd
eosim modeling info monte-carlo
```

---

## EoS Integration Commands

| Command | Description |
|---------|-------------|
| `eosim eos find` | Find EoS source code on this system |
| `eosim eos build` | Build EoS from source |
| `eosim eos test` | Build and run all EoS unit tests |
| `eosim eos test-suite` | Run eApps Python tests |
| `eosim ecosystem` | Test ALL EoS repos end-to-end |

---

## HIL Commands

| Command | Description |
|---------|-------------|
| `eosim hil detect` | Detect connected debug probes and serial ports |
| `eosim hil connect` | Connect to a board via OpenOCD |
| `eosim hil flash FIRMWARE` | Flash firmware to a real target |
| `eosim hil monitor` | Live register/memory monitoring |

See the [HIL Guide](hil-guide.md) for detailed usage.

---

## Bridge Commands

| Command | Description |
|---------|-------------|
| `eosim bridge status` | Show status of all external tool bridges |
| `eosim bridge xplane connect` | Connect to X-Plane simulator |
| `eosim bridge gazebo connect` | Connect to Gazebo simulator |
| `eosim bridge openfoam run` | Run an OpenFOAM simulation |

---

## Command Aliases

| Alias | Equivalent |
|-------|-----------|
| `eosim simulate PLATFORM` | `eosim run PLATFORM` |
| `eosim list-platforms` | `eosim list` |
