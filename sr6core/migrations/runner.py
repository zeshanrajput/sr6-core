"""
Centralized SQLite Schema Migration Runner for SR6 Core.
Uses PRAGMA user_version to track and sequentially execute migrations.
"""

import sqlite3
import logging
from typing import List, Callable, Tuple

logger = logging.getLogger(__name__)


def _table_has_column(conn: sqlite3.Connection, table: str, column: str) -> bool:
    try:
        cursor = conn.cursor()
        cols = [row[1] for row in cursor.execute(f"PRAGMA table_info({table})").fetchall()]
        return column in cols
    except Exception:
        return False


def _migration_001_core_rules(conn: sqlite3.Connection):
    """Initial core rules, FTS5 index, dataset meta, and CommLink6 ref tables."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS rules (
            id TEXT PRIMARY KEY,
            topic TEXT,
            chapter TEXT,
            source TEXT,
            page TEXT,
            authority_level INTEGER DEFAULT 3,
            tags TEXT,
            content TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sub_items (
            id TEXT,
            name TEXT,
            namespace TEXT,
            content TEXT,
            PRIMARY KEY (id, name)
        )
    """)
    try:
        conn.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS rules_fts USING fts5(
                id, topic, chapter, tags, content
            )
        """)
    except sqlite3.OperationalError:
        pass

    conn.execute("""
        CREATE TABLE IF NOT EXISTS dataset_meta (
            id TEXT PRIMARY KEY,
            name TEXT,
            version TEXT,
            commlink_version TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    ref_tables = {
        "ref_qualities": """
            id TEXT PRIMARY KEY,
            name TEXT,
            karma INTEGER,
            category TEXT,
            description TEXT,
            source TEXT,
            raw_xml TEXT,
            modifiers_json TEXT
        """,
        "ref_spells": """
            id TEXT PRIMARY KEY,
            name TEXT,
            category TEXT,
            duration TEXT,
            range TEXT,
            type TEXT,
            damage TEXT,
            drain TEXT,
            description TEXT,
            source TEXT,
            raw_xml TEXT,
            modifiers_json TEXT
        """,
        "ref_complex_forms": """
            id TEXT PRIMARY KEY,
            name TEXT,
            duration TEXT,
            target TEXT,
            fading TEXT,
            description TEXT,
            source TEXT,
            raw_xml TEXT,
            modifiers_json TEXT
        """,
        "ref_gear": """
            id TEXT PRIMARY KEY,
            name TEXT,
            category TEXT,
            rating TEXT,
            cost INTEGER,
            avail TEXT,
            description TEXT,
            source TEXT,
            raw_xml TEXT,
            modifiers_json TEXT
        """,
        "ref_weapons": """
            id TEXT PRIMARY KEY,
            name TEXT,
            category TEXT,
            damage TEXT,
            ap TEXT,
            attack_rating TEXT,
            modes TEXT,
            ammo TEXT,
            cost INTEGER,
            avail TEXT,
            source TEXT,
            raw_xml TEXT,
            modifiers_json TEXT
        """,
        "ref_cyberware": """
            id TEXT PRIMARY KEY,
            name TEXT,
            category TEXT,
            grade TEXT,
            essence REAL,
            cost INTEGER,
            avail TEXT,
            description TEXT,
            source TEXT,
            raw_xml TEXT,
            modifiers_json TEXT
        """,
        "ref_adept_powers": """
            id TEXT PRIMARY KEY,
            name TEXT,
            cost REAL,
            max_levels TEXT,
            action TEXT,
            description TEXT,
            source TEXT,
            raw_xml TEXT,
            modifiers_json TEXT
        """,
        "ref_vehicles": """
            id TEXT PRIMARY KEY,
            name TEXT,
            category TEXT,
            handling TEXT,
            speed TEXT,
            accel TEXT,
            body INTEGER,
            armor INTEGER,
            pilot INTEGER,
            sensor INTEGER,
            seats TEXT,
            cost INTEGER,
            avail TEXT,
            source TEXT,
            raw_xml TEXT,
            modifiers_json TEXT
        """,
        "ref_programs": """
            id TEXT PRIMARY KEY,
            name TEXT,
            category TEXT,
            cost INTEGER,
            avail TEXT,
            description TEXT,
            source TEXT,
            raw_xml TEXT,
            modifiers_json TEXT
        """,
        "ref_metatypes": """
            id TEXT PRIMARY KEY,
            name TEXT,
            karma_cost INTEGER,
            abilities TEXT,
            source TEXT,
            raw_xml TEXT,
            modifiers_json TEXT
        """
    }

    for tbl_name, schema in ref_tables.items():
        conn.execute(f"CREATE TABLE IF NOT EXISTS {tbl_name} ({schema})")
        if not _table_has_column(conn, tbl_name, "modifiers_json"):
            try:
                conn.execute(f"ALTER TABLE {tbl_name} ADD COLUMN modifiers_json TEXT")
            except Exception:
                pass

    # Ensure rules columns exist for legacy databases
    for col, col_type in [("page", "TEXT"), ("authority_level", "INTEGER DEFAULT 3"), ("tags", "TEXT")]:
        if not _table_has_column(conn, "rules", col):
            try:
                conn.execute(f"ALTER TABLE rules ADD COLUMN {col} {col_type}")
            except Exception:
                pass


def _migration_002_gameplay_tables(conn: sqlite3.Connection):
    """Seed & relational tables for Action Economy, Status Effects, and Edge Boosts."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS ref_actions (
            id TEXT PRIMARY KEY,
            name TEXT,
            action_type TEXT,
            category TEXT,
            test TEXT,
            opposed TEXT,
            threshold TEXT,
            description TEXT,
            source TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS ref_status_effects (
            id TEXT PRIMARY KEY,
            name TEXT,
            severity_levels TEXT,
            category TEXT,
            test TEXT,
            recovery_test TEXT,
            mechanical_effect TEXT,
            source TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS ref_edge_boosts (
            id TEXT PRIMARY KEY,
            name TEXT,
            cost INTEGER,
            category TEXT,
            trigger TEXT,
            timing TEXT,
            mechanical_effect TEXT,
            source TEXT
        )
    """)

    # Populate seed data if empty
    try:
        from sr6core.gameplay_tables import ACTIONS_DATA, STATUS_EFFECTS_DATA, EDGE_BOOSTS_DATA
        row = conn.execute("SELECT COUNT(*) FROM ref_actions").fetchone()
        if not row or row[0] == 0:
            for item in ACTIONS_DATA:
                conn.execute(
                    """INSERT OR REPLACE INTO ref_actions 
                       (id, name, action_type, category, test, opposed, threshold, description, source)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (item["id"], item["name"], item["action_type"], item["category"],
                     item["test"], item["opposed"], item["threshold"], item["description"], item["source"])
                )
            for item in STATUS_EFFECTS_DATA:
                conn.execute(
                    """INSERT OR REPLACE INTO ref_status_effects
                       (id, name, severity_levels, category, test, recovery_test, mechanical_effect, source)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (item["id"], item["name"], item["severity_levels"], item["category"],
                     item["test"], item["recovery_test"], item["mechanical_effect"], item["source"])
                )
            for item in EDGE_BOOSTS_DATA:
                conn.execute(
                    """INSERT OR REPLACE INTO ref_edge_boosts
                       (id, name, cost, category, trigger, timing, mechanical_effect, source)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (item["id"], item["name"], item["cost"], item["category"],
                     item["trigger"], item["timing"], item["mechanical_effect"], item["source"])
                )
    except Exception as e:
        logger.warning(f"Could not populate gameplay table seeds: {e}")


def _migration_003_srm_contacts_and_rulings(conn: sqlite3.Connection):
    """SRM Named Contacts and SRM official FAQ rulings."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS ref_contacts (
            id TEXT PRIMARY KEY,
            name TEXT,
            archetypes TEXT,
            connection INTEGER,
            loyalty INTEGER,
            source TEXT,
            notes TEXT,
            services TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS srm_rulings (
            id TEXT PRIMARY KEY,
            category TEXT,
            topic TEXT,
            ruling TEXT,
            source TEXT,
            page TEXT,
            authority_level INTEGER DEFAULT 2
        )
    """)


def _migration_004_rule_embeddings(conn: sqlite3.Connection):
    """Embeddings storage table for offline hybrid search."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS rule_embeddings (
            rule_id TEXT PRIMARY KEY,
            embedding BLOB
        )
    """)


MIGRATIONS: List[Tuple[int, str, Callable[[sqlite3.Connection], None]]] = [
    (1, "001_core_rules", _migration_001_core_rules),
    (2, "002_gameplay_tables", _migration_002_gameplay_tables),
    (3, "003_srm_contacts_and_rulings", _migration_003_srm_contacts_and_rulings),
    (4, "004_rule_embeddings", _migration_004_rule_embeddings),
]


def get_schema_version(conn: sqlite3.Connection) -> int:
    """Returns current PRAGMA user_version."""
    try:
        cursor = conn.cursor()
        row = cursor.execute("PRAGMA user_version").fetchone()
        return row[0] if row else 0
    except Exception:
        return 0


def run_migrations(conn: sqlite3.Connection) -> int:
    """
    Executes pending migrations in ascending order and updates PRAGMA user_version.
    Returns final schema version.
    """
    current_version = get_schema_version(conn)

    for version, name, func in MIGRATIONS:
        if version > current_version:
            logger.info(f"Applying migration {version} ({name})...")
            with conn:
                func(conn)
                conn.execute(f"PRAGMA user_version = {version}")
            current_version = version

    return current_version
