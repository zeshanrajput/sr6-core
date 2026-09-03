import pytest
from sr6core.rules_spirits import SPIRIT_CATALOG, get_spirit_channeling_info
from sr6core.character_manager import CharacterManager
from sr6core.exporters.mobile_json import export_mobile_json


def test_spirit_catalog_structure():
    assert "fire" in SPIRIT_CATALOG
    assert "kin" in SPIRIT_CATALOG
    assert "task" in SPIRIT_CATALOG
    assert "earth" in SPIRIT_CATALOG
    assert "plant" in SPIRIT_CATALOG

    fire = SPIRIT_CATALOG["fire"]
    assert fire["name"] == "Spirit of Fire"
    assert fire["category"] == "Core Elementals"
    assert len(fire["powers"]) > 0
    power_names = [p["name"] for p in fire["powers"]]
    assert "Elemental Attack (Fire)" in power_names

    task = SPIRIT_CATALOG["task"]
    assert task["name"] == "Spirit of Task"
    assert task["category"] == "Street Wyrd Spirits"
    skill_power = next((p for p in task["powers"] if p["name"] == "Skill"), None)
    assert skill_power is not None
    assert skill_power.get("requires_choice") is True


def test_get_spirit_channeling_info():
    # Force 1-2: 0 optional powers
    info2 = get_spirit_channeling_info("fire", force=2)
    assert info2 is not None
    assert info2["num_optional_allowed"] == 0
    assert len(info2["optional_powers"]) == 0

    # Force 3-5: 1 optional power
    info5 = get_spirit_channeling_info("fire", force=5)
    assert info5 is not None
    assert info5["name"] == "Spirit of Fire"
    assert info5["force"] == 5
    assert info5["attr_boost"] == 2  # floor(5/2) = 2
    assert info5["wound_boxes_ignored"] == 5
    assert info5["is_dual_natured"] is True
    assert info5["num_optional_allowed"] == 1
    assert len(info5["optional_powers"]) > 0

    # Force 6-8: 2 optional powers
    info6 = get_spirit_channeling_info("fire", force=6)
    assert info6["attr_boost"] == 3
    assert info6["num_optional_allowed"] == 2
    assert len(info6["optional_powers"]) > 0


def test_channeling_exporter_integration():
    cm = CharacterManager()
    velvet_data = cm.get_character_data("velvet")
    velvet_repo = cm.get_character_repo_dir("velvet")
    assert velvet_data is not None

    velvet_export = export_mobile_json(velvet_data, char_repo_path=velvet_repo)
    assert velvet_export["identity"]["has_channeling"] is True
    assert "spirit_channeling_catalog" in velvet_export
    assert "fire" in velvet_export["spirit_channeling_catalog"]
    assert "spirit_channeling_catalog" in velvet_export["powers"]

    # Reiko should not have channeling
    reiko_data = cm.get_character_data("reiko")
    reiko_repo = cm.get_character_repo_dir("reiko")
    reiko_export = export_mobile_json(reiko_data, char_repo_path=reiko_repo)
    assert reiko_export["identity"]["has_channeling"] is False
