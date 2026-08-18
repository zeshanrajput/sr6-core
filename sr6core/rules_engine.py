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


def get_scene_strategy_table(char_id: str = "velvet") -> str:
    """
    Renders a unified strategy table comparing Baseline vs Sustained Enhanced Attribute configurations
    for Social/Legwork and Combat scenes under Focused Concentration R3.
    """
    rows = [
        "| Operational Scene Mode | Sustained Spells (Focused Conc. R3) | Active Attributes | Primary Action Pools & Modifiers | Derived Defenses & Hits |",
        "| :--- | :--- | :--- | :--- | :--- |",
        "| **1. Baseline (Un-buffed)** | None (0 Sustained) | CHA 10, WIL 5, INT 3, REA 2, BOD 2 | **Spellcasting**: 15d6 (3 Hits)<br>**Influence**: 15d6 (3 Hits)<br>**Conjuring**: 7d6 (1 Hit) | **Drain Resist**: 15d6 (3 Hits)<br>**Composure**: 15d6 (3 Hits)<br>**Judge Intentions**: 8d6 (2 Hits) |",
        "| **2. Social & Legwork Mode** | 1. *Inc. Attr (Charisma)* (+4)<br>2. *Inc. Attr (Willpower)* (+4)<br>3. *Inc. Attr (Intuition)* (+4) | **CHA 14** *(Cap)*<br>**WIL 9**<br>**INT 7** | **Social Negotiation**: **19d6** (4 Hits) *(+4 Social Rating)*<br>**Inspire Competence**: **19d6** (4 Hits)<br>**Disguise / Persona Shift**: **10d6** (2 Hits) | **Drain Resist**: **23d6** (5 Hits)<br>**Composure**: **23d6** (5 Hits)<br>**Judge Intentions**: **16d6** (4 Hits)<br>**Memory**: **12d6** (3 Hits) |",
        "| **3. Combat Mode (Reflexes/Defense)** | 1. *Inc. Attr (Charisma)* (+4)<br>2. *Inc. Attr (Willpower)* (+4)<br>3. *Inc. Attr (Reaction)* (+4) | **CHA 14**<br>**WIL 9**<br>**REA 6** | **Spellcasting**: **15d6** (3 Hits)<br>**Counterspelling**: **15d6** (3 Hits)<br>**Physical Initiative**: **9 + 1D6** | **Drain Resist**: **23d6** (5 Hits)<br>**Defense Test (REA+INT)**: **9d6** (2 Hits)<br>**Stun Monitor**: 13 boxes |",
        "| **4. Combat Mode (Hardened Body)** | 1. *Inc. Attr (Charisma)* (+4)<br>2. *Inc. Attr (Willpower)* (+4)<br>3. *Inc. Attr (Body)* (+4) | **CHA 14**<br>**WIL 9**<br>**BOD 6** | **Spellcasting**: **15d6** (3 Hits)<br>**Damage Soak**: **7d6** (BOD 6 + Armor 1) | **Drain Resist**: **23d6** (5 Hits)<br>**Physical Monitor**: 11 boxes<br>**Stun Monitor**: 13 boxes |"
    ]
    return "\n".join(rows)


def get_sprite_action_table(char_id: str, sprite_level: int = 7) -> str:
    """
    Renders a Markdown table of Sprite Compiling, Registering, and Fading Downtime calculations.
    """
    cm = CharacterManager()
    char = cm.load_character(char_id)
    if not char:
        return f"*(Character '{char_id}' not found)*"

    data = char["data"]
    sp = ModifierEngine.get_sprite_downtime_pools(data, sprite_level=sprite_level)

    rows = [
        "| Downtime Action / Protocol | Base Pool | Bought Hits vs Defense | Fading / Mitigation | Net Services / Damage |",
        "| :--- | :---: | :---: | :---: | :---: |",
        f"| **Compile Sprite (L{sprite_level})** | Tasking 6 + RES 8 + Focus 4 = **{sp['compiling_pool']}d6** | **{sp['compiling_hits']} Hits** vs {sp['sprite_def_pool']}d6 ({sp['sprite_def_hits']} Hits) | FV: {sp['compiling_fade_fv']} vs Fade Res {sp['fade_res_pool']}d6 ({sp['fade_res_hits']} Hits) | **{sp['net_compiling_hits'] + 1} Services** (0 Drain) |",
        f"| **Register Sprite (L{sprite_level})** | Registering 8 + RES 8 + Focus 4 = **{sp['registering_pool']}d6** | **{sp['registering_hits']} Hits** vs {sp['sprite_def_pool']}d6 ({sp['sprite_def_hits']} Hits) | FV: {sp['registering_fade_fv']} vs Fade Res {sp['fade_res_pool']}d6 ({sp['fade_res_hits']} Hits) | **+{sp['net_registering_hits']} Services** ({sp['registering_damage']} Stun Drain) |",
        f"| **Resonance Focus Activation** | Resonance Focus R4 | Automatic (Activation FV: {sp['focus_fade_fv']}) | Fade Res {sp['focus_fade_res_pool']}d6 ({sp['focus_fade_res_hits']} Hits) | **0 Drain** (Mitigated) |"
    ]
    return "\n".join(rows)


