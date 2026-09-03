"""
Canonical Spirit Catalog and Channeling Resolution Module for Shadowrun 6e.
Covers core spirits (Air, Earth, Fire, Water, Beasts, Man/Kin) and Street Wyrd spirits
(Guardian, Guidance, Plant, Task) with full powers, optional powers, and channeling bonuses.
"""

from typing import Dict, Any, List, Optional


# Canonical Spirits from SR6 Core Rulebook and Street Wyrd (p. 7, 66, 121-122)
SPIRIT_CATALOG: Dict[str, Dict[str, Any]] = {
    "air": {
        "name": "Spirit of Air",
        "category": "Core Elementals",
        "source": "SR6 Core p. 147",
        "doc_link": "chapters/rules_and_downtime.html#conjuring-and-spirit-protocols",
        "powers": [
            {
                "name": "Accident",
                "action": "Major Action",
                "target": "Single Target",
                "effect": "Target must make REA + INT test vs Spirit Force x 2 or suffer clumsy accident/stumble.",
            },
            {
                "name": "Astral Form",
                "action": "Always",
                "target": "Self",
                "effect": "Dual-natured or wholly astral entity.",
            },
            {
                "name": "Concealment",
                "action": "Minor Action",
                "target": "Single Target / Area",
                "effect": "Adds Spirit Force as negative modifier to perception tests against target.",
            },
            {
                "name": "Confusion",
                "action": "Major Action",
                "target": "Single Target",
                "effect": "Target suffers negative dice pool modifier equal to net hits on all actions.",
            },
            {
                "name": "Engulf (Air)",
                "action": "Major Action",
                "target": "Melee",
                "effect": "Engulfs target in miniature vortex; deals (Force + 2)S + Fatigue I damage.",
            },
            {
                "name": "Movement",
                "action": "Minor Action",
                "target": "Single Target",
                "effect": "Multiplies or divides target's movement rate by spirit Force.",
            },
            {
                "name": "Search",
                "action": "Major Action",
                "target": "Area",
                "effect": "Searches for person, object, or location in physical or astral plane.",
            }
        ],
        "optional_powers": [
            {"name": "Elemental Attack (Cold or Electricity)", "action": "Major Action", "target": "LOS", "effect": "Ranged attack dealing (Force)P damage with Cold or Electrical secondary effects."},
            {"name": "Energy Aura (Cold or Electricity)", "action": "Always", "target": "Self", "effect": "Adds Cold or Electricity damage and AP to melee attacks, shocks/freezes attackers."},
            {"name": "Fear", "action": "Major Action", "target": "LOS", "effect": "Forces target to flee in terror on failed WIL + LOG test."},
            {"name": "Guard", "action": "Minor Action", "target": "Target", "effect": "Protects target against hazards, falling, and glitches."},
            {"name": "Noxious Breath", "action": "Major Action", "target": "Cone / Close", "effect": "Target makes BOD + WIL test vs Force or suffers nausea and disorientation."},
            {"name": "Psychokinesis", "action": "Major Action", "target": "LOS", "effect": "Manipulates physical objects with effective Strength equal to Force."}
        ],
        "weakness": "Allergy (Inhalation vector toxins, Severe)",
        "attributes_formula": "BOD: F-2, AGI: F+3, REA: F+4, STR: F-3, WIL: F, LOG: F, INT: F, CHA: F"
    },
    "earth": {
        "name": "Spirit of Earth",
        "category": "Core Elementals",
        "source": "SR6 Core p. 147",
        "doc_link": "chapters/rules_and_downtime.html#conjuring-and-spirit-protocols",
        "powers": [
            {
                "name": "Astral Form",
                "action": "Always",
                "target": "Self",
                "effect": "Dual-natured or wholly astral entity.",
            },
            {
                "name": "Binding",
                "action": "Major Action",
                "target": "Melee / Close",
                "effect": "Encases target in stone/earth; target is immobilized until breaking free (STR + BOD vs Force x 2).",
            },
            {
                "name": "Guard",
                "action": "Minor Action (Sustained)",
                "target": "Protected Target",
                "effect": "Protects target against accidents, glitches, and environmental hazards.",
            },
            {
                "name": "Movement",
                "action": "Minor Action",
                "target": "Single Target",
                "effect": "Multiplies or divides target movement rate by spirit Force.",
            },
            {
                "name": "Search",
                "action": "Major Action",
                "target": "Area",
                "effect": "Searches for person, object, or location in physical or astral plane.",
            }
        ],
        "optional_powers": [
            {"name": "Concealment", "action": "Minor Action", "target": "Single Target / Area", "effect": "Adds Spirit Force as negative modifier to perception tests."},
            {"name": "Confusion", "action": "Major Action", "target": "Single Target", "effect": "Imposes net hits penalty on all target actions."},
            {"name": "Elemental Attack (Chemical)", "action": "Major Action", "target": "LOS", "effect": "Ranged attack dealing (Force)P crushing or corrosive damage."},
            {"name": "Engulf (Earth)", "action": "Major Action", "target": "Melee", "effect": "Crushes and suffocates target in stone and dirt."},
            {"name": "Fear", "action": "Major Action", "target": "LOS", "effect": "Terrifying tremor/earthen presence forcing target to flee."}
        ],
        "weakness": "Allergy (Electricity, Severe)",
        "attributes_formula": "BOD: F+4, AGI: F-2, REA: F-1, STR: F+4, WIL: F, LOG: F-1, INT: F, CHA: F"
    },
    "fire": {
        "name": "Spirit of Fire",
        "category": "Core Elementals",
        "source": "SR6 Core p. 148",
        "doc_link": "chapters/rules_and_downtime.html#conjuring-and-spirit-protocols",
        "powers": [
            {
                "name": "Accident",
                "action": "Major Action",
                "target": "Single Target",
                "effect": "Forces accident/mishap test (REA + INT vs Force x 2).",
            },
            {
                "name": "Astral Form",
                "action": "Always",
                "target": "Self",
                "effect": "Dual-natured or wholly astral entity.",
            },
            {
                "name": "Confusion",
                "action": "Major Action",
                "target": "Single Target",
                "effect": "Dazzles target with flames, applying net hits penalty to all target tests.",
            },
            {
                "name": "Elemental Attack (Fire)",
                "action": "Major Action",
                "target": "LOS (Ranged)",
                "effect": "Projects bolt/blast of fire dealing (Force)P damage with Burning secondary effect.",
            },
            {
                "name": "Energy Aura (Fire)",
                "action": "Always",
                "target": "Self",
                "effect": "Surrounds form in blazing flames; deals fire damage to melee attackers and on touch.",
            },
            {
                "name": "Engulf (Fire)",
                "action": "Major Action",
                "target": "Melee",
                "effect": "Envelops target in intense conflagration dealing (Force)P continuous damage.",
            }
        ],
        "optional_powers": [
            {"name": "Fear", "action": "Major Action", "target": "LOS", "effect": "Terrifies target into fleeing."},
            {"name": "Guard", "action": "Minor Action", "target": "Protected Target", "effect": "Protects against glitches and fire hazards."},
            {"name": "Noxious Breath (Smoke)", "action": "Major Action", "target": "Cone", "effect": "Chokes target with dense toxic smoke."},
            {"name": "Search", "action": "Major Action", "target": "Area", "effect": "Locates target in astral or physical planes."}
        ],
        "weakness": "Allergy (Cold, Severe), Vulnerability (fire extinguishers)",
        "attributes_formula": "BOD: F+1, AGI: F+2, REA: F+3, STR: F-2, WIL: F, LOG: F, INT: F+1, CHA: F"
    },
    "water": {
        "name": "Spirit of Water",
        "category": "Core Elementals",
        "source": "SR6 Core p. 148",
        "doc_link": "chapters/rules_and_downtime.html#conjuring-and-spirit-protocols",
        "powers": [
            {
                "name": "Astral Form",
                "action": "Always",
                "target": "Self",
                "effect": "Dual-natured or wholly astral entity.",
            },
            {
                "name": "Concealment",
                "action": "Minor Action",
                "target": "Target / Area",
                "effect": "Cloaks target in mist, fog, or water reflection; -Force to perception.",
            },
            {
                "name": "Confusion",
                "action": "Major Action",
                "target": "Single Target",
                "effect": "Disorients with shifting water imagery, imposing net hits dice penalty.",
            },
            {
                "name": "Engulf (Water)",
                "action": "Major Action",
                "target": "Melee",
                "effect": "Drowns/engulfs target in water vortex dealing (Force)S fatigue/drowning damage.",
            },
            {
                "name": "Movement",
                "action": "Minor Action",
                "target": "Target",
                "effect": "Accelerates or decelerates swimming and surface speed by Force multiplier.",
            },
            {
                "name": "Search",
                "action": "Major Action",
                "target": "Area",
                "effect": "Searches for person, object, or location across waterways or astral plane.",
            }
        ],
        "optional_powers": [
            {"name": "Accident", "action": "Major Action", "target": "Single Target", "effect": "Causes slipping on ice/water or mechanical flooding."},
            {"name": "Binding", "action": "Major Action", "target": "Close", "effect": "Encapsulates target in dense watery tendrils (STR + BOD vs Force x 2)."},
            {"name": "Elemental Attack (Cold)", "action": "Major Action", "target": "LOS", "effect": "Sub-zero ice/water blast dealing (Force)P with Chilled/Soaked effect."},
            {"name": "Energy Aura (Cold)", "action": "Always", "target": "Self", "effect": "Sub-zero frost armor damaging melee attackers."},
            {"name": "Guard", "action": "Minor Action", "target": "Target", "effect": "Prevents drowning and water accidents."},
            {"name": "Weather Control", "action": "Major Action", "target": "Area", "effect": "Controls local precipitation, fog, and storm conditions."}
        ],
        "weakness": "Allergy (Fire, Severe)",
        "attributes_formula": "BOD: F, AGI: F+1, REA: F+2, STR: F, WIL: F, LOG: F, INT: F, CHA: F"
    },
    "beasts": {
        "name": "Spirit of Beasts",
        "category": "Core Spirits",
        "source": "SR6 Core p. 149",
        "doc_link": "chapters/rules_and_downtime.html#conjuring-and-spirit-protocols",
        "powers": [
            {
                "name": "Animal Control",
                "action": "Major Action",
                "target": "Mundane Animal",
                "effect": "Takes command of natural mundane critters.",
            },
            {
                "name": "Astral Form",
                "action": "Always",
                "target": "Self",
                "effect": "Dual-natured or wholly astral entity.",
            },
            {
                "name": "Enhanced Senses (Hearing, Low-Light, Smell)",
                "action": "Always",
                "target": "Self",
                "effect": "Supernatural olfactory, low-light, and auditory perception.",
            },
            {
                "name": "Fear",
                "action": "Major Action",
                "target": "LOS",
                "effect": "Predatory roar/intimidation forcing targets to flee on failed WIL + LOG test.",
            },
            {
                "name": "Movement",
                "action": "Minor Action",
                "target": "Target",
                "effect": "Boosts or slows target ground movement speed.",
            }
        ],
        "optional_powers": [
            {"name": "Concealment", "action": "Minor Action", "target": "Target", "effect": "Natural camouflage (-Force to perception)."},
            {"name": "Confusion", "action": "Major Action", "target": "Target", "effect": "Predatory distraction causing net hits dice penalty."},
            {"name": "Guard", "action": "Minor Action", "target": "Target", "effect": "Guards against terrain hazards and animal attacks."},
            {"name": "Natural Weapon (Claws/Bite)", "action": "Always", "target": "Melee", "effect": "Deals (Force + 2)P damage in melee."},
            {"name": "Noxious Breath", "action": "Major Action", "target": "Cone", "effect": "Foul predatory breath sickening targets."},
            {"name": "Search", "action": "Major Action", "target": "Area", "effect": "Tracks prey or objects by scent/aura."},
            {"name": "Venom", "action": "Always", "target": "Melee", "effect": "Injects toxic venom upon dealing damage."}
        ],
        "weakness": "Allergy (Silver, Severe)",
        "attributes_formula": "BOD: F+2, AGI: F+1, REA: F, STR: F+2, WIL: F, LOG: F, INT: F, CHA: F"
    },
    "kin": {
        "name": "Spirit of Kin / Man",
        "category": "Core Spirits",
        "source": "SR6 Core p. 149",
        "doc_link": "chapters/rules_and_downtime.html#conjuring-and-spirit-protocols",
        "powers": [
            {
                "name": "Accident",
                "action": "Major Action",
                "target": "Single Target",
                "effect": "Forces accident/mishap test (REA + INT vs Force x 2).",
            },
            {
                "name": "Astral Form",
                "action": "Always",
                "target": "Self",
                "effect": "Dual-natured or wholly astral entity.",
            },
            {
                "name": "Concealment",
                "action": "Minor Action",
                "target": "Single Target / Group",
                "effect": "Subtle perceptual camouflage (-Force to opposing Perception tests).",
            },
            {
                "name": "Confusion",
                "action": "Major Action",
                "target": "Single Target",
                "effect": "Mental fog imposing net hits penalty on all tests.",
            },
            {
                "name": "Enhanced Senses (Low-Light, Thermographic)",
                "action": "Always",
                "target": "Self",
                "effect": "Low-light and thermographic vision.",
            },
            {
                "name": "Guard",
                "action": "Minor Action (Sustained)",
                "target": "Protected Target",
                "effect": "Shields target from glitches, critical failures, and misfortune.",
            },
            {
                "name": "Influence",
                "action": "Major Action",
                "target": "Single Target",
                "effect": "Plants subtle psychic suggestions; target believes suggestion was their own idea.",
            },
            {
                "name": "Search",
                "action": "Major Action",
                "target": "Area",
                "effect": "Searches for person, object, or location.",
            }
        ],
        "optional_powers": [
            {"name": "Fear", "action": "Major Action", "target": "LOS", "effect": "Existential dread forcing retreat."},
            {
                "name": "Innate Spell",
                "action": "Complex Action",
                "target": "Per Spell",
                "effect": "Spirit knows and can cast one chosen spell known to the summoner at Force rating.",
                "requires_choice": True,
                "choice_label": "Innate Spell Choice"
            },
            {"name": "Movement", "action": "Minor Action", "target": "Target", "effect": "Increases or decreases target walking/running speed by Force factor."},
            {"name": "Psychokinesis", "action": "Major Action", "target": "LOS", "effect": "Telekinetic physical manipulation."}
        ],
        "weakness": "Allergy (Ferrous metal, Severe)",
        "attributes_formula": "BOD: F+1, AGI: F, REA: F+2, STR: F-2, WIL: F, LOG: F, INT: F+1, CHA: F"
    },
    "guardian": {
        "name": "Spirit of Guardian",
        "category": "Street Wyrd Spirits",
        "source": "Street Wyrd p. 7 / SRMG v2.4",
        "doc_link": "chapters/rules_and_downtime.html#conjuring-and-spirit-protocols",
        "powers": [
            {
                "name": "Astral Form",
                "action": "Always",
                "target": "Self",
                "effect": "Dual-natured or wholly astral combat guardian.",
            },
            {
                "name": "Guard",
                "action": "Minor Action (Sustained)",
                "target": "Ward",
                "effect": "Safeguards ward from surprise and hazards.",
            },
            {
                "name": "Movement",
                "action": "Minor Action",
                "target": "Target",
                "effect": "Augments tactical positioning and sprint speed.",
            },
            {
                "name": "Natural Weapon (Spectral Blade / Shield)",
                "action": "Always",
                "target": "Melee",
                "effect": "Deals (Force + 3)P physical damage with Armor Piercing.",
            }
        ],
        "optional_powers": [
            {"name": "Armor", "action": "Always", "target": "Self", "effect": "Grants +Force additional hardened armor / Defense Rating."},
            {"name": "Elemental Attack (Vengeance)", "action": "Major Action", "target": "LOS", "effect": "Deals (Force)P ranged energy strike."},
            {"name": "Energy Aura", "action": "Always", "target": "Self", "effect": "Protective radiant shield damaging melee attackers."},
            {"name": "Fear", "action": "Major Action", "target": "LOS", "effect": "Intimidating warrior presence terrifying adversaries."},
            {"name": "Psychokinesis", "action": "Major Action", "target": "LOS", "effect": "Disarms or deflects incoming attacks."}
        ],
        "weakness": "Allergy (Wood, Severe)",
        "attributes_formula": "BOD: F+3, AGI: F+2, REA: F+3, STR: F+3, WIL: F+1, LOG: F, INT: F, CHA: F"
    },
    "guidance": {
        "name": "Spirit of Guidance",
        "category": "Street Wyrd Spirits",
        "source": "Street Wyrd p. 7 / SRMG v2.4",
        "doc_link": "chapters/rules_and_downtime.html#conjuring-and-spirit-protocols",
        "powers": [
            {
                "name": "Astral Form",
                "action": "Always",
                "target": "Self",
                "effect": "Dual-natured ancestral guide.",
            },
            {
                "name": "Divination",
                "action": "Major Action",
                "target": "Summoner",
                "effect": "Grants cryptic insight and +Force bonus Edge on related forthcoming tests.",
            },
            {
                "name": "Guard",
                "action": "Minor Action",
                "target": "Target",
                "effect": "Protects against bad omens, hexes, and glitches.",
            },
            {
                "name": "Search",
                "action": "Major Action",
                "target": "Area",
                "effect": "Guides searcher directly to target or spiritual path.",
            },
            {
                "name": "Shadow Cloak",
                "action": "Minor Action",
                "target": "Self / Target",
                "effect": "Bends spiritual shadows to conceal aura and physical form.",
            }
        ],
        "optional_powers": [
            {"name": "Concealment", "action": "Minor Action", "target": "Target", "effect": "Aura and visual obfuscation."},
            {"name": "Confusion", "action": "Major Action", "target": "Target", "effect": "Labyrinthine mental confusion."},
            {"name": "Influence", "action": "Major Action", "target": "Target", "effect": "Subconscious behavioral guidance."}
        ],
        "weakness": "Allergy (Gold, Severe)",
        "attributes_formula": "BOD: F, AGI: F+1, REA: F+2, STR: F-2, WIL: F+2, LOG: F+2, INT: F+2, CHA: F+1"
    },
    "plant": {
        "name": "Spirit of Plant",
        "category": "Street Wyrd Spirits",
        "source": "Street Wyrd p. 55, 66 / SR5 Street Grimoire",
        "doc_link": "chapters/rules_and_downtime.html#conjuring-and-spirit-protocols",
        "powers": [
            {
                "name": "Astral Form",
                "action": "Always",
                "target": "Self",
                "effect": "Dual-natured or wholly astral entity.",
            },
            {
                "name": "Concealment",
                "action": "Minor Action",
                "target": "Target / Area",
                "effect": "Forest/foliage camouflage (-Force to perception).",
            },
            {
                "name": "Engulf (Vegetation)",
                "action": "Major Action",
                "target": "Melee",
                "effect": "Encloses target inside roots, wood, or thorny tendrils dealing (Force)P continuous damage.",
            },
            {
                "name": "Fear",
                "action": "Major Action",
                "target": "LOS",
                "effect": "Haunted woods terror forcing target to flee on failed WIL + LOG test.",
            },
            {
                "name": "Guard",
                "action": "Minor Action",
                "target": "Target",
                "effect": "Shields against glitches, misfortune, toxins, and environmental hazards.",
            },
            {
                "name": "Magical Guard",
                "action": "Minor Action (Sustained)",
                "target": "Summoner / Ward",
                "effect": "Provides spell defense using Counterspelling equal to spirit Force against incoming spells.",
            },
            {
                "name": "Silence",
                "action": "Major Action",
                "target": "Area",
                "effect": "Dampens all sound within (Force x 2) meter radius.",
            }
        ],
        "optional_powers": [
            {"name": "Accident", "action": "Major Action", "target": "Target", "effect": "Causes root entanglement, stumbling, or falling foliage."},
            {"name": "Confusion", "action": "Major Action", "target": "Target", "effect": "Hallucinogenic spores/pollen imposing net hits penalty."},
            {"name": "Movement", "action": "Minor Action", "target": "Target", "effect": "Accelerates or hinders passage through vegetation/terrain by Force multiplier."},
            {"name": "Noxious Breath", "action": "Major Action", "target": "Cone", "effect": "Chokes target in toxic pollen cloud imposing nausea."},
            {"name": "Search", "action": "Major Action", "target": "Area", "effect": "Searches for person, object, or location via root-network astral tracking."}
        ],
        "great_form_power": "Regeneration (Street Wyrd p. 66)",
        "weakness": "Allergy (Fire, Vulnerability [SR6 p. 229])",
        "attributes_formula": "BOD: F+3, AGI: F-1, REA: F, STR: F+2, WIL: F+1, LOG: F-1, INT: F, CHA: F"
    },
    "task": {
        "name": "Spirit of Task",
        "category": "Street Wyrd Spirits",
        "source": "Street Wyrd p. 7 / SRMG v2.4",
        "doc_link": "chapters/rules_and_downtime.html#conjuring-and-spirit-protocols",
        "powers": [
            {
                "name": "Accident",
                "action": "Major Action",
                "target": "Target",
                "effect": "Industrial mishaps or equipment jams.",
            },
            {
                "name": "Astral Form",
                "action": "Always",
                "target": "Self",
                "effect": "Dual-natured or wholly astral entity.",
            },
            {
                "name": "Binding",
                "action": "Major Action",
                "target": "Melee",
                "effect": "Traps target under heavy machinery or cables.",
            },
            {
                "name": "Movement",
                "action": "Minor Action",
                "target": "Target",
                "effect": "Accelerates physical work or machine operations.",
            },
            {
                "name": "Search",
                "action": "Major Action",
                "target": "Area",
                "effect": "Searches for tools, blueprints, or materials.",
            },
            {
                "name": "Skill",
                "action": "Always",
                "target": "Summoner / Self",
                "effect": "Possesses and provides teamwork dice equal to Force on one chosen technical or physical skill.",
                "requires_choice": True,
                "choice_label": "Designated Skill (e.g., Electronics, Engineering, Cracking)"
            }
        ],
        "optional_powers": [
            {"name": "Concealment", "action": "Minor Action", "target": "Target", "effect": "Hides within industrial equipment."},
            {"name": "Psychokinesis", "action": "Major Action", "target": "LOS", "effect": "Remotely manipulates tools and mechanical levers."}
        ],
        "weakness": "Allergy (Corrosives, Severe)",
        "attributes_formula": "BOD: F+2, AGI: F+1, REA: F+1, STR: F+2, WIL: F, LOG: F+1, INT: F, CHA: F"
    }
}


