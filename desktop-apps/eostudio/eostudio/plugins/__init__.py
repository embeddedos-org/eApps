"""Plugin system for EoStudio."""
from __future__ import annotations
from eostudio.plugins.plugin_base import Plugin, PluginHook, PluginManifest, PluginManager, PluginState
try:
    from eostudio.plugins.eosim_plugin import EoSimPlugin
except ImportError:
    EoSimPlugin = None  # type: ignore[assignment,misc]
__all__ = ["Plugin", "PluginHook", "PluginManifest", "PluginManager", "PluginState", "EoSimPlugin"]
