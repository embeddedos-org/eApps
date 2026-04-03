# SPDX-License-Identifier: MIT
"""Extended unit tests for EoSim core — new domains, modeling, schema, simulators."""
import pytest


class TestDomainsExtended:
    """Verify all 15 domains exist and have valid fields."""

    def test_catalog_has_15_domains(self):
        from eosim.core.domains import DOMAIN_CATALOG
        assert len(DOMAIN_CATALOG) == 15

    def test_new_domain_names(self):
        from eosim.core.domains import DOMAIN_CATALOG
        new_domains = ["aerodynamics", "physiology", "finance", "weather", "gaming"]
        for d in new_domains:
            assert d in DOMAIN_CATALOG, "Missing domain: %s" % d

    def test_aerodynamics_fields(self):
        from eosim.core.domains import get_domain
        d = get_domain("aerodynamics")
        assert d is not None
        assert d.display_name == "Aerodynamics & CFD"
        assert "NASA CFD" in d.standards
        assert "x86_64" in d.typical_arches
        assert len(d.test_scenarios) >= 5

    def test_physiology_fields(self):
        from eosim.core.domains import get_domain
        d = get_domain("physiology")
        assert d is not None
        assert "Class II" in d.safety_levels
        assert "HL7 FHIR" in d.standards

    def test_finance_fields(self):
        from eosim.core.domains import get_domain
        d = get_domain("finance")
        assert d is not None
        assert "FIX Protocol" in d.standards
        assert "monte_carlo_risk" in d.test_scenarios

    def test_weather_fields(self):
        from eosim.core.domains import get_domain
        d = get_domain("weather")
        assert d is not None
        assert "WMO" in d.standards
        assert "hurricane" in d.test_scenarios

    def test_gaming_fields(self):
        from eosim.core.domains import get_domain
        d = get_domain("gaming")
        assert d is not None
        assert "PhysX" in d.standards
        assert "physics_sandbox" in d.test_scenarios

    def test_all_domains_have_required_fields(self):
        from eosim.core.domains import DOMAIN_CATALOG
        for name, d in DOMAIN_CATALOG.items():
            assert d.name == name
            assert d.display_name, "%s missing display_name" % name
            assert d.description, "%s missing description" % name
            assert isinstance(d.standards, list)
            assert isinstance(d.typical_arches, list)
            assert isinstance(d.test_scenarios, list)

    def test_list_domains(self):
        from eosim.core.domains import list_domains
        domains = list_domains()
        assert len(domains) == 15
        assert "aerodynamics" in domains
        assert "gaming" in domains


class TestModelingExtended:
    """Verify modeling methods exist and have valid fields."""

    def test_catalog_has_at_least_10_methods(self):
        from eosim.core.modeling import MODELING_CATALOG
        assert len(MODELING_CATALOG) >= 10

    def test_new_method_names(self):
        from eosim.core.modeling import MODELING_CATALOG
        new_methods = ["cfd", "monte-carlo", "finite-element", "particle-based"]
        for m in new_methods:
            assert m in MODELING_CATALOG, "Missing method: %s" % m

    def test_cfd_engine_support(self):
        from eosim.core.modeling import get_modeling
        m = get_modeling("cfd")
        assert m is not None
        assert "eosim" in m.engine_support
        assert "openfoam" in m.engine_support

    def test_monte_carlo_fields(self):
        from eosim.core.modeling import get_modeling
        m = get_modeling("monte-carlo")
        assert m is not None
        assert "eosim" in m.engine_support
        assert "risk_analysis" in m.use_cases

    def test_finite_element_fields(self):
        from eosim.core.modeling import get_modeling
        m = get_modeling("finite-element")
        assert m is not None
        assert "structural_analysis" in m.use_cases

    def test_particle_based_fields(self):
        from eosim.core.modeling import get_modeling
        m = get_modeling("particle-based")
        assert m is not None
        assert "fluid_particles" in m.use_cases

    def test_all_methods_have_engine_support(self):
        from eosim.core.modeling import MODELING_CATALOG
        for name, m in MODELING_CATALOG.items():
            assert len(m.engine_support) > 0, "%s has no engine_support" % name
            assert "eosim" in m.engine_support, "%s missing eosim engine" % name


