"""
Mobile JSON Exporter for SR6 Characters.
Generates an enriched, self-contained data payload for mobile-first character sheet interfaces,
including base vs effective buffed pools, bought hits, breakdown components, weapon stat blocks,
drones with rigged pools, complex forms/spells/abilities, contacts with favor points, and financials.
"""

import os
import re
from typing import Dict, Any, List, Optional

from sr6core.modifiers import ModifierEngine, PoolModifier
from sr6core.vehicles import calculate_drone_action_pools
from sr6core.log_engine import get_log_totals


def _get_name(item: Any, default: str = "") -> str:
    if isinstance(item, str):
        return item
    if isinstance(item, dict):
        return item.get("name") or item.get("ref") or item.get("id") or default
    return str(item)


def _safe_item_list(raw_section: Any) -> List[Any]:
    if not raw_section:
        return []
    if isinstance(raw_section, list):
        items = []
        for elem in raw_section:
            if isinstance(elem, list):
                items.extend(_safe_item_list(elem))
            else:
                items.append(elem)
        return items
    if isinstance(raw_section, dict):
        items = []
        for k, v in raw_section.items():
            if isinstance(v, list):
                items.extend(_safe_item_list(v))
            elif isinstance(v, dict):
                items.append(v)
            elif isinstance(v, str):
                items.append({"name": v, "id": v})
        return items
    return []


