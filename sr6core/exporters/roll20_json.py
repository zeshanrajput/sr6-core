import os
import json
from typing import Dict, Any, Optional

from sr6core.log_engine import get_log_totals


def export_roll20_json(char_data: Dict[str, Any], char_repo_path: Optional[str] = None) -> str:
    identity = char_data.get("identity", {})
    attrs = char_data.get("attributes", {})
    lp = char_data.get("living_persona", {})
    log_totals = get_log_totals(char_repo_path) if char_repo_path and os.path.exists(char_repo_path) else {}

    roll20_payload = {
        "schema_version": "1.0",
        "system": "Shadowrun 6th Edition (SR6)",
        "character": {
            "name": identity.get("handle", "Unknown Runner"),
            "real_name": identity.get("real_name", ""),
            "metatype": identity.get("metatype", "Human"),
            "tradition": identity.get("tradition", ""),
            "mortype": identity.get("mortype", ""),
            "stream": identity.get("stream", ""),
            "gender": identity.get("gender", ""),
            "age": identity.get("age", ""),
            "financials": {
                "nuyen": log_totals.get("Nuyen", identity.get("nuyen", 0)),
                "karma_available": log_totals.get("Karma", identity.get("karma", 0)),
                "karma_lifetime": log_totals.get("Lifetime_Karma", 0),
                "heat": log_totals.get("Heat", 0),
                "reputation": log_totals.get("Reputation", {})
            },
            "attributes": {
                "body": attrs.get("body", 1),
                "agility": attrs.get("agility", 1),
                "reaction": attrs.get("reaction", 1),
                "strength": attrs.get("strength", 1),
                "willpower": attrs.get("willpower", 1),
                "logic": attrs.get("logic", 1),
                "intuition": attrs.get("intuition", 1),
                "charisma": attrs.get("charisma", 1),
                "edge": attrs.get("edge", 1),
                "magic": attrs.get("magic", 0),
                "resonance": attrs.get("resonance", 0),
                "power_points": attrs.get("power_points", 0),
            },
            "living_persona": lp,
            "skills": char_data.get("skills", []),
            "qualities": char_data.get("qualities", {}),
            "spells": char_data.get("spells", []),
            "adept_powers": char_data.get("adept_powers", []),
            "meta_echoes": char_data.get("meta_echoes", []),
            "weapons": char_data.get("weapons", []),
            "armors": char_data.get("armors", []),
            "matrix_devices": char_data.get("matrix_devices", []),
            "software": char_data.get("software", []),
            "items": char_data.get("items", []),
            "gear": char_data.get("gear", []),
            "drones": char_data.get("drones", []),
            "complex_forms": char_data.get("complex_forms", []),
            "contacts": log_totals.get("Contacts") or char_data.get("contacts", []),
        }
    }
    return json.dumps(roll20_payload, indent=2)
