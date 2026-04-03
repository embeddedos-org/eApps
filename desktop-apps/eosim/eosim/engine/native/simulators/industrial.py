# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""Industrial PLC simulator. Pure Python, cross-platform."""
import random


class IndustrialSimulator:
    PRODUCT_TYPE = 'industrial'
    DISPLAY_NAME = 'Industrial PLC'
    SCENARIOS = {
        'conveyor_sorting': {'speed_rpm': 500, 'description': 'Conveyor sorting'},
        'batch_mixing': {'temp_target': 65, 'description': 'Temp-controlled mixing'},
        'cnc_positioning': {'description': 'CNC positioning'},
        'emergency_stop': {'description': 'E-stop shutdown'},
        'redundancy_failover': {'description': 'Backup takeover'},
    }

    def __init__(self, vm):
        self.vm = vm; self.tick_count = 0; self.state = {}
        self.scenario = ''; self._scenario_step = 0

    def setup(self):
        from eosim.engine.native.peripherals.sensors import TemperatureSensor, ProximitySensor, ADCChannel
        from eosim.engine.native.peripherals.actuators import MotorController, ValveController, RelayBank
        from eosim.engine.native.peripherals.buses import ModbusController
        from eosim.engine.native.peripherals.composites import WatchdogTimer
        self.vm.add_peripheral('modbus0', ModbusController('modbus0', 0x40300200))
        self.vm.add_peripheral('motor0', MotorController('motor0', 0x40200000))
        self.vm.add_peripheral('valve0', ValveController('valve0', 0x40200300))
        self.vm.add_peripheral('relay0', RelayBank('relay0', 0x40200500))
        self.vm.add_peripheral('temp0', TemperatureSensor('temp0', 0x40100000, 0, 200))
        self.vm.add_peripheral('prox0', ProximitySensor('prox0', 0x40100400))
        self.vm.add_peripheral('adc0', ADCChannel('adc0', 0x40100600))
        self.vm.add_peripheral('wdt0', WatchdogTimer('wdt0', 0x40500200))
        self.state = {'conveyor_speed': 0, 'process_temp': 22, 'product_count': 0,
                      'e_stop': False, 'mode': 'IDLE', 'scenario': '', 'batch_complete': False}

    def load_scenario(self, name):
        if name not in self.SCENARIOS: return
        self.scenario = name; self._scenario_step = 0; self.state['scenario'] = name
        motor = self.vm.peripherals.get('motor0')
        if name == 'conveyor_sorting':
            if motor: motor.enabled = True; motor.target_speed = 500
            self.state['mode'] = 'RUNNING'
        elif name == 'batch_mixing': self.state['mode'] = 'RUNNING'
        elif name == 'cnc_positioning':
            if motor: motor.enabled = True
            self.state['mode'] = 'RUNNING'
        elif name == 'emergency_stop':
            self.state['e_stop'] = True; self.state['mode'] = 'E_STOP'
            if motor: motor.enabled = False; motor.target_speed = 0
        elif name == 'redundancy_failover': self.state['mode'] = 'FAILOVER'

    def tick(self):
        self.tick_count += 1
        for n, d in self.vm.peripherals.items():
            if hasattr(d, 'simulate_tick'): d.simulate_tick()
        motor = self.vm.peripherals.get('motor0')
        temp = self.vm.peripherals.get('temp0')
        prox = self.vm.peripherals.get('prox0')
        modbus = self.vm.peripherals.get('modbus0')
        valve = self.vm.peripherals.get('valve0')
        if self.scenario == 'batch_mixing' and temp:
            target = self.SCENARIOS['batch_mixing']['temp_target']
            err = target - temp.temperature
            if valve: valve.positions[0] = max(0, min(100, err * 5))
            temp.temperature += err * 0.02
            if abs(err) < 1 and self._scenario_step > 100: self.state['batch_complete'] = True
        elif self.scenario == 'cnc_positioning' and motor:
            step = self._scenario_step % 100
            motor.target_speed = 200 if step < 25 else (-200 if 50 <= step < 75 else 0)
        elif self.scenario == 'emergency_stop' and motor:
            motor.enabled = False; motor.target_speed = 0
        elif self.scenario == 'redundancy_failover' and self._scenario_step > 20:
            self.state['mode'] = 'RUNNING'
            if motor: motor.enabled = True
        if motor: self.state['conveyor_speed'] = motor.speed_rpm
        if temp: self.state['process_temp'] = round(temp.temperature, 1)
        if prox and prox.detected: self.state['product_count'] += 1
        if modbus:
            modbus.registers[0] = int(self.state['conveyor_speed'])
            modbus.registers[1] = int(self.state['process_temp'] * 10)
        if self.state['e_stop']: self.state['mode'] = 'E_STOP'
        elif motor and motor.enabled: self.state['mode'] = 'RUNNING'
        elif self.state['mode'] != 'FAILOVER': self.state['mode'] = 'IDLE'
        self._scenario_step += 1

    def get_state(self): return dict(self.state)
    def get_peripherals(self): return dict(self.vm.peripherals)
    def get_status_text(self): return f"{self.DISPLAY_NAME} | {self.state.get('mode','IDLE')} | Tick {self.tick_count}"
    def reset(self): self.tick_count = 0; self.state = {}; self.scenario = ''
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""Industrial PLC simulator — conveyor, process control, e-stop.

