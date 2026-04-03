# SPDX-License-Identifier: MIT
"""Tests for EoSim GUI components — expanded for multi-product simulator."""
import pytest


class TestProductTemplates:
    """Verify all 31 product templates exist and have valid fields."""

    def test_catalog_has_31_templates(self):
        from eosim.gui.product_templates import PRODUCT_CATALOG
        assert len(PRODUCT_CATALOG) == 31

    def test_all_template_names(self):
        from eosim.gui.product_templates import PRODUCT_CATALOG
        expected = {
            "iot_sensor", "smart_home_hub", "automotive_ecu",
            "ev_powertrain", "adas_controller",
            "medical_monitor", "drone_controller", "industrial_plc",
            "wearable_device", "robot_controller",
            "fixed_wing", "cubesat", "solar_inverter",
            "base_station_5g", "tactical_radio", "smart_meter",
            "surgical_robot", "submarine", "ag_drone", "electric_scooter",
            "cast_device", "game_world", "home_camera", "iptv_stb",
            "patient_model", "smart_speaker", "stock_market", "tv_os",
            "vbox_test", "weather_station_sim", "wind_tunnel",
        }
        assert set(PRODUCT_CATALOG.keys()) == expected

    def test_templates_have_required_fields(self):
        from eosim.gui.product_templates import PRODUCT_CATALOG
        required = [
            "name", "display_name", "icon", "arch", "ram_mb",
            "peripherals", "domain", "modeling", "description",
            "default_platform",
        ]
        for key, tpl in PRODUCT_CATALOG.items():
            for field in required:
                assert hasattr(tpl, field), f"Template '{key}' missing '{field}'"
                val = getattr(tpl, field)
                if field == "ram_mb":
                    assert val > 0, f"{key}.ram_mb must be > 0"
                elif field == "peripherals":
                    assert isinstance(val, list)
                    assert len(val) > 0, f"{key} must have peripherals"
                else:
                    assert val, f"Template '{key}' field '{field}' is empty"

    def test_simulator_class_field(self):
        from eosim.gui.product_templates import PRODUCT_CATALOG
        for key, tpl in PRODUCT_CATALOG.items():
            assert hasattr(tpl, 'simulator_class'), f"{key} missing simulator_class"
            assert tpl.simulator_class, f"{key} simulator_class is empty"

    def test_valid_arch(self):
        from eosim.gui.product_templates import PRODUCT_CATALOG
        from eosim.core.schema import VALID_ARCHES
        for key, tpl in PRODUCT_CATALOG.items():
            assert tpl.arch in VALID_ARCHES, f"{key} invalid arch: {tpl.arch}"

    def test_valid_domain(self):
        from eosim.gui.product_templates import PRODUCT_CATALOG
        from eosim.core.schema import VALID_DOMAINS
        for key, tpl in PRODUCT_CATALOG.items():
            assert tpl.domain in VALID_DOMAINS, f"{key} invalid domain: {tpl.domain}"

    def test_valid_modeling(self):
        from eosim.gui.product_templates import PRODUCT_CATALOG
        from eosim.core.schema import VALID_MODELING
        for key, tpl in PRODUCT_CATALOG.items():
            assert tpl.modeling in VALID_MODELING, f"{key} invalid modeling"

    def test_valid_peripherals(self):
        from eosim.gui.product_templates import PRODUCT_CATALOG
        from eosim.gui.widgets.build_panel import ALL_PERIPHERALS
        for key, tpl in PRODUCT_CATALOG.items():
            for p in tpl.peripherals:
                assert p in ALL_PERIPHERALS, f"{key} invalid peripheral: {p}"

    def test_get_template(self):
        from eosim.gui.product_templates import get_template
        tpl = get_template("iot_sensor")
        assert tpl is not None
        assert tpl.name == "iot_sensor"
        assert get_template("nonexistent") is None

    def test_list_templates(self):
        from eosim.gui.product_templates import list_templates
        names = list_templates()
        assert len(names) == 31
        assert names == sorted(names)


