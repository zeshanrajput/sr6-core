"""
Test suite for SR6 Mobile JSON and HTML exporters.
Validates multi-character compilation, standard buffs calculation, AI matrix attributes,
melee weapon fire mode handling, base vs buffed attributes, and standalone HTML generation.
"""

import os
import pytest
from sr6core.character_manager import CharacterManager
from sr6core.exporters.mobile_json import export_mobile_json
from sr6core.exporters.mobile_html import export_mobile_html, get_mobile_html_template


def test_mobile_json_export_reiko():
    cm = CharacterManager()
    char_data = cm.get_character_data("reiko")
    assert char_data is not None

    repo_dir = cm.get_character_repo_dir("reiko")
    res = export_mobile_json(char_data, char_repo_path=repo_dir)

    assert res["identity"]["handle"] == "Yuriko Star" or res["identity"]["handle"] == "Reiko"
    assert res["identity"]["is_ai"] is True
    assert res["attributes"]["resonance"] == 8
    assert len(res["skills"]) > 0

    # Verify AI Matrix Attributes exist in attributes_list
    attr_codes = [a["code"] for a in res["attributes_list"]]
    assert "ATT" in attr_codes
    assert "SLZ" in attr_codes
    assert "DP" in attr_codes
    assert "FW" in attr_codes
    assert "WIL" in attr_codes
    assert "LOG" in attr_codes
    assert "BOD" not in attr_codes  # AI does not have physical attributes

    # Verify Firewall has base vs buffed drill-down
    fw = next((a for a in res["attributes_list"] if a["code"] == "FW"), None)
    assert fw is not None
    assert fw["buffed"] == 9
    assert fw["base"] == 5
    assert fw["is_buffed"] is True
    assert "rules_matrix.html#matrix-attributes" in fw["doc_link"]

    # Verify Cracking pool includes Focus + Taz Symbiosis (without specialization pre-baked)
    cracking = next((s for s in res["skills"] if s["name"] == "Cracking"), None)
    assert cracking is not None
    assert cracking["buffed_pool"] >= 21
    assert cracking["bought_hits"] == cracking["buffed_pool"] // 4
    assert cracking["specialization"] == "Hacking"
    assert cracking["specialized_pool"] == cracking["buffed_pool"] + 2

    # Verify Amalgam Cestas: single 3P melee entry without fire modes
    cestas = next((w for w in res["weapons"] if "cestas" in w["name"].lower()), None)
    assert cestas is not None
    assert cestas["damage"] == "3P"
    assert cestas["is_melee"] is True
    assert cestas["modes_str"] == "Melee"
    assert cestas["ammo"] == "—"

    # Verify Tesla Coil has buffed AR 10 / 12 / — / — / —
    tesla = next((w for w in res["weapons"] if "tesla" in w["name"].lower()), None)
    assert tesla is not None
    assert tesla["attack_rating_str"] == "10 / 12 / — / — / —"

    # Verify Complex Forms link to rules_sprites.html#complex-forms
    cf = res["powers"]["complex_forms"]
    assert len(cf) >= 5
    assert any("cleaner" in c["name"].lower() for c in cf)
    assert "rules_sprites.html#complex-forms" in cf[0]["doc_link"]

    # Verify Sprite Symbiosis Powers (Override, Phantom, Death Mark, Harmonize)
    sp_powers = res["powers"]["sprite_powers"]
    assert len(sp_powers) == 4
    sp_names = [p["name"].lower() for p in sp_powers]
    assert "override" in sp_names
    assert "phantom" in sp_names
    assert "death mark" in sp_names
    assert "harmonize" in sp_names
    assert "rules_sprites.html#sprite-symbiosis-powers" in sp_powers[0]["doc_link"]

    # Verify Shiawase Man-at-Arms augmented & inhabited stats
    maa = next((v for v in res["vehicles"] if "man-at-arms" in v["name"].lower()), None)
    assert maa is not None
    assert maa["body"] == 16      # 10 base + 5 structural integrity + 1 home device
    assert maa["pilot"] == 9     # Replaced by Reiko's RES 8 + 1 Designer
    assert maa["armor"] == 17    # 8 base + 5 armor increase + 4 wrist shield
    assert maa["sensor"] == 7   # 3 base + 3 enhanced sensors + 1 sensor upgrade quality

    # Verify secondary drones (Kwonsham Dream Genie, Utility-One) have native base pilot 1 (no override/designer bonus)
    genie = next((v for v in res["vehicles"] if "dream genie" in v["name"].lower()), None)
    assert genie is not None
    assert genie["pilot"] == 1
    assert genie["body"] == 2

    utility = next((v for v in res["vehicles"] if "utility-one" in v["name"].lower()), None)
    assert utility is not None
    assert utility["pilot"] == 1
    assert utility["body"] == 2

    # Verify no duplicate stun cestas
    stun_cestas = [w for w in res["weapons"] if "stun" in w["name"].lower()]
    assert len(stun_cestas) == 0


