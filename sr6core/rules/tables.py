"""
Dedicated Action Economy, Status Effects, and Edge Boost Tables for SR6 Core.
Provides relational schema and seed dataset for:
- ref_actions: Minor, Major, Free, and Edge action economy & tests
- ref_status_effects: Conditions (Burning, Stunned, Dazed, Hobbled, etc.) and recovery tests
- ref_edge_boosts: 1-5 Edge costs, triggers, timing, and mechanical effects
"""

import sqlite3
from typing import Dict, Any, List, Optional


ACTIONS_DATA = [
    # Minor Actions
    {
        "id": "move",
        "name": "Move",
        "action_type": "Minor",
        "category": "Combat",
        "test": "None",
        "opposed": "None",
        "threshold": "None",
        "description": "Move up to your tactical movement speed (typically 10 meters). Can be taken multiple times per turn.",
        "source": "SR6 Core p. 42"
    },
    {
        "id": "take_cover",
        "name": "Take Cover",
        "action_type": "Minor",
        "category": "Combat",
        "test": "None",
        "opposed": "None",
        "threshold": "None",
        "description": "Position yourself behind physical terrain to gain Cover status (+2 or +4 Defense Rating).",
        "source": "SR6 Core p. 42"
    },
    {
        "id": "drop_prone",
        "name": "Drop Prone",
        "action_type": "Minor",
        "category": "Combat",
        "test": "None",
        "opposed": "None",
        "threshold": "None",
        "description": "Drop to the ground to gain Prone status (+2 DR vs ranged attacks, -2 DR vs melee attacks).",
        "source": "SR6 Core p. 41"
    },
    {
        "id": "stand_up",
        "name": "Stand Up",
        "action_type": "Minor",
        "category": "Combat",
        "test": "Athletics + Agility (if grappled or injured)",
        "opposed": "None",
        "threshold": "1",
        "description": "Stand up from prone or fallen position. Removes Prone status.",
        "source": "SR6 Core p. 42"
    },
    {
        "id": "reload_weapon",
        "name": "Reload Weapon",
        "action_type": "Minor",
        "category": "Combat",
        "test": "None",
        "opposed": "None",
        "threshold": "None",
        "description": "Insert fresh clip, speedloader, or battery into a readied firearm.",
        "source": "SR6 Core p. 42"
    },
    {
        "id": "quick_draw",
        "name": "Quick Draw",
        "action_type": "Minor",
        "category": "Combat",
        "test": "Firearms + Reaction",
        "opposed": "None",
        "threshold": "3",
        "description": "Draw a weapon and immediately ready it as a single Minor action. If successful, can attack as Major action on same turn.",
        "source": "SR6 Core p. 42"
    },
    {
        "id": "change_device_mode",
        "name": "Change Device Mode",
        "action_type": "Minor",
        "category": "Matrix/General",
        "test": "None",
        "opposed": "None",
        "threshold": "None",
        "description": "Switch operating mode on a gear item, cyberware implant, or commlink (e.g. Wireless ON/OFF, Smartgun link, AR to VR).",
        "source": "SR6 Core p. 41"
    },
    {
        "id": "shift_perception",
        "name": "Shift Perception",
        "action_type": "Minor",
        "category": "Magic",
        "test": "None",
        "opposed": "None",
        "threshold": "None",
        "description": "Awakened character shifts perception between the Physical and Astral planes.",
        "source": "SR6 Core p. 130"
    },
    {
        "id": "command_drone",
        "name": "Command Drone",
        "action_type": "Minor",
        "category": "Rigging",
        "test": "None",
        "opposed": "None",
        "threshold": "None",
        "description": "Issue verbal or DNI instruction to a slaved autonomous drone in your PAN/WAN.",
        "source": "SR6 Core p. 196"
    },
    {
        "id": "avoid_incoming",
        "name": "Avoid Incoming",
        "action_type": "Minor",
        "category": "Combat",
        "test": "Athletics + Agility",
        "opposed": "None",
        "threshold": "2",
        "description": "Drop to cover or dive away from an incoming blast radius, grenade, or suppression fire cone.",
        "source": "SR6 Core p. 41"
    },

    # Major Actions
    {
        "id": "attack",
        "name": "Attack",
        "action_type": "Major",
        "category": "Combat",
        "test": "Firearms or Close Combat + Agility",
        "opposed": "Defense Rating & Reaction + Intuition",
        "threshold": "Opposed",
        "description": "Make a single ranged or melee attack using a readied weapon against a target.",
        "source": "SR6 Core p. 42"
    },
    {
        "id": "fire_weapon",
        "name": "Fire Weapon",
        "action_type": "Major",
        "category": "Combat",
        "test": "Firearms + Agility",
        "opposed": "Defense Rating & Reaction + Intuition",
        "threshold": "Opposed",
        "description": "Discharge a readied ranged firearm in Single Shot, Semi-Automatic, Burst Fire, or Full Auto mode.",
        "source": "SR6 Core p. 42"
    },
    {
        "id": "cast_spell",
        "name": "Cast Spell",
        "action_type": "Major",
        "category": "Magic",
        "test": "Sorcery + Magic",
        "opposed": "Target Defense Rating / Willpower / Intuition",
        "threshold": "Opposed or Spell Threshold",
        "description": "Cast an active combat, health, illusion, manipulation, or detection spell. Incurs drain resistance test.",
        "source": "SR6 Core p. 131"
    },
    {
        "id": "compile_sprite",
        "name": "Compile Sprite",
        "action_type": "Major",
        "category": "Matrix/Resonance",
        "test": "Tasking + Resonance",
        "opposed": "Sprite Level x 2",
        "threshold": "Opposed",
        "description": "Compile a Resonance sprite from the Matrix substrate. Net hits equal registered tasks.",
        "source": "SR6 Core p. 187"
    },
    {
        "id": "register_sprite",
        "name": "Register Sprite",
        "action_type": "Major",
        "category": "Matrix/Resonance",
        "test": "Tasking + Resonance",
        "opposed": "Sprite Level x 2",
        "threshold": "Opposed",
        "description": "Register an active compiled sprite for long-term services. Incurs fading damage.",
        "source": "SR6 Core p. 188"
    },
    {
        "id": "brute_force",
        "name": "Brute Force",
        "action_type": "Major",
        "category": "Matrix",
        "test": "Cracking + Logic",
        "opposed": "Firewall + Willpower",
        "threshold": "Opposed",
        "description": "Forcefully smash through target ICE or host defenses to gain User or Admin Matrix access. Alerts host on failure.",
        "source": "SR6 Core p. 178"
    },
    {
        "id": "hack_on_the_fly",
        "name": "Hack on the Fly",
        "action_type": "Major",
        "category": "Matrix",
        "test": "Cracking + Logic",
        "opposed": "Firewall + Intuition",
        "threshold": "Opposed",
        "description": "Stealthily inject exploit payloads to gain User or Admin Matrix access without raising Overwatch Score.",
        "source": "SR6 Core p. 179"
    },
    {
        "id": "data_spike",
        "name": "Data Spike",
        "action_type": "Major",
        "category": "Matrix",
        "test": "Cracking + Logic",
        "opposed": "Firewall + Willpower",
        "threshold": "Opposed",
        "description": "Send destructive cybercombat code pulse inflicting Matrix Damage Value (DV) directly to persona or device.",
        "source": "SR6 Core p. 179"
    },
    {
        "id": "full_defense",
        "name": "Full Defense",
        "action_type": "Major",
        "category": "Combat",
        "test": "None",
        "opposed": "None",
        "threshold": "None",
        "description": "Focus entirely on dodging and evasion. Add your Willpower attribute to all defense tests until your next turn.",
        "source": "SR6 Core p. 43"
    },
    {
        "id": "sprint",
        "name": "Sprint",
        "action_type": "Major",
        "category": "Combat",
        "test": "Athletics + Agility",
        "opposed": "None",
        "threshold": "Hits x 5m",
        "description": "Surge into a dead sprint, adding +5 meters per hit to your movement distance.",
        "source": "SR6 Core p. 43"
    },
    {
        "id": "rigger_jump_in",
        "name": "Jump In (Rigger)",
        "action_type": "Major",
        "category": "Rigging",
        "test": "None",
        "opposed": "None",
        "threshold": "None",
        "description": "Directly inhabit a rigged vehicle or drone via Control Rig, substituting vehicle stats for your own.",
        "source": "SR6 Core p. 197"
    },
    {
        "id": "use_skill",
        "name": "Use Skill",
        "action_type": "Major",
        "category": "General",
        "test": "Linked Skill + Attribute",
        "opposed": "Opposed or Static Threshold",
        "threshold": "Variable",
        "description": "Perform any complex active skill test (Engineering, Biotech, Influence, Con, Stealth, Perception).",
        "source": "SR6 Core p. 44"
    }
]


