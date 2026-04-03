# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""Gaming simulator — rigid body physics, entities, terrain, AI.

Pure Python, cross-platform. No OS-specific dependencies.
"""
import math
import random


class GamingSimulator:
    """Game world & physics simulator.

    Physics: rigid body physics, collision detection, entity AI.
    Scenarios: physics_sandbox, entity_battle, terrain_exploration,
               ai_patrol, stress_test.
    """

    PRODUCT_TYPE = 'gaming'
    DISPLAY_NAME = 'Game World'

    SCENARIOS = {
        'physics_sandbox': {
            'gravity': -9.81, 'objects': 10,
            'description': 'Free physics sandbox with bouncing objects',
        },
        'entity_battle': {
            'team_a': 5, 'team_b': 5,
            'description': 'Two teams of AI entities in combat',
        },
        'terrain_exploration': {
            'map_size': 100, 'poi_count': 8,
            'description': 'Explorer entity navigating terrain',
        },
        'ai_patrol': {
            'patrol_points': 6, 'guard_count': 4,
            'description': 'AI guards patrolling waypoints',
        },
        'stress_test': {
            'entity_count': 100, 'physics_objects': 50,
            'description': 'Maximum load stress test',
        },
    }

    def __init__(self, vm):
        self.vm = vm
        self.tick_count = 0
        self.state = {}
        self.scenario = ''
        self._scenario_step = 0

    def setup(self):
        from eosim.engine.native.peripherals.sensors_gaming import (
            PhysicsEngine, TerrainSensor, EntityManager)
        from eosim.engine.native.peripherals.actuators_gaming import GameController

        self.vm.add_peripheral('physics', PhysicsEngine('physics', 0x40150000))
        self.vm.add_peripheral('terrain', TerrainSensor('terrain', 0x40150100))
        self.vm.add_peripheral('entities', EntityManager('entities', 0x40150200))
        self.vm.add_peripheral('game_ctrl', GameController('game_ctrl', 0x40250000))

        self.state = {
            'player_pos': [0.0, 0.0, 1.0],
            'player_vel': [0.0, 0.0, 0.0],
            'entity_count': 0, 'active_entities': 0,
            'collision_count': 0, 'fps': 60,
            'terrain_height': 0.0, 'surface_type': 'grass',
            'time_scale': 1.0, 'score': 0,
            'scenario': '',
        }

    def load_scenario(self, name: str):
        if name in self.SCENARIOS:
            self.scenario = name
            self._scenario_step = 0
            self.state['scenario'] = name
            cfg = self.SCENARIOS[name]
            entities = self.vm.peripherals.get('entities')
            if entities and name == 'entity_battle':
                for i in range(cfg.get('team_a', 5)):
                    entities.spawn_entity(i, random.uniform(-10, 0), random.uniform(-10, 10), 0)
                for i in range(cfg.get('team_b', 5)):
                    entities.spawn_entity(100 + i, random.uniform(0, 10), random.uniform(-10, 10), 0)
            elif entities and name == 'stress_test':
                for i in range(cfg.get('entity_count', 100)):
                    entities.spawn_entity(i, random.uniform(-50, 50), random.uniform(-50, 50), 0)

    def tick(self):
        self.tick_count += 1
        for name, dev in self.vm.peripherals.items():
            if hasattr(dev, 'simulate_tick'):
                dev.simulate_tick()

        self._apply_scenario()

        physics = self.vm.peripherals.get('physics')
        terrain = self.vm.peripherals.get('terrain')
        entities = self.vm.peripherals.get('entities')
        game_ctrl = self.vm.peripherals.get('game_ctrl')

        if physics:
            self.state['player_pos'] = [round(p, 3) for p in physics.position]
            self.state['player_vel'] = [round(v, 3) for v in physics.velocity]
            self.state['collision_count'] = physics.collision_count

        if terrain:
            self.state['terrain_height'] = round(terrain.height_at_pos, 2)
            surface_map = {0: 'grass', 1: 'rock', 2: 'water', 3: 'sand'}
            self.state['surface_type'] = surface_map.get(terrain.surface_type, 'unknown')

        if entities:
            self.state['entity_count'] = entities.entity_count
            self.state['active_entities'] = entities.active_entities

        if game_ctrl:
            self.state['time_scale'] = game_ctrl.time_scale

        load = (self.state.get('entity_count', 0) * 0.3 +
                self.state.get('collision_count', 0) * 0.1)
        self.state['fps'] = max(10, int(60 - load + random.gauss(0, 2)))

        self._scenario_step += 1

    def _apply_scenario(self):
        if not self.scenario:
            return
        cfg = self.SCENARIOS.get(self.scenario, {})
        physics = self.vm.peripherals.get('physics')
        entities = self.vm.peripherals.get('entities')

        if self.scenario == 'physics_sandbox':
            if physics and self._scenario_step % 100 == 0:
                physics.apply_force(
                    random.uniform(-50, 50),
                    random.uniform(-50, 50),
                    random.uniform(50, 200),
                )

        elif self.scenario == 'entity_battle':
            if entities:
                for ent in entities.entities:
                    if ent.get('active'):
                        for i in range(3):
                            ent['velocity'][i] = random.gauss(0, 1)
                if self._scenario_step % 50 == 0:
                    active = [e for e in entities.entities if e.get('active')]
                    if len(active) > 1:
                        victim = random.choice(active)
                        victim['active'] = False
                        self.state['score'] += 10

        elif self.scenario == 'terrain_exploration':
            if physics:
                physics.velocity[0] = math.cos(self._scenario_step * 0.02) * 3
                physics.velocity[1] = math.sin(self._scenario_step * 0.02) * 3

        elif self.scenario == 'ai_patrol':
            patrol_points = cfg.get('patrol_points', 6)
            if entities:
                for ent in entities.entities:
                    wp = self._scenario_step // 100 % patrol_points
                    angle = 2 * math.pi * wp / patrol_points
                    ent['velocity'] = [math.cos(angle) * 2, math.sin(angle) * 2, 0]

    def get_state(self) -> dict:
        return dict(self.state)

    def get_peripherals(self) -> dict:
        return dict(self.vm.peripherals)

    def get_status_text(self) -> str:
        scn = f" [{self.scenario}]" if self.scenario else ""
        return f"{self.DISPLAY_NAME} | Tick {self.tick_count}{scn}"

    def reset(self):
        self.tick_count = 0
        self.state = {}
        self.scenario = ''
        self._scenario_step = 0
