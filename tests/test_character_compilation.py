"""
Unit tests for Single-Source Character Compilation Pipeline:
Verifies that character_build.qmd + character_purchases.qmd + character_log.qmd
compile deterministically into character_master.yaml and the standalone mobile PWA.
"""

import os
from sr6core.character_manager import CharacterManager
from sr6core.ledger.purchases_sync import PurchasesSyncEngine
from sr6core.exporters.mobile_json import export_mobile_json


def test_standardized_trio_structure():
    """Verify all 3 characters adhere to the standardized trio: character_build, character_purchases, character_log."""
    cm = CharacterManager()
    for cid in ["reiko", "velvet", "venn"]:
        repo_dir = cm.get_character_repo_dir(cid)
        assert repo_dir is not None, f"Repo dir missing for {cid}"

        # Check core/ (primary segregated layout) with chapters/ fallback
        build_qmd = os.path.join(repo_dir, "core", "character_build.qmd")
        if not os.path.exists(build_qmd):
            build_qmd = os.path.join(repo_dir, "chapters", "character_build.qmd")

        purchases_qmd = os.path.join(repo_dir, "core", "character_purchases.qmd")
        if not os.path.exists(purchases_qmd):
            purchases_qmd = os.path.join(repo_dir, "chapters", "character_purchases.qmd")

        log_qmd = os.path.join(repo_dir, "core", "character_log.qmd")
        if not os.path.exists(log_qmd):
            log_qmd = os.path.join(repo_dir, "chapters", "character_log.qmd")

        assert os.path.exists(build_qmd), f"character_build.qmd missing in {cid}"
        assert os.path.exists(purchases_qmd), f"character_purchases.qmd missing in {cid}"
        assert os.path.exists(log_qmd), f"character_log.qmd missing in {cid}"


def test_full_compiler_sync_and_mobile_export():
    """Verify PurchasesSyncEngine and export_mobile_json compile clean, valid mobile datasets."""
    cm = CharacterManager()

    # 1. Sync purchases
    sync_results = PurchasesSyncEngine.sync_all()
    assert len(sync_results) >= 3

    # 2. Export mobile JSON for all characters
    for cid in ["reiko", "velvet", "venn"]:
        c_data = cm.get_character_data(cid)
        assert c_data is not None
        repo_dir = cm.get_character_repo_dir(cid)

        mobile_doc = export_mobile_json(c_data, char_repo_path=repo_dir)
        assert "identity" in mobile_doc
        assert "attributes" in mobile_doc
        assert "derived" in mobile_doc
        assert "skills" in mobile_doc
        assert "weapons" in mobile_doc
        assert "matrix" in mobile_doc
        assert "exceptions" in mobile_doc
        assert len(mobile_doc["exceptions"]) >= 3, f"Exceptions missing in {cid}"

        # Verify Reiko specific compiled states
        if cid == "reiko":
            maa = next((d for d in mobile_doc["drones"] if "man-at-arms" in d["name"].lower()), None)
            assert maa is not None
            assert maa["sensor"] == 13
            assert any("increased sensors 9" in m.lower() for m in maa["modifications"])
            assert maa["rigged_pools"]["gunnery"]["pool"] == 25
            assert maa["rigged_pools"]["perception"]["pool"] == 24
