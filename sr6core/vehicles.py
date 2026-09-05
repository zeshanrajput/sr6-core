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
    has_wheeled = False
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

    has_smart_tires = False

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

        # 4b. Secondary Propulsion (Wheeled)
        if "wheeled" in m_lower:
            has_wheeled = True

        # 5. Retractable Skates
        if "skates" in m_lower:
            has_retractable_skates = True

        # 6. Wrist Shield
        if "wrist shield" in m_lower or "wrist_shield" in m_lower:
            has_wrist_shield = True

        # 7. RAM Plating
        ram_match = re.search(r"ram\s+plating\s+(\d+)", m_lower)
        if ram_match:
            ram_val = int(ram_match.group(1))
            armor_bonus += ram_val
            notes_list.append(f"RAM Plating (+{ram_val} ARM)")

        # 8. Smart Tires
        if "smart tires" in m_lower or "smart_tires" in m_lower:
            has_smart_tires = True
            if not any("Smart Tires" in n for n in notes_list):
                notes_list.append("Smart Tires (+5 ACC, +10 SPD Interval)")

    # Anthroform Drone Armor Stacking:
    # Anthrodrones may wear metahuman armor (highest primary DR + cumulative layers) or use natural vehicle armor (whichever is higher).
    # Both can deploy a Wrist Shield for an additional +4 Defense Rating.
    is_anthro = any(k in name.lower() for k in ["butler", "man-at-arms", "man_at_arms", "samurai", "duelist", "anthro"]) or "anthro" in str(drone_dict.get("category", "")).lower()
    
    shield_dr = 4 if has_wrist_shield else 0
    if has_wrist_shield and not any("Wrist Shield" in n for n in notes_list):
        notes_list.append("Wrist Shield (+4 ARM)")

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

        aug_armor = effective_base_armor + shield_dr
    else:
        aug_armor = armor + armor_bonus + shield_dr

    aug_body = body + body_bonus
    inhabited_body = aug_body + 1  # Home Device Tuning adds +1 Body when inhabited
    # Inhabited / Override Pilot & Designer Quality (+1 Pilot, 2 Noise Reduction on Home Device)
    is_home_device = any(k in name.lower() for k in ["man-at-arms", "man_at_arms", "butler", "home device", "primary chassis"])
    res = int(char_data.get("attributes", {}).get("resonance", 8)) if char_data else 8
    pos_qualities = char_data.get("qualities", {}).get("positive", []) if char_data else []
    has_designer = any("designer" in str(q.get("name", q) if isinstance(q, dict) else q).lower() for q in pos_qualities)
    designer_pilot_bonus = 1 if has_designer else 0

    if is_home_device:
        inhabited_body = aug_body + 1  # Home Device Tuning adds +1 Body when inhabited
        inhabited_pilot = res + designer_pilot_bonus
        if has_designer:
            notes_list.append("Designer Quality (+1 Pilot, 2 Noise Reduction on Home Device)")
        pilot_str = f"{pilot} (Override: {inhabited_pilot})"
    else:
        inhabited_body = aug_body
        inhabited_pilot = pilot
        pilot_str = str(pilot)

    aug_sensor = sensor + sensor_bonus

    # Clean Top Row Handling, Accel & Speed strings
    han_str = f"{h_on}/{h_off}"
    acc_str = f"{a_on}/{a_off}"
    spd_str = str(speed)

    # 2nd Row Mobility & Propulsion Modes (Rotor, Wheeled & Retractable Skates)
    mobility_parts = []
    if has_rotor:
        mobility_parts.append("Rotor: Han 5, Acc 10, SPD 120 (20)")
    if has_wheeled:
        if has_smart_tires:
            mobility_parts.append("Wheeled (Smart Tires): Han 3/4, Acc 15, SPD 25/120")
        else:
            mobility_parts.append("Wheeled: Han 3/4, Acc 10, SPD 15/120")
    if has_retractable_skates:
        mobility_parts.append("Skates: 10/30/+2")
    mobility_str = ". ".join(mobility_parts)

    return {
        "name": name,
        "is_home_device": is_home_device,
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
        "mobility_str": mobility_str,
        "notes": notes_list,
        "mod_slots": calculate_vehicle_mod_slots(drone_dict, char_data=char_data),
        "summary_line": (
            f"HAN: {han_str} | ACC: {acc_str} | SPD: {spd_str} | "
            f"BOD: {aug_body}{f' (Inhabited: {inhabited_body})' if is_home_device else ''} | ARM: {aug_armor} | "
            f"PLT: {pilot_str} | SEN: {aug_sensor}"
        )
    }


