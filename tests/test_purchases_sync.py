"""
Unit tests for PurchasesSyncEngine and single-source purchase reconciliation.
"""

import os
from sr6core.ledger.purchases_sync import PurchasesSyncEngine
from sr6core.character.manager import CharacterManager


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

    # Verify Shiawase Man-at-Arms has cyberarm, Enhanced Sensors 9, HFC (RP-only), and Vector Thrust
    maa_key = next((k for k in mods if "man-at-arms" in k.lower()), None)
    assert maa_key is not None
    maa_mods = mods[maa_key]
    assert any("enhanced sensors 9" in m.lower() for m in maa_mods)
    assert any("hydrocarbon fuel converter" in m.lower() and "rp purposes only" in m.lower() for m in maa_mods)
    assert any("used synthetic cyberarm (right" in m.lower() for m in maa_mods)
    assert not any("used synthetic cyberarm (left" in m.lower() for m in maa_mods)
    assert any("secondary propulsion (vector thrust" in m.lower() for m in maa_mods)

    # Verify Drone quantities parsed (e.g. MCT Gnat x5, MCT Hornet x2)
    qtys = parsed.get("drone_quantities", {})
    assert any("gnat" in k.lower() and v == 5 for k, v in qtys.items())
    assert any("hornet" in k.lower() and v == 2 for k, v in qtys.items())

    # Verify non-device Matrix headings are not misclassified as commlink hardware
    dev_names = [d.get("name", "").lower() for d in parsed.get("matrix_devices", [])]
    assert "m-toc ii" in dev_names
    assert "software library" not in dev_names
    assert "knowsofts" not in dev_names

    # Verify Autosofts list
    assert "autosofts" in parsed
    assert any("targeting" in a.lower() for a in parsed["autosofts"])


def test_purchases_sync_execution():
    res = PurchasesSyncEngine.sync_character_purchases("reiko")
    assert res["status"] == "success"
    assert res["char_id"] == "reiko"
