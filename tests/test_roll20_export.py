"""
Unit tests for the Roll20 Shadowrun Sixth World (Genesis JSON) exporter.
Verifies strict compliance with the official Roll20 `Shadowrun6thEdition.html`
`doImport(json)` sheet worker contract.
"""

import json
import pytest
from sr6core.character.manager import CharacterManager
from sr6core.publishing.roll20_json import (
    ROLL20_ACTIVE_SKILLS,
    VALID_WEAPON_SKILLS,
    build_roll20_payload,
    export_roll20_json,
)


REQUIRED_ARRAY_KEYS = [
    "attributes",
    "qualities",
    "skills",
    "armors",
    "items",
    "augmentations",
    "vehicles",
    "drones",
    "sins",
    "lifestyles",
    "licenses",
    "contacts",
    "longRangeWeapons",
    "closeCombatWeapons",
    "spells",
    "rituals",
    "adeptPowers",
    "metamagic",
    "echoes",
    "complexForms",
    "martialArts",
    "matrixItems",
]

VALID_ATTRIBUTE_IDS = {
    "BODY",
    "AGILITY",
    "REACTION",
    "STRENGTH",
    "WILLPOWER",
    "LOGIC",
    "INTUITION",
    "CHARISMA",
    "EDGE",
    "MAGIC",
    "RESONANCE",
    "POWER_POINTS",
}

VALID_AUG_GRADES = {"STANDARD", "ALPHA", "BETA", "DELTA", "USED"}
VALID_SPELL_CATEGORIES = {
    "Combat spells",
    "Detection spells",
    "Heal spells",
    "Illusion spells",
    "Manipulation spells",
}
VALID_SPELL_DURATIONS = {"Instantaneous", "Sustained", "Limited", "Permanent"}
VALID_SPELL_RANGES = {"Line of sight", "Line of sight (Area)", "Special", "Touch"}
VALID_SPELL_TYPES = {"Physical", "Mana"}
VALID_SPELL_FEATURES = {"direct", "indirect", "sense_single", "sense_multi", "area"}
VALID_ADEPT_ACTIVATIONS = {"MAJOR_ACTION", "MINOR_ACTION", "PASSIVE"}
VALID_CF_DURATIONS = {"Sustained", "Immediate", "Permanent"}
VALID_MATRIX_SUBTYPES = {
    "COMMLINK",
    "CYBERDECK",
    "CYBER_HEADWARE",
    "RIGGER_CONSOLE",
    "CONTROL_RIG",
    "TAC_NET",
}


