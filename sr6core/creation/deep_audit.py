"""
Deep Character Auditor & Flexible Transaction Pricing Engine for SR6.
Performs item-by-item verification of master portfolios against CommLink6 database records.
Supports Base Book Price vs. Transaction Price with Quality Discounts, Contact Markups, DIY Rigger Modifiers, and Overrides.
"""

import sqlite3
from typing import Dict, Any, List, Optional, Tuple

from sr6core.rules_db import DEFAULT_DB_PATH
from sr6core.character_manager import CharacterManager


def calculate_transaction_price(base_cost: int, item_data: Dict[str, Any], char_data: Dict[str, Any]) -> Tuple[int, str]:
    """
    Calculates final transaction price given base price and price modification rules.
    Returns (final_price, explanation_note).
    """
    if "override_price" in item_data and item_data["override_price"] is not None:
        note = item_data.get("notes") or item_data.get("reason") or "Manual Price Override"
        return int(item_data["override_price"]), f"Custom Override ({note})"

    actual_cost = base_cost
    notes = []

    # 1. Contact markup (e.g. markup: 1.2 or contact_fee: 500)
    if "markup" in item_data:
        markup = float(item_data["markup"])
        actual_cost = int(actual_cost * markup)
        notes.append(f"Contact Markup x{markup:.2f}")
    if "contact_fee" in item_data:
        fee = int(item_data["contact_fee"])
        actual_cost += fee
        notes.append(f"Contact Fee +{fee}¥")

    # 2. DIY Rigger modification discount (e.g. diy_discount: 0.5 for self-work)
    if item_data.get("diy_work") or item_data.get("diy_discount"):
        disc = float(item_data.get("diy_discount", 0.5))
        actual_cost = int(actual_cost * disc)
        notes.append(f"DIY Rigger Self-Work Discount (-{int((1 - disc) * 100)}%)")

    # 3. Quality discounts (e.g. Smile for the Camera quality discount)
    qualities = char_data.get("qualities", {}).get("positive", [])
    for q in qualities:
        q_name = q.get("name", "").lower()
        if "smile for the camera" in q_name and item_data.get("category") in ["electronics", "drones", "sensors"]:
            actual_cost = int(actual_cost * 0.9)
            notes.append("Smile for the Camera Quality Discount (-10%)")
            break

    explanation = ", ".join(notes) if notes else "Standard Book Price"
    return actual_cost, explanation


