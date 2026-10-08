"""
Unit tests for the 2-page 76-column ASCII quick-sheet exporter.
Verifies strict <= 120 lines total budget and priority-based section rendering.
"""

import pytest
from sr6core.character_manager import CharacterManager
from sr6core.exporters.quick_sheet import export_quick_sheet, MAX_WIDTH


@pytest.fixture
def char_manager():
    return CharacterManager()


def test_quick_sheet_budget_reiko(char_manager):
    sheet = char_manager.export_character("reiko", fmt="quick_sheet")
    lines = sheet.splitlines()
    assert len(lines) <= 120, f"Reiko quick sheet exceeded 120 lines ({len(lines)} lines)"
    for idx, line in enumerate(lines):
        assert len(line) <= MAX_WIDTH, f"Line {idx+1} exceeded {MAX_WIDTH} cols: '{line}'"


def test_quick_sheet_budget_velvet(char_manager):
    sheet = char_manager.export_character("velvet", fmt="quick_sheet")
    lines = sheet.splitlines()
    assert len(lines) <= 120, f"Velvet quick sheet exceeded 120 lines ({len(lines)} lines)"
    for idx, line in enumerate(lines):
        assert len(line) <= MAX_WIDTH, f"Line {idx+1} exceeded {MAX_WIDTH} cols: '{line}'"


def test_quick_sheet_budget_venn(char_manager):
    sheet = char_manager.export_character("venn", fmt="quick_sheet")
    lines = sheet.splitlines()
    assert len(lines) <= 120, f"Venn quick sheet exceeded 120 lines ({len(lines)} lines)"
    for idx, line in enumerate(lines):
        assert len(line) <= MAX_WIDTH, f"Line {idx+1} exceeded {MAX_WIDTH} cols: '{line}'"


def test_quick_sheet_sections_present(char_manager):
    sheet = char_manager.export_character("reiko", fmt="quick_sheet")
    assert "SR6 DOSSIER" in sheet
    assert "ATTRIBUTES" in sheet
    assert "DEFENSE & CONDITION TRACK" in sheet
    assert "PRIMARY ACTION POOLS" in sheet
    assert "TACTICAL WEAPONS" in sheet
    assert "MATRIX PROFILE" in sheet
    assert "END DOSSIER" in sheet
    assert len(sheet.splitlines()) <= 75


def test_quick_sheet_multiple_specializations_rendered(char_manager):
    """Verify that multiple specializations render cleanly in quick sheet output."""
    sheet = char_manager.export_character("reiko", fmt="quick_sheet")
    assert "-- Registering: 20d6" in sheet
    assert "-- Compiling: 20d6" in sheet
    assert "-- Software: 23d6" in sheet
    assert "-- Complex Forms: 23d6" in sheet

