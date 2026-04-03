"""2D drawing canvas with zoom, pan, grid snap, and shape helpers."""

from __future__ import annotations

import tkinter as tk
from typing import Any, Callable, Dict, List, Optional, Tuple


class Canvas2D(tk.Canvas):
    """Pannable / zoomable 2D canvas with ruler edges and optional snap-to-grid."""

    def __init__(
        self,
        master: tk.Widget,
        bg: str = "#1e1e2e",
        width: int = 800,
        height: int = 600,
        grid_size: int = 20,
        snap: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(master, bg=bg, width=width, height=height, highlightthickness=0, **kwargs)

        self._zoom: float = 1.0
        self._pan_x: float = 0.0
        self._pan_y: float = 0.0
        self._grid_size: int = grid_size
        self._snap: bool = snap
        self._last_mouse: Optional[Tuple[int, int]] = None
        self._items: Dict[str, int] = {}

        self.bind("<ButtonPress-2>", self._on_pan_start)
        self.bind("<B2-Motion>", self._on_pan_move)
        self.bind("<MouseWheel>", self._on_scroll)
        self.bind("<Configure>", lambda e: self._redraw_grid())

        self.after(50, self._redraw_grid)

    # ------------------------------------------------------------------
    # Coordinate helpers
    # ------------------------------------------------------------------

    @property
    def zoom(self) -> float:
        return self._zoom

    def world_to_screen(self, wx: float, wy: float) -> Tuple[float, float]:
        sx = (wx + self._pan_x) * self._zoom
        sy = (wy + self._pan_y) * self._zoom
        return sx, sy

    def screen_to_world(self, sx: float, sy: float) -> Tuple[float, float]:
        wx = sx / self._zoom - self._pan_x
        wy = sy / self._zoom - self._pan_y
        return wx, wy

    def snap_point(self, wx: float, wy: float) -> Tuple[float, float]:
        if not self._snap:
            return wx, wy
        g = self._grid_size
        return round(wx / g) * g, round(wy / g) * g

    def set_snap(self, enabled: bool) -> None:
        self._snap = enabled

    def set_grid_size(self, size: int) -> None:
        self._grid_size = max(5, size)
        self._redraw_grid()

    # ------------------------------------------------------------------
    # Drawing helpers
    # ------------------------------------------------------------------

    def draw_line(
        self,
        x0: float, y0: float,
        x1: float, y1: float,
        color: str = "#cdd6f4",
        width: float = 1,
        tag: str = "user",
    ) -> int:
        sx0, sy0 = self.world_to_screen(x0, y0)
        sx1, sy1 = self.world_to_screen(x1, y1)
        return self.create_line(sx0, sy0, sx1, sy1, fill=color, width=width, tags=(tag,))

    def draw_rect(
        self,
        x0: float, y0: float,
        x1: float, y1: float,
        color: str = "#cdd6f4",
        fill: str = "",
        width: float = 1,
        tag: str = "user",
    ) -> int:
        sx0, sy0 = self.world_to_screen(x0, y0)
        sx1, sy1 = self.world_to_screen(x1, y1)
        return self.create_rectangle(sx0, sy0, sx1, sy1, outline=color, fill=fill, width=width, tags=(tag,))

    def draw_circle(
        self,
        cx: float, cy: float,
        radius: float,
        color: str = "#cdd6f4",
        fill: str = "",
        width: float = 1,
        tag: str = "user",
    ) -> int:
        r = radius * self._zoom
        sx, sy = self.world_to_screen(cx, cy)
        return self.create_oval(sx - r, sy - r, sx + r, sy + r, outline=color, fill=fill, width=width, tags=(tag,))

    def draw_polygon(
        self,
        points: List[Tuple[float, float]],
        color: str = "#cdd6f4",
        fill: str = "",
        width: float = 1,
        tag: str = "user",
    ) -> int:
        screen_pts: List[float] = []
        for wx, wy in points:
            sx, sy = self.world_to_screen(wx, wy)
            screen_pts.extend([sx, sy])
        return self.create_polygon(*screen_pts, outline=color, fill=fill, width=width, tags=(tag,))

    def draw_text(
        self,
        x: float, y: float,
        text: str,
        color: str = "#cdd6f4",
        font: Tuple[str, int] = ("Consolas", 10),
        tag: str = "user",
    ) -> int:
        sx, sy = self.world_to_screen(x, y)
        return self.create_text(sx, sy, text=text, fill=color, font=font, tags=(tag,))

    def clear_user_items(self) -> None:
        self.delete("user")

    # ------------------------------------------------------------------
    # Grid & rulers
    # ------------------------------------------------------------------

    def _redraw_grid(self) -> None:
        self.delete("grid")
        self.delete("ruler")
        w = self.winfo_width() or 800
        h = self.winfo_height() or 600
        step = max(5, int(self._grid_size * self._zoom))

        for x in range(0, w, step):
            self.create_line(x, 0, x, h, fill="#313244", tags=("grid",))
        for y in range(0, h, step):
            self.create_line(0, y, w, y, fill="#313244", tags=("grid",))

        ruler_h = 20
        self.create_rectangle(0, 0, w, ruler_h, fill="#181825", outline="", tags=("ruler",))
        self.create_rectangle(0, 0, ruler_h, h, fill="#181825", outline="", tags=("ruler",))

        for x in range(0, w, step * 5):
            world_x = x / self._zoom - self._pan_x
            self.create_line(x, 0, x, ruler_h, fill="#585b70", tags=("ruler",))
            self.create_text(x + 2, 10, text=f"{world_x:.0f}", fill="#585b70",
                             font=("Consolas", 7), anchor=tk.W, tags=("ruler",))

        for y in range(0, h, step * 5):
            world_y = y / self._zoom - self._pan_y
            self.create_line(0, y, ruler_h, y, fill="#585b70", tags=("ruler",))
            self.create_text(10, y + 2, text=f"{world_y:.0f}", fill="#585b70",
                             font=("Consolas", 7), anchor=tk.N, tags=("ruler",))

        self.tag_lower("grid")

    # ------------------------------------------------------------------
    # Mouse interaction
    # ------------------------------------------------------------------

    def _on_pan_start(self, event: tk.Event) -> None:
        self._last_mouse = (event.x, event.y)

    def _on_pan_move(self, event: tk.Event) -> None:
        if self._last_mouse is None:
            return
        dx = (event.x - self._last_mouse[0]) / self._zoom
        dy = (event.y - self._last_mouse[1]) / self._zoom
        self._pan_x += dx
        self._pan_y += dy
        self._last_mouse = (event.x, event.y)
        self._redraw_grid()

    def _on_scroll(self, event: tk.Event) -> None:
        factor = 1.1 if event.delta > 0 else 0.9
        self._zoom *= factor
        self._zoom = max(0.1, min(20.0, self._zoom))
        self._redraw_grid()
