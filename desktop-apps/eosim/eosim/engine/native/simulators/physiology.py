# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""Physiology simulator — patient cardiovascular, respiratory, pharmacokinetics."""
import math
import random


class PhysiologySimulator:
    PRODUCT_TYPE = 'physiology'
    DISPLAY_NAME = 'Patient Physiology'

    SCENARIOS = {
        'normal_vitals': {
            'hr': 72, 'spo2': 98, 'bp_sys': 120, 'bp_dia': 80,
            'description': 'Normal healthy patient vitals',
        },
        'cardiac_arrest': {
            'hr': 0, 'spo2': 60, 'bp_sys': 0, 'bp_dia': 0,
            'description': 'Cardiac arrest',
        },
        'respiratory_distress': {
            'hr': 110, 'spo2': 82, 'rr': 32,
            'description': 'Acute respiratory distress',
        },
        'drug_administration': {
            'hr': 72, 'drug_dose_mg': 10, 'drug_half_life_min': 30,
            'description': 'IV drug administration with PK modeling',
        },
        'hemorrhage': {
            'hr': 130, 'spo2': 90, 'bp_sys': 80, 'bp_dia': 50,
            'description': 'Class III hemorrhage',
        },
    }

    def __init__(self, vm):
        self.vm = vm
        self.tick_count = 0
        self.state = {}
        self.scenario = ''
        self._scenario_step = 0

    def setup(self):
        from eosim.engine.native.peripherals.sensors_physiology import (
            HeartModel, LungModel, BloodPressureSensor)
        from eosim.engine.native.peripherals.actuators_physiology import (
            VentilatorActuator, InfusionPump, SurgicalTool)
        self.vm.add_peripheral('heart', HeartModel('heart', 0x40120000))
        self.vm.add_peripheral('lung', LungModel('lung', 0x40120100))
        self.vm.add_peripheral('bp', BloodPressureSensor('bp', 0x40120200))
        self.vm.add_peripheral('ventilator', VentilatorActuator('ventilator', 0x40220000))
        self.vm.add_peripheral('infusion', InfusionPump('infusion', 0x40220100))
        self.vm.add_peripheral('surgical', SurgicalTool('surgical', 0x40220200))
        self.state = {
            'heart_rate': 72, 'cardiac_output_lpm': 5.0,
            'spo2': 98.0, 'respiratory_rate': 16,
            'bp_sys': 120.0, 'bp_dia': 80.0, 'map': 93.3,
            'temperature': 37.0, 'drug_concentration': 0.0,
            'blood_volume_ml': 5000, 'scenario': '',
        }

    def load_scenario(self, name):
        if name in self.SCENARIOS:
            self.scenario = name
            self._scenario_step = 0
            self.state['scenario'] = name

    def tick(self):
        self.tick_count += 1
        for n, dev in self.vm.peripherals.items():
            if hasattr(dev, 'simulate_tick'):
                dev.simulate_tick()
        heart = self.vm.peripherals.get('heart')
        lung = self.vm.peripherals.get('lung')
        bp = self.vm.peripherals.get('bp')
        if heart:
            self.state['heart_rate'] = round(heart.heart_rate_bpm, 0)
            self.state['cardiac_output_lpm'] = round(heart.cardiac_output_lpm, 2)
        if lung:
            self.state['spo2'] = round(lung.spo2_percent, 1)
            self.state['respiratory_rate'] = round(lung.respiratory_rate, 0)
        if bp:
            self.state['bp_sys'] = round(bp.systolic_mmhg, 0)
            self.state['bp_dia'] = round(bp.diastolic_mmhg, 0)
            self.state['map'] = round(bp.mean_arterial_pressure, 1)
        self.state['temperature'] += random.gauss(0, 0.005)
        self.state['temperature'] = round(max(35, min(42, self.state['temperature'])), 1)
        self._scenario_step += 1

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
