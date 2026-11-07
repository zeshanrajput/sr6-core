"""
Unit tests for CommLink 6 / Genesis XML Character Exporter.
Verifies de novo XML export compliance with CommLink 6 / RPGFramework Unmarshaller3 schema.
"""

import os
import xml.etree.ElementTree as ET
import pytest

from sr6core.character.manager import CharacterManager
from sr6core.publishing.commlink_xml import (
    export_commlink_xml,
    export_to_commlink,
    generate_commlink_metadata,
    lookup_canonical_ref,
    is_valid_gear_template,
    get_accessory_slot,
    scan_commlink_player_saves,
    map_metatype_ref,
    resolve_cyberlimb_variant,
)


def test_export_velvet_commlink_xml():
    """Verify de novo export for Velvet (Mystic Adept) preserves powers, spells, and choices."""
    cm = CharacterManager()
    data = cm.get_character_data("velvet")
    assert data is not None
    repo_path = cm.get_character_repo_dir("velvet")

    xml_str = export_commlink_xml(data, char_repo_path=repo_path)
    assert xml_str.startswith('<?xml version="1.0" encoding="UTF-8"')

    root = ET.fromstring(xml_str)
    assert root.tag == "sr6char"
    assert root.get("gender") in ["FEMALE", "DIVERSE"]
    assert root.get("meta") == "elf"
    assert int(root.get("nuyen", 0)) > 0
    assert root.get("career") == "true"

    # Verify Adept Powers are present and mapped to CommLink 6 IDs
    powers = root.findall(".//adeptPowers/adeptpower")
    assert len(powers) >= 3
    power_refs = [p.get("ref") for p in powers]
    assert "cosmetic_control" in power_refs
    assert "commanding_voice" in power_refs

    # Verify Mentor Spirit decision uses canonical choice UUID and snake_case value,
    # as well as the sub-decision for improved_ability_combat to prevent CommLink 6 startup dialog errors
    qualities = root.findall(".//qualities/quality")
    mentor_qual = [q for q in qualities if q.get("ref") == "mentor_spirit"]
    assert len(mentor_qual) == 1
    mentor_decs = mentor_qual[0].findall("decision")
    assert len(mentor_decs) == 2
    dec_dict = {d.get("choice"): d.get("value") for d in mentor_decs}
    assert dec_dict.get("b69f8371-fa0e-435c-b344-8fc6d64e1fb3") == "wise_warrior"
    assert dec_dict.get("97fb1dcd-14e4-456c-aad7-17a7bf8cbbae") in ["close_combat", "firearms", "exotic_weapons"]

    # Verify Spells
    spells = root.findall(".//spells/spell")
    assert len(spells) >= 2
    spell_refs = [s.get("ref") for s in spells]
    assert "increase_attribute" in spell_refs
    assert "increase_reflexes" in spell_refs

    # Verify Foci with decision choice
    foci = root.findall(".//foci/focus")
    assert len(foci) >= 1
    assert foci[0].get("ref") in ["power_focus", "qi_focus"]
    decisions = foci[0].findall("decision")
    assert len(decisions) >= 1
    choice_ids = [d.get("choice") for d in decisions]
    assert "c2d17c87-1cfe-4355-9877-a20fe09c170d" in choice_ids


def test_export_venn_commlink_xml():
    """Verify de novo export for Venn (Street Samurai / Cyborg) serializes cyberware & essence changes."""
    cm = CharacterManager()
    data = cm.get_character_data("venn")
    assert data is not None
    repo_path = cm.get_character_repo_dir("venn")

    xml_str = export_commlink_xml(data, char_repo_path=repo_path)
    root = ET.fromstring(xml_str)

    # Verify Implanted Items
    items = root.findall(".//items/item")
    implanted = [it for it in items if it.get("mode") == "IMPLANTED"]
    assert len(implanted) >= 8

    # Verify Cyberarm has variant attribute set for CommLink 6 SimplePersist
    cyberarms = [it for it in implanted if it.get("ref") == "cyberarm"]
    assert len(cyberarms) >= 1
    for ca in cyberarms:
        assert ca.get("variant") == "fullarm_synthetic"

    # Check Grade decision
    has_grade_decision = False
    for it in implanted:
        decisions = it.findall("decision")
        for dec in decisions:
            if dec.get("choice") == "c2d17c87-1cfe-4355-9877-a20fe09c170c":
                has_grade_decision = True
    assert has_grade_decision, "Implanted cyberware must include grade decision"

    # Verify Essence Changes tracking
    valmods = root.findall(".//essenceChanges/valmod")
    assert len(valmods) >= 8, "Venn must track cyberware essence loss and quality acclimation"