class TestBuildPanel:
    """Verify build config generation from product templates."""

    def test_iot_sensor_defaults(self):
        from eosim.gui.product_templates import PRODUCT_CATALOG
        tpl = PRODUCT_CATALOG["iot_sensor"]
        assert tpl.arch == "arm"
        assert tpl.ram_mb == 64
        assert "uart" in tpl.peripherals
        assert "gpio" in tpl.peripherals
        assert "i2c" in tpl.peripherals
        assert tpl.domain == "iot"

    def test_all_templates_have_valid_config(self):
        from eosim.gui.product_templates import PRODUCT_CATALOG
        for key, tpl in PRODUCT_CATALOG.items():
            assert isinstance(tpl.arch, str) and tpl.arch
            assert isinstance(tpl.ram_mb, int) and tpl.ram_mb > 0
            assert isinstance(tpl.peripherals, list) and len(tpl.peripherals) > 0

    def test_robot_controller_is_arm64(self):
        from eosim.gui.product_templates import PRODUCT_CATALOG
        tpl = PRODUCT_CATALOG["robot_controller"]
        assert tpl.arch == "arm64"
        assert tpl.ram_mb == 512

    def test_wearable_is_smallest_ram(self):
        from eosim.gui.product_templates import PRODUCT_CATALOG
        tpl = PRODUCT_CATALOG["wearable_device"]
        assert tpl.ram_mb == 32
        all_rams = [t.ram_mb for t in PRODUCT_CATALOG.values()]
        assert tpl.ram_mb == min(all_rams)

    def test_build_panel_select_product(self):
        from eosim.gui.widgets.build_panel import BuildPanel
        bp = BuildPanel()
        assert bp.select_product("automotive_ecu")
        config = bp.get_build_config()
        assert config['product'] == 'automotive_ecu'
        assert 'can' in config['peripherals']
        assert config['arch'] == 'arm'

    def test_build_panel_toggle_peripheral(self):
        from eosim.gui.widgets.build_panel import BuildPanel
        bp = BuildPanel()
        bp.select_product("iot_sensor")
        assert bp.toggle_peripheral("wifi") is True
        config = bp.get_build_config()
        assert 'wifi' in config['peripherals']
        assert bp.toggle_peripheral("wifi") is False
        config = bp.get_build_config()
        assert 'wifi' not in config['peripherals']

    def test_build_panel_peripheral_groups(self):
        from eosim.gui.widgets.build_panel import BuildPanel
        bp = BuildPanel()
        bp.select_product("drone_controller")
        groups = bp.get_peripheral_groups()
        assert 'Core' in groups
        assert 'Sensors' in groups
        assert 'Actuators' in groups
        assert 'Buses' in groups
        assert 'Wireless' in groups
        assert 'Composite' in groups

    def test_build_panel_list_products(self):
        from eosim.gui.widgets.build_panel import BuildPanel
        bp = BuildPanel()
        products = bp.list_products()
        assert len(products) == 31
        names = [p['name'] for p in products]
        assert names == sorted(names)


class TestSensors:
    """Verify sensor simulate_tick(), register reads, and value injection."""

    def test_temperature_sensor_tick(self):
        from eosim.engine.native.peripherals.sensors import TemperatureSensor
        s = TemperatureSensor('t', 0x1000)
        initial = s.temperature
        for _ in range(100):
            s.simulate_tick()
        assert s._tick_count == 100
        assert s.read_reg(0x00) == int(s.temperature * 100) & 0xFFFFFFFF

    def test_temperature_sensor_set_value(self):
        from eosim.engine.native.peripherals.sensors import TemperatureSensor
        s = TemperatureSensor('t', 0x1000)
        s.set_value(42.5, 80.0)
        assert s.temperature == 42.5
        assert s.humidity == 80.0

    def test_imu_sensor_axes(self):
        from eosim.engine.native.peripherals.sensors import IMUSensor
        imu = IMUSensor('imu', 0x2000, 9)
        imu.set_accel(1.0, 2.0, 9.81)
        assert imu.accel == [1.0, 2.0, 9.81]
        assert imu.read_reg(0x00) == 1000
        assert imu.read_reg(0x04) == 2000

    def test_gps_module_position(self):
        from eosim.engine.native.peripherals.sensors import GPSModule
        gps = GPSModule('gps', 0x3000)
        gps.set_position(40.7128, -74.0060, 10)
        assert gps.latitude == 40.7128
        assert gps.longitude == -74.0060

    def test_proximity_sensor(self):
        from eosim.engine.native.peripherals.sensors import ProximitySensor
        p = ProximitySensor('prox', 0x4000, max_range_cm=400)
        p.set_value(50.0)
        assert p.distance_cm == 50.0
        assert p.detected is True

    def test_ecg_sensor_waveform(self):
        from eosim.engine.native.peripherals.sensors import ECGSensor
        ecg = ECGSensor('ecg', 0x5000)
        ecg.set_heart_rate(100)
        assert ecg.heart_rate_bpm == 100
        for _ in range(50):
            ecg.simulate_tick()
        assert len(ecg.waveform) == 256
        assert ecg.read_reg(0x00) == 100

    def test_pulse_oximeter(self):
        from eosim.engine.native.peripherals.sensors import PulseOximeter
        spo2 = PulseOximeter('spo2', 0x6000)
        spo2.set_value(95.0, 80)
        assert spo2.spo2_percent == 95.0
        assert spo2.pulse_rate == 80

    def test_adc_channel(self):
        from eosim.engine.native.peripherals.sensors import ADCChannel
        adc = ADCChannel('adc', 0x7000, channels=4, resolution=12)
        adc.set_channel(0, 2048)
        assert adc.values[0] == 2048
        assert adc.read_reg(0x00) == 2048

    def test_pressure_sensor_altitude(self):
        from eosim.engine.native.peripherals.sensors import PressureSensor
        baro = PressureSensor('baro', 0x8000)
        baro.set_altitude(1000)
        assert abs(baro.altitude_m - 1000) < 1

    def test_sensor_io_handler(self):
        from eosim.engine.native.peripherals.sensors import TemperatureSensor
        s = TemperatureSensor('t', 0x1000)
        s.set_value(25.0)
        val = s.io_handler('read', 0x1000, 0)
        assert val == int(25.0 * 100)


