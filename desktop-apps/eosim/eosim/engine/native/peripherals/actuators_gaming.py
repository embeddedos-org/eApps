# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
import random
from eosim.engine.native.peripherals.actuators import ActuatorBase


class GameController(ActuatorBase):
    def __init__(self, name='game_ctrl0', base_addr=0x40250000):
        super().__init__(name, base_addr)
        self.spawn_queue = []
        self.destroy_queue = []
        self.force_x = 0.0
        self.force_y = 0.0
        self.force_z = 0.0
        self.time_scale = 1.0
        self.paused = False
        self.commands_processed = 0
    def simulate_tick(self):
        self.commands_processed += len(self.spawn_queue) + len(self.destroy_queue)
        self.spawn_queue.clear()
        self.destroy_queue.clear()
    def spawn(self, entity_type, x, y, z):
        self.spawn_queue.append({"type": entity_type, "pos": [x, y, z]})
    def destroy(self, entity_id):
        self.destroy_queue.append(entity_id)
    def read_reg(self, offset):
        if offset == 0x00: return self.commands_processed & 0xFFFFFFFF
        if offset == 0x04: return int(self.time_scale * 1000) & 0xFFFFFFFF
        if offset == 0x08: return int(self.paused)
        return 0
    def write_reg(self, offset, val):
        if offset == 0x00: self.time_scale = max(0.01, min(10.0, val / 1000.0))
        elif offset == 0x04: self.paused = bool(val & 1)
