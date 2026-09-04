"""
Unit tests for PurchasesSyncEngine and single-source purchase reconciliation.
"""

import os
from sr6core.ledger.purchases_sync import PurchasesSyncEngine
from sr6core.character_manager import CharacterManager


def test_parse_purchases_qmd_reiko():
    cm = CharacterManager()
    repo_dir = cm.get_character_repo_dir("reiko")
    assert repo_dir is not None

    core_path = os.path.join(repo_dir, "core", "character_purchases.qmd")
    chap_path = os.path.join(repo_dir, "chapters", "character_purchases.qmd")
    qmd_path = core_path if os.path.exists(core_path) else chap_path
    assert os.path.exists(qmd_path)

    parsed = PurchasesSyncEngine.parse_purchases_qmd(qmd_path)
    assert "drone_modifications" in parsed
    mods = parsed["drone_modifications"]

    # Verify Shiawase Man-at-Arms has cyberarm and Increased Sensors 6
    maa_key = next((k for k in mods if "man-at-arms" in k.lower()), None)
    assert maa_key is not None
    maa_mods = mods[maa_key]
    assert any("increased sensors 6" in m.lower() for m in maa_mods)
    assert any("used synthetic cyberarm (right" in m.lower() for m in maa_mods)
    assert any("secondary propulsion (wheeled)" in m.lower() for m in maa_mods)
    assert any("secondary propulsion (rotor)" in m.lower() for m in maa_mods)

    # Verify Autosofts list
    assert "autosofts" in parsed
    assert any("targeting" in a.lower() for a in parsed["autosofts"])


def test_purchases_sync_execution():
    res = PurchasesSyncEngine.sync_character_purchases("reiko")
    assert res["status"] == "success"
    assert res["char_id"] == "reiko"
