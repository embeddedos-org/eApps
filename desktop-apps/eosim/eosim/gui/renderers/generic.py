# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""Generic fallback 3D renderer for unknown domains."""

from eosim.gui.renderers import BaseRenderer, register_renderer


class GenericRenderer(BaseRenderer):
    DOMAIN = "generic"
    DISPLAY_NAME = "Generic"

    def setup(self, ax):
        ax.set_xlim(-1, 1)
        ax.set_ylim(-1, 1)
        ax.set_zlim(-1, 1)
        ax.set_xlabel("X", fontsize=7)
        ax.set_ylabel("Y", fontsize=7)
        ax.set_zlabel("Z", fontsize=7)
        ax.set_title("Generic View", fontsize=9)

    def update(self, ax, state: dict):
        tick = state.get("tick", 0)
        ax.scatter([0], [0], [0], color="#888888", s=40, depthshade=False)
        ax.set_title(f"Generic  tick={tick}", fontsize=8)


register_renderer("generic", GenericRenderer)
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""Generic 3D renderer — fallback bar chart of all numeric state values."""
import math
from eosim.gui.renderers import BaseRenderer, register_renderer


class GenericRenderer(BaseRenderer):
    """3D bar chart showing all numeric state values."""

    DOMAIN = 'generic'
    DISPLAY_NAME = 'Generic'

    def setup(self, ax):
        ax.set_title('Simulator State', fontsize=9)
        ax.set_xlabel('Key', fontsize=7)
        ax.set_ylabel('')
        ax.set_zlabel('Value', fontsize=7)

    def update(self, ax, state: dict):
        ax.cla()
        self.setup(ax)
        numeric = {}
        for k, v in state.items():
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                if math.isfinite(v):
                    numeric[k] = v
        if not numeric:
            return
        keys = list(numeric.keys())[:16]
        vals = [numeric[k] for k in keys]
        xs = list(range(len(keys)))
        colors = ['#4ec9b0' if v >= 0 else '#ff6b6b' for v in vals]
        ax.bar(xs, vals, zs=0, zdir='y', alpha=0.8, color=colors, width=0.6)
        ax.set_xticks(xs)
        ax.set_xticklabels(keys, rotation=45, ha='right', fontsize=6)
        ax.tick_params(axis='z', labelsize=7)


register_renderer('generic', GenericRenderer)
