"""Unit tests for the simulation engine — blocks, model assembly, signal generation."""

from __future__ import annotations

import math
import unittest

from eostudio.core.simulation.engine import (
    SimulationModel, Block, SourceBlock, GainBlock, SumBlock,
    PIDBlock, ScopeBlock, Signal,
)


class TestSignal(unittest.TestCase):
    def test_empty_signal(self) -> None:
        sig = Signal(name="test")
        self.assertEqual(sig.num_samples(), 0)

    def test_add_sample(self) -> None:
        sig = Signal(name="test")
        sig.add_sample(0.0, 1.0)
        sig.add_sample(0.1, 2.0)
        self.assertEqual(sig.num_samples(), 2)

    def test_mean(self) -> None:
        sig = Signal(name="test")
        for v in [1.0, 2.0, 3.0, 4.0]:
            sig.add_sample(0.0, v)
        self.assertAlmostEqual(sig.mean(), 2.5)

    def test_rms(self) -> None:
        sig = Signal(name="dc")
        for _ in range(10):
            sig.add_sample(0.0, 3.0)
        self.assertAlmostEqual(sig.rms(), 3.0)


class TestSourceBlock(unittest.TestCase):
    def test_step_signal(self) -> None:
        block = SourceBlock(block_id="src", name="Step", signal_type="step",
                            amplitude=1.0, frequency=0.0)
        output = block.compute(0.0, 0.5, [])
        self.assertAlmostEqual(output, 0.0)
        output = block.compute(0.0, 1.5, [])
        self.assertAlmostEqual(output, 1.0)

    def test_sine_signal(self) -> None:
        block = SourceBlock(block_id="src", name="Sine", signal_type="sine",
                            amplitude=2.0, frequency=1.0)
        output = block.compute(0.0, 0.25, [])
        self.assertAlmostEqual(output, 2.0 * math.sin(2 * math.pi * 0.25), places=4)

    def test_constant_signal(self) -> None:
        block = SourceBlock(block_id="src", name="Const", signal_type="constant",
                            amplitude=5.0, frequency=0.0)
        output = block.compute(0.0, 0.0, [])
        self.assertAlmostEqual(output, 5.0)


class TestGainBlock(unittest.TestCase):
    def test_gain(self) -> None:
        block = GainBlock(block_id="g", name="Gain", gain=3.0)
        output = block.compute(0.0, 0.0, [2.0])
        self.assertAlmostEqual(output, 6.0)

    def test_zero_gain(self) -> None:
        block = GainBlock(block_id="g", name="Zero", gain=0.0)
        output = block.compute(0.0, 0.0, [100.0])
        self.assertAlmostEqual(output, 0.0)


class TestSumBlock(unittest.TestCase):
    def test_addition(self) -> None:
        block = SumBlock(block_id="s", name="Sum", signs=["+", "+"])
        output = block.compute(0.0, 0.0, [3.0, 4.0])
        self.assertAlmostEqual(output, 7.0)

    def test_subtraction(self) -> None:
        block = SumBlock(block_id="s", name="Diff", signs=["+", "-"])
        output = block.compute(0.0, 0.0, [10.0, 3.0])
        self.assertAlmostEqual(output, 7.0)


class TestPIDBlock(unittest.TestCase):
    def test_proportional_only(self) -> None:
        block = PIDBlock(block_id="pid", name="P", Kp=2.0, Ki=0.0, Kd=0.0)
        output = block.compute(0.01, 0.0, [5.0])
        self.assertAlmostEqual(output, 10.0)

    def test_integral_accumulates(self) -> None:
        block = PIDBlock(block_id="pid", name="PI", Kp=0.0, Ki=1.0, Kd=0.0)
        block.compute(0.1, 0.0, [1.0])
        output = block.compute(0.1, 0.1, [1.0])
        self.assertGreater(output, 0.0)

    def test_reset(self) -> None:
        block = PIDBlock(block_id="pid", name="PID", Kp=1.0, Ki=1.0, Kd=1.0)
        block.compute(0.01, 0.0, [1.0])
        block.reset()
        self.assertAlmostEqual(block._integral, 0.0)


class TestScopeBlock(unittest.TestCase):
    def test_records_signal(self) -> None:
        block = ScopeBlock(block_id="scope", name="Out")
        block.compute(0.01, 0.0, [1.5])
        block.compute(0.01, 0.01, [2.5])
        self.assertEqual(len(block.signal.values), 2)


class TestSimulationModel(unittest.TestCase):
    def test_empty_model(self) -> None:
        model = SimulationModel()
        model.dt = 0.01
        model.duration = 0.1
        results = model.run()
        self.assertIsInstance(results, dict)

    def test_simple_chain(self) -> None:
        model = SimulationModel()
        model.dt = 0.01
        model.duration = 1.0
        src = SourceBlock(block_id="src", name="Step", signal_type="step",
                          amplitude=1.0, frequency=0.0)
        gain = GainBlock(block_id="g", name="Gain", gain=2.0)
        scope = ScopeBlock(block_id="scope", name="Out")
        model.add_block(src)
        model.add_block(gain)
        model.add_block(scope)
        model.connect("src", "g")
        model.connect("g", "scope")
        results = model.run()
        self.assertIn("Out", results)
        self.assertGreater(results["Out"].num_samples(), 0)


if __name__ == "__main__":
    unittest.main()
