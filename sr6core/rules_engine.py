"""
Rules Computation & Resolution Engine for SR6.
Bridges SQLite RulesDB, frontmatter parsing, namespace scoping, and rules resolution.
Exposes high-level Markdown table renderers for Quarto rules chapters and dossiers.
"""

import os
import re
import json
from typing import Dict, Any, List, Optional, Set

from sr6core.rules_db import RulesDB, DEFAULT_DB_PATH
from sr6core.character_manager import CharacterManager
from sr6core.modifiers import ModifierEngine
from sr6core.vehicles import parse_vehicle_modifications, calculate_drone_action_pools


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


def get_weapon_stats(item_id: str, db_path: str = DEFAULT_DB_PATH) -> Optional[Dict[str, Any]]:
    """
    Queries rules_index.db for weapon combat stats.
    Returns dictionary with id, name, dv, ar (list of int/None), mode, ammo, source.
    """
    import xml.etree.ElementTree as ET
    try:
        db = RulesDB(db_path=db_path)
        cursor = db.conn.cursor()

        row = cursor.execute(
            "SELECT id, name, category, source, raw_xml FROM ref_gear WHERE id = ? OR lower(id) = ?",
            (item_id, item_id.lower())
        ).fetchone()
    except Exception:
        return None

    if not row:
        return None

    w_id, name, category, source, raw_xml = row["id"], row["name"], row["category"], row["source"], row["raw_xml"]

    dmg, attack_list, mode, ammo = "0P", [], "SS", "—"
    if raw_xml:
        try:
            root = ET.fromstring(raw_xml)
            weapon_node = root.find("weapon")
            if weapon_node is not None:
                dmg = weapon_node.get("dmg", "0P")
                attack_raw = weapon_node.get("attack", "")
                if attack_raw:
                    for p in attack_raw.rstrip(",").split(","):
                        attack_list.append(int(p) if p.isdigit() else None)
                mode = weapon_node.get("mode", "SS")
                ammo = weapon_node.get("ammo", "—")
        except Exception:
            pass

    return {
        "id": w_id,
        "name": name,
        "category": category,
        "source": source.replace("_", " ").title() if source else "SR6 Core",
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
    return "\n".join(rows)


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
    Decompiling, Resonance Focus Activation, and Fading Resistance).
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
        f"| **Resonance Focus Activation** | Sustained Resonance Focus | Foci Rating (+{focus_bonus} to Resonance Tests) | **+{focus_bonus}d6** | **+{focus_bonus // 4} Hits** |",
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
    Renders a unified strategy table comparing Meatspace Baseline, Adrenaline Surge,
    Living Persona Matrix Mode, and Monad Boost / Cyberware Overdrive configurations.
    """
    rows = [
        "| Operational Mode | Active Augmentations & State | Effective Attributes | Primary Action Pools & Modifiers | Derived Defenses & Hits |",
        "| :--- | :--- | :--- | :--- | :--- |",
        "| **1. Meatspace Baseline (Chrome Active, Wireless ON)** | Used Skillwires R6 (Wireless ON: +1)<br>Used Skilljack R6 + Reflex Recorder (Firearms: +1)<br>Muscle Toner R2, Synaptic Booster R2, Muscle Aug R2<br>*Streamed on-demand activesofts (¥4,000/mo)* | **AGI 5** *(Aug)*<br>**REA 4** *(Aug)*<br>**STR 4** *(Aug)*<br>BOD 4, LOG 6, INT 4 | **Firearms (Praetor/Colt)**: **15d6** (4 Hits) *(Smartlink + Wires + Reflex)*<br>**Streamed Physical Softs**: **12d6** (3 Hits, AGI) / **11d6** (REA/STR)<br>**Engineering**: **7d6** (2 Hits) | **Physical Defense**: **8d6** (2 Hits)<br>**Damage Soak**: **8d6** (2 Hits) *(BOD 4 + Bone Density R4; -1 Phys dmg via Platelet Factories)*<br>**Defense Rating**: **7 DR** (SkinShield w/ Hood) / **8 DR** (Coat + Helmet)<br>**Physical Initiative**: **8 + 3D6** (4 Minor Actions) |",
        "| **2. Adrenaline Pump Surge (SRMG Drug Stacking)** | Adrenaline Pump (Used R2) releasing internal drug<br>Stacks with Synaptic Booster & Muscle Toner per SRMG rules | **AGI 7**<br>**REA 6**<br>**STR 6**<br>**WIL 7** | **Firearms (Praetor/Colt)**: **17d6** (4 Hits)<br>**Streamed Physical Softs**: **14d6** (3 Hits, AGI) / **13d6** (REA/STR)<br>**Athletics / Stealth**: **14d6** (3 Hits) | **Physical Defense**: **10d6** (2 Hits)<br>**Physical Initiative**: **10 + 3D6** *(Init Dice max 3D6)*<br>**Composure**: **9d6** (2 Hits)<br>**Crash**: Stun damage = $\\lceil \\text{rounds} / 2 \\rceil$ resisted w/ unaugmented Body |",
        "| **3. Matrix Living Persona (Veronica Co-Processing)** | Monad Living Persona (Whisper Nets: **A:2 S:6 D:7 F:8**)<br>NV 6 Allocated: +3 FW, +2 Sleaze, +1 DP<br>Hot-Sim VR Matrix Inhabitation | LOG 6<br>INT 4<br>WIL 5<br>CHA 2 | **Offensive Cracking (Hacking)**: **11d6** (2 Hits)<br>**Electronics (Software/Edit)**: **12d6** (3 Hits)<br>**Matrix Perception**: **10d6** (2 Hits)<br>**Hardware / Engineering**: **7d6** (2 Hits) | **Full Matrix Defense**: **13d6** (3 Hits) *(WIL 5 + FW 8; 15d6 active)*<br>**Matrix Initiative**: **9 + 3D6 (AR)** / **12 + 3D6 (Hot-Sim VR)**<br>**Matrix Soak**: **8d6** (Firewall 8) |",
        "| **4. Monad Boost & Overdrive (Peak Performance)** | **Monad NV Boost**: Minor Action, NV test (6 dice). Each hit gives +1 attribute or +1 Minor Action (Duration = hits in rounds; exhausts NV for 1 min).<br>**Cyberware Overdrive**: Minor Action to boost cyberware rating by +2 for 1 action (+1 Edge via *Maximum Overdrive*). | **AGI 7–9**<br>**REA 6–8**<br>**LOG 7–10** *(Mental Boost)* | **Physical Skills w/ Boost**: **13–16d6** (or **17d6** w/ Surge)<br>**Mental Skills w/ Boost**: **13–16d6** (LOG) / **11–13d6** (INT) / **12–14d6** (WIL)<br>**Firearms w/ Boost**: **16–18d6** | **Nanite Cost / Risk**: After boost ends, NV temporarily decreases by total boost for 1 minute. Overflow past racial max inflicts 1 Phys/Stun damage.<br>**Overdrive Risk**: 1 Wild Die; Glitches shut down ware. *(Bioware cannot be overdriven)* |"
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

    if char_id.lower() in ["venn", "union"]:
        rows = [
            "| Weapon Name | Mode (Rounds) | Final DV | Final Effective AR (C / N / M / F / E) | Notes & Constraints |",
            "| :--- | :---: | :---: | :---: | :--- |",
            "| **FN P93 Praetor** | **SA** (2) | 5P | **14 / 13 / 9 / — / —** | Internal Smartgun (+2 AR, +2 Attack Dice), Suppressor, Shock Pad (-1 burst penalty). 50(c) clip. |",
            "| | **BF** (4) | 6P | **12 / 11 / 7 / — / —** | 4-round narrow burst. Shock pad halves recoil penalty. |",
            "| | **FA** (10) | 7P | **10 / 9 / 5 / — / —** | 10-round full auto burst. |",
            "| **Colt Manhunter** | **SS** (1) | 3P | **12 / 12 / 10 / — / —** | Laser Sight / Smartlink (+2 AR, +2 Attack Dice), Silencer, Concealed Holster. 16(c) clip. |",
            "| | **SA** (2) | 4P | **10 / 10 / 8 / — / —** | 2-round semi-auto burst. |",
            "| **Monofilament Whip** | **Melee** | 4P | **14 / — / — / — / —** | Retractable whip from fingertip/skin pocket, Wireless ON (+2 AR). Concealed housing. |",
            "| **Narcoject Hornet** | **SA** (2) | 2S | **13 / 10 / — / — / —** | External Smartgun (+2 AR, +2 Attack Dice). Loaded with Narcoject tranquilizer toxin (12 darts). |"
        ]
        return "\n".join(rows)

    data = char["data"]
    weapons_sec = data.get("weapons", {})
    ranged_list = weapons_sec.get("ranged", []) if isinstance(weapons_sec, dict) else []
    melee_list = weapons_sec.get("close_combat", []) if isinstance(weapons_sec, dict) else []
    
    if isinstance(weapons_sec, list):
        flat_list = weapons_sec
    else:
        flat_list = ranged_list + melee_list

    rows = [
        "| Weapon Name | Mode (Rounds) | Final DV | Final Effective AR (C / N / M / F / E) | Notes & Constraints |",
        "| :--- | :---: | :---: | :---: | :--- |"
    ]

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

    # 1. Crimson Wasp Array (2x Link-Fired - Eye Mounts)
    wasp_stat = get_weapon_stats("crimson_wasp") or {"dv": "5P", "ar": [16, 14, 11, 6]}
    wasp_base_dv = int(re.sub(r"[^\d]", "", wasp_stat["dv"])) if re.search(r"\d", wasp_stat["dv"]) else 5
    # Base + 1 link-fired + 3 smartlink + 2 mount = +6 AR, +2 DV
    wasp_ss_ar = format_ar(wasp_stat["ar"], ar_bonus=6, burst_pen=0)
    wasp_sa_ar = format_ar(wasp_stat["ar"], ar_bonus=6, burst_pen=1)
    rows.append(f"| **Crimson Wasp Array (2x Link-Fired)** | **SS** (1/gun) | {wasp_base_dv + 2}P | **{wasp_ss_ar}** | Link-fired 2x Crimson Wasps in Eye Mounts (+2 DV array bonus, +1 AR). **1 round/gun** (2 rounds total) per attack. |")
    rows.append(f"| | **SA** (2/gun) | {wasp_base_dv + 3}P | **{wasp_sa_ar}** | Link-fired array (Drone mount halves SA penalty). **2 rounds/gun** (4 rounds total) per attack. |")

    # 2. Tesla Coil
    rows.append("| **Tesla Coil (MAA Cyberarm)** | **SS** (1) | 5S(e) | **10 / 12* / — / — / —** | Max 20m, 20m Cone Area Attack (Flamethrower rules), Cyberarm Mount (+2 AR). |")

    # 3. Amalgam Cestas
    rows.append("| **Amalgam Cestas (Man-at-Arms - Phys)** | **Melee** | 3P | **12 / — / — / — / —** | Personalized Grip +2 AR. Overrides Immunity to Normal Weapons. 1 Wild Die. |")

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
    Renders a unified multi-mode strategy table for character scene profiles.
    """
    if char_id.lower() == "velvet":
        rows = [
            "| Operational Mode | Active Adept Powers & Spells | Effective Attributes | Primary Action Pools & Modifiers | Derived Defenses & Hits |",
            "| :--- | :--- | :--- | :--- | :--- |",
            "| **1. Social & Legwork Mode** | Enhanced Social Stance, Kinesics R3, Voice Modulation | **CHA 14**, **WIL 9**, **INT 7** | **Influence**: **19d6** (4 Hits)<br>**Con / Deception**: **19d6** (4 Hits) | **Composure**: **23d6** (5 Hits)<br>**Judge Intentions**: **16d6** (4 Hits)<br>**Drain Soak**: **23d6** (5 Hits) |",
            "| **2. Combat Mode** | Combat Reflexes, Spell Defense Shield, Elemental Strike | **REA 8**, **AGI 6**, **BOD 5** | **Sorcery (Combat Spells)**: **15d6** (3 Hits)<br>**Close Combat**: **13d6** (3 Hits) | **Physical Defense**: **15d6** (3 Hits)<br>**Damage Soak**: **12d6** (3 Hits)<br>**Initiative**: **12 + 3D6** |"
        ]
        return "\n".join(rows)
    return get_monad_strategy_table(char_id)


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
    asdf = ModifierEngine.get_living_persona_asdf(data)
    persona = data.get("living_persona", {})
    base = persona.get("asdf_bonuses", {}) if isinstance(persona, dict) else {}
    synergies = data.get("synergies", {})
    tuning = synergies.get("living_persona_network_tuning", {}).get("asdf_bonuses", {})
    if not tuning:
        tuning = {"attack": 4, "sleaze": 8, "data_processing": 6, "firewall": 6}

    rows = [
        "| Matrix Attribute | Base ASDF | Applied Modifiers & Network Tuning | Active Rating |",
        "| :--- | :---: | :--- | :---: |",
        f"| **Attack (A)** | {base.get('attack', 3)} | Network Tuning (+{tuning.get('attack', 4)}) | **{asdf.get('attack', 7)}** |",
        f"| **Sleaze (S)** | {base.get('sleaze', 1)} | Network Tuning (+{tuning.get('sleaze', 8)}) | **{asdf.get('sleaze', 9)}** |",
        f"| **Data Processing (D)** | {base.get('data_processing', 1)} | Network Tuning (+{tuning.get('data_processing', 6)}) | **{asdf.get('data_processing', 7)}** |",
        f"| **Firewall (F)** | {base.get('firewall', 3)} | Network Tuning (+{tuning.get('firewall', 6)}) | **{asdf.get('firewall', 9)}** |"
    ]
    return "\n".join(rows)



