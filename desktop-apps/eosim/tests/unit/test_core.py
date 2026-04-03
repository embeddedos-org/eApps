# SPDX-License-Identifier: MIT
"""Unit tests for EoSim core."""
import pytest, os, tempfile, yaml
from eosim.core.platform import Platform, discover_platforms
from eosim.engine.backend import SimResult, RenodeEngine, QemuEngine
from eosim.tests.runner import run_checks
from eosim.artifacts.manager import collect_artifacts, generate_junit

class TestPlatform:
    def test_from_yaml(self, tmp_path):
        cfg = tmp_path / "platform.yml"
        cfg.write_text(yaml.dump({"name": "test", "arch": "arm64", "engine": "qemu",
            "runtime": {"memory_mb": 1024}, "qemu": {"machine": "virt", "cpu": "cortex-a57"}}))
        p = Platform.from_yaml(str(cfg))
        assert p.name == "test"
        assert p.arch == "arm64"
        assert p.engine == "qemu"
        assert p.runtime.memory_mb == 1024
        assert p.qemu.machine == "virt"

    def test_discover(self):
        root = os.path.join(os.path.dirname(__file__), "..", "..", "platforms")
        platforms = discover_platforms(root)
        assert len(platforms) >= 4
        assert "arm64-linux" in platforms
        assert "riscv64-linux" in platforms
        assert "x86_64-linux" in platforms

    def test_discover_empty(self, tmp_path):
        platforms = discover_platforms(str(tmp_path))
        assert len(platforms) == 0

    def test_defaults(self):
        p = Platform()
        assert p.runtime.memory_mb == 512
        assert p.runtime.headless is True
        assert p.engine == "renode"

class TestSimResult:
    def test_defaults(self):
        r = SimResult()
        assert r.success is False
        assert r.exit_code == -1
        assert r.artifacts == []

    def test_boot_detection(self):
        r = SimResult(stdout="kernel booted successfully login:")
        r.boot_detected = "login:" in r.stdout
        assert r.boot_detected is True

class TestRunner:
    def test_serial_contains_pass(self):
        r = SimResult(stdout="Welcome to EoS login: root")
        checks = [{"type": "serial_contains", "value": "login:"}]
        results = run_checks(r, checks)
        assert len(results) == 1
        assert results[0].passed is True

    def test_serial_contains_fail(self):
        r = SimResult(stdout="kernel panic")
        checks = [{"type": "serial_contains", "value": "login:"}]
        results = run_checks(r, checks)
        assert results[0].passed is False

    def test_timeout_check(self):
        r = SimResult(duration_s=30.0)
        checks = [{"type": "timeout", "seconds": 60}]
        results = run_checks(r, checks)
        assert results[0].passed is True

    def test_boot_success(self):
        r = SimResult(boot_detected=True)
        checks = [{"type": "boot_success"}]
        results = run_checks(r, checks)
        assert results[0].passed is True

    def test_multiple_checks(self):
        r = SimResult(stdout="EoS booted login:", duration_s=10, boot_detected=True)
        checks = [
            {"type": "serial_contains", "value": "login:"},
            {"type": "timeout", "seconds": 60},
            {"type": "boot_success"},
        ]
        results = run_checks(r, checks)
        assert all(t.passed for t in results)
        assert len(results) == 3

class TestArtifacts:
    def test_collect(self, tmp_path):
        log = tmp_path / "test.log"
        log.write_text("boot output")
        r = SimResult(platform="test", engine="qemu", success=True,
                       duration_s=5.0, log_file=str(log))
        manifest = collect_artifacts(r, str(tmp_path / "artifacts"))
        assert manifest["success"] is True
        assert manifest["platform"] == "test"

    def test_junit(self, tmp_path):
        results = [
            {"platform": "arm64", "success": True, "duration_s": 5.0},
            {"platform": "riscv", "success": False, "duration_s": 3.0},
        ]
        output = str(tmp_path / "junit.xml")
        path = generate_junit(results, output)
        assert os.path.exists(path)
        content = open(path).read()
        assert 'tests="2"' in content
        assert 'failures="1"' in content

