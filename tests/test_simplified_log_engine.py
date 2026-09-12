"""
Test suite for the simplified SR6 Quarto Character Log Engine.
Validates mission registry lookups, master contact resolution, dynamic mission rewards,
convenience tabletop helpers (lifestyle, work_for_the_people, bribe), database-driven
advancements (learn_complex_form, learn_spell), and character portfolio totals.
"""

import pytest
from sr6core.character.contacts import (
    get_contact,
    is_canonical_contact,
    parse_contact_types,
    infer_contact_types,
    search_contacts,
    format_contacts_table,
)
from sr6core.character.missions import get_mission, normalize_mission_code
from sr6core.character.ledger import (
    reset_log_state,
    init_character,
    mission,
    contact,
    work_for_the_people,
    work_for_the_man,
    bribe,
    lifestyle,
    learn_complex_form,
    learn_spell,
    add_sprite,
    add_spirit,
    get_log_totals,
    _GLOBAL_LOG_STATE,
)


def test_mission_registry_and_normalization():
    assert normalize_mission_code("SRM 2081-01") == "SRM.2081.01"
    assert normalize_mission_code("SRM.2081.01") == "SRM.2081.01"
    assert normalize_mission_code("CMP 2083-02") == "CMP.2083.02"
    assert normalize_mission_code("SMH 2083-01") == "SMH.2083.01"

    m = get_mission("SRM.2081.01")
    assert m is not None
    assert m["title"] == "Death of a Fixer"
    assert m["season"] == "2081"
    assert m["region"] == "SEA"
    assert m["type"] == "SRM"

    m2 = get_mission("SRM 2083-14")
    assert m2 is not None
    assert m2["title"] == "Deepest Roots"
    assert m2["region"] == "NOLA"


def test_contact_master_registry():
    c = get_contact("Brynne Taggart")
    assert c is not None
    assert c["connection"] == 4
    assert c["canonical"] is True
    assert c["region"] == "SEA"
    assert "Fixer" in c["job"]

    c2 = get_contact("Roanoke")
    assert c2 is not None
    assert c2["connection"] == 3
    assert c2["canonical"] is True
    assert c2["region"] == "NOLA"

    assert is_canonical_contact("Brynne Taggart") is True
    assert is_canonical_contact("Nonexistent NPC") is False

    # Check contact types
    assert "Criminal" in c["types"]
    assert "Street" in c["types"]
    assert c["types_str"] == "Criminal, Street"
    assert "Criminal" in c2["types"]
    assert "Matrix" in c2["types"]


def test_mission_helper_evaluation():
    reset_log_state()
    out = mission(
        "SRM.2081.01",
        karma=6,
        nuyen=8000,
        rep={"Seattle": 1},
        bribe=1000,
        expenses=500,
        difficulty="Normal",
        gm="Kira Capalu",
    )

    assert "SRM.2081.01" in out
    assert "Death of a Fixer" in out
    assert _GLOBAL_LOG_STATE["Karma"] == 6
    assert _GLOBAL_LOG_STATE["Lifetime_Karma"] == 6
    # Liquid nuyen: 8000 - 1000 - 500 = 6500
    assert _GLOBAL_LOG_STATE["Nuyen"] == 6500
    # Gross lifetime nuyen: 8000
    assert _GLOBAL_LOG_STATE["Lifetime_Nuyen"] == 8000
    assert _GLOBAL_LOG_STATE["Reputation"]["Seattle"] == 1
    assert len(_GLOBAL_LOG_STATE["Session_Logs"]) == 1
    assert "SRM.2081.01 | Death of a Fixer" in _GLOBAL_LOG_STATE["Session_Logs"][0]["title"]


def test_tabletop_helpers():
    reset_log_state()
    _GLOBAL_LOG_STATE["Karma"] = 10
    _GLOBAL_LOG_STATE["Lifetime_Karma"] = 10
    _GLOBAL_LOG_STATE["Nuyen"] = 10000
    _GLOBAL_LOG_STATE["Lifetime_Nuyen"] = 10000
    _GLOBAL_LOG_STATE["Heat"] = 2

    # Work for the people (unfunded: 2,000 Nuyen -> 1 Karma)
    wftp = work_for_the_people()
    assert "+1 Karma" in wftp
    assert _GLOBAL_LOG_STATE["Karma"] == 11
    assert _GLOBAL_LOG_STATE["Lifetime_Karma"] == 11
    assert _GLOBAL_LOG_STATE["Nuyen"] == 8000

    # Work for the people (funded / Hooder edge)
    wftp_funded = work_for_the_people(funded=True)
    assert "Funded" in wftp_funded
    assert _GLOBAL_LOG_STATE["Karma"] == 12
    assert _GLOBAL_LOG_STATE["Nuyen"] == 8000

    # Work for the man (1 Karma -> 2,000 Nuyen)
    wftm = work_for_the_man()
    assert "+2,000" in wftm
    assert _GLOBAL_LOG_STATE["Karma"] == 11
    assert _GLOBAL_LOG_STATE["Nuyen"] == 10000

    # Bribe to reduce heat
    b_out = bribe(amount=2000, heat_reduced=1)
    assert "Bribe" in b_out
    assert _GLOBAL_LOG_STATE["Nuyen"] == 8000
    assert _GLOBAL_LOG_STATE["Heat"] == 1

    # Lifestyle payment (Middle default is 5,000¥: 8,000 - 5,000 = 3,000¥)
    ls_out = lifestyle("Middle")
    assert "Middle" in ls_out
    assert _GLOBAL_LOG_STATE["Nuyen"] == 3000


