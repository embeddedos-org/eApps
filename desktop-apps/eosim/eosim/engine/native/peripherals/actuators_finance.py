# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""Finance domain actuators — trade executor, risk engine."""
import random

from eosim.engine.native.peripherals.actuators import ActuatorBase


class TradeExecutor(ActuatorBase):
    """Trade execution actuator — submit/cancel orders."""

    def __init__(self, name: str = 'trader0', base_addr: int = 0x40230000):
        super().__init__(name, base_addr)
        self.orders_submitted = 0
        self.orders_filled = 0
        self.orders_cancelled = 0
        self.position_qty = 0
        self.avg_fill_price = 0.0
        self.pnl = 0.0
        self._pending_orders = []

    def simulate_tick(self):
        filled = []
        for order in self._pending_orders:
            if random.random() < 0.8:
                self.orders_filled += 1
                qty = order.get('qty', 0)
                price = order.get('price', 100.0) * (1 + random.gauss(0, 0.001))
                if order.get('side') == 'buy':
                    self.position_qty += qty
                else:
                    self.position_qty -= qty
                self.avg_fill_price = price
                filled.append(order)
        for o in filled:
            self._pending_orders.remove(o)

    def submit_order(self, side: str, qty: int, price: float):
        self._pending_orders.append({'side': side, 'qty': qty, 'price': price})
        self.orders_submitted += 1

    def read_reg(self, offset: int) -> int:
        if offset == 0x00:
            return self.orders_submitted & 0xFFFFFFFF
        elif offset == 0x04:
            return self.orders_filled & 0xFFFFFFFF
        elif offset == 0x08:
            return self.position_qty & 0xFFFFFFFF
        elif offset == 0x0C:
            return int(self.avg_fill_price * 10000) & 0xFFFFFFFF
        return 0

    def write_reg(self, offset: int, val: int):
        if offset == 0x00:
            self.submit_order('buy', val, 100.0)
        elif offset == 0x04:
            self.submit_order('sell', val, 100.0)


class RiskEngine(ActuatorBase):
    """Risk management engine — position limits, VaR thresholds."""

    def __init__(self, name: str = 'risk0', base_addr: int = 0x40230100):
        super().__init__(name, base_addr)
        self.max_position = 10000
        self.var_limit = 50000.0
        self.current_var = 0.0
        self.risk_breach = False
        self.margin_used_pct = 0.0

    def simulate_tick(self):
        self.current_var += random.gauss(0, 100)
        self.current_var = max(0, self.current_var)
        self.risk_breach = self.current_var > self.var_limit
        self.margin_used_pct = min(100, self.current_var / self.var_limit * 100) if self.var_limit > 0 else 0

    def read_reg(self, offset: int) -> int:
        if offset == 0x00:
            return int(self.current_var * 100) & 0xFFFFFFFF
        elif offset == 0x04:
            return int(self.risk_breach)
        elif offset == 0x08:
            return int(self.margin_used_pct * 100) & 0xFFFFFFFF
        return 0

    def write_reg(self, offset: int, val: int):
        if offset == 0x00:
            self.max_position = val
        elif offset == 0x04:
            self.var_limit = val / 100.0