def simulate_roll20_do_import(payload: dict) -> None:
    """
    Simulate the exact execution of `doImport(json)` from Roll20's
    `Shadowrun6thEdition.html` (lines 13767-14688), asserting that no
    undefined lookups, null iterations, or TypeErrors can occur.
    """
    # 1. Required top-level arrays
    for key in REQUIRED_ARRAY_KEYS:
        assert key in payload, f"Missing required array key: {key}"
        assert isinstance(payload[key], list), f"Key '{key}' must be a list"

    # 2. Notes must be a non-empty string so `attrs.player_notes` is never undefined
    assert isinstance(payload.get("notes"), str) and len(payload["notes"]) > 0

    # 3. Attributes
    for attr in payload["attributes"]:
        assert attr["id"] in VALID_ATTRIBUTE_IDS, f"Invalid attribute ID: {attr['id']}"
        assert isinstance(attr["points"], (int, float))
        assert isinstance(attr["modifiedValue"], (int, float))

    # 4. Qualities
    for q in payload["qualities"]:
        assert isinstance(q["name"], str) and q["name"]
        assert isinstance(q["choice"], str)
        if q["choice"]:
            # Ensure choice wasn't left duplicated in name
            assert f"({q['choice'].lower()})" not in q["name"].lower()
        assert isinstance(q["positive"], bool)

    # 5. Skills, Knowledges & Languages
    valid_skill_ids = {v[0] for v in ROLL20_ACTIVE_SKILLS.values()} | {"knowledge", "language"}
    for sk in payload["skills"]:
        assert sk["id"] in valid_skill_ids, f"Invalid skill ID: {sk['id']}"
        assert isinstance(sk["influencedBy"], list)
        if sk["id"] not in ("knowledge", "language"):
            assert isinstance(sk["specializations"], list)
            assert str(sk["attribute"]).startswith("@{")

    # 6. Armors
    non_ignored_primary_count = 0
    for arm in payload["armors"]:
        assert isinstance(arm["accessories"], list)
        if not arm["isIgnored"] and arm["primary"]:
            non_ignored_primary_count += 1
    if payload["armors"]:
        assert non_ignored_primary_count == 1

    # 7. Augmentations
    for aug in payload["augmentations"]:
        assert aug["quality"] in VALID_AUG_GRADES
        assert isinstance(aug["essence"], (int, float))
        assert isinstance(aug["accessories"], list)

    # 8. SINs, Lifestyles & Licenses (Foreign Key integrity)
    sin_names = {s["name"] for s in payload["sins"]}
    assert len(sin_names) > 0, "At least one SIN must exist for lifestyle/license mapping"
    for lf in payload["lifestyles"]:
        assert lf["sin"] in sin_names, f"Lifestyle SIN '{lf['sin']}' not found in sins {sin_names}"
    for lic in payload["licenses"]:
        assert lic["sin"] in sin_names, f"License SIN '{lic['sin']}' not found in sins {sin_names}"

    # 9. Weapons
    for rw in payload["longRangeWeapons"]:
        assert rw["skill"] in VALID_WEAPON_SKILLS
        assert len(rw["attackRating"].split("/")) == 5
        assert isinstance(rw["ammunition"], str)
        assert isinstance(rw["wifi"], list)
        assert isinstance(rw["accessories"], list)

    for mw in payload["closeCombatWeapons"]:
        assert mw["skill"] in VALID_WEAPON_SKILLS
        assert len(mw["attackRating"].split("/")) == 5
        assert isinstance(mw["wifi"], list)
        assert isinstance(mw["accessories"], list)

    # 10. Spells
    seen_spells = set()
    for sp in payload["spells"]:
        assert sp["name"].lower() not in seen_spells, f"Duplicate spell: {sp['name']}"
        seen_spells.add(sp["name"].lower())
        assert sp["category"] in VALID_SPELL_CATEGORIES
        assert sp["duration"] in VALID_SPELL_DURATIONS
        assert sp["range"] in VALID_SPELL_RANGES
        assert sp["type"] in VALID_SPELL_TYPES
        assert isinstance(sp["features"], list)
        for feat in sp["features"]:
            assert feat in VALID_SPELL_FEATURES
        assert isinstance(sp["influencedBy"], list)

    # 11. Adept Powers
    for ap in payload["adeptPowers"]:
        assert ap["activation"] in VALID_ADEPT_ACTIVATIONS
        assert isinstance(ap["cost"], (int, float))

    # 12. Complex Forms
    for cf in payload["complexForms"]:
        assert cf["duration"] in VALID_CF_DURATIONS
        assert isinstance(cf["influences"], list)

    # 13. Matrix Items
    for mi in payload["matrixItems"]:
        assert mi["subType"] in VALID_MATRIX_SUBTYPES
        assert isinstance(mi["accessories"], list)
        assert isinstance(mi["programs"], list)