class TestActuators:
    """Verify motor/servo/ESC command response and state."""

    def test_motor_controller_enable(self):
        from eosim.engine.native.peripherals.actuators import MotorController
        m = MotorController('m', 0x1000)
        m.enabled = True
        m.target_speed = 1000
        for _ in range(50):
            m.simulate_tick()
        assert m.speed_rpm > 0

    def test_servo_controller_target(self):
        from eosim.engine.native.peripherals.actuators import ServoController
        s = ServoController('s', 0x2000, channels=4)
        s.set_target(0, 45.0)
        assert s.targets[0] == 45.0
        for _ in range(100):
            s.simulate_tick()
        assert abs(s.positions[0] - 45.0) < 5.0

    def test_esc_controller_armed(self):
        from eosim.engine.native.peripherals.actuators import ESCController
        esc = ESCController('esc', 0x3000, channels=4)
        esc.armed = True
        esc.enabled = True
        esc.throttle = [50.0, 50.0, 50.0, 50.0]
        for _ in range(50):
            esc.simulate_tick()
        for rpm in esc.rpm:
            assert rpm > 0

    def test_brake_actuator(self):
        from eosim.engine.native.peripherals.actuators import BrakeActuator
        b = BrakeActuator('b', 0x4000)
        b.target_pct = 80.0
        for _ in range(20):
            b.simulate_tick()
        assert b.pressure_pct > 50.0

    def test_steering_actuator(self):
        from eosim.engine.native.peripherals.actuators import SteeringActuator
        s = SteeringActuator('s', 0x5000)
        s.target_angle = 30.0
        for _ in range(20):
            s.simulate_tick()
        assert abs(s.angle_deg - 30.0) < 2.0

    def test_relay_bank_toggle(self):
        from eosim.engine.native.peripherals.actuators import RelayBank
        r = RelayBank('r', 0x6000, channels=4)
        r.write_reg(0x00, 0b0101)
        assert r.states[0] is True
        assert r.states[1] is False
        assert r.states[2] is True

    def test_pump_controller(self):
        from eosim.engine.native.peripherals.actuators import PumpController
        p = PumpController('p', 0x7000)
        p.enabled = True
        p.target_flow = 100.0
        for _ in range(50):
            p.simulate_tick()
        assert p.flow_rate_ml_min > 50.0

    def test_display_driver(self):
        from eosim.engine.native.peripherals.actuators import DisplayDriver
        d = DisplayDriver('d', 0x8000, 128, 64)
        assert d.width == 128
        assert d.height == 64
        assert len(d.framebuffer) == 128 * 64 // 8


