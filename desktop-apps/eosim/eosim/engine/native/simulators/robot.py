# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""Robot simulator. Pure Python, cross-platform."""
import math


class RobotSimulator:
    PRODUCT_TYPE = 'robot'
    DISPLAY_NAME = 'Robot Controller'
    SCENARIOS = {
        'home_calibration': {'description': 'Move all joints to home position'},
        'pick_and_place': {'pick': [45, 60, 120, 90, 45, 90], 'place': [135, 60, 120, 90, 135, 90], 'description': 'Pick and place'},
        'path_planning': {'waypoints': [[90]*6, [60,70,110,80,100,90], [120,50,130,100,80,90], [90]*6], 'description': 'Joint-space path'},
        'obstacle_avoidance': {'safe_cm': 30, 'description': 'Stop on obstacle'},
        'force_assembly': {'target_n': 5.0, 'description': 'Force-controlled insertion'},
    }
    LINK_LENGTHS = [0.2, 0.3, 0.25, 0.1, 0.1, 0.05]

    def __init__(self, vm):
        self.vm = vm; self.tick_count = 0; self.state = {}
        self.scenario = ''; self._scenario_step = 0
        self._targets = [90.0]*6; self._wp_idx = 0; self._gripper = False; self._phase = 'idle'

    def setup(self):
        from eosim.engine.native.peripherals.sensors import IMUSensor, ProximitySensor
        from eosim.engine.native.peripherals.actuators import ServoController, MotorController
        self.vm.add_peripheral('servo0', ServoController('servo0', 0x40200100, 6))
        self.vm.add_peripheral('motor0', MotorController('motor0', 0x40200000))
        self.vm.add_peripheral('imu0', IMUSensor('imu0', 0x40100200))
        self.vm.add_peripheral('prox0', ProximitySensor('prox0', 0x40100400))
        self.state = {'joint_angles': [90.0]*6, 'obstacle_dist_cm': 400, 'mode': 'IDLE', 'scenario': ''}

    def forward_kinematics(self, angles):
        x, z, c = 0.0, 0.0, 0.0
        for a, l in zip(angles, self.LINK_LENGTHS):
            c += math.radians(a - 90); x += l * math.cos(c); z += l * math.sin(c)
        return [round(x, 4), 0, round(z, 4)]

    def load_scenario(self, name):
        if name not in self.SCENARIOS: return
        self.scenario = name; self._scenario_step = 0; self._wp_idx = 0; self.state['scenario'] = name; self._phase = 'start'
        if name == 'home_calibration': self._targets = [90.0]*6; self.state['mode'] = 'CALIBRATING'
        elif name == 'pick_and_place': self._targets = list(self.SCENARIOS[name]['pick']); self._phase = 'pick'; self.state['mode'] = 'RUNNING'
        elif name == 'path_planning': self._targets = list(self.SCENARIOS[name]['waypoints'][0]); self.state['mode'] = 'RUNNING'
        elif name == 'obstacle_avoidance': self.state['mode'] = 'RUNNING'
        elif name == 'force_assembly': self._phase = 'approach'; self.state['mode'] = 'RUNNING'

    def _at_target(self, servo):
        return all(abs(servo.positions[i] - self._targets[i]) < 2 for i in range(min(6, servo.channels)))

    def tick(self):
        self.tick_count += 1
        for n, d in self.vm.peripherals.items():
            if hasattr(d, 'simulate_tick'): d.simulate_tick()
        servo = self.vm.peripherals.get('servo0')
        prox = self.vm.peripherals.get('prox0')
        if self.scenario == 'pick_and_place' and servo:
            cfg = self.SCENARIOS['pick_and_place']
            if self._phase == 'pick': self._targets = list(cfg['pick']); (self._gripper, self._phase) = (True, 'place') if self._at_target(servo) else (self._gripper, self._phase)
            elif self._phase == 'place': self._targets = list(cfg['place']); (self._gripper, self._phase, self.state['mode']) = (False, 'done', 'IDLE') if self._at_target(servo) else (self._gripper, self._phase, self.state['mode'])
        elif self.scenario == 'path_planning' and servo:
            wps = self.SCENARIOS['path_planning']['waypoints']
            if self._wp_idx < len(wps): self._targets = list(wps[self._wp_idx]); self._wp_idx += 1 if self._at_target(servo) else 0
            else: self.state['mode'] = 'IDLE'
        elif self.scenario == 'obstacle_avoidance' and prox:
            self.state['mode'] = 'E_STOP' if prox.distance_cm < self.SCENARIOS['obstacle_avoidance']['safe_cm'] else 'RUNNING'
        elif self.scenario == 'force_assembly' and self._phase == 'approach':
            self._targets[4] -= 0.5
            if abs(self._targets[4] - 90) * 0.1 >= self.SCENARIOS['force_assembly']['target_n']: self._phase = 'hold'; self.state['mode'] = 'IDLE'
        elif self.scenario == 'home_calibration' and servo and self._at_target(servo): self.state['mode'] = 'IDLE'
        if servo:
            for i in range(min(6, servo.channels)): servo.set_target(i, self._targets[i])
            self.state['joint_angles'] = [round(p, 1) for p in servo.positions[:6]]
        if prox: self.state['obstacle_dist_cm'] = round(prox.distance_cm, 1)
        self._scenario_step += 1

    def get_state(self): return dict(self.state)
    def get_peripherals(self): return dict(self.vm.peripherals)
    def get_status_text(self): return f"{self.DISPLAY_NAME} | {self.state.get('mode','IDLE')} | Tick {self.tick_count}"
    def reset(self): self.tick_count = 0; self.state = {}; self.scenario = ''; self._targets = [90.0]*6; self._wp_idx = 0
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""Robot simulator — 6-axis arm / mobile robot with kinematics.

