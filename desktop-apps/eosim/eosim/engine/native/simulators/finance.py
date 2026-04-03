# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""Finance simulator — stock market, GBM price model, risk analysis.

Pure Python, cross-platform. No OS-specific dependencies.
"""
import math
import random


class FinanceSimulator:
    """Financial markets simulator.

    Physics: GBM price model, P&L, VaR, order matching.
    Scenarios: bull_market, bear_market, flash_crash,
               earnings_report, monte_carlo_risk.
    """

    PRODUCT_TYPE = 'finance'
    DISPLAY_NAME = 'Financial Market'

    SCENARIOS = {
        'bull_market': {
            'drift': 0.001, 'volatility': 0.015,
            'description': 'Sustained upward price trend',
        },
        'bear_market': {
            'drift': -0.001, 'volatility': 0.02,
            'description': 'Sustained downward price trend',
        },
        'flash_crash': {
            'crash_tick': 100, 'crash_pct': -0.15,
            'description': 'Sudden market crash with recovery',
        },
        'earnings_report': {
            'event_tick': 50, 'gap_pct': 0.08, 'volatility': 0.03,
            'description': 'Earnings surprise with gap and vol spike',
        },
        'monte_carlo_risk': {
            'iterations': 1000, 'confidence': 0.95,
            'description': 'Monte Carlo VaR calculation',
        },
    }

    def __init__(self, vm):
        self.vm = vm
        self.tick_count = 0
        self.state = {}
        self.scenario = ''
        self._scenario_step = 0

    def setup(self):
        from eosim.engine.native.peripherals.sensors_finance import (
            MarketFeed, OrderBook)
        from eosim.engine.native.peripherals.actuators_finance import (
            TradeExecutor, RiskEngine)

        self.vm.add_peripheral('market', MarketFeed('market', 0x40130000))
        self.vm.add_peripheral('orderbook', OrderBook('orderbook', 0x40130100))
        self.vm.add_peripheral('trader', TradeExecutor('trader', 0x40230000))
        self.vm.add_peripheral('risk', RiskEngine('risk', 0x40230100))

        self.state = {
            'price': 100.0, 'bid': 99.95, 'ask': 100.05,
            'volume': 0, 'pnl': 0.0, 'position': 0,
            'var_95': 0.0, 'volatility': 0.02,
            'high': 100.0, 'low': 100.0, 'open': 100.0,
            'spread': 0.10, 'scenario': '',
        }

    def load_scenario(self, name: str):
        if name in self.SCENARIOS:
            self.scenario = name
            self._scenario_step = 0
            self.state['scenario'] = name
            cfg = self.SCENARIOS[name]
            market = self.vm.peripherals.get('market')
            if market and 'volatility' in cfg:
                market.volatility = cfg['volatility']
            if market and 'drift' in cfg:
                market._drift = cfg['drift']

    def tick(self):
        self.tick_count += 1
        for name, dev in self.vm.peripherals.items():
            if hasattr(dev, 'simulate_tick'):
                dev.simulate_tick()

        self._apply_scenario()

        market = self.vm.peripherals.get('market')
        orderbook = self.vm.peripherals.get('orderbook')
        trader = self.vm.peripherals.get('trader')
        risk = self.vm.peripherals.get('risk')

        if market:
            self.state['price'] = round(market.price, 4)
            self.state['bid'] = round(market.bid, 4)
            self.state['ask'] = round(market.ask, 4)
            self.state['volume'] = market.volume
            self.state['high'] = max(self.state['high'], market.price)
            self.state['low'] = min(self.state['low'], market.price)

        if orderbook:
            self.state['spread'] = round(orderbook.spread, 4)

        if trader:
            self.state['position'] = trader.position_qty
            cost_basis = trader.avg_fill_price * abs(trader.position_qty)
            market_val = market.price * abs(trader.position_qty) if market else 0
            self.state['pnl'] = round(market_val - cost_basis, 2) if trader.position_qty != 0 else 0

        if risk:
            self.state['var_95'] = round(risk.current_var, 2)

        returns = []
        if market and market.price > 0 and self.state['open'] > 0:
            ret = (market.price - self.state['open']) / self.state['open']
            self.state['volatility'] = round(abs(ret) * math.sqrt(252), 4)

        self._scenario_step += 1

    def _apply_scenario(self):
        if not self.scenario:
            return
        cfg = self.SCENARIOS.get(self.scenario, {})
        market = self.vm.peripherals.get('market')

        if self.scenario == 'flash_crash':
            crash_tick = cfg.get('crash_tick', 100)
            if self._scenario_step == crash_tick and market:
                crash_pct = cfg.get('crash_pct', -0.15)
                market.price *= (1 + crash_pct)
            elif self._scenario_step > crash_tick + 50 and market:
                market._drift = 0.002

        elif self.scenario == 'earnings_report':
            event_tick = cfg.get('event_tick', 50)
            if self._scenario_step == event_tick and market:
                gap_pct = cfg.get('gap_pct', 0.08)
                market.price *= (1 + gap_pct)
                market.volatility = cfg.get('volatility', 0.03)

    def get_state(self) -> dict:
        return dict(self.state)

    def get_peripherals(self) -> dict:
        return dict(self.vm.peripherals)

    def get_status_text(self) -> str:
        scn = f" [{self.scenario}]" if self.scenario else ""
        return f"{self.DISPLAY_NAME} | Tick {self.tick_count}{scn}"

    def reset(self):
        self.tick_count = 0
        self.state = {}
        self.scenario = ''
        self._scenario_step = 0