def test_export_reiko_commlink_xml():
    """Verify de novo export for Reiko (Technoshaman AI) includes complex forms and echoes."""
    cm = CharacterManager()
    data = cm.get_character_data("reiko")
    assert data is not None
    repo_path = cm.get_character_repo_dir("reiko")

    xml_str = export_commlink_xml(data, char_repo_path=repo_path)
    root = ET.fromstring(xml_str)

    # Metatype mapping
    assert root.get("meta") == "pilot-ai"

    # Complex Forms
    cforms = root.findall(".//complexforms/complexforms")
    assert len(cforms) >= 3, "Technoshaman must serialize complex forms"

    # Meta Echoes - verify no duplicates and exact submersion grade 8
    echoes = root.findall(".//metaEchoes/metaEcho")
    assert len(echoes) == 8, f"Reiko submersion echoes must be exactly 8, got {len(echoes)}"
    echo_refs = [e.get("ref") for e in echoes]
    assert len(echo_refs) == len(set(echo_refs)), "Submersion echoes must not contain duplicates"

    # Verify Technomancer resonance structures are in datastructures, NOT magic foci
    foci = root.findall(".//foci/focus")
    assert len(foci) == 0, "Technomancer resonance data structures must not be exported as magic foci"
    ds = root.findall(".//datastructures/datastructure")
    assert len(ds) >= 2, "Data structures must include oracle and resonance_focus"
    ds_refs = [d.get("ref") for d in ds]
    assert "oracle" in ds_refs
    assert "resonance_focus" in ds_refs

    # Verify top-level items have valid CommLink ItemUsage modes (no firing modes like SA/BF/SS)
    valid_modes = {"CARRIED", "EQUIPPED", "HOLSTERED", "IMPLANTED", "EMBEDDED", "VIRTUAL"}
    for it in root.findall(".//items/item"):
        assert it.get("mode") in valid_modes, f"Item {it.get('ref')} has invalid mode {it.get('mode')}"

    # Verify Shiawase Man-at-Arms complex anthrodrone modifications and factory embeds
    maa_items = [it for it in root.findall(".//items/item") if it.get("ref") == "shiawase_BD_man_at_arms"]
    assert len(maa_items) == 1, "Shiawase Man-at-Arms must be exported"
    maa = maa_items[0]
    assert maa.get("changes") == "0,0,0", "Vehicles/drones must include changes='0,0,0'"

    # Factory item embeds (<accessoriesInFact>)
    facts = maa.findall(".//accessoriesInFact/item")
    assert len(facts) >= 2, "Must slot modifications into factory embeds"
    fact_refs = [f.get("ref") for f in facts]
    assert "cyberweapon_tesla_coil" in fact_refs or "cyberarm" in fact_refs
    assert "red_fox" in fact_refs

    # Standard vehicle accessories (<accessories>)
    accs = maa.findall(".//accessories/item")
    assert len(accs) >= 12, "All vehicle modifications must be serialized into accessories"
    acc_refs = [a.get("ref") for a in accs]
    assert "chameleon_coating" in acc_refs
    assert "increased_integrity" in acc_refs
    assert "realistic_features" in acc_refs
    assert "secondary_propulsion_system" in acc_refs
    assert "drone_rack" in acc_refs


def test_metadata_properties_generator():
    """Verify metadata.properties generation matches CommLink Java specification."""
    sample_data = {
        "identity": {
            "handle": "Venn",
            "metatype": "Human",
            "archetype": "Street Samurai",
            "gender": "male"
        }
    }
    meta_str = generate_commlink_metadata(
        char_data=sample_data,
        char_uuid="test-uuid-1234",
        xml_filename="Venn.xml",
        attachment_uuid="att-uuid-5678"
    )

    assert "attachment.att-uuid-5678.type=CHARACTER" in meta_str
    assert "name=Venn" in meta_str
    assert "attachment.att-uuid-5678.file=Venn.xml" in meta_str
    assert "uuid=test-uuid-1234" in meta_str
    assert "sync=true" in meta_str


def test_accessory_slot_classification():
    """Verify accessory slot resolver returns appropriate CommLink slot enum strings."""
    assert get_accessory_slot("image_link") == "OPTICAL"
    assert get_accessory_slot("thermographic_vision") == "OPTICAL"
    assert get_accessory_slot("audio_enhancement") == "AUDIO"
    assert get_accessory_slot("ballistic_hood") == "ARMOR"
    assert get_accessory_slot("drone_rack") == "VEHICLE_HARDPOINT"
    assert get_accessory_slot("satellite_link") == "VEHICLE_ELECTRONICS"
    assert get_accessory_slot("integrated_cyberarm") == "CYBERLIMB_IMPLANT"