class TestBuses:
    """Verify CAN message send/receive, Modbus register read/write."""

    def test_can_send_receive(self):
        from eosim.engine.native.peripherals.buses import CANBusController
        can = CANBusController('can', 0x1000)
        can.loopback = True
        can.send_message(0x100, b'\x01\x02\x03')
        assert can.tx_count == 1
        msg = can.receive_message()
        assert msg is not None
        assert msg['id'] == 0x100
        assert msg['data'] == b'\x01\x02\x03'

    def test_can_inject_message(self):
        from eosim.engine.native.peripherals.buses import CANBusController
        can = CANBusController('can', 0x1000)
        can.inject_message(0x200, b'\xAA\xBB')
        assert can.rx_count == 1
        msg = can.receive_message()
        assert msg['id'] == 0x200

    def test_can_filter(self):
        from eosim.engine.native.peripherals.buses import CANBusController
        can = CANBusController('can', 0x1000)
        can.filters = [0x100]
        can.inject_message(0x100, b'\x01')
        can.inject_message(0x200, b'\x02')
        assert can.rx_count == 1

    def test_modbus_registers(self):
        from eosim.engine.native.peripherals.buses import ModbusController
        mb = ModbusController('mb', 0x2000)
        mb.write_holding(0, [100, 200, 300])
        assert mb.read_holding(0, 3) == [100, 200, 300]
        assert mb.transaction_count == 1

    def test_modbus_coils(self):
        from eosim.engine.native.peripherals.buses import ModbusController
        mb = ModbusController('mb', 0x2000)
        mb.write_coil(0, True)
        assert mb.read_coil(0) is True
        assert mb.read_coil(1) is False

    def test_arinc429_word(self):
        from eosim.engine.native.peripherals.buses import ARINC429
        a = ARINC429('a', 0x3000)
        a.send_word(0o310, 0, 0x1234, 0)
        assert a.tx_count == 1

    def test_ethernet_mac(self):
        from eosim.engine.native.peripherals.buses import EthernetMAC
        eth = EthernetMAC('eth', 0x4000)
        eth.send_packet(b'\xFF' * 64)
        assert eth.tx_packets == 1
        assert eth.tx_bytes == 64


class TestSimulators:
    """Verify each simulator creates correct peripherals and produces valid state."""

    def _create_vm(self):
        from eosim.engine.native import VirtualMachine
        return VirtualMachine(name="test", arch="arm", ram_mb=32)

    def test_vehicle_simulator(self):
        from eosim.engine.native.simulators import VehicleSimulator
        vm = self._create_vm()
        sim = VehicleSimulator(vm)
        sim.setup()
        assert 'can0' in vm.peripherals
        assert 'imu0' in vm.peripherals
        assert 'steering' in vm.peripherals
        sim.tick()
        state = sim.get_state()
        assert 'speed_kmh' in state
        assert 'soc_pct' in state

    def test_drone_simulator(self):
        from eosim.engine.native.simulators import DroneSimulator
        vm = self._create_vm()
        sim = DroneSimulator(vm)
        sim.setup()
        assert 'esc0' in vm.peripherals
        assert 'baro0' in vm.peripherals
        sim.tick()
        state = sim.get_state()
        assert 'altitude_m' in state
        assert 'flight_mode' in state
        assert state['flight_mode'] == 'DISARMED'

    def test_robot_simulator(self):
        from eosim.engine.native.simulators import RobotSimulator
        vm = self._create_vm()
        sim = RobotSimulator(vm)
        sim.setup()
        assert 'servo0' in vm.peripherals
        assert 'prox0' in vm.peripherals
        sim.tick()
        state = sim.get_state()
        assert 'joint_angles' in state
        assert len(state['joint_angles']) == 6

    def test_aircraft_simulator(self):
        from eosim.engine.native.simulators import AircraftSimulator
        vm = self._create_vm()
        sim = AircraftSimulator(vm)
        sim.setup()
        assert 'arinc0' in vm.peripherals
        sim.tick()
        state = sim.get_state()
        assert 'altitude_ft' in state
        assert 'airspeed_kts' in state

    def test_medical_simulator(self):
        from eosim.engine.native.simulators import MedicalSimulator
        vm = self._create_vm()
        sim = MedicalSimulator(vm)
        sim.setup()
        assert 'ecg0' in vm.peripherals
        assert 'spo2_0' in vm.peripherals
        sim.tick()
        state = sim.get_state()
        assert 'heart_rate' in state
        assert 'spo2' in state
        assert state['heart_rate'] == 72

    def test_industrial_simulator(self):
        from eosim.engine.native.simulators import IndustrialSimulator
        vm = self._create_vm()
        sim = IndustrialSimulator(vm)
        sim.setup()
        assert 'modbus0' in vm.peripherals
        assert 'relay0' in vm.peripherals
        sim.tick()
        state = sim.get_state()
        assert 'conveyor_speed' in state

    def test_iot_simulator(self):
        from eosim.engine.native.simulators import IoTSimulator
        vm = self._create_vm()
        sim = IoTSimulator(vm)
        sim.setup()
        assert 'wifi0' in vm.peripherals
        assert 'temp0' in vm.peripherals
        sim.tick()
        state = sim.get_state()
        assert 'temperature' in state

    def test_wearable_simulator(self):
        from eosim.engine.native.simulators import WearableSimulator
        vm = self._create_vm()
        sim = WearableSimulator(vm)
        sim.setup()
        assert 'display0' in vm.peripherals
        assert 'haptic0' in vm.peripherals
        sim.tick()
        state = sim.get_state()
        assert 'heart_rate' in state
        assert 'steps' in state

    def test_satellite_simulator(self):
        from eosim.engine.native.simulators import SatelliteSimulator
        vm = self._create_vm()
        sim = SatelliteSimulator(vm)
        sim.setup()
        assert 'rf0' in vm.peripherals
        assert 'crypto0' in vm.peripherals
        sim.tick()
        state = sim.get_state()
        assert 'solar_power_w' in state
        assert 'orbit_alt_km' in state

    def test_energy_simulator(self):
        from eosim.engine.native.simulators import EnergySimulator
        vm = self._create_vm()
        sim = EnergySimulator(vm)
        sim.setup()
        assert 'solar_adc' in vm.peripherals
        assert 'modbus0' in vm.peripherals
        sim.tick()
        state = sim.get_state()
        assert 'solar_power_w' in state
        assert 'battery_soc' in state

    def test_simulator_tick_increments(self):
        from eosim.engine.native.simulators import VehicleSimulator
        vm = self._create_vm()
        sim = VehicleSimulator(vm)
        sim.setup()
        assert sim.tick_count == 0
        sim.tick()
        sim.tick()
        sim.tick()
        assert sim.tick_count == 3

    def test_simulator_reset(self):
        from eosim.engine.native.simulators import DroneSimulator
        vm = self._create_vm()
        sim = DroneSimulator(vm)
        sim.setup()
        sim.tick()
        sim.tick()
        sim.reset()
        assert sim.tick_count == 0
        assert sim.state == {}


