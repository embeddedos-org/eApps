# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""Product simulator framework — BaseSimulator, individual simulators, and SimulatorFactory.

All simulators are pure Python, cross-platform (Linux/Windows/macOS).
No OS-specific dependencies. No tkinter, no C extensions.
"""
from eosim.engine.native.simulators.vehicle import VehicleSimulator
from eosim.engine.native.simulators.drone import DroneSimulator
from eosim.engine.native.simulators.robot import RobotSimulator
from eosim.engine.native.simulators.aircraft import AircraftSimulator
from eosim.engine.native.simulators.medical import MedicalSimulator
from eosim.engine.native.simulators.industrial import IndustrialSimulator
from eosim.engine.native.simulators.iot import IoTSimulator
from eosim.engine.native.simulators.satellite import SatelliteSimulator
from eosim.engine.native.simulators.energy import EnergySimulator
from eosim.engine.native.simulators.wearable import WearableSimulator
from eosim.engine.native.simulators.media import MediaDeviceSimulator
from eosim.engine.native.simulators.speaker import SmartSpeakerSimulator
from eosim.engine.native.simulators.camera import HomeCameraSimulator
from eosim.engine.native.simulators.aerodynamics import AerodynamicsSimulator
from eosim.engine.native.simulators.physiology import PhysiologySimulator
from eosim.engine.native.simulators.finance import FinanceSimulator
from eosim.engine.native.simulators.weather import WeatherSimulator
from eosim.engine.native.simulators.gaming import GamingSimulator


class BaseSimulator:
    """Base class for all product simulators (fallback for unmapped types)."""

    PRODUCT_TYPE = 'generic'
    DISPLAY_NAME = 'Generic Simulator'

    def __init__(self, vm):
        self.vm = vm
        self.tick_count = 0
        self.state = {}

    def setup(self):
        pass

    def tick(self):
        self.tick_count += 1
        for name, dev in self.vm.peripherals.items():
            if hasattr(dev, 'simulate_tick'):
                dev.simulate_tick()

    def get_state(self) -> dict:
        return dict(self.state)

    def get_peripherals(self) -> dict:
        return dict(self.vm.peripherals)

    def get_status_text(self) -> str:
        return f"{self.DISPLAY_NAME} | Tick {self.tick_count}"

    def reset(self):
        self.tick_count = 0
        self.state = {}


SIMULATOR_MAP = {
    'vehicle': VehicleSimulator,
    'automotive_ecu': VehicleSimulator,
    'ev_powertrain': VehicleSimulator,
    'adas_controller': VehicleSimulator,
    'electric_scooter': VehicleSimulator,
    'drone': DroneSimulator,
    'drone_controller': DroneSimulator,
    'ag_drone': DroneSimulator,
    'robot': RobotSimulator,
    'robot_controller': RobotSimulator,
    'surgical_robot': RobotSimulator,
    'aircraft': AircraftSimulator,
    'fixed_wing': AircraftSimulator,
    'cubesat': SatelliteSimulator,
    'satellite': SatelliteSimulator,
    'medical': MedicalSimulator,
    'medical_monitor': MedicalSimulator,
    'industrial': IndustrialSimulator,
    'industrial_plc': IndustrialSimulator,
    'iot': IoTSimulator,
    'iot_sensor': IoTSimulator,
    'smart_home_hub': IoTSimulator,
    'smart_meter': EnergySimulator,
    'wearable': WearableSimulator,
    'wearable_device': WearableSimulator,
    'energy': EnergySimulator,
    'solar_inverter': EnergySimulator,
    'tactical_radio': BaseSimulator,
    'submarine': BaseSimulator,
    'base_station_5g': BaseSimulator,
    'iptv_stb': MediaDeviceSimulator,
    'cast_device': MediaDeviceSimulator,
    'tv_os': MediaDeviceSimulator,
    'media_device': MediaDeviceSimulator,
    'aerodynamics': AerodynamicsSimulator,
    'wind_tunnel': AerodynamicsSimulator,
    'cfd_lab': AerodynamicsSimulator,
    'physiology': PhysiologySimulator,
    'patient_model': PhysiologySimulator,
    'finance': FinanceSimulator,
    'stock_market': FinanceSimulator,
    'trading_sim': FinanceSimulator,
    'weather': WeatherSimulator,
    'weather_station_sim': WeatherSimulator,
    'atmosphere': WeatherSimulator,
    'gaming': GamingSimulator,
    'game_world': GamingSimulator,
    'physics_sandbox': GamingSimulator,
    'smart_speaker': SmartSpeakerSimulator,
    'google_mini': SmartSpeakerSimulator,
    'home_camera': HomeCameraSimulator,
    'spy_camera': HomeCameraSimulator,
    'vbox_test': BaseSimulator,
}


class SimulatorFactory:
    """Factory to create the right simulator from a product template name."""

    @staticmethod
    def create(product_type: str, vm) -> 'BaseSimulator':
        cls = SIMULATOR_MAP.get(product_type, BaseSimulator)
        sim = cls(vm)
        sim.setup()
        return sim

    @staticmethod
    def list_simulators():
        return sorted(set(cls.PRODUCT_TYPE for cls in SIMULATOR_MAP.values()))
