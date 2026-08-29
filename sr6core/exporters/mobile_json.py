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
    base vs buffed pools, bought hits, and weapon/drone stat arrays.
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

    # Condition Monitors
    nv = int(identity.get("nanite_volume", 0))
    monad_toughness = (nv // 2) if ("monad" in mortype or nv > 0) else 0
    phys_boxes = 8 + ((bod + 1) // 2) + monad_toughness
    stun_boxes = 8 + ((wil + 1) // 2) + monad_toughness

    # Derived Pools
    composure = wil + cha
    judge_intentions = wil + int_val
    memory = wil + log_val
    lift_carry = bod + str_val

    # Living Persona ASDF / Defenses
    asdf = ModifierEngine.get_living_persona_asdf(char_data)
    mdef = ModifierEngine.get_full_matrix_defense(char_data)
    matrix_init = ModifierEngine.get_matrix_initiative(char_data)

    # Physical Defense Rating and Defense Pool
    phys_defense_pool = rea + int_val

    # Skills compilation with base vs buffed pools
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
        effective_pool = calc["effective_pool"]
        # Add specialization bonus to effective pool if present
        if s_spec:
            effective_pool += 2

        bought_hits = effective_pool // 4

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
                "source": f"Specialization ({s_spec})",
                "type": "specialization",
                "value": 2,
                "target": "action",
                "active": True
            })

        compiled_skills.append({
            "name": s_name,
            "id": s.get("id", s_name.lower().replace(" ", "_")),
            "rating": s_rating,
            "attribute": s_attr,
            "specialization": s_spec,
            "base_pool": base_pool,
            "buffed_pool": effective_pool,
            "bought_hits": bought_hits,
            "effective_attribute": calc.get("effective_attribute", s_attr),
            "is_attribute_overridden": calc.get("is_attribute_overridden", False),
            "breakdown_text": calc.get("breakdown", f"{s_attr[:3].upper()} + {s_rating} Rtg"),
            "buffs": buff_list
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

    # Weapons
    raw_weapons = _safe_item_list(char_data.get("weapons", []))
    compiled_weapons = []
    for w in raw_weapons:
        if isinstance(w, dict):
            w_name = w.get("name", w.get("ref", "Weapon"))
            dmg = w.get("damage", w.get("dv", "3P"))
            ar = w.get("attack_rating", w.get("ar", [10, 10, 8, 0, 0]))
            modes = w.get("mode", w.get("modes", "SA"))
            ammo = w.get("ammo", "—")
            mods = w.get("accessories", w.get("modifications", []))
            loaded_ammo = w.get("loaded_ammo") or w.get("ammo_type")
            notes = w.get("notes", "")

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
                except Exception:
                    pass

            # Calculate modified weapon stats if available
            try:
                from sr6core.models import WeaponStatBlock
                from sr6core.vault.statblock_parser import calculate_modified_weapon
                raw_ar_val = ar if isinstance(ar, list) else ([int(x.strip()) if x.strip().isdigit() else 0 for x in str(ar).split("/")] if "/" in str(ar) else [10, 10, 8, 0, 0])
                base_w = WeaponStatBlock(
                    name=w_name,
                    category=str(w.get("category", "General")),
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

            ar_str = " / ".join([str(x) if (x is not None and x > 0) else "—" for x in (ar if isinstance(ar, list) else [ar])])

            compiled_weapons.append({
                "name": w_name,
                "damage": dmg,
                "attack_rating": ar if isinstance(ar, list) else [ar],
                "attack_rating_str": ar_str,
                "modes": modes if isinstance(modes, list) else str(modes).split("/"),
                "modes_str": str(modes),
                "ammo": str(ammo),
                "loaded_ammo": loaded_ammo,
                "accessories": [str(m.get("name", m)) if isinstance(m, dict) else str(m) for m in mods],
                "notes": notes
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

    # Drones and Vehicles with Inhabited Action Pools
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
            "handling": f"{han_on}/{han_off}",
            "accel": f"{acc_on}/{acc_off}",
            "speed": spd,
            "interval": interval,
            "body": v_bod,
            "armor": v_arm,
            "pilot": pil,
            "sensor": sen,
            "seats": seats,
            "modifications": mods,
            "rigged_pools": formatted_pools
        })

    # Complex Forms, Spells, Adept Powers, Echoes, Monad Abilities
    complex_forms = []
    for cf in _safe_item_list(char_data.get("complex_forms", [])):
        if isinstance(cf, dict):
            complex_forms.append({
                "name": cf.get("name", cf.get("ref", "Complex Form")),
                "fading": cf.get("fading", cf.get("fv", 0)),
                "duration": cf.get("duration", "Instant"),
                "target": cf.get("target", "Device/Persona")
            })

    submersion_echoes = []
    for echo in _safe_item_list(char_data.get("meta_echoes", char_data.get("submersion_echoes", char_data.get("metamagics", [])))):
        submersion_echoes.append(_get_name(echo))

    spells = []
    for sp in _safe_item_list(char_data.get("spells", [])):
        if isinstance(sp, dict):
            spells.append({
                "name": sp.get("name", sp.get("ref", "Spell")),
                "drain": sp.get("drain", 0),
                "type": sp.get("type", "Physical"),
                "range": sp.get("range", "LOS"),
                "duration": sp.get("duration", "Instant")
            })

    adept_powers = []
    for ap in _safe_item_list(char_data.get("powers", char_data.get("adept_powers", []))):
        if isinstance(ap, dict):
            adept_powers.append({
                "name": ap.get("name", ap.get("ref", "Power")),
                "cost": ap.get("cost", 0),
                "rating": ap.get("rating"),
                "notes": ap.get("notes", "")
            })

    monad_abilities = []
    for ma in _safe_item_list(char_data.get("monad_abilities", [])):
        if isinstance(ma, dict):
            monad_abilities.append({
                "name": ma.get("name", "Ability"),
                "effect": ma.get("effect", ma.get("notes", ""))
            })

    # Augmentations (Cyberware / Bioware)
    augmentations = []
    for aug in _safe_item_list(char_data.get("cyberware")) + _safe_item_list(char_data.get("bioware")) + _safe_item_list(char_data.get("augmentations")):
        if isinstance(aug, dict):
            augmentations.append({
                "name": aug.get("name", aug.get("ref", "Augmentation")),
                "rating": aug.get("rating"),
                "grade": aug.get("grade", "Standard"),
                "essence": aug.get("essence", 0)
            })

    # Matrix Devices, Programs, Autosofts
    matrix_devices = char_data.get("matrix_devices", {})
    commlinks = matrix_devices.get("commlinks", []) if isinstance(matrix_devices, dict) else _safe_item_list(char_data.get("commlinks", []))
    hosts = matrix_devices.get("hosts", []) if isinstance(matrix_devices, dict) else []

    programs = [_get_name(p) for p in _safe_item_list(char_data.get("programs", []))]
    autosofts = [_get_name(a) for a in _safe_item_list(char_data.get("autosofts", []))]
    gear = [_get_name(g) for g in _safe_item_list(char_data.get("gear", [])) + _safe_item_list(char_data.get("items", []))]

    # Contacts
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
                "region": c.get("region", ""),
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
            "nanite_volume": nv
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
        "powers": {
            "complex_forms": complex_forms,
            "echoes": submersion_echoes,
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
