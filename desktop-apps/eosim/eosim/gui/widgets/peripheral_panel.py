# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""Peripheral display panel — dynamically renders domain-specific peripherals."""
from typing import Dict, List, Optional


class PeripheralSubPanel:
    """Base sub-panel for displaying a peripheral's state."""

    def __init__(self, name, device_type):
        self.name = name
        self.device_type = device_type
        self.visible = True
        self.data = {}

    def update(self, device):
        self.data = {'name': self.name, 'type': self.device_type}
        if hasattr(device, 'enabled'):
            self.data['enabled'] = device.enabled
        return self.data


class AutomotivePanel(PeripheralSubPanel):
    def update(self, device):
        super().update(device)
        if self.device_type == 'CANBusController':
            self.data['tx_count'] = getattr(device, 'tx_count', 0)
            self.data['rx_count'] = getattr(device, 'rx_count', 0)
            self.data['error_count'] = getattr(device, 'error_count', 0)
            self.data['bus_off'] = getattr(device, 'bus_off', False)
            self.data['rx_pending'] = len(device.rx_queue) if hasattr(device, 'rx_queue') else 0
        elif self.device_type == 'SteeringActuator':
            self.data['angle_deg'] = getattr(device, 'angle_deg', 0)
            self.data['torque_nm'] = getattr(device, 'torque_nm', 0)
        elif self.device_type == 'ThrottleActuator':
            self.data['position_pct'] = getattr(device, 'position_pct', 0)
        elif self.device_type == 'BrakeActuator':
            self.data['pressure_pct'] = getattr(device, 'pressure_pct', 0)
            self.data['abs_active'] = getattr(device, 'abs_active', False)
        return self.data


class DronePanel(PeripheralSubPanel):
    def update(self, device):
        super().update(device)
        if self.device_type == 'ESCController':
            self.data['armed'] = getattr(device, 'armed', False)
            self.data['throttle'] = list(getattr(device, 'throttle', []))
            self.data['rpm'] = list(getattr(device, 'rpm', []))
        return self.data


class MedicalPanel(PeripheralSubPanel):
    def update(self, device):
        super().update(device)
        if self.device_type == 'ECGSensor':
            self.data['heart_rate_bpm'] = getattr(device, 'heart_rate_bpm', 0)
            self.data['signal_quality'] = getattr(device, 'signal_quality', 0)
            wf = getattr(device, 'waveform', [])
            self.data['waveform'] = list(wf[-64:])
        elif self.device_type == 'PulseOximeter':
            self.data['spo2_percent'] = getattr(device, 'spo2_percent', 0)
            self.data['pulse_rate'] = getattr(device, 'pulse_rate', 0)
        elif self.device_type == 'PumpController':
            self.data['flow_rate'] = getattr(device, 'flow_rate_ml_min', 0)
            self.data['occlusion'] = getattr(device, 'occlusion', False)
        return self.data


class RobotPanel(PeripheralSubPanel):
    def update(self, device):
        super().update(device)
        if self.device_type == 'ServoController':
            self.data['positions'] = list(getattr(device, 'positions', []))
            self.data['targets'] = list(getattr(device, 'targets', []))
        elif self.device_type == 'MotorController':
            self.data['speed_rpm'] = getattr(device, 'speed_rpm', 0)
        elif self.device_type == 'ProximitySensor':
            self.data['distance_cm'] = getattr(device, 'distance_cm', 0)
            self.data['detected'] = getattr(device, 'detected', False)
        return self.data


class AircraftPanel(PeripheralSubPanel):
    def update(self, device):
        super().update(device)
        if self.device_type == 'PressureSensor':
            self.data['altitude_m'] = getattr(device, 'altitude_m', 0)
        elif self.device_type == 'GPSModule':
            self.data['speed_mps'] = getattr(device, 'speed_mps', 0)
            self.data['heading_deg'] = getattr(device, 'heading_deg', 0)
        elif self.device_type == 'ARINC429':
            self.data['tx_count'] = getattr(device, 'tx_count', 0)
            self.data['rx_count'] = getattr(device, 'rx_count', 0)
        return self.data


class IndustrialPanel(PeripheralSubPanel):
    def update(self, device):
        super().update(device)
        if self.device_type == 'ModbusController':
            self.data['slave_addr'] = getattr(device, 'slave_addr', 0)
            self.data['transactions'] = getattr(device, 'transaction_count', 0)
            regs = getattr(device, 'registers', [])
            self.data['registers'] = list(regs[:16])
        elif self.device_type == 'RelayBank':
            self.data['states'] = list(getattr(device, 'states', []))
        return self.data


class AerodynamicsPanel(PeripheralSubPanel):
    def update(self, device):
        super().update(device)
        if self.device_type == 'WindTunnelSensor':
            self.data['airspeed_mps'] = getattr(device, 'airspeed_mps', 0)
            self.data['mach_number'] = getattr(device, 'mach_number', 0)
            self.data['dynamic_pressure_pa'] = getattr(device, 'dynamic_pressure_pa', 0)
        elif self.device_type == 'ForceBalance':
            self.data['lift_n'] = getattr(device, 'lift_n', 0)
            self.data['drag_n'] = getattr(device, 'drag_n', 0)
        elif self.device_type == 'TunnelFanController':
            self.data['fan_speed_rpm'] = getattr(device, 'fan_speed_rpm', 0)
        return self.data


