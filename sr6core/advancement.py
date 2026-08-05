"""
Interactive Character Advancement & Shopping Wizard Engine for SR6.
Enables searching CommLink6 datasets, calculating transaction prices with custom modifiers,
and adding items, qualities, or spells to character dossiers.
"""

import os
import sqlite3
import yaml
from typing import Dict, Any, List, Optional, Tuple

from sr6core.rules_db import DEFAULT_DB_PATH
from sr6core.character_manager import CharacterManager
from sr6core.creation.deep_audit import calculate_transaction_price


def search_catalog(query: str, db_path: str = DEFAULT_DB_PATH, limit: int = 15) -> List[Dict[str, Any]]:
    if not os.path.exists(db_path):
        return []

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    results = []
    clean_q = f"%{query.strip().lower()}%"

    tables = [
        ("ref_qualities", "quality"),
        ("ref_spells", "spell"),
        ("ref_complex_forms", "complex_form"),
        ("ref_gear", "gear")
    ]

    for tbl, category in tables:
        try:
            rows = cursor.execute(
                f"SELECT * FROM {tbl} WHERE lower(id) LIKE ? OR lower(name) LIKE ? LIMIT ?",
                (clean_q, clean_q, limit)
            ).fetchall()
            for r in rows:
                item_dict = dict(r)
                item_dict["category"] = category
                results.append(item_dict)
        except Exception:
            pass

    conn.close()
    return results[:limit]


def purchase_item_for_character(
    char_id: str,
    item_ref: str,
    modifiers: Optional[Dict[str, Any]] = None,
    db_path: str = DEFAULT_DB_PATH
) -> Tuple[bool, str]:
    cm = CharacterManager()
    char_data = cm.get_character_data(char_id)
    if not char_data:
        return False, f"Character '{char_id}' not found."

    if modifiers is None:
        modifiers = {}

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    item_row = None
    item_cat = "gear"

    for tbl, cat in [("ref_gear", "gear"), ("ref_qualities", "quality"), ("ref_spells", "spell"), ("ref_complex_forms", "complex_form")]:
        row = cursor.execute(f"SELECT * FROM {tbl} WHERE id = ? OR lower(name) = ?", (item_ref, item_ref.lower())).fetchone()
        if row:
            item_row = dict(row)
            item_cat = cat
            break

    conn.close()

    if not item_row:
        return False, f"Item reference '{item_ref}' not found in CommLink6 database."

    item_name = item_row.get("name", item_ref)
    base_cost = int(item_row.get("cost", 0)) if str(item_row.get("cost", "")).isdigit() else 0

    item_entry = {"name": item_name, "ref": item_row["id"], **modifiers}
    final_price, price_note = calculate_transaction_price(base_cost, item_entry, char_data)

    char_path = cm.get_character_file_path(char_id)
    if not char_path or not os.path.exists(char_path):
        return False, f"Master dossier path for '{char_id}' not found."

    with open(char_path, "r", encoding="utf-8") as f:
        raw_yaml = yaml.safe_load(f)

    if item_cat == "gear":
        if "gear" not in raw_yaml:
            raw_yaml["gear"] = []
        raw_yaml["gear"].append({
            "name": item_name,
            "ref": item_row["id"],
            "base_cost": base_cost,
            "actual_cost": final_price,
            "transaction_note": price_note
        })
    elif item_cat == "quality":
        if "qualities" not in raw_yaml:
            raw_yaml["qualities"] = {"positive": [], "negative": []}
        q_type = "positive" if item_row.get("quality_type") == "positive" else "negative"
        raw_yaml["qualities"][q_type].append({
            "name": item_name,
            "ref": item_row["id"],
            "karma": int(item_row.get("karma", 0))
        })

    with open(char_path, "w", encoding="utf-8") as f:
        yaml.dump(raw_yaml, f, sort_keys=False)

    msg = f"Successfully purchased '{item_name}' for '{char_id}'. Final Price: {final_price}¥ ({price_note})."
    return True, msg