Pure Python, cross-platform. No OS-specific dependencies.
"""
import random


class IndustrialSimulator:
    PRODUCT_TYPE = 'industrial'
    DISPLAY_NAME = 'Industrial PLC'

    SCENARIOS = {
        'conveyor_sorting': {'speed_rpm': 500, 'description': 'Conveyor belt sorting by sensor'},
        'batch_mixing': {'temp_target': 65, 'description': 'Temperature-controlled batch mixing'},
        'cnc_positioning': {'description': 'CNC stepper motor positioning'},
        'emergency_stop': {'description': 'E-stop activated, safe shutdown'},
        'redundancy_failover': {'description': 'Primary controller fails, backup takes over'},
    }

    def __init__(self, vm):
        self.vm = vm
        self.tick_count = 0
        self.state = {}
        self.scenario = ''
        self._scenario_step = 0

    def setup(self):
        from eosim.engine.native.peripherals.sensors import TemperatureSensor, ProximitySensor, ADCChannel
        from eosim.engine.native.peripherals.actuators import MotorController, ValveController, RelayBank
        from eosim.engine.native.peripherals.buses import ModbusController
        from eosim.engine.native.peripherals.composites import WatchdogTimer

        self.vm.add_peripheral('modbus0', ModbusController('modbus0', 0x40300200))
        self.vm.add_peripheral('motor0', MotorController('motor0', 0x40200000))
        self.vm.add_peripheral('valve0', ValveController('valve0', 0x40200300))
        self.vm.add_peripheral('relay0', RelayBank('relay0', 0x40200500))
        self.vm.add_peripheral('temp0', TemperatureSensor('temp0', 0x40100000, 0, 200))
        self.vm.add_peripheral('prox0', ProximitySensor('prox0', 0x40100400))
        self.vm.add_peripheral('adc0', ADCChannel('adc0', 0x40100600))
        self.vm.add_peripheral('wdt0', WatchdogTimer('wdt0', 0x40500200))

        self.state = {
            'conveyor_speed': 0, 'process_temp': 22, 'product_count': 0,
            'e_stop': False, 'relay_states': [False] * 8, 'mode': 'IDLE',
            'scenario': '', 'pid_output': 0, 'batch_complete': False,
        }

    def load_scenario(self, name: str):
        if name not in self.SCENARIOS:
            return
        self.scenario = name
        self._scenario_step = 0
        self.state['scenario'] = name

        motor = self.vm.peripherals.get('motor0')
        if name == 'conveyor_sorting':
            if motor:
                motor.enabled = True
                motor.target_speed = self.SCENARIOS[name]['speed_rpm']
            self.state['mode'] = 'RUNNING'
        elif name == 'batch_mixing':
            self.state['mode'] = 'RUNNING'
        elif name == 'cnc_positioning':
            if motor:
                motor.enabled = True
            self.state['mode'] = 'RUNNING'
        elif name == 'emergency_stop':
            self.state['e_stop'] = True
            self.state['mode'] = 'E_STOP'
            if motor:
                motor.enabled = False
                motor.target_speed = 0
        elif name == 'redundancy_failover':
            self.state['mode'] = 'FAILOVER'

    def tick(self):
        self.tick_count += 1
        for name, dev in self.vm.peripherals.items():
            if hasattr(dev, 'simulate_tick'):
                dev.simulate_tick()

        motor = self.vm.peripherals.get('motor0')
        temp = self.vm.peripherals.get('temp0')
        prox = self.vm.peripherals.get('prox0')
        relay = self.vm.peripherals.get('relay0')
        modbus = self.vm.peripherals.get('modbus0')
        valve = self.vm.peripherals.get('valve0')

        self._apply_scenario(motor, temp, prox, valve)

        if motor:
            self.state['conveyor_speed'] = motor.speed_rpm
        if temp:
            self.state['process_temp'] = round(temp.temperature, 1)
        if prox and prox.detected:
            self.state['product_count'] += 1
        if relay:
            self.state['relay_states'] = list(relay.states)
        if modbus:
            modbus.registers[0] = int(self.state['conveyor_speed'])
            modbus.registers[1] = int(self.state['process_temp'] * 10)
            modbus.registers[2] = self.state['product_count']

        if self.state['e_stop']:
            self.state['mode'] = 'E_STOP'
        elif motor and motor.enabled:
            self.state['mode'] = 'RUNNING'
        elif self.state['mode'] != 'FAILOVER':
            self.state['mode'] = 'IDLE'

        self._scenario_step += 1

    def _apply_scenario(self, motor, temp, prox, valve):
        if not self.scenario:
            return

        if self.scenario == 'conveyor_sorting':
            if prox and prox.detected:
                relay = self.vm.peripherals.get('relay0')
                if relay:
                    relay.states[0] = True

        elif self.scenario == 'batch_mixing':
            target = self.SCENARIOS['batch_mixing']['temp_target']
            if temp:
                error = target - temp.temperature
                self.state['pid_output'] = max(0, min(100, error * 5))
                if valve:
                    valve.positions[0] = self.state['pid_output']
                if error < 0.5:
                    temp.temperature += 0.1
                else:
                    temp.temperature += error * 0.02
                if abs(error) < 1 and self._scenario_step > 100:
                    self.state['batch_complete'] = True

        elif self.scenario == 'cnc_positioning':
            if motor:
                step = self._scenario_step % 100
                if step < 25:
                    motor.target_speed = 200
                elif step < 50:
                    motor.target_speed = 0
                elif step < 75:
                    motor.target_speed = -200
                else:
                    motor.target_speed = 0

        elif self.scenario == 'emergency_stop':
            if motor:
                motor.enabled = False
                motor.target_speed = 0

        elif self.scenario == 'redundancy_failover':
            if self._scenario_step > 20:
                self.state['mode'] = 'RUNNING'
                if motor:
                    motor.enabled = True

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
