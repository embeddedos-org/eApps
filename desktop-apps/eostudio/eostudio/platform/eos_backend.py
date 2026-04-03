"""EoS Display HAL backend — adapter wrapping EosFrameBuffer."""

from __future__ import annotations

import os
import time
from typing import Any, Callable, Dict, List, Optional, Tuple

from eostudio.platform.display_backend import (
    DisplayBackend, EventType, InputEvent, WindowConfig,
)


class EosBackend(DisplayBackend):
    """Display backend for EoS using the EoS Display HAL (framebuffer/SDL2)."""

    def __init__(self) -> None:
        super().__init__()
        self._fb: Any = None
        self._width: int = 800
        self._height: int = 480
        self._pending_events: List[InputEvent] = []
        self._timers: Dict[int, Any] = {}
        self._next_timer_id: int = 1

    def init(self) -> None:
        from eostudio.platform.eos_display import EosFrameBuffer
        backend = os.environ.get("EOS_DISPLAY", "auto")
        self._fb = EosFrameBuffer(width=self._width, height=self._height,
                                  display_id=0, backend=backend)
        self._fb.init()

    def shutdown(self) -> None:
        if self._fb:
            self._fb.deinit()
            self._fb = None

    def is_available(self) -> bool:
        return (os.environ.get("EOS_DISPLAY") is not None
                or os.path.exists("/proc/eos")
                or os.environ.get("EOS_ROOT") is not None)

    def create_window(self, config: WindowConfig) -> int:
        self._width = config.width
        self._height = config.height
        if self._fb is None:
            self.init()
        self._windows[1] = self._fb
        return 1

    def destroy_window(self, window_id: int) -> None:
        self._windows.pop(window_id, None)

    def set_window_title(self, window_id: int, title: str) -> None:
        pass

    def get_window_size(self, window_id: int) -> Tuple[int, int]:
        return self._width, self._height

    def poll_events(self) -> List[InputEvent]:
        events = list(self._pending_events)
        self._pending_events.clear()
        return events

    def wait_events(self, timeout_ms: int = -1) -> List[InputEvent]:
        if timeout_ms > 0:
            time.sleep(timeout_ms / 1000.0)
        return self.poll_events()

    def _pack_color(self, color: int) -> int:
        return color & 0xFFFFFF

    def draw_rect(self, window_id: int, x: int, y: int, w: int, h: int,
                  color: int, filled: bool = True) -> None:
        if self._fb and filled:
            self._fb.draw_rect(x, y, w, h, self._pack_color(color))

    def draw_line(self, window_id: int, x1: int, y1: int,
                  x2: int, y2: int, color: int, width: int = 1) -> None:
        if not self._fb:
            return
        c = self._pack_color(color)
        dx, dy = abs(x2 - x1), abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy
        while True:
            self._fb.draw_pixel(x1, y1, c)
            if x1 == x2 and y1 == y2:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy

    def draw_circle(self, window_id: int, cx: int, cy: int, radius: int,
                    color: int, filled: bool = True) -> None:
        if not self._fb:
            return
        c = self._pack_color(color)
        if filled:
            for dy in range(-radius, radius + 1):
                for dx in range(-radius, radius + 1):
                    if dx * dx + dy * dy <= radius * radius:
                        px, py = cx + dx, cy + dy
                        if 0 <= px < self._width and 0 <= py < self._height:
                            self._fb.draw_pixel(px, py, c)

    def draw_text(self, window_id: int, x: int, y: int, text: str,
                  color: int = 0x000000, font_size: int = 14,
                  font_family: str = "") -> None:
        if self._fb:
            c = self._pack_color(color)
            self._fb.draw_rect(x, y, len(text) * 8, font_size + 4, c)

    def draw_image(self, window_id: int, x: int, y: int,
                   image_data: bytes, width: int, height: int) -> None:
        if self._fb:
            self._fb.draw_bitmap(x, y, width, height, image_data)

    def clear(self, window_id: int, color: int = 0xFFFFFF) -> None:
        if self._fb:
            self._fb.clear(self._pack_color(color))

    def flush(self, window_id: int) -> None:
        if self._fb:
            self._fb.flush()

    def get_clipboard_text(self) -> str:
        return ""

    def set_clipboard_text(self, text: str) -> None:
        pass

    def set_cursor(self, cursor_type: str) -> None:
        pass

    def schedule_timer(self, interval_ms: int, callback: Callable[[], None],
                       repeat: bool = False) -> int:
        tid = self._next_timer_id
        self._next_timer_id += 1
        self._timers[tid] = {"interval": interval_ms, "callback": callback,
                             "repeat": repeat}
        return tid

    def cancel_timer(self, timer_id: int) -> None:
        self._timers.pop(timer_id, None)
