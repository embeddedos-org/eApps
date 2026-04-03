"""Display backend abstraction for cross-platform EoStudio rendering."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Tuple


class EventType(Enum):
    QUIT = auto()
    KEY_DOWN = auto()
    KEY_UP = auto()
    MOUSE_DOWN = auto()
    MOUSE_UP = auto()
    MOUSE_MOVE = auto()
    MOUSE_SCROLL = auto()
    RESIZE = auto()
    FOCUS_IN = auto()
    FOCUS_OUT = auto()
    DROP_FILE = auto()
    TIMER = auto()


@dataclass
class InputEvent:
    """Platform-agnostic input event."""
    type: EventType
    x: int = 0
    y: int = 0
    button: int = 0
    key: str = ""
    modifiers: int = 0
    delta: int = 0
    width: int = 0
    height: int = 0
    data: Any = None
    timestamp: float = 0.0


@dataclass
class WindowConfig:
    """Window creation configuration."""
    title: str = "EoStudio"
    width: int = 1280
    height: int = 800
    min_width: int = 800
    min_height: int = 600
    resizable: bool = True
    fullscreen: bool = False
    icon_path: str = ""
    always_on_top: bool = False


class DisplayBackend(ABC):
    """Abstract base class for platform display backends.

    Subclass and implement all abstract methods to add a new
    platform target for the EoStudio GUI.
    """

    def __init__(self) -> None:
        self._running: bool = False
        self._event_handlers: Dict[EventType, List[Callable[[InputEvent], None]]] = {}
        self._windows: Dict[int, Any] = {}

    @abstractmethod
    def init(self) -> None:
        """Initialise the display subsystem."""

    @abstractmethod
    def shutdown(self) -> None:
        """Tear down the display subsystem and release resources."""

    @abstractmethod
    def is_available(self) -> bool:
        """Return True if this backend can run on the current platform."""

    @abstractmethod
    def create_window(self, config: WindowConfig) -> int:
        """Create a new window and return its integer handle."""

    @abstractmethod
    def destroy_window(self, window_id: int) -> None:
        """Destroy the window identified by *window_id*."""

    @abstractmethod
    def set_window_title(self, window_id: int, title: str) -> None:
        """Update the title bar text."""

    @abstractmethod
    def get_window_size(self, window_id: int) -> Tuple[int, int]:
        """Return (width, height) in pixels."""

    @abstractmethod
    def poll_events(self) -> List[InputEvent]:
        """Return pending input events without blocking."""

    @abstractmethod
    def wait_events(self, timeout_ms: int = -1) -> List[InputEvent]:
        """Block until at least one event is available."""

    def register_handler(self, event_type: EventType,
                         handler: Callable[[InputEvent], None]) -> None:
        self._event_handlers.setdefault(event_type, []).append(handler)

    def dispatch_events(self, events: List[InputEvent]) -> None:
        for ev in events:
            for handler in self._event_handlers.get(ev.type, []):
                handler(ev)

    @abstractmethod
    def draw_rect(self, window_id: int, x: int, y: int, w: int, h: int,
                  color: int, filled: bool = True) -> None:
        """Draw a rectangle. *color* is 0xRRGGBB."""

    @abstractmethod
    def draw_line(self, window_id: int, x1: int, y1: int,
                  x2: int, y2: int, color: int, width: int = 1) -> None:
        """Draw a line between two points."""

    @abstractmethod
    def draw_circle(self, window_id: int, cx: int, cy: int, radius: int,
                    color: int, filled: bool = True) -> None:
        """Draw a circle."""

    @abstractmethod
    def draw_text(self, window_id: int, x: int, y: int, text: str,
                  color: int = 0x000000, font_size: int = 14,
                  font_family: str = "") -> None:
        """Render text at the given position."""

    @abstractmethod
    def draw_image(self, window_id: int, x: int, y: int,
                   image_data: bytes, width: int, height: int) -> None:
        """Blit raw RGBA image data at (x, y)."""

    @abstractmethod
    def clear(self, window_id: int, color: int = 0xFFFFFF) -> None:
        """Clear the window to *color*."""

    @abstractmethod
    def flush(self, window_id: int) -> None:
        """Present the back-buffer to screen."""

    @abstractmethod
    def get_clipboard_text(self) -> str:
        """Return current clipboard text."""

    @abstractmethod
    def set_clipboard_text(self, text: str) -> None:
        """Copy text to the system clipboard."""

    @abstractmethod
    def set_cursor(self, cursor_type: str) -> None:
        """Set cursor: arrow, hand, crosshair, text, wait."""

    @abstractmethod
    def schedule_timer(self, interval_ms: int,
                       callback: Callable[[], None],
                       repeat: bool = False) -> int:
        """Schedule a timer callback. Return timer ID."""

    @abstractmethod
    def cancel_timer(self, timer_id: int) -> None:
        """Cancel a previously scheduled timer."""

    def run(self, on_frame: Optional[Callable[[], None]] = None) -> None:
        """Run the main event loop until quit."""
        self._running = True
        while self._running:
            events = self.poll_events()
            self.dispatch_events(events)
            for ev in events:
                if ev.type == EventType.QUIT:
                    self._running = False
            if on_frame:
                on_frame()

    def request_quit(self) -> None:
        self._running = False
