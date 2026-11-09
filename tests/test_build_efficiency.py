"""
Unit tests for the Build Efficiency and Total Equivalent Karma (TEK) engine.
"""

import pytest
from sr6core.creation.efficiency import (
    calculate_triangular_attribute,
    calculate_attribute_delta_karma,
    calculate_triangular_skill,
    calculate_build_efficiency,
)


def test_triangular_cost_formulas():
    assert calculate_triangular_attribute(1) == 0
    assert calculate_triangular_attribute(2) == 10
    assert calculate_triangular_attribute(5) == 70
    assert calculate_triangular_attribute(6) == 100
    assert calculate_triangular_attribute(10) == 270

    # Attribute delta
    assert calculate_attribute_delta_karma(1, 7) == 135
    assert calculate_attribute_delta_karma(6, 9) == 120

    # Skills
    assert calculate_triangular_skill(1) == 5
    assert calculate_triangular_skill(6) == 105
    assert calculate_triangular_skill(6, specs=1) == 110
    assert calculate_triangular_skill(7) == 140


def test_efficiency_evaluations_reiko_velvet():
    r_res = calculate_build_efficiency("reiko")
    assert r_res["tek"] >= 1100
    assert r_res["obs"]["total"] == 8
    assert r_res["unspent"]["cash"] == 90000
    assert not r_res["is_complete"]  # Excess pocket cash

    v_res = calculate_build_efficiency("velvet")
    assert v_res["tek"] >= 1500
    assert v_res["obs"]["total"] == 9
    assert v_res["breakdown"]["sustained_spells_dividend"] == 500  # CHA 14, WIL 9, 4D6 Reflexes
    assert v_res["unspent"]["cash"] <= 5000
    assert v_res["is_complete"]


def test_efficiency_evaluations_lab():
    vn_res = calculate_build_efficiency("venn")
    assert vn_res["tek"] >= 1800
    assert vn_res["obs"]["total"] == 7
    assert vn_res["breakdown"]["ware_attr_delta"] >= 300
    assert vn_res["unspent"]["contact_points"] == 0
    assert vn_res["is_complete"]  # Contacts allocated to Parnell & Dr. Ortiz

    ouro_res = calculate_build_efficiency("ouro")
    assert ouro_res["tek"] >= 1900
    assert ouro_res["obs"]["total"] == 11
    assert ouro_res["is_complete"]

    dal_res = calculate_build_efficiency("dalakitnon_adept")
    assert dal_res["tek"] >= 1300
    assert dal_res["obs"]["total"] == 13
    assert dal_res["obs"]["active_planes"] == 4  # 4/4 Planes Active
    assert dal_res["breakdown"]["sustained_spells_dividend"] == 420  # LOG 12, INT 7, 4D6 Reflexes
    assert dal_res["unspent"]["cash"] == 3575
    assert dal_res["is_complete"]  # Low Lifestyle prepaid (2,000¥), compliant with <= 5,000¥ limit

