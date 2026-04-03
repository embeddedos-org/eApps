# Hardware-in-the-Loop (HIL) Guide

This guide covers connecting EoSim to real development boards for hardware-in-the-loop testing.

## Overview

EoSim's HIL mode bridges the gap between simulation and real hardware testing. It connects to development boards via debug probes (SWD/JTAG) using OpenOCD, allowing you to:

- Flash firmware to real targets
- Monitor registers and memory in real-time
- Run the same test checks against physical hardware
- Validate simulation accuracy against real behavior

## Prerequisites

- **OpenOCD** — Install from [openocd.org](https://openocd.org/) or your package manager
- **Debug probe** — One of the supported probes (see below)
- **Development board** — Any board with a debug header
- **USB cable** — To connect the debug probe to your computer
- **pyserial** — Install with `pip install eosim[hil]`

### Supported Debug Probes

| Probe | Interface | Notes |
|-------|-----------|-------|
| ST-Link V2/V3 | SWD/JTAG | Built into STM32 Nucleo and Discovery boards |
| J-Link | SWD/JTAG | Segger J-Link (all variants) |
| CMSIS-DAP | SWD | Standard ARM debug interface |
| Black Magic Probe | SWD/JTAG | Open-source probe |
| Raspberry Pi GPIO | SWD | Use RPi GPIO pins as SWD adapter |

## Quick Start

### 1. Connect your hardware

Connect the debug probe to your development board's debug header (SWD or JTAG). Connect the probe to your computer via USB.

### 2. Detect connected probes

```bash
eosim hil detect
```

Output:
```
Debug probes:
  [1] ST-Link V2 (serial: 066BFF343633...)
      Interface: SWD
      Target: STM32F407

Serial ports:
  [1] COM3 / /dev/ttyACM0 (115200 baud)
```

### 3. Connect to the target

```bash
eosim hil connect --probe stlink --target stm32f4x
```

This starts an OpenOCD session and establishes a debug connection.

### 4. Flash firmware

```bash
eosim hil flash firmware.bin --target stm32f4x
```

Options:
- `--verify` — Verify flash after writing
- `--reset` — Reset target after flashing
- `--address 0x08000000` — Specify flash base address

### 5. Monitor in real-time

```bash
eosim hil monitor --target stm32f4x
```

The monitor shows:
- CPU registers (R0-R15, PSR, control registers)
- Memory regions (SRAM, Flash, peripherals)
- UART output (if serial port is connected)
- GPIO pin states

## Wiring Guide

### SWD Connection (4 wires)

```
Debug Probe          Target Board
───────────          ────────────
SWCLK  ────────────  SWCLK
SWDIO  ────────────  SWDIO
GND    ────────────  GND
3.3V   ────────────  VDD (optional, if board is self-powered)
```

### JTAG Connection (5+ wires)

```
Debug Probe          Target Board
───────────          ────────────
TCK    ────────────  TCK
TMS    ────────────  TMS
TDI    ────────────  TDI
TDO    ────────────  TDO
GND    ────────────  GND
TRST   ────────────  TRST (optional)
```

### Serial Console (for UART output)

```
USB-Serial Adapter   Target Board
──────────────────   ────────────
TX     ────────────  RX
RX     ────────────  TX
GND    ────────────  GND
```

## Platform Configuration for HIL

Set `engine: hil` in your platform YAML:

```yaml
name: stm32f4-hil
display_name: STM32F4 Discovery (Real Hardware)
arch: arm
engine: hil
vendor: ST
soc: STM32F407
class: devboard
domain: industrial

boot:
  firmware: build/firmware.bin

runtime:
  timeout_s: 30
  uart: /dev/ttyACM0
```

## Running HIL Tests

Once connected, you can run the same test framework against real hardware:

```bash
eosim test stm32f4-hil
```

This will:
1. Flash firmware to the target
2. Reset and start execution
3. Capture UART output via serial port
4. Run test checks (serial_contains, timeout, boot_success, etc.)
5. Generate test results and JUnit XML

## Troubleshooting

### Probe not detected

- Check USB connection and cable
- Ensure OpenOCD is installed: `openocd --version`
- On Linux, ensure udev rules are installed for your probe
- On Windows, ensure the correct USB driver is installed (WinUSB/libusb)

### Connection fails

- Verify SWD/JTAG wiring (especially GND)
- Check that the target is powered
- Try reducing SWD clock speed: `eosim hil connect --speed 1000`
- Ensure no other debugger is connected to the target

### Flash verification fails

- Ensure the firmware binary matches the target architecture
- Check flash base address (`--address`)
- Try erasing flash first: `eosim hil flash --erase firmware.bin`

### No serial output

- Verify TX/RX wiring (they should be crossed: probe TX → target RX)
- Check baud rate matches firmware configuration
- Ensure the correct serial port is specified in platform config
