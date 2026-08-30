"""
Unit tests for modular text sheets, item cards, and canonical OID resolution.
"""

import os
import pytest
from sr6core.oids import resolve_canonical_oid, normalize_oid
from sr6core.exporters.vtt_text import export_base_sheet, export_modular_text_sheets
from sr6core.cards import get_base_attributes_card, get_skills_card, get_item_card


SAMPLE_CHAR = {
    "identity": {
        "handle": "Yuriko Star",
        "real_name": "r31k0 Takahashi",
        "metatype": "AI-Pilot AI",
        "stream": "Technoshamans",
        "gender": "Diverse",
        "age": "~ 10"
    },
    "attributes": {
        "body": 5,
        "agility": 3,
        "reaction": 5,
        "strength": 3,
        "willpower": 6,
        "logic": 4,
        "intuition": 2,
        "charisma": 4,
        "edge": 4,
        "resonance": 8
    },
    "skills": [
        {"name": "Tasking", "id": "tasking", "attribute": "Resonance", "rating": 6, "specialization": "Registering"},
        {"name": "Cracking", "id": "cracking", "attribute": "Logic", "rating": 5, "specialization": "Hacking"},
    ],
    "complex_forms": [
        {"name": "Cleaner", "ref": "cleaner", "fading": 2, "duration": "Permanent"},
        {"name": "Puppeteer", "ref": "puppeteer", "fading": 5, "duration": "Sustained"}
    ],
    "qualities": {
        "positive": [{"name": "Natural Hacker", "ref": "natural_hacker"}],
        "negative": [{"name": "Hooder", "ref": "hooder", "rating": 2}]
    },
    "weapons": [
        {"name": "Ares Predator VI", "ref": "ares_predator_vi", "damage": "3P", "ap": "-1", "modes": "SA/BF", "ammo": "15(c)"}
    ],
    "contacts": [
        {"name": "Kuroshio", "connection": 4, "loyalty": 3, "archetype": "Fixer"}
    ]
}


def test_oid_normalization_and_aliases():
    assert normalize_oid("Natural Hacker") == "natural_hacker"
    assert normalize_oid("Ares Predator VI") == "ares_predator_vi"
    
    oid, row, cat = resolve_canonical_oid("quality", "Natural Hacker")
    assert oid in ["natural_hacker", "qual_natural_hacker"]

    oid_cf, row_cf, cat_cf = resolve_canonical_oid("complex_form", "Cleaner")
    assert oid_cf in ["cleaner", "cf_cleaner"]


def test_modular_text_sheets_generation():
    sheets = export_modular_text_sheets(SAMPLE_CHAR, "reiko")
    assert "reiko_base.txt" in sheets
    assert "reiko_contacts.txt" in sheets
    assert "reiko_combat.txt" in sheets
    assert "reiko_inventory.txt" in sheets
    assert "reiko_vehicles.txt" in sheets
    assert "reiko_powers.txt" in sheets

    for name, content in sheets.items():
        for i, line in enumerate(content.splitlines(), 1):
            assert len(line) <= 76, f"Line {i} in {name} exceeds 76 chars ({len(line)} chars): '{line}'"

    base_txt = sheets["reiko_base.txt"]
    assert "YURIKO STAR" in base_txt
    assert "Tasking" in base_txt
    assert "Composure" in base_txt


def test_card_structure_generation():
    base_card = get_base_attributes_card(SAMPLE_CHAR)
    assert base_card["category"] == "Core / Attributes"
    assert "FW (BOD)" in base_card["stats"]
    assert base_card["stats"]["RES / MAG"] == 8

    skills_card = get_skills_card(SAMPLE_CHAR)
    assert skills_card["category"] == "Active Skills"
    assert "Tasking" in skills_card["stats"]

    item_card = get_item_card("complex_form", {"name": "Cleaner", "ref": "cleaner"})
    assert item_card["name"] == "Cleaner"
    assert item_card["category"] == "complex_form"
    assert "Overwatch Score" in item_card["vault_text"]
