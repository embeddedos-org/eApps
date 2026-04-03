"""Device tree generator for Linux and Zephyr targets.

Converts board configuration dictionaries into standards-compliant Device Tree
Source (.dts), Device Tree Source Include (.dtsi), and Zephyr overlay (.overlay)
files.  Supports ARM Cortex-M, Cortex-A, RISC-V, and Xtensa architectures with
pre-built architecture templates.
"""

from __future__ import annotations

import textwrap
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


# ------------------------------------------------------------------
# Data model
# ------------------------------------------------------------------

@dataclass
class DeviceTreeNode:
    """A single node in a device tree hierarchy."""

    name: str
    compatible: str = ""
    reg: List[Tuple[int, int]] = field(default_factory=list)
    status: str = "okay"
    properties: Dict[str, Any] = field(default_factory=dict)
    children: List["DeviceTreeNode"] = field(default_factory=list)

    def add_child(self, child: "DeviceTreeNode") -> "DeviceTreeNode":
        self.children.append(child)
        return child

    def find(self, name: str) -> Optional["DeviceTreeNode"]:
        """Depth-first search for a node by name."""
        if self.name == name:
            return self
        for c in self.children:
            hit = c.find(name)
            if hit is not None:
                return hit
        return None


# ------------------------------------------------------------------
# Architecture templates
# ------------------------------------------------------------------

ARCH_TEMPLATES: Dict[str, Dict[str, Any]] = {
    "arm-cortex-m": {
        "model": "ARM Cortex-M MCU",
        "compatible": "arm,cortex-m",
        "#address-cells": 1,
        "#size-cells": 1,
        "cpu": {
            "compatible": "arm,cortex-m4",
            "reg": (0, 0),
            "clock-frequency": 168000000,
        },
        "nvic": {
            "compatible": "arm,v7m-nvic",
            "#interrupt-cells": 2,
            "interrupt-controller": True,
        },
        "systick": {
            "compatible": "arm,armv7m-systick",
        },
    },
    "arm-cortex-a": {
        "model": "ARM Cortex-A SoC",
        "compatible": "arm,cortex-a",
        "#address-cells": 2,
        "#size-cells": 2,
        "cpu": {
            "compatible": "arm,cortex-a53",
            "reg": (0, 0),
            "clock-frequency": 1200000000,
            "device_type": "cpu",
        },
        "gic": {
            "compatible": "arm,gic-400",
            "#interrupt-cells": 3,
            "interrupt-controller": True,
        },
        "timer": {
            "compatible": "arm,armv8-timer",
        },
    },
    "riscv": {
        "model": "RISC-V SoC",
        "compatible": "riscv",
        "#address-cells": 2,
        "#size-cells": 2,
        "cpu": {
            "compatible": "riscv",
            "reg": (0, 0),
            "riscv,isa": "rv64imafdc",
            "device_type": "cpu",
        },
        "plic": {
            "compatible": "riscv,plic0",
            "#interrupt-cells": 1,
            "interrupt-controller": True,
        },
        "clint": {
            "compatible": "riscv,clint0",
        },
    },
    "xtensa": {
        "model": "Xtensa SoC",
        "compatible": "cdns,xtensa",
        "#address-cells": 1,
        "#size-cells": 1,
        "cpu": {
            "compatible": "cdns,tensilica-xtensa-lx7",
            "reg": (0, 0),
            "clock-frequency": 240000000,
        },
        "intc": {
            "compatible": "cdns,xtensa-intc",
            "#interrupt-cells": 1,
            "interrupt-controller": True,
        },
    },
}


# ------------------------------------------------------------------
# Generator
# ------------------------------------------------------------------

