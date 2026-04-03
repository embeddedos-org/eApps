"""Responsive device presets and viewport management."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class DevicePreset:
    """Device screen preset for responsive preview."""
    name: str
    width: int
    height: int
    dpi: int = 96
    platform: str = "mobile"
    category: str = "phone"
    pixel_ratio: float = 1.0


DEVICE_PRESETS: Dict[str, DevicePreset] = {
    "iphone-se": DevicePreset("iPhone SE", 375, 667, 326, "ios", "phone", 2.0),
    "iphone-14": DevicePreset("iPhone 14", 390, 844, 460, "ios", "phone", 3.0),
    "iphone-14-pro-max": DevicePreset("iPhone 14 Pro Max", 430, 932, 460, "ios", "phone", 3.0),
    "iphone-15": DevicePreset("iPhone 15", 393, 852, 460, "ios", "phone", 3.0),
    "ipad-mini": DevicePreset("iPad Mini", 744, 1133, 326, "ios", "tablet", 2.0),
    "ipad-air": DevicePreset("iPad Air", 820, 1180, 264, "ios", "tablet", 2.0),
    "ipad-pro-12": DevicePreset("iPad Pro 12.9\"", 1024, 1366, 264, "ios", "tablet", 2.0),
    "pixel-7": DevicePreset("Pixel 7", 412, 915, 416, "android", "phone", 2.625),
    "pixel-7-pro": DevicePreset("Pixel 7 Pro", 412, 892, 512, "android", "phone", 3.5),
    "samsung-s23": DevicePreset("Samsung S23", 360, 780, 425, "android", "phone", 3.0),
    "samsung-s23-ultra": DevicePreset("Samsung S23 Ultra", 384, 824, 500, "android", "phone", 3.75),
    "android-tablet": DevicePreset("Android Tablet", 800, 1280, 213, "android", "tablet", 1.5),
    "laptop-sm": DevicePreset("Laptop 13\"", 1366, 768, 96, "desktop", "laptop", 1.0),
    "laptop-md": DevicePreset("Laptop 15\"", 1536, 864, 96, "desktop", "laptop", 1.0),
    "desktop-fhd": DevicePreset("Desktop FHD", 1920, 1080, 96, "desktop", "monitor", 1.0),
    "desktop-qhd": DevicePreset("Desktop QHD", 2560, 1440, 109, "desktop", "monitor", 1.0),
    "desktop-4k": DevicePreset("Desktop 4K", 3840, 2160, 163, "desktop", "monitor", 2.0),
    "watch-apple": DevicePreset("Apple Watch", 184, 224, 326, "wearable", "watch", 2.0),
    "tv-1080p": DevicePreset("TV 1080p", 1920, 1080, 40, "tv", "tv", 1.0),
    "tv-4k": DevicePreset("TV 4K", 3840, 2160, 80, "tv", "tv", 2.0),
}


@dataclass
class Breakpoint:
    """Responsive breakpoint definition."""
    name: str
    min_width: int
    max_width: int
    label: str


BREAKPOINTS: List[Breakpoint] = [
    Breakpoint("xs", 0, 575, "Extra Small"),
    Breakpoint("sm", 576, 767, "Small"),
    Breakpoint("md", 768, 991, "Medium"),
    Breakpoint("lg", 992, 1199, "Large"),
    Breakpoint("xl", 1200, 1599, "Extra Large"),
    Breakpoint("xxl", 1600, 99999, "2X Large"),
]


class ResponsiveViewport:
    """Constrains the design canvas to a target device preset."""

    def __init__(self, preset: Optional[DevicePreset] = None) -> None:
        self._preset = preset
        self._orientation: str = "portrait"
        self._scale: float = 1.0

    @property
    def preset(self) -> Optional[DevicePreset]:
        return self._preset

    def set_preset(self, name: str) -> None:
        self._preset = DEVICE_PRESETS.get(name)

    @property
    def orientation(self) -> str:
        return self._orientation

    def toggle_orientation(self) -> None:
        self._orientation = "landscape" if self._orientation == "portrait" else "portrait"

    @property
    def width(self) -> int:
        if not self._preset:
            return 1280
        return self._preset.height if self._orientation == "landscape" else self._preset.width

    @property
    def height(self) -> int:
        if not self._preset:
            return 800
        return self._preset.width if self._orientation == "landscape" else self._preset.height

    @property
    def scale(self) -> float:
        return self._scale

    def set_scale(self, scale: float) -> None:
        self._scale = max(0.1, min(5.0, scale))

    def fit_to_container(self, container_w: int, container_h: int) -> float:
        w, h = self.width, self.height
        scale_w = container_w / w if w > 0 else 1.0
        scale_h = container_h / h if h > 0 else 1.0
        self._scale = min(scale_w, scale_h, 1.0)
        return self._scale

    def get_breakpoint(self) -> str:
        w = self.width
        for bp in BREAKPOINTS:
            if bp.min_width <= w <= bp.max_width:
                return bp.name
        return "xl"

    @staticmethod
    def list_presets(category: Optional[str] = None) -> List[DevicePreset]:
        presets = list(DEVICE_PRESETS.values())
        if category:
            presets = [p for p in presets if p.category == category]
        return presets

    @staticmethod
    def list_categories() -> List[str]:
        return sorted(set(p.category for p in DEVICE_PRESETS.values()))
