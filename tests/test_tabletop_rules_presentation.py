"""
Unit tests for Tabletop Rules Presentation:
- Contextual Direct & Indirect Combat Spells with Amp Up and Increased Area modifiers
- SRM Matrix actions categorized strictly by Skill and Specialization
- Deterministic Downtime Spirit Binding & Sprite Registration under SRM Buying Hits rules
"""

import pytest
from sr6core.cards import get_item_card
from sr6core.rules_matrix_actions import (
    calculate_matrix_action_pool,
    render_matrix_actions_markdown,
    SRM_MATRIX_TAXONOMY
)
from sr6core.rules_conjuring_tables import (
    calculate_downtime_binding_table,
    render_downtime_binding_markdown
)


def test_spell_card_direct_combat_rules():
    card = get_item_card("spell", "Manabolt")
    md = card["markdown"]
    assert "Direct Combat Spell" in md
    assert "Sorcery + Magic" in md
    assert "Willpower + Intuition" in md
    assert "NOT resisted" in md
    assert "`+1 Damage Value (DV)` costs `+2 Drain Value (DV)`" in md


def test_spell_card_indirect_combat_rules():
    card = get_item_card("spell", "Fireball")
    md = card["markdown"]
    assert "Indirect Combat Spell" in md
    assert "Sorcery + Magic" in md
    assert "Reaction + Willpower" in md
    assert "Resisted with **Body**" in md
    assert "`+1 Damage Value (DV)` costs `+2 Drain Value (DV)`" in md
    assert "`+2 meters radius` costs `+1 Drain Value (DV)`" in md


def test_matrix_actions_srm_taxonomy():
    skills = [g["skill"] for g in SRM_MATRIX_TAXONOMY]
    assert "Electronics" in skills
    assert "Cracking" in skills

    specs = [g["specialization"] for g in SRM_MATRIX_TAXONOMY]
    assert "Computer" in specs
    assert "Software" in specs
    assert "Hardware" in specs
    assert "Hacking" in specs
    assert "Cybercombat" in specs


def test_matrix_actions_pool_calculation():
    # Test character with Cracking 6, Logic 6, Specialization Hacking
    char_data = {
        "attributes": {"logic": 6, "intuition": 5, "willpower": 5},
        "skills": [
            {
                "name": "Cracking",
                "rating": 6,
                "specializations": [{"name": "Hacking", "expertise": False}]
            },
            {
                "name": "Electronics",
                "rating": 5,
                "specializations": []
            }
        ]
    }

    # Hack on the Fly (Cracking: Hacking) -> 6 + 6 + 2 = 14d6
    res_hack = calculate_matrix_action_pool(char_data, "Cracking", "Hacking", "logic")
    assert res_hack["pool"] == 14
    assert res_hack["tier"] == "Specialized (+2d)"
    assert res_hack["bonus_dice"] == 2

    # Data Spike (Cracking: Cybercombat) -> 6 + 6 + 0 = 12d6
    res_spike = calculate_matrix_action_pool(char_data, "Cracking", "Cybercombat", "logic")
    assert res_spike["pool"] == 12
    assert res_spike["tier"] == "Base Skill"
    assert res_spike["bonus_dice"] == 0

    # Matrix Perception (Electronics: Computer) -> 5 + 5 + 0 = 10d6
    res_perc = calculate_matrix_action_pool(char_data, "Electronics", "Computer", "intuition")
    assert res_perc["pool"] == 10
    assert res_perc["tier"] == "Base Skill"


def test_downtime_binding_table_buying_hits_exact_cutoffs():
    # Runner with pool 12 (Bought hits = 3)
    # Spirit Force 1 (pool 2, hits 0) -> Net 3
    # Spirit Force 2 (pool 4, hits 1) -> Net 2
    # Spirit Force 3 (pool 6, hits 1) -> Net 2
    # Spirit Force 4 (pool 8, hits 2) -> Net 1
    # Spirit Force 5 (pool 10, hits 2) -> Net 1
    # Spirit Force 6 (pool 12, hits 3) -> Net 0 (Cutoff!)
    res_12 = calculate_downtime_binding_table(12, entity_type="Sprite", pool_name="Tasking (Compiling)")
    assert res_12["pc_bought_hits"] == 3
    assert res_12["max_viable_force"] == 5
    assert len(res_12["rows"]) == 5
    assert res_12["rows"][0]["net_hits"] == 3
    assert res_12["rows"][4]["force"] == 5
    assert res_12["rows"][4]["net_hits"] == 1

    # Runner with pool 16 (Bought hits = 4)
    # Stops at Force 7 (Force 8 hits = 4 -> Net 0)
    res_16 = calculate_downtime_binding_table(16, entity_type="Spirit", pool_name="Conjuring (Summoning)")
    assert res_16["pc_bought_hits"] == 4
    assert res_16["max_viable_force"] == 7
    assert len(res_16["rows"]) == 7
    assert res_16["rows"][6]["force"] == 7
    assert res_16["rows"][6]["net_hits"] == 1

    # Check Markdown rendering
    md = render_downtime_binding_markdown(16, entity_type="Spirit", pool_name="Conjuring (Summoning)")
    assert "SRM Downtime Binding Table: Spirits" in md
    assert "Force 7" in md
    assert "Ceases at Force 8" in md


def test_render_weapon_card_red_fox():
    """Verifies that render_weapon_card correctly renders Firing Squad laser weapon cards like red_fox."""
    from sr6core.rules_engine import render_weapon_card
    card_md = render_weapon_card("red_fox")
    assert "rEVOlution Arms Red Fox" in card_md
    assert "6P" in card_md
    assert "14 / 16 / 16 / 9" in card_md
    assert "SA/BF" in card_md
    assert "30(c)" in card_md
    assert "Firing Squad" in card_md
