"""
Unit tests for the Declarative Modifier Stack, SRMG Multi-Component Pool Optimizations,
SRM +4 Cap, Companion Skill Filtering, Dynamic Vehicle Modification Parser, and Rigging Engine in sr6-core.
"""

import pytest
from sr6core.modifiers import ModifierEngine, PoolModifier, PoolComponent, PoolOptimization
from sr6core.vehicles import parse_vehicle_modifications, calculate_drone_action_pools
from sr6core.rules_engine import (
    get_drone_statblock_table,
    get_drone_action_table,
    get_matrix_protocols_summary,
    get_matrix_action_table,
    get_sprite_action_table
)
from sr6core.creation.deep_audit import deep_audit_character


SAMPLE_YURIKO = {
    "identity": {
        "handle": "Yuriko Star",
        "real_name": "r31k0 Takahashi",
        "metatype": "AI-Pilot AI",
        "stream": "Technoshamans"
    },
    "attributes": {
        "body": 5, "agility": 3, "reaction": 5, "strength": 3,
        "willpower": 6, "logic": 4, "intuition": 2, "charisma": 4,
        "edge": 4, "resonance": 8
    },
    "living_persona": {
        "asdf_bonuses": {"firewall": 3, "sleaze": 1, "data_processing": 1, "attack": 3}
    },
    "qualities": {
        "positive": [{"name": "Natural Hacker"}, {"name": "Sensor Upgrade"}, {"name": "Designer"}],
        "negative": [{"name": "Hooder"}]
    },
    "synergies": {
        "attribute_substitutions": [
            {"domain": "matrix", "quality": "natural_hacker", "substitute_attribute": "resonance"}
        ],
        "foci": [
            {"name": "Resonance Focus", "rating": 4, "applies_to": "resonance"}
        ],
        "companions": [
            {
                "name": "Taz",
                "type": "Assassin Sprite",
                "level": 7,
                "skills": ["cracking", "electronics"],
                "autosofts": ["targeting", "stealth", "clearsight"],
                "powers": ["diagnosis"],
                "symbiosis_bonus": 4,
                "diagnosis_bonus": 3
            }
        ],
        "living_persona_network_tuning": {
            "asdf_bonuses": {"attack": 4, "sleaze": 8, "data_processing": 6, "firewall": 6}
        }
    },
    "skills": [
        {"name": "Tasking", "attribute": "Resonance", "rating": 6, "specialization": "Registering"},
        {"name": "Cracking", "attribute": "Logic", "rating": 5, "specialization": "Hacking"},
        {"name": "Electronics", "attribute": "Logic", "rating": 5, "specialization": "Software"},
        {"name": "Influence", "attribute": "Charisma", "rating": 1}
    ],
    "armors": [
        {"name": "Ares Securetech SkinShield", "rating": 2, "primary": True},
        {"name": "SecureTech Invisi-Shield Armor", "rating": 2, "primary": False}
    ],
    "drones": [
        {
            "name": "Shiawase Butler",
            "body": 4, "armor": 0, "pilot": 2, "sensor": 3, "speed": 8,
            "handling_on": 4, "handling_off": 5, "accel_on": 5, "accel_off": 5,
            "modifications": [
                "Increased Structural Integrity 2",
                "Secondary Propulsion (Rotor)",
                "Increased Sensors 3",
                "Retractable Skates",
                "Wrist Shield"
            ]
        }
    ]
}


def test_companion_filtering_across_all_skills():
    """Verifies Taz the Assassin Sprite grants symbiosis only to possessed skills & autosofts."""
    # 1. Cracking -> +4 Symbiosis
    cracking_mods = ModifierEngine.get_companion_modifiers(SAMPLE_YURIKO, "cracking")
    assert len(cracking_mods) == 1
    assert cracking_mods[0].value == 4
    assert cracking_mods[0].type == "symbiosis"

    # 2. Electronics -> +4 Symbiosis
    elec_mods = ModifierEngine.get_companion_modifiers(SAMPLE_YURIKO, "electronics")
    assert len(elec_mods) == 1
    assert elec_mods[0].value == 4

    # 3. Targeting Autosoft -> +4 Symbiosis
    target_mods = ModifierEngine.get_companion_modifiers(SAMPLE_YURIKO, "targeting")
    assert len(target_mods) == 1
    assert target_mods[0].value == 4

    # 4. Stealth Autosoft -> +4 Symbiosis
    stealth_mods = ModifierEngine.get_companion_modifiers(SAMPLE_YURIKO, "stealth")
    assert len(stealth_mods) == 1
    assert stealth_mods[0].value == 4

    # 5. Clearsight Autosoft -> +4 Symbiosis
    clear_mods = ModifierEngine.get_companion_modifiers(SAMPLE_YURIKO, "clearsight")
    assert len(clear_mods) == 1
    assert clear_mods[0].value == 4

    # 6. Piloting -> +3 Diagnosis
    pilot_mods = ModifierEngine.get_companion_modifiers(SAMPLE_YURIKO, "piloting")
    assert len(pilot_mods) == 1
    assert pilot_mods[0].value == 3
    assert pilot_mods[0].type == "diagnosis"

    # 7. Tasking -> +0 (Taz is a Sprite and cannot learn Tasking)
    tasking_mods = ModifierEngine.get_companion_modifiers(SAMPLE_YURIKO, "tasking")
    assert len(tasking_mods) == 0


