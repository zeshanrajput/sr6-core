"""
Unit tests for Catalyst's official fillable 2-page PDF character sheet exporter.
Verifies template repair (unlinked collided fields + multiline flags) and
populated data fidelity across Reiko, Velvet, and Venn.
"""

import os
import pymupdf
import pytest

from sr6core.character.manager import CharacterManager
from sr6core.publishing.fillable_pdf import export_fillable_pdf


MULTILINE_FIELDS = {
    "Skills",
    "Qualities",
    "Contacts",
    "Ranged Weapons",
    "Melee Weapons",
    "Armor",
    "Augmentations",
    "Gear",
    "Spells/Preparations/Rituals/Complex Forms",
    "Adept Powers or Other Abilities",
}


def _read_pdf_widgets(pdf_path: str):
    doc = pymupdf.open(pdf_path)
    try:
        page_count = len(doc)
        values = {}
        flags = {}
        for page in doc:
            for w in page.widgets():
                if w.field_type_string == "Text":
                    values[w.field_name] = w.field_value
                    flags[w.field_name] = w.field_flags
        return page_count, values, flags
    finally:
        doc.close()


@pytest.fixture
def char_manager():
    return CharacterManager()


def test_fillable_pdf_template_repairs_and_reiko_fields(char_manager, tmp_path):
    data = char_manager.get_character_data("reiko")
    repo_dir = char_manager.get_character_repo_dir("reiko")
    out_pdf = tmp_path / "reiko_sheet.pdf"

    result_path = export_fillable_pdf(data, char_repo_path=repo_dir, output_path=str(out_pdf))
    assert os.path.exists(result_path)
    assert out_pdf.stat().st_size > 100_000

    page_count, values, flags = _read_pdf_widgets(result_path)
    assert page_count == 2

    # Unlinked collided pairs must store independent values
    assert values["Body"] == "FW: 9"
    assert values["Agility"] == "DP: 7"
    assert values["Reaction"] == "SLZ: 9"
    assert values["Strength"] == "ATT: 7"
    assert values["Vehicle Body"] == "10(15)"
    assert values["Age"] == "~ 10"
    assert values["Height"] == "-"
    assert values["Primary Ranged Stats"] != values["Primary Melee Stats"]
    assert "DV 9P" in values["Primary Ranged Stats"]
    assert "DV 3P" in values["Primary Melee Stats"]
    assert values["Armor"] != values["Vehicle Armor"]
    assert values["Vehicle Armor"] == "8"

    # All 10 multi-row boxes must have PDF_TX_FIELD_IS_MULTILINE enabled
    for field_name in MULTILINE_FIELDS:
        assert field_name in flags, f"Missing multiline widget '{field_name}'"
        assert flags[field_name] & pymupdf.PDF_TX_FIELD_IS_MULTILINE

    # Reiko dossier accuracy
    assert values["MagicResonance"] == "9(13)"
    assert values["Karma"] == "5"
    assert values["Total Karma"] == "333"
    assert values["Vehicle"] == "Shiawase Man-at-Arms"
    assert values["Pilot"] == "2(10)"
    assert "Syntax Error" in values["Adept Powers or Other Abilities"]
    assert "Harmonize" in values["Adept Powers or Other Abilities"]


def test_fillable_pdf_velvet_and_venn(char_manager, tmp_path):
    velvet_pdf = tmp_path / "velvet_sheet.pdf"
    char_manager.export_character("velvet", fmt="pdf", output_path=str(velvet_pdf))
    v_pages, v_vals, _ = _read_pdf_widgets(str(velvet_pdf))
    assert v_pages == 2
    assert v_vals["MagicResonance"] == "6(9)"
    assert "Increase Attribute" in v_vals["Spells/Preparations/Rituals/Complex Forms"]
    assert "[Adept]" in v_vals["Adept Powers or Other Abilities"] or "Channeling" in v_vals["Adept Powers or Other Abilities"]

    venn_pdf = tmp_path / "venn_sheet.pdf"
    char_manager.export_character("venn", fmt="pdf", output_path=str(venn_pdf))
    n_pages, n_vals, _ = _read_pdf_widgets(str(venn_pdf))
    assert n_pages == 2
    assert n_vals["Essence"] == "0.49"
    assert "Synthetic Cyberarm" in n_vals["Augmentations"]
    assert "[Monad]" in n_vals["Adept Powers or Other Abilities"]
