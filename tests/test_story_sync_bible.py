"""
Unit tests for SR6 Story Sync Bible drift alerts, Section 1 & 2 entity auto-indexing,
and Section 3 legacy path resolution.
"""

import tempfile
import unittest
from pathlib import Path
from sr6core.narrative.sync import sync_narrative_context, derive_entity_tokens


class TestStorySyncBible(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp_dir.name)

    def tearDown(self):
        self.tmp_dir.cleanup()

    def _setup_mock_char(self, char_id: str = "mockchar") -> Path:
        char_dir = self.root / char_id
        char_dir.mkdir(parents=True)
        (char_dir / "narrative").mkdir(parents=True)
        (char_dir / "reference").mkdir(parents=True)

        # Baseline _quarto.yml
        quarto_yml = """project:
  type: book
book:
  title: "Mock Book"
  chapters:
    - index.qmd
    - part: "Narrative Log"
      chapters:
        - narrative/01_first.md
"""
        (char_dir / "_quarto.yml").write_text(quarto_yml, encoding="utf-8")

        # Baseline index.qmd
        index_qmd = """# Overview

### 2. Background & Campaign Narratives
* **[1. First](narrative/01_first.md)**: Narrative chapter covering First.
"""
        (char_dir / "index.qmd").write_text(index_qmd, encoding="utf-8")
        return char_dir

    def test_derive_entity_tokens(self):
        # Known multi-token or special cases
        self.assertEqual(derive_entity_tokens("~ (Tilde)"), ["~", "Tilde"])
        self.assertEqual(derive_entity_tokens("**Aisling & Étaín**"), ["Aisling", "Étaín", "Etain"])
        self.assertEqual(derive_entity_tokens("The River People & Mississippi Renovation Host"), ["River People", "Mississippi Renovation"])
        self.assertEqual(derive_entity_tokens("Shiawase Man-at-Arms (`Goshintai`)"), ["Man-at-Arms", "Goshintai"])
        self.assertEqual(derive_entity_tokens("Takahashi Satomi"), ["Takahashi Satomi", "Satomi"])
        self.assertEqual(derive_entity_tokens("Ni Ni Xiaolu"), ["Ni Ni Xiaolu", "Xiaolu"])
        self.assertEqual(derive_entity_tokens("Sigrûn"), ["Sigrûn", "Sigrun"])
        self.assertEqual(derive_entity_tokens("Donovan Pyke"), ["Donovan Pyke", "Donovan", "Pyke"])
        self.assertEqual(derive_entity_tokens("Mr. Nagai / \"The Curator\""), ["The Curator", "Mr. Nagai", "Curator", "Nagai"])

        # Generic / macro rows skipped
        self.assertEqual(derive_entity_tokens("Shiawase Corporate Tie"), [])
        self.assertEqual(derive_entity_tokens("Megacorps & Regional Dossiers"), [])

    def test_auto_index_style_a(self):
        """Tests Style A ([01](...)) entity auto-indexing in Section 1 and Section 2."""
        char_dir = self._setup_mock_char("reiko_mock")
        narrative_dir = char_dir / "narrative"

        (narrative_dir / "01_first.md").write_text("# 1. First\n\nTaz sat beside Reiko.", encoding="utf-8")
        (narrative_dir / "02_second.md").write_text("# 2. Second\n\nTaz slipped into `~` quietly.", encoding="utf-8")
        (narrative_dir / "03_third.md").write_text("# 3. Third\n\nBrynne Taggart met Taz at the threshold of `~`.", encoding="utf-8")

        continuity_md = """# Continuity Index

## 1. Key Character Foils & Entity Tracker

| Entity / Location | Sovereignty Tier | Role & Subtext | Chapter Appearances |
| :--- | :--- | :--- | :--- |
| **Taz** | `Tier 3` | Partner | [01](file:///c:/path/01_first.md) |
| **Brynne Taggart** | `Tier 1` | Fixer | [01](file:///c:/path/01_first.md) |
| **Nissan Samurai & MCT Butler** | `Archive` | Historical | [01](file:///c:/path/01_first.md) |
| **Megacorps & Regional Dossiers** | `Lore` | Setting | Throughout Anthology |

---

## 2. Key Locations, Virtual Sanctuaries, & Core Setting Constructs

| Location / Construct | Classification & 2084 Updates | Detailed Reference Guide | Key Chapter Appearances |
| :--- | :--- | :--- | :--- |
| **~ (Tilde)** | Sovereign Framework | [tilde.md](tilde.md) | [01](file:///c:/path/01_first.md) |

---

## 3. Anthology Narrative Chapter Index

| Chapter File | Title | Word Count | Status |
| --- | --- | --- | --- |
| [01_first.md](file:///c:/path/01_first.md) | 1. First | 50 | Verified |

**Total Anthology Word Count:** 50 words across 1 chapters.
"""
        (char_dir / "reference" / "story_continuity.md").write_text(continuity_md, encoding="utf-8")

        report, err = sync_narrative_context(str(char_dir))
        self.assertIsNone(err)
        self.assertEqual(report["chapter_count"], 3)
        self.assertGreater(len(report["entity_links_added"]), 0)

        updated_cont = (char_dir / "reference" / "story_continuity.md").read_text(encoding="utf-8")

        # Verify Taz has chapters 02 and 03 indexed in Style A [02], [03]
        self.assertIn("[01](file:///c:/path/01_first.md), [02](file:///", updated_cont)
        self.assertIn(", [03](file:///", updated_cont)

        # Verify Brynne Taggart has chapter 03 indexed
        self.assertIn("Brynne Taggart", updated_cont)
        self.assertIn("[01](file:///c:/path/01_first.md), [03](file:///", updated_cont)

        # Verify ~ (Tilde) in Section 2 has chapters 02 and 03
        self.assertIn("~ (Tilde)", updated_cont)
        self.assertIn("[01](file:///c:/path/01_first.md), [02](file:///", updated_cont)

        # Verify Archive and Throughout Anthology were skipped
        self.assertIn("| Throughout Anthology |", updated_cont)
        self.assertIn("| **Nissan Samurai & MCT Butler** | `Archive` | Historical | [01](file:///c:/path/01_first.md) |", updated_cont)

    def test_auto_index_style_b(self):
        """Tests Style B ([01_first.md](...)) entity auto-indexing in Section 1."""
        char_dir = self._setup_mock_char("velvet_mock")
        narrative_dir = char_dir / "narrative"

        (narrative_dir / "01_first.md").write_text("# 1. First\n\nWhiskey spoke.", encoding="utf-8")
        (narrative_dir / "02_second.md").write_text("# 2. Second\n\nMin-seo met Sigrûn in secret.", encoding="utf-8")
        (narrative_dir / "03_third.md").write_text("# 3. Third\n\nWhiskey and Donovan Pyke consulted Min-seo.", encoding="utf-8")

        continuity_md = """# Continuity Index

## 1. Key Character Contacts & Entity Tracker

| Entity / Contact | Role & Archetype | Chapter Appearances |
| --- | --- | --- |
| **Whiskey** | Street Doc | [01_first.md](file:///c:/path/01_first.md) |
| **Min-seo** | Protocol | [01_first.md](file:///c:/path/01_first.md), quoted in [02_second.md](file:///c:/path/02_second.md) (Note) |
| **Donovan Pyke** | Leader | None logged in narrative chapters (SRM 2081-12) |
| **Sigrûn** | Johnson | None logged in narrative chapters |

---

## 3. Anthology Narrative Chapter Index

| Chapter File | Title | Word Count | Status |
| --- | --- | --- | --- |
| [01_first.md](file:///c:/path/01_first.md) | 1. First | 50 | Verified |

**Total Anthology Word Count:** 50 words across 1 chapters.
"""
        (char_dir / "reference" / "story_continuity.md").write_text(continuity_md, encoding="utf-8")

        report, err = sync_narrative_context(str(char_dir))
        self.assertIsNone(err)

        updated_cont = (char_dir / "reference" / "story_continuity.md").read_text(encoding="utf-8")

        # Whiskey should append [03_third.md](file:///...)
        self.assertIn("[01_first.md](file:///c:/path/01_first.md), [03_third.md](file:///", updated_cont)

        # Min-seo should have [03_third.md] inserted before (Note)
        self.assertIn("quoted in [02_second.md](file:///c:/path/02_second.md), [03_third.md](file:///", updated_cont)
        self.assertIn("(Note)", updated_cont)

        # Donovan Pyke should replace 'None logged in narrative chapters' and retain '(SRM 2081-12)'
        self.assertIn("[03_third.md](file:///", updated_cont)
        self.assertIn("(SRM 2081-12)", updated_cont)
        self.assertNotIn("None logged in narrative chapters (SRM 2081-12)", updated_cont)

        # Sigrûn should replace 'None logged in narrative chapters' with [02_second.md]
        self.assertIn("[02_second.md](file:///", updated_cont)

    def test_safe_noop_on_non_appearance_tables(self):
        """Verifies that tables lacking Chapter Appearances (like Focus & Narrative Anchor or File Appearances) are untouched."""
        char_dir = self._setup_mock_char("venn_mock")
        narrative_dir = char_dir / "narrative"

        (narrative_dir / "01_first.md").write_text("# 1. First\n\nVenn pondered Monad ethics and Musok Tradition.", encoding="utf-8")

        continuity_md = """# Continuity Index

## 1. Key Character Foils & Entity Tracker

| Entity / Anchor | Role & Context | File Appearances |
| --- | --- | --- |
| **Venn** | Monad Dual-Consciousness | [identity_core.qmd](../chapters/identity_core.qmd) |

---

## 2. Core Setting References, Tradition, & Constructs

| Subject / Construct | Classification & Function | Detailed Reference Guide | Focus & Narrative Anchor |
| :--- | :--- | :--- | :--- |
| **Musok Tradition & Shamanism** | Korean Shamanic Lineage | [musok.md](musok.md) | Grounding of spiritual mediumship |

---

## 3. Dossier & Chapter Index

| Chapter File | Title | Word Count | Status |
| --- | --- | --- | --- |
| [01_first.md](file:///c:/path/01_first.md) | 1. First | 50 | Verified |

**Total Anthology Word Count:** 50 words across 1 chapters.
"""
        (char_dir / "reference" / "story_continuity.md").write_text(continuity_md, encoding="utf-8")

        report, err = sync_narrative_context(str(char_dir))
        self.assertIsNone(err)
        self.assertEqual(len(report["entity_links_added"]), 0)

        updated_cont = (char_dir / "reference" / "story_continuity.md").read_text(encoding="utf-8")
        # Ensure Section 1 and Section 2 tables are completely unchanged
        self.assertIn("| **Venn** | Monad Dual-Consciousness | [identity_core.qmd](../chapters/identity_core.qmd) |", updated_cont)
        self.assertIn("| **Musok Tradition & Shamanism** | Korean Shamanic Lineage | [musok.md](musok.md) | Grounding of spiritual mediumship |", updated_cont)

    def test_fix_legacy_section_3_links(self):
        """Tests that broken sr6{char_id}/chapters/ links in Section 3 are corrected."""
        char_dir = self._setup_mock_char("path_mock")
        narrative_dir = char_dir / "narrative"

        (narrative_dir / "01_first.md").write_text("# 1. First\n\nChapter one text.", encoding="utf-8")
        (narrative_dir / "02_second.md").write_text("# 2. Second\n\nChapter two text.", encoding="utf-8")

        continuity_md = """# Continuity Index

## 3. Anthology Narrative Chapter Index

| Chapter File | Title | Word Count | Status |
| --- | --- | --- | --- |
| [01_first.md](file:///c:/GitHub/sr6path_mock/chapters/01_first.md) | 1. First | 50 | Verified |
| [02_second.md](file:///c:/GitHub/sr6{char_id}/chapters/02_second.md) | 2. Second | 80 | Verified |

**Total Anthology Word Count:** 130 words across 2 chapters.
"""
        (char_dir / "reference" / "story_continuity.md").write_text(continuity_md, encoding="utf-8")

        report, err = sync_narrative_context(str(char_dir))
        self.assertIsNone(err)

        updated_cont = (char_dir / "reference" / "story_continuity.md").read_text(encoding="utf-8")
        self.assertNotIn("sr6path_mock/chapters", updated_cont)
        self.assertNotIn("sr6{char_id}/chapters", updated_cont)

        # Should be resolved to real posix file:// paths
        abs_01 = (narrative_dir / "01_first.md").resolve().as_posix()
        if abs_01[1] == ":":
            abs_01 = abs_01[0].lower() + abs_01[1:]
        self.assertIn(f"file:///{abs_01}", updated_cont)

    def test_bible_drift_alerts(self):
        """Tests that bible_drift_alerts fires when chapters exist on disk but are queued in storyboard.md or missing from voice_spec.md."""
        char_dir = self._setup_mock_char("drift_mock")
        narrative_dir = char_dir / "narrative"

        (narrative_dir / "01_first.md").write_text("# 1. First\n\nText.", encoding="utf-8")
        (narrative_dir / "36_chown.md").write_text("# 36. chown\n\nText.", encoding="utf-8")
        (narrative_dir / "37_dev_null.md").write_text("# 37. dev null\n\nText.", encoding="utf-8")

        storyboard_md = """# Storyboard

## VII. Post-Session Story Queue (Immediate Candidates)

1. **Chapter 36 — Post-CMP 2083-07: *chown*:**
2. **Chapter 37 — *dev null*:**
3. **Chapter 38 — *Future*:**
"""
        (char_dir / "reference" / "storyboard.md").write_text(storyboard_md, encoding="utf-8")

        voice_spec_md = """# Voice Spec

chapter_tiers:
  tier_1_keystones:
    chapters:
      - "01 First"
"""
        (char_dir / "reference" / "voice_spec.md").write_text(voice_spec_md, encoding="utf-8")

        report, err = sync_narrative_context(str(char_dir))
        self.assertIsNone(err)

        alerts = report.get("bible_drift_alerts", [])
        self.assertGreaterEqual(len(alerts), 3)

        # Check storyboard queue alerts
        self.assertTrue(any("Chapter 36" in a and "storyboard.md" in a for a in alerts))
        self.assertTrue(any("Chapter 37" in a and "storyboard.md" in a for a in alerts))

        # Check voice_spec unregistered alerts
        self.assertTrue(any("Chapter 36" in a and "voice_spec.md" in a for a in alerts))
        self.assertTrue(any("Chapter 37" in a and "voice_spec.md" in a for a in alerts))


    def test_print_sync_report_formatting(self):
        """Tests that print_sync_report cleanly formats entity links added and bible drift alerts."""
        import io
        from contextlib import redirect_stdout
        from sr6core.narrative.sync import print_sync_report

        mock_report = {
            "character_id": "test_char",
            "character_dir": "c:/mock/test_char",
            "chapter_count": 2,
            "total_words": 5000,
            "chapters": [
                {"track": 1, "filename": "01_a.md", "title": "A", "words": 2000, "audio_file": "01_a.mp3"},
                {"track": 2, "filename": "02_b.md", "title": "B", "words": 3000, "audio_file": None},
            ],
            "updated_files": ["reference/story_continuity.md"],
            "cleaned_unicode_files": [],
            "entity_links_added": [
                {"entity": "Taz", "track": 2, "chapter": "02_b.md", "section": "Section 1"}
            ],
            "bible_drift_alerts": [
                "Chapter 2 (02_b.md) exists on disk but is still listed in storyboard.md Post-Session Story Queue."
            ]
        }

        buf = io.StringIO()
        with redirect_stdout(buf):
            print_sync_report(mock_report)
        out = buf.getvalue()

        self.assertIn("NARRATIVE CONTEXT SYNCHRONIZATION REPORT", out)
        self.assertIn("Auto-Indexed Entity Appearances (1 added):", out)
        self.assertIn("[LINKED] Taz: Track 2 (02_b.md)", out)
        self.assertIn("Bible Drift Alerts (1):", out)
        self.assertIn("[ALERT] Chapter 2", out)

    def test_optimize_character_images_converts_jpegs_and_rewrites_refs(self):
        """Tests .jpg/.jpeg -> .webp conversion and raw + URL-encoded markdown rewriting."""
        from PIL import Image
        from sr6core.narrative.sync import optimize_character_images

        with tempfile.TemporaryDirectory() as tmpdir:
            char_dir = Path(tmpdir) / "testchar"
            (char_dir / "images").mkdir(parents=True)
            (char_dir / "reference").mkdir(parents=True)
            (char_dir / "narrative").mkdir(parents=True)

            jpeg_one = char_dir / "images" / "r31k0 - tea.jpeg"
            jpg_two = char_dir / "images" / "A&E-Glade.jpg"
            Image.new("RGB", (64, 64), color=(120, 40, 200)).save(jpeg_one, format="JPEG")
            Image.new("RGB", (64, 64), color=(20, 180, 90)).save(jpg_two, format="JPEG")

            index_qmd = char_dir / "index.qmd"
            index_qmd.write_text("![Tea](images/r31k0%20-%20tea.jpeg)\n", encoding="utf-8")

            visual_anchors = char_dir / "reference" / "visual_anchors.md"
            visual_anchors.write_text(
                "* **File:** [`r31k0 - tea.jpeg`](../images/r31k0%20-%20tea.jpeg)\n",
                encoding="utf-8",
            )

            chap_md = char_dir / "narrative" / "01_test.md"
            chap_md.write_text("![Glade](../images/A&E-Glade.jpg)\n", encoding="utf-8")

            result = optimize_character_images(char_dir)

            self.assertEqual(len(result["converted_images"]), 2)
            self.assertFalse(jpeg_one.exists())
            self.assertFalse(jpg_two.exists())
            self.assertTrue((char_dir / "images" / "r31k0 - tea.webp").exists())
            self.assertTrue((char_dir / "images" / "A&E-Glade.webp").exists())

            self.assertIn("images/r31k0%20-%20tea.webp", index_qmd.read_text(encoding="utf-8"))
            anchors_txt = visual_anchors.read_text(encoding="utf-8")
            self.assertIn("r31k0 - tea.webp", anchors_txt)
            self.assertIn("../images/r31k0%20-%20tea.webp", anchors_txt)
            self.assertIn("../images/A&E-Glade.webp", chap_md.read_text(encoding="utf-8"))

    def test_no_jpeg_files_in_character_portfolios(self):
        """Ensures all character gallery images remain WebP-only with zero .jpg/.jpeg assets."""
        chars_dir = Path("characters")
        leftover_jpegs = [
            p.as_posix()
            for p in chars_dir.rglob("*")
            if p.is_file()
            and "images" in p.parts
            and p.suffix.lower() in (".jpg", ".jpeg")
        ]
        self.assertEqual(leftover_jpegs, [], f"Found unoptimized JPEG files: {leftover_jpegs}")


if __name__ == "__main__":
    unittest.main()
