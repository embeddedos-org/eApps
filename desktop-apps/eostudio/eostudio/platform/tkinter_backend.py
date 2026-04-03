"""Tkinter display backend for Windows, Linux, and macOS."""

from __future__ import annotations

import time
from typing import Any, Callable, Dict, List, Optional, Tuple

from eostudio.platform.display_backend import (
    DisplayBackend, EventType, InputEvent, WindowConfig,
)


class TkinterBackend(DisplayBackend):
    """Display backend using Python's built-in tkinter toolkit."""

    def __init__(self) -> None:
        super().__init__()
        self._tk: Any = None
        self._canvases: Dict[int, Any] = {}
        self._pending_events: List[InputEvent] = []
        self._next_window_id: int = 1
        self._timers: Dict[int, str] = {}
        self._next_timer_id: int = 1

    def init(self) -> None:
        import tkinter as tk
        self._tk = tk.Tk()
        self._tk.withdraw()

    def shutdown(self) -> None:
        if self._tk:
            try:
                self._tk.quit()
                self._tk.destroy()
            except Exception:
                pass
            self._tk = None

    def is_available(self) -> bool:
        try:
            import tkinter
            return True
        except ImportError:
            return False

    def create_window(self, config: WindowConfig) -> int:
        import tkinter as tk
        if self._tk is None:
            self.init()
        wid = self._next_window_id
        self._next_window_id += 1
        if wid == 1:
            win = self._tk
            win.deiconify()
        else:
            win = tk.Toplevel(self._tk)
        win.title(config.title)
        win.geometry(f"{config.width}x{config.height}")
        win.minsize(config.min_width, config.min_height)
        win.resizable(config.resizable, config.resizable)
        if config.fullscreen:
            win.attributes("-fullscreen", True)
        if config.always_on_top:
            win.attributes("-topmost", True)
        canvas = tk.Canvas(win, width=config.width, height=config.height,
                           bg="#FFFFFF", highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        win.protocol("WM_DELETE_WINDOW",
                     lambda: self._pending_events.append(
                         InputEvent(type=EventType.QUIT)))
        canvas.bind("<ButtonPress>", lambda e: self._on_mouse(e, EventType.MOUSE_DOWN))
        canvas.bind("<ButtonRelease>", lambda e: self._on_mouse(e, EventType.MOUSE_UP))
        canvas.bind("<Motion>", lambda e: self._on_mouse(e, EventType.MOUSE_MOVE))
        canvas.bind("<MouseWheel>", lambda e: self._on_scroll(e))
        win.bind("<KeyPress>", lambda e: self._on_key(e, EventType.KEY_DOWN))
        win.bind("<KeyRelease>", lambda e: self._on_key(e, EventType.KEY_UP))
        win.bind("<Configure>", lambda e: self._on_resize(e))
        self._windows[wid] = win
        self._canvases[wid] = canvas
        return wid

    def destroy_window(self, window_id: int) -> None:
        win = self._windows.pop(window_id, None)
        self._canvases.pop(window_id, None)
        if win and win != self._tk:
            win.destroy()

    def set_window_title(self, window_id: int, title: str) -> None:
        win = self._windows.get(window_id)
        if win:
            win.title(title)

    def get_window_size(self, window_id: int) -> Tuple[int, int]:
        win = self._windows.get(window_id)
        if win:
            return win.winfo_width(), win.winfo_height()
        return 0, 0

    def _on_mouse(self, event: Any, etype: EventType) -> None:
        self._pending_events.append(InputEvent(
            type=etype, x=event.x, y=event.y,
            button=event.num, timestamp=time.time()))

    def _on_scroll(self, event: Any) -> None:
        self._pending_events.append(InputEvent(
            type=EventType.MOUSE_SCROLL, x=event.x, y=event.y,
            delta=event.delta, timestamp=time.time()))

    def _on_key(self, event: Any, etype: EventType) -> None:
        self._pending_events.append(InputEvent(
            type=etype, key=event.keysym,
            modifiers=event.state, timestamp=time.time()))

    def _on_resize(self, event: Any) -> None:
        if hasattr(event, "width") and hasattr(event, "height"):
            self._pending_events.append(InputEvent(
                type=EventType.RESIZE, width=event.width,
                height=event.height, timestamp=time.time()))

    def poll_events(self) -> List[InputEvent]:
        if self._tk:
            self._tk.update_idletasks()
            self._tk.update()
        events = list(self._pending_events)
        self._pending_events.clear()
        return events

    def wait_events(self, timeout_ms: int = -1) -> List[InputEvent]:
        if self._tk:
            if timeout_ms > 0:
                self._tk.after(timeout_ms,
                               lambda: self._pending_events.append(
                                   InputEvent(type=EventType.TIMER)))
            self._tk.update()
        events = list(self._pending_events)
        self._pending_events.clear()
        return events

    @staticmethod
    def _color_hex(color: int) -> str:
        return f"#{(color & 0xFFFFFF):06X}"

    def draw_rect(self, window_id: int, x: int, y: int, w: int, h: int,
                  color: int, filled: bool = True) -> None:
        canvas = self._canvases.get(window_id)
        if not canvas:
            return
        c = self._color_hex(color)
        if filled:
            canvas.create_rectangle(x, y, x + w, y + h, fill=c, outline="")
        else:
            canvas.create_rectangle(x, y, x + w, y + h, outline=c, width=1)

    def draw_line(self, window_id: int, x1: int, y1: int,
                  x2: int, y2: int, color: int, width: int = 1) -> None:
        canvas = self._canvases.get(window_id)
        if canvas:
            canvas.create_line(x1, y1, x2, y2,
                               fill=self._color_hex(color), width=width)

    def draw_circle(self, window_id: int, cx: int, cy: int, radius: int,
                    color: int, filled: bool = True) -> None:
        canvas = self._canvases.get(window_id)
        if not canvas:
            return
        c = self._color_hex(color)
        x1, y1 = cx - radius, cy - radius
        x2, y2 = cx + radius, cy + radius
        if filled:
            canvas.create_oval(x1, y1, x2, y2, fill=c, outline="")
        else:
            canvas.create_oval(x1, y1, x2, y2, outline=c, width=1)

    def draw_text(self, window_id: int, x: int, y: int, text: str,
                  color: int = 0x000000, font_size: int = 14,
                  font_family: str = "") -> None:
        canvas = self._canvases.get(window_id)
        if canvas:
            family = font_family or "Helvetica"
            canvas.create_text(x, y, text=text, anchor="nw",
                               fill=self._color_hex(color),
                               font=(family, font_size))

    def draw_image(self, window_id: int, x: int, y: int,
                   image_data: bytes, width: int, height: int) -> None:
        canvas = self._canvases.get(window_id)
        if not canvas:
            return
        try:
            import tkinter as tk
            from PIL import Image, ImageTk
            img = Image.frombytes("RGBA", (width, height), image_data)
            photo = ImageTk.PhotoImage(img)
            canvas.create_image(x, y, image=photo, anchor="nw")
            if not hasattr(canvas, "_photos"):
                canvas._photos = []
            canvas._photos.append(photo)
        except ImportError:
            self.draw_rect(window_id, x, y, width, height, 0xCCCCCC)

    def clear(self, window_id: int, color: int = 0xFFFFFF) -> None:
        canvas = self._canvases.get(window_id)
        if canvas:
            canvas.delete("all")
            canvas.configure(bg=self._color_hex(color))

    def flush(self, window_id: int) -> None:
        if self._tk:
            self._tk.update_idletasks()

    def get_clipboard_text(self) -> str:
        if self._tk:
            try:
                return self._tk.clipboard_get()  # type: ignore[no-any-return]
            except Exception:
                return ""
        return ""

    def set_clipboard_text(self, text: str) -> None:
        if self._tk:
            self._tk.clipboard_clear()
            self._tk.clipboard_append(text)

    def set_cursor(self, cursor_type: str) -> None:
        cursor_map = {
            "arrow": "", "hand": "hand2", "crosshair": "crosshair",
            "text": "xterm", "wait": "watch", "resize_ns": "sb_v_double_arrow",
            "resize_ew": "sb_h_double_arrow", "move": "fleur",
        }
        tk_cursor = cursor_map.get(cursor_type, "")
        for win in self._windows.values():
            win.configure(cursor=tk_cursor)

    def schedule_timer(self, interval_ms: int,
                       callback: Callable[[], None],
                       repeat: bool = False) -> int:
        tid = self._next_timer_id
        self._next_timer_id += 1

        def _fire() -> None:
            callback()
            if repeat and tid in self._timers:
                after_id = self._tk.after(interval_ms, _fire)
                self._timers[tid] = after_id

        if self._tk:
            after_id = self._tk.after(interval_ms, _fire)
            self._timers[tid] = after_id
        return tid

    def cancel_timer(self, timer_id: int) -> None:
        after_id = self._timers.pop(timer_id, None)
        if after_id and self._tk:
            self._tk.after_cancel(after_id)
