"""
Unit tests for Gameplay Reference Tables, Weapon Combat Stats Extraction,
Sub-Items Indexing, SRM Legality Metadata, and Contact Geo-Tagging.
"""

import pytest
from sr6core.rules_db import RulesDB
from sr6core.cards import get_item_card


def test_weapon_combat_stats_and_price_extraction():
    db = RulesDB()
    cursor = db.conn.cursor()

    # 1. Verify Ares Predator VI in ref_weapons has proper price and damage
    pred = cursor.execute("SELECT id, name, cost, damage, attack_rating, modes, ammo FROM ref_weapons WHERE id = 'ares_predator_vi'").fetchone()
    assert pred is not None
    assert pred["cost"] == 750
    assert pred["damage"] == "3P"
    assert "10" in pred["attack_rating"]
    assert "SA" in pred["modes"]
    assert "15" in pred["ammo"]

    # 2. Verify Ares Predator VI is NOT duplicated in ref_gear
    gear_pred = cursor.execute("SELECT id FROM ref_gear WHERE id = 'ares_predator_vi'").fetchone()
    assert gear_pred is None

    # 3. Verify other weapons (e.g., ares_alpha, ruger_super_warhawk)
    alpha = cursor.execute("SELECT cost, damage, attack_rating FROM ref_weapons WHERE id = 'ares_alpha'").fetchone()
    if alpha:
        assert alpha["cost"] > 0
        assert alpha["damage"] != "-"


def test_sub_items_table_and_queries():
    db = RulesDB()
    cursor = db.conn.cursor()

    # Check table exists and has rows
    count = cursor.execute("SELECT COUNT(*) FROM sub_items").fetchone()[0]
    assert count >= 20

    # Query canonical echoes and metamagics
    skinlink = db.get_sub_item("Skinlink")
    assert skinlink is not None
    assert skinlink["namespace"] == "echoes"
    assert "direct neural interface" in skinlink["content"].lower()

    centering = db.get_sub_item("Centering")
    assert centering is not None
    assert centering["namespace"] == "metamagic"
    assert "negative situational dice pool" in centering["content"].lower()

    # Query by ID
    overclocking = db.get_sub_item("echo_overclocking")
    assert overclocking is not None
    assert "overclocking" in overclocking["name"].lower()

    # Test integration with cards.py
    card = get_item_card("meta_echo", "Skinlink")
    assert card is not None
    assert "direct neural interface" in card["vault_text"].lower()
    assert "Echoes" in card["citation"]


def test_ref_actions_table():
    db = RulesDB()
    cursor = db.conn.cursor()

    count = cursor.execute("SELECT COUNT(*) FROM ref_actions").fetchone()[0]
    assert count >= 15

    # Check Minor Action: Avoid Incoming
    avoid = db.get_action("Avoid Incoming")
    assert avoid is not None
    assert avoid["action_type"] == "Minor"
    assert avoid["category"] == "Combat"

    # Check Major Action: Attack / Fire Weapon
    fire = db.get_action("Fire Weapon")
    assert fire is not None
    assert fire["action_type"] == "Major"
    assert "Firearms" in fire["test"]


def test_ref_status_effects_table():
    db = RulesDB()
    cursor = db.conn.cursor()

    count = cursor.execute("SELECT COUNT(*) FROM ref_status_effects").fetchone()[0]
    assert count >= 15

    burning = db.get_status_effect("Burning")
    assert burning is not None
    assert burning["category"] == "Environmental"
    assert "Agility + Reaction" in burning["recovery_test"]

    dazed = db.get_status_effect("Dazed")
    assert dazed is not None
    assert "-2" in dazed["effect"]


def test_ref_edge_boosts_table():
    db = RulesDB()
    cursor = db.conn.cursor()

    count = cursor.execute("SELECT COUNT(*) FROM ref_edge_boosts").fetchone()[0]
    assert count >= 10

    reroll = db.get_edge_boost("Reroll One Die")
    assert reroll is not None
    assert reroll["cost"] == 1

    add_edge = db.get_edge_boost("Add Edge to Pool")
    assert add_edge is not None
    assert add_edge["cost"] == 4


def test_srm_metadata_and_rulings():
    db = RulesDB()
    cursor = db.conn.cursor()

    # Check srm_status column exists on ref_weapons and ref_cyberware
    cols_w = [c[1] for c in cursor.execute("PRAGMA table_info(ref_weapons)").fetchall()]
    assert "srm_status" in cols_w

    cols_c = [c[1] for c in cursor.execute("PRAGMA table_info(ref_cyberware)").fetchall()]
    assert "srm_status" in cols_c

    # Check srm_rulings table
    count = cursor.execute("SELECT COUNT(*) FROM srm_rulings").fetchone()[0]
    assert count >= 5

    ruling = db.get_srm_ruling("Augmentation Cap")
    assert ruling is not None
    assert "+4" in ruling["ruling"]
    assert ruling["status"] == "Official FAQ"


def test_ref_contacts_city_and_season():
    db = RulesDB()
    cursor = db.conn.cursor()

    # Check columns exist
    cols = [c[1] for c in cursor.execute("PRAGMA table_info(ref_contacts)").fetchall()]
    assert "city" in cols
    assert "season" in cols

    # Check city records exist
    cities = cursor.execute("SELECT DISTINCT city FROM ref_contacts WHERE city IS NOT NULL").fetchall()
    city_names = [c[0] for c in cities]
    assert "Seattle" in city_names
    assert "Neo-Tokyo" in city_names
    assert "Chicago" in city_names
