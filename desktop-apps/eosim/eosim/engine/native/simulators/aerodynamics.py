# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""Aerodynamics simulator — wind tunnel, airfoil analysis, CFD.

Pure Python, cross-platform. No OS-specific dependencies.
"""
import math
import random


class AerodynamicsSimulator:
    """Aerodynamics & CFD simulator.

    Physics: Reynolds number, Cl/Cd curves, pressure distribution, turbulence.
    Scenarios: wind_tunnel_test, airfoil_sweep, turbulence_analysis,
               drag_reduction, mach_transition.
    """

    PRODUCT_TYPE = 'aerodynamics'
    DISPLAY_NAME = 'Aerodynamics / CFD'

    SCENARIOS = {
        'wind_tunnel_test': {
            'airspeed_mps': 50, 'aoa_deg': 5,
            'description': 'Standard wind tunnel test at moderate speed',
        },
        'airfoil_sweep': {
            'aoa_range': (-5, 20), 'airspeed_mps': 30,
            'description': 'Angle of attack sweep for Cl/Cd polar',
        },
        'turbulence_analysis': {
            'turbulence_intensity': 0.1, 'airspeed_mps': 40,
            'description': 'Turbulence intensity study',
        },
        'drag_reduction': {
            'airspeed_mps': 60, 'aoa_deg': 2,
            'description': 'Drag reduction optimization at cruise',
        },
        'mach_transition': {
            'mach_range': (0.7, 1.3), 'aoa_deg': 0,
            'description': 'Transonic Mach number sweep',
        },
    }

    def __init__(self, vm):
        self.vm = vm
        self.tick_count = 0
        self.state = {}
        self.scenario = ''
        self._scenario_step = 0

    def setup(self):
        from eosim.engine.native.peripherals.sensors_aerodynamics import (
            WindTunnelSensor, AirflowSensor, PitotTube, ForceBalance)
        from eosim.engine.native.peripherals.actuators_aerodynamics import (
            AeroActuator, TunnelFanController)

        self.vm.add_peripheral('wind_tunnel', WindTunnelSensor('wind_tunnel', 0x40110000))
        self.vm.add_peripheral('airflow', AirflowSensor('airflow', 0x40110100))
        self.vm.add_peripheral('pitot', PitotTube('pitot', 0x40110200))
        self.vm.add_peripheral('balance', ForceBalance('balance', 0x40110300))
        self.vm.add_peripheral('aero_act', AeroActuator('aero_act', 0x40210000))
        self.vm.add_peripheral('fan', TunnelFanController('fan', 0x40210100))

        self.state = {
            'airspeed_mps': 0.0, 'mach_number': 0.0, 'aoa_deg': 0.0,
            'reynolds_number': 0.0, 'cl': 0.0, 'cd': 0.01,
            'lift_n': 0.0, 'drag_n': 0.0, 'dynamic_pressure_pa': 0.0,
            'turbulence_intensity': 0.0, 'pressure_coeff': 0.0,
            'scenario': '',
        }

    def load_scenario(self, name):
        if name in self.SCENARIOS:
            self.scenario = name
            self._scenario_step = 0
            self.state['scenario'] = name
            cfg = self.SCENARIOS[name]
            if 'airspeed_mps' in cfg:
                tunnel = self.vm.peripherals.get('wind_tunnel')
                if tunnel:
                    tunnel.set_airspeed(cfg['airspeed_mps'])

    def tick(self):
        self.tick_count += 1
        for name, dev in self.vm.peripherals.items():
            if hasattr(dev, 'simulate_tick'):
                dev.simulate_tick()

        self._apply_scenario()

        tunnel = self.vm.peripherals.get('wind_tunnel')
        airflow = self.vm.peripherals.get('airflow')
        balance = self.vm.peripherals.get('balance')
        fan = self.vm.peripherals.get('fan')

        airspeed = tunnel.airspeed_mps if tunnel else 0
        self.state['airspeed_mps'] = round(airspeed, 2)
        self.state['mach_number'] = round(tunnel.mach_number if tunnel else 0, 4)
        self.state['dynamic_pressure_pa'] = round(tunnel.dynamic_pressure_pa if tunnel else 0, 1)

        aoa = self.state.get('aoa_deg', 0)
        aoa_rad = math.radians(aoa)
        cl = 2 * math.pi * math.sin(aoa_rad) * 0.9
        cd = 0.008 + cl * cl / (math.pi * 6 * 0.85)
        self.state['cl'] = round(cl, 4)
        self.state['cd'] = round(cd, 5)

        chord = 1.0
        nu = 1.46e-5
        self.state['reynolds_number'] = round(airspeed * chord / nu if nu > 0 else 0, 0)

        q = tunnel.dynamic_pressure_pa if tunnel else 0
        span = 2.0
        area = chord * span
        lift = q * area * cl
        drag = q * area * cd
        self.state['lift_n'] = round(lift, 2)
        self.state['drag_n'] = round(drag, 2)

        if balance:
            balance.set_forces(lift, drag)

        if airflow:
            self.state['turbulence_intensity'] = round(airflow.turbulence_intensity, 4)

        self.state['pressure_coeff'] = round(1 - (airspeed / 340.0) ** 2, 4) if airspeed < 340 else 0

        self._scenario_step += 1

    def _apply_scenario(self):
        if not self.scenario:
            return
        cfg = self.SCENARIOS.get(self.scenario, {})
        tunnel = self.vm.peripherals.get('wind_tunnel')
        fan = self.vm.peripherals.get('fan')

        if self.scenario == 'wind_tunnel_test':
            if fan:
                fan.target_speed_rpm = int(cfg.get('airspeed_mps', 50) * 100)
            self.state['aoa_deg'] = cfg.get('aoa_deg', 5)

        elif self.scenario == 'airfoil_sweep':
            aoa_range = cfg.get('aoa_range', (-5, 20))
            steps = 500
            progress = min(self._scenario_step / steps, 1.0)
            aoa = aoa_range[0] + (aoa_range[1] - aoa_range[0]) * progress
            self.state['aoa_deg'] = round(aoa, 1)

        elif self.scenario == 'turbulence_analysis':
            self.state['aoa_deg'] = 5 + random.gauss(0, 0.5)

        elif self.scenario == 'drag_reduction':
            self.state['aoa_deg'] = cfg.get('aoa_deg', 2)

        elif self.scenario == 'mach_transition':
            mach_range = cfg.get('mach_range', (0.7, 1.3))
            steps = 600
            progress = min(self._scenario_step / steps, 1.0)
            target_mach = mach_range[0] + (mach_range[1] - mach_range[0]) * progress
            target_speed = target_mach * 340
            if tunnel:
                tunnel.set_airspeed(target_speed)
            self.state['aoa_deg'] = cfg.get('aoa_deg', 0)

    def get_state(self):
        return dict(self.state)

    def get_peripherals(self):
        return dict(self.vm.peripherals)

    def get_status_text(self):
        scn = " [%s]" % self.scenario if self.scenario else ""
        return "%s | Tick %d%s" % (self.DISPLAY_NAME, self.tick_count, scn)

    def reset(self):
        self.tick_count = 0
        self.state = {}
        self.scenario = ''
        self._scenario_step = 0
