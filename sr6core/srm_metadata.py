"""
SRM (Shadowrun Missions) Metagame & Legality Metadata for SR6 Core.
Manages:
- srm_status (Legal, Restricted, Banned) column across reference catalog tables
- srm_rulings table with official Shadowrun Missions Guide (SRMG) rulings and FAQ exceptions
"""

import sqlite3
from typing import Dict, Any, List, Optional


OFFICIAL_SRM_RULINGS = [
    {
        "id": "srm_aug_cap",
        "topic": "Augmentation Cap (+4 Limit)",
        "category": "cap",
        "rule_or_item_id": "augmentation",
        "ruling": "Augmentation bonuses to any single attribute or skill are capped at +4. In multi-component tests (e.g., Attribute + Skill + Focus), total augmentation bonuses across all components cannot exceed +12.",
        "source": "SRMG v2.4 p. 11",
        "applies_to": "all"
    },
    {
        "id": "srm_focus_non_split",
        "topic": "Focus Non-Splitting Rule",
        "category": "focus",
        "rule_or_item_id": "foci",
        "ruling": "Untyped Power and Resonance Foci bonuses must be allocated entirely to a single test component and cannot be split across multiple test components.",
        "source": "SRMG v2.4 p. 12",
        "applies_to": "all"
    },
    {
        "id": "srm_teamwork_cap",
        "topic": "Teamwork Rating Cap",
        "category": "teamwork",
        "rule_or_item_id": "teamwork",
        "ruling": "Bonus dice gained from teamwork assistance tests cannot exceed the team leader's natural skill rating or autosoft rating.",
        "source": "SRMG v2.4 p. 13",
        "applies_to": "all"
    },
    {
        "id": "srm_living_persona_tuning",
        "topic": "Technomancer Network Tuning Cap",
        "category": "tuning",
        "rule_or_item_id": "living_persona",
        "ruling": "Technomancers tuning their living persona ASDF attributes are subject to the standard +4 augmentation limit per individual Matrix attribute.",
        "source": "SRMG v2.4 p. 14",
        "applies_to": "all"
    },
    {
        "id": "srm_cyberware_overdrive",
        "topic": "Cyberware Overdrive Mechanics",
        "category": "overdrive",
        "rule_or_item_id": "cyberware",
        "ruling": "Overdriving cyberware reduces Edge boost costs by 1 (or 2 with a wild die) but causes 1 box of unsoakable Physical strain damage if any 1s are rolled.",
        "source": "SRMG v2.4 p. 15",
        "applies_to": "all"
    },
    {
        "id": "srm_downtime_karma_rate",
        "topic": "Downtime Karma Exchange Rate",
        "category": "downtime",
        "rule_or_item_id": "advancement",
        "ruling": "Shadowrunners may convert up to 2,000 nuyen per Karma earned on a mission run, with a maximum conversion of 10 Karma per downtime phase.",
        "source": "SRMG v2.4 p. 18",
        "applies_to": "missions_only"
    },
    {
        "id": "srm_banned_infected",
        "topic": "Infected Character Legality",
        "category": "ban",
        "rule_or_item_id": "infected",
        "ruling": "HMHVV-infected player characters (Vampires, Ghouls, Wendigos, Nosferatu) are not permitted in sanctioned Shadowrun Missions campaign play.",
        "source": "SRMG v2.4 p. 6",
        "applies_to": "missions_only"
    },
    {
        "id": "srm_restricted_military_gear",
        "topic": "Military-Grade Availability Restrictions",
        "category": "restriction",
        "rule_or_item_id": "military_gear",
        "ruling": "Gear and weapons with an availability code containing 'F' (Forbidden) or Rating 6+ cannot be purchased during character creation without a campaign waiver.",
        "source": "SRMG v2.4 p. 8",
        "applies_to": "missions_only"
    }
]


def init_srm_metadata_tables(conn: sqlite3.Connection):
    """Adds srm_status columns to reference tables and creates srm_rulings table."""
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS srm_rulings (
            id TEXT PRIMARY KEY,
            topic TEXT,
            category TEXT,
            rule_or_item_id TEXT,
            ruling TEXT,
            source TEXT,
            applies_to TEXT,
            status TEXT DEFAULT 'Official FAQ'
        )
    """)

    # Ensure status column exists if table was created previously
    try:
        ruling_cols = [r[1] for r in cursor.execute("PRAGMA table_info(srm_rulings)").fetchall()]
        if "status" not in ruling_cols:
            cursor.execute("ALTER TABLE srm_rulings ADD COLUMN status TEXT DEFAULT 'Official FAQ'")
    except Exception:
        pass

    # Add srm_status column across all catalog reference tables
    for tbl in ["ref_weapons", "ref_cyberware", "ref_qualities", "ref_gear", "ref_adept_powers", "ref_spells"]:
        try:
            cols = [r[1] for r in cursor.execute(f"PRAGMA table_info({tbl})").fetchall()]
            if cols and "srm_status" not in cols:
                cursor.execute(f"ALTER TABLE {tbl} ADD COLUMN srm_status TEXT DEFAULT 'Legal'")
        except Exception:
            pass

    conn.commit()


def populate_srm_metadata(conn: sqlite3.Connection) -> Dict[str, int]:
    """Populates srm_rulings and tags known SRM restricted/banned items in reference tables."""
    init_srm_metadata_tables(conn)
    cursor = conn.cursor()
    rulings_count = 0

    for r in OFFICIAL_SRM_RULINGS:
        status_val = r.get("status", "Official FAQ")
        cursor.execute(
            """INSERT OR REPLACE INTO srm_rulings 
               (id, topic, category, rule_or_item_id, ruling, source, applies_to, status)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (r["id"], r["topic"], r["category"], r["rule_or_item_id"], r["ruling"], r["source"], r["applies_to"], status_val)
        )
        rulings_count += 1

    # Tag banned / restricted items
    try:
        # Banned infected qualities
        cursor.execute("""
            UPDATE ref_qualities 
            SET srm_status = 'Banned' 
            WHERE lower(id) LIKE '%infected%' OR lower(id) LIKE '%ghoul%' OR lower(id) LIKE '%vampire%' OR lower(id) LIKE '%wendigo%'
        """)

        # Restricted military weapons (Forbidden availability)
        cursor.execute("""
            UPDATE ref_weapons 
            SET srm_status = 'Restricted' 
            WHERE upper(avail) LIKE '%F%' OR upper(avail) LIKE '%L%'
        """)

        # Restricted military cyberware
        cursor.execute("""
            UPDATE ref_cyberware 
            SET srm_status = 'Restricted' 
            WHERE upper(avail) LIKE '%F%' OR upper(avail) LIKE '%L%'
        """)
    except Exception:
        pass

    conn.commit()
    return {"srm_rulings": rulings_count}
