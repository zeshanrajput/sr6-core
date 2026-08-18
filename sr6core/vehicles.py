"""
Vehicle & Drone Modification Parser, Augmented Profile Calculator, and Rigging Engine for SR6.

Supports:
  - Dynamic Vehicle Modifications (Structural Body, Armor Increase, Enhanced Sensors, Rotor Propulsion, Wrist Shields)
  - Standardized SR6 Single-Line Abbreviations (HAN, ACC, SPD, BOD, ARM, PLT, SEN)
  - Pilot Origins & Emergent AI Rigging Evaluation (Inhabited Override, Remote AR, Autopilot)

FUTURE RIGGER & RCC EXPANSION HOOKS:
  When expanding to meat-space riggers and RCC-based rigging:
  - Mode 1 (Autopilot): Drone Pilot + Shared RCC Autosofts
  - Mode 2 (Remote AR): Meat Physical Stats (BOD, AGI, REA, STR) + PC Skills (Piloting, Firearms, Stealth)
  - Mode 3 (Remote VR): Meat Mental Stats (WIL, LOG, INT, CHA) + PC Skills
  - Mode 4 (Jumped-In VR): Meat Mental Stats + PC Skills + Control Rig Rating (applies to AR, DR, threshold reductions)
  - Mode 5 (Autosoft Substitution): Emergent Intelligence or Pilot Origins substituting Autosofts
  - Mode 6 (Sprite / Form Override): Sprite Power Override or Enhance Automaton Complex Form
  - RCC Features: Noise Reduction (reduces distance/spam penalties), Program Sharing (Autosofts broadcast to swarm).
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from sr6core.modifiers import ModifierEngine


def parse_vehicle_modifications(drone_dict: Dict[str, Any], char_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Parses a vehicle or drone's modifications list and returns the augmented chassis profile.
    Uncapped for Body, Armor, and Sensors.
    """
    name = drone_dict.get("name", "Drone")
    body = int(drone_dict.get("body", 1))
    armor = int(drone_dict.get("armor", 0))
    pilot = int(drone_dict.get("pilot", 2))
    sensor = int(drone_dict.get("sensor", 2))
    speed = drone_dict.get("speed", 30)
    h_on = drone_dict.get("handling_on", 3)
    h_off = drone_dict.get("handling_off", h_on)
    a_on = drone_dict.get("accel_on", 5)
    a_off = drone_dict.get("accel_off", a_on)
    mods = drone_dict.get("modifications", [])

    body_bonus = 0
    armor_bonus = 0
    sensor_bonus = 0
    has_rotor = False
    has_retractable_skates = False
    has_wrist_shield = False
    notes_list = []

    # Inspect Character Network Sensor Upgrade
    if char_data:
        qualities = char_data.get("qualities", {})
        pos_q = qualities.get("positive", []) if isinstance(qualities, dict) else []
        pos_names = [q.get("name", "").lower() if isinstance(q, dict) else str(q).lower() for q in pos_q]
        if any("sensor upgrade" in qn or "sensor_upgrade" in qn for qn in pos_names):
            sensor_bonus += 1
            notes_list.append("Network Sensor Upgrade (+1)")

    # Parse Modifications
    for m in mods:
        m_str = str(m).strip()
        m_lower = m_str.lower()

        # 1. Structural Integrity (+Body)
        struct_match = re.search(r"structural\s+integrity\s+(\d+)", m_lower)
        if struct_match:
            b_val = int(struct_match.group(1))
            body_bonus += b_val
            notes_list.append(f"Structural Integrity (+{b_val} BOD)")

        # 2. Armor Increase (+Armor)
        armor_match = re.search(r"armor\s+increase\s+(\d+)", m_lower)
        if armor_match:
            a_val = int(armor_match.group(1))
            armor_bonus += a_val
            notes_list.append(f"Armor Increase (+{a_val} ARM)")

        # 3. Enhanced / Increased Sensors (+Sensor)
        sensor_match = re.search(r"(enhanced|increased)\s+sensors?\s+(\d+)", m_lower)
        if sensor_match:
            s_val = int(sensor_match.group(2))
            sensor_bonus += s_val
            notes_list.append(f"Enhanced Sensors (+{s_val} SEN)")

        # 4. Secondary Propulsion (Rotor)
        if "rotor" in m_lower:
            has_rotor = True

        # 5. Retractable Skates
        if "skates" in m_lower:
            has_retractable_skates = True

        # 6. Wrist Shield
        if "wrist shield" in m_lower or "wrist_shield" in m_lower:
            has_wrist_shield = True
            armor_bonus += 4
            notes_list.append("Wrist Shield (+4 ARM)")

        # 7. RAM Plating
        ram_match = re.search(r"ram\s+plating\s+(\d+)", m_lower)
        if ram_match:
            ram_val = int(ram_match.group(1))
            armor_bonus += ram_val
            notes_list.append(f"RAM Plating (+{ram_val} ARM)")

    # Anthroform Drone Armor Stacking:
    # Anthrodrones may wear metahuman armor (highest primary DR + cumulative layers) or use natural vehicle armor (whichever is higher).
    # Both can deploy a Wrist Shield for an additional +4 Defense Rating.
    is_anthro = any(k in name.lower() for k in ["butler", "man-at-arms", "man_at_arms", "samurai", "duelist", "anthro"]) or "anthro" in str(drone_dict.get("category", "")).lower()
    
    if is_anthro and char_data:
        armors = char_data.get("armors", [])
        primary_armor = 0
        cumulative_armor = 0
        worn_notes = []
        for a in armors:
            if isinstance(a, dict):
                a_name = a.get("name", "")
                rating = int(a.get("rating", a.get("armor", 0)))
                is_primary = a.get("primary", True)
                if is_primary:
                    if rating > primary_armor:
                        primary_armor = rating
                else:
                    cumulative_armor += rating
                    worn_notes.append(f"{a_name} (+{rating})")
        
        total_worn_armor = primary_armor + cumulative_armor
        vehicle_built_in = armor + armor_bonus
        
        if total_worn_armor > vehicle_built_in:
            effective_base_armor = total_worn_armor
            notes_list.append(f"Worn Anthro Armor ({total_worn_armor}: Primary {primary_armor} + Cumulative {cumulative_armor})")
        else:
            effective_base_armor = vehicle_built_in
            if vehicle_built_in > armor:
                pass  # already added in modification loop

        # Wrist Shield (+4 DR when deployed)
        has_wrist_shield = has_wrist_shield or "wrist shield" in [str(m).lower() for m in mods] or is_anthro
        if has_wrist_shield and not any("Wrist Shield" in n for n in notes_list):
            notes_list.append("Wrist Shield (+4 DR when deployed)")
        
        shield_dr = 4 if has_wrist_shield else 0
        aug_armor = effective_base_armor + shield_dr
    else:
        aug_armor = armor + armor_bonus

    aug_body = body + body_bonus
    inhabited_body = aug_body + 1  # Home Device Tuning adds +1 Body when inhabited
    aug_sensor = sensor + sensor_bonus

    # Handling, Accel & Speed strings
    if has_rotor:
        han_str = f"{h_on}/{h_off} (Rotor: 5)"
        acc_str = f"{a_on}/{a_off} (Rotor: 10)"
        spd_str = f"{speed} (Rotor: 120)"
    else:
        han_str = f"{h_on}/{h_off}"
        acc_str = f"{a_on}/{a_off}"
        spd_str = str(speed)

    # Inhabited / Override Pilot & Designer Quality (+1 Pilot, 2 Noise Reduction)
    res = int(char_data.get("attributes", {}).get("resonance", 8)) if char_data else 8
    pos_qualities = char_data.get("qualities", {}).get("positive", []) if char_data else []
    has_designer = any("designer" in str(q.get("name", q) if isinstance(q, dict) else q).lower() for q in pos_qualities)
    designer_pilot_bonus = 1 if has_designer else 0
    inhabited_pilot = res + designer_pilot_bonus

    if has_designer:
        notes_list.append("Designer Quality (+1 Pilot, 2 Noise Reduction on Home Device)")

    pilot_str = f"{pilot} (Override: {inhabited_pilot})"

    return {
        "name": name,
        "base_body": body,
        "augmented_body": aug_body,
        "inhabited_body": inhabited_body,
        "base_armor": armor,
        "augmented_armor": aug_armor,
        "base_pilot": pilot,
        "inhabited_pilot": inhabited_pilot,
        "base_sensor": sensor,
        "augmented_sensor": aug_sensor,
        "handling_str": han_str,
        "accel_str": acc_str,
        "speed_str": spd_str,
        "pilot_str": pilot_str,
        "has_rotor": has_rotor,
        "has_skates": has_retractable_skates,
        "notes": notes_list,
        "summary_line": (
            f"HAN: {han_str} | ACC: {acc_str} | SPD: {spd_str} | "
            f"BOD: {aug_body} (Inhabited: {inhabited_body}) | ARM: {aug_armor} | "
            f"PLT: {pilot_str} | SEN: {aug_sensor}"
        )
    }


