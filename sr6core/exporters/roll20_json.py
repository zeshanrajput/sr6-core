import os
import json
import sqlite3
import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional

from sr6core.rules_db import DEFAULT_DB_PATH
from sr6core.log_engine import get_log_totals
from sr6core.contacts import normalize_contacts_list

SKILL_ATTR_MAP = {
    "astral": "intuition",
    "athletics": "agility",
    "biotech": "logic",
    "close_combat": "agility",
    "con": "charisma",
    "conjuring": "magic",
    "cracking": "logic",
    "electronics": "logic",
    "enchanting": "magic",
    "engineering": "logic",
    "exotic_weapons": "agility",
    "firearms": "agility",
    "influence": "charisma",
    "outdoors": "intuition",
    "perception": "intuition",
    "piloting": "reaction",
    "sorcery": "magic",
    "stealth": "agility",
    "tasking": "resonance",
    "language": "logic",
    "knowledge": "logic"
}


def get_weapon_db_stats(w_ref: str, db_path: str = DEFAULT_DB_PATH) -> Dict[str, Any]:
    if not w_ref or not os.path.exists(db_path):
        return {}
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        row = cur.execute(
            "SELECT raw_xml FROM ref_weapons WHERE id = ? OR lower(id) = ? OR lower(name) = ?",
            (w_ref, w_ref.lower(), w_ref.lower())
        ).fetchone()
        conn.close()
        if not row or not row[0]:
            return {}
        root = ET.fromstring(row[0])
        w = root.find("weapon")
        if w is None:
            return {}
        return {
            "damage": w.get("dmg", ""),
            "attack_rating": w.get("attack", "").replace(",", "/").rstrip("/"),
            "modes": w.get("mode", ""),
            "ammo": w.get("ammo", ""),
            "skill": w.get("skill", ""),
            "spec": w.get("spec", "")
        }
    except Exception:
        return {}


def get_armor_db_stats(a_ref: str, db_path: str = DEFAULT_DB_PATH) -> Dict[str, Any]:
    if not a_ref or not os.path.exists(db_path):
        return {}
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        row = cur.execute(
            "SELECT raw_xml FROM ref_gear WHERE id = ? OR lower(id) = ? OR lower(name) = ?",
            (a_ref, a_ref.lower(), a_ref.lower())
        ).fetchone()
        conn.close()
        if not row or not row[0]:
            return {}
        root = ET.fromstring(row[0])
        a = root.find("armor")
        if a is None:
            return {}
        return {
            "defense_rating": int(a.get("rating", 0)),
            "social": int(a.get("social", 0))
        }
    except Exception:
        return {}