def test_natural_hacker_and_skill_pool_calculation():
    """Verifies skill pool calculation with Natural Hacker, Resonance Focus, and Symbiosis."""
    # Cracking: RES (8) + Rating (5) + Focus (4) + Symbiosis (4) = 21d6
    cracking_calc = ModifierEngine.calculate_skill_pool(
        SAMPLE_YURIKO, "Cracking", skill_rating=5, linked_attribute="logic"
    )
    assert cracking_calc["effective_pool"] == 21
    assert cracking_calc["base_pool"] == 9
    assert cracking_calc["effective_attribute"] == "resonance"

    # Tasking: RES (8) + Rating (6) + Focus (4) + No Symbiosis (0) = 18d6
    tasking_calc = ModifierEngine.calculate_skill_pool(
        SAMPLE_YURIKO, "Tasking", skill_rating=6, linked_attribute="resonance"
    )
    assert tasking_calc["effective_pool"] == 18
    assert tasking_calc["base_pool"] == 14


def test_srm_cap_enforcement():
    """Verifies that permanent augmentations to skills and attributes are clamped at SRM +4."""
    over_boosted_char = {
        **SAMPLE_YURIKO,
        "synergies": {
            **SAMPLE_YURIKO["synergies"],
            "companions": [
                {"name": "Taz", "type": "Assassin Sprite", "skills": ["cracking"], "symbiosis_bonus": 4},
                {"name": "Extra Spirit", "type": "Spirit", "skills": ["cracking"], "symbiosis_bonus": 3}
            ]
        }
    }
    calc = ModifierEngine.calculate_skill_pool(
        over_boosted_char, "Cracking", skill_rating=5, linked_attribute="logic"
    )
    # Total augmentations (+4 and +3) should be clamped to +4 max in SRM
    assert calc["effective_pool"] == 21


def test_multi_component_pool_optimization():
    """
    Verifies SRMG multi-component pool optimization:
    - Component 1 (Attribute A): capped at +4 augmentation
    - Component 2 (Attribute B / Skill): capped at +4 augmentation
    - Component 3 (Action Component): capped at +4 augmentation
    - Specializations & Teamwork are exempt from the +4 augmentation limit.
    - Total possible augmented bonus across 3 components = +12.
    """
    comp1 = PoolComponent("Attribute A", 5, "attribute", [
        PoolModifier("attr:a", "augmentation", "Cyberware", 3),
        PoolModifier("attr:a", "augmentation", "Bioware", 3)  # 3+3=6, clamped to 4
    ])
    assert comp1.raw_aug_bonus == 6
    assert comp1.clamped_aug_bonus == 4
    assert comp1.effective_value == 9

    comp2 = PoolComponent("Skill B", 6, "skill", [
        PoolModifier("skill:b", "symbiosis", "Sprite Symbiosis", 5)  # clamped to 4
    ])
    assert comp2.clamped_aug_bonus == 4
    assert comp2.effective_value == 10

    comp3 = PoolComponent("Action Attr C", 4, "action_attribute", [
        PoolModifier("attr:c", "focus", "Power Focus", 4)
    ])
    assert comp3.clamped_aug_bonus == 4
    assert comp3.effective_value == 8

    pool_opt = PoolOptimization(
        name="Multi-Component Test",
        components=[comp1, comp2, comp3],
        specialization=PoolModifier("skill:b", "specialization", "Spec", 2),
        teamwork=PoolModifier("skill:b", "teamwork", "Ally Teamwork", 4),
        tactical_modifiers=[PoolModifier("test", "tactical", "Tactical App", 2)]
    )

    # Base: 5 + 6 + 4 + 2 (spec) = 17
    # Total pool: 9 + 10 + 8 + 2 (spec) + 4 (teamwork) + 2 (tactical) = 35d6
    assert pool_opt.base_pool == 15
    assert pool_opt.total_pool == 35
    assert pool_opt.bought_hits == 8
    assert pool_opt.total_augmentations == 12
    assert pool_opt.max_possible_augmentations == 12