class TestSimulatorFactory:
    """Verify factory maps all product types to correct simulator."""

    def test_factory_creates_vehicle(self):
        from eosim.engine.native import VirtualMachine
        from eosim.engine.native.simulators import SimulatorFactory, VehicleSimulator
        vm = VirtualMachine(name="t", arch="arm", ram_mb=32)
        sim = SimulatorFactory.create("automotive_ecu", vm)
        assert isinstance(sim, VehicleSimulator)

    def test_factory_creates_drone(self):
        from eosim.engine.native import VirtualMachine
        from eosim.engine.native.simulators import SimulatorFactory, DroneSimulator
        vm = VirtualMachine(name="t", arch="arm", ram_mb=32)
        sim = SimulatorFactory.create("drone_controller", vm)
        assert isinstance(sim, DroneSimulator)

    def test_factory_creates_medical(self):
        from eosim.engine.native import VirtualMachine
        from eosim.engine.native.simulators import SimulatorFactory, MedicalSimulator
        vm = VirtualMachine(name="t", arch="arm", ram_mb=32)
        sim = SimulatorFactory.create("medical_monitor", vm)
        assert isinstance(sim, MedicalSimulator)

    def test_factory_creates_robot(self):
        from eosim.engine.native import VirtualMachine
        from eosim.engine.native.simulators import SimulatorFactory, RobotSimulator
        vm = VirtualMachine(name="t", arch="arm", ram_mb=32)
        sim = SimulatorFactory.create("robot_controller", vm)
        assert isinstance(sim, RobotSimulator)

    def test_factory_fallback_generic(self):
        from eosim.engine.native import VirtualMachine
        from eosim.engine.native.simulators import SimulatorFactory, BaseSimulator
        vm = VirtualMachine(name="t", arch="arm", ram_mb=32)
        sim = SimulatorFactory.create("unknown_product", vm)
        assert isinstance(sim, BaseSimulator)

    def test_factory_all_product_types_mapped(self):
        from eosim.gui.product_templates import PRODUCT_CATALOG
        from eosim.engine.native.simulators import SIMULATOR_MAP
        for key in PRODUCT_CATALOG:
            assert key in SIMULATOR_MAP, f"Product '{key}' not in SIMULATOR_MAP"

    def test_factory_list_simulators(self):
        from eosim.engine.native.simulators import SimulatorFactory
        sims = SimulatorFactory.list_simulators()
        assert 'vehicle' in sims
        assert 'drone' in sims
        assert 'medical' in sims
        assert 'robot' in sims
        assert 'generic' in sims