def test_database_driven_advancement():
    reset_log_state()
    _GLOBAL_LOG_STATE["Karma"] = 20

    # Learn complex form from ref_complex_forms
    cf_out = learn_complex_form("Resonance Wires")
    assert "Resonance Wires" in cf_out
    assert _GLOBAL_LOG_STATE["Karma"] == 15
    assert any(cf["name"] == "Resonance Wires" for cf in _GLOBAL_LOG_STATE["Complex_Forms"])

    # Learn spell from ref_spells
    sp_out = learn_spell("Heal")
    assert "Heal" in sp_out
    assert _GLOBAL_LOG_STATE["Karma"] == 10
    assert any(sp["name"] == "Heal" for sp in _GLOBAL_LOG_STATE["Spells"])


def test_simplified_sprites_and_spirits():
    reset_log_state()
    sp_out = add_sprite("Modular", level=7, count=2)
    assert "Modular" in sp_out
    assert "Rating 7" in sp_out
    assert len(_GLOBAL_LOG_STATE["Sprites"]) == 2

    spirit_out = add_spirit("Fire", force=6, tasks=3, count=1)
    assert "Spirit of Fire" in spirit_out
    assert "Force 6" in spirit_out
    assert len(_GLOBAL_LOG_STATE["Spirits"]) == 1


def test_character_portfolio_totals_exact_match():
    # Verify all 3 characters compile to their exact expected totals
    venn = get_log_totals("characters/venn")
    assert venn["Karma"] == 3
    assert venn["Lifetime_Karma"] == 3
    assert venn["Nuyen"] == 570
    assert venn["Lifetime_Nuyen"] == 570

    velvet = get_log_totals("characters/velvet")
    assert velvet["Karma"] == 17
    assert velvet["Lifetime_Karma"] == 55
    assert velvet["Nuyen"] == 565
    assert velvet["Lifetime_Nuyen"] == 117590

    reiko = get_log_totals("characters/reiko")
    assert reiko["Karma"] == 0
    assert reiko["Lifetime_Karma"] == 238
    assert reiko["Nuyen"] == 2550.0
    assert reiko["Lifetime_Nuyen"] == 387300
    assert reiko["Submersion_Grade"] == 8


def test_contact_types_and_search():
    # 1. Test parse_contact_types
    assert parse_contact_types("Criminal, Street") == ["Criminal", "Street"]
    assert parse_contact_types(["Corporate", "Magic"]) == ["Corporate", "Magic"]
    assert parse_contact_types("Types: Matrix, Criminal.") == ["Matrix", "Criminal"]
    assert parse_contact_types(None) == []

    # 2. Test infer_contact_types
    assert "Criminal" in infer_contact_types(job="Vory Borjevik")
    assert "Matrix" in infer_contact_types(job="Penose Spider")
    assert "Corporate" in infer_contact_types(job="Saeder-Krupp Johnson")

    # 3. Test global registry search by region & type
    sea_matrix = search_contacts(contact_type="Matrix", region="SEA")
    assert len(sea_matrix) >= 2
    names = [c["name"] for c in sea_matrix]
    assert "MacCallister" in names
    assert "Eddie Wei" in names

    # 4. Test character scoped search
    reiko_matrix = search_contacts(char_id="reiko", contact_type="Matrix")
    assert len(reiko_matrix) >= 5
    reiko_matrix_names = [c["name"] for c in reiko_matrix]
    assert "Claudette Laurier" in reiko_matrix_names
    assert "Roanoke" in reiko_matrix_names
    assert "Eddie Wei" in reiko_matrix_names

    # 5. Test character scoped search with region filter
    reiko_nola_matrix = search_contacts(char_id="reiko", region="NOLA", contact_type="Matrix")
    assert len(reiko_nola_matrix) >= 3
    assert all(c["region"] == "NOLA" for c in reiko_nola_matrix)

    # 6. Test markdown table formatting
    table = format_contacts_table(reiko_nola_matrix, title="Reiko NOLA Matrix Contacts")
    assert "### Reiko NOLA Matrix Contacts" in table
    assert "| Contact Name | Conn |" in table
    assert "Claudette Laurier" in table

