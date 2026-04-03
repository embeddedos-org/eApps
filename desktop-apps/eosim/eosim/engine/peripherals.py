# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""Peripheral simulation models for Renode."""

PERIPHERAL_MODELS = {
    "uart": {
        "renode_type": "UART",
        "description": "Universal Asynchronous Receiver-Transmitter",
        "analyzers": ["LoggingUartAnalyzer", "SocketUartAnalyzer"],
    },
    "spi": {
        "renode_type": "SPI",
        "description": "Serial Peripheral Interface",
        "analyzers": ["LoggingSpiAnalyzer"],
    },
    "i2c": {
        "renode_type": "I2C",
        "description": "Inter-Integrated Circuit",
        "analyzers": ["LoggingI2CAnalyzer"],
    },
    "gpio": {
        "renode_type": "GPIO",
        "description": "General Purpose Input/Output",
        "analyzers": ["LoggingGpioAnalyzer"],
    },
    "timer": {
        "renode_type": "Timer",
        "description": "Hardware timer/counter",
        "analyzers": [],
    },
    "ethernet": {
        "renode_type": "EthernetMAC",
        "description": "Ethernet MAC controller",
        "analyzers": ["PcapAnalyzer"],
    },
    "flash": {
        "renode_type": "SPI_NORFlash",
        "description": "NOR Flash memory",
        "analyzers": [],
    },
    "sdcard": {
        "renode_type": "SDCard",
        "description": "SD/MMC card controller",
        "analyzers": [],
    },
}

def generate_repl_peripherals(peripherals: list) -> str:
    lines = []
    for pname in peripherals:
        model = PERIPHERAL_MODELS.get(pname)
        if model:
            lines.append("// %s — %s" % (pname, model["description"]))
            lines.append("%s: %s @ sysbus" % (pname, model["renode_type"]))
            lines.append("")
    return "\n".join(lines)

def list_peripherals() -> list:
    return list(PERIPHERAL_MODELS.keys())