"""
Unit tests for TTS Audio Narration engine (cleaners, pronunciation rules, chunking, chapter detection).
"""

import unittest
from sr6core.narration import (
    clean_markdown_for_tts,
    clean_pronunciation,
    normalize_dialogue_cadence,
    split_into_narration_chunks,
    is_narrative_chapter,
)


class TestNarrationEngine(unittest.TestCase):
    def test_clean_markdown_for_tts(self):
        raw = "# Chapter 1\n\n![Image](foo.png)\nCheck out [this link](https://example.com) for details.\n\n---\n\n> Quoted text"
        cleaned = clean_markdown_for_tts(raw)
        self.assertNotIn("![Image]", cleaned)
        self.assertNotIn("https://example.com", cleaned)
        self.assertIn("this link", cleaned)
        self.assertIn("<SCENE_PAUSE>", cleaned)
        self.assertNotIn("# Chapter", cleaned)

    def test_clean_pronunciation(self):
        raw = "R-31-K-0 paid ¥500 for IC in Neo-Tokyo with Renraku."
        cleaned = clean_pronunciation(raw)
        self.assertIn("R 31 K 0", cleaned)
        self.assertIn("500 new yen", cleaned)
        self.assertIn("Ice", cleaned)
        self.assertIn("Neo Tokyo", cleaned)

    def test_normalize_dialogue_cadence(self):
        raw = "Wait -- what is -- that?"
        normalized = normalize_dialogue_cadence(raw)
        self.assertNotIn("--", normalized)

    def test_split_into_narration_chunks(self):
        text = "First sentence. Second sentence.\n\nSecond paragraph."
        chunks = split_into_narration_chunks(text, pacing="balanced")
        self.assertEqual(len(chunks), 3)
        self.assertEqual(chunks[0][0], "First sentence.")
        self.assertEqual(chunks[1][0], "Second sentence.")
        self.assertEqual(chunks[2][0], "Second paragraph.")

    def test_is_narrative_chapter(self):
        self.assertTrue(is_narrative_chapter("01 The Weight of Zero.md"))
        self.assertTrue(is_narrative_chapter("19 Distributed Ground.qmd"))
        self.assertFalse(is_narrative_chapter("dronomancy.md"))
        self.assertFalse(is_narrative_chapter("rules_combat.qmd"))


if __name__ == "__main__":
    unittest.main()
