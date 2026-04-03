# SPDX-License-Identifier: MIT
"""Extended GUI tests — new product templates, simulators, renderers, panels."""
import pytest


class TestNewProductTemplates:
    """Verify new product templates exist and have valid fields."""

    def test_catalog_has_new_templates(self):
        from eosim.gui.product_templates import PRODUCT_CATALOG
        assert len(PRODUCT_CATALOG) >= 25

    def test_new_template_names(self):
        from eosim.gui.product_templates import PRODUCT_CATALOG
        new_templates = ["wind_tunnel", "patient_model", "stock_market",
                         "weather_station_sim", "game_world"]
        for t in new_templates:
            assert t in PRODUCT_CATALOG, "Missing template: %s" % t

    def test_wind_tunnel_fields(self):
        from eosim.gui.product_templates import get_template
        t = get_template("wind_tunnel")
        assert t is not None
        assert t.domain == "aerodynamics"
        assert t.modeling == "cfd"
        assert t.arch == "x86_64"
        assert t.ram_mb == 512
        assert t.simulator_class == "AerodynamicsSimulator"

    def test_patient_model_fields(self):
        from eosim.gui.product_templates import get_template
        t = get_template("patient_model")
        assert t is not None
        assert t.domain == "physiology"
        assert t.modeling == "continuous"
        assert t.simulator_class == "PhysiologySimulator"

    def test_stock_market_fields(self):
        from eosim.gui.product_templates import get_template
        t = get_template("stock_market")
        assert t is not None
        assert t.domain == "finance"
        assert t.modeling == "monte-carlo"
        assert t.simulator_class == "FinanceSimulator"

    def test_weather_station_sim_fields(self):
        from eosim.gui.product_templates import get_template
        t = get_template("weather_station_sim")
        assert t is not None
        assert t.domain == "weather"
        assert t.simulator_class == "WeatherSimulator"

    def test_game_world_fields(self):
        from eosim.gui.product_templates import get_template
        t = get_template("game_world")
        assert t is not None
        assert t.domain == "gaming"
        assert t.modeling == "agent-based"
        assert t.ram_mb == 1024
        assert t.simulator_class == "GamingSimulator"

    def test_new_templates_have_required_fields(self):
        from eosim.gui.product_templates import PRODUCT_CATALOG
        required = ["name", "display_name", "icon", "arch", "ram_mb",
                     "peripherals", "domain", "modeling", "description",
                     "default_platform", "simulator_class"]
        new = ["wind_tunnel", "patient_model", "stock_market",
               "weather_station_sim", "game_world"]
        for key in new:
            tpl = PRODUCT_CATALOG[key]
            for field in required:
                val = getattr(tpl, field)
                if field == "ram_mb":
                    assert val > 0
                elif field == "peripherals":
                    assert isinstance(val, list) and len(val) > 0
                else:
                    assert val, "%s.%s is empty" % (key, field)

    def test_new_templates_valid_domain(self):
        from eosim.gui.product_templates import PRODUCT_CATALOG
        from eosim.core.schema import VALID_DOMAINS
        new = ["wind_tunnel", "patient_model", "stock_market",
               "weather_station_sim", "game_world"]
        for key in new:
            tpl = PRODUCT_CATALOG[key]
            assert tpl.domain in VALID_DOMAINS, "%s invalid domain: %s" % (key, tpl.domain)

    def test_new_templates_valid_modeling(self):
        from eosim.gui.product_templates import PRODUCT_CATALOG
        from eosim.core.schema import VALID_MODELING
        new = ["wind_tunnel", "stock_market", "game_world"]
        for key in new:
            tpl = PRODUCT_CATALOG[key]
            assert tpl.modeling in VALID_MODELING, "%s invalid modeling: %s" % (key, tpl.modeling)


