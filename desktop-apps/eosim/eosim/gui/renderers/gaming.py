# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""3D renderer for game worlds (domain: gaming)."""
from eosim.gui.renderers import BaseRenderer, register_renderer


class GamingRenderer(BaseRenderer):
    DOMAIN = "gaming"
    DISPLAY_NAME = "Game World"

    def __init__(self):
        super().__init__()

    def setup(self, ax):
        ax.set_xlim(-15, 15)
        ax.set_ylim(-15, 15)
        ax.set_zlim(-1, 10)
        ax.set_title("Game World", fontsize=9)

    def update(self, ax, state):
        pos = state.get("player_pos", [0, 0, 1])
        fps = state.get("fps", 60)
        score = state.get("score", 0)
        ax.set_title("Game Pos=(%.1f,%.1f,%.1f) FPS=%d Score=%d" % (pos[0], pos[1], pos[2], fps, score), fontsize=7)


register_renderer("gaming", GamingRenderer)