class TestSimulatorApp:
    """Verify VM creation from build config and basic lifecycle."""

    def test_vm_creation_from_config(self):
        from eosim.engine.native import VirtualMachine
        vm = VirtualMachine(name="test-iot", arch="arm", ram_mb=32)
        assert vm.name == "test-iot"
        assert vm.arch == "arm"
        assert not vm.running
        assert "uart0" in vm.peripherals
        assert "gpio0" in vm.peripherals
        assert "timer0" in vm.peripherals
        assert "spi0" in vm.peripherals
        assert "i2c0" in vm.peripherals
        assert "nvic" in vm.peripherals

    def test_vm_run_stop_lifecycle(self):
        from eosim.engine.native import VirtualMachine
        vm = VirtualMachine(name="lifecycle-test", arch="arm", ram_mb=16)
        result = vm.run(max_cycles=100, timeout_s=5.0)
        assert result["success"]
        assert result["cycles"] == 100
        assert not vm.running
        assert "boot_log" in result

    def test_vm_step(self):
        from eosim.engine.native import VirtualMachine
        vm = VirtualMachine(name="step-test", arch="arm", ram_mb=16)
        initial_pc = vm.cpu.state.pc
        vm.cpu.step()
        assert vm.cpu.state.pc == initial_pc + 4
        assert vm.cpu.state.cycles == 1

    def test_vm_uart_output(self):
        from eosim.engine.native import VirtualMachine
        vm = VirtualMachine(name="uart-test", arch="arm", ram_mb=16)
        vm.run(max_cycles=50, timeout_s=5.0)
        uart_out = vm.get_uart_output()
        assert "EoSim Virtual Machine" in uart_out
        assert "Booting" in uart_out

    def test_vm_gpio_interaction(self):
        from eosim.engine.native import VirtualMachine
        vm = VirtualMachine(name="gpio-test", arch="arm", ram_mb=16)
        gpio = vm.peripherals["gpio0"]
        assert gpio.input_val == 0
        gpio.set_input(5, True)
        assert gpio.input_val & (1 << 5)
        gpio.set_input(5, False)
        assert not (gpio.input_val & (1 << 5))

    def test_vm_peripheral_count(self):
        from eosim.engine.native import VirtualMachine
        vm = VirtualMachine(name="periph-test", arch="arm", ram_mb=16)
        assert len(vm.peripherals) == 6

    def test_memory_bus_dump(self):
        from eosim.engine.native import VirtualMachine
        vm = VirtualMachine(name="mem-test", arch="arm", ram_mb=16)
        dump = vm.bus.dump(0x20000000, 32)
        assert "20000000:" in dump

    def test_simulator_app_build_and_run(self):
        from eosim.gui.simulator_app import SimulatorApp
        app = SimulatorApp()
        vm = app.build_and_run("automotive_ecu")
        assert vm is not None
        assert app.running
        assert app.product_type == "automotive_ecu"
        assert 'can0' in vm.peripherals
        app.tick()
        state = app.get_state()
        assert 'speed_kmh' in state

    def test_simulator_app_run_cycles(self):
        from eosim.gui.simulator_app import SimulatorApp
        app = SimulatorApp()
        app.build_and_run("drone_controller")
        app.run_cycles(50)
        assert app.tick_count == 50

    def test_simulator_app_stop_reset(self):
        from eosim.gui.simulator_app import SimulatorApp
        app = SimulatorApp()
        app.build_and_run("medical_monitor")
        app.run_cycles(10)
        app.stop()
        assert not app.running
        app.reset()
        assert app.tick_count == 0

    def test_simulator_app_status_text(self):
        from eosim.gui.simulator_app import SimulatorApp
        app = SimulatorApp()
        assert app.get_status_text() == 'No simulation active'
        app.build_and_run("iot_sensor")
        text = app.get_status_text()
        assert 'IoT' in text

    def test_simulator_app_peripheral_names(self):
        from eosim.gui.simulator_app import SimulatorApp
        app = SimulatorApp()
        app.build_and_run("industrial_plc")
        names = app.get_peripheral_names()
        assert 'modbus0' in names
        assert 'relay0' in names


