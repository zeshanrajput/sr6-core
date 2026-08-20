"""
Unit tests for the 7-Axis Narrative Evaluator in sr6core.evaluator.
"""

import unittest
from sr6core.evaluator import evaluate_chapter_draft, format_scorecard_markdown


class TestEvaluator(unittest.TestCase):
    def test_evaluate_clean_prose(self):
        sample_prose = """
The rain drummed against the reinforced plasteel window of the Redmond dive bar.
Yuriko adjusted the optical filter on her cybereye, watching the Mitsuhama patrol cruiser drift past in the neon haze.
Her dermal plating felt warm under her leather coat as the actuator in her right elbow clicked into position.

She had planned this dead-drop for three days. There was no point in waiting for backup.
She slid the encrypted datachip across the scuffed synthetic tabletop toward the fixer.
"Take it or leave it," she said, her laryngeal modulator keeping her vocal timbre calm.
"""
        report = evaluate_chapter_draft(sample_prose, tier=2)
        self.assertIn("axis-voice-internality", report["scores"])
        self.assertIn("axis-pacing-structure", report["scores"])
        self.assertIn("axis-worldbuilding-grit", report["scores"])
        self.assertIn("no-ai-slop", report["scores"])
        self.assertGreaterEqual(report["overall_score"], 8.0)

        markdown = format_scorecard_markdown(report)
        self.assertIn("SR6 Narrative Evaluation Scorecard", markdown)
        self.assertIn("axis-worldbuilding-grit", markdown)

    def test_evaluate_buzzword_redlines(self):
        slop_prose = """
A testament to the tapestry of the sprawl, the city stood as a beacon.
She delved deep into the palpable mystery amidst the neon symphony.
"""
        report = evaluate_chapter_draft(slop_prose, tier=1)
        self.assertFalse(report["passed"])
        self.assertLess(report["scores"]["no-ai-slop"], 9.0)
        self.assertTrue(len(report["redlines"]) > 0)


if __name__ == "__main__":
    unittest.main()
