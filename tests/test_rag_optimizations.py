"""
Unit and integration tests for RAG search optimizations, card generation, and compact rendering.
"""

from sr6core.rules_db import RulesDB
from sr6core.cards import get_item_card
from sr6core.oids import resolve_canonical_oid


def test_fts5_stop_word_search():
    db = RulesDB()
    results = db.search_rules("raising nanite volume with karma", limit=5)
    assert len(results) > 0
    # Top result should be Monad / Whisper Nets exception
    top_id = results[0]["id"]
    assert "SRMG" in top_id or "WN" in top_id or "CN" in top_id


def test_universal_card_auto_detection():
    # 1. Bioware with rating formula
    card1 = get_item_card(None, "Cerebellum Booster")
    assert card1["name"] == "Cerebellum Booster"
    assert "Rating" in str(card1["stats"].get("essence"))

    # 2. Cyberware
    card2 = get_item_card("auto", "Skillwires")
    assert "skillwires" in card2["id"]

    # 3. Geneware / Enhancer
    card3 = get_item_card(None, "Cerebral Booster Enhancer")
    assert "0.2" in str(card3["stats"].get("essence"))


def test_direct_rule_get():
    db = RulesDB()
    rule = db.get_rule_by_topic_or_id("BS-0222")
    assert rule is not None
    assert "Cerebellum Booster" in rule["topic"]
    assert "Intuition" in rule["content"]