def test_mobile_json_export_velvet():
    cm = CharacterManager()
    char_data = cm.get_character_data("velvet")
    assert char_data is not None

    repo_dir = cm.get_character_repo_dir("velvet")
    res = export_mobile_json(char_data, char_repo_path=repo_dir)

    assert res["identity"]["handle"] == "Velvet"
    assert res["attributes"]["charisma"] == 10
    assert len(res["skills"]) > 0

    # Verify Buffed Charisma and Willpower in attributes_list
    cha = next((a for a in res["attributes_list"] if a["code"] == "CHA"), None)
    assert cha is not None
    assert cha["buffed"] == 14
    assert cha["base"] == 10
    assert cha["is_buffed"] is True

    wil = next((a for a in res["attributes_list"] if a["code"] == "WIL"), None)
    assert wil is not None
    assert wil["buffed"] == 9
    assert wil["base"] == 5
    assert wil["is_buffed"] is True

    # Verify Condition Monitors use BASE attributes (BOD 2 -> 9 boxes, WIL 5 -> 11 boxes)
    assert res["derived"]["physical_boxes"] == 9
    assert res["derived"]["stun_boxes"] == 11

    # Verify Derived Pools use BUFFED attributes (Composure: WIL 9 + CHA 14 = 23)
    assert res["derived"]["composure"] == 23

    # Verify Velvet's Influence and Con reflect the +4 sustained Charisma buff (CHA 14)
    infl = next((s for s in res["skills"] if s["name"].lower() == "influence"), None)
    assert infl is not None
    assert infl["buffed_pool"] == 19  # Base CHA 10 + 4 Spell + 5 Rtg = 19d6

    con = next((s for s in res["skills"] if s["name"].lower() == "con"), None)
    assert con is not None
    assert con["buffed_pool"] == 18   # Base CHA 10 + 4 Spell + 4 Rtg = 18d6

    # Verify Sap and Stun Baton are melee weapons with no fire modes
    sap = next((w for w in res["weapons"] if "sap" in w["name"].lower()), None)
    assert sap is not None
    assert sap["is_melee"] is True
    assert sap["modes_str"] == "Melee"
    assert sap["ammo"] == "—"

    stun_baton = next((w for w in res["weapons"] if "stun baton" in w["name"].lower()), None)
    assert stun_baton is not None
    assert stun_baton["is_melee"] is True
    assert stun_baton["modes_str"] == "Melee"
    assert stun_baton["ammo"] == "—"

    # Verify Spells: Increase Reflexes (Drain 5) and Increase Attribute (Drain 3)
    inc_refl = next((sp for sp in res["spells"] if "increase reflexes" in sp["name"].lower()), None)
    assert inc_refl is not None
    assert inc_refl["drain"] == 5
    assert inc_refl["duration"] == "Sustained"

    inc_attr = next((sp for sp in res["spells"] if "increase attribute" in sp["name"].lower()), None)
    assert inc_attr is not None
    assert inc_attr["drain"] == 3
    assert inc_attr["duration"] == "Sustained"

    # Verify Adept Powers
    cosmetic = next((p for p in res["adept_powers"] if "cosmetic" in p["name"].lower()), None)
    assert cosmetic is not None
    assert cosmetic["rating"] == 2

    sharp_tongue = next((p for p in res["adept_powers"] if "sharp tongue" in p["name"].lower()), None)
    assert sharp_tongue is not None


