"""Web/browser display backend using WebSocket + HTML5 Canvas."""

from __future__ import annotations

import base64
import time
from typing import Any, Callable, Dict, List, Tuple

from eostudio.platform.display_backend import (
    DisplayBackend, EventType, InputEvent, WindowConfig,
)


class WebBackend(DisplayBackend):
    """Display backend that streams draw commands over WebSocket to an
    HTML5 Canvas client, enabling browser-based EoStudio."""

    def __init__(self, host: str = "localhost", port: int = 8765) -> None:
        super().__init__()
        self._host = host
        self._port = port
        self._draw_queue: List[Dict[str, Any]] = []
        self._pending_events: List[InputEvent] = []
        self._window_configs: Dict[int, WindowConfig] = {}
        self._timers: Dict[int, Any] = {}
        self._next_timer_id: int = 1

    def init(self) -> None:
        pass

    def shutdown(self) -> None:
        self._draw_queue.clear()

    def is_available(self) -> bool:
        return True

    def create_window(self, config: WindowConfig) -> int:
        wid = len(self._window_configs) + 1
        self._window_configs[wid] = config
        self._windows[wid] = config
        self._send({"type": "create_window", "id": wid,
                    "title": config.title,
                "width": config.width, "height": config.height})
        return wid

    def destroy_window(self, window_id: int) -> None:
        self._window_configs.pop(window_id, None)
        self._windows.pop(window_id, None)
        self._send({"type": "destroy_window", "id": window_id})

    def set_window_title(self, window_id: int, title: str) -> None:
        self._send({"type": "set_title", "id": window_id, "title": title})

    def get_window_size(self, window_id: int) -> Tuple[int, int]:
        cfg = self._window_configs.get(window_id)
        return (cfg.width, cfg.height) if cfg else (0, 0)

    def poll_events(self) -> List[InputEvent]:
        events = list(self._pending_events)
        self._pending_events.clear()
        return events

    def wait_events(self, timeout_ms: int = -1) -> List[InputEvent]:
        if timeout_ms > 0:
            time.sleep(timeout_ms / 1000.0)
        return self.poll_events()

    def _send(self, cmd: Dict[str, Any]) -> None:
        self._draw_queue.append(cmd)

    @staticmethod
    def _css(color: int) -> str:
        return f"#{(color & 0xFFFFFF):06X}"

    def draw_rect(self, window_id: int, x: int, y: int, w: int, h: int,
                   color: int, filled: bool = True) -> None:
        self._send({"type": "rect", "wid": window_id, "x": x, "y": y,
                    "w": w, "h": h, "color": self._css(color), "filled": filled})

    def draw_line(self, window_id: int, x1: int, y1: int,
                  x2: int, y2: int, color: int, width: int = 1) -> None:
        self._send({"type": "line", "wid": window_id,
                    "x1": x1, "y1": y1, "x2": x2, "y2": y2,
                "color": self._css(color), "width": width})

    def draw_circle(self, window_id: int, cx: int, cy: int, radius: int,
                    color: int, filled: bool = True) -> None:
        self._send({"type": "circle", "wid": window_id,
                    "cx": cx, "cy": cy, "r": radius,
                "color": self._css(color), "filled": filled})

    def draw_text(self, window_id: int, x: int, y: int, text: str,
                  color: int = 0x000000, font_size: int = 14,
                  font_family: str = "") -> None:
        self._send({"type": "text", "wid": window_id, "x": x, "y": y,
                    "text": text, "color": self._css(color),
                    "fontSize": font_size,
                "fontFamily": font_family or "sans-serif"})

    def draw_image(self, window_id: int, x: int, y: int,
                   image_data: bytes, width: int, height: int) -> None:
        self._send({"type": "image", "wid": window_id, "x": x, "y": y,
                    "width": width, "height": height,
                "data": base64.b64encode(image_data).decode("ascii")})

    def clear(self, window_id: int, color: int = 0xFFFFFF) -> None:
        self._send({"type": "clear", "wid": window_id, "color": self._css(color)})

    def flush(self, window_id: int) -> None:
        self._send({"type": "flush", "wid": window_id})

    def get_draw_queue(self) -> List[Dict[str, Any]]:
        q = list(self._draw_queue)
        self._draw_queue.clear()
        return q

    def inject_event(self, event_dict: Dict[str, Any]) -> None:
        etype_map = {
            "mousedown": EventType.MOUSE_DOWN, "mouseup": EventType.MOUSE_UP,
            "mousemove": EventType.MOUSE_MOVE, "wheel": EventType.MOUSE_SCROLL,
            "keydown": EventType.KEY_DOWN, "keyup": EventType.KEY_UP,
            "resize": EventType.RESIZE,
        }
        etype = etype_map.get(event_dict.get("type", ""), EventType.MOUSE_MOVE)
        self._pending_events.append(InputEvent(
            type=etype, x=event_dict.get("x", 0), y=event_dict.get("y", 0),
            button=event_dict.get("button", 0), key=event_dict.get("key", ""),
            delta=event_dict.get("delta", 0), width=event_dict.get("width", 0),
            height=event_dict.get("height", 0), timestamp=time.time()))

    def get_clipboard_text(self) -> str:
        return ""

    def set_clipboard_text(self, text: str) -> None:
        self._send({"type": "clipboard", "text": text})

    def set_cursor(self, cursor_type: str) -> None:
        self._send({"type": "cursor", "cursor": cursor_type})

    def schedule_timer(self, interval_ms: int, callback: Callable[[], None],
                       repeat: bool = False) -> int:
        tid = self._next_timer_id
        self._next_timer_id += 1
        self._timers[tid] = {"interval": interval_ms, "callback": callback,
                             "repeat": repeat}
        return tid

    def cancel_timer(self, timer_id: int) -> None:
        self._timers.pop(timer_id, None)