class TestEngines:
    def test_renode_available(self):
        RenodeEngine.available()

    def test_qemu_available(self):
        QemuEngine.available("x86_64")

class TestSchema:
    def test_valid_platform(self):
        from eosim.core.schema import validate_platform
        data = {"name": "test", "arch": "arm64", "engine": "renode"}
        assert validate_platform(data) == []

    def test_missing_fields(self):
        from eosim.core.schema import validate_platform
        errors = validate_platform({})
        assert len(errors) == 3

    def test_invalid_arch(self):
        from eosim.core.schema import validate_platform
        errors = validate_platform({"name": "t", "arch": "z80", "engine": "qemu"})
        assert any("invalid arch" in e for e in errors)

    def test_invalid_engine(self):
        from eosim.core.schema import validate_platform
        errors = validate_platform({"name": "t", "arch": "arm64", "engine": "bochs"})
        assert any("invalid engine" in e for e in errors)


class TestScenarios:
    def test_wait_for_pass(self):
        from eosim.tests.scenarios import run_scenario
        from eosim.engine.backend import SimResult
        scenario = {"steps": [{"type": "wait_for", "pattern": "login:"}]}
        results = run_scenario(scenario, "Welcome login: root", 5.0)
        assert results[0].passed

    def test_assert_no_pass(self):
        from eosim.tests.scenarios import run_scenario
        scenario = {"steps": [{"type": "assert_no", "pattern": "panic"}]}
        results = run_scenario(scenario, "Booting Linux", 5.0)
        assert results[0].passed

    def test_assert_no_fail(self):
        from eosim.tests.scenarios import run_scenario
        scenario = {"steps": [{"type": "assert_no", "pattern": "panic"}]}
        results = run_scenario(scenario, "kernel panic", 5.0)
        assert not results[0].passed

    def test_count_matches(self):
        from eosim.tests.scenarios import run_scenario
        scenario = {"steps": [{"type": "count_matches", "pattern": "OK", "min_count": 3}]}
        results = run_scenario(scenario, "OK OK OK OK", 5.0)
        assert results[0].passed


class TestCluster:
    def test_from_yaml(self, tmp_path):
        from eosim.core.cluster import Cluster
        cfg = tmp_path / "cluster.yml"
        cfg.write_text("name: test\nnodes:\n  - name: n1\n    platform: arm64-linux\nlinks: []")
        c = Cluster.from_yaml(str(cfg))
        assert c.name == "test"
        assert len(c.nodes) == 1

    def test_validate_ok(self):
        from eosim.core.cluster import Cluster, ClusterNode
        c = Cluster(name="test", nodes=[ClusterNode(name="n1", platform="arm64-linux")])
        errors = c.validate({"arm64-linux": None})
        assert len(errors) == 0

    def test_validate_duplicate_node(self):
        from eosim.core.cluster import Cluster, ClusterNode
        c = Cluster(name="test", nodes=[
            ClusterNode(name="n1", platform="arm64-linux"),
            ClusterNode(name="n1", platform="arm64-linux")])
        errors = c.validate({"arm64-linux": None})
        assert any("duplicate" in e for e in errors)


class TestPeripherals:
    def test_list(self):
        from eosim.engine.peripherals import list_peripherals
        perips = list_peripherals()
        assert "uart" in perips
        assert "spi" in perips
        assert "gpio" in perips
        assert len(perips) >= 8

    def test_generate_repl(self):
        from eosim.engine.peripherals import generate_repl_peripherals
        repl = generate_repl_peripherals(["uart", "spi"])
        assert "UART" in repl
        assert "SPI" in repl


class TestJobQueue:
    def test_submit_and_get(self, tmp_path):
        from eosim.core.jobs import JobQueue
        q = JobQueue(str(tmp_path))
        job = q.submit("arm64-linux", "qemu")
        assert job.status == "pending"
        got = q.get(job.job_id)
        assert got is not None
        assert got.platform == "arm64-linux"

    def test_list_jobs(self, tmp_path):
        from eosim.core.jobs import JobQueue
        import time
        q = JobQueue(str(tmp_path))
        q.submit("arm64-linux")
        time.sleep(0.01)
        q.submit("riscv64-linux")
        jobs = q.list_jobs()
        assert len(jobs) >= 1

    def test_update_status(self, tmp_path):
        from eosim.core.jobs import JobQueue
        q = JobQueue(str(tmp_path))
        job = q.submit("arm64-linux")
        q.update(job.job_id, status="completed")
        updated = q.get(job.job_id)
        assert updated.status == "completed"