class TestNewSimulatorMap:
    """Assert new product types map correctly in SIMULATOR_MAP."""

    def test_aerodynamics_mappings(self):
        from eosim.engine.native.simulators import SIMULATOR_MAP
        from eosim.engine.native.simulators.aerodynamics import AerodynamicsSimulator
        for key in ['aerodynamics', 'wind_tunnel', 'cfd_lab']:
            assert key in SIMULATOR_MAP
            assert SIMULATOR_MAP[key] is AerodynamicsSimulator

    def test_physiology_mappings(self):
        from eosim.engine.native.simulators import SIMULATOR_MAP
        from eosim.engine.native.simulators.physiology import PhysiologySimulator
        for key in ['physiology', 'patient_model']:
            assert key in SIMULATOR_MAP
            assert SIMULATOR_MAP[key] is PhysiologySimulator

    def test_finance_mappings(self):
        from eosim.engine.native.simulators import SIMULATOR_MAP
        from eosim.engine.native.simulators.finance import FinanceSimulator
        for key in ['finance', 'stock_market', 'trading_sim']:
            assert key in SIMULATOR_MAP
            assert SIMULATOR_MAP[key] is FinanceSimulator

    def test_weather_mappings(self):
        from eosim.engine.native.simulators import SIMULATOR_MAP
        from eosim.engine.native.simulators.weather import WeatherSimulator
        for key in ['weather', 'weather_station_sim', 'atmosphere']:
            assert key in SIMULATOR_MAP
            assert SIMULATOR_MAP[key] is WeatherSimulator

    def test_gaming_mappings(self):
        from eosim.engine.native.simulators import SIMULATOR_MAP
        from eosim.engine.native.simulators.gaming import GamingSimulator
        for key in ['gaming', 'game_world', 'physics_sandbox']:
            assert key in SIMULATOR_MAP
            assert SIMULATOR_MAP[key] is GamingSimulator


class TestNewRenderers:
    """Assert new renderers registered."""

    def test_new_renderers_registered(self):
        from eosim.gui.renderers import get_renderer
        for domain in ['aerodynamics', 'physiology', 'finance', 'weather', 'gaming']:
            r = get_renderer(domain)
            assert r.DOMAIN == domain, "Renderer for %s not found" % domain

    def test_renderer_has_setup_and_update(self):
        from eosim.gui.renderers import get_renderer
        for domain in ['aerodynamics', 'physiology', 'finance', 'weather', 'gaming']:
            r = get_renderer(domain)
            assert hasattr(r, 'setup')
            assert hasattr(r, 'update')
            assert callable(r.setup)
            assert callable(r.update)


class TestNewPeripheralPanels:
    """Verify new domain panels instantiate."""

    def test_panel_classes_exist(self):
        from eosim.gui.widgets.peripheral_panel import (
            AerodynamicsPanel, PhysiologyPanel, FinancePanel,
            WeatherPanel, GamingPanel,
        )
        for cls in [AerodynamicsPanel, PhysiologyPanel, FinancePanel,
                    WeatherPanel, GamingPanel]:
            panel = cls("test", "TestDevice")
            assert panel.name == "test"
            assert panel.device_type == "TestDevice"

    def test_domain_panel_map_has_new_entries(self):
        from eosim.gui.widgets.peripheral_panel import DOMAIN_PANEL_MAP
        for domain in ['aerodynamics', 'physiology', 'finance', 'weather', 'gaming']:
            assert domain in DOMAIN_PANEL_MAP, "Missing domain panel: %s" % domain

    def test_device_domain_map_has_new_entries(self):
        from eosim.gui.widgets.peripheral_panel import DEVICE_DOMAIN_MAP
        new_devices = [
            'WindTunnelSensor', 'ForceBalance', 'HeartModel', 'LungModel',
            'MarketFeed', 'TradeExecutor', 'WeatherStation', 'Anemometer',
            'PhysicsEngine', 'EntityManager', 'GameController',
        ]
        for dev in new_devices:
            assert dev in DEVICE_DOMAIN_MAP, "Missing device mapping: %s" % dev


class TestNewBuildPanelPeripherals:
    """Verify new peripherals in build panel."""

    def test_new_peripherals_in_all_peripherals(self):
        from eosim.gui.widgets.build_panel import ALL_PERIPHERALS
        new_periphs = ['heart_model', 'bp_sensor', 'market_feed', 'order_book',
                       'anemometer', 'radar', 'physics_engine', 'terrain', 'entities']
        for p in new_periphs:
            assert p in ALL_PERIPHERALS, "Missing peripheral: %s" % p
