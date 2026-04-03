# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""Consumer Electronics 3D renderer — bar chart of key media/speaker/camera state values."""
import math
from eosim.gui.renderers import BaseRenderer, register_renderer


class ConsumerRenderer(BaseRenderer):
    """3D bar chart showing consumer electronics state values."""

    DOMAIN = 'consumer'
    DISPLAY_NAME = 'Consumer Electronics'

    _KEYS = ['channel', 'buffer_pct', 'volume_pct', 'stream_bitrate_kbps',
             'storage_used_mb', 'stream_fps', 'cast_peers', 'speaker_group_size',
             'alerts_count', 'command_count']

    def setup(self, ax):
        ax.set_title('Consumer Electronics', fontsize=9)
        ax.set_xlabel('Metric', fontsize=7)
        ax.set_ylabel('')
        ax.set_zlabel('Value', fontsize=7)

    def update(self, ax, state: dict):
        ax.cla()
        self.setup(ax)
        numeric = {}
        for k in self._KEYS:
            v = state.get(k)
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                if math.isfinite(v):
                    numeric[k] = v
        if not numeric:
            return
        keys = list(numeric.keys())[:12]
        vals = [numeric[k] for k in keys]
        xs = list(range(len(keys)))
        colors = ['#4ec9b0' if v >= 0 else '#ff6b6b' for v in vals]
        ax.bar(xs, vals, zs=0, zdir='y', alpha=0.8, color=colors, width=0.6)
        ax.set_xticks(xs)
        ax.set_xticklabels(keys, rotation=45, ha='right', fontsize=6)
        ax.tick_params(axis='z', labelsize=7)


register_renderer('consumer', ConsumerRenderer)