def calculate_vehicle_mod_slots(
    drone_dict: Dict[str, Any],
    char_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Computes Double Clutch (p. 120) vehicle & drone modification slots, hardpoints,
    and cyberlimb internal capacity accounting.

    Rules:
      - A vehicle or drone has Chassis, Powertrain, and Electronic mod slots equal to
        its unmodified Body in each category. Body increases (e.g. Structural Integrity)
        do not increase mod slots.
      - 2:1 permanent shifting: Available slots in any category can be shifted to another
        at a 2:1 ratio (spending 2 available slots to gain 1 needed slot).
      - Automated least-used conversion: When a category has a deficit, slots are automatically
        pulled from the category with the highest remaining available capacity.
      - Matching components replacement differential: Replacing a base component with a
        higher rating costs (rating - base) slots.
      - SRM Anthroform Limb Rule: Stock limbs on anthroform drones cost 0 Chassis slots and
        have 0 cyberware capacity. Replacing a stock limb with an actual cyberlimb costs 0
        additional Chassis slots (1-for-1 exchange) and unlocks full cyberlimb capacity.
      - Hardpoints: Base Standard Hardpoints = Body // 3.
    """
    name = drone_dict.get("name", "Drone")
    body = int(drone_dict.get("body", 1))
    base_sensor = int(drone_dict.get("sensor", 1))
    is_anthro = any(k in name.lower() for k in ["butler", "man-at-arms", "man_at_arms", "samurai", "duelist", "anthro"]) or "anthro" in str(drone_dict.get("category", "")).lower()
    is_small = "small" in str(drone_dict.get("category", "")).lower()

    base_slots = {
        "chassis": body,
        "powertrain": body,
        "electronic": body
    }

    if is_small and body > 3:
        base_hardpoints = 0.5  # 1 small hardpoint = 0.5 standard
        hp_type_desc = "Small (1)"
    elif body >= 3:
        base_hardpoints = body // 3
        hp_type_desc = f"Standard ({base_hardpoints})"
    else:
        base_hardpoints = 0
        hp_type_desc = "None (0)"

    raw_mods = list(drone_dict.get("modifications", []))
    accessories = list(drone_dict.get("accessories", []))
    all_mod_items = raw_mods + [a for a in accessories if a not in raw_mods]

    categorized = {
        "chassis": [],
        "powertrain": [],
        "electronic": [],
        "hardpoint": [],
        "accessory": []
    }
    cyberlimbs = []

    # First pass: identify cyberlimbs
    for m in all_mod_items:
        m_str = str(m.get("name", m) if isinstance(m, dict) else m).strip()
        m_low = m_str.lower()
        if "cyberarm" in m_low or "cyberleg" in m_low or "cyberskull" in m_low or "cybertorso" in m_low:
            cap_match = re.search(r"(\d+)\s+capacity", m_low)
            if cap_match:
                limb_cap = int(cap_match.group(1))
            elif "synthetic" in m_low:
                limb_cap = 8 if "arm" in m_low else (10 if "leg" in m_low else 2)
            else:
                limb_cap = 15 if "arm" in m_low else (20 if "leg" in m_low else 4)
            cyberlimbs.append({
                "name": m_str,
                "capacity": limb_cap,
                "used_capacity": 0,
                "items": []
            })

    # Second pass: classify modifications
    for m in all_mod_items:
        m_str = str(m.get("name", m) if isinstance(m, dict) else m).strip()
        m_low = m_str.lower()

        # 1. Weapon Mounts
        if "weapon mount" in m_low:
            x_m = re.search(r"x(\d+)", m_low)
            count = int(x_m.group(1)) if x_m else 1
            if "small" in m_low:
                hp_cost = 0.5 * count
                size_str = "Small"
            elif "large" in m_low:
                hp_cost = 2.0 * count
                size_str = "Large"
            elif "huge" in m_low:
                hp_cost = 3.0 * count
                size_str = "Huge"
            else:
                hp_cost = 1.0 * count
                size_str = "Standard"
            categorized["hardpoint"].append({
                "name": m_str,
                "category": "hardpoint",
                "rating": None,
                "slots_cost": 0,
                "hardpoints_used": hp_cost,
                "notes": f"Attached to {size_str} Hardpoint ({count}x)",
                "rule_ref": "DC p. 142"
            })
            continue

        # 2. Drone Rack / Bay
        if "drone rack" in m_low or "drone bay" in m_low:
            x_m = re.search(r"x(\d+)", m_low)
            count = int(x_m.group(1)) if x_m else 1
            if "mini" in m_low or "micro" in m_low:
                hp_cost = 0.5 * count
                size_str = "Mini/Micro"
            elif "medium" in m_low:
                hp_cost = 2.0 * count
                size_str = "Medium"
            elif "large" in m_low:
                hp_cost = 3.0 * count
                size_str = "Large"
            else:
                hp_cost = 1.0 * count
                size_str = "Small"
            categorized["hardpoint"].append({
                "name": m_str,
                "category": "hardpoint",
                "rating": None,
                "slots_cost": 0,
                "hardpoints_used": hp_cost,
                "notes": f"Drone Rack ({size_str})",
                "rule_ref": "DC p. 143"
            })
            continue

        # 3. Pop-Out Concealment
        if "pop-out concealment" in m_low:
            x_m = re.search(r"x(\d+)", m_low)
            count = int(x_m.group(1)) if x_m else 1
            slot_cost = 1 * count
            categorized["chassis"].append({
                "name": m_str,
                "category": "chassis",
                "rating": None,
                "slots_cost": slot_cost,
                "notes": f"Conceals weapon mounts under vehicle skin ({count}x)",
                "rule_ref": "DC p. 143"
            })
            continue

        # 4. Cyberlimb (Arm/Leg)
        if "cyberarm" in m_low or "cyberleg" in m_low:
            if is_anthro:
                slot_cost = 0
                notes = "Replaces stock anthro limb (0 Chassis slots per SRM guide). Unlocks cyberware capacity."
            else:
                slot_cost = 1
                notes = "Integrated cyberlimb mounted to chassis (1 Chassis slot)."
            categorized["chassis"].append({
                "name": m_str,
                "category": "chassis",
                "rating": None,
                "slots_cost": slot_cost,
                "notes": notes,
                "rule_ref": "DC p. 130, SRM Guide"
            })
            continue

        # 5. Tesla Coil (Cyberlimb weapon)
        if "tesla coil" in m_low:
            if cyberlimbs:
                cyberlimbs[0]["used_capacity"] += 8
                cyberlimbs[0]["items"].append("Tesla Coil (8 Capacity, 5S(e) Spray 20m)")
                categorized["accessory"].append({
                    "name": m_str,
                    "category": "accessory",
                    "rating": None,
                    "slots_cost": 0,
                    "notes": "Installed in Cyberarm: 8 Capacity [c] (SS, 5S(e) Spray 20m)",
                    "rule_ref": "Body Shop p. 76"
                })
            else:
                categorized["accessory"].append({
                    "name": m_str,
                    "category": "accessory",
                    "rating": None,
                    "slots_cost": 0,
                    "notes": "Cyber implant weapon (5S(e) Spray 20m)",
                    "rule_ref": "Body Shop p. 76"
                })
            continue

        # 6. Structural Integrity
        struct_m = re.search(r"structural\s+integrity\s+(\d+)", m_low)
        if struct_m:
            r_val = int(struct_m.group(1))
            categorized["chassis"].append({
                "name": m_str,
                "category": "chassis",
                "rating": r_val,
                "slots_cost": r_val,
                "notes": f"+{r_val} Body (Max 1/2 Base BOD)",
                "rule_ref": "DC p. 125"
            })
            continue

        # 7. Realistic Features
        real_m = re.search(r"realistic\s+features\s+(\d+)", m_low)
        if real_m:
            r_val = int(real_m.group(1))
            categorized["chassis"].append({
                "name": m_str,
                "category": "chassis",
                "rating": r_val,
                "slots_cost": r_val,
                "notes": f"Perception ({r_val}) threshold to identify as artificial",
                "rule_ref": "DC p. 131"
            })
            continue

        # 8. RAM Plating
        ram_m = re.search(r"ram\s+plating\s+(\d+)", m_low)
        if ram_m:
            r_val = int(ram_m.group(1))
            categorized["chassis"].append({
                "name": m_str,
                "category": "chassis",
                "rating": r_val,
                "slots_cost": 0.5 * r_val,
                "notes": f"+{r_val} Armor, Edge on Stealth, noise modifier vs sensor locks",
                "rule_ref": "DC p. 134"
            })
            continue

        # 9. Armor Increase / Standard Armor
        arm_m = re.search(r"(?:armor\s+increase|standard\s+armor)\s+(\d+)", m_low)
        if arm_m:
            r_val = int(arm_m.group(1))
            categorized["chassis"].append({
                "name": m_str,
                "category": "chassis",
                "rating": r_val,
                "slots_cost": r_val,
                "notes": f"+{r_val} Armor",
                "rule_ref": "DC p. 133"
            })
            continue

        # 10. Secondary Propulsion
        if "propulsion" in m_low or "rotor" in m_low or "wheeled" in m_low:
            if "rotor" in m_low:
                s_cost = 4
                notes = "Han 5, Acc 10, SPD 120 (20)"
            elif "wheeled" in m_low:
                s_cost = 2
                has_st = any("smart tires" in str(x).lower() or "smart_tires" in str(x).lower() for x in all_mod_items)
                if has_st:
                    notes = "Han 3/4, Acc 15, SPD 25/120 (with Smart Tires: +5 ACC, +10 SPD Interval)"
                else:
                    notes = "Han 3/4, Acc 10, SPD 15/120"
            elif "tracked" in m_low:
                s_cost = 2
                notes = "Han 4/2, Acc 4, SPD 15/60"
            elif "hovercraft" in m_low:
                s_cost = 3
                notes = "Han 4, Acc 10, SPD 15/90"
            elif "vector" in m_low:
                s_cost = 5
                notes = "Han 4, Acc 25, SPD 50/300"
            else:
                s_cost = 3
                notes = "Secondary Propulsion System"
            categorized["powertrain"].append({
                "name": m_str,
                "category": "powertrain",
                "rating": None,
                "slots_cost": s_cost,
                "notes": notes,
                "rule_ref": "DC p. 134-135"
            })
            continue

        # 11. Nitro Boost
        if "nitro boost" in m_low:
            categorized["powertrain"].append({
                "name": m_str,
                "category": "powertrain",
                "rating": None,
                "slots_cost": 2,
                "notes": "Doubles Acceleration for 1D6 rounds (1 Wild Die)",
                "rule_ref": "DC p. 133"
            })
            continue

        # 12. Chameleon Coating
        cham_m = re.search(r"chameleon\s+coating(?:\s+(\d+))?", m_low)
        if cham_m:
            r_val = int(cham_m.group(1)) if cham_m.group(1) else 2
            categorized["electronic"].append({
                "name": m_str,
                "category": "electronic",
                "rating": r_val,
                "slots_cost": 2,
                "notes": f"Invisible (Improved) Rating {r_val}",
                "rule_ref": "DC p. 138"
            })
            continue

        # 13. Enhanced / Increased Sensors
        sens_m = re.search(r"(?:enhanced|increased)\s+sensors?\s+(\d+)", m_low)
        if sens_m:
            r_val = int(sens_m.group(1))
            diff_cost = max(0, r_val - base_sensor)
            categorized["electronic"].append({
                "name": m_str,
                "category": "electronic",
                "rating": r_val,
                "slots_cost": diff_cost,
                "notes": f"Sensor {base_sensor} -> {r_val} (Differential cost: {r_val} - {base_sensor} = {diff_cost} slots)",
                "rule_ref": "DC p. 120, 142"
            })
            continue

        # 14. ECM
        ecm_m = re.search(r"ecm(?:\s+(\d+))?", m_low)
        if ecm_m:
            r_val = int(ecm_m.group(1)) if ecm_m.group(1) else 1
            categorized["electronic"].append({
                "name": m_str,
                "category": "electronic",
                "rating": r_val,
                "slots_cost": 1,
                "notes": f"ECM Rating {r_val} (Area or directional jammer)",
                "rule_ref": "DC p. 140"
            })
            continue

        # 15. Retrans Unit
        if "retrans" in m_low:
            categorized["electronic"].append({
                "name": m_str,
                "category": "electronic",
                "rating": None,
                "slots_cost": 1,
                "notes": "Signal rebroadcast eliminating accumulated noise",
                "rule_ref": "DC p. 141"
            })
            continue

        # 16. Smart Tires
        if "smart tires" in m_low or "smart_tires" in m_low:
            categorized["accessory"].append({
                "name": m_str,
                "category": "accessory",
                "rating": None,
                "slots_cost": 0,
                "notes": "+5 Acceleration, +10 Speed Interval (Wheeled mode, run-flat / adaptive terrain)",
                "rule_ref": "DC p. 120-121"
            })
            continue

        # 17. Accessories
        categorized["accessory"].append({
            "name": m_str,
            "category": "accessory",
            "rating": None,
            "slots_cost": 0,
            "notes": "Vehicle accessory (consumes 0 mod slots)",
            "rule_ref": "DC p. 120-121"
        })

    # Slot accounting & 2:1 shift
    cats = ["chassis", "powertrain", "electronic"]
    raw_used = {c: sum(m["slots_cost"] for m in categorized[c]) for c in cats}
    effective_cap = {c: base_slots[c] for c in cats}
    shifted_in = {c: 0 for c in cats}
    shifted_out = {c: 0 for c in cats}
    shifts_list = []

    # 1. Process explicit shifts if provided in drone_dict
    explicit_shifts = drone_dict.get("shifted_slots") or drone_dict.get("mod_slot_shifts") or {}
    if isinstance(explicit_shifts, dict):
        for k_s, v_s in explicit_shifts.items():
            m_sh = re.match(r"([a-zA-Z]+)_to_([a-zA-Z]+)", k_s.lower())
            if m_sh:
                f_c, t_c = m_sh.group(1), m_sh.group(2)
                if f_c in cats and t_c in cats and f_c != t_c:
                    spend = (int(v_s) // 2) * 2
                    gain = spend // 2
                    if spend > 0:
                        shifted_out[f_c] += spend
                        shifted_in[t_c] += gain
                        effective_cap[f_c] -= spend
                        effective_cap[t_c] += gain
                        shifts_list.append({
                            "from": f_c,
                            "to": t_c,
                            "slots_spent": spend,
                            "slots_gained": gain,
                            "explicit": True
                        })

    # 2. Automated conversion from least-used resource for any remaining deficit
    for def_c in cats:
        while raw_used[def_c] > effective_cap[def_c]:
            deficit = int(raw_used[def_c] - effective_cap[def_c])
            needed_spend = deficit * 2
            donor_candidates = []
            for donor_c in cats:
                if donor_c != def_c:
                    avail = effective_cap[donor_c] - raw_used[donor_c]
                    if avail >= 2:
                        donor_candidates.append((donor_c, avail))
            if not donor_candidates:
                break
            # Sort donor candidates descending by available capacity (least-used resource first!)
            donor_candidates.sort(key=lambda x: x[1], reverse=True)
            best_donor, best_avail = donor_candidates[0]
            max_donor_spend = (int(best_avail) // 2) * 2
            actual_spend = min(needed_spend, max_donor_spend)
            actual_gained = actual_spend // 2
            shifted_out[best_donor] += actual_spend
            shifted_in[def_c] += actual_gained
            effective_cap[best_donor] -= actual_spend
            effective_cap[def_c] += actual_gained
            shifts_list.append({
                "from": best_donor,
                "to": def_c,
                "slots_spent": actual_spend,
                "slots_gained": actual_gained,
                "explicit": False,
                "auto": True
            })

    remaining = {c: effective_cap[c] - raw_used[c] for c in cats}
    hardpoints_used = sum(m.get("hardpoints_used", 0) for m in categorized["hardpoint"])
    hp_remaining = base_hardpoints - hardpoints_used

    is_legal = all(remaining[c] >= 0 for c in cats) and (hp_remaining >= 0)
    for cl in cyberlimbs:
        if cl["used_capacity"] > cl["capacity"]:
            is_legal = False

    return {
        "drone_name": name,
        "unmodified_body": body,
        "is_anthro": is_anthro,
        "is_legal": is_legal,
        "base_slots": base_slots,
        "raw_used": raw_used,
        "effective_cap": effective_cap,
        "remaining": remaining,
        "shifted_in": shifted_in,
        "shifted_out": shifted_out,
        "shifts": shifts_list,
        "base_hardpoints": base_hardpoints,
        "hardpoints_used": hardpoints_used,
        "hardpoints_remaining": hp_remaining,
        "categorized_mods": categorized,
        "cyberlimbs": cyberlimbs
    }


def format_vehicle_mod_tables(mod_slots_data: Dict[str, Any]) -> str:
    """
    Renders standard Markdown tables for:
      1. Modification Slots & Capacity Summary (with 2:1 shift annotations)
      2. Installed Modifications by Category (Chassis, Powertrain, Electronic, Hardpoint, Accessory)
      3. Installed Cyberlimbs & Internal Capacity (if cyberlimbs exist)
    """
    if not mod_slots_data or not isinstance(mod_slots_data, dict):
        return ""

    base_slots = mod_slots_data.get("base_slots", {})
    effective_cap = mod_slots_data.get("effective_cap", {})
    raw_used = mod_slots_data.get("raw_used", {})
    remaining = mod_slots_data.get("remaining", {})
    shifts = mod_slots_data.get("shifts", [])
    categorized = mod_slots_data.get("categorized_mods", {})
    cyberlimbs = mod_slots_data.get("cyberlimbs", [])
    base_hp = mod_slots_data.get("base_hardpoints", 0)
    hp_used = mod_slots_data.get("hardpoints_used", 0)
    hp_rem = mod_slots_data.get("hardpoints_remaining", 0)

    # 1. Capacity Summary Table
    rows_summary = [
        "### Double Clutch Modification Slots & Capacity Summary",
        "",
        "| Category | Base Slots | Shifted Slots | Total Capacity | Used Slots | Remaining | Status |",
        "| :--- | :---: | :---: | :---: | :---: | :---: | :---: |"
    ]

    cat_labels = [("chassis", "Chassis"), ("powertrain", "Powertrain"), ("electronic", "Electronic")]
    for c_key, c_label in cat_labels:
        b = base_slots.get(c_key, 0)
        u = raw_used.get(c_key, 0)
        c = effective_cap.get(c_key, b)
        r = remaining.get(c_key, 0)

        # Shift annotation
        shift_notes = []
        for s in shifts:
            if s.get("to") == c_key:
                src = str(s.get("from", "")).title()
                shift_notes.append(f"+{s.get('slots_gained', 0)} *(from {src} @ 2:1)*")
            elif s.get("from") == c_key:
                tgt = str(s.get("to", "")).title()
                shift_notes.append(f"-{s.get('slots_spent', 0)} *(to {tgt} @ 2:1)*")
        shift_str = "<br>".join(shift_notes) if shift_notes else "-"

        status_str = f"**Legal ({'Full' if r == 0 else f'Available: {r}'})**" if r >= 0 else f"**OVER BUDGET ({r})**"
        u_display = int(u) if isinstance(u, float) and u.is_integer() else u
        r_display = int(r) if isinstance(r, float) and r.is_integer() else r
        rows_summary.append(f"| **{c_label}** | {b} | {shift_str} | {c} | {u_display} | {r_display} | {status_str} |")

    # Hardpoints row
    hp_b_display = int(base_hp) if isinstance(base_hp, float) and base_hp.is_integer() else base_hp
    hp_u_display = int(hp_used) if isinstance(hp_used, float) and hp_used.is_integer() else hp_used
    hp_r_display = int(hp_rem) if isinstance(hp_rem, float) and hp_rem.is_integer() else hp_rem
    hp_status = "**Legal (3/3 Used)**" if hp_b_display == 3 and hp_u_display == 3 else ("**Legal**" if hp_r_display >= 0 else "**OVER BUDGET**")
    rows_summary.append(f"| **Hardpoints** | {hp_b_display} (Standard) | - | {hp_b_display} | {hp_u_display} | {hp_r_display} | {hp_status} |")

    # 2. Installed Modifications Table
    rows_mods = [
        "",
        "### Installed Modifications by Category",
        "",
        "| Category | Modification Name | Rating | Slots Consumed | Availability & Cost Notes | Rule Reference |",
        "| :--- | :--- | :---: | :---: | :--- | :--- |"
    ]

    all_mods_ordered = (
        categorized.get("chassis", []) +
        categorized.get("powertrain", []) +
        categorized.get("electronic", []) +
        categorized.get("hardpoint", []) +
        categorized.get("accessory", [])
    )

    for mod in all_mods_ordered:
        cat_disp = mod.get("category", "Mod").title()
        mod_name = mod.get("name", "Modification")
        rating_disp = str(mod.get("rating")) if mod.get("rating") is not None else "-"
        s_cost = mod.get("slots_cost", 0)
        hp_cost = mod.get("hardpoints_used", 0)
        if mod.get("category") == "hardpoint":
            slots_disp = f"0 ({int(hp_cost) if isinstance(hp_cost, float) and hp_cost.is_integer() else hp_cost} HP)"
        else:
            slots_disp = str(int(s_cost) if isinstance(s_cost, float) and s_cost.is_integer() else s_cost)
        notes_disp = mod.get("notes", "")
        rule_ref = mod.get("rule_ref", "DC p. 120")
        rows_mods.append(f"| **{cat_disp}** | {mod_name} | {rating_disp} | {slots_disp} | {notes_disp} | {rule_ref} |")

    # 3. Installed Cyberlimbs Table (if applicable)
    rows_limbs = []
    if cyberlimbs:
        rows_limbs = [
            "",
            "### Installed Cyberlimbs & Internal Capacity",
            "",
            "| Installed Cyberlimb | Base Capacity | Used Capacity | Remaining | Installed Devices / Enhancements | Status |",
            "| :--- | :---: | :---: | :---: | :--- | :---: |"
        ]
        for cl in cyberlimbs:
            cl_name = cl.get("name", "Cyberlimb")
            c_tot = cl.get("capacity", 8)
            c_used = cl.get("used_capacity", 0)
            c_rem = c_tot - c_used
            items_str = ", ".join(cl.get("items", [])) if cl.get("items") else "*(Empty)*"
            cl_status = "**Legal (Full)**" if c_rem == 0 else ("**Legal**" if c_rem > 0 else "**OVER BUDGET**")
            rows_limbs.append(f"| **{cl_name}** | {c_tot} | {c_used} | {c_rem} | {items_str} | {cl_status} |")

    return "\n".join(rows_summary + rows_mods + rows_limbs)



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
    is_home_device = any(k in drone_dict.get("name", "").lower() for k in ["man-at-arms", "man_at_arms", "butler", "home device", "primary chassis"])
    if mode == "inhabited_override" and not is_home_device:
        # Reiko only overrides her Man-at-Arms home device; secondary drones operate on Autopilot
        mode = "autopilot"

    res = int(char_data.get("attributes", {}).get("resonance", 8))
    asdf = ModifierEngine.get_living_persona_asdf(char_data)
    active_d = asdf.get("data_processing", 7)
    active_s = asdf.get("sleaze", 9)
    active_f = asdf.get("firewall", 9)

    pos_qualities = char_data.get("qualities", {}).get("positive", []) if char_data else []
    has_designer = any("designer" in str(q.get("name", q) if isinstance(q, dict) else q).lower() for q in pos_qualities)
    designer_pilot_bonus = 1 if (has_designer and is_home_device) else 0
    inhabited_pilot = res + designer_pilot_bonus

    drone_profile = parse_vehicle_modifications(drone_dict, char_data=char_data)
    sensor_val = drone_profile["augmented_sensor"]
    focus_bonus = 4 if (res > 0 and is_home_device) else 0
    taz_symbiosis = 4
    taz_diagnosis = 3

    # Check for declared 'other' modifiers targeting targeting autosofts (e.g. Smartlink wireless bonus)
    targeting_other_bonus = 0
    targeting_other_breakdown = []
    for mod in char_data.get("modifiers", []):
        if not isinstance(mod, dict) or not mod.get("enabled", True):
            continue
        tgt = str(mod.get("target", "")).lower().strip()
        m_type = str(mod.get("type", "")).lower().strip()
        val = int(mod.get("value", 0))
        m_name = mod.get("name", "Modifier")
        if tgt in ["autosoft:targeting", "skill:targeting", "targeting", "gunnery"] and m_type == "other":
            targeting_other_bonus += val
            targeting_other_breakdown.append(f"{m_name} {val}")

    other_gunnery_str = f" + {' + '.join(targeting_other_breakdown)}" if targeting_other_breakdown else ""

    if mode == "inhabited_override" and is_home_device:
        # Mode 1: Inhabited Override (Reiko Primary)
        # Pilot replaced with Resonance (8) + Designer Quality (+1) = 9. Because test involves Resonance, Resonance Focus (+4) applies.
        # Maneuvering R9 (7 effective) + Pilot/RES (9) + Focus (4) + Taz Diagnosis (3) = 23d6
        piloting_pool = active_d + inhabited_pilot + focus_bonus + taz_diagnosis
        piloting_breakdown = f"Maneuvering {active_d} + Pilot/RES {inhabited_pilot} + Focus {focus_bonus} + Taz Diagnosis {taz_diagnosis} = {piloting_pool}d6"

        # Targeting R9 (7 effective) + Sensor (7) + Taz Symbiosis (4) + Other Modifiers = 18d6+ (Sensor-based test; Resonance Focus does not apply)
        gunnery_pool = active_d + sensor_val + taz_symbiosis + targeting_other_bonus
        gunnery_breakdown = f"Targeting {active_d} + Sensor {sensor_val} + Taz Symbiosis {taz_symbiosis}{other_gunnery_str} = {gunnery_pool}d6"

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

        # Gunnery/Targeting: Targeting (7) + Sensor (7) + Taz Symbiosis (4) + Other Modifiers = 18d6+
        gunnery_pool = active_d + sensor_val + taz_symbiosis + targeting_other_bonus
        gunnery_breakdown = f"Targeting {active_d} + Sensor {sensor_val} + Taz Symbiosis {taz_symbiosis}{other_gunnery_str} = {gunnery_pool}d6"

        # Evasion: Evasion (7) + Sleaze/REA (9) + Taz Symbiosis (4) = 20d6
        evasion_pool = active_d + active_s + taz_symbiosis
        evasion_breakdown = f"Evasion {active_d} + Sleaze/REA {active_s} + Taz Symbiosis {taz_symbiosis} = {evasion_pool}d6"

        # Perception: Clearsight (7) + Sensor (7) + Taz Symbiosis (4) = 18d6
        perception_pool = active_d + sensor_val + taz_symbiosis
        perception_breakdown = f"Clearsight {active_d} + Sensor {sensor_val} + Taz Symbiosis {taz_symbiosis} = {perception_pool}d6"

        # Stealth: Stealth (7) + Data Proc/AGI (7) + Taz Symbiosis (4) + Sneak-Sneak (2) = 20d6
        stealth_pool = active_d + active_d + taz_symbiosis + 2
        stealth_breakdown = f"Stealth {active_d} + Data Proc/AGI {active_d} + Taz Symbiosis {taz_symbiosis} + Tactical Soft 2 = {stealth_pool}d6"

    elif mode == "sprite_override":
        # Mode: Sprite Override (Level 7 Companion / Registered Sprite)
        sprite_rating = 7
        piloting_pool = active_d + sprite_rating + taz_diagnosis
        piloting_breakdown = f"Maneuvering {active_d} + Sprite Pilot {sprite_rating} + Taz Diagnosis {taz_diagnosis} = {piloting_pool}d6"
        gunnery_pool = active_d + sensor_val + taz_symbiosis + targeting_other_bonus
        gunnery_breakdown = f"Targeting {active_d} + Sensor {sensor_val} + Taz Symbiosis {taz_symbiosis}{other_gunnery_str} = {gunnery_pool}d6"
        evasion_pool = active_d + sprite_rating + taz_symbiosis
        evasion_breakdown = f"Evasion {active_d} + Sprite Pilot {sprite_rating} + Taz Symbiosis {taz_symbiosis} = {evasion_pool}d6"
        perception_pool = active_d + sensor_val + taz_symbiosis
        perception_breakdown = f"Clearsight {active_d} + Sensor {sensor_val} + Taz Symbiosis {taz_symbiosis} = {perception_pool}d6"
        stealth_pool = active_d + sprite_rating + taz_symbiosis
        stealth_breakdown = f"Stealth {active_d} + Sprite Pilot {sprite_rating} + Taz Symbiosis {taz_symbiosis} = {stealth_pool}d6"

    else:
        # Mode 3: Autopilot
        base_plt = drone_profile["base_pilot"]
        piloting_pool = active_d + base_plt
        piloting_breakdown = f"Maneuvering {active_d} + Pilot {base_plt} = {piloting_pool}d6"
        autopilot_other = targeting_other_bonus if is_home_device else 0
        other_auto_str = f" + {' + '.join(targeting_other_breakdown)}" if (is_home_device and targeting_other_breakdown) else ""
        gunnery_pool = active_d + sensor_val + autopilot_other
        gunnery_breakdown = f"Targeting {active_d} + Sensor {sensor_val}{other_auto_str} = {gunnery_pool}d6"
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