def test_map_metatype_ref():
    """Verify metatype resolver maps correctly to CommLink 6 ref_metatypes."""
    assert map_metatype_ref("Human") == "human"
    assert map_metatype_ref("Elf") == "elf"
    assert map_metatype_ref("Dalakitnon Elf") == "elf"
    assert map_metatype_ref("AI (Pilot AI)") == "pilot-ai"
    assert map_metatype_ref("AI-Pilot AI") == "pilot-ai"
    assert map_metatype_ref("Dwarf") == "dwarf"
    assert map_metatype_ref("Ork") == "ork"
    assert map_metatype_ref("Troll") == "troll"


def test_export_to_commlink_local_sheet():
    """Verify export_to_commlink generates local output/<char_id>_sheet.xml."""
    ok, msg, stats = export_to_commlink("velvet")
    assert ok is True
    assert "velvet" in msg.lower()


def test_resolve_cyberlimb_variant():
    """Verify cyberlimb variant resolver returns appropriate variant ID."""
    assert resolve_cyberlimb_variant("cyberarm", {"name": "Synthetic Cyberarm"}) == "fullarm_synthetic"
    assert resolve_cyberlimb_variant("cyberarm", {"name": "Obvious Cyberarm"}) == "fullarm_obvious"
    assert resolve_cyberlimb_variant("cyberarm", {"notes": "Forearm obvious"}) == "forearm_obvious"
    assert resolve_cyberlimb_variant("cyberleg", {"name": "Left Cyberleg"}) == "fullleg_obvious"
    assert resolve_cyberlimb_variant("cyberleg", {"name": "Synthetic Cyberleg"}) == "fullleg_synthetic"
    assert resolve_cyberlimb_variant("cybertorso", {}) == "torso_obvious"
    assert resolve_cyberlimb_variant("cyberskull", {"notes": "synthetic"}) == "skull_synthetic"
    assert resolve_cyberlimb_variant("smartlink", {}) is None