class TestNativeEngine:
    def test_vm_create(self):
        from eosim.engine.native import VirtualMachine
        vm = VirtualMachine('test', 'arm64', ram_mb=64)
        assert vm.name == 'test'
        assert vm.arch == 'arm64'
        assert len(vm.peripherals) >= 5

    def test_vm_run(self):
        from eosim.engine.native import VirtualMachine
        vm = VirtualMachine('test', 'arm', ram_mb=32)
        result = vm.run(max_cycles=100, timeout_s=5)
        assert result['success']
        assert result['cycles'] > 0
        assert 'EoSim' in result['boot_log']

    def test_memory(self):
        from eosim.engine.native.memory import MemoryBus, MemoryRegion
        bus = MemoryBus()
        bus.add_region(MemoryRegion('ram', 0x20000000, 1024))
        bus.write32(0x20000000, 0xDEADBEEF)
        assert bus.read32(0x20000000) == 0xDEADBEEF
        bus.write8(0x20000010, 0x42)
        assert bus.read8(0x20000010) == 0x42

    def test_uart(self):
        from eosim.engine.native.peripherals import UARTDevice
        uart = UARTDevice('uart0', 0x40000000)
        uart.write_reg(0x00, ord('H'))
        uart.write_reg(0x00, ord('i'))
        assert uart.get_output() == 'Hi'

    def test_gpio(self):
        from eosim.engine.native.peripherals import GPIODevice
        gpio = GPIODevice('gpio0', 0x40010000)
        gpio.write_reg(0x00, 0xFF)  # direction = output
        gpio.write_reg(0x04, 0x55)  # output value
        assert gpio.read_reg(0x04) == 0x55
        gpio.set_input(0, True)
        assert gpio.read_reg(0x08) & 1 == 1

    def test_timer(self):
        from eosim.engine.native.peripherals import TimerDevice
        timer = TimerDevice('timer0', 0x40020000)
        timer.write_reg(0x00, 10)  # reload = 10
        timer.write_reg(0x04, 3)   # enable + irq
        for _ in range(10):
            timer.tick()
        assert timer.irq_pending

    def test_spi(self):
        from eosim.engine.native.peripherals import SPIDevice
        spi = SPIDevice('spi0', 0x40030000)
        spi.write_reg(0x04, 1)  # enable
        spi.write_reg(0x00, 0xAA)  # tx
        assert spi.read_reg(0x04) & 2  # transfer complete

    def test_i2c(self):
        from eosim.engine.native.peripherals import I2CDevice
        i2c = I2CDevice('i2c0', 0x40040000)
        i2c.add_slave(0x50, lambda v: 0x42)
        i2c.write_reg(0x00, 0x50)  # slave addr
        i2c.write_reg(0x04, 0x01)  # tx
        assert i2c.read_reg(0x04) == 0x42  # rx from slave
        assert i2c.read_reg(0x08) == 1  # ACK

    def test_interrupt_controller(self):
        from eosim.engine.native.peripherals import InterruptController
        nvic = InterruptController('nvic', 0xE000E000)
        nvic.enable_irq(5)
        nvic.trigger(5)
        assert nvic.get_highest_pending() == 5
        nvic.acknowledge(5)
        assert nvic.get_highest_pending() == -1

    def test_cpu_state(self):
        from eosim.engine.native.cpu import CPUSimulator
        cpu = CPUSimulator('arm64')
        cpu.reset(entry=0x08000000, stack=0x20001000)
        assert cpu.state.pc == 0x08000000
        assert cpu.state.sp == 0x20001000

    def test_eosim_engine(self):
        from eosim.engine.backend import EoSimEngine
        assert EoSimEngine.available()


