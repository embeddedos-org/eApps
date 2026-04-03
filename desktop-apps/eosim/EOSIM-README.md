# 🖥 EoSim — Multi-Architecture Embedded Simulation Platform

[![CI](https://github.com/embeddedos-org/eosim/actions/workflows/ci.yml/badge.svg)](https://github.com/embeddedos-org/eosim/actions/workflows/ci.yml)
[![Nightly](https://github.com/embeddedos-org/eosim/actions/workflows/nightly.yml/badge.svg)](https://github.com/embeddedos-org/eosim/actions/workflows/nightly.yml)
[![Release](https://github.com/embeddedos-org/eosim/actions/workflows/release.yml/badge.svg)](https://github.com/embeddedos-org/eosim/actions/workflows/release.yml)
[![Version](https://img.shields.io/github/v/tag/embeddedos-org/eosim?label=version)](https://github.com/embeddedos-org/eosim/releases/latest)

**Simulate, validate, and test embedded systems before hardware is ready.**

EoSim is the simulation and validation platform for the EmbeddedOS ecosystem — supporting **52+ platforms** across **12 architectures** with native Python simulation engine, Renode support, GUI dashboard, cluster simulation, and CI-native configuration-driven testing.

## Install

```bash
pip install git+https://github.com/embeddedos-org/eosim.git
```

## Quick Start

```bash
eosim list                        # show available platforms
eosim info arm64-linux            # platform details
eosim run arm64-linux             # launch simulation
eosim test arm64-linux            # run validation tests
eosim doctor                      # check environment
eosim stats                       # platform registry statistics
eosim gui stm32f4                 # open GUI dashboard
```

## Supported Platforms (52+)

### ARM Cortex-M (MCU)

| Platform | SoC | Description |
|---|---|---|
| `stm32f4` | STM32F407 | Cortex-M4F, 168 MHz, FPU |
| `stm32h7` | STM32H743 | Cortex-M7, 480 MHz, Dual-core |
| `stm32l4` | STM32L4xx | Cortex-M4, Ultra-low-power |
| `nrf52` | nRF52840 | Cortex-M4F, BLE 5.0 |
| `nrf5340` | nRF5340 | Cortex-M33, Dual-core, BLE 5.3 |
| `nrf9160` | nRF9160 | Cortex-M33, LTE-M/NB-IoT |
| `samd51` | ATSAMD51 | Cortex-M4F, Arduino/Adafruit |
| `samc21` | ATSAMC21 | Cortex-M0+, CAN, Industrial |
| `k64f` | MK64FN1M0 | Cortex-M4F, Ethernet |
| `rp2040` | RP2040 | Dual Cortex-M0+, PIO |
| `psoc6` | PSoC 6 | Cortex-M4F + M0+, BLE |
| `s32k344` | S32K344 | Cortex-M7, Automotive CAN-FD |
| `renesas-ra6m5` | RA6M5 | Cortex-M33, TrustZone |

### ARM Cortex-A (Application Processors)

| Platform | SoC | Description |
|---|---|---|
| `raspi2b` | BCM2836 | Cortex-A7, Quad-core |
| `raspi3` | BCM2837 | Cortex-A53, 64-bit |
| `raspi4` | BCM2711 | Cortex-A72, 4-core, 8GB |
| `raspi5` | BCM2712 | Cortex-A76, 4-core |
| `raspi-zero2w` | BCM2710A1 | Cortex-A53, Compact |
| `imx8m` | i.MX8M | Cortex-A53, NPU, 4K |
| `am64x` | AM6442 | Cortex-A53 + R5F, Industrial |
| `stm32mp1` | STM32MP1 | Cortex-A7 + M4, Linux |
| `jetson-nano` | Tegra X1 | Cortex-A57, 128 CUDA |
| `jetson-orin` | Orin | Cortex-A78AE, 40 TOPS |
| `arm-vexpress` | Versatile Express | Cortex-A9/A15 development |
| `vexpress-a9` | VExpress A9 | Cortex-A9 QEMU target |
| `vexpress-a15` | VExpress A15 | Cortex-A15 QEMU target |
| `arm64` | Generic | AArch64 Linux |
| `arm-mcu` | Generic | ARM MCU reference |
| `beaglebone` | AM335x | Cortex-A8, PRU |

### RISC-V

| Platform | SoC | Description |
|---|---|---|
| `riscv64` | Generic | RISC-V 64-bit Linux |
| `sifive_u` | FU740 | RISC-V U74, Linux-capable |
| `esp32c3` | ESP32-C3 | RISC-V, Wi-Fi/BLE, Single-core |
| `kendryte-k210` | K210 | Dual-core RISC-V, AI |
| `gd32vf103` | GD32VF103 | RISC-V, 108 MHz, USB OTG |

### Xtensa

| Platform | SoC | Description |
|---|---|---|
| `esp32` | ESP32 | Xtensa LX6, Wi-Fi/BLE, Dual-core |
| `esp32s3` | ESP32-S3 | Xtensa LX7, AI acceleration |
| `xtensa-esp` | Generic | Xtensa ESP reference |

### x86 / MIPS / PowerPC / Other

| Platform | Arch | Description |
|---|---|---|
| `x86_64` | x86_64 | Generic Linux on q35 |
| `qemu-q35` | x86_64 | QEMU Q35 chipset |
| `mipsel` | MIPS | MIPS little-endian |
| `ppce500` | PowerPC | PowerPC e500 |
| `microblaze` | MicroBlaze | Xilinx soft-core FPGA |
| `arc-em` | ARC EM | Synopsys ARC |
| `versatilepb` | ARM | ARM Versatile PB |
| `pic32mz` | MIPS | Microchip PIC32MZ |
| `ti-msp432` | ARM | TI MSP432 |
| `ti-tms570` | ARM | TI TMS570 Safety MCU |

### Automotive / Safety

| Platform | SoC | Description |
|---|---|---|
| `aurix-tc3xx` | AURIX TC3xx | TriCore, Automotive safety |
| `renesas-rh850` | RH850 | Automotive MCU |
| `cortex-r5` | Generic | Cortex-R5 safety MCU |
| `cortex-r52` | Generic | Cortex-R52 safety MCU |

### Specialty Simulators

| Platform | Type | Description |
|---|---|---|
| `aerodynamics-sim` | Physics | Aerodynamics simulation |
| `finance-sim` | Domain | Financial modeling |
| `gaming-sim` | Domain | Game engine simulation |
| `physiology-sim` | Domain | Physiological simulation |
| `weather-sim` | Domain | Weather modeling |

## CLI Commands

| Command | Description |
|---|---|
| `eosim list` | List available simulation platforms (filterable by arch, vendor, class, engine) |
| `eosim info <platform>` | Show platform details (CPU, memory, peripherals) |
| `eosim run <platform>` | Run simulation (headless or interactive) |
| `eosim test <platform>` | Run validation tests |
| `eosim validate <config>` | Validate platform config file |
| `eosim artifact <platform>` | Export simulation artifacts |
| `eosim doctor` | Check environment health |
| `eosim stats` | Platform registry statistics |
| `eosim search <query>` | Fuzzy search platforms |
| `eosim gui [platform]` | Open GUI dashboard |

## Architecture

```
eosim/
├── eosim/
│   ├── cli/              CLI entry point (click-based)
│   ├── core/             Core simulation logic
│   ├── engine/           Backend engines (EoSim native, Renode)
│   ├── gui/              Tkinter GUI dashboard
│   ├── integrations/     External tool integrations
│   ├── artifacts/        Simulation artifact management
│   └── platforms/        Platform abstraction
├── platforms/            52+ platform definitions (YAML + Renode .repl/.resc)
│   ├── stm32f4/          STM32F4 Discovery
│   ├── raspi4/           Raspberry Pi 4
│   ├── esp32/            ESP32
│   ├── riscv64/          RISC-V 64-bit
│   ├── jetson-orin/      NVIDIA Jetson Orin
│   └── ...               + 47 more
├── tests/                Unit + integration + scenario tests
├── examples/             Demo scenarios (cluster-demo)
├── pyproject.toml        Python package configuration
└── pytest.ini            Test configuration
```

## Platform Definition Format

```yaml
name: arm64-linux
display_name: ARM64 Generic Linux
arch: arm64
engine: renode
simulation:
  machine: virt
  cpu: cortex-a57
boot:
  kernel: images/arm64-Image
  rootfs: images/arm64-rootfs.ext4
runtime:
  memory_mb: 2048
  headless: true
  uart: sysbus.uart0
```

## Engines

| Engine | Type | Speed | Fidelity | Use Case |
|---|---|---|---|---|
| **EoSim native** | Python simulation | Fast | Medium | Rapid prototyping, CI testing, peripheral logic |
| **Renode** | Deterministic sim | Medium | High | Peripheral-accurate, multi-node, deterministic |
| **QEMU** | Binary emulation | Medium | High | Full firmware on emulated CPU |
| **HIL** | Hardware-in-loop | Real-time | Exact | Real hardware via debug probe |

## GUI Dashboard

The optional Tkinter GUI provides:
- **GPIO panel** — pin visualizer with click-to-toggle
- **UART terminal** — real-time serial output
- **CPU state panel** — registers, PC, SP, flags, clock
- **Memory view** — hex dump of RAM/Flash regions
- **Peripheral registers** — TIM, ADC, SPI, I2C config
- **3D renderers** — drone, robot, vehicle, aircraft, medical, satellite

## EoS Ecosystem

| Repo | Description |
|---|---|
| [eos](https://github.com/embeddedos-org/eos) | Embedded OS — HAL, RTOS kernel, drivers, services |
| [eboot](https://github.com/embeddedos-org/eboot) | Bootloader — 24 board ports, secure boot, A/B slots |
| [ebuild](https://github.com/embeddedos-org/ebuild) | Build system — SDK generator, packaging |
| [eipc](https://github.com/embeddedos-org/eipc) | IPC framework — Go + C SDK, HMAC auth |
| [eai](https://github.com/embeddedos-org/eai) | AI layer — LLM inference, agent loop |
| [eni](https://github.com/embeddedos-org/eni) | Neural interface — BCI, Neuralink adapter |
| [eApps](https://github.com/embeddedos-org/eApps) | Cross-platform apps — 38 C + LVGL apps |
| [EoStudio](https://github.com/embeddedos-org/EoStudio) | Design suite — 10 editors with LLM integration |
| **EoSim** | **Simulation platform (this repo)** |

## Standards Compliance

This project is part of the EoS ecosystem and aligns with international standards including ISO/IEC/IEEE 15288:2023, ISO/IEC 12207, ISO/IEC/IEEE 42010, ISO/IEC 25000, ISO/IEC 25010, ISO/IEC 27001, ISO/IEC 15408, IEC 61508, ISO 26262, DO-178C, FIPS 140-3, POSIX (IEEE 1003), WCAG 2.1, and more. See the [EoS Compliance Documentation](https://github.com/embeddedos-org/.github/tree/master/docs/compliance) for full details including NTIA SBOM, SPDX, CycloneDX, and OpenChain compliance.

## License

MIT License — see [LICENSE](LICENSE) for details.
