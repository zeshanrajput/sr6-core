"""
Rules Computation & Resolution Engine for SR6.
Bridges SQLite RulesDB, frontmatter parsing, namespace scoping, and rules resolution.
Exposes high-level Markdown table renderers for Quarto rules chapters and dossiers.
"""

import os
import re
import json
import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Optional, Set

from sr6core.rules_db import RulesDB, DEFAULT_DB_PATH
from sr6core.character_manager import CharacterManager
from sr6core.modifiers import ModifierEngine
from sr6core.vehicles import parse_vehicle_modifications, calculate_drone_action_pools, format_vehicle_mod_tables


def normalize_name(name: str) -> str:
    """Normalizes string for fuzzy rule lookup (lowercase, stripped punctuation)."""
    if not name:
        return ""
    return re.sub(r'[^a-z0-9]', '', str(name).lower())


class RulesEngine:
    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db = RulesDB(db_path=db_path)

    def search_rules(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        return self.db.search_rules(query, limit=limit)

    def get_rule(self, rule_id: str) -> Optional[Dict[str, Any]]:
        return self.db.query_rule(rule_id)


CANONICAL_SUPPLEMENT_WEAPONS: Dict[str, Dict[str, Any]] = {
    "red_fox": {
        "id": "red_fox",
        "name": "rEVOlution Arms Red Fox",
        "category": "Energy Weapons",
        "dv": "6P",
        "ar": [14, 16, 16, 9, None],
        "mode": "SA/BF",
        "ammo": "30(c)",
        "source": "Firing Squad p. 116"
    },
    "crimson_wasp": {
        "id": "crimson_wasp",
        "name": "rEVOlution Arms Crimson Wasp",
        "category": "Energy Weapons",
        "dv": "5P",
        "ar": [16, 14, 11, 6, None],
        "mode": "SA",
        "ammo": "15(c)",
        "source": "Firing Squad p. 116"
    }
}


def get_weapon_stats(item_id: str, db_path: str = DEFAULT_DB_PATH) -> Optional[Dict[str, Any]]:
    """
    Queries rules_index.db for weapon combat stats.
    Returns dictionary with id, name, dv, ar (list of int/None), mode, ammo, source.
    """
    import xml.etree.ElementTree as ET
    search_term = item_id.lower().replace("_", " ")
    row = None
    try:
        db = RulesDB(db_path=db_path)
        cursor = db.conn.cursor()

        row = cursor.execute(
            """SELECT id, name, category, damage, ap, attack_rating, modes, ammo, cost, source, raw_xml 
               FROM ref_weapons 
               WHERE id = ? OR lower(id) = ? OR lower(name) = ? OR lower(name) LIKE ?""",
            (item_id, item_id.lower(), item_id.lower(), f"%{search_term}%")
        ).fetchone()

        if not row:
            row = cursor.execute(
                """SELECT id, name, category, source, raw_xml FROM ref_gear 
                   WHERE id = ? OR lower(id) = ? OR lower(name) = ? OR lower(name) LIKE ?""",
                (item_id, item_id.lower(), item_id.lower(), f"%{search_term}%")
            ).fetchone()
    except Exception:
        row = None

    if not row:
        for k, v in CANONICAL_SUPPLEMENT_WEAPONS.items():
            if item_id.lower() in [k, v["name"].lower()] or search_term in v["name"].lower():
                return dict(v)
        return None

    w_id = row["id"]
    name = row["name"]
    category = row["category"]
    source = row["source"]
    raw_xml = row["raw_xml"]

    dmg = row["damage"] if "damage" in row.keys() and row["damage"] and row["damage"] != "-" else "0P"
    mode = row["modes"] if "modes" in row.keys() and row["modes"] and row["modes"] != "-" else "SS"
    ammo = row["ammo"] if "ammo" in row.keys() and row["ammo"] and row["ammo"] != "-" else "—"

    attack_list = []
    if "attack_rating" in row.keys() and row["attack_rating"] and row["attack_rating"] != "-":
        for p in str(row["attack_rating"]).replace("–", "-").split("/"):
            attack_list.append(int(p.strip()) if p.strip().isdigit() else None)

    if raw_xml and (dmg in ["0P", "-", "—", ""] or not attack_list):
        try:
            root = ET.fromstring(raw_xml)
            weapon_node = root.find(".//weapon")
            if weapon_node is None:
                weapon_node = root.find(".//firearm")
            if weapon_node is not None:
                if dmg in ["0P", "-", "—", ""]:
                    dmg = weapon_node.get("dmg", weapon_node.get("damage", "0P"))
                attack_raw = weapon_node.get("attack", weapon_node.get("ar", ""))
                if attack_raw and not attack_list:
                    for p in attack_raw.rstrip(",").split(","):
                        attack_list.append(int(p) if p.isdigit() else None)
                if mode in ["SS", "-", ""]:
                    mode = weapon_node.get("mode", weapon_node.get("modes", "SS"))
                if ammo in ["—", "-", ""]:
                    ammo = weapon_node.get("ammo", "—")
        except Exception:
            pass

    return {
        "id": w_id,
        "name": name,
        "category": category,
        "source": source.replace("_", " ").title().replace(" P.", " p.") if source else "SR6 Core",
        "dv": dmg,
        "ar": attack_list,
        "mode": mode,
        "ammo": ammo
    }


def render_weapon_card(item_id: str, db_path: str = DEFAULT_DB_PATH) -> str:
    """
    Queries rules_index.db for weapon combat stats and renders an HTML callout box.
    Ignores purchase attributes (cost/avail) and displays combat stats & source.
    """
    w = get_weapon_stats(item_id, db_path=db_path)
    if not w:
        return f"*(Weapon '{item_id}' not found in database)*"

    ar_str = " / ".join([str(x) if x is not None else "—" for x in w["ar"]]) if w["ar"] else "—"

    callout = (
        f'::: {{.callout-note icon=false title="{w["name"]} [{w["category"].upper()}]"}}\n'
        f'**Combat Stats**: **ID**: `{w["id"]}` | **DV**: {w["dv"]} | **AR**: {ar_str} | **Mode**: {w["mode"]} | **Ammo**: {w["ammo"]}  \n'
        f'**Citation**: *{w["source"]}*\n'
        f':::\n'
    )
    return callout


def render_rule_card(rule_id: str, db_path: str = DEFAULT_DB_PATH) -> str:
    """
    Queries rules_index.db for a rules vault entry by ID or topic (e.g. 'KK-0044')
    and renders an HTML callout box with its content and citation.
    """
    db = RulesDB(db_path=db_path)
    rule = db.query_rule(rule_id)
    if not rule:
        matches = db.search_rules(rule_id, limit=1)
        if matches:
            rule = matches[0]

    if not rule:
        return f"*(Rule '{rule_id}' not found in Rules Vault)*"

    topic = rule.get("topic", rule_id)
    source = rule.get("source", "SR6 Core")
    page = rule.get("page", "N/A")
    raw_content = rule.get("content", "")

    # Strip YAML frontmatter if present
    content_body = raw_content
    if content_body.startswith("---"):
        end_idx = content_body.find("---", 3)
        if end_idx != -1:
            content_body = content_body[end_idx + 3:].strip()

    # Remove H2 header title if redundant
    content_body = re.sub(r"^##\s+.*\n+", "", content_body).strip()

    callout = (
        f'::: {{.callout-note icon=false title="{topic}"}}\n'
        f'{content_body}\n\n'
        f'**Citation**: *{source}* (p. {page})\n'
        f':::\n'
    )
    return callout


# ============================================================================
# High-Level Quarto Chapter Table Renderers & Character Bridges
# ============================================================================

def get_drone_statblock_table(char_id: str, drone_identifier: str) -> str:
    """Renders a Markdown stat block table for a vehicle/drone with all applied modification math."""
    cm = CharacterManager()
    char = cm.load_character(char_id)
    if not char:
        return f"*(Character '{char_id}' not found)*"

    data = char["data"]
    drones = data.get("drones", []) + data.get("vehicles", [])
    target_drone = None
    for d in drones:
        if isinstance(d, dict):
            name = d.get("name", "").lower()
            ref = d.get("ref", "").lower()
            if drone_identifier.lower() in name or drone_identifier.lower() in ref:
                target_drone = d
                break

    if not target_drone:
        return f"*(Drone '{drone_identifier}' not found in character dossier)*"

    profile = parse_vehicle_modifications(target_drone, char_data=data)
    
    rows = [
        "| SR6 Attribute | Rating / Value | Applied Modifiers Math & Notes |",
        "| :--- | :---: | :--- |",
        f"| **Handling (HND)** | **{profile['handling_str']}** | On/Off-Road Ground Handling / Rotor Assembly |",
        f"| **Acceleration (ACC)** | **{profile['accel_str']}** | On/Off-Road Acceleration / Rotor Assembly |",
        f"| **Top Speed (SPD) / Interval** | **{profile['speed_str']}** | Top Speed & Interval |",
        f"| **Body (BOD)** | **{profile['augmented_body']} ({profile['inhabited_body']})** | Base {profile['base_body']} + Modifications | Inhabited (+1 Tuning) |",
        f"| **Armor (ARM)** | **{profile['augmented_armor']}** | Base {profile['base_armor']} + Armor Increase / Ballistics Suite |",
        f"| **Pilot (PLT)** | **{profile['pilot_str']}** | Base {profile['base_pilot']} | Override when inhabited |",
        f"| **Sensor (SEN)** | **{profile['augmented_sensor']}** | Base {profile['base_sensor']} + Enhanced Sensors + Sensor Upgrade |"
    ]
    if profile.get("mobility_str"):
        rows.append(f"| **Propulsion Modes** | **{profile['mobility_str']}** | Secondary & Special Propulsion Profiles |")
    attr_table = "\n".join(rows)

    drone_name = target_drone.get("name", "Drone")
    mod_tables = format_vehicle_mod_tables(profile.get("mod_slots", {}), drone_name=drone_name)
    if mod_tables:
        return attr_table + "\n\n" + mod_tables
    return attr_table


def get_drone_action_table(char_id: str, drone_identifier: str = "butler", mode: str = "inhabited_override") -> str:
    """Renders a Markdown table of the 5 standardized drone action pools for a given mode."""
    cm = CharacterManager()
    char = cm.load_character(char_id)
    if not char:
        return f"*(Character '{char_id}' not found)*"

    data = char["data"]
    drones = data.get("drones", []) + data.get("vehicles", [])
    target_drone = None
    for d in drones:
        if isinstance(d, dict):
            name = d.get("name", "").lower()
            ref = d.get("ref", "").lower()
            if drone_identifier.lower() in name or drone_identifier.lower() in ref:
                target_drone = d
                break

    if not target_drone and drones:
        target_drone = drones[0]

    pools = calculate_drone_action_pools(data, target_drone or {}, mode=mode)
    
    rows = [
        "| Drone Action / Test | Base Skill & Attributes | Applied Modifiers Math | Final Dice Pool |",
        "| :--- | :---: | :--- | :---: |",
        f"| **Drone Piloting / Maneuvering** | Maneuvering + Pilot | {pools['piloting']['breakdown']} | **{pools['piloting']['pool']}d6** |",
        f"| **Drone Weapon Attack (Gunnery)** | Targeting + Sensor/DP | {pools['gunnery']['breakdown']} | **{pools['gunnery']['pool']}d6** |",
        f"| **Drone Evasion (Defense Test)** | Evasion + Pilot/Sleaze | {pools['evasion']['breakdown']} | **{pools['evasion']['pool']}d6** |",
        f"| **Drone Perception Test** | Clearsight + Sensor | {pools['perception']['breakdown']} | **{pools['perception']['pool']}d6** |",
        f"| **Drone Stealth Test** | Stealth + Pilot/DP | {pools['stealth']['breakdown']} | **{pools['stealth']['pool']}d6** |"
    ]
    return "\n".join(rows)


def get_matrix_action_table(char_id: str) -> str:
    """
    Renders a Markdown table of standardized Matrix Action Pools with transparent
    SRMG component breakdowns, applied modifiers math, total dice pools, and bought hits.
    """
    cm = CharacterManager()
    char = cm.load_character(char_id)
    if not char:
        return f"*(Character '{char_id}' not found)*"

    data = char["data"]
    pools = ModifierEngine.get_matrix_action_pools(data)

    rows = [
        "| Action Category / Test | Base Stat + Skill | Applied Modifiers Math | Final Dice Pool | Bought Hits |",
        "| :--- | :---: | :--- | :---: | :---: |"
    ]

    for key, opt in pools.items():
        name_str = f"**{opt.name}**"
        if opt.notes:
            name_str += f"<br>*{opt.notes}*"

        wild_str = f" ({opt.wild_dice} wild)" if opt.wild_dice else ""
        pool_str = f"**{opt.total_pool}d6**{wild_str}"
        hits_str = f"**{opt.bought_hits} Hits**"

        rows.append(
            f"| {name_str} | {opt.get_base_stat_skill_string()} | {opt.get_modifiers_breakdown_string()} | {pool_str} | {hits_str} |"
        )

    return "\n".join(rows)


def get_magic_action_table(char_id: str) -> str:
    """
    Renders a Markdown table of standardized Magic Action Pools with transparent
    SRMG component breakdowns, applied modifiers math, total dice pools, and bought hits.
    """
    cm = CharacterManager()
    char = cm.load_character(char_id)
    if not char:
        return f"*(Character '{char_id}' not found)*"

    data = char["data"]
    pools = ModifierEngine.get_magic_action_pools(data)

    rows = [
        "| Magic Action / Protocol | Base Stat + Skill | Applied Modifiers Math | Final Dice Pool | Bought Hits |",
        "| :--- | :---: | :--- | :---: | :---: |"
    ]

    for key, opt in pools.items():
        name_str = f"**{opt.name}**"
        if opt.notes:
            name_str += f"<br>*{opt.notes}*"

        wild_str = f" ({opt.wild_dice} wild)" if opt.wild_dice else ""
        pool_str = f"**{opt.total_pool}d6**{wild_str}"
        hits_str = f"**{opt.bought_hits} Hits**"

        rows.append(
            f"| {name_str} | {opt.get_base_stat_skill_string()} | {opt.get_modifiers_breakdown_string()} | {pool_str} | {hits_str} |"
        )

    return "\n".join(rows)


def get_sprite_action_table(char_id: str, sprite_level: int = 6) -> str:
    """
    Renders a Markdown table of standardized Technomancer Sprite Actions (Compiling, Registering,
    Decompiling, Resonance Focus [Data Structure per SRM], and Fading Resistance).
    """
    cm = CharacterManager()
    char = cm.load_character(char_id)
    if not char:
        return f"*(Character '{char_id}' not found)*"

    data = char["data"]
    attrs = data.get("attributes", {})
    res = attrs.get("resonance", 6)
    wil = attrs.get("willpower", 5)
    log_val = attrs.get("logic", 5)
    foci = data.get("synergies", {}).get("foci", [])
    focus_bonus = sum(f.get("rating", 0) for f in foci if f.get("applies_to") in ["resonance", "tasking", "all"])

    compile_pool = res + 6 + focus_bonus
    register_pool = res + 6 + focus_bonus
    fading_pool = wil + log_val

    rows = [
        "| Sprite Protocol / Action | Test Parameters | Applied Modifiers Math | Final Dice Pool | Bought Hits |",
        "| :--- | :---: | :--- | :---: | :---: |",
        f"| **Compile Sprite (L{sprite_level})** | Tasking (Compiling) + Resonance | Base RES ({res}) + Tasking (6) + Focus (+{focus_bonus}) | **{compile_pool}d6** | **{compile_pool // 4} Hits** |",
        f"| **Register Sprite (L{sprite_level})** | Tasking (Registering) + Resonance | Base RES ({res}) + Tasking (6) + Focus (+{focus_bonus}) | **{register_pool}d6** | **{register_pool // 4} Hits** |",
        f"| **Resonance Focus (Data Structure)** | Passive (SRM: No Action) | Rating (+{focus_bonus} to Resonance Tests; 0 Fading) | **+{focus_bonus}d6** | **+{focus_bonus // 4} Hits** |",
        f"| **Fading Resistance Test** | WIL ({wil}) + LOG ({log_val}) | Natural Drain/Fading Soak | **{fading_pool}d6** | **{fading_pool // 4} Hits** |"
    ]
    return "\n".join(rows)


def get_social_action_table(char_id: str) -> str:
    """
    Renders a Markdown table of standardized Social / Face Action Pools with transparent
    SRMG component breakdowns, applied modifiers math, total dice pools, and bought hits.
    """
    cm = CharacterManager()
    char = cm.load_character(char_id)
    if not char:
        return f"*(Character '{char_id}' not found)*"

    data = char["data"]
    pools = ModifierEngine.get_social_action_pools(data)

    rows = [
        "| Social Action / Protocol | Base Stat + Skill | Applied Modifiers Math | Final Dice Pool | Bought Hits |",
        "| :--- | :---: | :--- | :---: | :---: |"
    ]

    for key, opt in pools.items():
        name_str = f"**{opt.name}**"
        if opt.notes:
            name_str += f"<br>*{opt.notes}*"

        wild_str = f" ({opt.wild_dice} wild)" if opt.wild_dice else ""
        pool_str = f"**{opt.total_pool}d6**{wild_str}"
        hits_str = f"**{opt.bought_hits} Hits**"

        rows.append(
            f"| {name_str} | {opt.get_base_stat_skill_string()} | {opt.get_modifiers_breakdown_string()} | {pool_str} | {hits_str} |"
        )

    return "\n".join(rows)


def get_tactical_action_table(char_id: str, scene_mode: str = "baseline") -> str:
    """
    Renders a Markdown table of standardized Physical & Tactical Combat Action Pools
    with transparent SRMG component breakdowns, applied modifiers math, total dice pools, and bought hits.
    """
    cm = CharacterManager()
    char = cm.load_character(char_id)
    if not char:
        return f"*(Character '{char_id}' not found)*"

    data = char["data"]
    pools = ModifierEngine.get_tactical_action_pools(data, scene_mode=scene_mode)

    rows = [
        "| Tactical Action / Combat Test | Base Stat + Skill | Applied Modifiers Math | Final Dice Pool | Bought Hits |",
        "| :--- | :---: | :--- | :---: | :---: |"
    ]

    for key, opt in pools.items():
        name_str = f"**{opt.name}**"
        if opt.notes:
            name_str += f"<br>*{opt.notes}*"

        wild_str = f" ({opt.wild_dice} wild)" if opt.wild_dice else ""
        pool_str = f"**{opt.total_pool}d6**{wild_str}"
        hits_str = f"**{opt.bought_hits} Hits**"

        rows.append(
            f"| {name_str} | {opt.get_base_stat_skill_string()} | {opt.get_modifiers_breakdown_string()} | {pool_str} | {hits_str} |"
        )

    return "\n".join(rows)


def get_monad_strategy_table(char_id: str = "venn") -> str:
    """
    Renders a unified strategy table comparing Meatspace Baseline, Close Combat / Parkour,
    Living Persona Matrix Mode, and Monad Boost / Cyberware Overdrive configurations.
    """
    rows = [
        "| Operational Mode | Active Augmentations & State | Effective Attributes | Primary Action Pools & Modifiers | Derived Defenses & Hits |",
        "| :--- | :--- | :--- | :--- | :--- |",
        "| **1. Meatspace Baseline (Chrome Active, Wireless ON)** | 4 Synthetic Cyberlimbs (AGI+3 enhancements)<br>Redliner (+2 AGI, +2 STR to limbs)<br>Used Skillwires R6 (Wireless ON: +1)<br>Used Skilljack R6<br>Dual Nanohives R3 (6 Active NV Bioamplifiers) | **AGI 7** *(Cyberarms/legs)*<br>**STR 4** *(Cyberarms/legs)*<br>BOD 5, REA 2, LOG 6, INT 5<br>**WIL 8** *(Bio-Response Override)*<br>**CHA 3** *(Neurochem Regulator)* | **Close Combat (Unarmed)**: **15d6** (3 Hits, **5P DV**) *(Activesoft 6 + AGI 7 + Wires 1 + Neural Pattern 1; Bone Density 4P + Neuromuscular Amp +1P)*<br>**Cracking (Matrix Attack)**: **14d6** (3 Hits) *(Activesoft 6 + LOG 6 + Wires 1 + Neocortical Amp 1)*<br>**Electronics (Computer)**: **13d6** (3 Hits, 15d6 Computer) *(Electronics 6 + LOG 6 + Neocortical Amp 1)*<br>**Athletics**: **9d6** (2 Hits) *(Athletics 1 + AGI 7 + Neural Pattern 1)* | **Physical Defense**: **7d6** (1 Hit) *(REA 2 + INT 5)*<br>**Damage Soak**: **9d6** (2 Hits) *(BOD 5 + Bone Density R4)*<br>**Defense Rating**: **6 DR** (SkinShield w/ Hood)<br>**Physical Initiative**: **7 + 1D6**<br>**Condition Monitors**: 11 Phys / 13 Stun (+1 Stun Box via Bio-Response Override) |",
        "| **2. Cyberlimb Overdrive & Leaping Assault** | Overdriving Cyberlimbs (+2 AGI / +2 STR with 1 wild die)<br>Retractable Inline Skates + Gecko Tips / Tape Gloves<br>Generates +1 Edge via *Maximum Overdrive* | **AGI 9** *(Overdriven)*<br>**STR 6** *(Overdriven)*<br>WIL 8 | **Close Combat (Flying Kick Engine)**: **17d6** (4 Hits) *(Base 5P + 1 Iron Limbs + 3 Flying Kick = **9P Base DV**, surging to **10P Base DV** with Toughskin Spines)*<br>**Wall Running / Parkour**: **11d6** *(Athletics + Gecko Tips/Gloves)* | **High-Speed Glide**: 10m/rnd Sprint<br>**Flying Kick Threshold**: 1 hit (via Parkour/Athletics)<br>**Falling Absorption**: 4 boxes absorbed |",
        "| **3. Matrix Living Persona (Veronica Co-Processing)** | Monad Living Persona (Whisper Nets: **A:3 S:6 D:7 F:10**)<br>NV 6 Allocated: +2 FW, +1 DP, +1 Sleaze<br>Hot-Sim VR Matrix Inhabitation | LOG 6<br>INT 5<br>WIL 8<br>CHA 3 | **Offensive Cracking**: **14d6** (3 Hits) *(Activesoft 6 + LOG 6 + Wires 1 + Neocortical Amp 1)*<br>**Electronics (Computer)**: **13d6** (3 Hits, 15d6 Computer)<br>**Matrix Perception**: **11d6** (2 Hits)<br>**Full Matrix Defense**: **18d6** (4 Hits) *(WIL 8 + FW 10)* | **Full Matrix Defense**: **18d6** (4 Hits)<br>**Matrix Initiative**: **12 + 3D6 (Hot-Sim VR)**<br>**Matrix Soak**: **10d6** (Firewall 10) |",
        "| **4. Monad Physical Attribute Boost** | **Monad NV Boost**: Minor Action, NV test (6 dice). Rolling $\\ge 3$ hits adds **+4 Minor Actions** for duration.<br>With 4-Edge boost rolls 13 exploding dice. | **AGI 7–9**<br>**STR 4–6**<br>NV 6 | **Turn 1 Action Economy**: Converts to **3 Major Actions and 1 Minor Action** per combat round!<br>**Rapid Cellular Healing**: NV test reduces damage boxes | **Exhaustion Risk**: After boost ends, NV temporarily decreases by total boost for 1 minute.<br>**Adrenal Control**: WIL + NV (2) test (14d6) to remain conscious when monitors are full |"
    ]
    return "\n".join(rows)


def get_weapon_attack_table(char_id: str) -> str:
    """
    Renders a Markdown table of standardized weapon attack profiles,
    firing mode options, final effective Attack Ratings (AR), and weapon notes.
    """
    cm = CharacterManager()
    char = cm.load_character(char_id)
    if not char:
        return f"*(Character '{char_id}' not found)*"

    data = char["data"]
    weapons_sec = data.get("weapons", {})
    ranged_list = weapons_sec.get("ranged", []) if isinstance(weapons_sec, dict) else []
    melee_list = weapons_sec.get("close_combat", []) if isinstance(weapons_sec, dict) else []
    
    if isinstance(weapons_sec, list):
        flat_list = weapons_sec
    else:
        flat_list = ranged_list + melee_list

    def format_ar_array(base_ar: list, ar_bonus: int = 0, burst_pen: int = 0, grip_cn_bonus: int = 0) -> str:
        out = []
        for i in range(5):
            val = base_ar[i] if i < len(base_ar) and base_ar[i] is not None else None
            if val is not None and val > 0:
                cn_extra = grip_cn_bonus if i in [0, 1] else 0
                calc = max(0, val + ar_bonus + cn_extra - burst_pen)
                out.append(str(calc))
            else:
                out.append("—")
        return " / ".join(out)

    rows = [
        "| Weapon Name | Mode (Rounds) | Final DV | Final Effective AR (C / N / M / F / E) | Notes & Constraints |",
        "| :--- | :---: | :---: | :---: | :--- |"
    ]

    if char_id.lower() in ["reiko", "yuriko"]:
        # Reiko / Yuriko uses drone-mounted weapon systems
        def format_ar(base_ar: list, ar_bonus: int, burst_pen: int = 0, grip_cn_bonus: int = 0) -> str:
            out = []
            for i in range(5):
                val = base_ar[i] if i < len(base_ar) and base_ar[i] is not None else None
                if val is not None:
                    cn_extra = grip_cn_bonus if i in [0, 1] else 0
                    out.append(str(val + ar_bonus + cn_extra - burst_pen))
                else:
                    out.append("—")
            return " / ".join(out)

        # 1. Red Fox Array (2x Link-Fired - Eye Mounts)
        fox_stat = get_weapon_stats("red_fox") or {"dv": "6P", "ar": [14, 16, 16, 9]}
        fox_base_dv = int(re.sub(r"[^\d]", "", fox_stat["dv"])) if re.search(r"\d", fox_stat["dv"]) else 6
        # Link-fired: Base + 1 link-fired + 3 smartlink + 2 mount = +6 AR, +2 DV
        fox_link_ss_ar = format_ar(fox_stat["ar"], ar_bonus=6, burst_pen=0)
        fox_link_sa_ar = format_ar(fox_stat["ar"], ar_bonus=6, burst_pen=1)
        fox_link_bf_ar = format_ar(fox_stat["ar"], ar_bonus=6, burst_pen=2)
        rows.append(f"| **Red Fox Array (2x Link-Fired)** | **SS** (1/gun) | {fox_base_dv + 2}P* | **{fox_link_ss_ar}** | Link-fired 2x Red Foxes in Eye Mounts (Costs Minor Action; +2 DV, +1 AR). **1 round/gun** (2 rds total). 1 Wild Die. *Decreases by 3P at Medium. |")
        rows.append(f"| | **SA** (2/gun) | {fox_base_dv + 3}P* | **{fox_link_sa_ar}** | Link-fired array (Drone mount halves SA penalty). **2 rounds/gun** (4 rds total). *Decreases by 3P at Medium. |")
        rows.append(f"| | **BF** (4/gun) | {fox_base_dv + 4}P* | **{fox_link_bf_ar}** | Link-fired array (Drone mount halves BF penalty). **4 rounds/gun** (8 rds total). *Decreases by 3P at Medium. |")

        # 1b. Single Red Fox (Independent - Eye Mount)
        fox_single_ss_ar = format_ar(fox_stat["ar"], ar_bonus=5, burst_pen=0)
        fox_single_sa_ar = format_ar(fox_stat["ar"], ar_bonus=5, burst_pen=1)
        fox_single_bf_ar = format_ar(fox_stat["ar"], ar_bonus=5, burst_pen=2)
        rows.append(f"| **Single Red Fox (Independent)** | **SS** (1) | {fox_base_dv}P* | **{fox_single_ss_ar}** | Independent Eye Mount (NO Minor Action required). **1 round**. 1 Wild Die. *Decreases by 3P at Medium. |")
        rows.append(f"| | **SA** (2) | {fox_base_dv + 1}P* | **{fox_single_sa_ar}** | Independent mount (Drone mount halves SA penalty). **2 rounds**. *Decreases by 3P at Medium. |")
        rows.append(f"| | **BF** (4) | {fox_base_dv + 2}P* | **{fox_single_bf_ar}** | Independent mount (Drone mount halves BF penalty). **4 rounds**. *Decreases by 3P at Medium. |")

        # 2. Tesla Coil
        rows.append("| **Tesla Coil (MAA Cyberarm)** | **SS** (1) | 5S(e) | **10 / 12* / — / — / —** | Max 20m, 20m Cone Area Attack (Flamethrower rules), Cyberarm Mount (+2 AR). |")

        # 3. Amalgam Cestas
        rows.append("| **Amalgam Cestas (Man-at-Arms - Phys)** | **Melee** | 3P | **12 / — / — / — / —** | Personalized Grip +2 AR. Overrides Immunity to Normal Weapons. 1 Wild Die. |")
        return "\n".join(rows)

    if flat_list:
        for w in flat_list:
            if not isinstance(w, dict):
                continue
            w_name = w.get("name", "Unknown Weapon")
            w_modes = str(w.get("modes", "SA")).split("/")
            w_dv = str(w.get("damage", "3P"))
            w_notes = w.get("notes", "")
            raw_ar = w.get("attack_rating", "")
            if isinstance(raw_ar, list):
                base_ar = raw_ar
            elif isinstance(raw_ar, str):
                base_ar = [int(p.strip()) if p.strip().isdigit() else 0 for p in raw_ar.replace("–", "-").split("/")]
            else:
                base_ar = [10, 10, 8, 0, 0]

            m = re.match(r"^(\d+)([A-Za-z]+.*)$", w_dv)
            base_dmg_num = int(m.group(1)) if m else 3
            dmg_type = m.group(2) if m else "P"

            first_mode = True
            for mode in w_modes:
                mode_clean = mode.strip().upper()
                name_cell = f"**{w_name}**" if first_mode else ""
                
                if mode_clean == "MELEE":
                    ar_str = format_ar_array(base_ar)
                    rows.append(f"| {name_cell} | **Melee** | {w_dv} | **{ar_str}** | {w_notes if first_mode else ''} |")
                elif mode_clean == "SS":
                    ar_str = format_ar_array(base_ar)
                    ss_notes = w_notes if first_mode else "Single shot mode."
                    rows.append(f"| {name_cell} | **SS** (1) | {base_dmg_num - (1 if 'SA' in w_modes else 0)}{dmg_type} | **{ar_str if not 'SA' in w_modes else format_ar_array([x + 2 if x > 0 else 0 for x in base_ar])}** | {ss_notes} |")
                elif mode_clean == "SA":
                    has_shock_pad = "shock pad" in str(w.get("accessories", [])).lower() or "shock pad" in w_notes.lower()
                    ar_str = format_ar_array(base_ar)
                    sa_notes = w_notes if first_mode else ("2-round semi-auto burst." if not has_shock_pad else "2-round narrow burst.")
                    rows.append(f"| {name_cell} | **SA** (2) | {w_dv} | **{ar_str}** | {sa_notes} |")
                elif mode_clean == "BF":
                    has_shock_pad = "shock pad" in str(w.get("accessories", [])).lower() or "shock pad" in w_notes.lower()
                    pen = 2 if has_shock_pad else 4
                    bf_ar = format_ar_array([max(0, x - pen) if x > 0 else 0 for x in base_ar])
                    rows.append(f"| {name_cell} | **BF** (4) | {base_dmg_num + 1}{dmg_type} | **{bf_ar}** | 4-round narrow burst. Shock pad halves recoil penalty. |")
                elif mode_clean == "FA":
                    has_shock_pad = "shock pad" in str(w.get("accessories", [])).lower() or "shock pad" in w_notes.lower()
                    pen = 4 if has_shock_pad else 6
                    fa_ar = format_ar_array([max(0, x - pen) if x > 0 else 0 for x in base_ar])
                    rows.append(f"| {name_cell} | **FA** (10) | {base_dmg_num + 2}{dmg_type} | **{fa_ar}** | 10-round full auto burst. |")
                first_mode = False
        return "\n".join(rows)

    return "\n".join(rows)


def get_sprite_commands_table(char_id: str = "reiko", sprite_level: int = 6) -> str:
    """
    Renders a Markdown table detailing the 6 standard Technomancer Sprite Commands
    (Signal Boost, Host Ken, Hyperthreading, File Ken, Cybercombat Boost, Device Ken)
    and their mechanical rules.
    """
    dv_boost = (sprite_level + 1) // 2
    rows = [
        "| Sprite Command | Task / Action Type | Mechanical Effect & Modifiers | Rules & Usage Constraints |",
        "| :--- | :--- | :--- | :--- |",
        f"| **Signal Boost** | Simple Action | Reduces Noise by **{sprite_level}** across all active PAN channels. | Sustained while sprite remains on Matrix overwatch. |",
        f"| **Host Ken** | Simple Action | Grants Teamwork bonus (Rating {sprite_level}) on Host navigation and Matrix Perception. | Teamwork rules apply. Max bonus capped at Technomancer skill rating. |",
        f"| **Hyperthreading** | Complex Action | Compiles task routines to reduce Fading Value of sustained Complex Forms by 1. | Requires active Resonance bond. |",
        f"| **File Ken** | Simple Action | Teamwork assistance on Matrix Search and Decryption tests (Level {sprite_level}). | Teamwork rules apply. |",
        f"| **Cybercombat Boost** | Free Action | Adds **+{dv_boost} Matrix DV** on successful Cybercombat and Brute Force attacks. | Applies to next attack test. |",
        f"| **Device Ken** | Simple Action | Teamwork assistance on Control Device and Hardware tests (Level {sprite_level}). | Teamwork rules apply. |"
    ]
    return "\n".join(rows)


def get_scene_strategy_table(char_id: str = "velvet") -> str:
    """
    Renders a unified multi-mode strategy table for character scene profiles,
    including universal sustained anchor spells, channeled spirits, and scene-calibrated pools.
    """
    cm = CharacterManager()
    char = cm.load_character(char_id)
    if not char:
        if char_id.lower() == "venn":
            return get_monad_strategy_table(char_id)
        return f"*(Character '{char_id}' not found)*"

    data = char["data"]
    attrs = data.get("attributes", {})
    mag = int(attrs.get("magic", 0))

    # If the character is not a magician/mystic adept or has no magic, fallback to monad/tactical table
    if mag == 0:
        return get_monad_strategy_table(char_id)

    # Gather qualities, skills, modifiers
    qualities = data.get("qualities", {})
    pos_quals = qualities.get("positive", []) if isinstance(qualities, dict) else []
    fc_qual = next(
        (q for q in pos_quals if "focused_concentration" in str(q.get("ref", "")).lower() or "focused concentration" in str(q.get("name", "")).lower()),
        None
    )
    fc_rating = fc_qual.get("rating", 3) if fc_qual else 3

    skills = {s.get("name", "").lower(): s for s in data.get("skills", [])}
    sorcery_data = skills.get("sorcery", {})
    sorcery_rating = int(sorcery_data.get("rating", 0))
    sorcery_spec = 2 if sorcery_data.get("specialization") else 0
    power_focus_mods = ModifierEngine.get_focus_modifiers(data, "magic")
    power_focus = sum(m.value for m in power_focus_mods)

    casting_pool = sorcery_rating + sorcery_spec + mag + power_focus
    bought_hits = casting_pool // 4
    inc_attr_bonus = min(4, 1 + max(0, bought_hits - 1)) if bought_hits > 0 else 0

    cha = int(attrs.get("charisma", 0))
    wil = int(attrs.get("willpower", 0))
    log_val = int(attrs.get("logic", 0))
    int_val = int(attrs.get("intuition", 0))
    bod = int(attrs.get("body", 0))
    agi = int(attrs.get("agility", 0))
    rea = int(attrs.get("reaction", 0))
    str_val = int(attrs.get("strength", 0))

    # Universal Sustained Anchors (Slots 1 & 2): Charisma first, Willpower second
    cha_eff = cha + inc_attr_bonus
    wil_eff = wil + inc_attr_bonus

    drain_init = wil + cha
    drain_mid = wil + cha_eff
    drain_final = wil_eff + cha_eff

    # Channeled spirit mechanics (Street Wyrd p. 122): Force = Magic - 1
    # Any physical attribute with rank < Force increases by Force // 2 (max +4)
    # Magician ignores points of wound modifiers equal to spirit Force
    spirit_level = max(1, mag - 1)
    spirit_phys_bonus = spirit_level // 2
    bod_chan = bod + spirit_phys_bonus if bod < spirit_level else bod
    agi_chan = agi + spirit_phys_bonus if agi < spirit_level else agi
    rea_chan = rea + spirit_phys_bonus if rea < spirit_level else rea
    str_chan = str_val + spirit_phys_bonus if str_val < spirit_level else str_val

    # Check for learned spells
    spells = [s.get("name", "").lower() for s in data.get("spells", [])]
    has_charm = "charm" in spells

    # Skills for action pools
    inf_rating = int(skills.get("influence", {}).get("rating", 0))
    con_rating = int(skills.get("con", {}).get("rating", 0))

    def fmt_hits(pool: int) -> str:
        h = pool // 4
        return f"{h} {'Hit' if h == 1 else 'Hits'}"

    # Callout / protocol description
    protocol_callout = [
        "> **Deterministic Universal Buffing Protocol (Always Cast First & Second):**",
        "> ",
        f"> Velvet sustains up to **{fc_rating} spells simultaneously with 0 sustaining penalties** via **Focused Concentration (Rating {fc_rating})**, reaching the maximum **+4 SRMG Augmentation Cap** deterministically by buying hits.",
        "> ",
        f"> * **Deterministic Casting Pool**: Sorcery {sorcery_rating} + Spec {sorcery_spec} + Magic {mag} + Power Focus {power_focus} = **{casting_pool}d6** $\\rightarrow$ **{fmt_hits(casting_pool)}** (1 base + {bought_hits - 1} net hits = **+{inc_attr_bonus} attribute boost**).",
        f"> * **Universal Anchor 1 (Cast First)**: *Increase Attribute: Charisma (+{inc_attr_bonus})* $\\rightarrow$ Boosts Charisma from {cha} to **{cha_eff}**. Resisted by base Drain soak of **{drain_init}d6** ({fmt_hits(drain_init)} vs Drain 3) $\\rightarrow$ **0 Drain**.",
        f"> * **Universal Anchor 2 (Cast Second)**: *Increase Attribute: Willpower (+{inc_attr_bonus})* $\\rightarrow$ Boosts Willpower from {wil} to **{wil_eff}**. Resisted by upgraded Drain soak of **{drain_mid}d6** ({fmt_hits(drain_mid)} vs Drain 3) $\\rightarrow$ **0 Drain**.",
        f"> * **Peak Drain Soak**: With CHA **{cha_eff}** and WIL **{wil_eff}**, permanent Drain soak reaches **{drain_final}d6** ({fmt_hits(drain_final)}), completely absorbing all Drain from subsequent spells and spirit commands.",
        ""
    ]

    # Mode 1: Social & Legwork
    int_eff_social = int_val + inc_attr_bonus
    if has_charm:
        log_eff_social = log_val
        slot3_social = "**Charm** (+4 to Con & Influence tests)"
        inf_pool = inf_rating + cha_eff + 4
        con_pool = con_rating + cha_eff + 4
    else:
        log_eff_social = log_val + inc_attr_bonus
        slot3_social = f"**Increase Attribute: Logic (+{inc_attr_bonus})** *(Interim: boosts LOG to {log_eff_social} until Charm is learned)*"
        inf_pool = inf_rating + cha_eff
        con_pool = con_rating + cha_eff

    judge_intentions_social = int_eff_social + wil_eff
    composure_social = wil_eff + cha_eff
    memory_social = log_eff_social + wil_eff

    channeled_influence_base = mag + cha_eff
    channeled_influence_focus = mag + power_focus + cha_eff

    row1 = (
        f"| **1. Social & Legwork Mode** | "
        f"**Channeled Kindred Spirit (Level {spirit_level})**:<br>"
        f"* Physicals Bonus: **+{spirit_phys_bonus}** to BOD, AGI, REA, STR (Force/2)<br>"
        f"* Bonus Power: *Innate Spell (Increase Attribute: Intuition)* (+{inc_attr_bonus} INT)<br>"
        f"* Spirit Power: *Influence* (Channeled: MAG + CHA vs WIL+LOG)<br><br>"
        f"**Sustained Slot 3**:<br>* {slot3_social} | "
        f"**CHA {cha_eff}**, **WIL {wil_eff}**, **INT {int_eff_social}**, **LOG {log_eff_social}**<br>"
        f"BOD {bod_chan}, AGI {agi_chan}, REA {rea_chan}, STR {str_chan} | "
        f"**Influence (Skill)**: **{inf_pool}d6** ({fmt_hits(inf_pool)})<br>"
        f"**Con / Deception**: **{con_pool}d6** ({fmt_hits(con_pool)})<br>"
        f"**Channeled Influence Power**: **{channeled_influence_base}d6** ({fmt_hits(channeled_influence_base)}) *(MAG {mag} + CHA {cha_eff}{f' / {channeled_influence_focus}d6 w/ Focus' if power_focus else ''} vs WIL+LOG)*<br>"
        f"*(Cosmetic Control: -1 Edge on Con)* | "
        f"**Composure**: **{composure_social}d6** ({fmt_hits(composure_social)})<br>"
        f"**Judge Intentions**: **{judge_intentions_social}d6** ({fmt_hits(judge_intentions_social)})<br>"
        f"**Memory Test**: **{memory_social}d6** ({fmt_hits(memory_social)})<br>"
        f"**Drain Soak**: **{drain_final}d6** ({fmt_hits(drain_final)}) |"
    )

    # Mode 2: Tactical Combat (Kindred Spirit L5 with Psychokinesis, Sustained Slot 3: Increase Reflexes)
    refl_bonus = inc_attr_bonus
    rea_eff_combat = rea_chan + refl_bonus
    phys_def_combat = rea_eff_combat + int_val
    full_def_combat = phys_def_combat + wil_eff
    init_score_combat = rea_eff_combat + int_val
    init_dice_combat = 1 + (bought_hits // 2)

    psychokinesis_pool = mag + wil_eff
    psychokinesis_focus = mag + power_focus + wil_eff
    confusion_pool = mag + wil_eff
    confusion_focus = mag + power_focus + wil_eff

    row2 = (
        f"| **2. Tactical Combat Mode** | "
        f"**Channeled Kindred Spirit (Level {spirit_level})**:<br>"
        f"* Physicals Bonus: **+{spirit_phys_bonus}** to BOD, AGI, REA, STR (Force/2)<br>"
        f"* Bonus Power: *Psychokinesis* (Minor Action telekinetic manipulation)<br>"
        f"* Spirit Powers: *Influence*, *Confusion*, *Accident*, *Guard*, *Concealment*<br><br>"
        f"**Sustained Slot 3**:<br>* **Increase Reflexes** (+{refl_bonus} REA, +{bought_hits // 2}D6 Init) | "
        f"**CHA {cha_eff}**, **WIL {wil_eff}**, **REA {rea_eff_combat}**<br>"
        f"BOD {bod_chan}, AGI {agi_chan}, STR {str_chan}, INT {int_val}, LOG {log_val} | "
        f"**Channeled Influence Power**: **{channeled_influence_base}d6** ({fmt_hits(channeled_influence_base)}) *(MAG {mag} + CHA {cha_eff}{f' / {channeled_influence_focus}d6 w/ Focus' if power_focus else ''} vs WIL+LOG)*<br>"
        f"**Channeled Psychokinesis**: **{psychokinesis_pool}d6** ({fmt_hits(psychokinesis_pool)}) *(MAG {mag} + WIL {wil_eff}{f' / {psychokinesis_focus}d6 w/ Focus' if power_focus else ''}; STR/AGI = {psychokinesis_pool // 4})*<br>"
        f"**Channeled Confusion**: **{confusion_pool}d6** ({fmt_hits(confusion_pool)}) *(vs WIL+LOG; inflicts Dazed & Confused)*<br>"
        f"**Sorcery (Spellcasting)**: **{casting_pool}d6** ({fmt_hits(casting_pool)})<br>"
        f"*(Guard: Glitch immunity; Concealment: -{spirit_level} enemy perception; ignores {spirit_level} wound points)* | "
        f"**Physical Defense**: **{phys_def_combat}d6** ({fmt_hits(phys_def_combat)})<br>"
        f"**Full Defense**: **{full_def_combat}d6** ({fmt_hits(full_def_combat)})<br>"
        f"**Initiative**: **{init_score_combat} + {init_dice_combat}D6**<br>"
        f"**Damage Soak**: **{bod_chan}d6** *(+ Armor)*<br>"
        f"**Drain Soak**: **{drain_final}d6** ({fmt_hits(drain_final)}) |"
    )

    # Mode 3: Investigation & Technical Mode
    int_eff_invest = int_val + inc_attr_bonus
    elec_pool = spirit_level + log_val
    eng_pool = spirit_level + log_val
    judge_intentions_invest = int_eff_invest + wil_eff
    phys_def_invest = rea_chan + int_eff_invest
    full_def_invest = phys_def_invest + wil_eff

    row3 = (
        f"| **3. Investigation & Technical Mode** | "
        f"**Channeled Task Spirit (Level {spirit_level})**:<br>"
        f"* Physicals Bonus: **+{spirit_phys_bonus}** to BOD, AGI, REA, STR (Force/2)<br>"
        f"* Channeled Skills: *Electronics {spirit_level}*, *Engineering {spirit_level}*<br>"
        f"* Spirit Powers: *Search* ({spirit_level * 2}d6), *Psychokinesis*<br><br>"
        f"**Sustained Slot 3**:<br>* **Increase Attribute: Intuition (+{inc_attr_bonus})** | "
        f"**CHA {cha_eff}**, **WIL {wil_eff}**, **INT {int_eff_invest}**<br>"
        f"BOD {bod_chan}, AGI {agi_chan}, REA {rea_chan}, STR {str_chan}, LOG {log_val} | "
        f"**Channeled Electronics**: **{elec_pool}d6** ({fmt_hits(elec_pool)})<br>"
        f"**Channeled Engineering**: **{eng_pool}d6** ({fmt_hits(eng_pool)})<br>"
        f"**Perception / Assensing**: **{int_eff_invest}d6** ({fmt_hits(int_eff_invest)}; + Search {spirit_level * 2}d6)<br>"
        f"**Judge Intentions**: **{judge_intentions_invest}d6** ({fmt_hits(judge_intentions_invest)}) | "
        f"**Composure**: **{drain_final}d6** ({fmt_hits(drain_final)})<br>"
        f"**Physical Defense**: **{phys_def_invest}d6** ({fmt_hits(phys_def_invest)})<br>"
        f"**Full Defense**: **{full_def_invest}d6** ({fmt_hits(full_def_invest)})<br>"
        f"**Drain Soak**: **{drain_final}d6** ({fmt_hits(drain_final)}) |"
    )

    table_headers = [
        "| Operational Mode | Channeled Spirit & Sustained Slot 3 | Effective Attributes | Primary Action Pools & Modifiers | Derived Defenses & Hits |",
        "| :--- | :--- | :--- | :--- | :--- |",
        row1,
        row2,
        row3
    ]

    return "\n".join(protocol_callout + table_headers)


def get_character_table_pools(char_id: str) -> dict:
    """
    Detects domain relevance per archetype and returns active table pool metadata.
    """
    cm = CharacterManager()
    char = cm.load_character(char_id)
    if not char:
        return {}

    data = char["data"]
    attrs = data.get("attributes", {})
    res = int(attrs.get("resonance", 0))
    mag = int(attrs.get("magic", 0))
    drones = data.get("drones", [])

    domains = []
    if res > 0 or data.get("living_persona"):
        domains.extend(["matrix_operations", "resonance_emergence"])
    if drones:
        domains.append("rigging_and_drones")
    if mag > 0:
        domains.append("sorcery_and_magic")
    domains.append("tactical_combat")

    return {
        "char_id": char_id,
        "name": data.get("identity", {}).get("handle", char_id.title()),
        "active_domains": domains,
        "is_technomancer": res > 0,
        "is_magician": mag > 0,
        "has_drones": len(drones) > 0
    }


def get_matrix_protocols_summary(char_id: str = "reiko") -> Dict[str, Any]:
    """Returns summarized Matrix ASDF, full defense hits/pool, and active derived values."""
    cm = CharacterManager()
    char = cm.load_character(char_id)
    if not char:
        return {}
    data = char["data"]
    asdf = ModifierEngine.get_living_persona_asdf(data)
    full_def = ModifierEngine.get_full_matrix_defense(data)
    asdf_str = f"A:{asdf.get('attack', 7)} S:{asdf.get('sleaze', 9)} D:{asdf.get('data_processing', 7)} F:{asdf.get('firewall', 9)}"
    return {
        "asdf": asdf,
        "asdf_str": asdf_str,
        "full_defense_pool": full_def.get("pool", 34),
        "full_defense_hits": full_def.get("effective_hits", 8),
        "full_defense_breakdown": full_def.get("breakdown", "")
    }


def get_matrix_asdf_derivation_table(char_id: str = "reiko") -> str:
    """Renders a Markdown table showing the derivation of active Matrix ASDF attributes."""
    cm = CharacterManager()
    char = cm.load_character(char_id)
    if not char:
        return f"*(Character '{char_id}' not found)*"
    data = char["data"]
    identity = data.get("identity", {})
    mortype = str(identity.get("mortype", "")).lower()

    if "monad" in mortype or char_id == "venn":
        attrs = data.get("attributes", {})
        cha = int(attrs.get("charisma", 2))
        int_val = int(attrs.get("intuition", 5))
        log_val = int(attrs.get("logic", 6))
        wil = int(attrs.get("willpower", 7))
        rows = [
            "| Matrix Attribute | Base Attribute | Applied Nanite Bioamplifiers & NV | Active Rating |",
            "| :--- | :---: | :--- | :---: |",
            f"| **Attack (A)** | Charisma ({cha}) | Neurochemical Regulator (+1) | **{cha + 1}** |",
            f"| **Sleaze (S)** | Intuition ({int_val}) | Nanite Volume Sleaze (+1) | **{int_val + 1}** |",
            f"| **Data Processing (D)** | Logic ({log_val}) | Nanite Volume DP (+1) | **{log_val + 1}** |",
            f"| **Firewall (F)** | Willpower ({wil}) | Bio-Response (+1) + NV (+2) | **{wil + 3}** |"
        ]
        ar = (cha + 1) + (int_val + 1)
        dr = (log_val + 1) + (wil + 3)
        notes = [
            f"\n* **Matrix Attack Rating (AR = Attack + Sleaze)**: $\\mathbf{{{ar}}}$",
            f"* **Matrix Defense Rating (DR = Data Processing + Firewall)**: $\\mathbf{{{dr}}}$"
        ]
        return "\n".join(rows + notes)

    # Reiko / Emerged Technoshaman Living Persona Derivation
    # Point Buy: Attack 3, Sleaze 5, Data Processing 3, Firewall 5
    # Assassin Sprite Symbiosis: +3 / +2 / +1 / +0
    # Programs: Toolbox (+1 DP), Encryption (+1 FW)
    # Resonance Split (Resonance 8): Distributed (+1 / +2 / +2 / +3 = 8) to reach the +4 Augmented Limit on all 4 attributes
    # Final Active ASDF: 7 / 9 / 7 / 9 -> Attack Rating 16, Defense Rating 16
    rows = [
        "| Matrix Attribute | Base (Point Buy) | Sprite Symbiosis (Assassin) | Programs (Toolbox / Encryption) | Resonance Split (Res 8) | Total Buff (+4 Cap) | Active Rating |",
        "| :--- | :---: | :---: | :---: | :---: | :---: | :---: |",
        "| **Attack (A)** | 3 | +3 | — | +1 | **+4** | **7** |",
        "| **Sleaze (S)** | 5 | +2 | — | +2 | **+4** | **9** |",
        "| **Data Processing (D)** | 3 | +1 | +1 *(Toolbox)* | +2 | **+4** | **7** |",
        "| **Firewall (F)** | 5 | +0 | +1 *(Encryption)* | +3 | **+4** | **9** |"
    ]

    notes = [
        "\n* **Matrix Attack Rating (AR = Attack + Sleaze)**: $7 + 9 = \\mathbf{16}$",
        "* **Matrix Defense Rating (DR = Data Processing + Firewall)**: $7 + 9 = \\mathbf{16}$",
        "* **Augmentation Cap Enforcement**: Under SR6 AI and living persona rules (*Hack & Slash* pp. 116–120), Matrix attributes are subject to the standard **+4 Augmented Attribute Limit**. Reiko's 8 flexible Resonance points are distributed ($1 + 2 + 2 + 3 = 8$) to bring each attribute to exactly the +4 maximum buff ceiling."
    ]
    return "\n".join(rows + notes)



# ============================================================================
# Multi-Modifier Derived Interaction Engine
# ============================================================================

def get_multi_modifier_interactions(char_id: str, threshold: int = 2) -> List[Dict[str, Any]]:
    """
    Identifies all test pools, attributes, and derived statistics for a character that
    utilize more than `threshold` (default > 2) modifiers, collating their mechanics,
    stacking legality, and operational constraints for dynamic rules page generation.
    """
    from sr6core.exporters.mobile_json import export_mobile_json

    cm = CharacterManager()
    char = cm.load_character(char_id)
    if not char:
        return []

    data = char["data"]
    char_repo = cm.get_character_repo_dir(char_id)
    mob_data = export_mobile_json(data, char_repo_path=char_repo)
    declared_mods = data.get("modifiers", [])
    identity = mob_data.get("identity", {})
    attrs = data.get("attributes", {})

    results = []

    # 1. Evaluate Skills & Tests
    for s in mob_data.get("skills", []):
        s_name = s.get("name", "")
        buffs = s.get("buffs", [])
        linked_attr = s.get("attribute", "").lower()
        mods_list = []
        for b in buffs:
            mods_list.append({
                "source": b.get("source", "Modifier"),
                "value": b.get("value", 0),
                "type": b.get("type", "skill"),
                "notes": b.get("notes", "") or "Active modifier",
                "rule_anchor": b.get("rule_anchor", "")
            })

        # Check gear/qualities affecting logic skills
        if linked_attr == "logic":
            math_spu = next((m for m in declared_mods if m.get("id") == "math_spu"), None)
            if math_spu:
                mods_list.append({
                    "source": "Math SPU",
                    "value": "-1 Edge",
                    "type": "gear",
                    "notes": "Reduces Edge boost cost by 1 (min 1) on Logic-linked skills; overdrive reduces cost by 2 with +1 wild die",
                    "rule_anchor": "rules/rules_and_downtime.html#cyberware-overdrive"
                })

        # Close Combat special handling
        if s_name.lower().startswith("close combat"):
            bd = next((m for m in declared_mods if "bone_density" in m.get("id", "")), None)
            if bd:
                mods_list.append({
                    "source": "Bone Density Augmentation R4",
                    "value": "+4P DV",
                    "type": "augmentation",
                    "notes": "Replaces standard unarmed strike (1S) with 4P Physical DV, +4 soak dice",
                    "rule_anchor": "rules/rules_and_downtime.html#augmentation-stacking"
                })
            nm = next((m for m in declared_mods if "neuromuscular" in m.get("id", "")), None)
            if nm:
                mods_list.append({
                    "source": "Neuromuscular Amplifier Colony",
                    "value": "+1P DV",
                    "type": "augmentation",
                    "notes": "+1 DV to all melee and unarmed attacks (sustained by 2 NV in Nanohive)",
                    "rule_anchor": "rules/rules_and_downtime.html#monad-nanite-boosts"
                })
            mods_list.append({
                "source": "Flying Kick (Martial Art Maneuver)",
                "value": "+3P DV",
                "type": "technique",
                "notes": "Requires 1 Net Hit on Athletics/Parkour leap to add +3 DV (surges base unarmed to 8P-10P DV)",
                "rule_anchor": "rules/rules_and_downtime.html#tactical-combat"
            })

        # Social skills special handling (e.g. Velvet)
        if s_name.lower().startswith("influence") or s_name.lower().startswith("con"):
            adept_powers = data.get("adept_powers", [])
            kinesics = next((p for p in adept_powers if "kinesics" in p.get("name", "").lower()), None)
            if kinesics:
                mods_list.append({
                    "source": f"Kinesics (Rating {kinesics.get('rating', 3)})",
                    "value": f"+{kinesics.get('rating', 3)}",
                    "type": "adept power",
                    "notes": "Adept micro-expression control adds bonus dice to social defense and deception",
                    "rule_anchor": "rules_and_downtime.html#adept-powers"
                })
            voice_mod = next((p for p in adept_powers if "voice modulation" in p.get("name", "").lower()), None)
            if voice_mod:
                mods_list.append({
                    "source": "Voice Modulation",
                    "value": "+2",
                    "type": "adept power",
                    "notes": "Pitch and harmonic modulation adds +2 dice to verbal Influence and Con tests",
                    "rule_anchor": "rules_and_downtime.html#adept-powers"
                })

        if len(mods_list) > threshold:
            legality = "All active modifiers stack legally. "
            constraints = ""
            if any(m["type"] == "augmentation" for m in mods_list):
                legality += "Total augmentation bonuses remain within the SRMG +4 Augmentation Cap. "
            if any("Skillwires" in m["source"] for m in mods_list):
                constraints += "Requires Skillwires to be 'Wireless ON' to spend Edge on associated tests. "
            if any("Colony" in m["source"] or "Amplifier" in m["source"] for m in mods_list):
                constraints += "Colonies require dedicated internal Nanite Volume (NV) in the Nanohive to sustain. "
            if any("Math SPU" in m["source"] for m in mods_list):
                constraints += "Math SPU reduces Edge boost costs by 1 (min 1). "

            results.append({
                "category": "Skill & Action Pools",
                "name": s_name,
                "total_pool": f"{s.get('buffed_pool', s.get('pool', 0))}d6",
                "base_summary": s.get("breakdown_text") or s.get("breakdown") or f"{linked_attr.upper()} {attrs.get(linked_attr, 0)} + Skill {s.get('base_rating', 0)}",
                "modifiers": mods_list,
                "stacking_legality": legality.strip(),
                "operational_constraints": constraints.strip() or "Standard action test resolution.",
                "count": len(mods_list)
            })

    # 2. Living Persona & Matrix Defenses
    if identity.get("is_monad") or data.get("living_persona") or int(attrs.get("resonance", 0)) > 0:
        if identity.get("is_monad"):
            wil_val = int(attrs.get("willpower", 1))
            fw_mods = [
                {
                    "source": "Natural Willpower Base",
                    "value": str(wil_val),
                    "type": "attribute",
                    "notes": "Base biological willpower",
                    "rule_anchor": ""
                }
            ]
            # Check for bio-response override in declared_mods or nanotech
            bio = next((m for m in declared_mods if "bio-response" in m.get("id", "").lower() or "bio-response" in m.get("name", "").lower()), None)
            if bio:
                fw_mods.append({
                    "source": bio.get("name", "Bio-Response Override Colony"),
                    "value": "+1",
                    "type": "augmentation",
                    "notes": "Nanite sensory damping structures boost Willpower by +1",
                    "rule_anchor": "rules/rules_and_downtime.html#monad-nanite-boosts"
                })
            # Check for nanite volume / firewall emulation
            nv = identity.get("nanite_volume", 0)
            if nv or any("volume" in m.get("id", "").lower() for m in declared_mods):
                fw_mods.append({
                    "source": "Monad Nanite Volume Allocation",
                    "value": "+2",
                    "type": "monad ability",
                    "notes": "Emulates hardware firewall pathways via nanite volume allocation",
                    "rule_anchor": "rules/rules_and_downtime.html#monad-matrix-attributes"
                })
            # Full defense calculation
            fw_mods.append({
                "source": "Full Matrix Defense Action",
                "value": f"+WIL ({wil_val})",
                "type": "matrix defense",
                "notes": f"Adds augmented Willpower ({wil_val}) to Firewall for Full Matrix Defense",
                "rule_anchor": "rules/rules_and_downtime.html#tactical-combat"
            })
            if len(fw_mods) > threshold:
                results.append({
                    "category": "Matrix Defense & Living Persona",
                    "name": "Firewall & Full Matrix Defense",
                    "total_pool": f"FW {wil_val + 2} / {wil_val * 2 + 2}d6 Full Defense",
                    "base_summary": f"Base WIL {wil_val} + Nanite Boosts + Full Defense (+WIL {wil_val})",
                    "modifiers": fw_mods,
                    "stacking_legality": "Bio-Response Override (+1) operates well within the SRMG +4 Augmentation Cap. Monad NV allocation emulates unbrickable biological hardware architecture. Full Matrix Defense stacks augmented Willpower directly with Firewall.",
                    "operational_constraints": "Bio-Response Override requires 3 NV sustained by the cyberleg Nanohives. Degrades in 1 week without hive maintenance.",
                    "count": len(fw_mods)
                })
        elif int(attrs.get("resonance", 0)) > 0:
            cha_val = int(attrs.get("charisma", 1))
            int_val = int(attrs.get("intuition", 1))
            log_val = int(attrs.get("logic", 1))
            wil_val = int(attrs.get("willpower", 1))
            res_val = int(attrs.get("resonance", 1))

            asdf_mods = [
                {"source": "Base ASDF Array", "value": f"A:{cha_val} S:{int_val} D:{log_val} F:{wil_val}", "type": "base", "notes": "Living Persona base stats", "rule_anchor": ""},
                {"source": "Network Tuning / Symbiosis", "value": "+4 to all ASDF", "type": "technomancer synergy", "notes": "Living persona tuning adds +4 across all Matrix attributes", "rule_anchor": "rules_matrix.html"},
                {"source": "Taz Symbiosis", "value": "+4 Tasking", "type": "teamwork", "notes": "Companion sprite assistance adds +4 teamwork dice", "rule_anchor": "rules_sprites.html"},
                {"source": "Resonance Focus R4", "value": "+4 Focus", "type": "focus", "notes": "Applies +4 dice to Resonance-linked action tests", "rule_anchor": "rules_matrix.html"}
            ]
            if len(asdf_mods) > threshold:
                results.append({
                    "category": "Resonance & Living Persona",
                    "name": "Technomancer ASDF & Resonance Operations",
                    "total_pool": f"A:{cha_val + 4} S:{int_val + 4} D:{log_val + 4} F:{wil_val + 4} (Resonance {res_val} + Focus 4 = {res_val + 4}d6 Base)",
                    "base_summary": "Base ASDF + Network Tuning (+4) + Taz Symbiosis (+4) + Resonance Focus (+4)",
                    "modifiers": asdf_mods,
                    "stacking_legality": "Network Tuning provides +4 augmented Matrix attributes, respecting the SRMG +4 limit. Taz Symbiosis provides teamwork dice capped at skill rating. Focus bonus applies as an untyped magical tool bonus.",
                    "operational_constraints": "Sustaining complex forms requires Resonance bond. Taz must remain registered and in PAN proximity.",
                    "count": len(asdf_mods)
                })

    # 3. Damage Resistance & Armor
    bod = int(attrs.get("body", 1))
    bd_mod = next((m for m in declared_mods if any(k in m.get("id", "") or k in m.get("name", "").lower() for k in ["bone_density", "orthoskin", "dermal"])), None)
    if not bd_mod:
        for c in data.get("cyberware", []):
            if isinstance(c, dict) and any(k in c.get("name", "").lower() or k in c.get("ref", "").lower() for k in ["bone density", "orthoskin", "dermal"]):
                bd_mod = c
                break

    if bd_mod:
        soak_mods = [
            {"source": "Natural Body Base", "value": bod, "type": "attribute", "notes": "Base natural Body attribute", "rule_anchor": ""},
            {"source": bd_mod.get("name", "Bone Density Augmentation R4"), "value": "+4 Soak", "type": "augmentation", "notes": "+4 dice for damage resistance soak (reaches the +4 SRMG Augmentation Soak limit)", "rule_anchor": "rules/rules_and_downtime.html#augmentation-stacking"}
        ]
        # Inspect armor gear
        armors = data.get("armors", []) or data.get("armor", [])
        if armors:
            for a in armors:
                if isinstance(a, dict):
                    a_name = a.get("name", "Armor")
                    a_dr = a.get("defense_rating") or a.get("dr") or 2
                    if "hood" in a_name.lower() and "skinshield" in a_name.lower():
                        soak_mods.append({
                            "source": "Securetech SkinShield",
                            "value": "+2 DR",
                            "type": "armor gear",
                            "notes": "Form-fitting under-armor layer adds +2 to Defense Rating",
                            "rule_anchor": "rules/rules_and_downtime.html#tactical-combat"
                        })
                        soak_mods.append({
                            "source": "Ballistic Hood",
                            "value": "+1 DR",
                            "type": "armor gear",
                            "notes": "Integrated head protection adds +1 to Defense Rating",
                            "rule_anchor": "rules/rules_and_downtime.html#tactical-combat"
                        })
                    else:
                        soak_mods.append({
                            "source": a_name,
                            "value": f"+{a_dr} DR",
                            "type": "armor gear",
                            "notes": f"Armor provides +{a_dr} to Defense Rating",
                            "rule_anchor": "rules/rules_and_downtime.html#tactical-combat"
                        })
        else:
            soak_mods.extend([
                {"source": "Securetech SkinShield", "value": "+2 DR", "type": "armor gear", "notes": "Form-fitting under-armor layer adds +2 to Defense Rating", "rule_anchor": "rules/rules_and_downtime.html#tactical-combat"},
                {"source": "Ballistic Hood", "value": "+1 DR", "type": "armor gear", "notes": "Integrated head protection adds +1 to Defense Rating", "rule_anchor": "rules/rules_and_downtime.html#tactical-combat"}
            ])

        if len(soak_mods) > threshold:
            results.append({
                "category": "Damage Resistance & Protection",
                "name": "Damage Resistance Soak & Defense Rating (DR)",
                "total_pool": f"{bod + 4}d6 Soak / 6 DR",
                "base_summary": f"Body {bod} + Bone Density R4 (+4) + SkinShield (+2 DR) + Ballistic Hood (+1 DR)",
                "modifiers": soak_mods,
                "stacking_legality": "Bone Density provides +4 Body soak dice, reaching the +4 SRMG Augmentation Soak limit. Armor layers provide Defense Rating (DR) rather than soak dice, obeying SR6 unbundled armor rules.",
                "operational_constraints": "SkinShield has 0 Social Modifier, allowing full concealment in formal, corporate, or street environments.",
                "count": len(soak_mods)
            })

    # 4. Condition Monitors & Wound Mitigation (Data-Driven from Body & Willpower)
    wil = int(attrs.get("willpower", 1))
    base_phys_boxes = (bod + 1) // 2 + 8
    base_stun_boxes = (wil + 1) // 2 + 8

    stun_mods = [
        {"source": "Natural Willpower Formula", "value": f"{base_stun_boxes} boxes", "type": "attribute", "notes": f"Base formula: ceil(WIL {wil} / 2) + 8", "rule_anchor": ""}
    ]
    extra_stun = 0
    wound_shift = 0

    # Inspect qualities and nanotech for condition monitor bonuses
    qualities = data.get("qualities", {})
    pos_q = qualities.get("positive", []) if isinstance(qualities, dict) else []
    for q in pos_q:
        q_name = q.get("name", str(q)) if isinstance(q, dict) else str(q)
        if "toughness" in q_name.lower():
            extra_stun += 1
            stun_mods.append({
                "source": q_name,
                "value": "+1 box",
                "type": "quality",
                "notes": "Expands Condition Monitor capacity",
                "rule_anchor": "rules/rules_and_downtime.html"
            })
        if "pain tolerance" in q_name.lower() or "high pain" in q_name.lower():
            wound_shift += 1
            stun_mods.append({
                "source": q_name,
                "value": "-1 wound step",
                "type": "quality",
                "notes": "Ignores wound penalties up to rating",
                "rule_anchor": "rules/rules_and_downtime.html"
            })

    if identity.get("is_monad"):
        stun_mods.append({
            "source": "Monad Toughness Swarm Protocol",
            "value": "+1 box, -1 wound step",
            "type": "monad ability",
            "notes": "Internal nanite swarm absorbs kinetic shock and shifts wound penalty thresholds",
            "rule_anchor": "rules/rules_and_downtime.html#monad-nanite-boosts"
        })
        extra_stun += 1
        wound_shift += 1

    if len(stun_mods) > threshold:
        shift_note = f" (Wound Shift -{wound_shift})" if wound_shift > 0 else ""
        results.append({
            "category": "Health & Condition Monitors",
            "name": "Stun Condition Monitor & Wound Resistance",
            "total_pool": f"{base_stun_boxes + extra_stun} Stun Boxes{shift_note}",
            "base_summary": f"Base {base_stun_boxes} boxes + Enhancements (+{extra_stun} boxes)",
            "modifiers": stun_mods,
            "stacking_legality": "Condition Monitor expansions increase damage thresholds rather than test pools, avoiding dice pool caps entirely.",
            "operational_constraints": f"Wound penalties apply every 3 boxes of damage taken (adjusted by {wound_shift} box threshold shift)." if wound_shift > 0 else "Wound penalties apply every 3 boxes of damage taken.",
            "count": len(stun_mods)
        })

    # 5. Magic Actions & Foci Protocols (Velvet & Awakened)
    mag_val = int(attrs.get("magic", 0))
    if mag_val > 0:
        magic_pools = ModifierEngine.get_magic_action_pools(data, enhanced=True)

        # 1. Spellcasting & Sorcery
        spell_opt = magic_pools.get("spellcasting")
        if spell_opt:
            sorc_mods = []
            for c in spell_opt.components:
                for m in c.modifiers:
                    if m.enabled:
                        sorc_mods.append({
                            "source": m.source,
                            "value": f"+{m.value}",
                            "type": m.type,
                            "notes": getattr(m, "notes", None) or "Magic-linked focus or attribute augmentation",
                            "rule_anchor": getattr(m, "rule_anchor", None) or "rules/rules_and_downtime.html#foci"
                        })
            if spell_opt.specialization:
                sorc_mods.append({
                    "source": spell_opt.specialization.source,
                    "value": f"+{spell_opt.specialization.value}",
                    "type": "specialization",
                    "notes": "Applies +2 bonus dice to Spellcasting tests",
                    "rule_anchor": "rules/rules_and_downtime.html#spellcasting"
                })
            for m in spell_opt.tactical_modifiers:
                sorc_mods.append({
                    "source": m.source,
                    "value": f"+{m.value}",
                    "type": m.type,
                    "notes": getattr(m, "notes", None) or "Adept ability enhancement",
                    "rule_anchor": getattr(m, "rule_anchor", None) or "rules/rules_and_downtime.html#adept-powers"
                })
            if len(sorc_mods) >= threshold:
                results.append({
                    "category": "Magic & Foci Protocols",
                    "name": "Spellcasting (Sorcery)",
                    "total_pool": f"{spell_opt.total_pool}d6 ({spell_opt.bought_hits} Bought Hits)",
                    "base_summary": f"{spell_opt.get_base_stat_skill_string()} + {spell_opt.get_modifiers_breakdown_string()}",
                    "modifiers": sorc_mods,
                    "stacking_legality": "Power Focus (+3) operates within the SRMG +4 Augmentation limit for Magic. Skill Specialization (+2) is an exempt modifier under SRMG multi-component rules.",
                    "operational_constraints": "Requires Power Focus to be bonded and carried. Sustained spells maintained via Focused Concentration R3.",
                    "count": len(sorc_mods)
                })

        # 2. Spirit Channeling Inhabitation
        chan_opt = magic_pools.get("channeling")
        if chan_opt:
            chan_mods = []
            for c in chan_opt.components:
                for m in c.modifiers:
                    if m.enabled:
                        chan_mods.append({
                            "source": m.source,
                            "value": f"+{m.value}",
                            "type": m.type,
                            "notes": getattr(m, "notes", None) or "Magic-linked focus bonus",
                            "rule_anchor": getattr(m, "rule_anchor", None) or "rules/rules_and_downtime.html#foci"
                        })
            for m in chan_opt.action_modifiers:
                chan_mods.append({
                    "source": m.source,
                    "value": f"+{m.value}",
                    "type": m.type,
                    "notes": "Initiate Grade bonus added to Channeling test (Street Wyrd p. 122)",
                    "rule_anchor": "rules/rules_and_downtime.html#channeling-and-spirit-protocols"
                })
            if len(chan_mods) >= threshold:
                results.append({
                    "category": "Magic & Spirit Protocols",
                    "name": "Spirit Channeling (Inhabitation)",
                    "total_pool": f"{chan_opt.total_pool}d6 ({chan_opt.bought_hits} Bought Hits)",
                    "base_summary": f"{chan_opt.get_base_stat_skill_string()} + {chan_opt.get_modifiers_breakdown_string()}",
                    "modifiers": chan_mods,
                    "stacking_legality": "Power Focus (+3) applies directly to Magic component. Initiate Grade applies as an action-component modifier, stacking legally.",
                    "operational_constraints": "Requires conscious inhabitation of an existing bound spirit (Force 3 or Force 5). Grants dual natured state and physical attribute boosts.",
                    "count": len(chan_mods)
                })

        # 3. Drain Resistance Soak
        drain_opt = magic_pools.get("drain_resistance")
        if drain_opt:
            drain_mods = []
            for c in drain_opt.components:
                for m in c.modifiers:
                    if m.enabled:
                        drain_mods.append({
                            "source": f"{c.name}: {m.source}",
                            "value": f"+{m.value}",
                            "type": m.type,
                            "notes": "Sustained Increase Attribute Health spell (+4 SRMG Augmentation Cap)",
                            "rule_anchor": "rules/rules_and_downtime.html#sustained-spells"
                        })
            if len(drain_mods) >= threshold:
                results.append({
                    "category": "Magic & Tradition Defenses",
                    "name": "Drain Resistance (Shinto / Musok)",
                    "total_pool": f"{drain_opt.total_pool}d6 ({drain_opt.bought_hits} Bought Hits)",
                    "base_summary": f"{drain_opt.get_base_stat_skill_string()} + {drain_opt.get_modifiers_breakdown_string()}",
                    "modifiers": drain_mods,
                    "stacking_legality": "Increase Attribute spells boost Willpower (+4) and Charisma (+4) up to the SRMG +4 Augmentation limit per attribute, stacking across the two tradition components.",
                    "operational_constraints": "Sustained with 0 sustaining penalties under Focused Concentration (Rating 3).",
                    "count": len(drain_mods)
                })

    return results


def render_multi_modifier_interactions(char_id: str, threshold: int = 2) -> str:
    """
    Renders structured Markdown callout boxes and breakdown tables for any test pool,
    attribute, or derived stat with more than `threshold` active modifiers.
    """
    interactions = get_multi_modifier_interactions(char_id, threshold=threshold)
    if not interactions:
        return "*(No pools currently exceed the multi-modifier interaction threshold)*\n"

    sections = []
    sections.append(f"> **Automated Multi-Modifier Audit**: The following {len(interactions)} tests, pools, and derived statistics utilize **more than {threshold} active modifiers**, requiring explicit mechanical interaction auditing under SRMG rules.\n")

    for item in interactions:
        title = f"⚡ {item['category'].upper()}: {item['name']} ({item['total_pool']})"
        rows = [
            f"::: {{.callout-note icon=false title=\"{title}\"}}",
            f"**Derivation**: `{item['base_summary']}`  ",
            f"**Active Interacting Modifiers ({item['count']})**:\n",
            "| Modifier Source | Type | Value / Effect | Notes & Operational Mechanism | Citation / Link |",
            "| :--- | :---: | :---: | :--- | :--- |"
        ]
        for m in item["modifiers"]:
            source_link = f"[{m['source']}]({m['rule_anchor']})" if m.get("rule_anchor") else f"**{m['source']}**"
            val_str = f"+{m['value']}" if isinstance(m['value'], int) and m['value'] > 0 else str(m['value'])
            rows.append(f"| {source_link} | `{m['type']}` | **{val_str}** | {m['notes']} | `{m.get('rule_anchor') or 'Core Rules'}` |")

        rows.append(f"\n* **Stacking Legality & Caps Check**: {item['stacking_legality']}")
        rows.append(f"* **Operational Constraints & Interdependencies**: {item['operational_constraints']}")
        rows.append(":::\n")
        sections.append("\n".join(rows))

    return "\n\n".join(sections)


# ============================================================================
# Dynamic Rules Page Re-exports
# ============================================================================

from sr6core.rules_matrix_actions import render_matrix_actions_markdown
from sr6core.rules_conjuring_tables import (
    render_downtime_binding_markdown,
    calculate_downtime_binding_table,
)