class DeviceTreeGenerator:
    """Generates Device Tree source files from board configurations."""

    # ---- construction from board config ----

    @staticmethod
    def from_board_config(config: dict) -> DeviceTreeNode:
        """Convert a board configuration dictionary into a DT node hierarchy.

        Expected *config* keys:
            name, arch, cpu, clock_mhz, memory (list of {name, base, size}),
            peripherals (list of {type, name, base, size, irq, ...}),
            chosen (dict), aliases (dict).
        """
        arch = config.get("arch", "arm-cortex-m")
        tmpl = ARCH_TEMPLATES.get(arch, ARCH_TEMPLATES["arm-cortex-m"])

        root = DeviceTreeNode(
            name="/",
            compatible=config.get("compatible", tmpl.get("compatible", "")),
            properties={
                "model": config.get("name", tmpl.get("model", "Board")),
                "#address-cells": tmpl.get("#address-cells", 1),
                "#size-cells": tmpl.get("#size-cells", 1),
            },
        )

        # chosen
        chosen_data = config.get("chosen", {})
        chosen_props: Dict[str, Any] = {}
        if "stdout-path" not in chosen_data:
            chosen_props["stdout-path"] = "&uart0"
        chosen_props.update(chosen_data)
        root.add_child(DeviceTreeNode(name="chosen", properties=chosen_props))

        # aliases
        alias_data = config.get("aliases", {})
        if alias_data:
            root.add_child(DeviceTreeNode(name="aliases", properties=alias_data))

        # cpus
        cpus_node = root.add_child(DeviceTreeNode(
            name="cpus",
            properties={"#address-cells": 1, "#size-cells": 0},
        ))
        cpu_info = tmpl.get("cpu", {})
        cpu_compat = config.get("cpu", cpu_info.get("compatible", "arm,cortex-m4"))
        clock_hz = config.get("clock_mhz", 168) * 1_000_000
        cpu_props: Dict[str, Any] = {"device_type": "cpu", "clock-frequency": clock_hz}
        if "riscv,isa" in cpu_info:
            cpu_props["riscv,isa"] = cpu_info["riscv,isa"]
        cpus_node.add_child(DeviceTreeNode(
            name="cpu@0",
            compatible=cpu_compat,
            reg=[(0, 0)],
            properties=cpu_props,
        ))

        # memory
        for mem in config.get("memory", [{"name": "sram", "base": 0x20000000, "size": 0x20000}]):
            base = mem.get("base", 0x20000000)
            size = mem.get("size", 0x20000)
            root.add_child(DeviceTreeNode(
                name=f"memory@{base:x}",
                compatible="mmio-sram" if "sram" in mem.get("name", "").lower() else "memory",
                reg=[(base, size)],
                properties={"device_type": "memory"},
            ))

        # soc node for peripherals
        soc = root.add_child(DeviceTreeNode(
            name="soc",
            compatible="simple-bus",
            properties={
                "#address-cells": tmpl.get("#address-cells", 1),
                "#size-cells": tmpl.get("#size-cells", 1),
                "ranges": True,
            },
        ))

        # interrupt controller
        for ic_key in ("nvic", "gic", "plic", "intc"):
            ic = tmpl.get(ic_key)
            if ic:
                ic_node = DeviceTreeNode(
                    name=ic_key,
                    compatible=ic["compatible"],
                    properties={
                        k: v for k, v in ic.items() if k != "compatible"
                    },
                )
                soc.add_child(ic_node)
                break

        # peripherals
        _PERIPH_COMPAT = {
            "uart": "ns16550",
            "spi": "arm,pl022",
            "i2c": "snps,designware-i2c",
            "gpio": "arm,pl061",
            "adc": "st,stm32-adc",
            "pwm": "st,stm32-pwm",
            "timer": "arm,sp804",
            "can": "bosch,m_can",
            "ethernet": "snps,dwmac",
            "usb": "snps,dwc2",
            "dma": "arm,pl330",
            "watchdog": "arm,sp805",
            "rtc": "arm,pl031",
        }

        for periph in config.get("peripherals", []):
            ptype = periph.get("type", "uart")
            pname = periph.get("name", f"{ptype}0")
            base = periph.get("base", 0x40000000)
            size = periph.get("size", 0x400)
            irq = periph.get("irq")
            props: Dict[str, Any] = {}
            if irq is not None:
                props["interrupts"] = [irq]
            if periph.get("clock"):
                props["clock-frequency"] = periph["clock"]
            props.update({
                k: v for k, v in periph.items()
                if k not in ("type", "name", "base", "size", "irq", "clock")
            })
            soc.add_child(DeviceTreeNode(
                name=f"{pname}@{base:x}",
                compatible=periph.get("compatible", _PERIPH_COMPAT.get(ptype, f"vendor,{ptype}")),
                reg=[(base, size)],
                status=periph.get("status", "okay"),
                properties=props,
            ))

        return root

    # ---- serialisation helpers ----

    @classmethod
    def _format_value(cls, val: Any) -> str:
        """Format a property value for DTS output."""
        if isinstance(val, bool):
            return ""  # boolean property, no value
        if isinstance(val, int):
            return f"<0x{val:x}>"
        if isinstance(val, str):
            if val.startswith("&") or val.startswith("/"):
                return f"{val}"
            return f'"{val}"'
        if isinstance(val, (list, tuple)):
            if all(isinstance(v, int) for v in val):
                inner = " ".join(f"0x{v:x}" for v in val)
                return f"<{inner}>"
            parts = ", ".join(cls._format_value(v) for v in val)
            return parts
        return str(val)

    @classmethod
    def _node_to_lines(cls, node: DeviceTreeNode, indent: int = 0) -> List[str]:
        """Recursively render a node and its children to DTS source lines."""
        pad = "\t" * indent
        lines: List[str] = []

        # node header
        if node.name == "/":
            lines.append(f"{pad}/ {{")
        else:
            lines.append(f"{pad}{node.name} {{")

        inner = "\t" * (indent + 1)

        # compatible
        if node.compatible:
            lines.append(f'{inner}compatible = "{node.compatible}";')

        # reg
        if node.reg:
            if len(node.reg) == 1:
                base, size = node.reg[0]
                lines.append(f"{inner}reg = <0x{base:x} 0x{size:x}>;")
            else:
                parts = " ".join(f"0x{b:x} 0x{s:x}" for b, s in node.reg)
                lines.append(f"{inner}reg = <{parts}>;")

        # status (only if not root)
        if node.name != "/" and node.status:
            lines.append(f'{inner}status = "{node.status}";')

        # properties
        for key, val in node.properties.items():
            if isinstance(val, bool) and val:
                lines.append(f"{inner}{key};")
            elif isinstance(val, bool) and not val:
                continue
            else:
                formatted = cls._format_value(val)
                lines.append(f"{inner}{key} = {formatted};")

        # children
        for child in node.children:
            lines.append("")
            lines.extend(cls._node_to_lines(child, indent + 1))

        lines.append(f"{pad}}};")
        return lines

    # ---- public API ----

    @classmethod
    def to_dts(cls, root: DeviceTreeNode) -> str:
        """Generate a complete .dts source file."""
        header = [
            "/dts-v1/;",
            "",
            "/*",
            f" * Device Tree Source for {root.properties.get('model', 'Board')}",
            " * Auto-generated by EoStudio",
            " */",
            "",
        ]
        body = cls._node_to_lines(root, indent=0)
        return "\n".join(header + body) + "\n"

    @classmethod
    def to_dtsi(cls, root: DeviceTreeNode) -> str:
        """Generate a .dtsi include file (no /dts-v1/ header)."""
        header = [
            "/*",
            f" * Device Tree Source Include for {root.properties.get('model', 'Board')}",
            " * Auto-generated by EoStudio",
            " */",
            "",
        ]
        body = cls._node_to_lines(root, indent=0)
        return "\n".join(header + body) + "\n"

    @classmethod
    def to_overlay(cls, changes: List[Dict[str, Any]]) -> str:
        """Generate a Zephyr .overlay file from a list of node changes.

        Each change dict should contain:
            path: str — node path (e.g. "&uart0", "/soc/spi@40003000")
            status: str — "okay" or "disabled" (optional)
            properties: dict — properties to override (optional)
        """
        lines = [
            "/*",
            " * Zephyr Device Tree Overlay",
            " * Auto-generated by EoStudio",
            " */",
            "",
        ]

        for change in changes:
            path = change.get("path", "")
            lines.append(f"{path} {{")
            if "status" in change:
                lines.append(f'\tstatus = "{change["status"]}";')
            for key, val in change.get("properties", {}).items():
                if isinstance(val, bool) and val:
                    lines.append(f"\t{key};")
                elif isinstance(val, bool):
                    continue
                else:
                    formatted = cls._format_value(val)
                    lines.append(f"\t{key} = {formatted};")
            lines.append("};")
            lines.append("")

        return "\n".join(lines)
