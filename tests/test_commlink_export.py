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

    # Meta Echoes
    echoes = root.findall(".//metaEchoes/metaEcho")
    assert len(echoes) >= 1, "Reiko submersion echoes must be serialized"

    # Verify Technomancer resonance structures are NOT exported into magical <foci>
    foci = root.findall(".//foci/focus")
    assert len(foci) == 0, "Technomancer resonance data structures must not be exported as magic foci"


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