class TestCPUPanel:
    """Verify CPUPanel.update_state works with both dicts and objects."""

    @pytest.fixture(autouse=True)
    def _skip_no_tk(self):
        tk = pytest.importorskip("tkinter")
        import os
        import sys
        if sys.platform.startswith("linux") and not os.environ.get("DISPLAY") and not os.environ.get("WAYLAND_DISPLAY"):
            pytest.skip("No display available for tkinter on headless Linux")
        try:
            root = tk.Tk()
            root.destroy()
        except tk.TclError:
            pytest.skip("Tk runtime not available")

    def test_update_state_from_dict(self):
        """CPUPanel.update_state should accept a dict and store values."""
        import tkinter as tk
        from eosim.gui.widgets.cpu_panel import CPUPanel
        root = tk.Tk()
        root.withdraw()
        try:
            panel = CPUPanel(root)
            state = {
                'regs': [i * 100 for i in range(16)],
                'pc': 0x08001000,
                'sp': 0x20010000,
                'lr': 0x08000800,
                'cpsr': 0x60000013,
                'cycles': 42,
                'mode': 'user',
                'halted': False,
            }
            panel.update_state(state)
            assert panel._prev_pc == 0x08001000
            assert panel._prev_sp == 0x20010000
            assert panel._prev_lr == 0x08000800
            assert panel._prev_cpsr == 0x60000013
            assert panel._prev_regs[0] == 0
            assert panel._prev_regs[5] == 500
        finally:
            root.destroy()

    def test_update_state_from_cpu_state_object(self):
        """CPUPanel.update_state should accept a CPUState-like object."""
        import tkinter as tk
        from eosim.gui.widgets.cpu_panel import CPUPanel
        root = tk.Tk()
        root.withdraw()
        try:
            panel = CPUPanel(root)

            class FakeCPU:
                regs = [0] * 16
                pc = 0x08000000
                sp = 0x20000000
                lr = 0
                cpsr = 0
                cycles = 10
                mode = 'supervisor'
                halted = False

            panel.update_state(FakeCPU())
            assert panel._prev_pc == 0x08000000
            assert panel._prev_regs == [0] * 16
        finally:
            root.destroy()

    def test_reset_clears_state(self):
        """CPUPanel.reset should zero out all previous values."""
        import tkinter as tk
        from eosim.gui.widgets.cpu_panel import CPUPanel
        root = tk.Tk()
        root.withdraw()
        try:
            panel = CPUPanel(root)
            state = {
                'regs': [999] * 16, 'pc': 0xDEAD, 'sp': 0xBEEF,
                'lr': 0xCAFE, 'cpsr': 0xF0000000, 'cycles': 100,
            }
            panel.update_state(state)
            assert panel._prev_pc == 0xDEAD
            panel.reset()
            assert panel._prev_pc == 0
            assert panel._prev_sp == 0
            assert panel._prev_regs == [0] * 16
        finally:
            root.destroy()


class TestTkPeripheralPanel:
    """Verify domain sub-panel data flow for each simulator type."""

    def _create_sim(self, product_type):
        from eosim.engine.native import VirtualMachine
        from eosim.engine.native.simulators import SimulatorFactory
        vm = VirtualMachine(name="test", arch="arm", ram_mb=32)
        sim = SimulatorFactory.create(product_type, vm)
        return vm, sim

    def test_automotive_state_keys(self):
        vm, sim = self._create_sim("automotive_ecu")
        sim.tick()
        state = sim.get_state()
        assert 'speed_kmh' in state
        assert 'steering_deg' in state
        assert 'soc_pct' in state
        assert 'can0' in vm.peripherals
        can = vm.peripherals['can0']
        assert hasattr(can, 'tx_count')

    def test_drone_state_keys(self):
        vm, sim = self._create_sim("drone_controller")
        sim.tick()
        state = sim.get_state()
        assert 'motor_rpm' in state
        assert len(state['motor_rpm']) == 4
        assert 'altitude_m' in state
        assert 'flight_mode' in state
        assert 'roll_deg' in state

    def test_medical_state_keys(self):
        vm, sim = self._create_sim("medical_monitor")
        for _ in range(10):
            sim.tick()
        state = sim.get_state()
        assert 'heart_rate' in state
        assert 'spo2' in state
        assert 'temperature' in state
        assert 'alarm' in state
        assert 'ecg_waveform' in state

    def test_robot_state_keys(self):
        vm, sim = self._create_sim("robot_controller")
        sim.tick()
        state = sim.get_state()
        assert 'joint_angles' in state
        assert len(state['joint_angles']) == 6
        assert 'gripper_open' in state

    def test_aircraft_state_keys(self):
        vm, sim = self._create_sim("fixed_wing")
        sim.tick()
        state = sim.get_state()
        assert 'altitude_ft' in state
        assert 'airspeed_kts' in state
        assert 'heading_deg' in state

    def test_industrial_state_keys(self):
        vm, sim = self._create_sim("industrial_plc")
        sim.tick()
        state = sim.get_state()
        assert 'conveyor_speed' in state
        assert 'modbus0' in vm.peripherals

    def test_iot_state_keys(self):
        vm, sim = self._create_sim("iot_sensor")
        sim.tick()
        state = sim.get_state()
        assert 'temperature' in state

    def test_satellite_state_keys(self):
        vm, sim = self._create_sim("cubesat")
        sim.tick()
        state = sim.get_state()
        assert 'solar_power_w' in state
        assert 'orbit_alt_km' in state

    def test_energy_state_keys(self):
        vm, sim = self._create_sim("solar_inverter")
        sim.tick()
        state = sim.get_state()
        assert 'solar_power_w' in state
        assert 'battery_soc' in state

    def test_wearable_state_keys(self):
        vm, sim = self._create_sim("wearable_device")
        sim.tick()
        state = sim.get_state()
        assert 'heart_rate' in state
        assert 'steps' in state

    def test_peripheral_panel_configure(self):
        """PeripheralPanel should create sub-panels for all VM peripherals."""
        from eosim.gui.widgets.peripheral_panel import PeripheralPanel
        vm, sim = self._create_sim("automotive_ecu")
        panel = PeripheralPanel()
        panel.configure_for_product(vm, 'automotive')
        assert len(panel.sub_panels) > 0
        result = panel.update(vm)
        assert isinstance(result, dict)
        assert len(result) > 0


