# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""3D renderer for 6-DOF robotic arms (domain: robotics)."""

import math

from eosim.gui.renderers import BaseRenderer, register_renderer

_LINK_LENGTHS = [0.2, 0.3, 0.25, 0.1, 0.1, 0.05]


class RobotRenderer(BaseRenderer):
    DOMAIN = "robotics"
    DISPLAY_NAME = "Robot Arm"

    def __init__(self):
        self._ee_trail: list = []

    # ---- DH-style forward kinematics (math module only) ----
    @staticmethod
    def _mat4_identity():
        return [
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1],
        ]

    @staticmethod
    def _mat4_mul(a, b):
        r = [[0.0] * 4 for _ in range(4)]
        for i in range(4):
            for j in range(4):
                for k in range(4):
                    r[i][j] += a[i][k] * b[k][j]
        return r

    @staticmethod
    def _dh_matrix(theta, d, a_len, alpha):
        ct, st = math.cos(theta), math.sin(theta)
        ca, sa = math.cos(alpha), math.sin(alpha)
        return [
            [ct, -st * ca,  st * sa, a_len * ct],
            [st,  ct * ca, -ct * sa, a_len * st],
            [0,   sa,       ca,      d],
            [0,   0,        0,       1],
        ]

    def _forward_kinematics(self, angles):
        """Return list of (x, y, z) joint positions from base to end-effector."""
        positions = [(0.0, 0.0, 0.0)]
        T = self._mat4_identity()

        # simplified DH: alternating axes along z then x
        for i, (length, theta) in enumerate(zip(_LINK_LENGTHS, angles)):
            alpha = math.pi / 2 if i % 2 == 0 else 0.0
            dh = self._dh_matrix(theta, 0.0, length, alpha)
            T = self._mat4_mul(T, dh)
            positions.append((T[0][3], T[1][3], T[2][3]))
        return positions

    # ---- renderer interface ----
    def setup(self, ax):
        ax.set_xlim(-0.8, 0.8)
        ax.set_ylim(-0.8, 0.8)
        ax.set_zlim(-0.2, 1.0)
        ax.set_xlabel("X", fontsize=7)
        ax.set_ylabel("Y", fontsize=7)
        ax.set_zlabel("Z", fontsize=7)
        ax.set_title("Robot Arm", fontsize=9)

    def update(self, ax, state: dict):
        raw_angles = state.get("joint_angles", [0.0] * 6)
        angles = [math.radians(a) for a in raw_angles]
        gripper_open = state.get("gripper_open", True)
        op_mode = state.get("op_mode", "IDLE")

        # compute joint positions
        joints = self._forward_kinematics(angles)

        # draw links as thick lines
        link_color = "#44aaff"
        for i in range(len(joints) - 1):
            x0, y0, z0 = joints[i]
            x1, y1, z1 = joints[i + 1]
            ax.plot([x0, x1], [y0, y1], [z0, z1],
                    color=link_color, linewidth=3, solid_capstyle="round")

        # draw joint markers
        jx = [j[0] for j in joints]
        jy = [j[1] for j in joints]
        jz = [j[2] for j in joints]
        ax.scatter(jx, jy, jz, color="#ffcc00", s=25, depthshade=False,
                   zorder=5)

        # end-effector marker
        ex, ey, ez = joints[-1]
        marker = "*" if gripper_open else "o"
        ee_color = "#00ff88" if gripper_open else "#ff4444"
        ax.scatter([ex], [ey], [ez], color=ee_color, s=80, marker=marker,
                   depthshade=False, zorder=6)

        # end-effector trail
        self._ee_trail.append((ex, ey, ez))
        if len(self._ee_trail) > 150:
            self._ee_trail = self._ee_trail[-150:]
        if len(self._ee_trail) > 1:
            n = len(self._ee_trail)
            for idx in range(0, n, max(1, n // 40)):
                px, py, pz = self._ee_trail[idx]
                alpha = 0.15 + 0.85 * (idx / n)
                ax.scatter([px], [py], [pz], color="#00ff88", s=6,
                           alpha=alpha, depthshade=False)

        # base plate
        ax.scatter([0], [0], [0], color="#666666", s=100, marker="s",
                   depthshade=False, zorder=1)

        ax.set_title(f"Robot  {op_mode}  grip={'OPEN' if gripper_open else 'CLOSED'}",
                     fontsize=8)


register_renderer("robotics", RobotRenderer)
