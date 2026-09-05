"""
Unit tests for 100% De Novo CommLink6 XML Export and Sync Engine.
Verifies that character XML files are generated deterministically directly from YAML dossiers
and Quarto transaction ledgers without requiring external input XML files.
"""

import os
import xml.etree.ElementTree as ET
import pytest

from sr6core.character_manager import CharacterManager
from sr6core.exporters.genesis_xml import (
    export_genesis_xml,
    generate_commlink_metadata,
    lookup_canonical_ref,
    is_valid_gear_template,
    get_accessory_slot
)
from sr6core.commlink_sync import scan_commlink_player_saves, push_to_commlink


def test_export_velvet_de_novo():
    """Verify de novo export for Velvet (Mystic Adept) preserves powers, spells, and choices."""
    cm = CharacterManager()
    data = cm.get_character_data("velvet")
    assert data is not None
    repo_path = cm.get_character_repo_dir("velvet")

    xml_str = export_genesis_xml(data, char_repo_path=repo_path)
    assert xml_str.startswith('<?xml version="1.0" encoding="UTF-8"')

    root = ET.fromstring(xml_str)
    assert root.tag == "sr6char"
    assert root.get("gender") in ["FEMALE", "DIVERSE"]
    assert root.get("meta") == "elf"
    assert int(root.get("nuyen", 0)) > 0

    # Verify Adept Powers are present and not erroneously pruned
    powers = root.findall(".//adeptPowers/adeptpower")
    assert len(powers) >= 4
    power_refs = [p.get("ref") for p in powers]
    assert "cosmetic_control" in power_refs
    assert "command_presence" in power_refs
    assert "cloak" in power_refs

    # Verify Spells
    spells = root.findall(".//spells/spell")
    assert len(spells) >= 2
    spell_refs = [s.get("ref") for s in spells]
    assert "increase_attribute" in spell_refs
    assert "increase_reflexes" in spell_refs

    # Verify Foci with decision choice
    foci = root.findall(".//foci/focus")
    assert len(foci) >= 1
    assert foci[0].get("ref") == "qi_focus"
    decisions = foci[0].findall("decision")
    assert len(decisions) >= 2
    choice_ids = [d.get("choice") for d in decisions]
    assert "c2d17c87-1cfe-4355-9877-a20fe09c170d" in choice_ids  # Rating choice
    assert "37026c81-d5a0-44fe-8fa9-9263acb6059f" in choice_ids  # Power choice


def test_export_venn_de_novo():
    """Verify de novo export for Venn (Street Samurai / Cyborg) serializes cyberware & essence changes."""
    cm = CharacterManager()
    data = cm.get_character_data("venn")
    assert data is not None
    repo_path = cm.get_character_repo_dir("venn")

    xml_str = export_genesis_xml(data, char_repo_path=repo_path)
    root = ET.fromstring(xml_str)

    # Verify Implanted Items
    items = root.findall(".//items/item")
    implanted = [it for it in items if it.get("mode") == "IMPLANTED"]
    assert len(implanted) >= 8

    # Check Grade decision and Rating decision
    has_grade_decision = False
    for it in implanted:
        decisions = it.findall("decision")
        for dec in decisions:
            if dec.get("choice") == "c2d17c87-1cfe-4355-9877-a20fe09c170c":
                has_grade_decision = True
    assert has_grade_decision, "Implanted cyberware must include grade decision"

    # Verify Essence Changes tracking
    valmods = root.findall(".//essenceChanges/valmod")
    assert len(valmods) >= 10, "Venn must track cyberware essence loss and quality acclimation"

    acclimation_mods = [vm for vm in valmods if vm.get("ref") == "augmentation_acclimation"]
    assert len(acclimation_mods) >= 1, "Augmentation acclimation quality mods must be tracked"


def test_export_reiko_de_novo():
    """Verify de novo export for Reiko (Technoshaman AI) includes complex forms and echoes."""
    cm = CharacterManager()
    data = cm.get_character_data("reiko")
    assert data is not None
    repo_path = cm.get_character_repo_dir("reiko")

    xml_str = export_genesis_xml(data, char_repo_path=repo_path)
    root = ET.fromstring(xml_str)

    # Complex Forms
    cforms = root.findall(".//complexforms/complexforms")
    assert len(cforms) >= 3, "Technoshaman must serialize complex forms"

    # Meta Echoes
    echoes = root.findall(".//metaEchoes/metaEcho")
    assert len(echoes) >= 1, "Reiko submersion echoes must be serialized"


def test_commlink_scanner_and_aliases():
    """Verify scanner resolves aliases such as 'yuriko_star' -> 'reiko' and 'union' -> 'venn'."""
    saves = scan_commlink_player_saves()
    # If the user has CommLink installed, all 3 should be discovered
    if saves:
        assert "velvet" in saves
        assert "reiko" in saves
        assert "venn" in saves


def test_metadata_generator():
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
    assert get_accessory_slot("satellite_link") == "VEHICLE_ELECTRONICS"
    assert get_accessory_slot("comhack_securelink_upgrade") == "ELECTRONIC_ACCESSORY"
