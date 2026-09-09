"""
Unit tests for the Rules Accessibility Suite:
- Sourcebook Explorer (sr6 source)
- PACKs Catalog & Card Generator (sr6 card pack)
- Cyberlimb & Ware Calculator (sr6 calc)
- Tabletop Rules Cheatsheets (sr6 cheat)
- Native MCP Server Tools Integration
"""

import pytest
from sr6core.source_explorer import resolve_book_file, search_source_book, format_source_results
from sr6core.packs_catalog import parse_6wc_packs, compile_packs_to_db, get_pack, format_pack_card
from sr6core.calculator import calculate_cyberlimb, calculate_ware, format_limb_calculation, format_ware_calculation
from sr6core.cheatsheets import get_cheatsheet, list_cheatsheets, format_cheatsheets_index
from sr6core.mcp import TOOLS_DEFINITIONS, TOOL_HANDLERS


def test_source_explorer_book_resolution():
    p, name = resolve_book_file("6wc")
    assert p is not None
    assert "Sixth_World_Companion" in name

    p, name = resolve_book_file("bs")
    assert p is not None
    assert "Body_Shop" in name

    p, name = resolve_book_file("crb")
    assert p is not None
    assert "Seattle" in name


def test_source_explorer_search():
    res = search_source_book("6wc", "Cyberarm: Excellence", context_lines=4)
    assert "error" not in res
    assert res["total_matches"] > 0
    formatted = format_source_results(res)
    assert "Cyberarm: Excellence" in formatted


def test_packs_catalog_parse_and_get():
    packs = parse_6wc_packs()
    assert len(packs) > 10
    names = [p["name"] for p in packs]
    assert any("Excellence" in n for n in names)

    # Test retrieval from ref_packs table
    pack = get_pack("Cyberarm: Excellence")
    assert pack is not None
    assert pack["cost"] == 60000
    assert pack["essence"] == 1.0
    assert "used" in pack["alternate_grades"]
    assert pack["alternate_grades"]["used"]["cost"] == 30000

    card_md = format_pack_card(pack)
    assert "[PACK]" in card_md
    assert "60,000¥" in card_md
    assert "Used" in card_md


def test_cyberlimb_calculator_standard_arm():
    calc = calculate_cyberlimb(limb="cyberarm", synthetic=True, grade="standard", agi_enhancement=2)
    assert calc["limb"] == "Cyberarm"
    assert calc["final_essence"] == 1.0
    assert calc["total_cost"] == 25000  # 20k base + 5k (2x 2500 agi)
    assert calc["total_capacity"] == 8
    assert calc["used_capacity"] == 2
    assert calc["free_capacity"] == 6
    assert calc["is_legal_capacity"] is True
    assert calc["resulting_attributes"]["agility"] == 4


def test_cyberlimb_calculator_used_adapsin_with_bulk():
    # Synthetic Cyberleg, Used grade (0.5x cost, 1.1x ess), Adapsin (0.9x ess), Bulk R4 (+4 Cap, 4k cost)
    calc = calculate_cyberlimb(
        limb="cyberleg",
        synthetic=True,
        grade="used",
        adapsin=True,
        agi_enhancement=4,
        bulk_mod=4
    )
    assert calc["final_essence"] == 0.99  # 1.0 * 1.1 * 0.9 = 0.99
    assert calc["limb_shell_cost"] == 10000  # 20k * 0.5
    assert calc["bulk_mod_cost"] == 4000
    assert calc["enhancements_cost"] == 10000  # 4 * 2500
    assert calc["total_cost"] == 24000
    assert calc["total_capacity"] == 14  # 10 base + 4 bulk
    assert calc["used_capacity"] == 4
    assert calc["free_capacity"] == 10


def test_cyberlimb_calculator_over_capacity():
    calc = calculate_cyberlimb(
        limb="cyberarm",
        synthetic=True,
        agi_enhancement=4,
        str_enhancement=4,
        armor_enhancement=2  # Total 10 cap, base synth arm has 8
    )
    assert calc["total_capacity"] == 8
    assert calc["used_capacity"] == 10
    assert calc["free_capacity"] == -2
    assert calc["is_legal_capacity"] is False
    rep = format_limb_calculation(calc)
    assert "OVER CAPACITY" in rep


def test_ware_calculator():
    # Bone density augmentation (bioware) - Adapsin exempt
    calc = calculate_ware("Bone Density R4", base_cost=30000, base_essence=1.20, grade="betaware", is_bioware=True, adapsin=True)
    assert calc["final_cost"] == 45000  # 30k * 1.5
    assert calc["final_essence"] == 0.84  # 1.2 * 0.7 = 0.84 (Adapsin not applied to bioware)
    assert calc["adapsin_warning"] is not None

    # Cyberware - Adapsin applied
    calc_cyber = calculate_ware("Skilljack R6", base_cost=60000, base_essence=0.60, grade="used", is_bioware=False, adapsin=True)
    assert calc_cyber["final_cost"] == 30000  # 60k * 0.5
    assert calc_cyber["final_essence"] == 0.59  # 0.6 * 1.1 * 0.9 = 0.594 -> 0.59
    assert calc_cyber["adapsin_applied"] is True


def test_cheatsheets():
    sheets = list_cheatsheets()
    assert len(sheets) == 4
    topics = [s["topic"] for s in sheets]
    assert "matrix" in topics
    assert "actions" in topics
    assert "monad" in topics
    assert "combat" in topics

    m = get_cheatsheet("matrix")
    assert "ASDF" in m["content"]
    assert "Full Matrix Defense" in m["content"]

    idx = format_cheatsheets_index()
    assert "**`matrix`**" in idx


def test_mcp_server_new_tools():
    tool_names = [t["name"] for t in TOOLS_DEFINITIONS]
    assert "sr6_query_db" in tool_names
    assert "sr6_get_schema" in tool_names
    assert "sr6_source_search" in tool_names
    assert "sr6_calculate_limb" in tool_names
    assert "sr6_get_cheatsheet" in tool_names

    for name in ["sr6_query_db", "sr6_get_schema", "sr6_source_search", "sr6_calculate_limb", "sr6_get_cheatsheet"]:
        assert name in TOOL_HANDLERS

    # Test executing handler directly
    res = TOOL_HANDLERS["sr6_get_cheatsheet"]({"topic": "actions"})
    assert "Action Economy" in res
    assert "Turn-Start" in res

    calc_res = TOOL_HANDLERS["sr6_calculate_limb"]({"limb": "cyberarm", "agi_enhancement": 4, "grade": "used", "adapsin": True})
    assert "0.99" in calc_res
    assert "Agility 6" in calc_res