def test_velvet_roll20_export():
    """Verify Velvet's Roll20 Genesis JSON export and all character-specific mechanics."""
    cm = CharacterManager()
    raw_json = cm.export_character("velvet", fmt="roll20")
    payload = json.loads(raw_json)

    # Run full Roll20 doImport simulation
    simulate_roll20_do_import(payload)

    # Verify core identity and resources
    assert payload["streetName"] == "Velvet"
    assert payload["name"] == "Kim Jin-Young"
    assert payload["metaType"] == "Elf"
    assert payload["karma"] == 74
    assert payload["freeKarma"] == 7
    assert payload["nuyen"] == 13465
    assert payload["initiation"] == 3
    assert payload["reputation"] == 10

    # Verify attributes (Charisma 10, Magic 6, Power Points 3, Willpower 5)
    attr_map = {a["id"]: a["modifiedValue"] for a in payload["attributes"]}
    assert attr_map["CHARISMA"] == 10
    assert attr_map["WILLPOWER"] == 5
    assert attr_map["MAGIC"] == 6
    assert attr_map["POWER_POINTS"] == 3

    # Verify skills, languages, and knowledges are properly separated
    active_skills = {s["id"]: s for s in payload["skills"] if s["id"] not in ("knowledge", "language")}
    assert set(active_skills.keys()) == {"sorcery", "conjuring", "influence", "con"}
    assert active_skills["sorcery"]["rating"] == 5
    assert active_skills["sorcery"]["specializations"] == [{"name": "Spellcasting", "expertise": False}]
    assert any("Power Focus" in inf for inf in active_skills["sorcery"]["influencedBy"])

    languages = [s["name"] for s in payload["skills"] if s["id"] == "language"]
    assert "Korean (Native)" in languages
    assert "English (Specialist)" in languages
    assert "Japanese (Basic)" in languages

    knowledges = [s["name"] for s in payload["skills"] if s["id"] == "knowledge"]
    assert "Small Unit Tactics" in knowledges
    assert "MCT" in knowledges
    assert "Wuxing" in knowledges
    assert "East Asian Media" in knowledges

    # Verify spells are deduplicated (3 unique spells, not 6)
    assert len(payload["spells"]) == 3
    spell_names = {sp["name"]: sp for sp in payload["spells"]}
    assert spell_names["Increase Attribute"]["category"] == "Heal spells"
    assert spell_names["Increase Reflexes"]["category"] == "Heal spells"
    assert spell_names["Physical Barrier"]["category"] == "Manipulation spells"
    assert spell_names["Physical Barrier"]["range"] == "Line of sight (Area)"

    # Verify adept powers & metamagics with full rulebook descriptions
    assert len(payload["adeptPowers"]) == 5
    for ap in payload["adeptPowers"]:
        assert len(ap["description"]) > 40
    assert len(payload["metamagic"]) == 3
    for mm in payload["metamagic"]:
        assert len(mm["description"]) > 40

    # Verify Armor split: Skinshield (Primary) + Ballistic Hood (Cumulative) + RACS 2 (Cumulative)
    assert len(payload["armors"]) == 3
    armor_by_name = {a["name"]: a for a in payload["armors"]}
    assert armor_by_name["Ares SecureTech Skinshield"]["primary"] is True
    assert armor_by_name["Ares SecureTech Skinshield"]["isIgnored"] is False
    assert armor_by_name["Ares SecureTech Skinshield"]["rating"] == 2
    assert armor_by_name["Ares SecureTech Skinshield"]["socialrating"] == 2
    assert armor_by_name["Ballistic Hood"]["primary"] is False
    assert armor_by_name["Ballistic Hood"]["isIgnored"] is False
    assert armor_by_name["Ballistic Hood"]["rating"] == 1
    assert armor_by_name["Ruthenium Armor Concealment System (RACS 2)"]["primary"] is False
    assert armor_by_name["Ruthenium Armor Concealment System (RACS 2)"]["isIgnored"] is False
    assert armor_by_name["Ruthenium Armor Concealment System (RACS 2)"]["rating"] == 2

    # Verify Augmentations vs. Gear routing
    aug_names = {a["name"] for a in payload["augmentations"]}
    assert aug_names == {"Nanopaste Disguise Kit", "Nanocosmetics Kit", "Savior Medkit"}
    for aug in payload["augmentations"]:
        assert aug["essence"] == 0.0
        assert len(aug["description"]) > 20

    item_names = {i["name"] for i in payload["items"]}
    assert "Power Focus (Rating 3)" in item_names
    assert "Contacts (Rating 3 w/ Flare Comp, Image Link, Thermo)" in item_names
    assert "Earbuds (Rating 3)" in item_names
    assert "Subvocal Microphone" in item_names
    assert "DocWagon Gold Contract (12 Months)" in item_names
    assert "Commlink Software Library" in item_names

    # Verify Elemental Attack ranged weapon macro card (and NO Engulf in melee weapons)
    ranged_names = {rw["name"]: rw for rw in payload["longRangeWeapons"]}
    assert "Elemental Attack" in ranged_names
    assert ranged_names["Elemental Attack"]["damage"] == "6P"
    assert ranged_names["Elemental Attack"]["attackRating"] == "16/16/16/-/-"
    melee_names = {mw["name"] for mw in payload["closeCombatWeapons"]}
    assert "Engulf" not in melee_names

    # Verify merged contacts (chargen + mission contacts) & favor points formatting
    contact_map = {c["name"]: c for c in payload["contacts"]}
    assert len(contact_map) == 23
    assert "Ni Ni Xiaolu (1 FP)" in contact_map
    assert "Ms. Snow" in contact_map
    assert "Vincent Grisome" in contact_map
    assert "Claudette Laurier" in contact_map
    assert "Le Tigre" in contact_map
    assert "Hana" in contact_map
    assert "Conclave" in contact_map
    assert contact_map["Brynne Taggart (1 FP)"]["influence"] == 5
    assert contact_map["Whiskey"]["loyalty"] == 3

    # Verify matrix devices and commlink apps synced from character_purchases.qmd
    assert len(payload["matrixItems"]) >= 1
    erika = payload["matrixItems"][0]
    assert erika["name"] == "Erika Elite"
    assert erika["deviceRating"] == 4
    prog_names = [p["name"] for p in erika["programs"]]
    assert "Nanomask" in prog_names
    assert "Thermal Mood Reading" in prog_names