class TestPlatformExtendedFields:
    """Tests for new Platform metadata fields."""

    def test_from_yaml_with_metadata(self, tmp_path):
        cfg = tmp_path / "platform.yml"
        cfg.write_text(yaml.dump({
            "name": "test-mcu", "arch": "arm", "engine": "eosim",
            "vendor": "ST", "class": "mcu", "soc": "STM32F407",
            "domain": "industrial", "modeling": "deterministic",
            "domain_config": {"safety_level": "SIL-2"},
            "modeling_config": {"seed": 42},
            "runtime": {"memory_mb": 128},
        }))
        p = Platform.from_yaml(str(cfg))
        assert p.vendor == "ST"
        assert p.platform_class == "mcu"
        assert p.soc == "STM32F407"
        assert p.domain == "industrial"
        assert p.modeling == "deterministic"
        assert p.domain_config == {"safety_level": "SIL-2"}
        assert p.modeling_config == {"seed": 42}

    def test_from_yaml_without_metadata(self, tmp_path):
        cfg = tmp_path / "platform.yml"
        cfg.write_text(yaml.dump({"name": "bare", "arch": "arm64", "engine": "qemu"}))
        p = Platform.from_yaml(str(cfg))
        assert p.vendor == ""
        assert p.platform_class == ""
        assert p.soc == ""
        assert p.domain == ""
        assert p.modeling == ""
        assert p.domain_config == {}
        assert p.modeling_config == {}

    def test_backward_compat_defaults(self):
        p = Platform()
        assert p.vendor == ""
        assert p.platform_class == ""
        assert p.soc == ""
        assert p.domain == ""
        assert p.modeling == ""

    def test_class_keyword_mapping(self, tmp_path):
        cfg = tmp_path / "platform.yml"
        cfg.write_text(yaml.dump({
            "name": "t", "arch": "arm", "engine": "eosim", "class": "sbc",
        }))
        p = Platform.from_yaml(str(cfg))
        assert p.platform_class == "sbc"