STATUS_EFFECTS_DATA = [
    {
        "id": "blinded",
        "name": "Blinded",
        "category": "Physical",
        "effect": "-4 dice pool penalty to all physical, combat, and perception tests. Cannot target with Line of Sight (LOS) spells.",
        "duration": "Until obstruction or flash effect is cleared",
        "recovery_test": "Body + Willpower (1)",
        "source": "SR6 Core p. 51"
    },
    {
        "id": "burning",
        "name": "Burning",
        "category": "Environmental",
        "effect": "Takes [Rating]P Physical damage at the start of each combat round. Flame spreads to adjacent flammable items.",
        "duration": "Until extinguished or fuel consumed",
        "recovery_test": "Agility + Reaction (2) to drop and roll, or water immersion",
        "source": "SR6 Core p. 51"
    },
    {
        "id": "chilled",
        "name": "Chilled",
        "category": "Environmental",
        "effect": "-2 dice pool penalty to physical actions. Tactical movement speed reduced by 50%.",
        "duration": "1 hour or until adequately warmed",
        "recovery_test": "Body + Willpower (2)",
        "source": "SR6 Core p. 51"
    },
    {
        "id": "confused",
        "name": "Confused",
        "category": "Mental",
        "effect": "-2 dice pool penalty to all mental, tactical, and Matrix actions. Target cannot allocate Edge to teamwork tests.",
        "duration": "1 minute per net hit",
        "recovery_test": "Logic + Willpower (2)",
        "source": "SR6 Core p. 52"
    },
    {
        "id": "corrosive",
        "name": "Corrosive",
        "category": "Environmental",
        "effect": "Suffers [Rating]P damage each combat round. Reduces armor rating by 1 each round until completely dissolved.",
        "duration": "Until washed off or neutralized",
        "recovery_test": "Reaction + Agility (2)",
        "source": "SR6 Core p. 52"
    },
    {
        "id": "cover",
        "name": "Cover",
        "category": "Combat",
        "effect": "+2 bonus to Defense Rating (Light Cover) or +4 bonus to Defense Rating (Heavy Cover) against ranged attacks.",
        "duration": "While maintaining position behind terrain",
        "recovery_test": "None",
        "source": "SR6 Core p. 52"
    },
    {
        "id": "dazed",
        "name": "Dazed",
        "category": "Mental",
        "effect": "Lose 1 Minor Action on each combat turn. -2 dice pool penalty to all tests.",
        "duration": "1 combat round per hit",
        "recovery_test": "Willpower + Body (2)",
        "source": "SR6 Core p. 52"
    },
    {
        "id": "deafened",
        "name": "Deafened",
        "category": "Physical",
        "effect": "-2 dice pool penalty to Perception tests. Unaware of acoustic alerts, footsteps, or verbal calls.",
        "duration": "Until flashbang/acoustic trauma clears",
        "recovery_test": "None",
        "source": "SR6 Core p. 52"
    },
    {
        "id": "fatigued",
        "name": "Fatigued",
        "category": "Physical",
        "effect": "-2 dice pool penalty to all physical pools. Drain and Fading resistance thresholds increase by 1.",
        "duration": "Until 8 hours of uninterrupted rest",
        "recovery_test": "Body + Willpower (3)",
        "source": "SR6 Core p. 52"
    },
    {
        "id": "frightened",
        "name": "Frightened",
        "category": "Mental",
        "effect": "Target must immediately move away from source of fear. Suffixes -3 dice pool penalty if forced into melee.",
        "duration": "Duration of critter power or spell",
        "recovery_test": "Willpower + Charisma (3)",
        "source": "SR6 Core p. 53"
    },
    {
        "id": "hobbled",
        "name": "Hobbled",
        "category": "Physical",
        "effect": "Movement speed reduced by 50%. Cannot take Sprint actions. -2 penalty to athletic defense.",
        "duration": "Until physical damage is treated",
        "recovery_test": "First Aid / Medicine (2)",
        "source": "SR6 Core p. 53"
    },
    {
        "id": "invisible",
        "name": "Invisible",
        "category": "Magic/Tech",
        "effect": "Cannot be targeted with direct line of sight or visual perception. Receives Heavy Cover (+4 DR) against area attacks.",
        "duration": "While spell or cloaking system sustained",
        "recovery_test": "Intuition + Perception vs. Spell Invisibility Hits",
        "source": "SR6 Core p. 53"
    },
    {
        "id": "nauseated",
        "name": "Nauseated",
        "category": "Physical",
        "effect": "Character can only take Minor Actions. -2 penalty to all tests.",
        "duration": "Duration of toxin or spell effect",
        "recovery_test": "Body + Willpower (3)",
        "source": "SR6 Core p. 53"
    },
    {
        "id": "paralyzed",
        "name": "Paralyzed",
        "category": "Physical",
        "effect": "Complete biological motor shutdown. Incapable of physical actions. Defense Rating reduced to 0.",
        "duration": "Per toxin/spell duration profile",
        "recovery_test": "Body + Willpower (4)",
        "source": "SR6 Core p. 53"
    },
    {
        "id": "petrified",
        "name": "Petrified",
        "category": "Magic",
        "effect": "Turned to stone. Immune to toxins and biofeedback; takes no biological damage.",
        "duration": "Permanent unless dispelled",
        "recovery_test": "Dispel Magic test",
        "source": "SR6 Core p. 54"
    },
    {
        "id": "poisoned",
        "name": "Poisoned",
        "category": "Physical",
        "effect": "Suffers toxin DV and secondary conditions (Nauseated, Dazed, or Stunned) based on poison toxicity profile.",
        "duration": "Per chemical compound speed and duration",
        "recovery_test": "Body + Willpower vs Toxin Power",
        "source": "SR6 Core p. 54"
    },
    {
        "id": "prone",
        "name": "Prone",
        "category": "Combat",
        "effect": "+2 Defense Rating vs ranged attacks; -2 Defense Rating vs melee attacks.",
        "duration": "Until Stand Up action taken",
        "recovery_test": "Stand Up Minor Action",
        "source": "SR6 Core p. 54"
    },
    {
        "id": "stunned",
        "name": "Stunned",
        "category": "Physical",
        "effect": "Incapable of taking actions for 1 full combat round. Drops all sustained spells, foci, and complex forms.",
        "duration": "1 combat round",
        "recovery_test": "Body + Willpower (2)",
        "source": "SR6 Core p. 54"
    },
    {
        "id": "unconscious",
        "name": "Unconscious",
        "category": "Physical",
        "effect": "Character is completely incapacitated. Defense Rating drops to 0. Auto-fails all active defense tests.",
        "duration": "Until damage box healed or awakened by medical care",
        "recovery_test": "First Aid / Biotech test",
        "source": "SR6 Core p. 54"
    }
]


