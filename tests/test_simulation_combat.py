"""
Test suite for SR6 Combat & Magic Simulation Engine.
Verifies AR vs DR Edge advantage math, opposed attack tests, damage calculation,
and spell drain / technomancer fading resistance.
"""

from sr6core.simulation.combat import CombatResolver
from sr6core.simulation.matrix_magic import resolve_drain_test, resolve_matrix_action


def test_compare_ar_dr_edge():
    # Attacker AR 12 vs Defender DR 8 -> Diff = 4 -> Attacker gains 1 Edge
    att_edge, def_edge = CombatResolver.compare_ar_dr(12, 8)
    assert att_edge == 1
    assert def_edge == 0

    # Attacker AR 6 vs Defender DR 10 -> Diff = -4 -> Defender gains 1 Edge
    att_edge, def_edge = CombatResolver.compare_ar_dr(6, 10)
    assert att_edge == 0
    assert def_edge == 1

    # Attacker AR 10 vs Defender DR 8 -> Diff = 2 -> No Edge gained
    att_edge, def_edge = CombatResolver.compare_ar_dr(10, 8)
    assert att_edge == 0
    assert def_edge == 0


def test_resolve_combat_attack():
    res = CombatResolver.resolve_attack(
        attacker_pool=14,
        defender_pool=8,
        base_dv=4,
        soak_pool=10,
        damage_type="P",
        attacker_name="Yuriko",
        defender_name="Renraku Red Samurai",
        weapon_name="Ares Predator VI",
        attacker_ar=12,
        defender_dr=8,
    )

    assert res.attacker_name == "Yuriko"
    assert res.base_dv == 4
    assert res.attacker_edge_gained == 1
    assert res.damage_type == "P"
    assert res.attack_roll.pool == 14
    assert res.defense_roll.pool == 8
    assert res.net_hits == res.attack_roll.hits - res.defense_roll.hits

    if res.is_hit:
        assert res.modified_dv == 4 + res.net_hits
        assert res.soak_roll is not None
        assert res.damage_inflicted == max(0, res.modified_dv - res.soak_roll.hits)
    else:
        assert res.damage_inflicted == 0


def test_resolve_drain_test():
    # Test Fading DV 4 against pool 12
    res = resolve_drain_test(drain_value=4, resistance_pool=12, test_type="Fading")
    assert res.drain_value == 4
    assert res.test_type == "Fading"
    assert res.drain_taken == max(0, 4 - res.resistance_roll.hits)
