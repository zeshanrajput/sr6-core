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
            capacity TEXT,
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

    # Ensure v_cyberware_grades view exists
    try:
        conn.execute("""
            CREATE VIEW IF NOT EXISTS v_cyberware_grades AS
            SELECT 
                id,
                name,
                category,
                essence AS standard_essence,
                cost AS standard_cost,
                0 AS standard_avail_mod,
                ROUND(essence * 1.1, 2) AS used_essence,
                CAST(ROUND(cost * 0.5) AS INTEGER) AS used_cost,
                -1 AS used_avail_mod,
                ROUND(essence * 0.8, 2) AS alpha_essence,
                CAST(ROUND(cost * 1.2) AS INTEGER) AS alpha_cost,
                1 AS alpha_avail_mod,
                ROUND(essence * 0.7, 2) AS beta_essence,
                CAST(ROUND(cost * 1.5) AS INTEGER) AS beta_cost,
                2 AS beta_avail_mod,
                ROUND(essence * 0.5, 2) AS delta_essence,
                CAST(ROUND(cost * 2.5) AS INTEGER) AS delta_cost,
                3 AS delta_avail_mod,
                ROUND(essence * 1.1, 2) AS exoware_essence,
                CAST(ROUND(cost * 0.8) AS INTEGER) AS exoware_cost,
                0 AS exoware_avail_mod,
                capacity,
                avail,
                source,
                modifiers_json
            FROM ref_cyberware;
        """)
    except Exception:
        pass

    # Ensure rules columns exist for legacy databases
    for col, col_type in [("page", "TEXT"), ("authority_level", "INTEGER DEFAULT 3"), ("tags", "TEXT")]:
        if not _table_has_column(conn, "rules", col):
            try:
                conn.execute(f"ALTER TABLE rules ADD COLUMN {col} {col_type}")
            except Exception:
                pass

    # Populate minimal canonical reference seeds if tables are empty
    try:
        row = conn.execute("SELECT COUNT(*) FROM ref_weapons").fetchone()
        if not row or row[0] == 0:
            conn.execute(
                """INSERT OR REPLACE INTO ref_weapons 
                   (id, name, category, damage, ap, attack_rating, modes, ammo, cost, avail, source, raw_xml)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                ("ares_predator_vi", "Ares Predator VI", "Heavy Pistols", "3P", "-", "10/10/8/-/-", "SA", "15(c)", 750, "3", "SR6 Core p. 256",
                 '<weapon id="ares_predator_vi" dmg="3P" attack="10,10,8" mode="SA" ammo="15(c)"/>')
            )
            conn.execute(
                """INSERT OR REPLACE INTO ref_weapons 
                   (id, name, category, damage, ap, attack_rating, modes, ammo, cost, avail, source, raw_xml)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                ("ares_alpha", "Ares Alpha", "Assault Rifles", "4P", "-", "4/11/9/7/2", "SA/BF/FA", "42(c)", 2650, "4", "SR6 Core p. 257",
                 '<weapon id="ares_alpha" dmg="4P" attack="4,11,9,7,2" mode="SA/BF/FA" ammo="42(c)"/>')
            )
            conn.execute(
                """INSERT OR REPLACE INTO ref_weapons 
                   (id, name, category, damage, ap, attack_rating, modes, ammo, cost, avail, source, raw_xml)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                ("ruger_super_warhawk", "Ruger Super Warhawk", "Heavy Pistols", "4P", "-", "10/9/6/-/-", "SS", "6(cy)", 450, "2", "SR6 Core p. 256",
                 '<weapon id="ruger_super_warhawk" dmg="4P" attack="10,9,6" mode="SS" ammo="6(cy)"/>')
            )

        # Ensure canonical supplement weapons (e.g. Firing Squad laser weapons) exist
        conn.execute(
            """INSERT OR IGNORE INTO ref_weapons 
               (id, name, category, damage, ap, attack_rating, modes, ammo, cost, avail, source, raw_xml)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            ("red_fox", "rEVOlution Arms Red Fox", "Energy Weapons", "6P", "-", "14/16/16/9/-", "SA/BF", "30(c)", 2800, "6(I)", "Firing Squad p. 116",
             '<weapon id="red_fox" name="rEVOlution Arms Red Fox" cat="Energy Weapons" dmg="6P" attack="14,16,16,9" mode="SA/BF" ammo="30(c)" cost="2800" avail="6(I)" src="FS 116"/>')
        )
        conn.execute(
            """INSERT OR IGNORE INTO ref_weapons 
               (id, name, category, damage, ap, attack_rating, modes, ammo, cost, avail, source, raw_xml)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            ("crimson_wasp", "rEVOlution Arms Crimson Wasp", "Energy Weapons", "5P", "-", "16/14/11/6/-", "SA", "15(c)", 1500, "6(I)", "Firing Squad p. 116",
             '<weapon id="crimson_wasp" name="rEVOlution Arms Crimson Wasp" cat="Energy Weapons" dmg="5P" attack="16,14,11,6" mode="SA" ammo="15(c)" cost="1500" avail="6(I)" src="FS 116"/>')
        )
        row_sp = conn.execute("SELECT COUNT(*) FROM ref_spells").fetchone()
        if not row_sp or row_sp[0] == 0:
            conn.execute(
                """INSERT OR REPLACE INTO ref_spells 
                   (id, name, category, duration, range, type, damage, drain, description, source, raw_xml)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                ("manabolt", "Manabolt", "Combat", "Instant", "LOS", "Mana", "P", "4", "A direct combat spell that channels raw mana.", "SR6 Core p. 135",
                 '<spell id="manabolt" cat="Combat" drain="4" type="M" range="LOS" dur="I" dmg="P"><spellfeature ref="direct"/></spell>')
            )
            conn.execute(
                """INSERT OR REPLACE INTO ref_spells 
                   (id, name, category, duration, range, type, damage, drain, description, source, raw_xml)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                ("fireball", "Fireball", "Combat", "Instant", "LOS (A)", "Physical", "P", "5", "An indirect combat spell that explodes in flame.", "SR6 Core p. 134",
                 '<spell id="fireball" cat="Combat" drain="5" type="P" range="LOS (A)" dur="I" dmg="P"><spellfeature ref="indirect"/><spellfeature ref="area"/></spell>')
            )
        row_cw = conn.execute("SELECT COUNT(*) FROM ref_cyberware").fetchone()
        if not row_cw or row_cw[0] == 0:
            conn.execute(
                """INSERT OR REPLACE INTO ref_cyberware 
                   (id, name, category, grade, essence, cost, avail, capacity, description, source, raw_xml, modifiers_json)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                ("wired_reflexes", "Wired Reflexes", "Bodyware", "standard", 2.0, 39000, "3", "-", "Neural accelerators grant reaction and initiative.", "SR6 Core p. 284",
                 '<item id="wired_reflexes"><usage mode="IMPLANTED" value="2.0"/><attrdef id="PRICE" table="39000"/><bonus><attribute name="REACTION" value="1"/><attribute name="INITIATIVE_DICE" value="1"/></bonus></item>',
                 '[{"type": "attribute", "ref": "reaction", "value": 1}, {"type": "attribute", "ref": "initiative_dice", "value": 1}]')
            )
            conn.execute(
                """INSERT OR REPLACE INTO ref_cyberware 
                   (id, name, category, grade, essence, cost, avail, description, source, raw_xml, modifiers_json)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                ("cybereyes", "Cybereyes", "Eyeware", "standard", 0.3, 6000, "2", "Replacement cybernetic optical sensors.", "SR6 Core p. 282",
                 '<item id="cybereyes"><usage mode="IMPLANTED" value="0.3"/><attrdef id="PRICE" table="6000"/></item>',
                 '[]')
            )
        row_q = conn.execute("SELECT COUNT(*) FROM ref_qualities").fetchone()
        if not row_q or row_q[0] == 0:
            conn.execute(
                """INSERT OR REPLACE INTO ref_qualities 
                   (id, name, karma, category, description, source, raw_xml, modifiers_json)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                ("quick_healer", "Quick Healer", 4, "Positive", "Gain +2 dice on healing tests.", "SR6 Core p. 74", '<quality id="quick_healer"/>', '[]')
            )
            conn.execute(
                """INSERT OR REPLACE INTO ref_qualities 
                   (id, name, karma, category, description, source, raw_xml, modifiers_json)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                ("sinner", "SINner", -8, "Negative", "Possesses a System Identification Number.", "SR6 Core p. 79", '<quality id="sinner"/>', '[]')
            )
        row_g = conn.execute("SELECT COUNT(*) FROM ref_gear").fetchone()
        if not row_g or row_g[0] == 0:
            conn.execute(
                """INSERT OR REPLACE INTO ref_gear 
                   (id, name, category, rating, cost, avail, description, source, raw_xml, modifiers_json)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                ("medkit", "Medkit", "Biotech", "3", 1500, "2", "Portable medical stabilization kit.", "SR6 Core p. 269", '<gear id="medkit"/>', '[]')
            )
    except Exception as e:
        logger.warning(f"Could not populate baseline reference seeds: {e}")


