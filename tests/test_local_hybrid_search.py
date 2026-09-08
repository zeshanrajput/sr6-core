"""
Unit tests for Local Hybrid Search (FTS5 + SQLite-Vec / Precomputed Embeddings + RRF).
Tests embedding generation, vector table creation, batch indexing, vector search, and RRF.
"""

import sqlite3
import pytest
import numpy as np

from sr6core.rag.embeddings import LocalEmbeddingEngine, VectorVault, EMBEDDING_DIM
from sr6core.rules_db import RulesDB


def test_embedding_engine_dimension_and_norm():
    engine = LocalEmbeddingEngine.get_instance()
    emb = engine.embed_text("healing fading damage technomancer")
    assert isinstance(emb, np.ndarray)
    assert emb.shape == (EMBEDDING_DIM,)
    assert emb.dtype == np.float32
    # Check unit norm (L2)
    norm = np.linalg.norm(emb)
    assert pytest.approx(norm, rel=1e-3) == 1.0


def test_vector_vault_lifecycle_in_memory():
    conn = sqlite3.connect(":memory:")
    # Ensure tables
    has_vec = VectorVault.ensure_tables(conn)
    cursor = conn.cursor()
    tables = [r[0] for r in cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    assert "rule_embeddings" in tables

    # Test batch indexing
    sample_rules = [
        {"id": "RULE-001", "topic": "Fading and Drain", "content": "Technomancers suffer fading damage when compiling sprites."},
        {"id": "RULE-002", "topic": "First Aid and Healing", "content": "Characters can heal physical damage using medical kits and first aid skills."},
        {"id": "RULE-003", "topic": "Recoil Compensation", "content": "Gas vent systems and heavy barrels reduce recoil penalties on automatic weapons."}
    ]
    VectorVault.index_rules_batch(conn, sample_rules, batch_size=2)

    # Verify rows in rule_embeddings
    count = cursor.execute("SELECT COUNT(*) FROM rule_embeddings").fetchone()[0]
    assert count == 3

    # Test vector search
    results = VectorVault.search_vector(conn, "how to treat wounds and heal physical injury", limit=2)
    assert len(results) > 0
    top_hit = results[0]
    assert top_hit["id"] == "RULE-002"

    conn.close()


def test_reciprocal_rank_fusion():
    kw_hits = [
        {"id": "A", "score": 10.0},
        {"id": "B", "score": 8.0},
        {"id": "C", "score": 5.0}
    ]
    vec_hits = [
        {"id": "B", "score": 0.95},
        {"id": "D", "score": 0.85},
        {"id": "A", "score": 0.70}
    ]
    fused = VectorVault.reciprocal_rank_fusion(kw_hits, vec_hits, rrf_k=60, limit=3)
    assert len(fused) == 3
    # B appeared high in both (#2 and #1), so it should rank highest in fused RRF
    assert fused[0]["id"] == "B"
    assert "rrf_score" in fused[0]


def test_rules_db_hybrid_search():
    db = RulesDB()
    # Test conceptual question search with semantic enabled
    results = db.search_rules("how do I heal fading damage", limit=5, enable_semantic=True)
    assert isinstance(results, list)
    assert len(results) > 0
