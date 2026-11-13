"""
Unit Tests for Narrative Tools: Clean-Room Story Packet & TTS Audio Narration Pre-Flight.
"""

import pytest
from pathlib import Path

from sr6core.narrative.packet import build_story_packet
from sr6core.narrative.prep_audio import scan_audio_prep, print_audio_prep_report


def test_build_story_packet_reiko():
    """Verifies clean-room story packet generation firewalls rubrics and includes voice essence & callbacks."""
    packet_md, err = build_story_packet(
        "reiko",
        "characters/reiko/narrative/37 dev-null.md",
        beat=1,
        callbacks=["33"],
    )

    assert err is None
    assert packet_md is not None
    assert len(packet_md) > 500

    # Verify Character Voice Essence is present
    packet_lower = packet_md.lower()
    assert "digital intelligence" in packet_lower or "yuriko" in packet_lower or "mindspeech" in packet_lower

    # Verify Evaluation Rubric is cleanly firewalled OUT
    assert "passing_threshold" not in packet_lower
    assert "tier_1_keystones" not in packet_lower
    assert "tiered chapter architecture" not in packet_lower
    assert "evaluation benchmarks" not in packet_lower

    # Verify Callback Chapter 33 is included
    assert "33 code freeze" in packet_lower or "code freeze" in packet_lower
    assert "gazebo" in packet_lower or "mississippi renovation society" in packet_lower

    # Verify Target Chapter 37 is included
    assert "dev-null" in packet_lower or "/dev/null" in packet_lower


def test_build_story_packet_with_items():
    """Verifies item rules lookups via RulesDB / RAGEngine are formatted as compact excerpts."""
    packet_md, err = build_story_packet(
        "reiko",
        "characters/reiko/narrative/37 dev-null.md",
        beat=1,
        items=["Ares Predator VI"],
    )

    assert err is None
    assert packet_md is not None
    assert "ares predator vi" in packet_md.lower()


def test_build_story_packet_invalid_character():
    """Verifies graceful handling of non-existent characters."""
    packet_md, err = build_story_packet(
        "nonexistent_runner_xyz_123",
        "some_file.md",
    )
    assert packet_md == ""
    assert err is not None
    assert "Could not resolve character" in err


def test_scan_audio_prep_heteronyms_and_unmapped():
    """Verifies TTS heteronym detection and unmapped proper noun / lore term extraction."""
    sample_prose = (
        "Reiko bowed before the shrine, brushing away her tears.\n"
        "At his boot heel, needles of *Discidium* frost clung to the frame.\n"
        "The silver entity inclined his head. *I am Xylothrope.*\n"
    )

    report, err = scan_audio_prep(sample_prose)
    assert err is None
    assert report is not None

    # 1. Verify Heteronym Detection
    het_words = [h["word"].lower() for h in report["heteronyms"]]
    assert "bowed" in het_words
    assert "tears" in het_words

    # 'bowed' is mapped in pronunciations.yaml (to 'boughed')
    bowed_item = next(h for h in report["heteronyms"] if h["word"].lower() == "bowed")
    assert bowed_item["mapped_to"] is not None

    # 'tears' is an unmapped heteronym
    tears_item = next(h for h in report["heteronyms"] if h["word"].lower() == "tears")
    assert tears_item["mapped_to"] is None

    # 2. Verify Unmapped Term Detection
    unmapped_names = [u["term"] for u in report["unmapped_terms"]]
    assert "Xylothrope" in unmapped_names

    # 3. Discidium is already mapped in pronunciations.yaml -> must NOT be in unmapped_terms
    assert "Discidium" not in unmapped_names

    # 4. Discidium should be tracked in mapped_lore_terms
    mapped_terms = [m["term"] for m in report["mapped_lore_terms"]]
    assert "Discidium" in mapped_terms


def test_print_audio_prep_report():
    """Verifies that report printing executes without throwing exceptions."""
    sample_prose = (
        "Reiko bowed before the shrine, brushing away her tears.\n"
        "The entity inclined his head. *I am Apophenian.*\n"
    )
    report, _ = scan_audio_prep(sample_prose)
    assert report is not None
    print_audio_prep_report(report)


def test_audio_prep_unicode_stoplist_and_italic_span():
    """Verifies Unicode capitalized matching, mapped stoplist override, and italic span deduplication."""
    sample_prose = (
        "Reiko spoke quietly with Aisling and Étaín beside the shrine.\n"
        "Wait, she whispered. Okay. Tomorrow they would cross *Human Malice* together.\n"
    )
    report, err = scan_audio_prep(sample_prose)
    assert err is None
    assert report is not None

    mapped_terms = [m["term"] for m in report["mapped_lore_terms"]]
    unmapped_terms = [u["term"] for u in report["unmapped_terms"]]

    # Mapped names even at sentence start or inside linter stoplist appear in mapped_lore_terms
    assert "Reiko" in mapped_terms
    assert "Aisling" in mapped_terms
    assert "Étaín" in mapped_terms
    assert "Étaín" not in unmapped_terms

    # Multi-word italic phrase is kept intact rather than split into unmapped single words
    assert "Human" not in unmapped_terms
    assert "Malice" not in unmapped_terms

    # Extra stop words at sentence/quote boundaries are filtered out
    assert "Wait" not in unmapped_terms
    assert "Okay" not in unmapped_terms


def test_continuity_resolve_character_dir():
    """Verifies build_continuity_report resolves character IDs and reads narrative/ in numeric order."""
    from sr6core.narrative.continuity import build_continuity_report
    report, err = build_continuity_report("reiko")
    assert err is None
    assert report["chapter_count"] >= 37
    first_file = report["chapters"][0]["filename"]
    assert first_file.startswith("01")
