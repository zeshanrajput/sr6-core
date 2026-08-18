"""
Unique Identifier (OID) Harmonization and Resolution Engine for SR6.
Standardizes references across Genesis XML, CommLink6 datasets, Rules Vault, and YAML dossiers.
"""

import os
import re
import sqlite3
from typing import Dict, Any, Optional, Tuple, List
from sr6core.rules_db import DEFAULT_DB_PATH

# Category prefixes used across Genesis XML and CommLink6
OID_PREFIXES: Dict[str, str] = {
    "quality": "qual_",
    "spell": "sp_",
    "complex_form": "cf_",
    "weapon": "wpn_",
    "armor": "arm_",
    "vehicle": "veh_",
    "drone": "drn_",
    "skill": "sk_",
    "attribute": "attr_",
    "gear": "gear_",
    "cyberware": "cyber_",
    "bioware": "bio_",
    "program": "prog_",
    "meta_echo": "echo_",
    "contact": "cont_",
}

# Table mapping in SQLite rules_index.db
TABLE_CATEGORY_MAP: Dict[str, str] = {
    "quality": "ref_qualities",
    "spell": "ref_spells",
    "complex_form": "ref_complex_forms",
    "weapon": "ref_weapons",
    "vehicle": "ref_vehicles",
    "drone": "ref_vehicles",
    "gear": "ref_gear",
    "cyberware": "ref_cyberware",
    "bioware": "ref_cyberware",
    "contact": "ref_contacts",
    "program": "ref_gear",
    "meta_echo": "ref_qualities",
}

# Common alias dictionary for standard normalization
COMMON_ALIASES: Dict[str, str] = {
    # Skills
    "tasking": "sk_tasking",
    "cracking": "sk_cracking",
    "electronics": "sk_electronics",
    "athletics": "sk_athletics",
    "biotech": "sk_biotech",
    "close_combat": "sk_close_combat",
    "con": "sk_con",
    "conjuring": "sk_conjuring",
    "enchanting": "sk_enchanting",
    "engineering": "sk_engineering",
    "exotic_weapons": "sk_exotic_weapons",
    "firearms": "sk_firearms",
    "influence": "sk_influence",
    "outdoors": "sk_outdoors",
    "perception": "sk_perception",
    "piloting": "sk_piloting",
    "sorcery": "sk_sorcery",
    "stealth": "sk_stealth",
    
    # Attributes
    "body": "attr_body",
    "agility": "attr_agility",
    "reaction": "attr_reaction",
    "strength": "attr_strength",
    "willpower": "attr_willpower",
    "logic": "attr_logic",
    "intuition": "attr_intuition",
    "charisma": "attr_charisma",
    "edge": "attr_edge",
    "resonance": "attr_resonance",
    "magic": "attr_magic",
    "essence": "attr_essence",
    
    # Complex Forms
    "cleaner": "cf_cleaner",
    "diffusion": "cf_diffusion",
    "technoregeneration": "cf_technoregeneration",
    "puppeteer": "cf_puppeteer",
    "editor": "cf_editor",
    "resonance_spike": "cf_resonance_spike",
    "resonance_veil": "cf_resonance_veil",
    "static_veil": "cf_static_veil",
    "pulse_storm": "cf_pulse_storm",
    "derez": "cf_derez",
    "tattletale": "cf_tattletale",
    
    # Qualities
    "natural_hacker": "qual_natural_hacker",
    "technoshaman": "qual_technoshaman",
    "designer": "qual_designer",
    "sensor_upgrade": "qual_sensor_upgrade",
    "pilot_origins": "qual_pilot_origins",
    "buddy_system": "qual_buddy_system",
    "sprite_bane": "qual_sprite_bane",
    "hooder": "qual_hooder",
    "analytical_mind": "qual_analytical_mind",
    "ambidextrous": "qual_ambidextrous",
    "guts": "qual_guts",
    "aptitude": "qual_aptitude",
    "toughness": "qual_toughness",
}


def normalize_oid(identifier: str) -> str:
    """Normalizes an arbitrary string into a standard snake_case ID."""
    if not identifier:
        return ""
    clean = re.sub(r"[^\w\s-]", "", identifier.strip().lower())
    return re.sub(r"[-\s]+", "_", clean)


def resolve_canonical_oid(
    category: str,
    raw_input: str,
    db_path: str = DEFAULT_DB_PATH
) -> Tuple[str, Optional[Dict[str, Any]]]:
    """
    Resolves a canonical OID and database row for a given category and item identifier or name.
    
    Returns:
        (canonical_oid, db_record_or_none)
    """
    if not raw_input:
        return "unknown", None

    norm_input = normalize_oid(raw_input)
    cat_lower = category.lower().strip()

    # 1. Direct Alias Check
    if norm_input in COMMON_ALIASES:
        norm_input = COMMON_ALIASES[norm_input]

    # 2. Database Lookup
    tbl = TABLE_CATEGORY_MAP.get(cat_lower, "ref_gear")
    db_row = None

    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Priority A: Exact match on id
            db_row = cursor.execute(f"SELECT * FROM {tbl} WHERE id = ? OR lower(id) = ?", (raw_input, norm_input)).fetchone()

            # Priority B: Exact match on name
            if not db_row:
                db_row = cursor.execute(f"SELECT * FROM {tbl} WHERE lower(name) = lower(?)", (raw_input,)).fetchone()

            # Priority C: Stripped prefix match (e.g. searching 'cleaner' finding 'cf_cleaner')
            if not db_row:
                prefix = OID_PREFIXES.get(cat_lower, "")
                if prefix and not norm_input.startswith(prefix):
                    prefixed = f"{prefix}{norm_input}"
                    db_row = cursor.execute(f"SELECT * FROM {tbl} WHERE id = ? OR lower(id) = ?", (prefixed, prefixed)).fetchone()

            # Priority D: Like search on name
            if not db_row:
                db_row = cursor.execute(
                    f"SELECT * FROM {tbl} WHERE name LIKE ? AND id NOT LIKE 'pack_%'",
                    (f"%{raw_input}%",)
                ).fetchone()

            conn.close()
        except Exception:
            pass

    if db_row:
        row_dict = dict(db_row)
        return row_dict.get("id", norm_input), row_dict

    # Fallback to normalized input with appropriate prefix
    prefix = OID_PREFIXES.get(cat_lower, "")
    if prefix and not norm_input.startswith(prefix) and not any(norm_input.startswith(p) for p in OID_PREFIXES.values()):
        return f"{prefix}{norm_input}", None

    return norm_input, None
