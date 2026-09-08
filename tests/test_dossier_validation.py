"""
Unit tests for Character Dossier Integrity Validation (Item 7).
Tests foreign key validation of YAML character items against SQLite catalog keys,
typo detection, fuzzy matching suggestions, and price checking.
"""

import pytest
from sr6core.validation import DossierValidator


def test_validator_clean_name():
    assert DossierValidator.clean_name("10x Regular Ammo") == "regular ammo"
    assert DossierValidator.clean_name("Trauma Patch (Rating 4)") == "trauma patch"
    assert DossierValidator.clean_name("Stim Patches") == "stim patch"
    assert DossierValidator.clean_name("Plastic Explosives") == "plastic explosive"


def test_validator_lookup_exact():
    validator = DossierValidator()
    # Exact match on known gear
    res = validator.validate_item("gear", "Medkit")
    assert res["valid"] is True
    assert res["matched_key"] is not None

    # Exact match on cyberware
    res = validator.validate_item("cyberware", "Wired Reflexes")
    assert res["valid"] is True


def test_validator_fuzzy_suggestion():
    validator = DossierValidator()
    # Misspelled weapon
    res = validator.validate_item("weapons", "Ares Predater")
    assert res["valid"] is False
    assert len(res["suggestions"]) > 0
    assert any("ares_predator" in s.lower() or "ares predator" in s.lower().replace("_", " ") for s in res["suggestions"])


def test_validator_validate_dossier():
    validator = DossierValidator()
    mock_dossier = {
        "identity": {"handle": "TestRunner"},
        "qualities": {
            "positive": [{"name": "Quick Healer"}],
            "negative": [{"name": "SINner"}]
        },
        "weapons": [
            {"name": "Ares Predator VI"}
        ],
        "cyberware": [
            {"name": "Cybereyes", "rating": 2}
        ],
        "gear": [
            {"name": "10x Medkit", "rating": 3}
        ]
    }

    report = validator.validate_dossier(mock_dossier)
    assert "summary" in report
    assert report["summary"]["total_items"] >= 4
    assert report["summary"]["unresolved_count"] == 0
    assert report["is_valid"] is True


def test_validator_catches_unresolved_item():
    validator = DossierValidator()
    bad_dossier = {
        "identity": {"handle": "Ghost"},
        "weapons": [
            {"name": "Nonexistent Plasma Cannon 9000"}
        ]
    }
    report = validator.validate_dossier(bad_dossier)
    assert report["is_valid"] is False
    assert report["summary"]["unresolved_count"] == 1
    assert len(report["unresolved"]) == 1
    formatted = validator.format_report(report)
    assert "UNRESOLVED" in formatted