def export_mobile_json(char_data: Dict[str, Any], char_repo_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Compiles enriched character JSON with full synergy derivations,
    base vs buffed pools, bought hits, weapon/drone stat arrays,
    and universal drill-down metadata.
    """
    identity = char_data.get("identity", {})
    attrs = char_data.get("attributes", {})
    skills_raw = char_data.get("skills", [])
    qualities_raw = char_data.get("qualities", {})
    synergies = char_data.get("synergies", {})

    totals = get_log_totals(char_repo_path) if char_repo_path and os.path.exists(char_repo_path) else {}

    handle = identity.get("handle", "Unknown Runner")
    real_name = identity.get("real_name", "N/A")
    metatype = identity.get("metatype", "Human")
    role = identity.get("role", char_data.get("role", "Shadowrunner"))
    stream = identity.get("stream", "")
    tradition = identity.get("tradition", identity.get("mortype", ""))
    mortype = str(identity.get("mortype", "")).lower()
    gender = identity.get("gender", "Diverse")
    age = identity.get("age", "~")
    nuyen = totals.get("Nuyen", identity.get("nuyen", 0))
    karma_avail = totals.get("Karma", identity.get("karma", 0))
    karma_life = totals.get("Lifetime_Karma", identity.get("total_karma", karma_avail))

    is_monad = "monad" in mortype or "monad" in str(metatype).lower()
    is_ai = ("pilot ai" in str(metatype).lower() or str(metatype).lower() == "ai" or "ai" in stream.lower()) and not is_monad
    is_velvet = "velvet" in handle.lower() or "kim jin-young" in real_name.lower()

    # Base attributes
    bod = int(attrs.get("body", 1))
    agi = int(attrs.get("agility", 1))
    rea = int(attrs.get("reaction", 1))
    str_val = int(attrs.get("strength", 1))
    wil = int(attrs.get("willpower", 1))
    log_val = int(attrs.get("logic", 1))
    int_val = int(attrs.get("intuition", 1))
    cha = int(attrs.get("charisma", 1))
    edg = int(attrs.get("edge", 1))
    res = int(attrs.get("resonance", 0))
    mag = int(attrs.get("magic", 0))
    ess = float(attrs.get("essence", 6.0))

    # Living Persona ASDF / Defenses
    asdf = ModifierEngine.get_living_persona_asdf(char_data)
    mdef = ModifierEngine.get_full_matrix_defense(char_data)
    matrix_init = ModifierEngine.get_matrix_initiative(char_data)

    # Calculate Buffed Attributes
    # Velvet: +4 Charisma, +4 Willpower from Sustained Increase Attribute spells
    buffed_cha = cha + 4 if is_velvet else cha
    buffed_wil = wil + 4 if is_velvet else wil

    # Venn / Union: Bioware bonuses (Muscle Toner +2 AGI, Synaptic Booster +2 REA, Muscle Augmentation +2 STR)
    buffed_agi = agi
    buffed_rea = rea
    buffed_str = str_val
    buffed_bod = bod
    buffed_log = log_val
    buffed_int = int_val

    if is_monad:
        # Check bioware in character data
        cyb_bio = _safe_item_list(char_data.get("cyberware")) + _safe_item_list(char_data.get("bioware"))
        for item in cyb_bio:
            name_lower = _get_name(item).lower()
            if "muscle toner" in name_lower and buffed_agi == agi:
                buffed_agi = max(buffed_agi, agi + 2)
            elif "synaptic booster" in name_lower and buffed_rea == rea:
                buffed_rea = max(buffed_rea, rea + 2)
            elif "muscle augmentation" in name_lower and buffed_str == str_val:
                buffed_str = max(buffed_str, str_val + 2)

    # Condition Monitors: Strictly based on BASE attributes!
    nv = int(identity.get("nanite_volume", 0))
    monad_toughness = (nv // 2) if (is_monad or nv > 0) else 0
    phys_boxes = 8 + ((bod + 1) // 2) + monad_toughness
    stun_boxes = 8 + ((wil + 1) // 2) + monad_toughness

    # Derived Pools (using buffed attributes)
    composure = buffed_wil + buffed_cha
    judge_intentions = buffed_wil + buffed_int
    memory = buffed_wil + buffed_log
    lift_carry = buffed_bod + buffed_str

    # Physical Defense & Defense Rating
    phys_defense_pool = buffed_rea + buffed_int

    # Attributes Grid / List Compilation with Base vs Buffed & Deep Links
    attributes_list = []

    if is_ai:
        # AI Metatypes have Matrix Attributes (Attack, Sleaze, Data Processing, Firewall) instead of Physical Attributes
        base_att = 3
        base_slz = 5
        base_dp = 3
        base_fw = 5

        att_val = asdf.get("attack", 7)
        slz_val = asdf.get("sleaze", 9)
        dp_val = asdf.get("data_processing", 7)
        fw_val = asdf.get("firewall", 9)

        attributes_list = [
            {
                "name": "Attack",
                "code": "ATT",
                "base": base_att,
                "buffed": att_val,
                "is_buffed": att_val != base_att,
                "buffs": [{"source": "Network Tuning / Symbiosis", "value": att_val - base_att, "notes": "Subject to +4 Augmented Attribute Limit"}],
                "breakdown": f"Base {base_att} + Network Tuning (+{att_val - base_att}) = {att_val}",
                "doc_link": "chapters/rules_matrix.html#matrix-attributes"
            },
            {
                "name": "Sleaze",
                "code": "SLZ",
                "base": base_slz,
                "buffed": slz_val,
                "is_buffed": slz_val != base_slz,
                "buffs": [{"source": "Network Tuning / Symbiosis", "value": slz_val - base_slz, "notes": "Subject to +4 Augmented Attribute Limit"}],
                "breakdown": f"Base {base_slz} + Network Tuning (+{slz_val - base_slz}) = {slz_val}",
                "doc_link": "chapters/rules_matrix.html#matrix-attributes"
            },
            {
                "name": "Data Processing",
                "code": "DP",
                "base": base_dp,
                "buffed": dp_val,
                "is_buffed": dp_val != base_dp,
                "buffs": [{"source": "Network Tuning / Symbiosis", "value": dp_val - base_dp, "notes": "Subject to +4 Augmented Attribute Limit"}],
                "breakdown": f"Base {base_dp} + Network Tuning (+{dp_val - base_dp}) = {dp_val}",
                "doc_link": "chapters/rules_matrix.html#matrix-attributes"
            },
            {
                "name": "Firewall",
                "code": "FW",
                "base": base_fw,
                "buffed": fw_val,
                "is_buffed": fw_val != base_fw,
                "buffs": [{"source": "Network Tuning / Symbiosis", "value": fw_val - base_fw, "notes": "Subject to +4 Augmented Attribute Limit"}],
                "breakdown": f"Base {base_fw} + Network Tuning (+{fw_val - base_fw}) = {fw_val}",
                "doc_link": "chapters/rules_matrix.html#matrix-attributes"
            },
            {
                "name": "Willpower",
                "code": "WIL",
                "base": wil,
                "buffed": buffed_wil,
                "is_buffed": buffed_wil != wil,
                "buffs": [],
                "breakdown": f"Base {wil}",
                "doc_link": "chapters/rules_matrix.html#matrix-attributes"
            },
            {
                "name": "Logic",
                "code": "LOG",
                "base": log_val,
                "buffed": buffed_log,
                "is_buffed": buffed_log != log_val,
                "buffs": [],
                "breakdown": f"Base {log_val}",
                "doc_link": "chapters/rules_matrix.html#matrix-attributes"
            },
            {
                "name": "Intuition",
                "code": "INT",
                "base": int_val,
                "buffed": buffed_int,
                "is_buffed": buffed_int != int_val,
                "buffs": [],
                "breakdown": f"Base {int_val}",
                "doc_link": "chapters/rules_matrix.html#matrix-attributes"
            },
            {
                "name": "Charisma",
                "code": "CHA",
                "base": cha,
                "buffed": buffed_cha,
                "is_buffed": buffed_cha != cha,
                "buffs": [],
                "breakdown": f"Base {cha}",
                "doc_link": "chapters/rules_matrix.html#matrix-attributes"
            },
            {
                "name": "Edge",
                "code": "EDG",
                "base": edg,
                "buffed": edg,
                "is_buffed": False,
                "buffs": [],
                "breakdown": f"Base {edg}",
                "doc_link": "chapters/rules_matrix.html#network-benefits"
            },
            {
                "name": "Resonance",
                "code": "RES",
                "base": res,
                "buffed": res,
                "is_buffed": True,
                "buffs": [{"source": "Resonance Focus (+4)", "value": 4, "notes": "Applies +4 dice to Resonance-linked action tests"}],
                "breakdown": f"Base {res} (+4 Focus on tests)",
                "doc_link": "chapters/rules_matrix.html#matrix-action-pools"
            }
        ]
    else:
        # Standard Metatypes (Velvet, Venn/Union)
        attributes_list = [
            {
                "name": "Body",
                "code": "BOD",
                "base": bod,
                "buffed": buffed_bod,
                "is_buffed": buffed_bod != bod or is_monad,
                "buffs": [{"source": "Bone Density Augmentation R4", "value": 4, "notes": "+4 unarmored soak (8 Soak)"}] if is_monad else [],
                "breakdown": f"Base {bod}" + (" (+4 Bone Density soak)" if is_monad else ""),
                "doc_link": "chapters/rules_and_downtime.html#augmentation-stacking" if is_monad else "chapters/rules_and_downtime.html"
            },
            {
                "name": "Agility",
                "code": "AGI",
                "base": agi,
                "buffed": buffed_agi,
                "is_buffed": buffed_agi != agi,
                "buffs": [{"source": "Muscle Toner R2 (Used)", "value": buffed_agi - agi, "notes": "+2 Agility bioware"}] if buffed_agi != agi else [],
                "breakdown": f"Base {agi} + Muscle Toner (+{buffed_agi - agi}) = {buffed_agi}" if buffed_agi != agi else f"Base {agi}",
                "doc_link": "chapters/rules_and_downtime.html#augmentation-stacking" if is_monad else "chapters/rules_and_downtime.html"
            },
            {
                "name": "Reaction",
                "code": "REA",
                "base": rea,
                "buffed": buffed_rea,
                "is_buffed": buffed_rea != rea,
                "buffs": [{"source": "Synaptic Booster R2 (Used)", "value": buffed_rea - rea, "notes": "+2 Reaction, +2D6 Initiative"}] if buffed_rea != rea else [],
                "breakdown": f"Base {rea} + Synaptic Booster (+{buffed_rea - rea}) = {buffed_rea}" if buffed_rea != rea else f"Base {rea}",
                "doc_link": "chapters/rules_and_downtime.html#augmentation-stacking" if is_monad else "chapters/rules_and_downtime.html"
            },
            {
                "name": "Strength",
                "code": "STR",
                "base": str_val,
                "buffed": buffed_str,
                "is_buffed": buffed_str != str_val,
                "buffs": [{"source": "Muscle Augmentation R2 (Used)", "value": buffed_str - str_val, "notes": "+2 Strength bioware"}] if buffed_str != str_val else [],
                "breakdown": f"Base {str_val} + Muscle Augmentation (+{buffed_str - str_val}) = {buffed_str}" if buffed_str != str_val else f"Base {str_val}",
                "doc_link": "chapters/rules_and_downtime.html#augmentation-stacking" if is_monad else "chapters/rules_and_downtime.html"
            },
            {
                "name": "Willpower",
                "code": "WIL",
                "base": wil,
                "buffed": buffed_wil,
                "is_buffed": buffed_wil != wil,
                "buffs": [{"source": "Increase Attribute Spell (F4)", "value": buffed_wil - wil, "notes": "Sustained via Focused Concentration R3"}] if buffed_wil != wil else [],
                "breakdown": f"Base {wil} + Increase Attribute (+{buffed_wil - wil}) = {buffed_wil}" if buffed_wil != wil else f"Base {wil}",
                "doc_link": "chapters/rules_and_downtime.html#sustained-spells" if is_velvet else "chapters/rules_and_downtime.html"
            },
            {
                "name": "Logic",
                "code": "LOG",
                "base": log_val,
                "buffed": buffed_log,
                "is_buffed": buffed_log != log_val or is_monad,
                "buffs": [{"source": "Monad Mental Boost (NV)", "value": 4, "notes": "Surges to Logic 10 / Math SPU +1"}] if is_monad else [],
                "breakdown": f"Base {log_val}" + (" (Surges to 10 under Monad Boost)" if is_monad else ""),
                "doc_link": "chapters/rules_and_downtime.html#monad-nanite-boosts" if is_monad else "chapters/rules_and_downtime.html"
            },
            {
                "name": "Intuition",
                "code": "INT",
                "base": int_val,
                "buffed": buffed_int,
                "is_buffed": buffed_int != int_val,
                "buffs": [],
                "breakdown": f"Base {int_val}",
                "doc_link": "chapters/rules_and_downtime.html"
            },
            {
                "name": "Charisma",
                "code": "CHA",
                "base": cha,
                "buffed": buffed_cha,
                "is_buffed": buffed_cha != cha,
                "buffs": [{"source": "Increase Attribute Spell (F4)", "value": buffed_cha - cha, "notes": "Sustained via Focused Concentration R3"}] if buffed_cha != cha else [],
                "breakdown": f"Base {cha} + Increase Attribute (+{buffed_cha - cha}) = {buffed_cha}" if buffed_cha != cha else f"Base {cha}",
                "doc_link": "chapters/rules_and_downtime.html#sustained-spells" if is_velvet else "chapters/rules_and_downtime.html"
            },
            {
                "name": "Edge",
                "code": "EDG",
                "base": edg,
                "buffed": edg,
                "is_buffed": False,
                "buffs": [],
                "breakdown": f"Base {edg}",
                "doc_link": "chapters/rules_and_downtime.html"
            },
            {
                "name": "Magic" if mag > 0 else ("Resonance" if res > 0 else ("Nanite Volume" if is_monad else "Essence")),
                "code": "MAG" if mag > 0 else ("RES" if res > 0 else ("NV" if is_monad else "ESS")),
                "base": mag if mag > 0 else (res if res > 0 else (nv if is_monad else ess)),
                "buffed": mag if mag > 0 else (res if res > 0 else (nv if is_monad else ess)),
                "is_buffed": False,
                "buffs": [],
                "breakdown": f"Base {mag if mag > 0 else (res if res > 0 else (nv if is_monad else f'{ess:.2f}'))}",
                "doc_link": "chapters/rules_and_downtime.html#monad-matrix-attributes" if is_monad else ("chapters/rules_and_downtime.html#foci-protocols" if mag > 0 else "chapters/rules_and_downtime.html")
            }
        ]

    # Skills compilation: Specialization (+2) is NOT added to top-level buffed_pool
    compiled_skills = []
    for s in skills_raw:
        if not isinstance(s, dict):
            continue
        s_name = s.get("name", "Skill")
        s_rating = int(s.get("rating", 1))
        s_attr = s.get("attribute", "logic")
        s_spec = s.get("specialization")

        calc = ModifierEngine.calculate_skill_pool(
            char_data,
            skill_name=s_name,
            skill_rating=s_rating,
            linked_attribute=s_attr,
            specialization=s_spec
        )

        base_pool = calc["base_pool"]
        # General effective pool (DO NOT add specialization +2 here)
        general_effective_pool = calc["effective_pool"]

        bought_hits = general_effective_pool // 4
        specialized_pool = general_effective_pool + 2 if s_spec else general_effective_pool
        specialized_hits = specialized_pool // 4

        buff_list = []
        for m in calc.get("applied_modifiers", []):
            buff_list.append({
                "source": m.source,
                "type": m.type,
                "value": m.value,
                "target": m.target,
                "active": True
            })
        if s_spec:
            buff_list.append({
                "source": f"Specialization: {s_spec}",
                "type": "specialization",
                "value": 2,
                "target": "action",
                "active": False  # Action-specific bonus
            })

        compiled_skills.append({
            "name": s_name,
            "id": s.get("id", s_name.lower().replace(" ", "_")),
            "rating": s_rating,
            "attribute": s_attr,
            "specialization": s_spec,
            "base_pool": base_pool,
            "buffed_pool": general_effective_pool,
            "bought_hits": bought_hits,
            "specialized_pool": specialized_pool,
            "specialized_hits": specialized_hits,
            "effective_attribute": calc.get("effective_attribute", s_attr),
            "is_attribute_overridden": calc.get("is_attribute_overridden", False),
            "breakdown_text": calc.get("breakdown", f"{s_attr[:3].upper()} + {s_rating} Rtg"),
            "buffs": buff_list,
            "doc_link": "chapters/rules_matrix.html#matrix-action-pools" if is_ai else "chapters/rules_and_downtime.html"
        })

    # Activesofts (Software run on Skillwires R6 with +1 Wireless-ON bonus -> Rating 7)
    activesofts_raw = char_data.get("activesofts", [])
    if isinstance(activesofts_raw, list):
        for soft in activesofts_raw:
            if not isinstance(soft, dict):
                continue
            soft_name = soft.get("name", "Activesoft")
            base_r = int(soft.get("rating", 6))
            # Skillwires R6 Wireless-ON bonus (+1 to skill rating)
            aug_r = base_r + 1
            soft_attr = soft.get("attribute", "agility").lower()
            if "firearms" in soft_name.lower():
                soft_attr = "agility"
            elif "cracking" in soft_name.lower():
                soft_attr = "logic"
            elif "perception" in soft_name.lower():
                soft_attr = "intuition"
            elif "engineering" in soft_name.lower():
                soft_attr = "logic"
            elif "stealth" in soft_name.lower():
                soft_attr = "agility"
            elif "close combat" in soft_name.lower():
                soft_attr = "agility"

            # Attribute value (augmented)
            attr_val = buffed_agi if soft_attr == "agility" else (
                buffed_log if soft_attr == "logic" else (
                    buffed_int if soft_attr == "intuition" else (
                        buffed_rea if soft_attr == "reaction" else (
                            buffed_str if soft_attr == "strength" else (
                                buffed_cha if soft_attr == "charisma" else int(attrs.get(soft_attr, 1))
                            )
                        )
                    )
                )
            )
            base_attr_val = int(attrs.get(soft_attr, 1))

            extra_mod = 0
            extra_mod_name = ""
            if "firearms" in soft_name.lower():
                extra_mod = 1
                extra_mod_name = "Reflex Recorder (+1)"
            elif "engineering" in soft_name.lower():
                extra_mod = 1
                extra_mod_name = "Math SPU (+1)"

            total_pool = attr_val + aug_r + extra_mod
            base_pool = base_attr_val + base_r
            bought_hits = total_pool // 4

            buff_list = [
                {"source": "Skillwires Wireless ON", "type": "cyberware", "value": 1, "target": "skill", "active": True}
            ]
            if extra_mod:
                buff_list.append({"source": extra_mod_name, "type": "augmentation", "value": extra_mod, "target": "skill", "active": True})

            breakdown_parts = [f"{soft_attr[:3].upper()} {attr_val}", f"{base_r} Base Soft", "Skillwires (+1)"]
            if extra_mod_name:
                breakdown_parts.append(extra_mod_name)

            clean_display_name = soft_name.replace(" Activesoft", "").replace(" activesoft", "")

            compiled_skills.append({
                "name": f"{clean_display_name} (Activesoft)",
                "id": soft_name.lower().replace(" ", "_"),
                "rating": aug_r,
                "base_rating": base_r,
                "is_activesoft": True,
                "attribute": soft_attr,
                "specialization": None,
                "base_pool": base_pool,
                "buffed_pool": total_pool,
                "bought_hits": bought_hits,
                "specialized_pool": total_pool,
                "specialized_hits": bought_hits,
                "effective_attribute": soft_attr,
                "is_attribute_overridden": False,
                "breakdown_text": " + ".join(breakdown_parts) + f" = {total_pool}d6",
                "buffs": buff_list,
                "doc_link": "chapters/rules_and_downtime.html#activesofts-and-skillwires"
            })

    # Qualities
    pos_raw = qualities_raw.get("positive", []) if isinstance(qualities_raw, dict) else []
    neg_raw = qualities_raw.get("negative", []) if isinstance(qualities_raw, dict) else []
    pos_qualities = []
    for q in pos_raw:
        if isinstance(q, dict):
            pos_qualities.append({
                "name": q.get("name", q.get("ref", "Quality")),
                "rating": q.get("rating"),
                "choice": q.get("choice"),
                "notes": q.get("notes")
            })
        else:
            pos_qualities.append({"name": str(q)})

    neg_qualities = []
    for q in neg_raw:
        if isinstance(q, dict):
            neg_qualities.append({
                "name": q.get("name", q.get("ref", "Quality")),
                "rating": q.get("rating"),
                "choice": q.get("choice"),
                "notes": q.get("notes")
            })
        else:
            neg_qualities.append({"name": str(q)})

    # Weapons compilation with Melee handling and Base vs Buffed stats
    raw_weapons = _safe_item_list(char_data.get("weapons", []))
    compiled_weapons = []
    for w in raw_weapons:
        if isinstance(w, dict):
            w_name = w.get("name", w.get("ref", "Weapon"))
            dmg = w.get("damage", w.get("dv", "3P"))
            ar = w.get("attack_rating", w.get("ar", [10, 10, 8, 0, 0]))
            category = str(w.get("category", "General")).lower()
            modes = w.get("mode", w.get("modes", "SA"))
            ammo = w.get("ammo", "—")
            mods = w.get("accessories", w.get("modifications", []))
            loaded_ammo = w.get("loaded_ammo") or w.get("ammo_type")
            notes = w.get("notes", "")

            # Check if melee / physical weapon (Sap, Stun Baton, Knives, Cestas, Unarmed)
            is_melee = category in ["melee", "unarmed", "exotic_melee", "close_combat", "club", "clubs", "blade", "blades"] or any(
                x in w_name.lower() for x in ["cesta", "cestas", "whip", "dagger", "sword", "knife", "blade", "unarmed", "fist", "club", "staff", "sap", "baton", "stun baton"]
            )

            # Store base stats before modification engine
            base_dmg = dmg
            base_ar = ar
            base_modes = modes
            base_ammo = ammo

            # Attempt rules engine resolution if missing
            if not dmg or not ar:
                try:
                    from sr6core.rules_engine import get_weapon_stats
                    w_db = get_weapon_stats(w.get("ref", w_name))
                    if w_db:
                        dmg = dmg or w_db.get("dv", "3P")
                        ar = ar or w_db.get("ar", [10, 10, 8, 0, 0])
                        modes = modes or w_db.get("mode", "SA")
                        ammo = ammo or w_db.get("ammo", "—")
                        base_dmg = dmg
                        base_ar = ar
                        base_modes = modes
                        base_ammo = ammo
                except Exception:
                    pass

            # Calculate modified weapon stats if available
            try:
                from sr6core.models import WeaponStatBlock
                from sr6core.vault.statblock_parser import calculate_modified_weapon
                raw_ar_val = ar if isinstance(ar, list) else ([int(x.strip()) if x.strip().isdigit() else 0 for x in str(ar).split("/")] if "/" in str(ar) else [10, 10, 8, 0, 0])
                base_w = WeaponStatBlock(
                    name=w_name,
                    category=category,
                    damage=str(dmg),
                    attack_rating=raw_ar_val,
                    firing_modes=modes.split("/") if isinstance(modes, str) else list(modes),
                    ammo_capacity=int(re.search(r"\d+", str(ammo)).group(0)) if ammo and re.search(r"\d+", str(ammo)) else None,
                    ammo_feed="c",
                )
                mod_w = calculate_modified_weapon(base_w, accessories=mods, ammo_type=loaded_ammo)
                dmg = mod_w.damage
                ar = mod_w.attack_rating
                if mod_w.ammo_capacity:
                    ammo = f"{mod_w.ammo_capacity}({mod_w.ammo_feed or 'c'})"
                if mod_w.firing_modes:
                    modes = "/".join(mod_w.firing_modes)
            except Exception:
                pass

            def _format_ar(val: Any) -> str:
                if isinstance(val, list):
                    return " / ".join([str(x) if (isinstance(x, (int, float)) and x > 0) or (isinstance(x, str) and x.isdigit() and int(x) > 0) else "—" for x in val])
                if isinstance(val, str):
                    if "/" in val:
                        return " / ".join([p.strip() if p.strip() not in ["0", "-", "—", ""] else "—" for p in val.split("/")])
                    return val if val not in ["0", "-", ""] else "—"
                if isinstance(val, (int, float)):
                    return str(val) if val > 0 else "—"
                return str(val)

            ar_str = _format_ar(ar)
            base_ar_str = _format_ar(base_ar)

            # For melee / physical weapons, fire modes and ammo do not apply
            if is_melee:
                modes = []
                modes_str = "Melee"
                ammo = "—"
                base_modes_str = "Melee"
                base_ammo = "—"
            else:
                modes_str = str(modes)
                base_modes_str = str(base_modes)

            # Determine doc link
            doc_link = "chapters/rules_combat.html#amalgam-protocols" if "amalgam" in w_name.lower() or "cesta" in w_name.lower() else (
                "chapters/rules_combat.html#tactical-weapon-arrays" if is_ai else "chapters/rules_and_downtime.html#weapon-attack-table"
            )

            compiled_weapons.append({
                "name": w_name,
                "is_melee": is_melee,
                "category": category,
                "damage": dmg,
                "base_damage": base_dmg,
                "attack_rating": ar if isinstance(ar, list) else [ar],
                "attack_rating_str": ar_str,
                "base_attack_rating_str": base_ar_str,
                "modes": modes if isinstance(modes, list) else str(modes).split("/"),
                "modes_str": modes_str,
                "base_modes_str": base_modes_str,
                "ammo": str(ammo),
                "base_ammo": str(base_ammo),
                "loaded_ammo": loaded_ammo,
                "accessories": [str(m.get("name", m)) if isinstance(m, dict) else str(m) for m in mods],
                "notes": notes,
                "doc_link": doc_link
            })

    # Armor
    raw_armors = _safe_item_list(char_data.get("armors", char_data.get("armor", [])))
    compiled_armors = []
    total_dr = 0
    for a in raw_armors:
        if isinstance(a, dict):
            a_name = a.get("name", a.get("ref", "Armor"))
            dr = int(a.get("defense_rating", a.get("rating", 0)))
            total_dr += dr
            mods = a.get("modifications", [])
            compiled_armors.append({
                "name": a_name,
                "defense_rating": dr,
                "modifications": [str(m.get("name", m)) if isinstance(m, dict) else str(m) for m in mods]
            })

    # Drones and Vehicles with Inhabited Action Pools and Base vs Mod Stats
    from sr6core.vehicles import parse_vehicle_modifications
    raw_drones = _safe_item_list(char_data.get("drones", []))
    raw_vehicles = _safe_item_list(char_data.get("vehicles", []))
    compiled_vehicles = []
    for item in raw_vehicles + raw_drones:
        if not isinstance(item, dict):
            continue
        v_name = item.get("name", "Drone / Vehicle")
        v_role = item.get("role", "")
        han_on = item.get("handling_on", item.get("handling", 3))
        han_off = item.get("handling_off", han_on)
        acc_on = item.get("accel_on", item.get("accel", 10))
        acc_off = item.get("accel_off", acc_on)
        spd = item.get("speed", item.get("top_speed", 120))
        interval = item.get("interval", item.get("speed_interval_on", 15))
        v_bod = item.get("body", 1)
        v_arm = item.get("armor", 0)
        pil = item.get("pilot", 1)
        sen = item.get("sensor", 1)
        seats = item.get("seats", "-")
        mods = [str(m.get("name", m)) if isinstance(m, dict) else str(m) for m in item.get("modifications", [])]

        aug_profile = parse_vehicle_modifications(item, char_data=char_data)
        action_pools = calculate_drone_action_pools(char_data, item)
        formatted_pools = {}
        if action_pools:
            for p_key, p_val in action_pools.items():
                if isinstance(p_val, dict):
                    pool_num = p_val.get("pool", 0)
                    formatted_pools[p_key] = {
                        "pool": pool_num,
                        "hits": pool_num // 4,
                        "breakdown": p_val.get("breakdown", "")
                    }

        compiled_vehicles.append({
            "name": v_name,
            "role": v_role,
            "handling": aug_profile.get("handling_str", f"{han_on}/{han_off}"),
            "accel": aug_profile.get("accel_str", f"{acc_on}/{acc_off}"),
            "speed": aug_profile.get("speed_str", str(spd)),
            "interval": interval,
            "body": aug_profile.get("inhabited_body", v_bod),
            "base_body": aug_profile.get("base_body", v_bod),
            "armor": aug_profile.get("augmented_armor", v_arm),
            "base_armor": aug_profile.get("base_armor", v_arm),
            "pilot": aug_profile.get("inhabited_pilot", pil),
            "base_pilot": aug_profile.get("base_pilot", pil),
            "sensor": aug_profile.get("augmented_sensor", sen),
            "base_sensor": aug_profile.get("base_sensor", sen),
            "seats": seats,
            "modifications": mods,
            "profile_notes": aug_profile.get("notes", []),
            "mobility_str": aug_profile.get("mobility_str", ""),
            "rigged_pools": formatted_pools,
            "doc_link": "chapters/rules_drones.html#tactical-drones" if is_ai else "chapters/rules_and_downtime.html"
        })

    # Complex Forms, Spells, Adept Powers, Echoes, Monad Abilities, Sprite Powers with Deep Links
    complex_forms = []
    for cf in _safe_item_list(char_data.get("complex_forms", [])):
        if isinstance(cf, dict):
            cf_name = cf.get("name", cf.get("ref", "Complex Form"))
            complex_forms.append({
                "name": cf_name,
                "fading": cf.get("fading", cf.get("fv", 0)),
                "duration": cf.get("duration", "Instant"),
                "target": cf.get("target", "Device/Persona"),
                "notes": cf.get("notes", ""),
                "doc_link": "chapters/rules_sprites.html#complex-forms"
            })

    submersion_echoes = []
    for echo in _safe_item_list(char_data.get("meta_echoes", char_data.get("submersion_echoes", char_data.get("metamagics", [])))):
        echo_name = _get_name(echo)
        submersion_echoes.append({
            "name": echo_name,
            "doc_link": "chapters/rules_matrix.html#network-benefits"
        })

    sprite_powers = []
    for sp in _safe_item_list(char_data.get("sprite_powers", [])):
        if isinstance(sp, dict):
            sprite_powers.append({
                "name": sp.get("name", "Sprite Power"),
                "type": sp.get("type", "Sprite Power (Symbiosis)"),
                "target": sp.get("target", "PAN / Matrix Icon"),
                "action": sp.get("action", "Minor Action"),
                "effect": sp.get("effect", sp.get("notes", "")),
                "doc_link": "chapters/rules_sprites.html#sprite-symbiosis-powers"
            })

    spells = []
    for sp in _safe_item_list(char_data.get("spells", [])):
        if isinstance(sp, dict):
            sp_name = sp.get("name", sp.get("ref", "Spell"))
            spells.append({
                "name": sp_name,
                "drain": sp.get("drain", 0),
                "type": sp.get("type", "Physical"),
                "range": sp.get("range", "Touch" if "increase" in sp_name.lower() else "LOS"),
                "duration": sp.get("duration", "Sustained" if "increase" in sp_name.lower() else "Instant"),
                "notes": sp.get("notes", ""),
                "doc_link": sp.get("doc_link", "chapters/rules_and_downtime.html#spell-library")
            })

    adept_powers = []
    for ap in _safe_item_list(char_data.get("powers", char_data.get("adept_powers", []))):
        if isinstance(ap, dict):
            adept_powers.append({
                "name": ap.get("name", ap.get("ref", "Power")),
                "cost": ap.get("cost", 0),
                "rating": ap.get("rating"),
                "notes": ap.get("notes", ""),
                "doc_link": ap.get("doc_link", "chapters/rules_and_downtime.html#adept-powers")
            })

    monad_abilities = []
    for ma in _safe_item_list(char_data.get("monad_abilities", [])):
        if isinstance(ma, dict):
            monad_abilities.append({
                "name": ma.get("name", "Ability"),
                "effect": ma.get("effect", ma.get("notes", "")),
                "doc_link": "chapters/rules_and_downtime.html#monad-nanite-boosts"
            })

    # Augmentations (Cyberware / Bioware) with Deep Links
    augmentations = []
    for aug in _safe_item_list(char_data.get("cyberware")) + _safe_item_list(char_data.get("bioware")) + _safe_item_list(char_data.get("augmentations")):
        if isinstance(aug, dict):
            augmentations.append({
                "name": aug.get("name", aug.get("ref", "Augmentation")),
                "rating": aug.get("rating"),
                "grade": aug.get("grade", "Standard"),
                "essence": aug.get("essence", 0),
                "notes": aug.get("notes", ""),
                "doc_link": "chapters/rules_and_downtime.html#augmentation-stacking"
            })

    # Matrix Devices, Programs, Autosofts
    matrix_devices = char_data.get("matrix_devices", {})
    commlinks = matrix_devices.get("commlinks", []) if isinstance(matrix_devices, dict) else _safe_item_list(char_data.get("commlinks", []))
    hosts = matrix_devices.get("hosts", []) if isinstance(matrix_devices, dict) else []

    programs = [_get_name(p) for p in _safe_item_list(char_data.get("programs", []))]
    autosofts = [_get_name(a) for a in _safe_item_list(char_data.get("autosofts", []))]
    gear = [_get_name(g) for g in _safe_item_list(char_data.get("gear", [])) + _safe_item_list(char_data.get("items", []))]

    # Contacts with explicit sorting fields
    raw_contacts = char_data.get("contacts", [])
    compiled_contacts = []
    for c in raw_contacts:
        if isinstance(c, dict):
            compiled_contacts.append({
                "name": c.get("name", "Contact"),
                "connection": c.get("connection", 1),
                "loyalty": c.get("loyalty", 1),
                "archetype": c.get("archetype", c.get("type", "Contact")),
                "favors": c.get("favors", c.get("favor_balance", 0)),
                "region": c.get("region", "Seattle / Global"),
                "description": c.get("description", c.get("notes", ""))
            })

    return {
        "identity": {
            "handle": handle,
            "real_name": real_name,
            "metatype": metatype,
            "role": role,
            "stream": stream,
            "tradition": tradition,
            "mortype": mortype,
            "gender": gender,
            "age": age,
            "nuyen": nuyen,
            "karma": karma_avail,
            "lifetime_karma": karma_life,
            "nanite_volume": nv,
            "is_ai": is_ai,
            "is_monad": is_monad
        },
        "attributes": {
            "body": bod,
            "agility": agi,
            "reaction": rea,
            "strength": str_val,
            "willpower": wil,
            "logic": log_val,
            "intuition": int_val,
            "charisma": cha,
            "edge": edg,
            "resonance": res,
            "magic": mag,
            "essence": ess
        },
        "attributes_list": attributes_list,
        "derived": {
            "composure": composure,
            "judge_intentions": judge_intentions,
            "memory": memory,
            "lift_carry": lift_carry,
            "physical_defense": phys_defense_pool,
            "defense_rating": total_dr,
            "physical_boxes": phys_boxes,
            "stun_boxes": stun_boxes
        },
        "matrix": {
            "asdf": asdf,
            "matrix_defense": mdef.get("pool", 0),
            "matrix_defense_hits": mdef.get("effective_hits", 0),
            "matrix_defense_breakdown": mdef.get("breakdown", ""),
            "matrix_initiative": matrix_init
        },
        "skills": compiled_skills,
        "qualities": {
            "positive": pos_qualities,
            "negative": neg_qualities
        },
        "weapons": compiled_weapons,
        "armors": compiled_armors,
        "vehicles": compiled_vehicles,
        "spells": spells,
        "adept_powers": adept_powers,
        "complex_forms": complex_forms,
        "sprite_powers": sprite_powers,
        "monad_abilities": monad_abilities,
        "augmentations": augmentations,
        "powers": {
            "complex_forms": complex_forms,
            "echoes": submersion_echoes,
            "sprite_powers": sprite_powers,
            "spells": spells,
            "adept_powers": adept_powers,
            "monad_abilities": monad_abilities,
            "augmentations": augmentations
        },
        "inventory": {
            "commlinks": commlinks,
            "hosts": hosts,
            "programs": programs,
            "autosofts": autosofts,
            "gear": gear
        },
        "contacts": compiled_contacts
    }