class PhysiologyPanel(PeripheralSubPanel):
    def update(self, device):
        super().update(device)
        if self.device_type == 'HeartModel':
            self.data['heart_rate_bpm'] = getattr(device, 'heart_rate_bpm', 0)
            self.data['cardiac_output_lpm'] = getattr(device, 'cardiac_output_lpm', 0)
        elif self.device_type == 'LungModel':
            self.data['spo2_percent'] = getattr(device, 'spo2_percent', 0)
            self.data['respiratory_rate'] = getattr(device, 'respiratory_rate', 0)
        elif self.device_type == 'BloodPressureSensor':
            self.data['systolic_mmhg'] = getattr(device, 'systolic_mmhg', 0)
            self.data['diastolic_mmhg'] = getattr(device, 'diastolic_mmhg', 0)
        return self.data


class FinancePanel(PeripheralSubPanel):
    def update(self, device):
        super().update(device)
        if self.device_type == 'MarketFeed':
            self.data['price'] = getattr(device, 'price', 0)
            self.data['bid'] = getattr(device, 'bid', 0)
            self.data['ask'] = getattr(device, 'ask', 0)
            self.data['volume'] = getattr(device, 'volume', 0)
        elif self.device_type == 'TradeExecutor':
            self.data['orders_filled'] = getattr(device, 'orders_filled', 0)
            self.data['position_qty'] = getattr(device, 'position_qty', 0)
        elif self.device_type == 'RiskEngine':
            self.data['current_var'] = getattr(device, 'current_var', 0)
            self.data['risk_breach'] = getattr(device, 'risk_breach', False)
        return self.data


class WeatherPanel(PeripheralSubPanel):
    def update(self, device):
        super().update(device)
        if self.device_type == 'WeatherStation':
            self.data['temperature_c'] = getattr(device, 'temperature_c', 0)
            self.data['humidity_pct'] = getattr(device, 'humidity_pct', 0)
            self.data['pressure_hpa'] = getattr(device, 'pressure_hpa', 0)
        elif self.device_type == 'Anemometer':
            self.data['wind_speed_mps'] = getattr(device, 'wind_speed_mps', 0)
            self.data['wind_direction_deg'] = getattr(device, 'wind_direction_deg', 0)
        elif self.device_type == 'RadarSensor':
            self.data['reflectivity_dbz'] = getattr(device, 'reflectivity_dbz', 0)
        return self.data


class GamingPanel(PeripheralSubPanel):
    def update(self, device):
        super().update(device)
        if self.device_type == 'PhysicsEngine':
            self.data['position'] = list(getattr(device, 'position', [0, 0, 0]))
            self.data['collision_count'] = getattr(device, 'collision_count', 0)
        elif self.device_type == 'EntityManager':
            self.data['entity_count'] = getattr(device, 'entity_count', 0)
            self.data['active_entities'] = getattr(device, 'active_entities', 0)
        elif self.device_type == 'GameController':
            self.data['time_scale'] = getattr(device, 'time_scale', 1.0)
            self.data['paused'] = getattr(device, 'paused', False)
        return self.data


DOMAIN_PANEL_MAP = {
    'automotive': AutomotivePanel,
    'robotics_drone': DronePanel,
    'medical': MedicalPanel,
    'robotics_robot': RobotPanel,
    'aerospace': AircraftPanel,
    'industrial': IndustrialPanel,
    'aerodynamics': AerodynamicsPanel,
    'physiology': PhysiologyPanel,
    'finance': FinancePanel,
    'weather': WeatherPanel,
    'gaming': GamingPanel,
}

DEVICE_DOMAIN_MAP = {
    'CANBusController': 'automotive',
    'LINBusController': 'automotive',
    'SteeringActuator': 'automotive',
    'ThrottleActuator': 'automotive',
    'BrakeActuator': 'automotive',
    'ESCController': 'robotics_drone',
    'ECGSensor': 'medical',
    'PulseOximeter': 'medical',
    'PumpController': 'medical',
    'ServoController': 'robotics_robot',
    'ARINC429': 'aerospace',
    'MIL1553Bus': 'aerospace',
    'ModbusController': 'industrial',
    'RelayBank': 'industrial',
    'WindTunnelSensor': 'aerodynamics',
    'AirflowSensor': 'aerodynamics',
    'PitotTube': 'aerodynamics',
    'ForceBalance': 'aerodynamics',
    'AeroActuator': 'aerodynamics',
    'TunnelFanController': 'aerodynamics',
    'HeartModel': 'physiology',
    'LungModel': 'physiology',
    'BloodPressureSensor': 'physiology',
    'VentilatorActuator': 'physiology',
    'InfusionPump': 'physiology',
    'MarketFeed': 'finance',
    'OrderBook': 'finance',
    'TradeExecutor': 'finance',
    'RiskEngine': 'finance',
    'WeatherStation': 'weather',
    'Anemometer': 'weather',
    'RadarSensor': 'weather',
    'PhysicsEngine': 'gaming',
    'TerrainSensor': 'gaming',
    'EntityManager': 'gaming',
    'GameController': 'gaming',
}


class PeripheralPanel:
    """Dynamic peripheral panel that creates sub-panels based on VM peripherals."""

    def __init__(self):
        self.sub_panels = {}
        self.domain = ''

    def configure_for_product(self, vm, domain=''):
        self.sub_panels.clear()
        self.domain = domain
        for name, device in vm.peripherals.items():
            device_type = type(device).__name__
            domain_key = DEVICE_DOMAIN_MAP.get(device_type, '')
            panel_cls = DOMAIN_PANEL_MAP.get(domain_key, PeripheralSubPanel)
            self.sub_panels[name] = panel_cls(name, device_type)

    def update(self, vm):
        results = {}
        for name, panel in self.sub_panels.items():
            device = vm.peripherals.get(name)
            if device:
                results[name] = panel.update(device)
        return results

    def get_visible_panels(self):
        return [name for name, panel in self.sub_panels.items() if panel.visible]

    def get_panel_data(self, name):
        panel = self.sub_panels.get(name)
        return panel.data if panel else {}