class TestRegistry:
    """Tests for PlatformRegistry filter, group, search, stats."""

    def _make_registry(self):
        from eosim.core.registry import PlatformRegistry
        p1 = Platform(name="stm32f4", arch="arm", engine="eosim",
                       vendor="ST", platform_class="mcu", soc="STM32F407",
                       domain="industrial")
        p2 = Platform(name="nrf52", arch="arm", engine="eosim",
                       vendor="Nordic", platform_class="mcu", soc="nRF52840",
                       domain="iot")
        p3 = Platform(name="raspi4", arch="arm64", engine="renode",
                       vendor="Raspberry Pi", platform_class="sbc", soc="BCM2711",
                       domain="consumer")
        p4 = Platform(name="esp32", arch="xtensa", engine="eosim",
                       vendor="Espressif", platform_class="mcu", soc="ESP32",
                       domain="iot")
        return PlatformRegistry.from_dict({
            "stm32f4": p1, "nrf52": p2, "raspi4": p3, "esp32": p4,
        })

    def test_count(self):
        reg = self._make_registry()
        assert reg.count() == 4

    def test_all(self):
        reg = self._make_registry()
        assert len(reg.all()) == 4

    def test_get_existing(self):
        reg = self._make_registry()
        p = reg.get("stm32f4")
        assert p is not None
        assert p.vendor == "ST"

    def test_get_missing(self):
        reg = self._make_registry()
        assert reg.get("nonexistent") is None

    def test_filter_by_arch(self):
        reg = self._make_registry()
        results = reg.filter(arch="arm")
        assert len(results) == 2
        assert all(p.arch == "arm" for p in results)

    def test_filter_by_vendor(self):
        reg = self._make_registry()
        results = reg.filter(vendor="ST")
        assert len(results) == 1
        assert results[0].name == "stm32f4"

    def test_filter_by_class(self):
        reg = self._make_registry()
        results = reg.filter(platform_class="mcu")
        assert len(results) == 3

    def test_filter_by_engine(self):
        reg = self._make_registry()
        results = reg.filter(engine="eosim")
        assert len(results) == 3

    def test_filter_by_domain(self):
        reg = self._make_registry()
        results = reg.filter(domain="iot")
        assert len(results) == 2

    def test_filter_combined(self):
        reg = self._make_registry()
        results = reg.filter(arch="arm", vendor="Nordic")
        assert len(results) == 1
        assert results[0].name == "nrf52"

    def test_filter_no_results(self):
        reg = self._make_registry()
        results = reg.filter(arch="mipsel", vendor="ST")
        assert len(results) == 0

    def test_filter_case_insensitive(self):
        reg = self._make_registry()
        results = reg.filter(vendor="st")
        assert len(results) == 1

    def test_group_by_arch(self):
        reg = self._make_registry()
        groups = reg.group_by("arch")
        assert "arm" in groups
        assert "arm64" in groups
        assert len(groups["arm"]) == 2

    def test_group_by_vendor(self):
        reg = self._make_registry()
        groups = reg.group_by("vendor")
        assert "ST" in groups
        assert "Nordic" in groups

    def test_search(self):
        reg = self._make_registry()
        results = reg.search("STM32")
        assert len(results) == 1
        assert results[0].name == "stm32f4"

    def test_search_case_insensitive(self):
        reg = self._make_registry()
        results = reg.search("espressif")
        assert len(results) == 1
        assert results[0].name == "esp32"

    def test_search_by_arch(self):
        reg = self._make_registry()
        results = reg.search("xtensa")
        assert len(results) >= 1

    def test_stats(self):
        reg = self._make_registry()
        st = reg.stats()
        assert "arch" in st
        assert "vendor" in st
        assert "platform_class" in st
        assert "engine" in st
        assert st["arch"]["arm"] == 2

    def test_vendors(self):
        reg = self._make_registry()
        vendors = reg.vendors()
        assert "ST" in vendors
        assert "Nordic" in vendors

    def test_arches(self):
        reg = self._make_registry()
        arches = reg.arches()
        assert "arm" in arches
        assert "arm64" in arches

    def test_classes(self):
        reg = self._make_registry()
        classes = reg.classes()
        assert "mcu" in classes
        assert "sbc" in classes

    def test_registry_from_dir(self):
        from eosim.core.registry import PlatformRegistry
        root = os.path.join(os.path.dirname(__file__), "..", "..", "platforms")
        reg = PlatformRegistry(root)
        assert reg.count() >= 41


class TestHostEnvironment:
    """Tests for HostEnvironment detection and binary resolution."""

    def test_detect(self):
        from eosim.core.host import HostEnvironment
        env = HostEnvironment.detect()
        assert env.os_name in ("windows", "macos", "linux")
        assert env.arch != ""
        assert env.python_version != ""

    def test_platform_info(self):
        from eosim.core.host import HostEnvironment
        env = HostEnvironment.detect()
        info = env.platform_info()
        assert "os" in info
        assert "python" in info
        assert "arch" in info
        assert "shell" in info

    def test_adapt_path_windows(self):
        from eosim.core.host import HostEnvironment
        env = HostEnvironment(os_name="windows")
        assert "\\" in env.adapt_path("some/path/to/file")

    def test_adapt_path_linux(self):
        from eosim.core.host import HostEnvironment
        env = HostEnvironment(os_name="linux")
        assert "/" in env.adapt_path("some\\path\\to\\file")

    def test_resolve_binary_none(self):
        from eosim.core.host import HostEnvironment
        env = HostEnvironment.detect()
        result = env.resolve_binary("this_binary_definitely_does_not_exist_12345")
        assert result is None