def test_matrix_action_pools_comprehensive():
    """Verifies all 7 standardized Matrix Action Pools for Yuriko."""
    pools = ModifierEngine.get_matrix_action_pools(SAMPLE_YURIKO)

    # 1. Offensive Cracking: Hacking -> 27d6 (1 wild), 6 Hits
    hacking = pools["cracking_hacking"]
    assert hacking.total_pool == 27
    assert hacking.bought_hits == 6
    assert hacking.wild_dice == 1

    # 2. Offensive Cracking: Other -> 24d6 (1 wild), 6 Hits
    other = pools["cracking_other"]
    assert other.total_pool == 24
    assert other.bought_hits == 6
    assert other.wild_dice == 1

    # 3. Full Matrix Defense -> 34d6, 8 Hits
    mdef = pools["full_matrix_defense"]
    assert mdef.total_pool == 34
    assert mdef.bought_hits == 8

    # 4. Electronics: Software -> 23d6, 5 Hits
    soft = pools["electronics_software"]
    assert soft.total_pool == 23
    assert soft.bought_hits == 5

    # 5. Electronics: Other -> 21d6, 5 Hits
    elec = pools["electronics_other"]
    assert elec.total_pool == 21
    assert elec.bought_hits == 5

    # 6. Downtime Buying Gear -> 23d6, 5 Hits
    buy = pools["buy_gear"]
    assert buy.total_pool == 23
    assert buy.bought_hits == 5

    # 7. Programming / Coding -> 23d6, 5 Hits
    prog = pools["programming"]
    assert prog.total_pool == 23
    assert prog.bought_hits == 5


def test_dynamic_vehicle_modification_parser():
    """Verifies that vehicle modifications dynamically calculate augmented Body, Armor, and Sensors."""
    butler = SAMPLE_YURIKO["drones"][0]
    profile = parse_vehicle_modifications(butler, char_data=SAMPLE_YURIKO)
    assert profile["augmented_body"] == 6  # 4 base + 2 structural
    assert profile["inhabited_body"] == 7  # 6 + 1 inhabited tuning
    assert profile["augmented_armor"] == 8   # 4 worn anthro (2 skin + 2 invisi) + 4 wrist shield
    assert profile["augmented_sensor"] == 7  # 3 base + 3 enhanced + 1 network sensor upgrade
    assert profile["has_rotor"] is True
    assert "Rotor: 5" in profile["handling_str"]
    assert "Rotor: 120" in profile["speed_str"]


def test_drone_action_pool_evaluator():
    """Verifies Inhabited Override and Remote AR action pool calculations."""
    butler = SAMPLE_YURIKO["drones"][0]
    
    # Mode 1: Inhabited Override (Includes Designer Quality +1 Pilot bonus on Home Device)
    pools_inhabited = calculate_drone_action_pools(SAMPLE_YURIKO, butler, mode="inhabited_override")
    assert pools_inhabited["piloting"]["pool"] == 23  # Maneuvering 7 + Pilot/RES 9 + Focus 4 + Diagnosis 3
    assert pools_inhabited["gunnery"]["pool"] == 24   # Targeting 7 + Pilot/RES 9 + Focus 4 + Symbiosis 4
    assert pools_inhabited["evasion"]["pool"] == 24   # Evasion 7 + Pilot/RES 9 + Focus 4 + Symbiosis 4
    assert pools_inhabited["stealth"]["pool"] == 26   # Stealth 7 + Pilot/RES 9 + Focus 4 + Symbiosis 4 + Sneak 2

    # Mode 2: Remote AR
    pools_remote = calculate_drone_action_pools(SAMPLE_YURIKO, butler, mode="remote_ar")
    assert pools_remote["piloting"]["pool"] == 19     # Maneuvering 7 + Sleaze 9 + Diagnosis 3
    assert pools_remote["evasion"]["pool"] == 20      # Evasion 7 + Sleaze 9 + Symbiosis 4


