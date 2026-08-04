"""
Roll20 VTT Character Sheet JSON Exporter for SR6.
"""

import json
from typing import Dict, Any


def export_roll20_json(char_data: Dict[str, Any]) -> str:
    identity = char_data.get("identity", {})
    attrs = char_data.get("attributes", {})
    lp = char_data.get("living_persona", {})
    
    roll20_payload = {
        "schema_version": "1.0",
        "system": "Shadowrun 6th Edition (SR6)",
        "character": {
            "name": identity.get("handle", "Unknown Runner"),
            "real_name": identity.get("real_name", ""),
            "metatype": identity.get("metatype", "Human"),
            "stream": identity.get("stream", ""),
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
                "resonance": attrs.get("resonance", 0),
            },
            "living_persona": lp,
            "skills": char_data.get("skills", []),
            "qualities": char_data.get("qualities", {}),
            "drones": char_data.get("drones", []),
            "complex_forms": char_data.get("complex_forms", []),
        }
    }
    return json.dumps(roll20_payload, indent=2)