class TestDomains:
    """Tests for domain profiles and catalog."""

    def test_catalog_complete(self):
        from eosim.core.domains import DOMAIN_CATALOG, list_domains
        domains = list_domains()
        assert len(domains) == 15
        expected = ["automotive", "medical", "industrial", "consumer",
                     "aerospace", "iot", "robotics", "defense", "energy", "telecom",
                     "aerodynamics", "physiology", "finance", "weather", "gaming"]
        for d in expected:
            assert d in domains

    def test_get_domain(self):
        from eosim.core.domains import get_domain
        d = get_domain("automotive")
        assert d is not None
        assert d.display_name == "Automotive / Transportation"
        assert "ISO 26262" in d.standards
        assert len(d.safety_levels) == 4

    def test_get_domain_missing(self):
        from eosim.core.domains import get_domain
        assert get_domain("nonexistent") is None

    def test_suggest_platforms(self):
        from eosim.core.domains import suggest_platforms
        from eosim.core.registry import PlatformRegistry
        p1 = Platform(name="auto-mcu", arch="arm", platform_class="mcu",
                       domain="automotive")
        p2 = Platform(name="iot-sensor", arch="xtensa", platform_class="mcu",
                       domain="iot")
        reg = PlatformRegistry.from_dict({"auto-mcu": p1, "iot-sensor": p2})
        results = suggest_platforms("automotive", reg)
        assert any(p.name == "auto-mcu" for p in results)


class TestModeling:
    """Tests for modeling method catalog."""

    def test_catalog_complete(self):
        from eosim.core.modeling import MODELING_CATALOG, list_modeling_methods
        methods = list_modeling_methods()
        assert len(methods) == 10
        expected = ["deterministic", "stochastic", "discrete-event",
                     "continuous", "hybrid", "agent-based", "cfd",
                     "monte-carlo", "finite-element", "particle-based"]
        for m in expected:
            assert m in methods

    def test_get_modeling(self):
        from eosim.core.modeling import get_modeling
        m = get_modeling("deterministic")
        assert m is not None
        assert "eosim" in m.engine_support
        assert "renode" in m.engine_support

    def test_get_modeling_missing(self):
        from eosim.core.modeling import get_modeling
        assert get_modeling("nonexistent") is None

    def test_validate_compatible(self):
        from eosim.core.modeling import validate_modeling_for_engine
        warnings = validate_modeling_for_engine("deterministic", "eosim")
        assert len(warnings) == 0

    def test_validate_incompatible(self):
        from eosim.core.modeling import validate_modeling_for_engine
        warnings = validate_modeling_for_engine("stochastic", "qemu")
        assert len(warnings) > 0
        assert "not supported" in warnings[0]

    def test_validate_unknown_method(self):
        from eosim.core.modeling import validate_modeling_for_engine
        warnings = validate_modeling_for_engine("unknown_method", "eosim")
        assert len(warnings) > 0
        assert "Unknown" in warnings[0]


class TestSchemaExtended:
    """Tests for extended schema validation (class, domain, modeling)."""

    def test_valid_eosim_engine(self):
        from eosim.core.schema import validate_platform
        data = {"name": "t", "arch": "arm", "engine": "eosim"}
        assert validate_platform(data) == []

    def test_valid_class(self):
        from eosim.core.schema import validate_platform
        data = {"name": "t", "arch": "arm", "engine": "eosim", "class": "mcu"}
        assert validate_platform(data) == []

    def test_invalid_class(self):
        from eosim.core.schema import validate_platform
        errors = validate_platform({"name": "t", "arch": "arm", "engine": "eosim",
                                     "class": "invalid_class"})
        assert any("invalid class" in e for e in errors)

    def test_valid_domain(self):
        from eosim.core.schema import validate_platform
        data = {"name": "t", "arch": "arm", "engine": "eosim",
                "domain": "automotive"}
        assert validate_platform(data) == []

    def test_invalid_domain(self):
        from eosim.core.schema import validate_platform
        errors = validate_platform({"name": "t", "arch": "arm", "engine": "eosim",
                                     "domain": "invalid_domain"})
        assert any("invalid domain" in e for e in errors)

    def test_valid_modeling(self):
        from eosim.core.schema import validate_platform
        data = {"name": "t", "arch": "arm", "engine": "eosim",
                "modeling": "deterministic"}
        assert validate_platform(data) == []

    def test_invalid_modeling(self):
        from eosim.core.schema import validate_platform
        errors = validate_platform({"name": "t", "arch": "arm", "engine": "eosim",
                                     "modeling": "invalid_method"})
        assert any("invalid modeling" in e for e in errors)
