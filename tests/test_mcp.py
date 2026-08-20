"""
Unit tests for the SR6 Core MCP JSON-RPC Server in sr6core.mcp.
"""

import json
import unittest
from unittest.mock import patch, MagicMock
from sr6core.mcp import (
    TOOLS_DEFINITIONS,
    RESOURCES_DEFINITIONS,
    PROMPTS_DEFINITIONS,
    TOOL_HANDLERS,
    handle_search_rules,
    handle_lint_prose,
    handle_audit_character,
    handle_check_continuity,
    handle_get_item_card,
    handle_evaluate_draft,
    handle_parse_combat_ledger,
    handle_read_resource,
    handle_get_prompt,
)


class TestMCPServer(unittest.TestCase):
    def test_tool_definitions_structure(self):
        self.assertGreaterEqual(len(TOOLS_DEFINITIONS), 8)
        tool_names = [t["name"] for t in TOOLS_DEFINITIONS]
        self.assertIn("sr6_search_rules", tool_names)
        self.assertIn("sr6_query_rag", tool_names)
        self.assertIn("sr6_lint_prose", tool_names)
        self.assertIn("sr6_evaluate_draft", tool_names)
        self.assertIn("sr6_parse_combat_ledger", tool_names)
        self.assertIn("sr6_audit_character", tool_names)
        self.assertIn("sr6_check_continuity", tool_names)
        self.assertIn("sr6_get_item_card", tool_names)

        for t in TOOLS_DEFINITIONS:
            self.assertIn("name", t)
            self.assertIn("description", t)
            self.assertIn("inputSchema", t)
            self.assertEqual(t["inputSchema"]["type"], "object")

    def test_resources_and_prompts_definitions(self):
        self.assertGreaterEqual(len(RESOURCES_DEFINITIONS), 4)
        uris = [r["uri"] for r in RESOURCES_DEFINITIONS]
        self.assertIn("sr6://campaign/contacts", uris)
        self.assertIn("sr6://rules/summary", uris)

        self.assertGreaterEqual(len(PROMPTS_DEFINITIONS), 3)
        prompt_names = [p["name"] for p in PROMPTS_DEFINITIONS]
        self.assertIn("sr6_audit_chapter", prompt_names)
        self.assertIn("sr6_draft_scene", prompt_names)
        self.assertIn("sr6_sync_portfolio", prompt_names)

    @patch("sr6core.rules_db.RulesDB")
    def test_handle_search_rules(self, mock_rules_db_cls):
        mock_db = MagicMock()
        mock_rules_db_cls.return_value = mock_db
        mock_db.get_enriched_item.return_value = {
            "name": "Ambidextrous",
            "id": "ambidextrous",
            "item_type": "quality",
            "commlink_data": {"karma": 4},
            "rules_vault": {"source": "SR6", "page": 68, "authority_level": 1, "content": "No off-hand penalty."}
        }

        res = handle_search_rules({"query": "ambidextrous"})
        self.assertIn("Ambidextrous", res)
        self.assertIn("CommLink6 Stats", res)
        self.assertIn("SR6", res)

    @patch("sr6core.linter.analyze_prose")
    def test_handle_lint_prose(self, mock_analyze_prose):
        mock_analyze_prose.return_value = ({
            "word_count": 1500,
            "ellipses_count": 2,
            "ellipses_per_300": 0.40,
            "ellipses_valid": True,
            "buzzwords_found": [],
            "cognitive_buffers_found": [],
            "redlines": []
        }, None)

        res = handle_lint_prose({"file_path": "chapters/test.qmd"})
        self.assertIn("1,500 words", res)
        self.assertIn("[PASS]", res)

    def test_handle_evaluate_draft(self):
        draft = "The rain drummed against the plasteel window. Mitsuhama patrol cruisers floated past. Dermal plating humming."
        res = handle_evaluate_draft({"text_or_path": draft, "tier": 2})
        self.assertIn("SR6 Narrative Evaluation Scorecard", res)

    def test_handle_parse_combat_ledger(self):
        draft = "Yuriko fired 4 APDS rounds and took 2 boxes of physical damage."
        res = handle_parse_combat_ledger({"text_or_path": draft})
        self.assertIn("Tabletop Action & Combat Ledger Report", res)
        self.assertIn("apds: -4", res)

    def test_handle_read_resource(self):
        res = handle_read_resource("sr6://campaign/contacts")
        self.assertIsNotNone(res)
        self.assertEqual(res["mimeType"], "application/json")
        self.assertIn("contacts", res["uri"])

    def test_handle_get_prompt(self):
        p = handle_get_prompt("sr6_audit_chapter", {"file_path": "chapters/test.qmd", "tier": "1"})
        self.assertIsNotNone(p)
        self.assertIn("messages", p)
        self.assertIn("chapters/test.qmd", p["messages"][0]["content"]["text"])


if __name__ == "__main__":
    unittest.main()
