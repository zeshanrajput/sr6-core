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
        raw = '# Chapter 1\n\n![Image](foo.png)\n"You downed a helicopter?" she asked.\n\n*What is the encryption level?* Nathan asked.\n\n*Rating 3 maglock,* Veronica replied.\n\nCheck out [this link](https://example.com) for details.\n\n---\n\n> Quoted text'
        cleaned = clean_markdown_for_tts(raw)
        self.assertNotIn("![Image]", cleaned)
        self.assertNotIn("https://example.com", cleaned)
        self.assertIn('"You downed a helicopter?" she asked.', cleaned)
        self.assertIn('"What is the encryption level?" Nathan asked.', cleaned)
        self.assertIn('"Rating 3 maglock," Veronica replied.', cleaned)
        self.assertIn("this link", cleaned)
        self.assertIn("<SCENE_PAUSE>", cleaned)
        self.assertNotIn("# Chapter", cleaned)

    def test_clean_pronunciation_breathed_and_mechs(self):
        raw = "She breathed deeply near the warmech and biomech units in the battlemech hangar."
        cleaned = clean_pronunciation(raw)
        self.assertIn("breethed", cleaned)
        self.assertIn("warmek", cleaned)
        self.assertIn("biomek", cleaned)
        self.assertIn("battlemek", cleaned)

    def test_clean_pronunciation(self):
        raw = "Reiko's deck at r3sP@wn's grid wasn't working with Rei-chan and Yuriko-san. AGENT_OF_ORDER / SANITIZE_INPUT. I'll be fine."
        cleaned = clean_pronunciation(raw)
        self.assertIn("Rayko's", cleaned)
        self.assertIn("respawn's", cleaned)
        self.assertIn("was not", cleaned)
        self.assertIn("Rei chahn", cleaned)
        self.assertIn("Yooreeko sahn", cleaned)
        self.assertIn("AGENT OF ORDER. SANITIZE INPUT.", cleaned)
        self.assertIn("I'll", cleaned)

    def test_clean_pronunciation_credsticks_and_lore(self):
        raw = "Three certified credsticks lay beside a single credstick in Sham Shui Po. Kwai Chung lot CT4 near the Wuxing Skytower. Kang Anning practiced Daesul."
        cleaned = clean_pronunciation(raw)
        self.assertIn("cred sticks", cleaned)
        self.assertIn("cred stick", cleaned)
        self.assertIn("Shahm Shooee Poh", cleaned)
        self.assertIn("Kwye Chung", cleaned)
        self.assertIn("Sky Tower", cleaned)
        self.assertIn("Kahng Ahn ning", cleaned)
        self.assertIn("Day sool", cleaned)

    def test_normalize_dialogue_cadence(self):
        raw = "Wait -- what is -- that?"
        normalized = normalize_dialogue_cadence(raw)
        self.assertNotIn("--", normalized)

    def test_split_into_narration_chunks(self):
        text = "First sentence. Second sentence.\n\n<SCENE_PAUSE>\n\nSecond paragraph."
        chunks = split_into_narration_chunks(text, pacing="balanced")
        self.assertEqual(len(chunks), 4)
        self.assertEqual(chunks[0][0], "First sentence.")
        self.assertEqual(chunks[1][0], "Second sentence.")
        self.assertEqual(chunks[2][0], "")
        self.assertEqual(chunks[2][1], 1.0)
        self.assertEqual(chunks[3][0], "Second paragraph.")

    def test_is_narrative_chapter(self):
        self.assertTrue(is_narrative_chapter("01 The Weight of Zero.md"))
        self.assertTrue(is_narrative_chapter("19 Distributed Ground.qmd"))
        self.assertFalse(is_narrative_chapter("dronomancy.md"))
        self.assertFalse(is_narrative_chapter("rules_combat.qmd"))


if __name__ == "__main__":
    unittest.main()