Pure Python, cross-platform (Linux/Windows/macOS). No OS-specific dependencies.
"""
import math
import random


class RobotSimulator:
    """Industrial robot arm / mobile robot simulator.

    Physics: forward kinematics, joint angles, torques, workspace limits.
    Scenarios: pick-and-place, path planning, obstacle avoidance,
               force-controlled assembly, home position calibration.
    """

    PRODUCT_TYPE = 'robot'
    DISPLAY_NAME = 'Robot Controller'

    SCENARIOS = {
        'home_calibration': {'description': 'Move all joints to home (90 deg) position'},
        'pick_and_place': {
            'pick_pos': [45, 60, 120, 90, 45, 90],
            'place_pos': [135, 60, 120, 90, 135, 90],
            'description': 'Pick object from A, place at B',
        },
        'path_planning': {
            'waypoints': [
                [90, 90, 90, 90, 90, 90], [60, 70, 110, 80, 100, 90],
                [120, 50, 130, 100, 80, 90], [90, 90, 90, 90, 90, 90],
            ],
            'description': 'Follow planned joint-space path',
        },
        'obstacle_avoidance': {'safe_distance_cm': 30, 'description': 'Stop if obstacle detected'},
        'force_assembly': {'target_force_n': 5.0, 'description': 'Force-controlled insertion'},
    }

    LINK_LENGTHS = [0.2, 0.3, 0.25, 0.1, 0.1, 0.05]

    def __init__(self, vm):
        self.vm = vm
        self.tick_count = 0
        self.state = {}
        self.scenario = ''
        self._scenario_step = 0
        self._target_joints = [90.0] * 6
        self._waypoint_idx = 0
        self._gripper_closed = False
        self._phase = 'idle'

    def setup(self):
        from eosim.engine.native.peripherals.sensors import IMUSensor, ProximitySensor
        from eosim.engine.native.peripherals.actuators import ServoController, MotorController

        self.vm.add_peripheral('servo0', ServoController('servo0', 0x40200100, 6))
        self.vm.add_peripheral('motor0', MotorController('motor0', 0x40200000))
        self.vm.add_peripheral('imu0', IMUSensor('imu0', 0x40100200))
        self.vm.add_peripheral('prox0', ProximitySensor('prox0', 0x40100400))
        self.vm.add_peripheral('prox1', ProximitySensor('prox1', 0x40100410, 200))

        self.state = {
            'joint_angles': [90.0] * 6, 'joint_torques': [0.0] * 6,
            'end_effector_xyz': [0, 0, 0], 'gripper_open': True,
            'obstacle_dist_cm': 400, 'mode': 'IDLE', 'scenario': '',
            'workspace_violation': False,
        }

    def forward_kinematics(self, angles: list) -> list:
        x, y, z = 0.0, 0.0, 0.0
        cumulative = 0.0
        for angle, length in zip(angles, self.LINK_LENGTHS):
            rad = math.radians(angle - 90)
            cumulative += rad
            x += length * math.cos(cumulative)
            z += length * math.sin(cumulative)
        y = self.LINK_LENGTHS[0] * math.sin(math.radians(angles[0] - 90))
        return [round(x, 4), round(y, 4), round(z, 4)]

    def load_scenario(self, name: str):
        if name not in self.SCENARIOS:
            return
        self.scenario = name
        self._scenario_step = 0
        self._waypoint_idx = 0
        self.state['scenario'] = name
        self._phase = 'start'

        if name == 'home_calibration':
            self._target_joints = [90.0] * 6
            self.state['mode'] = 'CALIBRATING'
        elif name == 'pick_and_place':
            self._target_joints = list(self.SCENARIOS[name]['pick_pos'])
            self._gripper_closed = False
            self.state['mode'] = 'RUNNING'
            self._phase = 'move_to_pick'
        elif name == 'path_planning':
            self._target_joints = list(self.SCENARIOS[name]['waypoints'][0])
            self.state['mode'] = 'RUNNING'
        elif name == 'obstacle_avoidance':
            self.state['mode'] = 'RUNNING'
        elif name == 'force_assembly':
            self.state['mode'] = 'RUNNING'
            self._phase = 'approach'

    def _at_target(self, servo) -> bool:
        for i in range(min(6, servo.channels)):
            if abs(servo.positions[i] - self._target_joints[i]) > 2.0:
                return False
        return True

    def tick(self):
        self.tick_count += 1
        for name, dev in self.vm.peripherals.items():
            if hasattr(dev, 'simulate_tick'):
                dev.simulate_tick()

        servo = self.vm.peripherals.get('servo0')
        prox = self.vm.peripherals.get('prox0')

        self._apply_scenario(servo, prox)

        if servo:
            for i in range(min(6, servo.channels)):
                servo.set_target(i, self._target_joints[i])
            self.state['joint_angles'] = [round(p, 1) for p in servo.positions[:6]]
            for i in range(6):
                self.state['joint_torques'][i] = round(
                    abs(servo.targets[i] - servo.positions[i]) * 0.1, 2)

        self.state['end_effector_xyz'] = self.forward_kinematics(self.state['joint_angles'])
        self.state['gripper_open'] = not self._gripper_closed

        reach = math.sqrt(sum(c * c for c in self.state['end_effector_xyz']))
        self.state['workspace_violation'] = reach > sum(self.LINK_LENGTHS) * 0.95

        if prox:
            self.state['obstacle_dist_cm'] = round(prox.distance_cm, 1)
        self._scenario_step += 1

    def _apply_scenario(self, servo, prox):
        if not self.scenario:
            return
        if self.scenario == 'home_calibration':
            if servo and self._at_target(servo):
                self.state['mode'] = 'IDLE'
                self._phase = 'done'
        elif self.scenario == 'pick_and_place':
            cfg = self.SCENARIOS['pick_and_place']
            if self._phase == 'move_to_pick':
                self._target_joints = list(cfg['pick_pos'])
                if servo and self._at_target(servo):
                    self._gripper_closed = True
                    self._phase = 'move_to_place'
            elif self._phase == 'move_to_place':
                self._target_joints = list(cfg['place_pos'])
                if servo and self._at_target(servo):
                    self._gripper_closed = False
                    self._phase = 'done'
                    self.state['mode'] = 'IDLE'
        elif self.scenario == 'path_planning':
            wps = self.SCENARIOS['path_planning']['waypoints']
            if self._waypoint_idx < len(wps):
                self._target_joints = list(wps[self._waypoint_idx])
                if servo and self._at_target(servo):
                    self._waypoint_idx += 1
            else:
                self.state['mode'] = 'IDLE'
        elif self.scenario == 'obstacle_avoidance':
            safe = self.SCENARIOS['obstacle_avoidance']['safe_distance_cm']
            if prox and prox.distance_cm < safe:
                self.state['mode'] = 'E_STOP'
            else:
                self.state['mode'] = 'RUNNING'
        elif self.scenario == 'force_assembly':
            if self._phase == 'approach':
                self._target_joints[4] -= 0.5
                force = abs(self._target_joints[4] - 90) * 0.1
                target_f = self.SCENARIOS['force_assembly']['target_force_n']
                if force >= target_f:
                    self._phase = 'hold'
                    self.state['mode'] = 'IDLE'

    def get_state(self) -> dict:
        return dict(self.state)

    def get_peripherals(self) -> dict:
        return dict(self.vm.peripherals)

    def get_status_text(self) -> str:
        mode = self.state.get('mode', 'IDLE')
        return f"{self.DISPLAY_NAME} | {mode} | Tick {self.tick_count}"

    def reset(self):
        self.tick_count = 0
        self.state = {}
        self.scenario = ''
        self._scenario_step = 0
        self._target_joints = [90.0] * 6
        self._waypoint_idx = 0