def _migration_002_gameplay_tables(conn: sqlite3.Connection):
    """Seed & relational tables for Action Economy, Status Effects, and Edge Boosts."""
    try:
        from sr6core.gameplay_tables import populate_gameplay_tables
        populate_gameplay_tables(conn)
    except Exception as e:
        logger.warning(f"Could not populate gameplay table seeds: {e}")


def _migration_003_srm_contacts_and_rulings(conn: sqlite3.Connection):
    """SRM Named Contacts and SRM official FAQ rulings."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS ref_contacts (
            id TEXT PRIMARY KEY,
            name TEXT,
            connection INTEGER,
            archetype TEXT,
            region TEXT,
            types TEXT,
            uses TEXT,
            source TEXT,
            city TEXT,
            season TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS srm_rulings (
            id TEXT PRIMARY KEY,
            category TEXT,
            topic TEXT,
            rule_or_item_id TEXT,
            ruling TEXT,
            source TEXT,
            applies_to TEXT,
            status TEXT,
            page TEXT,
            authority_level INTEGER DEFAULT 2
        )
    """)

    try:
        from sr6core.srm_contacts import OFFICIAL_SRM_CONTACTS
        row = conn.execute("SELECT COUNT(*) FROM ref_contacts").fetchone()
        if not row or row[0] == 0:
            for c in OFFICIAL_SRM_CONTACTS:
                city = c.get("city") or c.get("region", "Seattle").split("/")[0].strip()
                region_low = c.get("region", "").lower()
                source_low = c.get("source", "").lower()
                if "neo-tokyo" in region_low or "neo tokyo" in region_low or "tokyo" in region_low:
                    season = c.get("season") or "Season 9 (Neo-Tokyo)"
                    city = "Neo-Tokyo"
                elif "chicago" in region_low:
                    season = c.get("season") or "Season 8 (Chicago)"
                    city = "Chicago"
                elif "seattle" in region_low or "2081" in source_low:
                    season = c.get("season") or "Season 10 (Seattle 2081)"
                    city = "Seattle"
                else:
                    season = c.get("season") or "SRM Global / Special"
                conn.execute(
                    """INSERT OR REPLACE INTO ref_contacts 
                       (id, name, connection, archetype, region, types, uses, source, city, season)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (c["id"], c["name"], c["connection"], c["archetype"], c["region"], c["types"], c["uses"], c["source"], city, season)
                )
    except Exception as e:
        logger.warning(f"Could not populate ref_contacts seeds: {e}")

    try:
        from sr6core.srm_metadata import populate_srm_metadata
        populate_srm_metadata(conn)
    except Exception as e:
        logger.warning(f"Could not populate srm_metadata seeds: {e}")



def _migration_004_rule_embeddings(conn: sqlite3.Connection):
    """Embeddings storage table for offline hybrid search."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS rule_embeddings (
            rule_id TEXT PRIMARY KEY,
            embedding BLOB
        )
    """)


def _migration_005_canonical_supplement_weapons(conn: sqlite3.Connection):
    """Seed canonical supplement weapons (e.g. Firing Squad laser weapons) into ref_weapons."""
    # Ensure ref_weapons has all required standard columns if upgrading from a partial legacy schema
    for col, col_type in [
        ("category", "TEXT"), ("damage", "TEXT"), ("ap", "TEXT"),
        ("attack_rating", "TEXT"), ("modes", "TEXT"), ("ammo", "TEXT"),
        ("cost", "INTEGER"), ("avail", "TEXT"), ("source", "TEXT"),
        ("raw_xml", "TEXT")
    ]:
        if not _table_has_column(conn, "ref_weapons", col):
            try:
                conn.execute(f"ALTER TABLE ref_weapons ADD COLUMN {col} {col_type}")
            except Exception:
                pass

    supplement_weapons = [
        (
            "red_fox",
            "rEVOlution Arms Red Fox",
            "Energy Weapons",
            "6P",
            "-",
            "14/16/16/9/-",
            "SA/BF",
            "30(c)",
            2800,
            "6(I)",
            "Firing Squad p. 116",
            '<weapon id="red_fox" name="rEVOlution Arms Red Fox" cat="Energy Weapons" dmg="6P" attack="14,16,16,9" mode="SA/BF" ammo="30(c)" cost="2800" avail="6(I)" src="FS 116"/>'
        ),
        (
            "crimson_wasp",
            "rEVOlution Arms Crimson Wasp",
            "Energy Weapons",
            "5P",
            "-",
            "16/14/11/6/-",
            "SA",
            "15(c)",
            1500,
            "6(I)",
            "Firing Squad p. 116",
            '<weapon id="crimson_wasp" name="rEVOlution Arms Crimson Wasp" cat="Energy Weapons" dmg="5P" attack="16,14,11,6" mode="SA" ammo="15(c)" cost="1500" avail="6(I)" src="FS 116"/>'
        )
    ]
    for w in supplement_weapons:
        conn.execute(
            """INSERT OR REPLACE INTO ref_weapons 
               (id, name, category, damage, ap, attack_rating, modes, ammo, cost, avail, source, raw_xml)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            w
        )
        conn.execute("DELETE FROM ref_gear WHERE id = ?", (w[0],))


MIGRATIONS: List[Tuple[int, str, Callable[[sqlite3.Connection], None]]] = [
    (1, "001_core_rules", _migration_001_core_rules),
    (2, "002_gameplay_tables", _migration_002_gameplay_tables),
    (3, "003_srm_contacts_and_rulings", _migration_003_srm_contacts_and_rulings),
    (4, "004_rule_embeddings", _migration_004_rule_embeddings),
    (5, "005_canonical_supplement_weapons", _migration_005_canonical_supplement_weapons),
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
