# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""Build panel — peripheral selection and build configuration.

Expands peripheral checkboxes to include all device types,
grouped by category. Auto-checks peripherals from product template.
"""
from typing import Dict, List, Set
from eosim.gui.product_templates import PRODUCT_CATALOG, get_template


PERIPHERAL_CATEGORIES = {
    'Core': ['uart', 'gpio', 'timer', 'spi', 'i2c', 'nvic'],
    'Sensors': [
        'temp', 'barometer', 'imu', 'gps', 'proximity',
        'light', 'adc', 'current', 'ecg', 'spo2', 'mag',
        'airspeed', 'wind_tunnel', 'pitot', 'force_balance',
        'heart_model', 'bp_sensor', 'market_feed', 'order_book',
        'anemometer', 'radar', 'physics_engine', 'terrain', 'entities',
    ],
    'Actuators': [
        'motor', 'servo', 'esc', 'valve', 'pump', 'relay',
        'display', 'haptic', 'steering', 'throttle', 'brake',
    ],
    'Buses': [
        'can', 'lin', 'modbus', 'ethernet', 'arinc429', 'mil1553',
    ],
    'Wireless': [
        'wifi', 'ble', 'lora', 'zigbee', 'rf',
    ],
    'Composite': [
        'bms', 'psu', 'watchdog', 'crypto', 'rtc',
    ],
    'Media & Display': [
        'hdmi', 'audio', 'camera', 'ir', 'usb', 'gpu', 'touch', 'pcie',
    ],
}

ALL_PERIPHERALS: Set[str] = set()
for periphs in PERIPHERAL_CATEGORIES.values():
    ALL_PERIPHERALS.update(periphs)


class BuildConfig:
    """Configuration for a simulation build."""

    def __init__(self):
        self.product_type: str = ''
        self.arch: str = 'arm'
        self.ram_mb: int = 128
        self.selected_peripherals: Set[str] = set()
        self.simulator_class: str = ''

    def load_from_template(self, product_name: str):
        """Load config from a product template, auto-checking peripherals."""
        template = get_template(product_name)
        if not template:
            return False
        self.product_type = template.name
        self.arch = template.arch
        self.ram_mb = template.ram_mb
        self.selected_peripherals = set(template.peripherals)
        self.simulator_class = template.simulator_class
        return True

    def toggle_peripheral(self, name: str) -> bool:
        """Toggle a peripheral on/off. Returns new state."""
        if name in self.selected_peripherals:
            self.selected_peripherals.discard(name)
            return False
        else:
            self.selected_peripherals.add(name)
            return True

    def to_dict(self) -> dict:
        return {
            'product': self.product_type,
            'arch': self.arch,
            'ram_mb': self.ram_mb,
            'peripherals': sorted(self.selected_peripherals),
            'simulator_class': self.simulator_class,
        }


class BuildPanel:
    """Build panel with grouped peripheral selection.

    Organizes peripherals by category (Core, Sensors, Actuators, Buses,
    Wireless, Composite) and auto-checks based on product template.
    """

    def __init__(self):
        self.config = BuildConfig()
        self.categories = dict(PERIPHERAL_CATEGORIES)

    def select_product(self, product_name: str) -> bool:
        """Select a product template and auto-check its peripherals."""
        return self.config.load_from_template(product_name)

    def get_peripheral_groups(self) -> Dict[str, List[dict]]:
        """Return peripheral groups with checked state for UI rendering."""
        groups = {}
        for category, periphs in self.categories.items():
            items = []
            for p in periphs:
                items.append({
                    'name': p,
                    'checked': p in self.config.selected_peripherals,
                    'category': category,
                })
            groups[category] = items
        return groups

    def toggle_peripheral(self, name: str) -> bool:
        """Toggle a peripheral checkbox. Returns new state."""
        return self.config.toggle_peripheral(name)

    def get_build_config(self) -> dict:
        """Get the current build configuration."""
        return self.config.to_dict()

    def list_products(self) -> List[dict]:
        """Return list of all product templates for selection UI."""
        products = []
        for key in sorted(PRODUCT_CATALOG.keys()):
            tpl = PRODUCT_CATALOG[key]
            products.append({
                'name': tpl.name,
                'display_name': tpl.display_name,
                'icon': tpl.icon,
                'domain': tpl.domain,
                'arch': tpl.arch,
                'description': tpl.description,
            })
        return products
