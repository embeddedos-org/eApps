# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""Gaming domain sensors — physics engine, terrain sensor, entity manager."""
import math
import random

from eosim.engine.native.peripherals.sensors import SensorBase


class PhysicsEngine(SensorBase):
    def __init__(self, name='physics0', base_addr=0x40150000):
        super().__init__(name, base_addr)
        self.position = [0.0, 0.0, 0.0]
        self.velocity = [0.0, 0.0, 0.0]
        self.collision_count = 0
        self.gravity = -9.81

    def simulate_tick(self):
        super().simulate_tick()
        self.velocity[2] += self.gravity * 0.01
        for i in range(3):
            self.position[i] += self.velocity[i] * 0.01
        if self.position[2] < 0:
            self.position[2] = 0
            self.velocity[2] = -self.velocity[2] * 0.6
            self.collision_count += 1

    def set_position(self, x, y, z):
        self.position = [x, y, z]

    def apply_force(self, fx, fy, fz, mass=1.0):
        if mass > 0:
            self.velocity[0] += fx / mass * 0.01
            self.velocity[1] += fy / mass * 0.01
            self.velocity[2] += fz / mass * 0.01

    def read_reg(self, offset):
        idx = offset // 4
        if idx < 3: return int(self.position[idx] * 1000) & 0xFFFFFFFF
        if idx < 6: return int(self.velocity[idx - 3] * 1000) & 0xFFFFFFFF
        if idx == 6: return self.collision_count & 0xFFFFFFFF
        return 0


class TerrainSensor(SensorBase):
    def __init__(self, name='terrain0', base_addr=0x40150100):
        super().__init__(name, base_addr)
        self.height_at_pos = 0.0
        self.surface_type = 0
        self.slope_deg = 0.0
        self.friction_coeff = 0.5

    def simulate_tick(self):
        super().simulate_tick()

    def set_terrain(self, height, surface, slope=0.0):
        self.height_at_pos = height
        self.surface_type = surface
        self.slope_deg = slope

    def read_reg(self, offset):
        if offset == 0x00: return int(self.height_at_pos * 1000) & 0xFFFFFFFF
        if offset == 0x04: return self.surface_type & 0xFFFFFFFF
        return 0


class EntityManager(SensorBase):
    def __init__(self, name='entities0', base_addr=0x40150200):
        super().__init__(name, base_addr)
        self.entity_count = 0
        self.active_entities = 0
        self.nearest_distance = 999.0
        self.entities = []

    def simulate_tick(self):
        super().simulate_tick()
        for ent in self.entities:
            for i in range(3):
                ent['position'][i] += ent.get('velocity', [0, 0, 0])[i] * 0.01
        self.active_entities = len([e for e in self.entities if e.get('active', True)])

    def spawn_entity(self, entity_id, x, y, z):
        self.entities.append({'id': entity_id, 'position': [x, y, z], 'velocity': [0, 0, 0], 'active': True})
        self.entity_count = len(self.entities)

    def read_reg(self, offset):
        if offset == 0x00: return self.entity_count & 0xFFFFFFFF
        if offset == 0x04: return self.active_entities & 0xFFFFFFFF
        return 0
