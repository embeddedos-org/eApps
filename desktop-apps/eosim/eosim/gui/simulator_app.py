# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""EoSim Simulator App — main application controller.

Uses SimulatorFactory to instantiate the correct product simulator
based on the selected product template. Manages VM lifecycle,
simulation ticking, and panel updates.
"""
from eosim.engine.native import VirtualMachine
from eosim.engine.native.simulators import SimulatorFactory, BaseSimulator
from eosim.gui.product_templates import PRODUCT_CATALOG, get_template


class SimulatorApp:
    """Main simulation application controller.

    Manages VM creation, product simulator binding, and simulation lifecycle.
    """

    def __init__(self):
        self.vm = None
        self.simulator: BaseSimulator = None
        self.product_type = ''
        self.running = False
        self.tick_count = 0
        self.build_config = {}

    def build_and_run(self, product_type: str, peripherals: list = None,
                      arch: str = '', ram_mb: int = 0):
        """Build a VM from a product template and start simulation.

        Uses SimulatorFactory.create() to instantiate the right simulator,
        which adds domain-specific peripherals to the VM via setup().
        """
        template = get_template(product_type)
        if template:
            arch = arch or template.arch
            ram_mb = ram_mb or template.ram_mb
        else:
            arch = arch or 'arm'
            ram_mb = ram_mb or 128

        self.product_type = product_type
        self.build_config = {
            'product': product_type,
            'arch': arch,
            'ram_mb': ram_mb,
            'peripherals': peripherals or (template.peripherals if template else []),
        }

        self.vm = VirtualMachine(
            name=f'eosim-{product_type}',
            arch=arch,
            ram_mb=ram_mb,
        )

        self.simulator = SimulatorFactory.create(product_type, self.vm)
        self.running = True
        self.tick_count = 0
        return self.vm

    def tick(self):
        """Advance simulation one step."""
        if not self.running or not self.simulator:
            return
        self.simulator.tick()
        self.tick_count += 1

    def run_cycles(self, count: int = 100):
        """Run multiple simulation ticks."""
        for _ in range(count):
            self.tick()

    def stop(self):
        """Stop the simulation."""
        self.running = False
        if self.vm:
            self.vm.running = False

    def reset(self):
        """Reset the simulation state."""
        if self.simulator:
            self.simulator.reset()
        self.tick_count = 0

    def get_state(self) -> dict:
        """Get current simulator state for UI display."""
        if not self.simulator:
            return {}
        return self.simulator.get_state()

    def get_status_text(self) -> str:
        """Get status line for display."""
        if not self.simulator:
            return 'No simulation active'
        return self.simulator.get_status_text()

    def get_peripheral_names(self) -> list:
        """Return list of peripheral names attached to the current VM."""
        if not self.vm:
            return []
        return list(self.vm.peripherals.keys())

    def get_peripheral(self, name: str):
        """Get a specific peripheral from the VM."""
        if not self.vm:
            return None
        return self.vm.peripherals.get(name)

    def _update_all_panels(self) -> dict:
        """Collect data from all peripherals for panel updates.

        Returns a dict keyed by panel type with sub-dicts of values.
        """
        if not self.vm or not self.simulator:
            return {}

        panels = {
            'simulator': self.simulator.get_state(),
            'cpu': self.vm.cpu.state.dump() if self.vm.cpu else '',
            'uart': self.vm.get_uart_output(),
            'peripherals': {},
        }

        for name, dev in self.vm.peripherals.items():
            info = {'type': type(dev).__name__, 'enabled': getattr(dev, 'enabled', False)}
            if hasattr(dev, 'get_state'):
                info['state'] = dev.get_state()
            panels['peripherals'][name] = info

        return panels
