"""EoSim plugin — connects EoSim as a first-class simulation plugin in EoStudio.

This plugin discovers the EoSim installation, initialises the
:class:`EoSimBridge`, registers simulation hooks, and provides menu / toolbar
/ panel contributions so that designers can simulate hardware directly from
the EoStudio GUI.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from eostudio.plugins.plugin_base import (
    Plugin,
    PluginHook,
    PluginManifest,
    PluginState,
)

try:
    from eostudio.core.simulation.eosim_bridge import EoSimBridge
except ImportError:
    EoSimBridge = None  # type: ignore[assignment,misc]

log = logging.getLogger(__name__)


# ------------------------------------------------------------------
# Simulation result container
# ------------------------------------------------------------------

@dataclass
class SimulationResult:
    """Encapsulates the outcome of an EoSim simulation run."""

    success: bool = False
    platform: str = ""
    duration_ms: float = 0.0
    log: str = ""
    metrics: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


# ------------------------------------------------------------------
# EoSim plugin
# ------------------------------------------------------------------

class EoSimPlugin(Plugin):
    """EoSim hardware simulator plugin for EoStudio."""

    manifest = PluginManifest(
        id="eosim",
        name="EoSim Hardware Simulator",
        version="0.1.0",
        description="Integrates EoSim hardware simulation into EoStudio.",
        author="EoS Team",
        plugin_type="simulator",
        entry_point="EoStudio.plugins.eosim_plugin",
        dependencies=["eosim"],
        min_EoStudio_version="0.1.0",
        config_schema={
            "eosim_path": {"type": "string", "default": ""},
            "default_platform": {"type": "string", "default": "stm32f4"},
            "auto_simulate": {"type": "boolean", "default": False},
            "simulation_timeout": {"type": "integer", "default": 30},
        },
    )

    def __init__(self, manifest: Optional[PluginManifest] = None) -> None:
        super().__init__(manifest or self.__class__.manifest)
        self._bridge: Any = None
        self._current_platform: str = "stm32f4"
        self._last_result: Optional[SimulationResult] = None
        self._available_platforms: List[str] = []
        self._available_domains: List[str] = []
        self._eosim_version: str = ""

    # -- lifecycle ------------------------------------------------

    def activate(self, context: Dict[str, Any]) -> bool:
        """Discover EoSim and initialise the bridge."""
        try:
            if EoSimBridge is not None:
                self._bridge = EoSimBridge()
                if hasattr(self._bridge, "discover"):
                    self._bridge.discover()
                if hasattr(self._bridge, "version"):
                    self._eosim_version = str(self._bridge.version)
                if hasattr(self._bridge, "list_platforms"):
                    self._available_platforms = list(self._bridge.list_platforms())
                if hasattr(self._bridge, "list_domains"):
                    self._available_domains = list(self._bridge.list_domains())
            else:
                self._discover_eosim_cli()

            # apply user config
            self._current_platform = self.config.get(
                "default_platform",
                context.get("default_platform", "stm32f4"),
            )

            # register hooks
            self._hooks = {
                PluginHook.ON_DESIGN_CHANGE: self._on_design_change,
                PluginHook.ON_BUILD: self._on_build,
                PluginHook.ON_SIMULATE: self._on_simulate,
                PluginHook.ON_EXPORT: self._on_export,
                PluginHook.POST_CODEGEN: self._on_post_codegen,
            }

            self.state = PluginState.ACTIVE
            log.info("EoSim plugin activated (platform=%s)", self._current_platform)
            return True
        except Exception as exc:
            self.state = PluginState.ERROR
            log.error("EoSim plugin activation failed: %s", exc)
            return False

    def deactivate(self) -> None:
        if self._bridge is not None and hasattr(self._bridge, "close"):
            try:
                self._bridge.close()
            except Exception:
                pass
        self._bridge = None
        self.state = PluginState.DISABLED
        log.info("EoSim plugin deactivated")

    # -- private helpers ------------------------------------------

    def _discover_eosim_cli(self) -> None:
        """Fall-back discovery via CLI / importlib."""
        import importlib
        try:
            eosim = importlib.import_module("eosim")
            self._eosim_version = getattr(eosim, "__version__", "unknown")
        except ImportError:
            self._eosim_version = ""
            log.warning("EoSim package not found; simulation disabled")

        if not self._available_platforms:
            self._available_platforms = [
                "stm32f4", "stm32h7", "esp32", "nrf52", "nrf5340",
                "nrf9160", "rp2040", "imx8m", "raspi4", "k64f",
                "psoc6", "pic32mz", "samc21", "s32k344", "renesas-ra6m5",
                "renesas-rh850", "ti-msp432", "ti-tms570",
                "jetson-orin", "x86_64", "arm64", "riscv64",
            ]
        if not self._available_domains:
            self._available_domains = [
                "consumer", "vehicle", "drone", "robot",
                "medical", "industrial", "satellite", "aircraft",
                "iot", "wearable", "energy", "speaker", "camera", "media",
            ]

    # -- hook handlers --------------------------------------------

    def _on_design_change(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the design against the target platform constraints."""
        design = data.get("design", {})
        platform = data.get("platform", self._current_platform)
        warnings: List[str] = []
        errors: List[str] = []

        _ = design.get("peripherals", [])
        memory = design.get("memory", [])

        # basic constraint validation
        if self._bridge and hasattr(self._bridge, "validate_design"):
            result = self._bridge.validate_design(design, platform)
            return {"valid": result.get("valid", True), "messages": result.get("messages", [])}

        total_ram = sum(m.get("size", 0) for m in memory if "ram" in m.get("name", "").lower())
        total_flash = sum(m.get("size", 0) for m in memory if "flash" in m.get("name", "").lower())

        platform_limits = {
            "stm32f4": {"max_ram": 192 * 1024, "max_flash": 1024 * 1024},
            "esp32": {"max_ram": 520 * 1024, "max_flash": 4 * 1024 * 1024},
            "nrf52": {"max_ram": 256 * 1024, "max_flash": 1024 * 1024},
            "rp2040": {"max_ram": 264 * 1024, "max_flash": 16 * 1024 * 1024},
        }
        limits = platform_limits.get(platform, {})
        if limits:
            if total_ram > limits.get("max_ram", float("inf")):
                errors.append(f"RAM usage ({total_ram} bytes) exceeds {platform} limit ({limits['max_ram']} bytes)")
            if total_flash > limits.get("max_flash", float("inf")):
                errors.append(f"Flash usage ({total_flash} bytes) exceeds {platform} limit ({limits['max_flash']} bytes)")

        return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}

    def _on_build(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger a firmware build via EoSim / ebuild."""
        board_config = data.get("board_config", {})
        source_dir = data.get("source_dir", "")
        platform = data.get("platform", self._current_platform)

        if self._bridge and hasattr(self._bridge, "build"):
            result = self._bridge.build(board_config, source_dir, platform)
            return {"success": result.get("success", False), "output": result.get("output", "")}

        return {
            "success": False,
            "output": "EoSim bridge not available; manual build required.",
            "command": f"ebuild --platform {platform} --config board.yaml {source_dir}",
        }

    def _on_simulate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Launch EoSim simulation for the current design."""
        design = data.get("design", {})
        platform = data.get("platform", self._current_platform)
        result = self.simulate_current_design(design, platform)
        self._last_result = result
        return {
            "success": result.success,
            "platform": result.platform,
            "duration_ms": result.duration_ms,
            "log": result.log,
            "metrics": result.metrics,
            "errors": result.errors,
        }

    def _on_export(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Export board config YAML and generate firmware."""
        design = data.get("design", {})
        files = self.export_for_eosim(design)
        return {"files": files}

    def _on_post_codegen(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate generated code against the target platform."""
        generated_files = data.get("files", {})
        platform = data.get("platform", self._current_platform)
        warnings: List[str] = []

        if self._bridge and hasattr(self._bridge, "validate_code"):
            result = self._bridge.validate_code(generated_files, platform)
            return result  # type: ignore[no-any-return]

        for fname, content in generated_files.items():
            if fname.endswith(".c") or fname.endswith(".h"):
                if "#include" not in content:
                    warnings.append(f"{fname}: no includes found")
                lines = content.split("\n")
                if len(lines) > 5000:
                    warnings.append(f"{fname}: very large file ({len(lines)} lines)")

        return {"valid": True, "warnings": warnings}

    # -- UI contributions -----------------------------------------

    def get_menu_items(self) -> List[Dict[str, Any]]:
        return [
            {"label": "Simulate with EoSim", "callback_name": "simulate_current_design"},
            {"label": "Launch EoSim GUI", "callback_name": "launch_eosim_gui"},
            {"label": "Select Platform", "callback_name": "select_platform"},
            {"label": "View 3D Product", "callback_name": "view_3d_product"},
            {"label": "Run Domain Simulation", "callback_name": "launch_domain_simulator"},
        ]

    def get_toolbar_items(self) -> List[Dict[str, Any]]:
        return [
            {"label": "\u25b6 Simulate", "icon": "play", "callback_name": "simulate_current_design"},
            {"label": "\u2699 Platform", "icon": "settings", "callback_name": "select_platform"},
        ]

    def get_panel(self) -> Optional[Dict[str, Any]]:
        available = self._eosim_version != ""
        return {
            "title": "EoSim Status",
            "content": {
                "available": available,
                "version": self._eosim_version or "not installed",
                "current_platform": self._current_platform,
                "last_result": (
                    {
                        "success": self._last_result.success,
                        "platform": self._last_result.platform,
                        "duration_ms": self._last_result.duration_ms,
                    }
                    if self._last_result
                    else None
                ),
                "available_platforms": self._available_platforms,
                "available_domains": self._available_domains,
            },
        }

    # -- public API -----------------------------------------------

    def simulate_current_design(
        self, design: Dict[str, Any], platform: Optional[str] = None,
    ) -> SimulationResult:
        """Run a full EoSim simulation for *design* on *platform*."""
        platform = platform or self._current_platform

        if self._bridge and hasattr(self._bridge, "simulate"):
            try:
                raw = self._bridge.simulate(design, platform)
                result = SimulationResult(
                    success=raw.get("success", False),
                    platform=platform,
                    duration_ms=raw.get("duration_ms", 0.0),
                    log=raw.get("log", ""),
                    metrics=raw.get("metrics", {}),
                    errors=raw.get("errors", []),
                    warnings=raw.get("warnings", []),
                )
            except Exception as exc:
                result = SimulationResult(
                    success=False,
                    platform=platform,
                    errors=[str(exc)],
                )
        else:
            result = SimulationResult(
                success=False,
                platform=platform,
                errors=["EoSim bridge not available"],
            )

        self._last_result = result
        return result

    def select_platform(self) -> str:
        """Return the list of available platforms for user selection."""
        return self._current_platform

    def get_available_platforms(self) -> List[str]:
        return list(self._available_platforms)

    def set_platform(self, platform: str) -> None:
        if platform in self._available_platforms:
            self._current_platform = platform
            log.info("EoSim platform set to %s", platform)
        else:
            log.warning("Unknown platform %s", platform)

    def build_and_simulate(
        self, board_config: Dict[str, Any], firmware_source: str,
    ) -> SimulationResult:
        """Build firmware from *firmware_source* then run simulation."""
        build_result = self._on_build({
            "board_config": board_config,
            "source_dir": firmware_source,
            "platform": self._current_platform,
        })
        if not build_result.get("success"):
            return SimulationResult(
                success=False,
                platform=self._current_platform,
                errors=[build_result.get("output", "Build failed")],
            )
        return self.simulate_current_design(board_config, self._current_platform)

    def export_for_eosim(self, design: Dict[str, Any]) -> Dict[str, str]:
        """Generate YAML board config and firmware source files for EoSim."""
        import yaml  # type: ignore[import-untyped]

        files: Dict[str, str] = {}

        board_yaml = {
            "name": design.get("name", "board"),
            "platform": self._current_platform,
            "arch": design.get("arch", "arm-cortex-m"),
            "clock_mhz": design.get("clock_mhz", 168),
            "memory": design.get("memory", []),
            "peripherals": design.get("peripherals", []),
        }
        files["board.yaml"] = yaml.dump(board_yaml, default_flow_style=False, sort_keys=False)

        try:
            from eostudio.codegen.hardware import FirmwareGenerator
            gen = FirmwareGenerator(board_yaml, target_os="eos")
            fw_files = gen.generate(app_name=design.get("name", "app"))
            files.update(fw_files)
        except ImportError:
            log.warning("FirmwareGenerator not available; skipping code generation")

        return files

    def get_available_domains(self) -> List[str]:
        """Return the list of simulation domains from the bridge."""
        return list(self._available_domains)

    def launch_domain_simulator(self, domain: str, platform: Optional[str] = None) -> SimulationResult:
        """Launch an EoSim domain-specific simulator."""
        platform = platform or self._current_platform

        if self._bridge and hasattr(self._bridge, "launch_domain"):
            try:
                raw = self._bridge.launch_domain(domain, platform)
                return SimulationResult(
                    success=raw.get("success", False),
                    platform=platform,
                    duration_ms=raw.get("duration_ms", 0.0),
                    log=raw.get("log", ""),
                    metrics=raw.get("metrics", {}),
                )
            except Exception as exc:
                return SimulationResult(success=False, platform=platform, errors=[str(exc)])

        return SimulationResult(
            success=False,
            platform=platform,
            errors=[f"EoSim bridge not available for domain '{domain}'"],
        )

    def launch_eosim_gui(self) -> None:
        """Launch the EoSim standalone GUI application."""
        import subprocess as sp
        try:
            sp.Popen(
                [sys.executable, "-m", "eosim", "gui"],
                stdout=sp.DEVNULL,
                stderr=sp.DEVNULL,
            )
        except Exception as exc:
            log.error("Failed to launch EoSim GUI: %s", exc)

    def view_3d_product(self, platform: Optional[str] = None) -> None:
        """Launch the EoSim 3-D product viewer."""
        import subprocess as sp
        platform = platform or self._current_platform
        try:
            sp.Popen(
                [sys.executable, "-m", "eosim", "view3d", "--platform", platform],
                stdout=sp.DEVNULL,
                stderr=sp.DEVNULL,
            )
        except Exception as exc:
            log.error("Failed to launch 3D viewer: %s", exc)


# make sys available at module level for launch helpers
import sys  # noqa: E402
