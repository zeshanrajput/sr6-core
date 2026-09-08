"""
Unit tests for Relational Normalization & Structured Rules Extraction in sr6-core.
Tests weapon mounts, augmentation grades view, structured modifiers extraction,
and ModifierEngine dynamic passive modifier ingestion from SQLite.
"""

import json
import sqlite3
import pytest

from sr6core.dataset_compiler import (
    extract_modifications_json,
    extract_weapon_features,
    extract_cyberware_stats,
    migrate_existing_dataset_tables,
)
from sr6core.rules_db import RulesDB
from sr6core.modifiers import ModifierEngine


def test_extract_modifications_json():
    xml = """
    <item id="WIRED_REFLEXES_1">
        <bonus>
            <attribute name="REACTION" value="1"/>
            <attribute name="INITIATIVE_DICE" value="1"/>
        </bonus>
    </item>
    """
    mods_json = extract_modifications_json(xml)
    assert mods_json != "[]"
    mods = json.loads(mods_json)
    assert any(m["ref"] == "reaction" and m["value"] == 1 for m in mods)
    assert any("initiative_dice" in m["ref"] and m["value"] == 1 for m in mods)


def test_extract_weapon_features():
    xml = """
    <item id="ARES_ALPHA">
        <accessory_mounts>
            <mount id="TOP"/>
            <mount id="UNDER"/>
        </accessory_mounts>
        <embedded_accessories>
            <item id="SMARTGUN_INTERNAL"/>
        </embedded_accessories>
    </item>
    """
    feats = extract_weapon_features(xml)
    assert "TOP" in feats["mounts"]
    assert "UNDER" in feats["mounts"]
    assert feats["mount_top"] == 1
    assert feats["mount_under"] == 1
    assert feats["mount_barrel"] == 0
    embedded = json.loads(feats["embedded_accessories_json"])
    assert any(e["ref"] == "SMARTGUN_INTERNAL" for e in embedded)


def test_extract_cyberware_stats():
    xml = """
    <item id="CYBER_EYES_2">
        <usage mode="IMPLANTED" value="0.3"/>
        <attrdef id="PRICE" table="6000"/>
    </item>
    """
    ess, cost = extract_cyberware_stats(xml)
    assert ess == 0.3
    assert cost == 6000


def test_cyberware_grades_view_and_queries():
    db = RulesDB()
    # Check Wired Reflexes or Cyberarm in cyberware grades view
    wired = db.get_cyberware_with_grades("wired_reflexes")
    assert wired is not None
    assert "grades" in wired
    grades = wired["grades"]
    assert "standard" in grades
    assert "alphaware" in grades
    assert "betaware" in grades
    assert "deltaware" in grades
    assert "used" in grades
    assert "exoware" in grades

    std_ess = grades["standard"]["essence"]
    std_cost = grades["standard"]["cost"]

    # Used / Omegaware: x1.1 ess, x0.5 cost, -1 avail
    assert grades["used"]["essence"] == round(std_ess * 1.1, 2)
    assert grades["used"]["cost"] == round(std_cost * 0.5)
    assert grades["used"]["avail_mod"] == -1

    # Alphaware: x0.8 ess, x1.2 cost, +1 avail
    assert grades["alphaware"]["essence"] == round(std_ess * 0.8, 2)
    assert grades["alphaware"]["cost"] == round(std_cost * 1.2)
    assert grades["alphaware"]["avail_mod"] == 1

    # Betaware: x0.7 ess, x1.5 cost, +2 avail
    assert grades["betaware"]["essence"] == round(std_ess * 0.7, 2)
    assert grades["betaware"]["cost"] == round(std_cost * 1.5)
    assert grades["betaware"]["avail_mod"] == 2

    # Deltaware: x0.5 ess, x2.5 cost, +3 avail
    assert grades["deltaware"]["essence"] == round(std_ess * 0.5, 2)
    assert grades["deltaware"]["cost"] == round(std_cost * 2.5)
    assert grades["deltaware"]["avail_mod"] == 3

    # Exoware: x1.1 ess, x0.8 cost, 0 avail
    assert grades["exoware"]["essence"] == round(std_ess * 1.1, 2)
    assert grades["exoware"]["cost"] == round(std_cost * 0.8)
    assert grades["exoware"]["avail_mod"] == 0


def test_weapon_mounts_query():
    db = RulesDB()
    ares = db.get_weapon_mounts_and_accessories("ares_alpha")
    if ares:
        assert isinstance(ares["mounts"], list)
        assert "mount_top" in ares


def test_modifier_engine_passive_modifiers_from_dossier():
    char_data = {
        "identity": {"handle": "Chrome"},
        "cyberware": [
            {"name": "Wired Reflexes", "rating": 1},
            {"name": "Cybereyes", "rating": 2}
        ],
        "qualities": {
            "positive": [{"name": "Quick Healer"}],
            "negative": []
        }
    }
    passives = ModifierEngine.get_passive_modifiers_from_dossier(char_data)
    assert isinstance(passives, list)
    assert any("reaction" in p.target and p.value == 1 for p in passives)
    assert any("initiative_dice" in p.target and p.value == 1 for p in passives)