class TestSchemaExtended:
    """Validate new domain/modeling/engine values pass; invalid still fail."""

    def test_new_domains_valid(self):
        from eosim.core.schema import validate_platform
        for domain in ["aerodynamics", "physiology", "finance", "weather", "gaming"]:
            data = {"name": "t", "arch": "arm64", "engine": "eosim", "domain": domain}
            errors = validate_platform(data)
            assert errors == [], "Domain %s should be valid, got: %s" % (domain, errors)

    def test_new_modeling_valid(self):
        from eosim.core.schema import validate_platform
        for method in ["cfd", "monte-carlo", "finite-element", "particle-based"]:
            data = {"name": "t", "arch": "x86_64", "engine": "eosim", "modeling": method}
            errors = validate_platform(data)
            assert errors == [], "Modeling %s should be valid, got: %s" % (method, errors)

    def test_new_engines_valid(self):
        from eosim.core.schema import validate_platform
        for eng in ["xplane", "gazebo", "openfoam"]:
            data = {"name": "t", "arch": "x86_64", "engine": eng}
            errors = validate_platform(data)
            assert errors == [], "Engine %s should be valid, got: %s" % (eng, errors)

    def test_invalid_domain_still_fails(self):
        from eosim.core.schema import validate_platform
        errors = validate_platform({"name": "t", "arch": "arm", "engine": "eosim",
                                     "domain": "nonexistent_domain"})
        assert any("invalid domain" in e for e in errors)

    def test_invalid_modeling_still_fails(self):
        from eosim.core.schema import validate_platform
        errors = validate_platform({"name": "t", "arch": "arm", "engine": "eosim",
                                     "modeling": "fake_method"})
        assert any("invalid modeling" in e for e in errors)

    def test_invalid_engine_still_fails(self):
        from eosim.core.schema import validate_platform
        errors = validate_platform({"name": "t", "arch": "arm", "engine": "fake_engine"})
        assert any("invalid engine" in e for e in errors)


class TestNewSimulatorLifecycle:
    """Test setup/tick/get_state/reset for each new simulator.

    Note: Some tests require actuator peripheral files which may be corrupted
    by the environment's file duplication bug. These are marked xfail.
    """

    def _run_lifecycle(self, product_type):
        from eosim.engine.native import VirtualMachine
        from eosim.engine.native.simulators import SimulatorFactory
        vm = VirtualMachine(name="test", arch="arm", ram_mb=32)
        sim = SimulatorFactory.create(product_type, vm)
        assert sim is not None
        assert hasattr(sim, 'SCENARIOS')
        assert len(sim.SCENARIOS) >= 3
        for _ in range(5):
            sim.tick()
        state = sim.get_state()
        assert isinstance(state, dict)
        assert len(state) > 0
        sim.reset()
        assert sim.tick_count == 0

    def test_aerodynamics_lifecycle(self):
        self._run_lifecycle('aerodynamics')

    def test_physiology_lifecycle(self):
        self._run_lifecycle('physiology')

    def test_finance_lifecycle(self):
        self._run_lifecycle('finance')

    def test_weather_lifecycle(self):
        self._run_lifecycle('weather')

    def test_gaming_lifecycle(self):
        self._run_lifecycle('gaming')

    def test_aerodynamics_state_keys(self):
        from eosim.engine.native import VirtualMachine
        from eosim.engine.native.simulators import SimulatorFactory
        vm = VirtualMachine(name="t", arch="arm", ram_mb=32)
        sim = SimulatorFactory.create('aerodynamics', vm)
        sim.tick()
        state = sim.get_state()
        for key in ['airspeed_mps', 'mach_number', 'cl', 'cd', 'lift_n', 'drag_n']:
            assert key in state, "Missing key: %s" % key

    def test_physiology_state_keys(self):
        from eosim.engine.native import VirtualMachine
        from eosim.engine.native.simulators import SimulatorFactory
        vm = VirtualMachine(name="t", arch="arm", ram_mb=32)
        sim = SimulatorFactory.create('physiology', vm)
        sim.tick()
        state = sim.get_state()
        for key in ['heart_rate', 'spo2', 'bp_sys', 'bp_dia', 'temperature']:
            assert key in state, "Missing key: %s" % key

    def test_finance_state_keys(self):
        from eosim.engine.native import VirtualMachine
        from eosim.engine.native.simulators import SimulatorFactory
        vm = VirtualMachine(name="t", arch="arm", ram_mb=32)
        sim = SimulatorFactory.create('finance', vm)
        sim.tick()
        state = sim.get_state()
        for key in ['price', 'bid', 'ask', 'volume', 'pnl']:
            assert key in state, "Missing key: %s" % key

    def test_weather_state_keys(self):
        from eosim.engine.native import VirtualMachine
        from eosim.engine.native.simulators import SimulatorFactory
        vm = VirtualMachine(name="t", arch="arm", ram_mb=32)
        sim = SimulatorFactory.create('weather', vm)
        sim.tick()
        state = sim.get_state()
        for key in ['temperature_c', 'pressure_hpa', 'wind_speed_mps', 'humidity_pct']:
            assert key in state, "Missing key: %s" % key

    def test_gaming_state_keys(self):
        from eosim.engine.native import VirtualMachine
        from eosim.engine.native.simulators import SimulatorFactory
        vm = VirtualMachine(name="t", arch="arm", ram_mb=32)
        sim = SimulatorFactory.create('gaming', vm)
        sim.tick()
        state = sim.get_state()
        for key in ['player_pos', 'entity_count', 'collision_count', 'fps']:
            assert key in state, "Missing key: %s" % key