def test_matrix_protocols_summary():
    """Verifies active ASDF and full matrix defense calculations."""
    asdf = ModifierEngine.get_living_persona_asdf(SAMPLE_YURIKO)
    assert asdf["attack"] == 7
    assert asdf["sleaze"] == 9
    assert asdf["data_processing"] == 7
    assert asdf["firewall"] == 9

    mdef = ModifierEngine.get_full_matrix_defense(SAMPLE_YURIKO)
    assert mdef["pool"] == 34  # 8 RES + 9 FW + 6 PA + 7 DP + 4 Focus = 34
    assert mdef["effective_hits"] == 8


def test_matrix_action_table_renderer():
    """Verifies that get_matrix_action_table generates a valid Markdown table."""
    table_md = get_matrix_action_table("yuriko")
    assert "| Action Category / Test | Base Stat + Skill | Applied Modifiers Math | Final Dice Pool | Bought Hits |" in table_md
    assert "**Offensive Cracking: Hacking**" in table_md
    assert "**27d6** (1 wild)" in table_md
    assert "**6 Hits**" in table_md
    assert "**Full Matrix Defense Test**" in table_md
    assert "**34d6**" in table_md
    assert "**8 Hits**" in table_md


def test_sprite_action_table_renderer():
    """Verifies that get_sprite_action_table generates valid downtime tables."""
    table_md = get_sprite_action_table("yuriko", sprite_level=7)
    assert "Compile Sprite (L7)" in table_md
    assert "Register Sprite (L7)" in table_md
    assert "Resonance Focus Activation" in table_md


def test_deep_audit_synergies():
    """Verifies deep character auditing on synergies and augmentation caps."""
    audit_res = deep_audit_character("yuriko")
    assert "synergy_audits" in audit_res
    assert len(audit_res["synergy_audits"]) >= 2
    # All synergies for Yuriko must be within the +4 SRMG cap
    assert all(s["srm_cap_valid"] for s in audit_res["synergy_audits"])


def test_weapon_attack_table_renderer():
    """Verifies that get_weapon_attack_table dynamically computes weapon arrays, firing modes, and effective AR."""
    from sr6core.rules_engine import get_weapon_attack_table
    table_md = get_weapon_attack_table("yuriko")
    assert "| Weapon Name | Mode (Rounds) | Final DV | Final Effective AR (C / N / M / F / E) | Notes & Constraints |" in table_md
    assert "**Red Fox Array (Link-Fired)**" in table_md
    assert "10P" in table_md
    assert "**Crimson Wasp Array (2x Link-Fired)**" in table_md
    assert "7P" in table_md
    assert "**Ares Predator VI**" in table_md
    assert "**Monofilament Whip**" in table_md
    assert "**Amalgam Cestas (Butler - Phys)**" in table_md


def test_character_table_pools():
    """Verifies that get_character_table_pools detects domain relevance per archetype."""
    from sr6core.rules_engine import get_character_table_pools
    yuriko_pools = get_character_table_pools("yuriko")
    assert "matrix_operations" in yuriko_pools["active_domains"]
    assert "rigging_and_drones" in yuriko_pools["active_domains"]
    assert "resonance_emergence" in yuriko_pools["active_domains"]
    assert yuriko_pools["is_technomancer"] is True
    assert yuriko_pools["is_magician"] is False


def test_canonical_contacts_and_log_engine():
    """Verifies that canonical SRM contacts lock Connection ratings and auto-promote loyalty via favor points."""
    from sr6core.contacts import is_canonical_contact, get_canonical_contact
    from sr6core.log_engine import reset_log_state, contact, inc, state

    assert is_canonical_contact("Brynne Taggart") is True
    assert is_canonical_contact("Whiskey") is True
    assert is_canonical_contact("Indomitable Will") is True
    assert is_canonical_contact("Roanoke") is True
    assert is_canonical_contact("Lady Brane Deigh") is True
    assert is_canonical_contact("Piotr Krolik") is False

    reset_log_state()
    # Initial encounter
    c_str = contact("Brynne Taggart", connection=10, loyalty=2, notes="Character Creation")
    # Returns formatted Markdown string
    assert "**Brynne Taggart**" in c_str
    assert "C:4 L:2" in c_str
    # Canonical connection MUST be 4, ignoring 10
    c = state["Contacts"]["Brynne Taggart"]
    assert c["connection"] == 4
    assert c["loyalty"] == 2
    assert c["favors"] == 0
    assert "Getting jobs" in c["description"]

    # Mission 1 gains 1 FP (Total 1 FP -> not enough for Loyalty 3, needs 3 FP)
    contact("Brynne Taggart", fp=1, notes="SRM 2081-05")
    assert state["Contacts"]["Brynne Taggart"]["loyalty"] == 2
    assert state["Contacts"]["Brynne Taggart"]["favors"] == 1

    # Mission 2 gains 2 FP (Total 3 FP -> auto-promotes to Loyalty 3, spending 3 FP)
    contact("Brynne Taggart", fp=2, notes="SRM 2081-06")
    assert state["Contacts"]["Brynne Taggart"]["loyalty"] == 3
    assert state["Contacts"]["Brynne Taggart"]["favors"] == 0
    assert state["Contacts"]["Brynne Taggart"]["connection"] == 4

    # Lifetime tracking
    inc("Karma", 5)
    inc("Nuyen", 10000)
    inc("Karma", -3)
    inc("Nuyen", -4000)
    assert state["Karma"] == 2
    assert state["Lifetime_Karma"] == 5
    assert state["Nuyen"] == 6000
    assert state["Lifetime_Nuyen"] == 10000


