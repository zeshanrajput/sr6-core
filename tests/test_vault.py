"""
Unit tests for SR6 Vault subsystem:
- PDF conversion utilities & GPU Docling post-processor
- Atomization and frontmatter structure
- Vault health auditing
- Web FAQ ingestion and Authority Level 2 ranking
- SQLite search and authority filtering
"""

import os
import pytest
from sr6core.rules_db import RulesDB, DEFAULT_VAULT_DIR, DEFAULT_CONVERTED_DIR
from sr6core.vault.atomizer import clean_header, get_tags, is_header_footer_artifact, FILE_MAP
from sr6core.vault.auditor import audit_vault
from sr6core.vault.web_importer import parse_faq_html, clean_html_entities
from sr6core.vault.pdf_converter import (
    clean_markdown_artifacts,
    clean_shadowrun_markdown,
    is_cuda_available,
    convert_pdf_to_md,
)
from sr6core.rag.search import search_rules_db, deduplicate_and_resolve_conflicts


def test_file_map_includes_faq():
    assert "Shadowrun_Sixth_World_FAQ.md" in FILE_MAP
    faq_info = FILE_MAP["Shadowrun_Sixth_World_FAQ.md"]
    assert faq_info["abbrev"] == "SSWFAQ"
    assert faq_info["level"] == 2
    assert faq_info["name"] == "Shadowrun Sixth World FAQ"


def test_file_map_includes_core_city_editions():
    assert "Shadowrun_CGL_Sixth_Edition_Shadowrun_Sixth_World_Core_Rulebook.md" in FILE_MAP
    assert FILE_MAP["Shadowrun_CGL_Sixth_Edition_Shadowrun_Sixth_World_Core_Rulebook.md"]["abbrev"] == "SR6H"
    assert "CAT28000B_SR6 Berlin Edition.md" in FILE_MAP
    assert "CAT28000S_SR6 Core City Edition Seattle.md" in FILE_MAP


def test_clean_header():
    assert clean_header("### Combat Rules **Section**") == "Combat Rules Section"
    assert clean_header("## *Advantages*") == "Advantages"


def test_get_tags():
    tags = get_tags("This spell deals stun damage in cybercombat.")
    assert "magic" in tags
    assert "combat" in tags
    assert "matrix" in tags


def test_is_header_footer_artifact():
    assert is_header_footer_artifact("123") is True
    assert is_header_footer_artifact("SHADOWRUN // CORE RULES") is True
    assert is_header_footer_artifact("Shadowrun Missions Guide") is True
    assert is_header_footer_artifact("| Weapon | Damage |") is False
    assert is_header_footer_artifact("Normal prose paragraph text.") is False


def test_clean_shadowrun_markdown_kerning():
    raw = "The shado wrunner was inf amous for compa tible cyber ware on meta humans."
    cleaned = clean_shadowrun_markdown(raw)
    assert "shadowrunner" in cleaned
    assert "infamous" in cleaned
    assert "compatible" in cleaned
    assert "cyberware" in cleaned
    assert "metahumans" in cleaned


def test_clean_shadowrun_markdown_jackpoint():
    raw = """
Some initial text.

> Posted by: Glitch (12:44:09/10-14-80)
> Watch your back when dealing with Ares security.

More text here.
"""
    cleaned = clean_shadowrun_markdown(raw)
    assert "> **[JackPoint] Glitch (12:44:09/10-14-80)**" in cleaned
    assert "> Watch your back when dealing with Ares security." in cleaned


def test_clean_shadowrun_markdown_artifacts():
    raw = """
<!-- image -->
SHADOWRUN // SIXTH WORLD
**==> picture [568 x 345] intentionally omitted <==**
**----- Start of picture text -----**<br>
Content text here with &amp; entity.
**----- End of picture text -----**<br>
"""
    cleaned = clean_shadowrun_markdown(raw)
    assert "<!-- image -->" not in cleaned
    assert "SHADOWRUN // SIXTH WORLD" not in cleaned
    assert "intentionally omitted" not in cleaned
    assert "Content text here with & entity." in cleaned


def test_is_cuda_available():
    # User machine has RTX 4060 with CUDA
    assert is_cuda_available() is True


def test_parse_faq_html():
    sample_html = """
    <main>
      <h2 class="wp-block-heading"><strong>The Life You Have Left</strong></h2>
      <h2 class="has-medium-font-size wp-block-heading" id="Tir-Tairngire"><strong>How do you pronounce Tir Tairngire?</strong></h2>
      <p class="wp-block-paragraph">T&iacute;r Tairngire is ostensibly pronounced &ldquo;Teer Tahrn-GEE-rah.&rdquo; [<a href="/#page-top">top</a>]</p>
      
      <h2 class="has-medium-font-size wp-block-heading" id="UCAS">What about UCAS?</h2>
      <p class="wp-block-paragraph">Both &ldquo;You-KASS&rdquo; and &ldquo;You-See-Ay-Ess&rdquo; are used. [<a href="/#page-top">top</a>]</p>
    </main>
    """
    items = parse_faq_html(sample_html)
    assert len(items) == 2
    assert items[0]["chapter"] == "The Life You Have Left"
    assert items[0]["question"] == "How do you pronounce Tir Tairngire?"
    assert items[0]["anchor"] == "Tir-Tairngire"
    assert "Teer Tahrn-GEE-rah" in items[0]["answers"][0]

    assert items[1]["question"] == "What about UCAS?"
    assert items[1]["anchor"] == "UCAS"


def test_vault_audit():
    res = audit_vault()
    assert res["total_files"] >= 18640
    assert "total_files" in res
    assert "report_text" in res
    assert res["header_only_count"] == 0


def test_sqlite_sswfaq_lookup():
    db = RulesDB()
    rule = db.query_rule("SSWFAQ-0001")
    assert rule is not None
    assert rule["source"] == "Shadowrun Sixth World FAQ"
    assert rule["authority_level"] == 2
    assert "Tir Tairngire" in rule["topic"]


def test_sqlite_sswfaq_search_and_authority_ranking():
    db = RulesDB()
    results = db.search_rules("imaging scope armor")
    assert len(results) > 0
    # SSWFAQ-0145 should be found
    faq_matches = [r for r in results if r["source"] == "Shadowrun Sixth World FAQ"]
    assert len(faq_matches) > 0
    assert faq_matches[0]["authority_level"] == 2
