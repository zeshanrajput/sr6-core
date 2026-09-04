"""
Canonical Nanotech & Nanohive Catalog and Resolution Module for Shadowrun 6e.
Covers Monad nanite mechanics, Nanohives (Body Shop p. 108-111), and canonical
nanite colonies (templates, doses) with full rules statblocks and presets.
"""

from typing import Dict, Any, List, Optional


# Canonical Nanohive Colonies Catalog (Body Shop p. 108-112)
NANOHIVE_CATALOG: Dict[str, Dict[str, Any]] = {
    "dynamic_features": {
        "id": "dynamic_features",
        "name": "Dynamic Features",
        "type": "template",
        "default_nv": 1,
        "min_nv": 1,
        "max_nv": 3,
        "fixed_nv": False,
        "source": "Body Shop p. 110",
        "doc_link": "chapters/rules_and_downtime.html#nanoware-protocols",
        "category": "Infiltration / Biometric",
        "effect": "Dynamically shifts epidermal pigmentation, melanin, hair follicles, and subcutaneous facial geometry on command. 1 NV: Cosmetic alterations; 2 NV: Full facial reconstruction (+1 Edge on Disguise); 3 NV: Real-time biometric identity mimicry (+2 Edge on Disguise/Impersonation).",
        "active_by_default": False,
        "stat_effects": {
            "type": "situational",
            "notes": "Cosmetic to full facial shift (+1 to +2 Edge on disguise)"
        }
    },
    "neuromuscular_amplifier": {
        "id": "neuromuscular_amplifier",
        "name": "Neuromuscular Amplifier",
        "type": "template",
        "default_nv": 2,
        "min_nv": 2,
        "max_nv": 4,
        "fixed_nv": False,
        "source": "Body Shop p. 110",
        "doc_link": "chapters/rules_and_downtime.html#nanoware-protocols",
        "category": "Combat Augmentation",
        "effect": "Reinforces skeletal myofibrils and strike vectors through micro-hydraulic nanite lattice networks. Requires at least 2 NV to form the colony, but additional NV (up to 4+ NV) can be assigned for overdriving or enhanced strike amplification. Grants +1 Melee DV to all unarmed and physical strikes (synergizes with Iron Limbs, Bone Density R4, and Toughskin Spines for 10P Flying Kick).",
        "active_by_default": True,
        "stat_effects": {
            "target": "damage:unarmed",
            "value": 1,
            "type": "augmentation",
            "notes": "+1 DV to all melee/unarmed attacks (min 2 NV; overdriving capable)"
        }
    },
    "bio_response_override": {
        "id": "bio_response_override",
        "name": "Bio-Response Override",
        "type": "dose",
        "default_nv": 3,
        "min_nv": 3,
        "max_nv": 3,
        "fixed_nv": True,
        "source": "Body Shop p. 110",
        "doc_link": "chapters/rules_and_downtime.html#nanoware-protocols",
        "category": "Physiological / Resilience",
        "effect": "Single pre-bought dose colony requiring 3 NV from the nanohive to sustain (dies in 1 week without hive maintenance). Suppresses nociceptors and autonomous shock reactions while stabilizing neurochemical homeostasis. Grants +1 Willpower (buffing Composure, Judge Intentions, Memory, and Living Persona Firewall) and adds +1 box to the Stun Condition Monitor.",
        "active_by_default": True,
        "stat_effects": {
            "target": "attribute:willpower",
            "value": 1,
            "type": "augmentation",
            "notes": "+1 Willpower, +1 Stun Condition box (requires 3 NV to sustain)"
        }
    },
    "neurochemical_regulator": {
        "id": "neurochemical_regulator",
        "name": "Neurochemical Regulator",
        "type": "dose",
        "default_nv": 2,
        "min_nv": 2,
        "max_nv": 2,
        "fixed_nv": True,
        "source": "Body Shop p. 110",
        "doc_link": "chapters/rules_and_downtime.html#nanoware-protocols",
        "category": "Social / Psychological",
        "effect": "Single pre-bought dose colony requiring 2 NV from the nanohive to sustain (dies in 1 week without hive maintenance). Modulates endocrine flows, suppressing erratic micro-expressions and voice stress while enhancing charisma projecting. Grants +1 Charisma on social interactions and composure tests.",
        "active_by_default": True,
        "stat_effects": {
            "target": "attribute:charisma",
            "value": 1,
            "type": "augmentation",
            "notes": "+1 Charisma on social and composure tests (requires 2 NV to sustain)"
        }
    },
    "neocortical_neural_amp": {
        "id": "neocortical_neural_amp",
        "name": "Neocortical Neural Amp",
        "type": "dose",
        "default_nv": 2,
        "min_nv": 2,
        "max_nv": 2,
        "fixed_nv": True,
        "source": "Body Shop p. 110",
        "doc_link": "chapters/rules_and_downtime.html#nanoware-protocols",
        "category": "Cognitive Augmentation",
        "effect": "Single pre-bought dose colony requiring 2 NV from the nanohive to sustain (dies in 1 week without hive maintenance). Accelerates synaptic transmission across neocortical columns. Grants +1 dice pool bonus to all Logic-linked skill tests (Biotech, Cracking, Electronics, Engineering). Stacks with Math SPU Edge cost reductions.",
        "active_by_default": True,
        "stat_effects": {
            "target": "attribute:logic",
            "value": 1,
            "type": "skill bonus",
            "notes": "+1 on all Logic skill tests (requires 2 NV to sustain)"
        }
    },
    "limbic_neural_amp": {
        "id": "limbic_neural_amp",
        "name": "Limbic Neural Amp",
        "type": "dose",
        "default_nv": 2,
        "min_nv": 2,
        "max_nv": 2,
        "fixed_nv": True,
        "source": "Body Shop p. 110",
        "doc_link": "chapters/rules_and_downtime.html#nanoware-protocols",
        "category": "Cognitive Augmentation",
        "effect": "Single pre-bought dose colony requiring 2 NV from the nanohive to sustain (dies in 1 week without hive maintenance). Sharpens amygdala and hippocampal sensory processing pathways. Grants +1 dice pool bonus to all Intuition-linked skill tests (Perception, Stealth, Tracking).",
        "active_by_default": True,
        "stat_effects": {
            "target": "attribute:intuition",
            "value": 1,
            "type": "skill bonus",
            "notes": "+1 on all Intuition skill tests (requires 2 NV to sustain)"
        }
    },
    "neural_pattern_reinforcement": {
        "id": "neural_pattern_reinforcement",
        "name": "Neural Pattern Reinforcement",
        "type": "dose",
        "default_nv": 2,
        "min_nv": 2,
        "max_nv": 2,
        "fixed_nv": True,
        "source": "Body Shop p. 110",
        "doc_link": "chapters/rules_and_downtime.html#nanoware-protocols",
        "category": "Motor / Physical Augmentation",
        "effect": "Single pre-bought dose colony requiring 2 NV from the nanohive to sustain (dies in 1 week without hive maintenance). Hardens motor cortex engrams and neuromuscular kinesthetic pathways. Grants +1 dice pool bonus to all Agility-linked skill tests (Athletics, Close Combat, Firearms).",
        "active_by_default": True,
        "stat_effects": {
            "target": "attribute:agility",
            "value": 1,
            "type": "skill bonus",
            "notes": "+1 on all Agility skill tests (requires 2 NV to sustain)"
        }
    },
    "tech_infestation": {
        "id": "tech_infestation",
        "name": "Tech Infestation",
        "type": "dose",
        "default_nv": 1,
        "min_nv": 1,
        "max_nv": 3,
        "fixed_nv": False,
        "source": "Body Shop p. 111",
        "doc_link": "chapters/rules_and_downtime.html#nanoware-protocols",
        "category": "Hardware / Infiltration",
        "effect": "Nanites extrude through dermal contact points into target electronic, commlink, or cyberware hardware circuitry. Provides physical datajack bridging without requiring a cyberware datajack; enables contact hijacking and direct device control.",
        "active_by_default": False,
        "stat_effects": {
            "type": "situational",
            "notes": "Direct dermal datajack bridge & contact hijacking without cyberware datajack"
        }
    }
}


