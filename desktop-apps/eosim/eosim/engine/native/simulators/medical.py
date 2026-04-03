# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""Medical device simulator — patient monitor with profiles and alarms.

Pure Python, cross-platform. No OS-specific dependencies.
"""
import math
import random


class MedicalSimulator:
    PRODUCT_TYPE = 'medical'
    DISPLAY_NAME = 'Medical Monitor'

    PATIENT_PROFILES = {
        'normal_adult': {'hr': 72, 'spo2': 98, 'temp': 36.8, 'bp_sys': 120, 'bp_dia': 80, 'rr': 16},
        'pediatric': {'hr': 110, 'spo2': 98, 'temp': 37.0, 'bp_sys': 90, 'bp_dia': 60, 'rr': 24},
        'cardiac_arrhythmia': {'hr': 140, 'spo2': 94, 'temp': 37.2, 'bp_sys': 100, 'bp_dia': 70, 'rr': 20},
        'respiratory_distress': {'hr': 100, 'spo2': 88, 'temp': 38.5, 'bp_sys': 130, 'bp_dia': 85, 'rr': 30},
        'sepsis': {'hr': 120, 'spo2': 92, 'temp': 39.5, 'bp_sys': 85, 'bp_dia': 55, 'rr': 26},
    }

    SCENARIOS = {
        'normal_monitoring': {'profile': 'normal_adult', 'description': 'Stable patient monitoring'},
        'alarm_trigger': {'profile': 'cardiac_arrhythmia', 'description': 'Cardiac alarm triggered'},
        'sensor_disconnect': {'description': 'SpO2 probe disconnected mid-monitoring'},
        'pump_occlusion': {'description': 'IV pump line occluded'},
        'battery_failover': {'description': 'AC power loss, switch to battery'},
    }

    def __init__(self, vm):
        self.vm = vm
        self.tick_count = 0
        self.state = {}
        self.scenario = ''
        self._scenario_step = 0
        self._profile = 'normal_adult'

    def setup(self):
        from eosim.engine.native.peripherals.sensors import ECGSensor, PulseOximeter, TemperatureSensor
        from eosim.engine.native.peripherals.actuators import PumpController, DisplayDriver
        from eosim.engine.native.peripherals.composites import WatchdogTimer, BatteryManagement

        self.vm.add_peripheral('ecg0', ECGSensor('ecg0', 0x40100800))
        self.vm.add_peripheral('spo2_0', PulseOximeter('spo2_0', 0x40100900))
        self.vm.add_peripheral('temp_patient', TemperatureSensor('temp_patient', 0x40100010, 30, 42))
        self.vm.add_peripheral('pump0', PumpController('pump0', 0x40200400))
        self.vm.add_peripheral('display0', DisplayDriver('display0', 0x40200600))
        self.vm.add_peripheral('wdt0', WatchdogTimer('wdt0', 0x40500200))
        self.vm.add_peripheral('bms0', BatteryManagement('bms0', 0x40500000, 2, 3000))

        self._apply_profile('normal_adult')
        self.state = {
            'heart_rate': 72, 'spo2': 98, 'temperature': 36.8,
            'bp_sys': 120, 'bp_dia': 80, 'resp_rate': 16,
            'alarm': 'NONE', 'alarm_priority': 0,
            'pump_flow': 0, 'ecg_waveform': [],
            'on_battery': False, 'soc_pct': 100,
            'profile': 'normal_adult', 'scenario': '',
            'sensor_connected': True,
        }

    def _apply_profile(self, name: str):
        p = self.PATIENT_PROFILES.get(name, self.PATIENT_PROFILES['normal_adult'])
        self._profile = name
        ecg = self.vm.peripherals.get('ecg0')
        spo2 = self.vm.peripherals.get('spo2_0')
        temp = self.vm.peripherals.get('temp_patient')
        if ecg:
            ecg.set_heart_rate(p['hr'])
        if spo2:
            spo2.set_value(p['spo2'], p['hr'])
        if temp:
            temp.set_value(p['temp'])

    def load_scenario(self, name: str):
        if name not in self.SCENARIOS:
            return
        self.scenario = name
        self._scenario_step = 0
        self.state['scenario'] = name

        cfg = self.SCENARIOS[name]
        if 'profile' in cfg:
            self._apply_profile(cfg['profile'])
            self.state['profile'] = cfg['profile']

        if name == 'pump_occlusion':
            pump = self.vm.peripherals.get('pump0')
            if pump:
                pump.enabled = True
                pump.target_flow = 50.0

        if name == 'battery_failover':
            bms = self.vm.peripherals.get('bms0')
            if bms:
                self.state['on_battery'] = True

    def tick(self):
        self.tick_count += 1
        for name, dev in self.vm.peripherals.items():
            if hasattr(dev, 'simulate_tick'):
                dev.simulate_tick()

        ecg = self.vm.peripherals.get('ecg0')
        spo2 = self.vm.peripherals.get('spo2_0')
        temp = self.vm.peripherals.get('temp_patient')
        pump = self.vm.peripherals.get('pump0')
        bms = self.vm.peripherals.get('bms0')

        self._apply_scenario_effects()

        if self.state.get('sensor_connected', True):
            if ecg:
                self.state['heart_rate'] = ecg.heart_rate_bpm
                self.state['ecg_waveform'] = list(ecg.waveform[-64:])
            if spo2:
                self.state['spo2'] = round(spo2.spo2_percent, 1)
        else:
            self.state['spo2'] = 0
            self.state['heart_rate'] = 0

        if temp:
            self.state['temperature'] = round(temp.temperature, 1)
        if pump:
            self.state['pump_flow'] = round(pump.flow_rate_ml_min, 1)
        if bms:
            self.state['soc_pct'] = round(bms.soc_percent, 1)

        p = self.PATIENT_PROFILES.get(self._profile, {})
        self.state['bp_sys'] = p.get('bp_sys', 120) + random.randint(-3, 3)
        self.state['bp_dia'] = p.get('bp_dia', 80) + random.randint(-2, 2)
        self.state['resp_rate'] = p.get('rr', 16) + random.randint(-1, 1)

        self._evaluate_alarms()
        self._scenario_step += 1

    def _apply_scenario_effects(self):
        if not self.scenario:
            return
        if self.scenario == 'sensor_disconnect' and self._scenario_step > 30:
            self.state['sensor_connected'] = False
        elif self.scenario == 'pump_occlusion' and self._scenario_step > 50:
            pump = self.vm.peripherals.get('pump0')
            if pump:
                pump.occlusion = True
        elif self.scenario == 'battery_failover':
            bms = self.vm.peripherals.get('bms0')
            if bms:
                bms.current_ma = 500

    def _evaluate_alarms(self):
        alarm = 'NONE'
        priority = 0
        hr = self.state.get('heart_rate', 72)
        spo2 = self.state.get('spo2', 98)
        temp_c = self.state.get('temperature', 37)
        pump = self.vm.peripherals.get('pump0')

        if not self.state.get('sensor_connected', True):
            alarm = 'SENSOR_DISCONNECT'
            priority = 2
        elif pump and pump.occlusion:
            alarm = 'PUMP_OCCLUSION'
            priority = 3
        elif hr > 150 or hr < 40:
            alarm = 'HR_CRITICAL'
            priority = 3
        elif hr > 120 or hr < 50:
            alarm = 'HR_ABNORMAL'
            priority = 2
        elif spo2 < 85:
            alarm = 'SPO2_CRITICAL'
            priority = 3
        elif spo2 < 90:
            alarm = 'LOW_SPO2'
            priority = 2
        elif temp_c > 39.5:
            alarm = 'HIGH_TEMP'
            priority = 2
        elif temp_c > 39:
            alarm = 'TEMP_WARNING'
            priority = 1

        self.state['alarm'] = alarm
        self.state['alarm_priority'] = priority

    def get_state(self) -> dict:
        return dict(self.state)

    def get_peripherals(self) -> dict:
        return dict(self.vm.peripherals)

    def get_status_text(self) -> str:
        hr = self.state.get('heart_rate', 0)
        alarm = self.state.get('alarm', 'NONE')
        return f"{self.DISPLAY_NAME} | HR {hr} | {alarm} | Tick {self.tick_count}"

    def reset(self):
        self.tick_count = 0
        self.state = {}
        self.scenario = ''
        self._profile = 'normal_adult'
