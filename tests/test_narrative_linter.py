"""
Unit tests for Narrative Linter enhancements:
- Ellipses count & gate
- Multi-speaker paragraph detection
- Sentence burstiness CV & paragraph braiding
- Cross-chapter window echo detection
- MCP prose linting formatting
"""

import os
import tempfile
import unittest
from sr6core.narrative.linter import analyze_prose, print_prose_report
from sr6core.mcp import handle_lint_prose, handle_evaluate_draft


class TestNarrativeLinter(unittest.TestCase):
    def test_ellipses_valid_pass_and_fail(self):
        # 1. Passing case: clean text without excessive ellipses
        # 300 words with 0 ellipses -> density 0.00 <= 0.60 -> True
        passing_words = ["word"] * 300
        passing_text = " ".join(passing_words) + "."
        report_pass, err_pass = analyze_prose(passing_text)
        self.assertIsNone(err_pass)
        self.assertIsNotNone(report_pass)
        self.assertEqual(report_pass["ellipses_count"], 0)
        self.assertEqual(report_pass["ellipses_per_300"], 0.0)
        self.assertTrue(report_pass["ellipses_valid"])

        # 2. Failing case: 100 words with 3 ellipses
        # density = (3 / 100) * 300 = 9.00 > 0.60 -> False
        failing_text = (
            "The runner waited in the shadow of the conduit... "
            "Her breath misted in the cold air as the patrol vehicle approached slowly... "
            "She had to choose between fighting or running... "
            + " ".join(["word"] * 70)
            + "."
        )
        report_fail, err_fail = analyze_prose(failing_text)
        self.assertIsNone(err_fail)
        self.assertIsNotNone(report_fail)
        self.assertGreaterEqual(report_fail["ellipses_count"], 3)
        self.assertGreater(report_fail["ellipses_per_300"], 0.60)
        self.assertFalse(report_fail["ellipses_valid"])
        self.assertFalse(report_fail["gates_passed"])
        self.assertTrue(any("ellipses" in r.lower() for r in report_fail["redlines"]))

    def test_multi_speaker_detection(self):
        # Case A: Mixed acoustic quote + mindspeech in same paragraph
        mixed_para = (
            '"We need to get out of here right now," Velvet said aloud. '
            '*Stay behind me,* she transmitted across the link.'
        )
        report_mixed, _ = analyze_prose(mixed_para)
        self.assertIsNotNone(report_mixed)
        self.assertEqual(len(report_mixed["multi_speaker_paragraphs"]), 1)
        self.assertFalse(report_mixed["gates_passed"])
        self.assertTrue(any("multi-speaker" in r.lower() for r in report_mixed["redlines"]))

        # Case B: Two distinct capitalized speaker names with dialogue verbs
        distinct_para = (
            '"Hold your fire," Reiko commanded. '
            '"I cannot acquire the target," Bast replied.'
        )
        report_distinct, _ = analyze_prose(distinct_para)
        self.assertIsNotNone(report_distinct)
        self.assertEqual(len(report_distinct["multi_speaker_paragraphs"]), 1)

        # Case C: Single speaker dialogue in one paragraph should NOT trigger
        single_speaker_para = (
            '"Hold your fire," Reiko commanded. '
            '"Wait until they enter the primary killzone," Reiko added.'
        )
        report_single, _ = analyze_prose(single_speaker_para)
        self.assertIsNotNone(report_single)
        self.assertEqual(len(report_single["multi_speaker_paragraphs"]), 0)

        # Case D: Single emphasized word in italics + dialogue should NOT trigger mindspeech
        italic_word_para = (
            'Velvet drew her *Discidium* from the magnetic scabbard. '
            '"Stand down," she said.'
        )
        report_italic, _ = analyze_prose(italic_word_para)
        self.assertIsNotNone(report_italic)
        self.assertEqual(len(report_italic["multi_speaker_paragraphs"]), 0)

    def test_burstiness_and_paragraph_braiding(self):
        prose = (
            "# Scene 1\n\n"
            "The night market was cold.\n\n"
            "The drizzle fell steadily over the rusted corrugated roofs of Redmond. "
            "Neon signs flickered in the oily puddles along the curb. "
            "Velvet adjusted her coat collar against the sulfur breeze. "
            "Her cyber-optics calibrated the distance to the extraction vehicle.\n\n"
            "The drone hovered thirty meters above the intersection. "
            "Its sensor suite swept across the empty alleyway. "
            "Steam drifted from a broken heating conduit beneath the sidewalk. "
            "Shadows stretched long across the wet plasteel pavement.\n"
        )
        report, err = analyze_prose(prose)
        self.assertIsNone(err)
        self.assertIsNotNone(report)

        # Check paragraph counts
        self.assertEqual(report["paragraph_count"], 3)
        self.assertEqual(report["braided_paragraph_count"], 2)
        self.assertEqual(report["braided_ratio"], 66.7)

        # Check single-sentence paragraph detection
        self.assertEqual(len(report["single_sentence_paragraphs"]), 1)
        self.assertEqual(report["single_sentence_paragraphs"][0][1], "The night market was cold.")
        self.assertGreater(report["single_sentence_per_1k"], 0.0)

        # Check burstiness CV
        self.assertGreater(report["sentence_len_std"], 0.0)
        self.assertGreater(report["burstiness_cv"], 0.0)

    def test_cross_chapter_echo_window(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            ch1_path = os.path.join(tmpdir, "01_prologue.md")
            ch2_path = os.path.join(tmpdir, "02_descent.md")
            ch3_path = os.path.join(tmpdir, "03_breach.md")
            ch4_path = os.path.join(tmpdir, "04_standoff.md")

            shared_phrase = "rain drummed against the reinforced plasteel"

            with open(ch1_path, "w", encoding="utf-8") as f:
                f.write(f"# Chapter 1\n\nThe {shared_phrase} hull during the long night extraction.")
            with open(ch2_path, "w", encoding="utf-8") as f:
                f.write(f"# Chapter 2\n\nOutside the vehicle, {shared_phrase} barrier continuously.")
            with open(ch3_path, "w", encoding="utf-8") as f:
                f.write(f"# Chapter 3\n\nShe listened as {shared_phrase} shutters throughout the storm.")
            with open(ch4_path, "w", encoding="utf-8") as f:
                f.write(f"# Chapter 4\n\nIn the sanctuary, the {shared_phrase} frame groaned.")

            report, err = analyze_prose(ch4_path, window=3)
            self.assertIsNone(err)
            self.assertIsNotNone(report)

            echoes = report["cross_chapter_echoes"]
            self.assertGreater(len(echoes), 0)

            # Check that the shared phrase appears and references preceding chapters
            flagged_phrases = [e["phrase"] for e in echoes]
            self.assertTrue(any("reinforced plasteel" in p or "rain drummed" in p for p in flagged_phrases))

            matching_entry = next((e for e in echoes if "reinforced plasteel" in e["phrase"] or "rain drummed" in e["phrase"]), None)
            self.assertIsNotNone(matching_entry)
            self.assertGreaterEqual(len(matching_entry["chapters"]), 2)
            self.assertGreaterEqual(matching_entry["count_in_current"], 1)

    def test_mcp_output_formatting(self):
        prose = (
            "The neon light flickered against the damp brick wall. "
            "Lee Ji-yoo stood motionless beneath the rusted fire escape. "
            "Her cyber-optic focused on the entrance of the nightclub. "
            "Three security guards monitored the guest manifest.\n"
        )
        res = handle_lint_prose({"file_path": prose})
        self.assertIn("SR6 Narrative Evaluation Scorecard", res)
        self.assertIn("Readiness Status", res)
        self.assertIn("Sentence Burstiness", res)
        self.assertIn("Paragraph Braiding Ratio", res)
        self.assertIn("Single-Sentence Paragraphs", res)


if __name__ == "__main__":
    unittest.main()
