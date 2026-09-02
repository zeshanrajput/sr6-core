"""
Test suite for SR6 Dice Simulation Engine.
Verifies d6 statistical boundaries, Rule of Six exploding dice, bought hits,
Glitch & Critical Glitch detection, and Edge reroll maneuvers.
"""

import random
import pytest
from sr6core.simulation.dice import roll_pool, apply_edge_reroll_failures, DiceRollResult


def test_roll_pool_empty():
    res = roll_pool(0)
    assert res.pool == 0
    assert len(res.dice) == 0
    assert res.hits == 0
    assert res.is_glitch is False


def test_buy_hits():
    res = roll_pool(15, buy_hits=True)
    assert res.hits == 3  # 15 // 4 = 3
    assert res.bought_hits == 3
    assert len(res.dice) == 0

    res2 = roll_pool(16, buy_hits=True)
    assert res2.hits == 4


def test_glitch_detection():
    # Mock RNG that produces four 1s and one 5 (pool = 5)
    class GlitchRNG:
        def __init__(self):
            self.vals = [1, 1, 1, 1, 5]
            self.idx = 0

        def randint(self, a, b):
            val = self.vals[self.idx % len(self.vals)]
            self.idx += 1
            return val

    res = roll_pool(5, rng=GlitchRNG())
    assert res.hits == 1
    assert res.ones == 4
    assert res.is_glitch is True
    assert res.is_critical_glitch is False


def test_critical_glitch_detection():
    # Mock RNG that produces all 1s
    class CritGlitchRNG:
        def randint(self, a, b):
            return 1

    res = roll_pool(6, rng=CritGlitchRNG())
    assert res.hits == 0
    assert res.ones == 6
    assert res.is_glitch is True
    assert res.is_critical_glitch is True


def test_exploding_rule_of_six():
    # Mock RNG: 6 followed by 6 followed by 5 (3 hits from 1 initial die)
    class ExplodeRNG:
        def __init__(self):
            self.seq = [6, 6, 5]
            self.idx = 0

        def randint(self, a, b):
            val = self.seq[self.idx]
            self.idx += 1
            return val

    res = roll_pool(1, is_exploding=True, rng=ExplodeRNG())
    assert res.hits == 3
    assert len(res.dice) == 3
    assert res.dice == [6, 6, 5]


def test_edge_reroll_failures():
    # Initial roll with 2 hits (5, 6) and 2 failures (2, 3)
    init_res = DiceRollResult(
        pool=4,
        dice=[5, 6, 2, 3],
        hits=2,
        ones=0,
        is_glitch=False,
        is_critical_glitch=False,
    )

    class FixedRNG:
        def __init__(self):
            self.seq = [5, 6]  # Both rerolled dice hit
            self.idx = 0

        def randint(self, a, b):
            val = self.seq[self.idx]
            self.idx += 1
            return val

    rerolled = apply_edge_reroll_failures(init_res, rng=FixedRNG())
    assert rerolled.hits == 4
    assert len(rerolled.dice) == 4
    assert rerolled.edge_spent == 1
