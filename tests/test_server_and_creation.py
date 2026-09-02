"""
Test suite for SR6 Live-Sync Server & Character Creation Subsystems.
"""

import pytest
from sr6core.creation.priority import audit_priority_build, calculate_priority_allocation
from sr6core.character_manager import CharacterManager


def test_priority_auditor_standard():
    # Valid standard priority allocation (A, B, C, D, E)
    budget = {
        "priority_metatype": "E",
        "priority_attributes": "A",
        "priority_special": "B",
        "priority_skills": "C",
        "priority_resources": "D"
    }
    valid, warnings = audit_priority_build(budget, is_sum_to_ten=False)
    assert valid is True
    assert len(warnings) == 0


def test_priority_auditor_invalid_duplicate():
    # Invalid: duplicate rank A
    budget = {
        "priority_metatype": "A",
        "priority_attributes": "A",
        "priority_special": "B",
        "priority_skills": "C",
        "priority_resources": "D"
    }
    valid, warnings = audit_priority_build(budget, is_sum_to_ten=False)
    assert valid is False
    assert len(warnings) > 0


def test_sum_to_ten_auditor():
    # Valid Sum-to-ten (A=4, A=4, D=1, D=1, E=0 -> Total 10)
    budget = {
        "priority_metatype": "E",      # 0
        "priority_attributes": "A",    # 4
        "priority_special": "A",       # 4
        "priority_skills": "D",        # 1
        "priority_resources": "D"      # 1
    }
    valid, warnings = audit_priority_build(budget, is_sum_to_ten=True)
    assert valid is True
    assert len(warnings) == 0


def test_calculate_priority_allocation_reiko():
    cm = CharacterManager()
    char_data = cm.get_character_data("reiko")
    assert char_data is not None

    alloc = calculate_priority_allocation(char_data)
    assert "attributes" in alloc
    assert "skills" in alloc
    assert "resources" in alloc
    assert alloc["attributes"]["budget"] >= 16
    assert alloc["skills"]["budget"] >= 20