def test_reiko_roll20_export():
    """Verify Reiko's Emergent Intelligence / Technoshaman Roll20 Genesis JSON export."""
    cm = CharacterManager()
    raw_json = cm.export_character("reiko", fmt="roll20")
    payload = json.loads(raw_json)

    # Run full Roll20 doImport simulation
    simulate_roll20_do_import(payload)

    # 1. Identity & Submersion
    assert payload["streetName"] == "Yuriko Star"
    assert payload["name"] == "r31k0 Takahashi"
    assert "AI" in payload["metaType"]
    assert payload["submersion"] == 8

    # 2. Core Attributes (Man-at-Arms Body 15, DP 7 -> Agi 7, Sleaze 9 -> Rea 9, Attack 7 -> Str 7)
    attr_map = {a["id"]: a["modifiedValue"] for a in payload["attributes"]}
    assert attr_map["BODY"] == 15
    assert attr_map["AGILITY"] == 7
    assert attr_map["REACTION"] == 9
    assert attr_map["STRENGTH"] == 7
    assert attr_map["WILLPOWER"] == 6
    assert attr_map["LOGIC"] == 4
    assert attr_map["INTUITION"] == 2
    assert attr_map["CHARISMA"] == 4
    assert attr_map["EDGE"] == 4
    assert attr_map["RESONANCE"] == 8

    # 3. Qualities (Includes Network Benefits and Matrix Defense Umbrella)
    q_names = {q["name"] for q in payload["qualities"]}
    assert "Natural Hacker" in q_names
    assert "Stream: Technoshamans" in q_names
    assert "Designer" in q_names
    assert "Sensor Upgrade" in q_names
    assert "Pilot Origins" in q_names
    assert "Buddy System" in q_names
    assert "Sprite Bane" in q_names
    assert "Hooder" in q_names
    assert "Network Benefits" in q_names
    assert "Matrix Defense Umbrella" in q_names

    # 4. Ranged Weapons & Tesla Cone Angles Preserved
    rw_map = {rw["name"]: rw for rw in payload["longRangeWeapons"]}
    assert "Red Fox Array (2x Link-Fired)" in rw_map
    assert "Red Fox (single beam)" in rw_map
    assert "Tesla Coil (Straight)" in rw_map
    assert "Tesla Coil (Wobbly)" in rw_map
    assert "Tesla Coil (Sweep)" in rw_map
    assert "apex angle 8.58" in rw_map["Tesla Coil (Wobbly)"]["description"]
    assert "apex angle 28.07" in rw_map["Tesla Coil (Sweep)"]["description"]

    # 5. Shiawase Man-at-Arms Drone Stats
    drone_map = {d["name"]: d for d in payload["drones"]}
    assert "Shiawase Man-at-Arms" in drone_map
    maa = drone_map["Shiawase Man-at-Arms"]
    assert maa["pilot"] == 9  # 8 Resonance + 1 Designer
    assert maa["body"] == 10
    assert maa["armor"] == 8
    assert maa["sensor"] == 2

    # 6. Secondary Drones have Sensor Upgrade +1
    assert "Federated-Boeing Sky Commander (Seattle Retrans Relay)" in drone_map
    sky = drone_map["Federated-Boeing Sky Commander (Seattle Retrans Relay)"]
    assert sky["sensor"] == 4

    # 7. Echoes (All 8 Submersion Echoes)
    echo_names = {e["name"] for e in payload["echoes"]}
    assert len(echo_names) == 8
    assert "New Sprite Type" in echo_names
    assert "Sprite Conduit" in echo_names
    assert "Sprite Symbiosis" in echo_names
    assert "Living Network" in echo_names
    assert "Transcendent Network" in echo_names
    assert "Overclocking" in echo_names
    assert "Software Emulator" in echo_names
    assert "Sprite Link" in echo_names

    # 8. Complex Forms & Symbiosed Sprite Powers
    cf_map = {cf["name"]: cf for cf in payload["complexForms"]}
    assert "Cyber Spike" in cf_map
    assert "Resonance Spike" in cf_map
    assert "Enlighten Automaton" in cf_map
    assert "Sprite Power: Death Mark" in cf_map
    assert "Sprite Power: Phantom" in cf_map
    assert "Sprite Power: Override" in cf_map
    assert "Sprite Power: Harmonize" in cf_map
    assert "23d6" in cf_map["Cyber Spike"]["description"]
    assert "23d6" in cf_map["Resonance Spike"]["description"]

    # 9. Matrix Devices
    m_dev_map = {md["name"]: md for md in payload["matrixItems"]}
    assert "Living Persona (r31-K0 / Pilot AI)" in m_dev_map
    lp = m_dev_map["Living Persona (r31-K0 / Pilot AI)"]
    assert lp["attack"] == 7
    assert lp["sleaze"] == 9
    assert lp["dataProcessing"] == 7
    assert lp["firewall"] == 9
    assert "M-TOC Mark II" in m_dev_map
    assert "Essy Motors DroneMaster" in m_dev_map
    assert "The Holy Wild Sanctuary Host (~)" in m_dev_map
    assert "Oracle" in m_dev_map["The Holy Wild Sanctuary Host (~)"]["description"]

    # 10. Armor (Man-At-Arms Base Armor is Primary)
    assert len(payload["armors"]) == 1
    assert payload["armors"][0]["name"] == "Man-At-Arms Base Armor"
    assert payload["armors"][0]["primary"] is True
    assert payload["armors"][0]["rating"] == 8


@pytest.mark.parametrize("char_id", ["velvet", "reiko", "venn"])
def test_all_characters_pass_roll20_do_import_contract(char_id: str):
    """Ensure every portfolio character generates a crash-free Roll20 Genesis JSON."""
    cm = CharacterManager()
    raw_json = cm.export_character(char_id, fmt="roll20")
    payload = json.loads(raw_json)
    simulate_roll20_do_import(payload)

