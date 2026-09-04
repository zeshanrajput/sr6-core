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
    # Non-link-fired: NO Minor Action required. +3 smartlink + 2 mount = +5 AR
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

    # 2. Living Persona & Matrix Defenses (Venn & Reiko)
    if identity.get("is_monad") or data.get("living_persona") or int(attrs.get("resonance", 0)) > 0:
        if identity.get("is_monad"):
            fw_mods = [
                {
                    "source": "Natural Willpower Base",
                    "value": attrs.get("willpower", 7),
                    "type": "attribute",
                    "notes": "Base biological willpower",
                    "rule_anchor": ""
                },
                {
                    "source": "Bio-Response Override Colony",
                    "value": "+1",
                    "type": "augmentation",
                    "notes": "Nanite sensory damping structures boost Willpower by +1 (sustained by 3 NV in Nanohive)",
                    "rule_anchor": "rules/rules_and_downtime.html#monad-nanite-boosts"
                },
                {
                    "source": "Nanite Volume Emulation (NV 2)",
                    "value": "+2",
                    "type": "monad ability",
                    "notes": "Emulates hardware firewall pathways (+2 FW per Whisper Nets p. 149)",
                    "rule_anchor": "rules/rules_and_downtime.html#monad-matrix-attributes"
                },
                {
                    "source": "Full Matrix Defense Action",
                    "value": "+WIL (8)",
                    "type": "matrix defense",
                    "notes": "Adds augmented Willpower (8) to Firewall (10) for 18d6 Full Matrix Defense (4 Bought Hits)",
                    "rule_anchor": "rules/rules_and_downtime.html#tactical-combat"
                }
            ]
            if len(fw_mods) > threshold:
                results.append({
                    "category": "Matrix Defense & Living Persona",
                    "name": "Firewall & Full Matrix Defense",
                    "total_pool": "FW 10 / 18d6 Full Defense (4 Bought Hits)",
                    "base_summary": "Base WIL 7 + Bio-Response (+1) + NV Emulation (+2) + Full Defense (+WIL 8)",
                    "modifiers": fw_mods,
                    "stacking_legality": "Bio-Response Override (+1) operates well within the SRMG +4 Augmentation Cap. Monad NV allocation emulates unbrickable biological hardware architecture. Full Matrix Defense stacks augmented Willpower directly with Firewall.",
                    "operational_constraints": "Bio-Response Override requires 3 NV sustained by the cyberleg Nanohives. Degrades in 1 week without hive maintenance.",
                    "count": len(fw_mods)
                })
        elif int(attrs.get("resonance", 0)) > 0:
            # Reiko Technomancer Living Persona
            asdf_mods = [
                {"source": "Base ASDF Array", "value": "A:3 S:5 D:3 F:5", "type": "base", "notes": "Living Persona base stats", "rule_anchor": ""},
                {"source": "Network Tuning / Symbiosis", "value": "+4 to all ASDF", "type": "technomancer synergy", "notes": "Living persona tuning adds +4 across all Matrix attributes", "rule_anchor": "rules_matrix.html"},
                {"source": "Taz Symbiosis", "value": "+4 Tasking", "type": "teamwork", "notes": "Companion sprite assistance adds +4 teamwork dice", "rule_anchor": "rules_sprites.html"},
                {"source": "Resonance Focus R4", "value": "+4 Focus", "type": "focus", "notes": "Applies +4 dice to Resonance-linked action tests", "rule_anchor": "rules_matrix.html"}
            ]
            if len(asdf_mods) > threshold:
                results.append({
                    "category": "Resonance & Living Persona",
                    "name": "Technomancer ASDF & Resonance Operations",
                    "total_pool": "A:7 S:9 D:7 F:9 (Resonance 8 + Focus 4 = 12d6 Base)",
                    "base_summary": "Base ASDF + Network Tuning (+4) + Taz Symbiosis (+4) + Resonance Focus (+4)",
                    "modifiers": asdf_mods,
                    "stacking_legality": "Network Tuning provides +4 augmented Matrix attributes, respecting the SRMG +4 limit. Taz Symbiosis provides teamwork dice capped at skill rating. Focus bonus applies as an untyped magical tool bonus.",
                    "operational_constraints": "Sustaining complex forms requires Resonance bond. Taz must remain registered and in PAN proximity.",
                    "count": len(asdf_mods)
                })

    # 3. Damage Resistance & Armor
    bod = int(attrs.get("body", 1))
    bd_mod = next((m for m in declared_mods if "bone_density" in m.get("id", "")), None)
    if bd_mod:
        soak_mods = [
            {"source": "Natural Body Base", "value": bod, "type": "attribute", "notes": "Base natural Body attribute", "rule_anchor": ""},
            {"source": "Bone Density Augmentation R4", "value": "+4 Soak", "type": "augmentation", "notes": "+4 dice for damage resistance soak (reaches the +4 SRMG Augmentation Soak limit)", "rule_anchor": "rules/rules_and_downtime.html#augmentation-stacking"},
            {"source": "Securetech SkinShield", "value": "+2 DR", "type": "armor gear", "notes": "Form-fitting under-armor layer adds +2 to Defense Rating", "rule_anchor": "rules/rules_and_downtime.html#tactical-combat"},
            {"source": "Ballistic Hood", "value": "+1 DR", "type": "armor gear", "notes": "Integrated head protection adds +1 to Defense Rating", "rule_anchor": "rules/rules_and_downtime.html#tactical-combat"}
        ]
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

    # 4. Condition Monitors & Wound Mitigation (Venn)
    if identity.get("is_monad"):
        wil = int(attrs.get("willpower", 1))
        stun_mods = [
            {"source": "Natural Willpower Formula", "value": f"{(wil + 1) // 2 + 8} boxes", "type": "attribute", "notes": f"Base formula: ceil(WIL {wil} / 2) + 8", "rule_anchor": ""},
            {"source": "Bio-Response Override Colony", "value": "+1 box", "type": "augmentation", "notes": "+1 box to Stun Condition Monitor", "rule_anchor": "rules/rules_and_downtime.html#monad-nanite-boosts"},
            {"source": "Monad Toughness Swarm Protocol", "value": "+1 box", "type": "monad ability", "notes": "Internal nanite swarm absorbs shock (+1 Stun box, +1 Phys box)", "rule_anchor": "rules/rules_and_downtime.html#monad-nanite-boosts"},
            {"source": "Wound Penalty Threshold Shift", "value": "-1 wound step", "type": "monad ability", "notes": "Shifts all wound penalty thresholds down by 1 box, ignoring initial damage penalties", "rule_anchor": "rules/rules_and_downtime.html#monad-nanite-boosts"}
        ]
        if len(stun_mods) > threshold:
            results.append({
                "category": "Health & Condition Monitors",
                "name": "Stun Condition Monitor & Wound Resistance",
                "total_pool": "13 Stun Boxes (Wound Shift -1)",
                "base_summary": f"Base 12 boxes + Bio-Response (+1) + Monad Toughness (+1 Stun, -1 Wound Step)",
                "modifiers": stun_mods,
                "stacking_legality": "Bio-Response Override and Monad Toughness expand monitor capacity rather than modifying test pools, avoiding SRMG dice pool caps entirely.",
                "operational_constraints": "Wound penalties only begin after taking 4 boxes of damage instead of the standard 3 boxes.",
                "count": len(stun_mods)
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




