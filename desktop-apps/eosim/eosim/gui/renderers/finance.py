# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""3D renderer for financial markets (domain: finance)."""
from eosim.gui.renderers import BaseRenderer, register_renderer


class FinanceRenderer(BaseRenderer):
    DOMAIN = "finance"
    DISPLAY_NAME = "Financial Market"

    def __init__(self):
        super().__init__()
        self._price_history = []

    def setup(self, ax):
        ax.set_xlim(0, 100)
        ax.set_ylim(-1, 1)
        ax.set_zlim(80, 120)
        ax.set_title("Financial Market", fontsize=9)

    def update(self, ax, state):
        price = state.get("price", 100)
        pnl = state.get("pnl", 0)
        ax.set_title("Market $%.2f PnL=$%.2f" % (price, pnl), fontsize=8)


register_renderer("finance", FinanceRenderer)
