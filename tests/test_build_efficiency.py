"""
Unit tests for the Build Efficiency, 20-Point OBS, and Session 4 Checkpoint engine.
"""

from sr6core.creation.efficiency import (
    calculate_triangular_attribute,
    calculate_attribute_delta_karma,
    calculate_triangular_skill,
    calculate_build_efficiency,
    generate_lab_scorecard_markdown,
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
    assert r_res["tek"] >= 1300
    assert r_res["obs"]["max"] == 20
    assert r_res["obs"]["total"] == 10
    assert r_res["unspent"]["cash"] == 90000
    assert not r_res["is_complete"]  # Excess pocket cash

    v_res = calculate_build_efficiency("velvet")
    assert v_res["tek"] >= 1600
    assert v_res["obs"]["total"] == 13
    assert v_res["breakdown"]["sustained_spells_dividend"] == 650  # CHA 14, WIL 9, 4D6 Reflexes + Conjuring Engine
    assert v_res["unspent"]["cash"] <= 5000
    assert v_res["is_complete"]


def test_efficiency_evaluations_lab():
    vn_res = calculate_build_efficiency("venn")
    assert 1900 <= vn_res["tek"] <= 2050  # De-duplicated 4-limb cyber-suite (340k ware delta)
    assert vn_res["obs"]["total"] == 14
    assert vn_res["obs"]["active_planes"] == 3
    assert not vn_res["obs"]["tactical"]["force_multiplication"]["met"]
    assert vn_res["breakdown"]["ware_attr_delta"] == 340
    assert vn_res["unspent"]["contact_points"] == 0
    assert vn_res["session4"]["tek"] >= 2100
    assert vn_res["is_complete"]

    ouro_res = calculate_build_efficiency("ouro")
    assert ouro_res["tek"] >= 2250
    assert ouro_res["obs"]["total"] == 15
    assert ouro_res["obs"]["active_planes"] == 3
    assert not ouro_res["obs"]["tactical"]["force_multiplication"]["met"]  # Single body Day 1
    assert ouro_res["session4"]["tek"] >= 2500
    assert ouro_res["is_complete"]

    ashe_res = calculate_build_efficiency("AshE")
    assert ashe_res["tek"] >= 2100
    assert ashe_res["obs"]["total"] == 14
    assert ashe_res["obs"]["tactical"]["force_multiplication"]["met"]  # Twin Silverstar Day 1
    assert ashe_res["session4"]["obs_total"] == 15
    assert ashe_res["session4"]["active_planes"] == 3
    assert ashe_res["session4"]["tek"] >= 2400
    assert ashe_res["is_complete"]

    # Alias compatibility for AshE / etain
    assert calculate_build_efficiency("etain")["tek"] == ashe_res["tek"]
    assert calculate_build_efficiency("ashe")["tek"] == ashe_res["tek"]

    dal_res = calculate_build_efficiency("mad_dalek")
    assert dal_res["tek"] >= 1700
    assert dal_res["obs"]["total"] == 17
    assert dal_res["obs"]["active_planes"] == 4
    assert dal_res["breakdown"]["sustained_spells_dividend"] == 570  # LOG 12, INT 7, 4D6 Reflexes + Conjuring Engine
    assert dal_res["unspent"]["cash"] == 3575
    assert dal_res["unspent"]["karma"] == 5
    assert dal_res["session4"]["tek"] >= 1800
    assert dal_res["is_complete"]

    # Backward compatibility alias test
    dal_res_alias = calculate_build_efficiency("dalakitnon_adept")
    assert dal_res_alias["tek"] == dal_res["tek"]


def test_generate_lab_scorecard_markdown(tmp_path):
    out_file = tmp_path / "scorecard.md"
    md = generate_lab_scorecard_markdown(output_path=out_file)
    assert out_file.exists()
    for name in ["Ouro", "Venn", "AshE", "MAD Dalek", "Velvet", "Yuriko Star"]:
        assert name in md
    for cid in ["ouro", "venn", "AshE", "mad_dalek", "velvet", "reiko"]:
        assert f"`{cid}`" in md
    assert "Day-1 vs. Session 4 Mulligan Scorecard" in md
    assert "8-Dimension Capability Matrix" in md
    assert "Data-Driven TEK Karma Breakdown Ledger" in md