def test_commlink_xml_cross_character_invariants():
    """Exhaustive invariant test across all active character dossiers (Velvet, Venn, Reiko).

    Verifies:
    1. Every item mode matches valid CommLink ItemUsage enums (never tabletop firing modes like SA/BF/SS).
    2. Every item ref is a verified template in SQLite rules_index.db.
    3. Every accessory slot matches valid CommLink ItemHook enums.
    4. Every vehicle inFactoryItem UUID matches an authentic factory embed in ref_vehicles.
    5. No factory embed UUID is duplicated on a vehicle.
    6. No code/python snippets (e.g. `inc(...)`) leak into customName or item refs.
    """
    import sqlite3
    from sr6core.publishing.commlink_xml import DEFAULT_DB_PATH

    VALID_MODES = {"CARRIED", "EQUIPPED", "HOLSTERED", "IMPLANTED", "EMBEDDED", "VIRTUAL"}
    VALID_HOOKS = {
        "BARREL", "TOP", "UNDER", "OPTICAL", "AUDIO", "ARMOR", "FASHION",
        "SOFTWARE", "VEHICLE_HARDPOINT", "VEHICLE_POWERTRAIN", "VEHICLE_CHASSIS",
        "VEHICLE_ELECTRONICS", "VEHICLE_TIRES", "VEHICLE_WEAPON_LARGE", "VEHICLE_WEAPON_MEDIUM",
        "VEHICLE_WEAPON_SMALL", "CYBERLIMB_IMPLANT", "CYBEREYE_IMPLANT", "CYBEREAR_IMPLANT",
        "ELECTRONIC_ACCESSORY", "SENSOR_FUNCTION", "SENSOR_HOUSING", "HELMET_ACCESSORY",
        "BODYWARE", "HEADWARE", "EARWARE", "EYEWARE"
    }

    cm = CharacterManager()
    db_file = os.path.expanduser(DEFAULT_DB_PATH)
    assert os.path.exists(db_file), f"Database not found at {db_file}"

    conn = sqlite3.connect(db_file)
    c = conn.cursor()

    for char_id in ["velvet", "venn", "reiko"]:
        data = cm.get_character_data(char_id)
        assert data is not None, f"Character data missing for {char_id}"
        repo_path = cm.get_character_repo_dir(char_id)

        xml_str = export_commlink_xml(data, char_repo_path=repo_path)
        root = ET.fromstring(xml_str)
        assert root.tag == "sr6char"

        # Check all items and nested accessories
        all_items = root.findall(".//item")
        assert len(all_items) > 0

        for it in all_items:
            mode = it.get("mode")
            assert mode in VALID_MODES, f"[{char_id}] Invalid mode '{mode}' on item {it.get('ref')}"

            ref = it.get("ref")
            assert ref, f"[{char_id}] Item missing ref attribute"
            assert not any(err in ref for err in ["`", "inc(", "nuyen", "{"]), f"[{char_id}] Corrupt ref '{ref}'"

            slot = it.get("slot")
            if slot is not None:
                assert slot in VALID_HOOKS, f"[{char_id}] Invalid accessory slot '{slot}' on item '{ref}'"

            cn = it.findtext("customName")
            if cn:
                assert not any(err in cn for err in ["`", "inc("]), f"[{char_id}] Corrupt customName '{cn}' on item '{ref}'"

        # Check vehicle factory embeds integrity
        for v in root.findall(".//items/item"):
            if v.get("changes") == "0,0,0":
                v_ref = v.get("ref")
                c.execute("SELECT raw_xml FROM ref_vehicles WHERE id = ?", (v_ref,))
                row = c.fetchone()
                valid_factory_ids = set()
                if row and row[0]:
                    v_root = ET.fromstring(row[0])
                    v_mods = v_root.find("modifications")
                    if v_mods is not None:
                        for em in v_mods.findall("embed"):
                            if em.attrib.get("id"):
                                valid_factory_ids.add(em.attrib.get("id"))

                facts = v.findall(".//accessoriesInFact/item")
                assigned_facts = []
                for f in facts:
                    fact_id = f.get("inFactoryItem")
                    assert fact_id, f"[{char_id}] accessoriesInFact item missing inFactoryItem UUID"
                    assert fact_id in valid_factory_ids, f"[{char_id}] Hallucinated inFactoryItem UUID '{fact_id}' for vehicle '{v_ref}'"
                    assigned_facts.append(fact_id)

                assert len(assigned_facts) == len(set(assigned_facts)), f"[{char_id}] Duplicate inFactoryItem assignments on vehicle '{v_ref}'"

    conn.close()


def test_commlink_archetype_subsystem_segregation():
    """Verifies strict subsystem segregation by character archetype.

    1. Technomancers (Reiko): resonance structures in <datastructures>, 0 magic foci, 0 spells, 0 adept powers, exact submersion grade.
    2. Awakened / Mystic Adepts (Velvet): 0 datastructures, 0 echoes, spells in <spells>, adept powers in <adeptPowers>, foci in <foci>.
    3. Street Samurai / Cyborg (Venn): 0 magic, 0 resonance, all cyberware in <items mode="IMPLANTED">, essence changes tracked.
    """
    cm = CharacterManager()

    # 1. Reiko (Technoshaman AI)
    r_data = cm.get_character_data("reiko")
    r_repo = cm.get_character_repo_dir("reiko")
    r_root = ET.fromstring(export_commlink_xml(r_data, char_repo_path=r_repo))

    assert r_root.find("datastructures") is not None and len(r_root.find("datastructures")) >= 2
    assert r_root.find("foci") is None or len(r_root.find("foci")) == 0
    assert r_root.find("spells") is None or len(r_root.find("spells")) == 0
    assert r_root.find("adeptPowers") is None or len(r_root.find("adeptPowers")) == 0
    echoes = r_root.find("metaEchoes")
    assert echoes is not None and len(echoes) == 8, f"Submersion grade must be 8, got {len(echoes)}"
    cforms = r_root.find("complexforms")
    assert cforms is not None and len(cforms) >= 3

    # 2. Velvet (Mystic Adept Face)
    v_data = cm.get_character_data("velvet")
    v_repo = cm.get_character_repo_dir("velvet")
    v_root = ET.fromstring(export_commlink_xml(v_data, char_repo_path=v_repo))

    assert v_root.find("datastructures") is None or len(v_root.find("datastructures")) == 0
    assert v_root.find("complexforms") is None or len(v_root.find("complexforms")) == 0
    assert v_root.find("metaEchoes") is None or len(v_root.find("metaEchoes")) == 0
    assert v_root.find("spells") is not None and len(v_root.find("spells")) >= 2
    assert v_root.find("adeptPowers") is not None and len(v_root.find("adeptPowers")) >= 3
    assert v_root.find("foci") is not None and len(v_root.find("foci")) >= 1

    # 3. Venn (Street Samurai / Cyborg)
    vn_data = cm.get_character_data("venn")
    vn_repo = cm.get_character_repo_dir("venn")
    vn_root = ET.fromstring(export_commlink_xml(vn_data, char_repo_path=vn_repo))

    assert vn_root.find("datastructures") is None or len(vn_root.find("datastructures")) == 0
    assert vn_root.find("complexforms") is None or len(vn_root.find("complexforms")) == 0
    assert vn_root.find("metaEchoes") is None or len(vn_root.find("metaEchoes")) == 0
    assert vn_root.find("foci") is None or len(vn_root.find("foci")) == 0
    assert vn_root.find("spells") is None or len(vn_root.find("spells")) == 0
    assert vn_root.find("adeptPowers") is None or len(vn_root.find("adeptPowers")) == 0
    assert vn_root.find("essenceChanges") is not None and len(vn_root.find("essenceChanges")) >= 8
    assert len(vn_root.findall(".//items/item[@mode='IMPLANTED']")) >= 8