def deep_audit_character(char_id: str, db_path: str = DEFAULT_DB_PATH) -> Dict[str, Any]:
    cm = CharacterManager()
    char_data = cm.get_character_data(char_id)
    if not char_data:
        return {"valid": False, "errors": [f"Character '{char_id}' not found."]}

    db_path = os.environ.get("SR6_RULES_DB_PATH", db_path)
    conn = None
    cursor = None
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
        except Exception:
            conn = None
            cursor = None

    def _get_row(table: str, ref_val: str, name_val: str):
        if not cursor:
            return None
        try:
            return cursor.execute(f"SELECT * FROM {table} WHERE id = ? OR lower(name) = ?", (ref_val, name_val.lower())).fetchone()
        except Exception:
            return None

    warnings = []
    audit_details = []

    # 1. Audit Qualities
    total_pos_karma = 0
    total_neg_karma = 0
    pos_qualities = char_data.get("qualities", {}).get("positive", [])
    neg_qualities = char_data.get("qualities", {}).get("negative", [])

    for q in pos_qualities:
        q_ref = q.get("ref", q.get("name", "").lower().replace(" ", "_"))
        row = _get_row("ref_qualities", q_ref, q.get("name", ""))
        if "karma" in q:
            actual_k = q["karma"]
        else:
            expected_k = int(row["karma"]) if row and "karma" in row.keys() and str(row["karma"]).isdigit() else 5
            rating = q.get("rating", 1)
            actual_k = expected_k * rating
        total_pos_karma += actual_k
        audit_details.append({
            "category": "Quality (Positive)",
            "name": q.get("name"),
            "ref": q_ref,
            "karma": actual_k,
            "verified_in_db": row is not None
        })

    for q in neg_qualities:
        q_ref = q.get("ref", q.get("name", "").lower().replace(" ", "_"))
        row = _get_row("ref_qualities", q_ref, q.get("name", ""))
        if "karma" in q:
            actual_k = q["karma"]
        else:
            expected_k = int(row["karma"]) if row and "karma" in row.keys() and str(row["karma"]).isdigit() else 5
            rating = q.get("rating", 1)
            actual_k = expected_k * rating
        total_neg_karma += actual_k

        audit_details.append({
            "category": "Quality (Negative)",
            "name": q.get("name"),
            "ref": q_ref,
            "karma": -actual_k,
            "verified_in_db": row is not None
        })

    if total_pos_karma > 50:
        warnings.append(f"Positive qualities total ({total_pos_karma} Karma) exceeds standard 50 Karma cap.")
    if total_neg_karma > 50:
        warnings.append(f"Negative qualities total ({total_neg_karma} Karma) exceeds standard 50 Karma cap.")

    # 2. Audit Gear & Vehicles/Drones
    gear_audits = []
    for drone in char_data.get("drones", []):
        d_ref = drone.get("ref", drone.get("name", "").lower().replace(" ", "_"))
        row = _get_row("ref_gear", d_ref, drone.get("name", ""))
        base_price = int(row["cost"]) if row and "cost" in row.keys() and str(row["cost"]).isdigit() else 10000
        final_price, price_note = calculate_transaction_price(base_price, drone, char_data)
        gear_audits.append({
            "name": drone.get("name"),
            "ref": d_ref,
            "base_cost": base_price,
            "transaction_cost": final_price,
            "pricing_note": price_note,
            "verified_in_db": row is not None
        })

    if conn:
        conn.close()

    # 3. Audit Synergies, Augmentation Caps & Multi-Component Pools
    synergies = char_data.get("synergies", {})
    synergy_audits = []

    # Check Foci
    foci = synergies.get("foci", [])
    for f in foci:
        if isinstance(f, dict):
            f_name = f.get("name", "Focus")
            f_rating = int(f.get("rating", 1))
            f_applies = f.get("applies_to", "")
            if f_rating > 4:
                warnings.append(f"Focus '{f_name}' rating ({f_rating}) exceeds standard +4 SRMG augmentation cap on {f_applies}.")
            synergy_audits.append({
                "type": "Focus",
                "name": f_name,
                "rating": f_rating,
                "applies_to": f_applies,
                "srm_cap_valid": f_rating <= 4
            })

    # Check Companions (Symbiosis & Powers)
    companions = synergies.get("companions", [])
    for comp in companions:
        if isinstance(comp, dict):
            c_name = comp.get("name", "Companion")
            c_symb = int(comp.get("symbiosis_bonus", 0))
            if c_symb > 4:
                warnings.append(f"Companion '{c_name}' symbiosis bonus (+{c_symb}) exceeds standard +4 SRMG augmentation cap.")
            synergy_audits.append({
                "type": "Companion",
                "name": c_name,
                "symbiosis_bonus": c_symb,
                "diagnosis_bonus": comp.get("diagnosis_bonus", 0),
                "skills": comp.get("skills", []),
                "autosofts": comp.get("autosofts", []),
                "srm_cap_valid": c_symb <= 4
            })

    is_valid = len(warnings) == 0

    return {
        "char_id": char_id,
        "valid": is_valid,
        "warnings": warnings,
        "total_pos_karma": total_pos_karma,
        "total_neg_karma": total_neg_karma,
        "net_quality_karma": total_pos_karma - total_neg_karma,
        "gear_audits": gear_audits,
        "synergy_audits": synergy_audits,
        "audit_details": audit_details
    }

