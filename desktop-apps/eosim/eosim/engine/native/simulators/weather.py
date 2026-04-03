# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""Weather simulator — atmospheric pressure, temperature, precipitation."""
import math
import random


class WeatherSimulator:
    PRODUCT_TYPE = 'weather'
    DISPLAY_NAME = 'Weather System'

    SCENARIOS = {
        'clear_sky': {
            'pressure_hpa': 1023, 'temp_c': 25, 'humidity': 30,
            'description': 'Clear sky high-pressure system',
        },
        'thunderstorm': {
            'pressure_hpa': 1005, 'temp_c': 30, 'humidity': 90,
            'description': 'Convective thunderstorm with heavy rain',
        },
        'cold_front': {
            'pressure_drop_rate': 0.5, 'temp_drop_rate': 0.1,
            'description': 'Approaching cold front passage',
        },
        'hurricane': {
            'pressure_hpa': 950, 'wind_speed_mps': 55, 'temp_c': 28,
            'description': 'Category 3 hurricane simulation',
        },
        'fog_formation': {
            'temp_c': 10, 'humidity': 98, 'wind_speed_mps': 1,
            'description': 'Radiation fog formation at dawn',
        },
    }

    def __init__(self, vm):
        self.vm = vm
        self.tick_count = 0
        self.state = {}
        self.scenario = ''
        self._scenario_step = 0

    def setup(self):
        from eosim.engine.native.peripherals.sensors_weather import (
            WeatherStation, Anemometer, RadarSensor)
        from eosim.engine.native.peripherals.actuators_weather import WeatherActuator
        self.vm.add_peripheral('station', WeatherStation('station', 0x40140000))
        self.vm.add_peripheral('anemometer', Anemometer('anemometer', 0x40140100))
        self.vm.add_peripheral('radar', RadarSensor('radar', 0x40140200))
        self.vm.add_peripheral('wx_actuator', WeatherActuator('wx_actuator', 0x40240000))
        self.state = {
            'temperature_c': 20.0, 'humidity_pct': 55.0,
            'pressure_hpa': 1013.25, 'wind_speed_mps': 5.0,
            'wind_direction_deg': 180.0, 'precipitation_mm_hr': 0.0,
            'visibility_km': 10.0, 'cloud_cover_pct': 30.0,
            'dew_point_c': 10.0, 'reflectivity_dbz': 0.0,
            'scenario': '',
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
        station = self.vm.peripherals.get('station')
        anemometer = self.vm.peripherals.get('anemometer')
        radar = self.vm.peripherals.get('radar')
        if station:
            self.state['temperature_c'] = round(station.temperature_c, 1)
            self.state['humidity_pct'] = round(station.humidity_pct, 1)
            self.state['pressure_hpa'] = round(station.pressure_hpa, 2)
            self.state['precipitation_mm_hr'] = round(station.precipitation_mm_hr, 2)
            self.state['visibility_km'] = round(station.visibility_km, 1)
            self.state['cloud_cover_pct'] = round(station.cloud_cover_pct, 1)
        if anemometer:
            self.state['wind_speed_mps'] = round(anemometer.wind_speed_mps, 1)
            self.state['wind_direction_deg'] = round(anemometer.wind_direction_deg, 0)
        if radar:
            self.state['reflectivity_dbz'] = round(radar.reflectivity_dbz, 1)
        t = self.state['temperature_c']
        rh = self.state['humidity_pct']
        if rh > 0:
            a, b = 17.27, 237.7
            alpha = (a * t / (b + t)) + math.log(rh / 100.0)
            self.state['dew_point_c'] = round((b * alpha) / (a - alpha), 1) if a != alpha else t
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
