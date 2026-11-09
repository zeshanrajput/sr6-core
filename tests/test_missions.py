"""
Tests for SRM Mission Registry, Table Matchmaker, Rent Cadence Linter, and Career Runway.
"""

import pytest
from sr6core.character.mission_registry import (
    CANONICAL_MISSIONS,
    normalize_mission_code,
    get_mission_record,
    search_missions
)
from sr6core.character.mission_match import (
    match_mission,
    get_available_missions,
    calculate_runway,
    audit_character_missions,
    parse_character_missions_log
)


def test_mission_code_normalization():
    assert normalize_mission_code("SRM 2081-01") == "SRM.2081.01"
    assert normalize_mission_code("srm.2081.01") == "SRM.2081.01"
    assert normalize_mission_code("2081-14") == "SRM.2081.14"
    assert normalize_mission_code("2083-05") == "SRM.2083.05"
    assert normalize_mission_code("Death of a Fixer") == "SRM.2081.01"
    assert normalize_mission_code("CMP 2020-05") == "CMP.2081.05"
    assert normalize_mission_code("CMP 2081-09") == "CMP.2081.09"
    assert normalize_mission_code("Build-a-Runner") == "Build-A-Runner"
    assert normalize_mission_code("Top Chef - Seattle") == "CMP.2081.FT"


def test_canonical_mission_registry():
    assert len(CANONICAL_MISSIONS) >= 80
    assert "SRM.2081.01" in CANONICAL_MISSIONS
    assert "SRM.2083.16" in CANONICAL_MISSIONS
    assert "CMP.2081.09" in CANONICAL_MISSIONS
    assert "PM.2081.01" in CANONICAL_MISSIONS
    assert "SMH.2083.02" in CANONICAL_MISSIONS

    rec = get_mission_record("2081-14")
    assert rec is not None
    assert rec["title"] == "The Advantages of History"
    assert rec["season"] == "2081"
    assert rec["arc"] == "Seattle 2081"


def test_table_matchmaker():
    # Velvet played SRM 2081-01, Reiko has not
    res_01 = match_mission("SRM 2081-01")
    assert res_01["characters"]["velvet"]["available"] is False
    assert res_01["characters"]["velvet"]["status"] == "ALREADY PLAYED"
    assert res_01["characters"]["reiko"]["available"] is True
    assert res_01["characters"]["reiko"]["status"] == "AVAILABLE"

    # SRM 2081-14 is available for active runners
    res_14 = match_mission("2081-14")
    assert res_14["characters"]["reiko"]["available"] is True
    assert res_14["characters"]["velvet"]["available"] is True
    assert "venn" not in res_14["characters"]  # Lab prototypes excluded by default

    # Explicit query including venn
    res_venn = match_mission("2081-14", char_ids=["venn"])
    assert res_venn["characters"]["venn"]["available"] is True


def test_character_available_missions():
    avail_reiko = get_available_missions("reiko")
    assert avail_reiko["char_id"] == "reiko"
    assert avail_reiko["total_missions"] >= 80
    assert avail_reiko["played_count"] >= 30
    assert avail_reiko["available_count"] > 0
    assert "Seattle 2081" in avail_reiko["arcs"]
    assert "New Orleans 2083" in avail_reiko["arcs"]


def test_career_runway_calculation():
    runway = calculate_runway("reiko")
    assert runway["played_missions"] >= 30
    assert runway["remaining_missions"] > 0
    assert runway["projected_karma"]["conservative"] > 0
    assert runway["projected_nuyen"]["net_veteran"] > 0
    assert runway["projected_nuyen"]["rent_drag"] > 0
    assert runway["mechanical_plan"]["has_plan"] is True


def test_character_missions_audit():
    # Reiko passes duplicate and rent checks
    audit_reiko = audit_character_missions("reiko")
    assert audit_reiko["valid"] is True
    assert len(audit_reiko["errors"]) == 0
    assert audit_reiko["srm_count"] >= 20
    assert audit_reiko["rent_payments"] >= 10

    # Velvet has 5 SRMs and 0 rent payments -> should fail rent cadence check
    audit_velvet = audit_character_missions("velvet")
    assert audit_velvet["valid"] is False
    assert any("RENT CADENCE DEFICIT" in err for err in audit_velvet["errors"])


def test_search_missions_db():
    results = search_missions("Brynne Taggart")
    assert len(results) > 0
    codes = [r["code"] for r in results]
    assert any("2081-01" in c or "2081-05" in c or "2081-06" in c for c in codes)


def test_render_campaign_roadmap_html():
    from sr6core.publishing.campaign_roadmap import render_campaign_roadmap
    html_reiko = render_campaign_roadmap("reiko")
    assert "CAMPAIGN ROADMAP //" in html_reiko
    assert "SEATTLE 2081 CORE STORY ARC" in html_reiko
    assert "BLOOD DIAMONDS" in html_reiko
    assert "DENVER WAR" in html_reiko
    assert "100% COMPLETE" in html_reiko
    assert "progress-bar" in html_reiko

    html_velvet = render_campaign_roadmap("velvet")
    assert "CAMPAIGN ROADMAP //" in html_velvet
    assert "progress-bar" in html_velvet