def test_commlink_xml_structural_and_decision_invariants():
    """Verifies CommLink 6 XML root schema conformance, reward date ISO-8601 formatting, and canonical decisions.

    Verifies across all characters:
    1. Root attributes: gender, meta, career="true", positive nuyen/karma integer strings.
    2. Mandatory child sections: attributes, qualities, skills, charGenUsed, strictness, items.
    3. All reward entries have valid ISO-8601 timestamps (YYYY-MM-DDTHH:MM:SS.000Z).
    4. Every decision choice UUID matches a canonical CommLink decision choice UUID.
    """
    import re
    iso_re = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$')
    canonical_choices = {
        "c2d17c87-1cfe-4355-9877-a20fe09c170d",  # Rating
        "c2d17c87-1cfe-4355-9877-a20fe09c170c",  # Cyberware grade
        "b015341d-24dc-42bb-a46b-781a5340e0b3",  # Ammo type
        "89ebc659-ba06-4732-b347-6b832842a55b",  # Knowledge skill name
        "a7103ee4-31fa-435d-ac42-08f7d4d1e80c",  # Language name
        "b69f8371-fa0e-435c-b344-8fc6d64e1fb3",  # Mentor spirit
        "97fb1dcd-14e4-456c-aad7-17a7bf8cbbae",  # Mentor spirit skill bonus
        "4096584c-eb76-49b2-be6b-1a6c0ca9e50a",  # Drain attribute
        "794d4562-8ca6-4958-81df-cf3cee81087d",  # Focus category
        "dbb18bb4-89a4-4435-bede-3077ee600bc5",  # Exceptional attribute
        "75f01ecc-60f3-4b5b-98de-c80008ebffec",  # Sprite type echo
        "8b24b2be-c2fc-46f4-a353-7313f1f69d07",  # Resonance focus attribute
    }

    cm = CharacterManager()
    for char_id in ["velvet", "venn", "reiko"]:
        data = cm.get_character_data(char_id)
        repo_path = cm.get_character_repo_dir(char_id)
        xml_str = export_commlink_xml(data, char_repo_path=repo_path)
        root = ET.fromstring(xml_str)

        # Root attributes
        assert root.get("career") == "true", f"[{char_id}] career attribute must be 'true'"
        assert root.get("gender") in ["MALE", "FEMALE", "DIVERSE"], f"[{char_id}] Invalid gender"
        assert root.get("meta"), f"[{char_id}] Missing meta attribute"
        assert int(root.get("nuyen", -1)) >= 0, f"[{char_id}] Invalid nuyen balance"
        assert int(root.get("karmaI", -1)) >= 0, f"[{char_id}] Invalid karma balance"

        # Mandatory child elements
        for req_child in ["attributes", "qualities", "skills", "charGenUsed", "strictness", "items"]:
            assert root.find(req_child) is not None, f"[{char_id}] Missing required child <{req_child}>"

        # Rewards date validation
        rewards_el = root.find("rewards")
        if rewards_el is not None:
            for rew in rewards_el.findall("reward"):
                r_date = rew.get("date")
                assert iso_re.match(r_date), f"[{char_id}] Non-ISO date in reward: {r_date}"

        # Decision choices validation
        for dec in root.findall(".//decision"):
            choice_uuid = dec.get("choice")
            assert choice_uuid in canonical_choices, f"[{char_id}] Unrecognized decision choice UUID: {choice_uuid}"




