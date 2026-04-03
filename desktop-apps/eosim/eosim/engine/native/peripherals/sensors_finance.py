# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""Finance domain sensors — market feed, order book."""
import random
import math

from eosim.engine.native.peripherals.sensors import SensorBase


class MarketFeed(SensorBase):
    """Real-time market data feed — price, volume, bid/ask."""

    def __init__(self, name: str = 'market0', base_addr: int = 0x40130000):
        super().__init__(name, base_addr)
        self.price = 100.0
        self.bid = 99.95
        self.ask = 100.05
        self.volume = 0
        self.tick_count_feed = 0
        self.volatility = 0.02
        self._drift = 0.0001

    def simulate_tick(self):
        super().simulate_tick()
        self.tick_count_feed += 1
        ret = self._drift + self.volatility * random.gauss(0, 1) * 0.01
        self.price *= (1 + ret)
        self.price = max(0.01, self.price)
        spread = self.price * 0.001
        self.bid = self.price - spread / 2
        self.ask = self.price + spread / 2
        self.volume += random.randint(10, 500)

    def set_price(self, price: float):
        self.price = max(0.01, price)
        spread = self.price * 0.001
        self.bid = self.price - spread / 2
        self.ask = self.price + spread / 2

    def read_reg(self, offset: int) -> int:
        if offset == 0x00:
            return int(self.price * 10000) & 0xFFFFFFFF
        elif offset == 0x04:
            return int(self.bid * 10000) & 0xFFFFFFFF
        elif offset == 0x08:
            return int(self.ask * 10000) & 0xFFFFFFFF
        elif offset == 0x0C:
            return self.volume & 0xFFFFFFFF
        return 0


class OrderBook(SensorBase):
    """Order book depth sensor — top-of-book levels."""

    def __init__(self, name: str = 'orderbook0', base_addr: int = 0x40130100):
        super().__init__(name, base_addr)
        self.bid_levels = [(99.95, 100), (99.90, 200), (99.85, 150)]
        self.ask_levels = [(100.05, 120), (100.10, 180), (100.15, 90)]
        self.total_bid_volume = 450
        self.total_ask_volume = 390
        self.spread = 0.10

    def simulate_tick(self):
        super().simulate_tick()
        for i in range(len(self.bid_levels)):
            price, qty = self.bid_levels[i]
            qty = max(10, qty + random.randint(-20, 20))
            self.bid_levels[i] = (price, qty)
        for i in range(len(self.ask_levels)):
            price, qty = self.ask_levels[i]
            qty = max(10, qty + random.randint(-20, 20))
            self.ask_levels[i] = (price, qty)
        self.total_bid_volume = sum(q for _, q in self.bid_levels)
        self.total_ask_volume = sum(q for _, q in self.ask_levels)
        if self.bid_levels and self.ask_levels:
            self.spread = self.ask_levels[0][0] - self.bid_levels[0][0]

    def read_reg(self, offset: int) -> int:
        if offset == 0x00:
            return self.total_bid_volume & 0xFFFFFFFF
        elif offset == 0x04:
            return self.total_ask_volume & 0xFFFFFFFF
        elif offset == 0x08:
            return int(self.spread * 10000) & 0xFFFFFFFF
        return 0
