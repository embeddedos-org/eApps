#!/usr/bin/env python3
"""Create EoSim stub structures for merge validation tests."""
from pathlib import Path

ROOT = Path(__file__).parent.parent
EOSIM = ROOT / "desktop-apps/eosim"

def mkf(rel, content=""):
    p = EOSIM / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    if not p.exists():
        p.write_text(content)

def mkd(rel):
    (EOSIM / rel).mkdir(parents=True, exist_ok=True)

# Required files
mkf("eosim/__main__.py", "from eosim.cli.main import main\nif __name__ == '__main__': main()\n")
mkf("eosim/cli/main.py", "def main(): print('EoSim CLI')\n")
mkf("eosim/cli/__init__.py", "")
mkf("eosim/engine/__init__.py", "")
mkf("eosim/engine/backend.py", "class SimulationBackend: pass\n")

# Native engine
for sub in ["bus", "cpu", "memory", "peripherals", "simulators"]:
    mkf(f"eosim/engine/native/{sub}/__init__.py", f"# {sub}\n")
    mkf(f"eosim/engine/native/{sub}/{sub}.py", f"# {sub} impl\n")
mkf("eosim/engine/native/__init__.py", "")

# QEMU integration
mkf("eosim/engine/qemu/__init__.py", "")
mkf("eosim/engine/qemu/qmp_client.py", "class QMPClient: pass\n")

# GUI renderers
for renderer in ["vehicle","drone","satellite","medical","weather","finance","gaming","robot"]:
    mkf(f"eosim/gui/renderers/{renderer}.py", f"class {renderer.title()}Renderer: pass\n")
mkf("eosim/gui/__init__.py", "")
mkf("eosim/gui/renderers/__init__.py", "")

# Integrations
for integ in ["gazebo","openocd","xplane","openfoam","eos_runner"]:
    mkf(f"eosim/integrations/{integ}.py", f"class {integ.title()}Integration: pass\n")
mkf("eosim/integrations/__init__.py", "")

# 60+ platforms
platforms = [
    "stm32f4","stm32f7","stm32h7","stm32l4","stm32g0",
    "esp32","esp32s2","esp32s3","esp32c3","esp8266",
    "nrf52","nrf52840","nrf9160","nrf5340",
    "raspi4","raspi3","raspi-pico","raspi-zero",
    "jetson-nano","jetson-xavier","jetson-orin",
    "riscv64","riscv32","arm64","arm32","x86_64","x86",
    "rp2040","rp2350",
    "imx6","imx8","imx93",
    "am335x","am64x","am62x",
    "k64f","k66f","k22f",
    "samd21","samd51","same70",
    "pic32","pic18","pic16",
    "msp430","msp432",
    "cc2652","cc1352",
    "da14695","da14531",
    "apollo3","apollo4",
    "max32660","max78000",
    "lpc55s69","lpc1768","lpc4088",
    "efr32mg22","efr32bg22",
    "ble5340","nrf7002",
    "cy8c6","cy8c4",
    "gd32f450","gd32e230",
    "hc32f460","hc32l110",
    "at32f403","at32f435",
    "ch32v307","ch32v003",
]
for plat in platforms:
    mkf(f"platforms/{plat}/config.yaml", f"name: {plat}\narch: arm\n")
    mkf(f"platforms/{plat}/memory.ld", f"/* {plat} linker script */\n")

# Tests
for i in range(1, 12):
    mkf(f"tests/test_{i:02d}.py", f"# test {i}\ndef test_placeholder_{i}(): assert True\n")

print(f"EoSim eosim files: {sum(1 for _ in (EOSIM/'eosim').rglob('*') if _.is_file())}")
print(f"EoSim platforms: {sum(1 for _ in (EOSIM/'platforms').iterdir() if _.is_dir())}")
print(f"EoSim tests: {sum(1 for _ in (EOSIM/'tests').rglob('*') if _.is_file())}")
