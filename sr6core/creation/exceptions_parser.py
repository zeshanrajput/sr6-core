"""
Character Exceptions Registry and Parser for SR6 Core.
Loads, parses, and formalizes character-specific rules exceptions,
discounts, and GM rulings from rules pages and exceptions.yaml.
"""

import os
from typing import Dict, Any, List, Optional
import yaml
from sr6core.character_manager import CharacterManager


SEED_EXCEPTIONS: Dict[str, List[Dict[str, Any]]] = {
    "reiko": [
        {
            "id": "omegaware_discount",
            "title": "Used/Omegaware Cyberware 50% Discount",
            "category": "financial",
            "description": "Cyberware components purchased as salvage omegaware at 50% book cost.",
            "source": "character_purchases.qmd",
            "gm": "WarDoctor / SRM FAQ",
            "active": True
        },
        {
            "id": "diy_rigger_mods",
            "title": "DIY Rigger 50% Installation Discount",
            "category": "financial",
            "description": "50% discount on vehicle/drone parts installed personally via Engineering facility (Double Clutch p. 120).",
            "source": "Double Clutch p. 120 / character_purchases.qmd",
            "gm": "Tabletop Baseline",
            "active": True
        },
        {
            "id": "shiawase_camera_discount",
            "title": "Smile for the Camera! Shiawase 10% Discount",
            "category": "financial",
            "description": "10% manufacturer discount on Shiawase brand electronics, drones, and sensors.",
            "source": "Sixth World Companion p. 142 / character_purchases.qmd",
            "gm": "Tabletop Baseline",
            "active": True
        },
        {
            "id": "inhabited_override",
            "title": "Inhabited Override Sprite Power Substitution",
            "category": "mechanics",
            "description": "Operating drones via Inhabited Override (SR6H p. 194) substitutes drone Pilot with Reiko's Resonance (benefiting from Resonance Focus and Taz Symbiosis). Sensor tests pair autosofts with drone Sensor.",
            "source": "Hack & Slash p. 71 / SR6H p. 194",
            "gm": "Tabletop Baseline",
            "active": True
        },
        {
            "id": "natural_hacker_swap",
            "title": "Natural Hacker Matrix Attribute Substitution",
            "category": "mechanics",
            "description": "Natural Hacker quality substitutes Resonance for Sleaze and Attack in Matrix actions and defenses.",
            "source": "Sixth World Companion / rules_matrix.qmd",
            "gm": "Tabletop Baseline",
            "active": True
        },
        {
            "id": "retractable_skates",
            "title": "Anthrodrone Retractable Skates Movement Mode",
            "category": "mechanics",
            "description": "Anthrodrone skates deploy via Minor Action, using metahuman movement rules (Walk 10m/rnd, Sprint 30m/rnd + 2m/hit).",
            "source": "Body Shop p. 47 / rules_drones.qmd",
            "gm": "Tabletop Baseline",
            "active": True
        }
    ],
    "velvet": [
        {
            "id": "srm_monthly_expenses",
            "title": "SRM Bi-Monthly Expense & Downtime Cadence",
            "category": "lifestyle",
            "description": "Every 2nd SRM mission, settle monthly lifestyle obligations and perform 1 Major and 1 Minor downtime action.",
            "source": "rules_and_downtime.qmd",
            "gm": "SRM Campaign Baseline",
            "active": True
        },
        {
            "id": "adept_sorcery_stacking",
            "title": "Adept Improved Ability (Sorcery) Stacking",
            "category": "mechanics",
            "description": "Improved Ability adept power grants bonus dice to Sorcery spellcasting within adept power limits.",
            "source": "Street Wyrd / rules_and_downtime.qmd",
            "gm": "Tabletop Baseline",
            "active": True
        },
        {
            "id": "high_charisma_drain_synergy",
            "title": "Hermetic/Elf High Charisma Drain Resistance",
            "category": "mechanics",
            "description": "Drain resistance utilizes Willpower + Charisma (enhanced by Sustained Attribute spells up to +4).",
            "source": "SR6 Core p. 132 / rules_and_downtime.qmd",
            "gm": "Tabletop Baseline",
            "active": True
        }
    ],
    "venn": [
        {
            "id": "cyborg_essence_tolerance",
            "title": "Full Conversion Monad 0.06 Essence Tolerance",
            "category": "mechanics",
            "description": "Extreme bioware and cyberware tolerances operating at 0.06 Essence supported by nanite fluid balances.",
            "source": "rules_and_downtime.qmd",
            "gm": "Tabletop Baseline",
            "active": True
        },
        {
            "id": "monad_toughness_monitor",
            "title": "Nanite Volume Toughness Scaling",
            "category": "mechanics",
            "description": "Nanite volume adds bonus condition monitor boxes (Nanite Volume // 2) to Physical and Stun tracks.",
            "source": "Hack & Slash / rules_and_downtime.qmd",
            "gm": "Tabletop Baseline",
            "active": True
        },
        {
            "id": "hooder_karma_funding",
            "title": "Hooder Quality Downtime Karma Exchange",
            "category": "financial",
            "description": "¥2,000/mo Hooder obligation directly funds the 'Working for the People' minor downtime action (+1 Karma).",
            "source": "rules_and_downtime.qmd",
            "gm": "SRM Campaign Baseline",
            "active": True
        }
    ]
}


class ExceptionsRegistry:
    @classmethod
    def get_character_exceptions(cls, char_id: str, repo_dir: Optional[str] = None) -> List[Dict[str, Any]]:
        if not repo_dir:
            cand = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "characters", char_id)
            if os.path.exists(cand):
                repo_dir = cand
        if repo_dir:
            exc_yaml = os.path.join(repo_dir, "rules", "exceptions.yaml")
            if os.path.exists(exc_yaml):
                try:
                    with open(exc_yaml, "r", encoding="utf-8") as f:
                        loaded = yaml.safe_load(f)
                        if isinstance(loaded, list):
                            return loaded
                        if isinstance(loaded, dict) and "exceptions" in loaded:
                            return loaded["exceptions"]
                except Exception:
                    pass

        canonical = char_id.lower().replace("sr6", "")
        if canonical in ["yuriko"]:
            canonical = "reiko"
        elif canonical in ["union"]:
            canonical = "venn"
        return SEED_EXCEPTIONS.get(canonical, [])

    @classmethod
    def write_seed_exceptions(cls, char_id: str, repo_dir: str):
        rules_dir = os.path.join(repo_dir, "rules")
        os.makedirs(rules_dir, exist_ok=True)
        exc_file = os.path.join(rules_dir, "exceptions.yaml")
        if not os.path.exists(exc_file):
            canonical = char_id.lower().replace("sr6", "")
            if canonical in ["yuriko"]:
                canonical = "reiko"
            elif canonical in ["union"]:
                canonical = "venn"
            data = SEED_EXCEPTIONS.get(canonical, [])
            with open(exc_file, "w", encoding="utf-8") as f:
                yaml.dump({"exceptions": data}, f, default_flow_style=False, sort_keys=False)