def get_sprite_commands_table(char_id: str = "yuriko", sprite_level: int = 7) -> str:
    """
    Renders a Markdown table of all available Sprite Commands / Tasks from Hack & Slash and the SRMG FAQ.
    Details command name, associated sprite types, task cost, mechanical effect, and SRMG rules.
    """
    half_res_ceil = (sprite_level + 1) // 2  # e.g. 7 -> 4
    rows = [
        "| Sprite Command / Task | Native Sprite Types | Task Cost | Mechanical Effect (Level " + str(sprite_level) + ") | SRMG Rules & Teamwork Limits |",
        "| :--- | :--- | :---: | :--- | :--- |",
        f"| **Signal Boost** | Courier, Defender | 1 Task | Reduces Noise by **{sprite_level}** for **{sprite_level} combat rounds** | Only benefits the technomancer (does not apply to other PAN devices). |",
        f"| **Host Ken** | Crack | 1 Task | Adds **+{sprite_level}d6** on Matrix actions or Complex Forms targeting a Host or IC | Teamwork rules apply (bonus dice capped at character's base skill rating). |",
        f"| **Hyperthreading** | Data, Music | 1 Task | Adds **+{sprite_level}d6** on Threading Complex Forms | Teamwork rules apply (bonus dice capped at Tasking skill rating). |",
        f"| **File Ken** | Data | 1 Task | Adds **+{sprite_level}d6** on Matrix actions targeting a File | Teamwork rules apply (bonus dice capped at character's base skill rating). |",
        f"| **Cybercombat Boost** | Fault, Assassin | 1 Task | Adds **+{half_res_ceil} Matrix DV** to *Data Spike* or *Resonance Spike* | SRMG rule: Damage boost is $\\lceil\\text{{Resonance}}/2\\rceil$ (half Resonance, rounded up). |",
        f"| **Device Ken** | Machine | 1 Task | Adds **+{sprite_level}d6** on Matrix actions or Complex Forms targeting a Device | Teamwork rules apply (bonus dice capped at character's base skill rating). |"
    ]
    return "\n".join(rows)


def get_matrix_asdf_derivation_table(char_id: str) -> str:
    """
    Renders a transparent derivation table showing how Base ASDF, Sprite Symbiosis,
    Running Programs, and Resonance Allocations combine with the +4 SRMG Augmentation Cap
    to produce the final Active Matrix Attributes for AI/EI characters.
    """
    rows = [
        "| Matrix Attribute | Base Value | Sprite Symbiosis | Running Programs | Resonance Tuning | Clamped Augmentation | Final Active ASDF |",
        "| :--- | :---: | :---: | :---: | :---: | :---: | :---: |",
        "| **Attack (ATT)** | 3 | +3 (Assassin) | — | +1 | **+4** (AI/EI +4 Cap) | **7** |",
        "| **Sleaze (SLZ)** | 5 | +2 (Assassin) | — | +2 | **+4** (AI/EI +4 Cap) | **9** |",
        "| **Data Processing (DP)** | 3 | +1 (Assassin) | +1 (Toolbox) | +2 | **+4** (AI/EI +4 Cap) | **7** |",
        "| **Firewall (FW)** | 5 | +0 (Assassin) | +1 (Encryption) | +3 | **+4** (AI/EI +4 Cap) | **9** |"
    ]
    return "\n".join(rows)


def get_matrix_protocols_summary(char_id: str) -> Dict[str, Any]:
    """Returns the computed Active ASDF, Matrix Initiative, and Full Matrix Defense stats."""
    cm = CharacterManager()
    char = cm.load_character(char_id)
    if not char:
        return {}

    data = char["data"]
    asdf = ModifierEngine.get_living_persona_asdf(data)
    mdef = ModifierEngine.get_full_matrix_defense(data)
    init_str = ModifierEngine.get_matrix_initiative(data)
    
    return {
        "asdf_str": f"A:{asdf['attack']:02d} S:{asdf['sleaze']:02d} D:{asdf['data_processing']:02d} F:{asdf['firewall']:02d}",
        "asdf": asdf,
        "full_defense_pool": mdef["pool"],
        "full_defense_hits": mdef["effective_hits"],
        "full_defense_breakdown": mdef["breakdown"],
        "matrix_initiative": init_str
    }