def export_roll20_json(char_data: Dict[str, Any], char_repo_path: Optional[str] = None, db_path: str = DEFAULT_DB_PATH) -> str:
    identity = char_data.get("identity", {})
    attrs = char_data.get("attributes", {})
    log_totals = get_log_totals(char_repo_path) if char_repo_path and os.path.exists(char_repo_path) else {}

    handle = identity.get("handle", identity.get("name", "Unknown"))
    real_name = identity.get("real_name", handle)

    # Check for direct CommLink6 Genesis JSON export first
    commlink_pdf_dir = os.path.expanduser("~/CommLink6/pdfs")
    possible_paths = [
        os.path.join(commlink_pdf_dir, f"{handle}.json"),
        os.path.join(commlink_pdf_dir, f"{real_name}.json"),
        os.path.join("C:/Users/zesha/CommLink6/pdfs", f"{handle}.json"),
        os.path.join("C:/Users/zesha/CommLink6/pdfs", f"{real_name}.json"),
    ]
    for p in possible_paths:
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    c_json = json.load(f)
                if c_json.get("system") == "SHADOWRUN6":
                    # Update dynamic financials from log if available
                    if "Karma" in log_totals:
                        c_json["freeKarma"] = int(log_totals["Karma"])
                    if "Lifetime_Karma" in log_totals:
                        c_json["karma"] = int(log_totals["Lifetime_Karma"])
                    if "Nuyen" in log_totals:
                        c_json["nuyen"] = int(log_totals["Nuyen"])
                    if "Heat" in log_totals:
                        c_json["heat"] = int(log_totals["Heat"])
                    return json.dumps(c_json, indent=2)
            except Exception:
                pass

    # Otherwise, generate Genesis JSON structure from char_data
    body = int(attrs.get("body", 1))
    agility = int(attrs.get("agility", 1))
    reaction = int(attrs.get("reaction", 1))
    strength = int(attrs.get("strength", 1))
    willpower = int(attrs.get("willpower", 1))
    logic = int(attrs.get("logic", 1))
    intuition = int(attrs.get("intuition", 1))
    charisma = int(attrs.get("charisma", 1))
    edge = int(attrs.get("edge", 1))
    magic = int(attrs.get("magic", 0))
    resonance = int(attrs.get("resonance", 0))
    power_points = int(attrs.get("power_points", 0))

    karma_avail = int(log_totals.get("Karma", identity.get("karma", 0)))
    karma_life = int(log_totals.get("Lifetime_Karma", karma_avail))

    def parse_dimension(val: Any) -> int:
        if isinstance(val, int):
            return val
        if isinstance(val, str):
            digits = "".join(c for c in val if c.isdigit())
            return int(digits) if digits else 0
        return 0

    size_val = parse_dimension(identity.get("size") or identity.get("height", 0))
    weight_val = parse_dimension(identity.get("weight", 0))

    devices = char_data.get("matrix_devices", [])
    primary_dp = 2
    for d in devices:
        if isinstance(d, dict) and "data_processing" in d:
            primary_dp = max(primary_dp, int(d["data_processing"]))

    attributes_list = [
        {"name": "Body", "id": "BODY", "points": body, "modifiedValue": body},
        {"name": "Agility", "id": "AGILITY", "points": agility, "modifiedValue": agility},
        {"name": "Reaction", "id": "REACTION", "points": reaction, "modifiedValue": reaction},
        {"name": "Strength", "id": "STRENGTH", "points": strength, "modifiedValue": strength},
        {"name": "Willpower", "id": "WILLPOWER", "points": willpower, "modifiedValue": willpower},
        {"name": "Logic", "id": "LOGIC", "points": logic, "modifiedValue": logic},
        {"name": "Intuition", "id": "INTUITION", "points": intuition, "modifiedValue": intuition},
        {"name": "Charisma", "id": "CHARISMA", "points": charisma, "modifiedValue": charisma},
        {"name": "Edge", "id": "EDGE", "points": edge, "modifiedValue": edge},
        {"name": "Magic", "id": "MAGIC", "points": magic, "modifiedValue": magic},
        {"name": "Resonance", "id": "RESONANCE", "points": resonance, "modifiedValue": resonance},
        {"name": "Power Points", "id": "POWER_POINTS", "points": power_points, "modifiedValue": power_points},
        {"name": "Defense Pool", "id": "DEFENSE_POOL_PHYSICAL", "points": 0, "modifiedValue": reaction + intuition},
        {"name": "Composure", "id": "COMPOSURE", "points": 0, "modifiedValue": willpower + charisma},
        {"name": "Judge Intentions", "id": "JUDGE_INTENTIONS", "points": 0, "modifiedValue": intuition + charisma},
        {"name": "Memory", "id": "MEMORY", "points": 0, "modifiedValue": logic + willpower},
        {"name": "Lift / Carry", "id": "LIFT_CARRY", "points": 0, "modifiedValue": body + strength}
    ]

    initiatives_list = [
        {"name": "Initiative (Astral)", "id": "INITIATIVE_ASTRAL", "value": (intuition + logic) if magic > 0 else 0, "dice": "+2D6"},
        {"name": "Initiative", "id": "INITIATIVE_PHYSICAL", "value": reaction + intuition, "dice": "+1D6"},
        {"name": "Initiative (Matrix AR)", "id": "INITIATIVE_MATRIX", "value": reaction + intuition, "dice": "+1D6"},
        {"name": "Initiative (Matrix VR)", "id": "INITIATIVE_MATRIX_VR_COLD", "value": primary_dp + intuition, "dice": "+2D6"},
        {"name": "Initiative (Matrix Hot)", "id": "INITIATIVE_MATRIX_VR_HOT", "value": primary_dp + intuition, "dice": "+3D6"}
    ]

    # Qualities
    raw_qualities = char_data.get("qualities", {})
    qualities_list = []
    if isinstance(raw_qualities, dict):
        for q in raw_qualities.get("positive", []):
            if isinstance(q, str):
                qualities_list.append({"name": q, "id": q.lower().replace(" ", "_"), "choice": "", "positive": True, "rating": 0, "page": "", "description": ""})
            elif isinstance(q, dict):
                qualities_list.append({"name": q.get("name", ""), "id": q.get("ref", q.get("name", "").lower().replace(" ", "_")), "choice": q.get("choice", ""), "positive": True, "rating": int(q.get("rating", 0)), "page": q.get("page", ""), "description": q.get("description", "")})
        for q in raw_qualities.get("negative", []):
            if isinstance(q, str):
                qualities_list.append({"name": q, "id": q.lower().replace(" ", "_"), "choice": "", "positive": False, "rating": 0, "page": "", "description": ""})
            elif isinstance(q, dict):
                qualities_list.append({"name": q.get("name", ""), "id": q.get("ref", q.get("name", "").lower().replace(" ", "_")), "choice": q.get("choice", ""), "positive": False, "rating": int(q.get("rating", 0)), "page": q.get("page", ""), "description": q.get("description", "")})

    # Skills
    skills_list = []
    for s in char_data.get("skills", []):
        s_name = s.get("name", "")
        s_id = s.get("id", s_name.lower().replace(" ", "_"))
        attr_name = SKILL_ATTR_MAP.get(s_id, s.get("attribute", "Agility")).capitalize()
        specs = []
        if s.get("specialization"):
            spec_name = s.get("specialization")
            specs.append({
                "name": spec_name,
                "id": spec_name.lower().replace(" ", "_"),
                "expertise": False,
                "attribute": attr_name,
                "pool": 0,
                "description": ""
            })
        skills_list.append({
            "name": s_name,
            "id": s_id,
            "attribute": attr_name,
            "rating": int(s.get("rating", 1)),
            "pool": 0,
            "specializations": specs,
            "influencedBy": [],
            "description": ""
        })

    # Spells
    spells_list = []
    for sp in char_data.get("spells", []):
        if isinstance(sp, str):
            spells_list.append({"name": sp, "id": sp.lower().replace(" ", "_"), "category": "Combat spells", "type": "Physical", "duration": "Instant", "range": "LOS", "drain": 3, "features": [], "isAlchemistic": False, "influencedBy": [], "page": "", "description": ""})
        elif isinstance(sp, dict):
            spells_list.append({"name": sp.get("name", ""), "id": sp.get("ref", sp.get("name", "").lower().replace(" ", "_")), "category": sp.get("category", "Heal spells"), "type": sp.get("type", "Physical"), "duration": sp.get("duration", "Sustained"), "range": sp.get("range", "Touch"), "drain": int(sp.get("drain", 3)), "features": [], "isAlchemistic": False, "influencedBy": [], "page": sp.get("page", ""), "description": sp.get("description", "")})

    # Adept Powers
    adept_list = []
    for ap in char_data.get("adept_powers", []):
        if isinstance(ap, str):
            adept_list.append({"name": ap, "activation": "PASSIVE", "level": 0, "cost": 1.0, "page": "", "description": ""})
        elif isinstance(ap, dict):
            adept_list.append({"name": ap.get("name", ""), "activation": ap.get("activation", "PASSIVE"), "level": int(ap.get("rating", ap.get("level", 0))), "cost": float(ap.get("cost", 1.0)), "page": ap.get("page", ""), "description": ap.get("description", "")})

    # Weapons
    long_range = []
    close_combat = []
    for w in char_data.get("weapons", []):
        w_dict = {"name": w} if isinstance(w, str) else dict(w)
        w_ref = w_dict.get("ref", w_dict.get("name", ""))
        db_stats = get_weapon_db_stats(w_ref, db_path=db_path)
        if db_stats:
            for k, v in db_stats.items():
                if v and k not in w_dict:
                    w_dict[k] = v
        w_type = w_dict.get("type", "Firearms")
        if "close" in w_type.lower() or "melee" in w_type.lower() or "club" in w_type.lower() or "blade" in w_type.lower():
            close_combat.append({
                "name": w_dict.get("name", ""),
                "type": "Close Combat Weapons",
                "subtype": w_dict.get("subtype", "Clubs"),
                "skill": None,
                "pool": int(w_dict.get("pool", agility)),
                "damage": w_dict.get("damage", "2S"),
                "attackRating": w_dict.get("attack_rating", "4/-/-/-/-"),
                "wifi": [],
                "accessories": [],
                "page": "",
                "description": "",
                "primary": False
            })
        else:
            long_range.append({
                "name": w_dict.get("name", ""),
                "type": "Firearms",
                "subtype": w_dict.get("subtype", "Light Pistols"),
                "skill": None,
                "pool": int(w_dict.get("pool", agility)),
                "damage": w_dict.get("damage", "2P"),
                "attackRating": w_dict.get("attack_rating", "9/8/6/-/-"),
                "mode": w_dict.get("modes", "SA"),
                "ammunition": str(w_dict.get("ammo", "15(c)")),
                "wifi": [],
                "accessories": [],
                "page": "",
                "description": "",
                "primary": False
            })

    # Armors
    armors_list = []
    for a in char_data.get("armors", []):
        a_dict = {"name": a} if isinstance(a, str) else dict(a)
        a_ref = a_dict.get("ref", a_dict.get("name", ""))
        db_stats = get_armor_db_stats(a_ref, db_path=db_path)
        dr = a_dict.get("defense_rating") or (db_stats.get("defense_rating", 0) if db_stats else 0)
        armors_list.append({
            "name": a_dict.get("name", ""),
            "rating": int(dr),
            "socialrating": int(a_dict.get("social", 0)),
            "accessories": [],
            "isIgnored": False,
            "page": "",
            "description": "",
            "primary": True if not armors_list else False
        })

    # Contacts
    contacts_list = []
    for c in normalize_contacts_list(log_totals.get("Contacts") or char_data.get("contacts", [])):
        if isinstance(c, dict):
            contacts_list.append({
                "name": c.get("name", ""),
                "type": c.get("archetype", c.get("type", "Contact")),
                "loyalty": int(c.get("loyalty", 1)),
                "influence": int(c.get("connection", c.get("influence", 1))),
                "description": c.get("description", ""),
                "favors": int(c.get("favors", 0))
            })

    genesis_payload = {
        "system": "SHADOWRUN6",
        "version": "3.2.0",
        "name": real_name,
        "streetName": handle,
        "metaType": identity.get("metatype", "Human"),
        "size": size_val,
        "weight": weight_val,
        "age": str(identity.get("age", "")),
        "gender": identity.get("gender", ""),
        "heat": int(log_totals.get("Heat", identity.get("heat", 0))),
        "reputation": 0,
        "karma": karma_life,
        "freeKarma": karma_avail,
        "nuyen": int(log_totals.get("Nuyen", identity.get("nuyen", 0))),
        "initiation": int(identity.get("initiation", 0)),
        "submersion": int(identity.get("submersion", 0)),
        "attributes": attributes_list,
        "initiatives": initiatives_list,
        "qualities": qualities_list,
        "skills": skills_list,
        "spells": spells_list,
        "rituals": [],
        "metamagic": [{"name": m if isinstance(m, str) else m.get("name", ""), "page": "", "description": ""} for m in char_data.get("meta_echoes", [])],
        "echoes": None,
        "complexForms": char_data.get("complex_forms", []),
        "adeptPowers": adept_list,
        "longRangeWeapons": long_range,
        "closeCombatWeapons": close_combat,
        "armors": armors_list,
        "items": char_data.get("items", []),
        "augmentations": char_data.get("augmentations", []),
        "vehicles": char_data.get("vehicles", []),
        "drones": char_data.get("drones", []),
        "lifestyles": [{"name": ls.get("name", "Low"), "customName": ls.get("name", "Low"), "cost": 0, "paidMonths": 1, "sin": None, "options": None, "description": None} for ls in char_data.get("lifestyles", [])] if char_data.get("lifestyles") else [],
        "sins": [{"name": s.get("name", ""), "description": None, "quality": int(s.get("rating", 6))} for s in char_data.get("sins", [])] if char_data.get("sins") else [],
        "contacts": contacts_list,
        "licenses": char_data.get("licenses", []),
        "matrixItems": devices,
        "martialArts": [],
        "signatureManeuvers": [],
        "notes": None
    }
    return json.dumps(genesis_payload, indent=2)