def calculate_drone_action_pools(
    char_data: Dict[str, Any],
    drone_dict: Dict[str, Any],
    mode: str = "inhabited_override"
) -> Dict[str, Any]:
    """
    Calculates the 5 standardized drone action pools:
      - Piloting / Maneuvering
      - Gunnery / Targeting Attack
      - Evasion / Defense Test
      - Perception / Clearsight Test
      - Stealth Test

    Modes:
      - 'inhabited_override': Reiko Sprite Power Override + Designer Quality (Pilot=Resonance+1, Focus=4, Taz Symbiosis=4, Diagnosis=3)
      - 'remote_ar': Pilot Origins AI Matrix ASDF attributes + Autosofts + Symbiosis
      - 'autopilot': Drone Base Pilot + Autosofts
      - 'jumped_in_vr': Rigger VR control rig operation (Piloting+INT, Gunnery+LOG)
    """
    res = int(char_data.get("attributes", {}).get("resonance", 8))
    asdf = ModifierEngine.get_living_persona_asdf(char_data)
    active_d = asdf.get("data_processing", 7)
    active_s = asdf.get("sleaze", 9)
    active_f = asdf.get("firewall", 9)

    pos_qualities = char_data.get("qualities", {}).get("positive", []) if char_data else []
    has_designer = any("designer" in str(q.get("name", q) if isinstance(q, dict) else q).lower() for q in pos_qualities)
    designer_pilot_bonus = 1 if has_designer else 0
    inhabited_pilot = res + designer_pilot_bonus

    drone_profile = parse_vehicle_modifications(drone_dict, char_data=char_data)
    sensor_val = drone_profile["augmented_sensor"]
    focus_bonus = 4 if res > 0 else 0
    taz_symbiosis = 4
    taz_diagnosis = 3

    if mode == "inhabited_override":
        # Mode 1: Inhabited Override (Reiko Primary)
        # Pilot replaced with Resonance (8) + Designer Quality (+1) = 9. Because test involves Resonance, Resonance Focus (+4) applies.
        # Maneuvering R9 (7 effective) + Pilot/RES (9) + Focus (4) + Taz Diagnosis (3) = 23d6
        piloting_pool = active_d + inhabited_pilot + focus_bonus + taz_diagnosis
        piloting_breakdown = f"Maneuvering {active_d} + Pilot/RES {inhabited_pilot} + Focus {focus_bonus} + Taz Diagnosis {taz_diagnosis} = {piloting_pool}d6"

        # Targeting R9 (7 effective) + Pilot/RES (9) + Focus (4) + Taz Symbiosis (4) = 24d6
        gunnery_pool = active_d + inhabited_pilot + focus_bonus + taz_symbiosis
        gunnery_breakdown = f"Targeting {active_d} + Pilot/RES {inhabited_pilot} + Focus {focus_bonus} + Taz Symbiosis {taz_symbiosis} = {gunnery_pool}d6"

        # Evasion R9 (7 effective) + Pilot/RES (9) + Focus (4) + Taz Symbiosis (4) = 24d6
        evasion_pool = active_d + inhabited_pilot + focus_bonus + taz_symbiosis
        evasion_breakdown = f"Evasion {active_d} + Pilot/RES {inhabited_pilot} + Focus {focus_bonus} + Taz Symbiosis {taz_symbiosis} = {evasion_pool}d6"

        # Clearsight R9 (7 effective) + Sensor (7) + Taz Symbiosis (4) = 18d6
        perception_pool = active_d + sensor_val + taz_symbiosis
        perception_breakdown = f"Clearsight {active_d} + Sensor {sensor_val} + Taz Symbiosis {taz_symbiosis} = {perception_pool}d6"

        # Stealth R9 (7 effective) + Pilot/RES (9) + Focus (4) + Taz Symbiosis (4) + Sneak-Sneak (2) = 26d6
        stealth_pool = active_d + inhabited_pilot + focus_bonus + taz_symbiosis + 2
        stealth_breakdown = f"Stealth {active_d} + Pilot/RES {inhabited_pilot} + Focus {focus_bonus} + Taz Symbiosis {taz_symbiosis} + Tactical Soft Sneak-Sneak 2 = {stealth_pool}d6"

    elif mode == "remote_ar":
        # Mode 2: Remote AR Control (AI Physical attributes mapped to ASDF)
        # Piloting: Maneuvering (7) + Sleaze (9) + Taz Diagnosis (3) = 19d6
        piloting_pool = active_d + active_s + taz_diagnosis
        piloting_breakdown = f"Maneuvering {active_d} + Sleaze/REA {active_s} + Taz Diagnosis {taz_diagnosis} = {piloting_pool}d6"

        # Gunnery: Targeting (7) + Data Proc/AGI (7) + Taz Symbiosis (4) = 18d6
        gunnery_pool = active_d + active_d + taz_symbiosis
        gunnery_breakdown = f"Targeting {active_d} + Data Proc/AGI {active_d} + Taz Symbiosis {taz_symbiosis} = {gunnery_pool}d6"

        # Evasion: Evasion (7) + Sleaze/REA (9) + Taz Symbiosis (4) = 20d6
        evasion_pool = active_d + active_s + taz_symbiosis
        evasion_breakdown = f"Evasion {active_d} + Sleaze/REA {active_s} + Taz Symbiosis {taz_symbiosis} = {evasion_pool}d6"

        # Perception: Clearsight (7) + Sensor (7) + Taz Symbiosis (4) = 18d6
        perception_pool = active_d + sensor_val + taz_symbiosis
        perception_breakdown = f"Clearsight {active_d} + Sensor {sensor_val} + Taz Symbiosis {taz_symbiosis} = {perception_pool}d6"

        # Stealth: Stealth (7) + Data Proc/AGI (7) + Taz Symbiosis (4) + Sneak-Sneak (2) = 20d6
        stealth_pool = active_d + active_d + taz_symbiosis + 2
        stealth_breakdown = f"Stealth {active_d} + Data Proc/AGI {active_d} + Taz Symbiosis {taz_symbiosis} + Tactical Soft 2 = {stealth_pool}d6"

    else:
        # Mode 3: Autopilot
        base_plt = drone_profile["base_pilot"]
        piloting_pool = active_d + base_plt
        piloting_breakdown = f"Maneuvering {active_d} + Pilot {base_plt} = {piloting_pool}d6"
        gunnery_pool = active_d + sensor_val
        gunnery_breakdown = f"Targeting {active_d} + Sensor {sensor_val} = {gunnery_pool}d6"
        evasion_pool = active_d + base_plt
        evasion_breakdown = f"Evasion {active_d} + Pilot {base_plt} = {evasion_pool}d6"
        perception_pool = active_d + sensor_val
        perception_breakdown = f"Clearsight {active_d} + Sensor {sensor_val} = {perception_pool}d6"
        stealth_pool = active_d + base_plt
        stealth_breakdown = f"Stealth {active_d} + Pilot {base_plt} = {stealth_pool}d6"

    return {
        "drone_name": drone_dict.get("name", "Drone"),
        "mode": mode,
        "piloting": {"pool": piloting_pool, "breakdown": piloting_breakdown},
        "gunnery": {"pool": gunnery_pool, "breakdown": gunnery_breakdown},
        "evasion": {"pool": evasion_pool, "breakdown": evasion_breakdown},
        "perception": {"pool": perception_pool, "breakdown": perception_breakdown},
        "stealth": {"pool": stealth_pool, "breakdown": stealth_breakdown}
    }