def test_sprite_commands_table_renderer():
    """Verifies that get_sprite_commands_table correctly renders all 6 commands and SRMG rules."""
    from sr6core.rules_engine import get_sprite_commands_table
    table = get_sprite_commands_table("yuriko", sprite_level=7)
    assert "| **Signal Boost**" in table
    assert "| **Host Ken**" in table
    assert "| **Hyperthreading**" in table
    assert "| **File Ken**" in table
    assert "| **Cybercombat Boost**" in table
    assert "| **Device Ken**" in table
    assert "+4 Matrix DV" in table  # ceil(7/2) = 4
    assert "Reduces Noise by **7**" in table
    assert "Teamwork rules apply" in table


def test_magic_and_social_action_pools_and_tables():
    """Verifies that ModifierEngine and rules_engine correctly calculate magic and social action pools for Velvet."""
    from sr6core.character_manager import CharacterManager
    from sr6core.modifiers import ModifierEngine
    from sr6core.rules_engine import get_magic_action_table, get_social_action_table, get_scene_strategy_table

    cm = CharacterManager()
    char = cm.get_character_data("velvet")
    assert char is not None

    # Enhanced mode (Default)
    magic_pools_enh = ModifierEngine.get_magic_action_pools(char, enhanced=True)
    assert magic_pools_enh["spellcasting"].total_pool == 15  # Sorcery 6 + MAG 6 + Impr Ability R3
    assert magic_pools_enh["drain_resistance"].total_pool == 23  # WIL 9 + CHA 14 = 23d6 (5 Hits)
    assert magic_pools_enh["drain_resistance"].bought_hits == 5

    # Baseline mode
    magic_pools_base = ModifierEngine.get_magic_action_pools(char, enhanced=False)
    assert magic_pools_base["drain_resistance"].total_pool == 15  # WIL 5 + CHA 10 = 15d6 (3 Hits)
    assert magic_pools_base["drain_resistance"].bought_hits == 3

    # Social Enhanced mode (Default)
    social_pools_enh = ModifierEngine.get_social_action_pools(char, scene_mode="social_enhanced")
    assert social_pools_enh["influence"].total_pool == 19  # Influence 5 + CHA 14 = 19d6 (4 Hits)
    assert social_pools_enh["composure"].total_pool == 23  # WIL 9 + CHA 14 = 23d6 (5 Hits)
    assert social_pools_enh["judge_intentions"].total_pool == 16  # INT 7 + WIL 9 = 16d6 (4 Hits)

    # Social Baseline mode
    social_pools_base = ModifierEngine.get_social_action_pools(char, scene_mode="baseline")
    assert social_pools_base["influence"].total_pool == 15  # Influence 5 + CHA 10 = 15d6 (3 Hits)
    assert social_pools_base["judge_intentions"].total_pool == 8  # INT 3 + WIL 5 = 8d6 (2 Hits)

    # Tables
    magic_table = get_magic_action_table("velvet")
    assert "Spellcasting (Sorcery)" in magic_table
    assert "**15d6**" in magic_table
    assert "**3 Hits**" in magic_table

    social_table = get_social_action_table("velvet")
    assert "Social Negotiation" in social_table
    assert "**19d6**" in social_table
    assert "**4 Hits**" in social_table

    strategy_table = get_scene_strategy_table("velvet")
    assert "Social & Legwork Mode" in strategy_table
    assert "Combat Mode" in strategy_table