EDGE_BOOSTS_DATA = [
    {
        "id": "reroll_one",
        "name": "Reroll One Die",
        "cost": 1,
        "timing": "Post-roll",
        "category": "Core",
        "effect": "Reroll any single die from your roll result. You must keep the second result.",
        "source": "SR6 Core p. 45"
    },
    {
        "id": "negate_edge_boost",
        "name": "Negate Opponent Edge Boost",
        "cost": 1,
        "timing": "Any",
        "category": "Tactical",
        "effect": "Cancel 1 Edge spent by an opponent on a single opposed test.",
        "source": "SR6 Core p. 45"
    },
    {
        "id": "add_three_to_initiative",
        "name": "Add +3 to Initiative Score",
        "cost": 1,
        "timing": "Pre-roll",
        "category": "Combat",
        "effect": "Increase your Initiative Score by +3 for the current combat round.",
        "source": "SR6 Core p. 45"
    },
    {
        "id": "plus_one_die_result",
        "name": "+1 to Single Die Roll",
        "cost": 2,
        "timing": "Post-roll",
        "category": "Core",
        "effect": "Increase the face value of a single die by 1 (e.g. turn a 4 into a 5 to gain a hit).",
        "source": "SR6 Core p. 45"
    },
    {
        "id": "give_ally_edge",
        "name": "Give Ally 1 Edge",
        "cost": 2,
        "timing": "Any",
        "category": "Tactical",
        "effect": "Transfer 1 point of Edge to an allied runner who is in visual or comm range.",
        "source": "SR6 Core p. 45"
    },
    {
        "id": "buy_one_automatic_hit",
        "name": "Buy 1 Automatic Hit",
        "cost": 2,
        "timing": "Post-roll",
        "category": "Core",
        "effect": "Add 1 automatic hit to your test result after seeing the initial roll.",
        "source": "SR6 Core p. 46"
    },
    {
        "id": "heal_one_stun",
        "name": "Heal 1 Stun Damage",
        "cost": 3,
        "timing": "Any",
        "category": "Combat",
        "effect": "Immediately clear 1 box of Stun damage from your Condition Monitor.",
        "source": "SR6 Core p. 46"
    },
    {
        "id": "extra_minor_action",
        "name": "Extra Minor Action",
        "cost": 3,
        "timing": "Any",
        "category": "Combat",
        "effect": "Gain 1 additional Minor Action to spend on your current combat turn.",
        "source": "SR6 Core p. 46"
    },
    {
        "id": "add_edge_to_pool",
        "name": "Add Edge to Pool & Exploding Sixes",
        "cost": 4,
        "timing": "Pre-roll",
        "category": "Core",
        "effect": "Add your full Edge attribute rating to your dice pool before rolling. All 6s explode (Rule of Six).",
        "source": "SR6 Core p. 46"
    },
    {
        "id": "reroll_all_failures",
        "name": "Reroll All Failures",
        "cost": 4,
        "timing": "Post-roll",
        "category": "Core",
        "effect": "Reroll every die in your pool that did not score a hit (rolls of 1 through 4).",
        "source": "SR6 Core p. 46"
    },
    {
        "id": "toggled_critical_hit",
        "name": "Critical Hit (Damage Surge)",
        "cost": 5,
        "timing": "Post-roll",
        "category": "Combat",
        "effect": "Transform a successful attack into a critical strike: add +3 DV or knock the target down.",
        "source": "SR6 Core p. 46"
    },
    {
        "id": "count_twos_as_glitches",
        "name": "Subvert Opponent (2s Glitch)",
        "cost": 5,
        "timing": "Pre-roll",
        "category": "Tactical",
        "effect": "Forces the opponent to count rolls of both 1 and 2 toward calculating a glitch on their test.",
        "source": "SR6 Core p. 46"
    }
]


