# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""3D viewer panel — matplotlib embedded in tkinter for real-time 3D visualization."""
import tkinter as tk
from tkinter import ttk

try:
    import matplotlib
    matplotlib.use('TkAgg')
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


class Viewer3DPanel(ttk.LabelFrame):
    """Real-time 3D visualization panel using matplotlib."""

    def __init__(self, parent):
        super().__init__(parent, text="3D View", padding=4)
        self._domain = ''
        self._renderer = None
        self._ax = None
        self._canvas = None
        self._fig = None
        self._build()

    def _build(self):
        if not HAS_MATPLOTLIB:
            lbl = ttk.Label(
                self,
                text="Install matplotlib for 3D view:\npip install matplotlib",
                font=("Consolas", 9), foreground="gray",
                justify=tk.CENTER,
            )
            lbl.pack(expand=True)
            return

        self._fig = Figure(figsize=(4, 3), dpi=80, facecolor='#2d2d2d')
        self._ax = self._fig.add_subplot(111, projection='3d',
                                          facecolor='#1e1e1e')
        self._ax.set_title('No simulation', fontsize=9, color='white')
        self._style_axes(self._ax)

        self._canvas = FigureCanvasTkAgg(self._fig, master=self)
        self._canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self._canvas.draw()

    def _style_axes(self, ax):
        ax.tick_params(colors='#888888', labelsize=6)
        ax.xaxis.label.set_color('#aaaaaa')
        ax.yaxis.label.set_color('#aaaaaa')
        ax.zaxis.label.set_color('#aaaaaa')
        ax.title.set_color('#d4d4d4')
        try:
            ax.xaxis.pane.fill = False
            ax.yaxis.pane.fill = False
            ax.zaxis.pane.fill = False
        except Exception:
            pass

    def set_domain(self, domain: str):
        """Switch to a domain-specific renderer."""
        if not HAS_MATPLOTLIB:
            return
        self._domain = domain
        from eosim.gui.renderers import get_renderer
        self._renderer = get_renderer(domain)
        if self._ax:
            self._ax.cla()
            self._renderer.setup(self._ax)
            self._style_axes(self._ax)
            self._canvas.draw()

    def update_3d(self, state: dict, domain: str = ''):
        """Update 3D scene from simulator state."""
        if not HAS_MATPLOTLIB or not self._ax or not self._renderer:
            return
        if domain and domain != self._domain:
            self.set_domain(domain)
        self._ax.cla()
        self._renderer.setup(self._ax)
        self._renderer.update(self._ax, state)
        self._style_axes(self._ax)
        try:
            self._canvas.draw_idle()
        except Exception:
            pass

    def reset(self):
        """Reset the 3D view."""
        if not HAS_MATPLOTLIB or not self._ax:
            return
        self._ax.cla()
        self._ax.set_title('No simulation', fontsize=9, color='white')
        self._style_axes(self._ax)
        self._renderer = None
        self._domain = ''
        self._canvas.draw()