class TestScenarioLoading:
    """Verify each simulator's load_scenario changes state correctly."""

    def _create_sim(self, product_type):
        from eosim.engine.native import VirtualMachine
        from eosim.engine.native.simulators import SimulatorFactory
        vm = VirtualMachine(name="test", arch="arm", ram_mb=32)
        sim = SimulatorFactory.create(product_type, vm)
        return vm, sim

    def test_vehicle_highway_cruise(self):
        vm, sim = self._create_sim("automotive_ecu")
        sim.load_scenario('highway_cruise')
        assert sim.scenario == 'highway_cruise'
        assert sim.state.get('scenario') == 'highway_cruise'
        for _ in range(50):
            sim.tick()
        assert sim.state['speed_kmh'] > 0

    def test_vehicle_emergency_braking(self):
        vm, sim = self._create_sim("automotive_ecu")
        sim.load_scenario('highway_cruise')
        for _ in range(100):
            sim.tick()
        speed_before = sim.state['speed_kmh']
        sim.load_scenario('emergency_braking')
        for _ in range(100):
            sim.tick()
        assert sim.state['speed_kmh'] <= speed_before

    def test_drone_takeoff(self):
        vm, sim = self._create_sim("drone_controller")
        sim.load_scenario('takeoff')
        assert sim.state.get('flight_mode') != 'DISARMED'
        for _ in range(100):
            sim.tick()
        assert sim.state['altitude_m'] > 0

    def test_drone_motor_failure(self):
        vm, sim = self._create_sim("drone_controller")
        sim.load_scenario('motor_failure')
        assert sim.state.get('motor_failure') == 2

    def test_medical_alarm_trigger(self):
        vm, sim = self._create_sim("medical_monitor")
        sim.load_scenario('alarm_trigger')
        assert sim.state.get('scenario') == 'alarm_trigger'
        for _ in range(10):
            sim.tick()
        assert sim.state['heart_rate'] > 100

    def test_medical_sensor_disconnect(self):
        vm, sim = self._create_sim("medical_monitor")
        sim.load_scenario('sensor_disconnect')
        for _ in range(50):
            sim.tick()
        assert sim.state.get('sensor_connected') is False

    def test_all_simulators_have_scenarios(self):
        """Every non-base simulator should have a SCENARIOS dict."""
        from eosim.engine.native.simulators import (
            VehicleSimulator, DroneSimulator, MedicalSimulator,
            RobotSimulator, AircraftSimulator, IndustrialSimulator,
            IoTSimulator, SatelliteSimulator, EnergySimulator,
            WearableSimulator,
        )
        for cls in [VehicleSimulator, DroneSimulator, MedicalSimulator,
                    RobotSimulator, AircraftSimulator, IndustrialSimulator,
                    IoTSimulator, SatelliteSimulator, EnergySimulator,
                    WearableSimulator]:
            assert hasattr(cls, 'SCENARIOS'), f"{cls.__name__} missing SCENARIOS"
            assert len(cls.SCENARIOS) > 0, f"{cls.__name__} has empty SCENARIOS"

    def test_all_simulators_load_scenario(self):
        """Every simulator's load_scenario should set scenario name in state."""
        from eosim.engine.native import VirtualMachine
        from eosim.engine.native.simulators import SimulatorFactory, SIMULATOR_MAP
        tested = set()
        for product_type, cls in SIMULATOR_MAP.items():
            if cls.__name__ in tested or cls.__name__ == 'BaseSimulator':
                continue
            tested.add(cls.__name__)
            vm = VirtualMachine(name="t", arch="arm", ram_mb=32)
            sim = SimulatorFactory.create(product_type, vm)
            scenarios = getattr(sim, 'SCENARIOS', {})
            if scenarios:
                first = list(scenarios.keys())[0]
                sim.load_scenario(first)
                assert sim.state.get('scenario') == first, (
                    f"{cls.__name__}.load_scenario('{first}') "
                    f"didn't set state['scenario']"
                )
