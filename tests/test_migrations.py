"""
Unit tests for Centralized SQLite Migration Runner.
"""

import sqlite3
import pytest
from sr6core.migrations.runner import run_migrations, get_schema_version, MIGRATIONS


def test_migrations_fresh_db():
    conn = sqlite3.connect(":memory:")
    assert get_schema_version(conn) == 0

    final_version = run_migrations(conn)
    assert final_version == len(MIGRATIONS)
    assert get_schema_version(conn) == len(MIGRATIONS)

    # Verify tables created
    cursor = conn.cursor()
    tables = [row[0] for row in cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    
    assert "rules" in tables
    assert "sub_items" in tables
    assert "ref_qualities" in tables
    assert "ref_spells" in tables
    assert "ref_weapons" in tables
    assert "ref_actions" in tables
    assert "ref_status_effects" in tables
    assert "ref_edge_boosts" in tables
    assert "ref_contacts" in tables
    assert "srm_rulings" in tables
    assert "rule_embeddings" in tables

    # Verify column presence
    q_cols = [r[1] for r in cursor.execute("PRAGMA table_info(ref_qualities)").fetchall()]
    assert "modifiers_json" in q_cols

    w_cols = [r[1] for r in cursor.execute("PRAGMA table_info(ref_weapons)").fetchall()]
    assert "modifiers_json" in w_cols

    # Idempotency test: Running again changes nothing
    assert run_migrations(conn) == len(MIGRATIONS)
    assert get_schema_version(conn) == len(MIGRATIONS)


def test_migrations_legacy_upgrade():
    conn = sqlite3.connect(":memory:")
    # Simulate legacy table without modifiers_json or user_version
    conn.execute("CREATE TABLE ref_weapons (id TEXT PRIMARY KEY, name TEXT)")
    assert get_schema_version(conn) == 0

    run_migrations(conn)
    assert get_schema_version(conn) == len(MIGRATIONS)

    cursor = conn.cursor()
    cols = [r[1] for r in cursor.execute("PRAGMA table_info(ref_weapons)").fetchall()]
    assert "modifiers_json" in cols
