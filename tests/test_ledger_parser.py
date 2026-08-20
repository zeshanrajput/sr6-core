"""
Unit tests for the Combat Ledger Parser in sr6core.ledger_parser.
"""

import unittest
from sr6core.ledger_parser import parse_combat_ledger_prose, format_ledger_patch_markdown


class TestLedgerParser(unittest.TestCase):
    def test_parse_ammo_and_damage(self):
        combat_prose = """
Yuriko fired 6 APDS rounds at the Mitsuhama drone.
The return burst caught her shoulder; she took 3 boxes of physical damage.
Resisting the spell fading, she took 2 boxes of stun drain.
At the end of the run, she earned 7 Karma and 15,000 Nuyen.
"""
        report = parse_combat_ledger_prose(combat_prose)
        self.assertEqual(report["ammo_spent"].get("APDS"), 6)
        self.assertEqual(report["damage_taken"]["physical"], 3)
        self.assertEqual(report["damage_taken"]["drain_stun"], 2)
        self.assertEqual(report["karma_delta"], 7)
        self.assertEqual(report["nuyen_delta"], 15000)
        self.assertTrue(report["has_changes"])

        diff_md = format_ledger_patch_markdown(report)
        self.assertIn("Tabletop Action & Combat Ledger Report", diff_md)
        self.assertIn("apds: -6", diff_md)
        self.assertIn("physical_wounds_add: +3", diff_md)

    def test_parse_embedded_quarto_cells(self):
        quarto_prose = """
```{python}
inc('Karma', 8)
inc('Nuyen', 25000)
inc('ammo_gel', -12)
```
"""
        report = parse_combat_ledger_prose(quarto_prose)
        self.assertEqual(report["karma_delta"], 8)
        self.assertEqual(report["nuyen_delta"], 25000)
        self.assertEqual(report["ammo_spent"].get("ammo_gel"), 12)


if __name__ == "__main__":
    unittest.main()
