"""
Test suite for SR6 Mobile JSON and HTML exporters.
Validates multi-character compilation, standard buffs calculation, and standalone HTML generation.
"""

import os
import pytest
from sr6core.character_manager import CharacterManager
from sr6core.exporters.mobile_json import export_mobile_json
from sr6core.exporters.mobile_html import export_mobile_html, get_mobile_html_template


def test_mobile_json_export_yuriko():
    cm = CharacterManager()
    char_data = cm.get_character_data("yuriko")
    assert char_data is not None

    repo_dir = cm.get_character_repo_dir("yuriko")
    res = export_mobile_json(char_data, char_repo_path=repo_dir)

    assert res["identity"]["handle"] == "Yuriko Star"
    assert res["attributes"]["resonance"] == 8
    assert len(res["skills"]) > 0

    # Verify Cracking pool includes Focus + Taz Symbiosis
    cracking = next((s for s in res["skills"] if s["name"] == "Cracking"), None)
    assert cracking is not None
    assert cracking["buffed_pool"] >= 21
    assert cracking["bought_hits"] == cracking["buffed_pool"] // 4
    assert len(cracking["buffs"]) >= 2


def test_mobile_json_export_velvet():
    cm = CharacterManager()
    char_data = cm.get_character_data("velvet")
    assert char_data is not None

    repo_dir = cm.get_character_repo_dir("velvet")
    res = export_mobile_json(char_data, char_repo_path=repo_dir)

    assert res["identity"]["handle"] == "Velvet"
    assert res["attributes"]["charisma"] == 10
    assert len(res["skills"]) > 0


def test_mobile_json_export_union():
    cm = CharacterManager()
    char_data = cm.get_character_data("union")
    assert char_data is not None

    repo_dir = cm.get_character_repo_dir("union")
    res = export_mobile_json(char_data, char_repo_path=repo_dir)

    assert res["identity"]["handle"] == "Venn" or res["identity"]["handle"] == "Union"
    assert res["attributes"]["edge"] == 7
    assert len(res["weapons"]) > 0


def test_standalone_mobile_html():
    cm = CharacterManager()
    char_data = cm.get_character_data("yuriko")
    repo_dir = cm.get_character_repo_dir("yuriko")
    
    html = export_mobile_html(char_data, char_id="yuriko", char_repo_path=repo_dir)
    assert "<!DOCTYPE html>" in html
    assert "Yuriko Star" in html
    assert "Cracking" in html
    assert "sw.js" in html


def test_multi_bundle_mobile_html():
    cm = CharacterManager()
    bundle = {}
    for cid in ["yuriko", "velvet", "union"]:
        c_data = cm.get_character_data(cid)
        c_repo = cm.get_character_repo_dir(cid)
        bundle[cid] = export_mobile_json(c_data, char_repo_path=c_repo)

    html = get_mobile_html_template(bundle, initial_char_id="yuriko")
    assert "<!DOCTYPE html>" in html
    assert "Yuriko Star" in html
    assert "Velvet" in html
    assert "charSelect" in html
