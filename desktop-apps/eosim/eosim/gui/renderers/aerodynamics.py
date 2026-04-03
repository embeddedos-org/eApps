# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""3D renderer for aerodynamics (domain: aerodynamics)."""
import math
from eosim.gui.renderers import BaseRenderer, register_renderer


class AerodynamicsRenderer(BaseRenderer):
    DOMAIN = "aerodynamics"
    DISPLAY_NAME = "Aerodynamics"

    def __init__(self):
        super().__init__()

    def setup(self, ax):
        ax.set_xlim(-2, 2)
        ax.set_ylim(-2, 2)
        ax.set_zlim(-1, 3)
        ax.set_title("Aerodynamics", fontsize=9)

    def update(self, ax, state):
        aoa = state.get("aoa_deg", 0)
        cl = state.get("cl", 0)
        cd = state.get("cd", 0)
        airspeed = state.get("airspeed_mps", 0)
        mach = state.get("mach_number", 0)
        ax.set_title("Aero V=%.0fm/s M=%.3f AoA=%.1f Cl=%.3f Cd=%.4f" % (airspeed, mach, aoa, cl, cd), fontsize=8)


register_renderer("aerodynamics", AerodynamicsRenderer)