def init_gameplay_tables(conn: sqlite3.Connection):
    """Creates ref_actions, ref_status_effects, and ref_edge_boosts tables."""
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ref_actions (
            id TEXT PRIMARY KEY,
            name TEXT,
            action_type TEXT,
            category TEXT,
            test TEXT,
            opposed TEXT,
            threshold TEXT,
            description TEXT,
            source TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ref_status_effects (
            id TEXT PRIMARY KEY,
            name TEXT,
            category TEXT,
            effect TEXT,
            duration TEXT,
            recovery_test TEXT,
            source TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ref_edge_boosts (
            id TEXT PRIMARY KEY,
            name TEXT,
            cost INTEGER,
            timing TEXT,
            category TEXT,
            effect TEXT,
            source TEXT
        )
    """)
    conn.commit()


def populate_gameplay_tables(conn: sqlite3.Connection) -> Dict[str, int]:
    """Populates all three gameplay tables with official SR6 dataset rows."""
    init_gameplay_tables(conn)
    cursor = conn.cursor()
    counts = {"actions": 0, "status_effects": 0, "edge_boosts": 0}

    for act in ACTIONS_DATA:
        cursor.execute(
            """INSERT OR REPLACE INTO ref_actions 
               (id, name, action_type, category, test, opposed, threshold, description, source)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (act["id"], act["name"], act["action_type"], act["category"], act["test"],
             act["opposed"], act["threshold"], act["description"], act["source"])
        )
        counts["actions"] += 1

    for eff in STATUS_EFFECTS_DATA:
        cursor.execute(
            """INSERT OR REPLACE INTO ref_status_effects 
               (id, name, category, effect, duration, recovery_test, source)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (eff["id"], eff["name"], eff["category"], eff["effect"],
             eff["duration"], eff["recovery_test"], eff["source"])
        )
        counts["status_effects"] += 1

    for eb in EDGE_BOOSTS_DATA:
        cursor.execute(
            """INSERT OR REPLACE INTO ref_edge_boosts 
               (id, name, cost, timing, category, effect, source)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (eb["id"], eb["name"], eb["cost"], eb["timing"], eb["category"], eb["effect"], eb["source"])
        )
        counts["edge_boosts"] += 1

    conn.commit()
    return counts
