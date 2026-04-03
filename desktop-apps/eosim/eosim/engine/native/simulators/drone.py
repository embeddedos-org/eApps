# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""Drone / UAV simulator — quadrotor/multirotor with flight modes.

Pure Python, cross-platform (Linux/Windows/macOS). No OS-specific dependencies.
"""
import math
import random


class DroneSimulator:
    """Quadrotor/multirotor UAV simulator.

    Physics: attitude (roll/pitch/yaw), altitude, motor mixing, simplified PID.
    Flight modes: DISARMED, STABILIZE, ALT_HOLD, LOITER, RTL, WAYPOINT.
    Scenarios: takeoff, hover, waypoint mission, wind gust, low battery RTL, motor failure.
    """

    PRODUCT_TYPE = 'drone'
    DISPLAY_NAME = 'Drone / UAV'

    FLIGHT_MODES = ['DISARMED', 'STABILIZE', 'ALT_HOLD', 'LOITER', 'RTL', 'WAYPOINT']

    SCENARIOS = {
        'takeoff': {'description': 'Arm and climb to 10m altitude'},
        'hover': {'description': 'Hold position at current altitude'},
        'waypoint_mission': {
            'waypoints': [(37.3861, -122.0839, 50), (37.3870, -122.0830, 50),
                          (37.3875, -122.0840, 30)],
            'description': 'Fly through GPS waypoints',
        },
        'wind_gust': {'wind_speed_mps': 8, 'wind_dir_deg': 45, 'description': 'Respond to sudden wind gust'},
        'low_battery_rtl': {'soc_trigger': 20, 'description': 'Auto RTL when battery low'},
        'motor_failure': {'failed_motor': 2, 'description': 'Motor 3 failure mid-flight'},
    }

    def __init__(self, vm):
        self.vm = vm
        self.tick_count = 0
        self.state = {}
        self.scenario = ''
        self._scenario_step = 0
        self._pid_alt = {'p': 0.5, 'i': 0.01, 'd': 0.2, 'integral': 0, 'prev_error': 0}
        self._pid_roll = {'p': 0.8, 'i': 0.02, 'd': 0.3, 'integral': 0, 'prev_error': 0}
        self._pid_pitch = {'p': 0.8, 'i': 0.02, 'd': 0.3, 'integral': 0, 'prev_error': 0}
        self._home_lat = 0
        self._home_lon = 0
        self._waypoint_idx = 0
        self._target_alt = 0
        self._wind = [0, 0]

    def setup(self):
        from eosim.engine.native.peripherals.sensors import IMUSensor, GPSModule, PressureSensor
        from eosim.engine.native.peripherals.actuators import ESCController
        from eosim.engine.native.peripherals.composites import BatteryManagement

        self.vm.add_peripheral('imu0', IMUSensor('imu0', 0x40100200, 9))
        self.vm.add_peripheral('gps0', GPSModule('gps0', 0x40100300))
        self.vm.add_peripheral('baro0', PressureSensor('baro0', 0x40100100))
        self.vm.add_peripheral('esc0', ESCController('esc0', 0x40200200, 4))
        self.vm.add_peripheral('bms0', BatteryManagement('bms0', 0x40500000, 4, 5000))

        gps = self.vm.peripherals['gps0']
        self._home_lat = gps.latitude
        self._home_lon = gps.longitude

        self.state = {
            'altitude_m': 0, 'roll_deg': 0, 'pitch_deg': 0, 'yaw_deg': 0,
            'vx_mps': 0, 'vy_mps': 0, 'vz_mps': 0,
            'flight_mode': 'DISARMED', 'motor_rpm': [0, 0, 0, 0],
            'soc_pct': 85, 'scenario': '', 'motor_failure': -1,
        }

    def load_scenario(self, name: str):
        if name in self.SCENARIOS:
            self.scenario = name
            self._scenario_step = 0
            self.state['scenario'] = name
            self._waypoint_idx = 0

            if name == 'takeoff':
                self.set_flight_mode('ALT_HOLD')
                self._target_alt = 10
                esc = self.vm.peripherals.get('esc0')
                if esc:
                    esc.armed = True
                    esc.enabled = True

            elif name == 'hover':
                self.set_flight_mode('LOITER')
                self._target_alt = self.state.get('altitude_m', 10)

            elif name == 'waypoint_mission':
                self.set_flight_mode('WAYPOINT')
                esc = self.vm.peripherals.get('esc0')
                if esc:
                    esc.armed = True
                    esc.enabled = True
                self._target_alt = 50

            elif name == 'wind_gust':
                cfg = self.SCENARIOS[name]
                angle = math.radians(cfg['wind_dir_deg'])
                self._wind = [cfg['wind_speed_mps'] * math.cos(angle),
                              cfg['wind_speed_mps'] * math.sin(angle)]

            elif name == 'motor_failure':
                self.state['motor_failure'] = self.SCENARIOS[name]['failed_motor']

    def set_flight_mode(self, mode: str):
        if mode in self.FLIGHT_MODES:
            self.state['flight_mode'] = mode
            esc = self.vm.peripherals.get('esc0')
            if mode == 'DISARMED':
                if esc:
                    esc.armed = False
            else:
                if esc:
                    esc.armed = True
                    esc.enabled = True

    def _pid_compute(self, pid: dict, error: float) -> float:
        pid['integral'] += error * 0.01
        pid['integral'] = max(-50, min(50, pid['integral']))
        derivative = (error - pid['prev_error']) / 0.01
        pid['prev_error'] = error
        return pid['p'] * error + pid['i'] * pid['integral'] + pid['d'] * derivative

    def tick(self):
        self.tick_count += 1
        for name, dev in self.vm.peripherals.items():
            if hasattr(dev, 'simulate_tick'):
                dev.simulate_tick()

        esc = self.vm.peripherals.get('esc0')
        baro = self.vm.peripherals.get('baro0')
        imu = self.vm.peripherals.get('imu0')
        bms = self.vm.peripherals.get('bms0')
        gps = self.vm.peripherals.get('gps0')
        mode = self.state['flight_mode']

        if mode == 'DISARMED':
            self.state['motor_rpm'] = [0, 0, 0, 0]
            self.state['soc_pct'] = round(bms.soc_percent if bms else 0, 1)
            return

        if self.scenario == 'low_battery_rtl' and bms:
            trigger = self.SCENARIOS['low_battery_rtl']['soc_trigger']
            if bms.soc_percent < trigger and mode != 'RTL':
                self.set_flight_mode('RTL')

        base_throttle = 50
        roll_cmd = 0
        pitch_cmd = 0

        if mode == 'ALT_HOLD' or mode == 'LOITER' or mode == 'WAYPOINT':
            alt_error = self._target_alt - self.state.get('altitude_m', 0)
            alt_correction = self._pid_compute(self._pid_alt, alt_error)
            base_throttle = 50 + max(-30, min(30, alt_correction))

        if mode == 'STABILIZE':
            roll_error = 0 - self.state.get('roll_deg', 0)
            pitch_error = 0 - self.state.get('pitch_deg', 0)
            roll_cmd = self._pid_compute(self._pid_roll, roll_error)
            pitch_cmd = self._pid_compute(self._pid_pitch, pitch_error)

        if mode == 'LOITER':
            roll_error = 0 - self.state.get('roll_deg', 0)
            pitch_error = 0 - self.state.get('pitch_deg', 0)
            roll_cmd = self._pid_compute(self._pid_roll, roll_error)
            pitch_cmd = self._pid_compute(self._pid_pitch, pitch_error)

        if mode == 'RTL':
            self._target_alt = max(self.state.get('altitude_m', 0), 20)
            if gps:
                dlat = self._home_lat - gps.latitude
                dlon = self._home_lon - gps.longitude
                dist = math.sqrt(dlat ** 2 + dlon ** 2) * 111320
                if dist > 2:
                    pitch_cmd = min(15, dist * 0.5)
                    gps.heading_deg = math.degrees(math.atan2(dlon, dlat)) % 360
                else:
                    self._target_alt = max(0, self._target_alt - 0.5)
                    if self._target_alt < 1:
                        self.set_flight_mode('DISARMED')

        if mode == 'WAYPOINT':
            wps = self.SCENARIOS.get('waypoint_mission', {}).get('waypoints', [])
            if wps and self._waypoint_idx < len(wps) and gps:
                wp = wps[self._waypoint_idx]
                dlat = wp[0] - gps.latitude
                dlon = wp[1] - gps.longitude
                self._target_alt = wp[2]
                dist = math.sqrt(dlat ** 2 + dlon ** 2) * 111320
                if dist < 5:
                    self._waypoint_idx += 1
                else:
                    pitch_cmd = min(20, dist * 0.3)
                    gps.heading_deg = math.degrees(math.atan2(dlon, dlat)) % 360

        motor_mix = [
            base_throttle - roll_cmd + pitch_cmd,
            base_throttle + roll_cmd + pitch_cmd,
            base_throttle + roll_cmd - pitch_cmd,
            base_throttle - roll_cmd - pitch_cmd,
        ]

        failed = self.state.get('motor_failure', -1)
        if failed >= 0 and failed < 4:
            motor_mix[failed] = 0

        if esc:
            for i in range(min(4, esc.channels)):
                esc.throttle[i] = max(0, min(100, motor_mix[i]))

        if esc and esc.armed:
            avg_throttle = sum(esc.throttle) / len(esc.throttle)
            lift = (avg_throttle - 50) * 0.02
            gravity = -0.098
            self.state['vz_mps'] = self.state.get('vz_mps', 0) * 0.95 + lift + gravity

            self.state['vx_mps'] = self.state.get('vx_mps', 0) * 0.98 + self._wind[0] * 0.001
            self.state['vy_mps'] = self.state.get('vy_mps', 0) * 0.98 + self._wind[1] * 0.001

            alt = self.state.get('altitude_m', 0) + self.state['vz_mps'] * 0.1
            self.state['altitude_m'] = max(0, round(alt, 2))
            self.state['motor_rpm'] = list(esc.rpm)

            diff_lr = esc.throttle[0] - esc.throttle[1] if len(esc.throttle) > 1 else 0
            diff_fb = esc.throttle[2] - esc.throttle[3] if len(esc.throttle) > 3 else 0
            self.state['roll_deg'] = round(diff_lr * 0.5 + random.gauss(0, 0.3), 1)
            self.state['pitch_deg'] = round(diff_fb * 0.5 + random.gauss(0, 0.3), 1)
            self.state['yaw_deg'] = round((self.state.get('yaw_deg', 0) + random.gauss(0, 0.2)) % 360, 1)

            if baro:
                baro.set_altitude(self.state['altitude_m'])
            if imu:
                imu.set_accel(
                    self.state['pitch_deg'] * 0.1 + self._wind[0] * 0.01,
                    self.state['roll_deg'] * 0.1 + self._wind[1] * 0.01,
                    9.81 - self.state['vz_mps'] * 0.5)

        self.state['soc_pct'] = round(bms.soc_percent if bms else 0, 1)
        if bms:
            bms.current_ma = sum(self.state['motor_rpm']) * 0.05 + 200

        self._scenario_step += 1

    def get_state(self) -> dict:
        return dict(self.state)

    def get_peripherals(self) -> dict:
        return dict(self.vm.peripherals)

    def get_status_text(self) -> str:
        mode = self.state.get('flight_mode', 'DISARMED')
        alt = self.state.get('altitude_m', 0)
        return f"{self.DISPLAY_NAME} | {mode} | Alt {alt:.1f}m | Tick {self.tick_count}"

    def reset(self):
        self.tick_count = 0
        self.state = {}
        self.scenario = ''
        self._scenario_step = 0
        self._waypoint_idx = 0
        self._wind = [0, 0]
        for pid in [self._pid_alt, self._pid_roll, self._pid_pitch]:
            pid['integral'] = 0
            pid['prev_error'] = 0
