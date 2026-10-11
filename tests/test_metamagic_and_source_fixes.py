"""
Unit tests for metamagic cheatsheets, sourcebook acronym fixes, and card category disambiguation.
"""

import pytest
from sr6core.rules.source_explorer import resolve_book_file, BOOK_ACRONYMS
from sr6core.rules.cheatsheets import get_cheatsheet, list_cheatsheets
from sr6core.rules.cards import get_item_card


def test_sourcebook_acronyms_resolution():
    """Verify that all core acronyms resolve to valid files."""
    for code in ["sw", "dc", "fs", "cn", "pp", "crb", "hns", "bs", "6wc"]:
        path, label = resolve_book_file(code)
        assert path is not None, f"Failed to resolve code: {code}"
        assert path.exists(), f"Path does not exist: {path}"


def test_metamagic_cheatsheet_content():
    """Verify that metamagic cheatsheet is present, complete, and aliased."""
    meta = get_cheatsheet("metamagic")
    assert meta is not None
    assert "Initiation Karma Formula" in meta["content"]
    assert "Centering" in meta["content"]
    assert "Street Wyrd" in meta["content"]
    assert "Deadly Arts" in meta["content"]
    assert "Smooth Operations" in meta["content"]

    # Test aliases
    for alias in ["magic", "metamagics", "initiation", "initiations"]:
        sheet = get_cheatsheet(alias)
        assert sheet is not None
        assert sheet["title"] == meta["title"]


def test_card_metamagic_disambiguation():
    """Verify that card lookup properly distinguishes metamagic from qualities."""
    # Charlatan metamagic from Smooth Operations
    meta_card = get_item_card("metamagic", "Charlatan")
    assert meta_card is not None
    assert "Smooth Operations" in meta_card["markdown"] or "prestidigitation" in meta_card["markdown"]

    # Charlatan quality from Sixth World Companion
    quality_card = get_item_card("quality", "Charlatan")
    assert quality_card is not None
    assert "Sixth World Companion" in quality_card["markdown"] or "Life Path" in quality_card["markdown"]


def test_card_street_wyrd_game_information_stitching():
    """Verify that Psychometry card contains both description and Game Information mechanics."""
    card = get_item_card("metamagic", "Psychometry")
    assert card is not None
    assert "Game Information" in card["markdown"]
    assert "Astral + Intuition + Initiate Grade" in card["markdown"]


def test_srmg_acronym_resolution():
    """Verify that srmg and missionsguide resolve to Missions SR6 Guide."""
    for code in ["srmg", "missionsguide", "srm", "missions"]:
        path, label = resolve_book_file(code)
        assert path is not None, f"Failed to resolve code: {code}"
        assert path.exists(), f"Path does not exist: {path}"
        assert "391504-Missions_SR6_Guide_v2_4.md" in str(path)


def test_rag_multi_rule_retrieval():
    """Verify that RAGEngine can retrieve multiple distinct rule chunks by ID."""
    from sr6core.rag.engine import RAGEngine
    engine = RAGEngine()
    rule1 = engine.get_rule("SRMG-0156")
    rule2 = engine.get_rule("SW-0520")
    assert rule1 is not None
    assert "Why wouldn't I pay to have spells quickened on me?" in rule1["topic"]
    assert rule2 is not None
    assert "Immunity to Normal Weapons" in rule2["content"]