def test_mobile_json_export_venn():
    cm = CharacterManager()
    char_data = cm.get_character_data("venn")
    assert char_data is not None

    repo_dir = cm.get_character_repo_dir("venn")
    res = export_mobile_json(char_data, char_repo_path=repo_dir)

    assert res["identity"]["handle"] == "Venn" or res["identity"]["handle"] == "Union"
    assert res["identity"]["is_monad"] is True
    assert res["attributes"]["edge"] == 7
    assert len(res["weapons"]) > 0

    # Verify Nanite Volume is displayed and NOT Resonance
    nv_attr = next((a for a in res["attributes_list"] if a["code"] == "NV"), None)
    assert nv_attr is not None
    assert nv_attr["name"] == "Nanite Volume"
    assert nv_attr["buffed"] == 4
    res_attr = next((a for a in res["attributes_list"] if a["code"] == "RES"), None)
    assert res_attr is None

    # Verify Venn's Activesofts are displayed on skills page at rating 7
    firearms_soft = next((s for s in res["skills"] if "firearms" in s["name"].lower()), None)
    assert firearms_soft is not None
    assert firearms_soft["rating"] == 7
    assert firearms_soft["base_rating"] == 6
    assert firearms_soft["is_activesoft"] is True
    assert firearms_soft["buffed_pool"] == 15  # AGI 7 + 7 Soft + 1 Reflex Recorder = 15d6

    cracking_soft = next((s for s in res["skills"] if "cracking" in s["name"].lower()), None)
    assert cracking_soft is not None
    assert cracking_soft["rating"] == 7
    assert cracking_soft["base_rating"] == 6
    assert cracking_soft["buffed_pool"] == 13  # LOG 6 + 7 Soft = 13d6

    # Verify physical melee weapon (Monofilament Whip) has no fire mode
    whip = next((w for w in res["weapons"] if "whip" in w["name"].lower()), None)
    assert whip is not None
    assert whip["is_melee"] is True
    assert whip["modes_str"] == "Melee"

    # Verify firearm (FN P93 Praetor) has augmented AR from smartlink
    praetor = next((w for w in res["weapons"] if "praetor" in w["name"].lower()), None)
    assert praetor is not None
    assert praetor["is_melee"] is False
    assert "SA" in praetor["modes_str"]
    assert "10 / 11 / 8" in praetor["attack_rating_str"]
    assert "8 / 9 / 8" in praetor["base_attack_rating_str"]

    # Verify Colt Manhunter augmented AR from smartlink (Close & Near +2)
    colt = next((w for w in res["weapons"] if "colt" in w["name"].lower()), None)
    assert colt is not None
    assert "10 / 10 / 6" in colt["attack_rating_str"]
    assert "8 / 8 / 6" in colt["base_attack_rating_str"]


def test_standalone_mobile_html():
    cm = CharacterManager()
    char_data = cm.get_character_data("reiko")
    repo_dir = cm.get_character_repo_dir("reiko")
    
    html = export_mobile_html(char_data, char_id="reiko", char_repo_path=repo_dir)
    assert "<!DOCTYPE html>" in html
    assert "Cracking" in html
    assert "sw.js" in html
    assert "attrDrilldownArea" in html


def test_multi_bundle_mobile_html():
    cm = CharacterManager()
    bundle = {}
    for cid in ["reiko", "velvet", "venn"]:
        c_data = cm.get_character_data(cid)
        c_repo = cm.get_character_repo_dir(cid)
        bundle[cid] = export_mobile_json(c_data, char_repo_path=c_repo)

    html = get_mobile_html_template(bundle, initial_char_id="reiko")
    assert "<!DOCTYPE html>" in html
    assert "Velvet" in html
    assert "charSelect" in html
    assert "contactFilterBar" in html
