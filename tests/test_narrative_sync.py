"""
Unit tests for narrative synchronization and audio tag sniffing.
"""

import os
import tempfile
import unittest
from pathlib import Path
from sr6core.narrative.sync import sync_narrative_context, resolve_character_dir
from sr6core.narrative.linter import analyze_prose


class TestNarrativeSyncAndSniffing(unittest.TestCase):
    def test_resolve_character_dir(self):
        char_dir = resolve_character_dir("velvet")
        self.assertIsNotNone(char_dir)
        self.assertTrue(char_dir.exists())
        self.assertEqual(char_dir.name, "velvet")

    def test_sync_narrative_context_velvet(self):
        report, err = sync_narrative_context("velvet")
        self.assertIsNone(err)
        self.assertIsNotNone(report)
        self.assertEqual(report["character_id"], "velvet")
        self.assertGreaterEqual(report["chapter_count"], 12)
        self.assertGreater(report["total_words"], 15000)

        # Check Chapter 12 is in chapters list
        ch_12 = next((c for c in report["chapters"] if c["track"] == 12), None)
        self.assertIsNotNone(ch_12)
        self.assertEqual(ch_12["filename"], "12_Iron.md")
        self.assertEqual(ch_12["audio_file"], "12_Iron.mp3")

    def test_linter_detects_unicode_artifacts(self):
        text_with_corrupt_char = "# Chapter Title\n\nThis line has a corrupted char here: \ufffd and continues."
        report, err = analyze_prose(text_with_corrupt_char)
        self.assertIsNone(err)
        self.assertIsNotNone(report)
        self.assertIn("unicode_artifact_matches", report)
        self.assertEqual(len(report["unicode_artifact_matches"]), 1)
        self.assertEqual(report["unicode_artifact_matches"][0][0], 3)


if __name__ == "__main__":
    unittest.main()