# Operational Presets for Venn
NANOHIVE_PRESETS: Dict[str, Dict[str, Any]] = {
    "default_combat": {
        "name": "Combat & Stealth (Default)",
        "description": "Standard field deployment maximizing melee strike power, neural perception, and cognitive speed.",
        "active_colonies": [
            "neuromuscular_amplifier",
            "bio_response_override",
            "neurochemical_regulator",
            "neocortical_neural_amp",
            "limbic_neural_amp",
            "neural_pattern_reinforcement"
        ],
        "volumes": {
            "neuromuscular_amplifier": 2,
            "bio_response_override": 3,
            "neurochemical_regulator": 2,
            "neocortical_neural_amp": 2,
            "limbic_neural_amp": 2,
            "neural_pattern_reinforcement": 2
        },
        "total_nv": 13,
        "active_count": 6
    },
    "social_infil": {
        "name": "Deep Social Infiltration",
        "description": "Sacrifices strike amplification to run Dynamic Features R3 for full biometric disguise alongside emotional stabilization.",
        "active_colonies": [
            "dynamic_features",
            "bio_response_override",
            "neurochemical_regulator",
            "neocortical_neural_amp",
            "limbic_neural_amp",
            "tech_infestation"
        ],
        "volumes": {
            "dynamic_features": 3,
            "bio_response_override": 3,
            "neurochemical_regulator": 2,
            "neocortical_neural_amp": 2,
            "limbic_neural_amp": 2,
            "tech_infestation": 1
        },
        "total_nv": 13,
        "active_count": 6
    },
    "cyber_hijack": {
        "name": "Cyber & Hardware Hijacking",
        "description": "Prioritizes Tech Infestation for dermal physical hijacking and Dynamic Features for evasion during electronic breaches.",
        "active_colonies": [
            "tech_infestation",
            "neocortical_neural_amp",
            "limbic_neural_amp",
            "neural_pattern_reinforcement",
            "bio_response_override",
            "dynamic_features"
        ],
        "volumes": {
            "tech_infestation": 2,
            "neocortical_neural_amp": 2,
            "limbic_neural_amp": 2,
            "neural_pattern_reinforcement": 2,
            "bio_response_override": 3,
            "dynamic_features": 1
        },
        "total_nv": 12,
        "active_count": 6
    }
}