def get_spirit_channeling_info(spirit_key: str, force: int) -> Optional[Dict[str, Any]]:
    """
    Computes channeling benefits for a specific spirit type and Force rating.
    """
    if spirit_key not in SPIRIT_CATALOG:
        return None

    spec = SPIRIT_CATALOG[spirit_key]
    # Physical attribute augmentation: floor(Force / 2)
    attr_boost = max(1, force // 2) if force > 1 else 0
    wound_boxes_ignored = force

    # Optional powers unlock per SR6 Core: 1 optional power for every 3 full points of Force (floor(Force / 3))
    # Force 1-2: 0, Force 3-5: 1, Force 6-8: 2, etc.
    num_optional_allowed = force // 3

    return {
        "key": spirit_key,
        "name": spec["name"],
        "category": spec["category"],
        "source": spec["source"],
        "force": force,
        "attr_boost": attr_boost,
        "wound_boxes_ignored": wound_boxes_ignored,
        "is_dual_natured": True,
        "base_powers": spec["powers"],
        "num_optional_allowed": num_optional_allowed,
        "optional_powers": spec["optional_powers"] if num_optional_allowed > 0 else [],
        "all_optional_powers": spec["optional_powers"],
        "weakness": spec.get("weakness"),
        "doc_link": spec.get("doc_link", "chapters/rules_and_downtime.html#conjuring-and-spirit-protocols")
    }
