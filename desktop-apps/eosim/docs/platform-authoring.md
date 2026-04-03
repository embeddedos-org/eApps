# Platform Authoring Guide

This guide explains how to create new platform configurations for EoSim.

## Platform Directory Structure

Each platform lives in its own directory under `platforms/`:

```
platforms/
└── my-board/
    ├── platform.yml    # Platform configuration (required)
    └── tests.yml       # Test checks (optional)
```

## platform.yml Reference

### Minimal Example

```yaml
name: my-board
arch: arm
engine: eosim
```

### Full Example

```yaml
name: my-board
display_name: My Custom Board
arch: arm
engine: eosim
vendor: Acme Corp
soc: ACM32F407
class: mcu
domain: industrial
modeling: deterministic

boot:
  firmware: firmware.bin
  kernel: ""
  rootfs: ""
  dtb: ""

runtime:
  memory_mb: 256
  headless: true
  uart: sysbus.uart0
  timeout_s: 60

qemu:
  machine: virt
  cpu: cortex-m4
  extra_args: []

artifacts:
  log_dir: out/logs
  trace_dir: out/traces
  report_dir: out/reports
```

### Field Reference

#### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Unique platform identifier (use lowercase with hyphens) |
| `arch` | string | CPU architecture (see valid values below) |
| `engine` | string | Preferred simulation engine |

#### Optional Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `display_name` | string | `""` | Human-readable platform name |
| `vendor` | string | `""` | Hardware vendor name |
| `soc` | string | `""` | System-on-chip identifier |
| `class` | string | `""` | Platform classification |
| `domain` | string | `""` | Simulation domain |
| `modeling` | string | `""` | Modeling method |
| `repl` | string | `""` | Renode platform description file path |
| `resc` | string | `""` | Renode script file path |

### Valid Values

**Architectures (`arch`):**
`arm64`, `aarch64`, `arm`, `riscv64`, `riscv32`, `x86_64`, `mipsel`, `powerpc`, `xtensa`, `tricore`, `arc`, `microblaze`, `mips`

**Engines (`engine`):**
`eosim` (native), `renode`, `qemu`, `qemu-live`, `hil`, `xplane`, `gazebo`, `openfoam`

**Classes (`class`):**
`mcu`, `mpu`, `soc`, `sbc`, `fpga`, `virtual`, `desktop`, `server`, `devboard`, `automotive`, `safety`, `industrial`, `medical`, `aerospace`

**Domains (`domain`):**
`automotive`, `medical`, `industrial`, `consumer`, `aerospace`, `iot`, `robotics`, `defense`, `energy`, `telecom`, `aerodynamics`, `physiology`, `finance`, `weather`, `gaming`

**Modeling (`modeling`):**
`deterministic`, `stochastic`, `discrete-event`, `continuous`, `hybrid`, `agent-based`, `cfd`, `monte-carlo`, `finite-element`, `particle-based`

## tests.yml Reference

Test files define assertions to validate simulation output.

### Example

```yaml
checks:
  - type: serial_contains
    value: "Booting EoS"
  - type: exit_code
    value: "0"
  - type: timeout
    seconds: 30
  - type: boot_success
    value: "login:"
```

### Check Types

| Type | Fields | Description |
|------|--------|-------------|
| `serial_contains` | `value` | Assert UART output contains the given string |
| `exit_code` | `value` | Assert process exit code matches (as string) |
| `timeout` | `seconds` | Assert simulation completes within N seconds |
| `boot_success` | `value` | Assert boot marker (e.g., login prompt) appears |
| `wait_for` | `value`, `seconds` | Wait up to N seconds for pattern to appear |
| `assert_no` | `value` | Assert pattern is NOT present in output |
| `timing` | `min_seconds`, `max_seconds` | Assert duration is within bounds |
| `count_matches` | `value`, `count` | Assert pattern appears exactly N times |

## Step-by-Step: Creating a New Platform

### 1. Create the platform directory

```bash
mkdir platforms/my-board
```

### 2. Create platform.yml

```bash
cat > platforms/my-board/platform.yml << 'EOF'
name: my-board
display_name: My Custom Board
arch: arm
engine: eosim
vendor: Acme Corp
soc: ACM32F407
class: mcu
domain: industrial
modeling: deterministic
runtime:
  memory_mb: 128
  timeout_s: 30
EOF
```

### 3. Validate the configuration

```bash
eosim validate platforms/my-board/platform.yml
```

### 4. Add test checks (optional)

```bash
cat > platforms/my-board/tests.yml << 'EOF'
checks:
  - type: serial_contains
    value: "Ready"
  - type: exit_code
    value: "0"
EOF
```

### 5. Verify the platform appears

```bash
eosim list | grep my-board
eosim info my-board
```

### 6. Run a simulation

```bash
eosim run my-board
eosim test my-board
```

## Using the Template

A template platform directory is available at `platforms/templates/` that you can copy and customize:

```bash
cp -r platforms/templates/custom platforms/my-board
# Edit platforms/my-board/platform.yml
```

## Cluster Definitions

For multi-node simulations, create a cluster YAML file:

```yaml
name: my-cluster
nodes:
  - name: gateway
    platform: raspi4
    role: gateway
  - name: sensor-1
    platform: stm32f4
    role: sensor

links:
  - type: uart
    from: gateway
    to: sensor-1
    config:
      baud: 115200
```

Run with:

```bash
eosim run --cluster my-cluster.yml
```

See `examples/cluster-demo/` for working examples.