def get_weapon_attack_table(char_id: str) -> str:
    """
    Renders a Markdown table of standardized weapon attack profiles, link-fired arrays,
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

    # 1. Red Fox Array (Link-Fired)
    fox_stat = get_weapon_stats("red_fox") or {"dv": "6P", "ar": [14, 16, 16, 9]}
    fox_base_dv = int(re.sub(r"[^\d]", "", fox_stat["dv"])) if re.search(r"\d", fox_stat["dv"]) else 6
    # Base + 2 link-fired + 3 smartlink + 2 mount = +7 AR, +4 DV
    fox_ss_ar = format_ar(fox_stat["ar"], ar_bonus=7, burst_pen=0)
    fox_sa_ar = format_ar(fox_stat["ar"], ar_bonus=7, burst_pen=1)
    fox_bf_ar = format_ar(fox_stat["ar"], ar_bonus=7, burst_pen=2)
    rows.append(f"| **Red Fox Array (Link-Fired)** | **SS** (1/gun) | {fox_base_dv + 4}P | **{fox_ss_ar}** | Link-fired 1x Red Fox + 2x Crimson Wasps (+4 DV array bonus, +2 AR). **1 round/gun** (3 rounds total) per attack. |")
    rows.append(f"| | **SA** (2/gun) | {fox_base_dv + 5}P | **{fox_sa_ar}** | Link-fired array (Drone mount halves SA penalty). **2 rounds/gun** (6 rounds total) per attack. |")
    rows.append(f"| | **BF** (4/gun) | {fox_base_dv + 6}P | **{fox_bf_ar}** | Link-fired array (Drone mount halves BF penalty). **4 rounds/gun** (12 rounds total) per attack. |")

    # 2. Crimson Wasp Array (2x Link-Fired)
    wasp_stat = get_weapon_stats("crimson_wasp") or {"dv": "5P", "ar": [16, 14, 11, 6]}
    wasp_base_dv = int(re.sub(r"[^\d]", "", wasp_stat["dv"])) if re.search(r"\d", wasp_stat["dv"]) else 5
    wasp_ss_ar = format_ar(wasp_stat["ar"], ar_bonus=6, burst_pen=0)
    wasp_sa_ar = format_ar(wasp_stat["ar"], ar_bonus=6, burst_pen=1)
    wasp_bf_ar = format_ar(wasp_stat["ar"], ar_bonus=6, burst_pen=2)
    rows.append(f"| **Crimson Wasp Array (2x Link-Fired)** | **SS** (1/gun) | {wasp_base_dv + 2}P | **{wasp_ss_ar}** | Link-fired 2x Crimson Wasps (+2 DV array bonus, +1 AR). **1 round/gun** (2 rounds total) per attack. |")
    rows.append(f"| | **SA** (2/gun) | {wasp_base_dv + 3}P | **{wasp_sa_ar}** | Link-fired array (Drone mount halves SA penalty). **2 rounds/gun** (4 rounds total) per attack. |")
    rows.append(f"| | **BF** (4/gun) | {wasp_base_dv + 4}P | **{wasp_bf_ar}** | Link-fired array (Drone mount halves BF penalty). **4 rounds/gun** (8 rounds total) per attack. |")

    # 3. Tesla Coil
    rows.append("| **Tesla Coil (MAA Cyberarm)** | **SS** (1) | 5S(e) | **10 / 12* / — / — / —** | Max 20m, 20m Cone Area Attack (Flamethrower rules), Cyberarm Mount (+2 AR). |")

    # 4. Ares Predator VI
    pred_stat = get_weapon_stats("ares_predator_vi") or {"dv": "3P", "ar": [10, 10, 8]}
    pred_base_dv = int(re.sub(r"[^\d]", "", pred_stat["dv"])) if re.search(r"\d", pred_stat["dv"]) else 3
    pred_ss_ar = format_ar(pred_stat["ar"], ar_bonus=3, burst_pen=0, grip_cn_bonus=1)
    pred_sa_ar = format_ar(pred_stat["ar"], ar_bonus=3, burst_pen=2, grip_cn_bonus=1)
    pred_bf_ar = format_ar(pred_stat["ar"], ar_bonus=3, burst_pen=4, grip_cn_bonus=1)
    rows.append(f"| **Ares Predator VI** | **SS** (1) | {pred_base_dv}P | **{pred_ss_ar}** | Hand-held sidearm (+4 AR Close/Near with Smartlink + Grip). |")
    rows.append(f"| | **SA** (2) | {pred_base_dv + 1}P | **{pred_sa_ar}** | 2-round SA burst. |")
    rows.append(f"| | **BF** (4) | {pred_base_dv + 2}P | **{pred_bf_ar}** | 4-round narrow burst. |")

    # 5. Monofilament Whip
    whip_stat = get_weapon_stats("monofilament_whip") or {"dv": "6P", "ar": [14]}
    whip_base_dv = int(re.sub(r"[^\d]", "", whip_stat["dv"])) if re.search(r"\d", whip_stat["dv"]) else 6
    whip_ar = format_ar(whip_stat["ar"], ar_bonus=4, burst_pen=0)
    rows.append(f"| **Monofilament Whip** | **Melee** | {whip_base_dv}P | **{whip_ar}** | Fingertip Cyberarm Mount (+2 AR) + Wireless ON (+2 AR). |")

    # 6. Amalgam Cestas
    rows.append("| **Amalgam Cestas (Butler - Phys)** | **Melee** | 3P | **12 / — / — / — / —** | Personalized Grip +2 AR. Overrides Immunity to Normal Weapons. 1 Wild Die. |")

    return "\n".join(rows)


def get_character_table_pools(char_id: str) -> Dict[str, Any]:
    """
    Returns the table-relevant action pools and domain classifications tailored to a character's archetype.
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
    skills = data.get("skills", [])

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


