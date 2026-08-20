"""
Modular Character Sheet & VTT Plain-Text Exporter for SR6.
Generates standardized, print-friendly text files:
  - Base Sheet (1 page: Identity, Financials/Karma, Attributes, Effective Table Dice Pools, Defenses)
  - Contacts Sheet (SRM Canonical Standards, Fixed Connection, Chronological Notes)
  - Combat & Weapons/Armor Sheet (Link-Fired Arrays, Firing Modes, Modifiers, Ballistics)
  - Inventory & Electronics Sheet (M-TOC II, Programs, Autosofts, Apps, Munitions, SINs)
  - Vehicles & Drones Sheet (Single-Line SR6 Abbreviations, Augmented Values, Inhabited Action Pools)
  - Powers, Spells & Complex Forms Sheet (SR6 Abbreviations: FV, P/S, Compact Echoes)
"""

import os
import re
import textwrap
from typing import Dict, Any, List, Optional
from sr6core.log_engine import get_log_totals
from sr6core.modifiers import ModifierEngine
from sr6core.vehicles import parse_vehicle_modifications, calculate_drone_action_pools

MAX_LINE_WIDTH = 76


def _wrap(text: str, width: int = MAX_LINE_WIDTH, initial_indent: str = "", subsequent_indent: str = "") -> List[str]:
    """Wraps text cleanly without exceeding MAX_LINE_WIDTH."""
    if not text:
        return []
    return textwrap.wrap(
        text,
        width=width,
        initial_indent=initial_indent,
        subsequent_indent=subsequent_indent,
        break_long_words=False,
        break_on_hyphens=False
    ) or [initial_indent + text]


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


def _get_name(item: Any, default: str = "") -> str:
    if isinstance(item, str):
        return item
    if isinstance(item, dict):
        return item.get("name") or item.get("ref") or item.get("id") or default
    return str(item)


def export_base_sheet(char_data: Dict[str, Any], char_repo_path: Optional[str] = None) -> str:
    """Generates the primary 1-page Base Character Sheet strictly within 76-character line bounds."""
    identity = char_data.get("identity", {})
    attrs = char_data.get("attributes", {})
    skills = char_data.get("skills", [])
    qualities = char_data.get("qualities", {})

    totals = get_log_totals(char_repo_path) if char_repo_path and os.path.exists(char_repo_path) else {}

    handle = identity.get("handle", "Unknown").upper() if isinstance(identity, dict) else "UNKNOWN"
    real_name = identity.get("real_name", "N/A") if isinstance(identity, dict) else "N/A"
    metatype = identity.get("metatype", "Human") if isinstance(identity, dict) else "Human"
    stream = identity.get("stream", "") if isinstance(identity, dict) else ""
    tradition = identity.get("tradition", identity.get("mortype", "")) if isinstance(identity, dict) else ""
    mortype = str(identity.get("mortype", "")).lower() if isinstance(identity, dict) else ""
    gender = identity.get("gender", "N/A") if isinstance(identity, dict) else "N/A"
    age = identity.get("age", "N/A") if isinstance(identity, dict) else "N/A"

    bod = int(attrs.get("body", 1)) if isinstance(attrs, dict) else 1
    agi = int(attrs.get("agility", 1)) if isinstance(attrs, dict) else 1
    rea = int(attrs.get("reaction", 1)) if isinstance(attrs, dict) else 1
    str_val = int(attrs.get("strength", 1)) if isinstance(attrs, dict) else 1
    wil = int(attrs.get("willpower", 1)) if isinstance(attrs, dict) else 1
    log_val = int(attrs.get("logic", 1)) if isinstance(attrs, dict) else 1
    int_val = int(attrs.get("intuition", 1)) if isinstance(attrs, dict) else 1
    cha = int(attrs.get("charisma", 1)) if isinstance(attrs, dict) else 1
    edg = int(attrs.get("edge", 1)) if isinstance(attrs, dict) else 1
    res = int(attrs.get("resonance", 0)) if isinstance(attrs, dict) else 0
    mag = int(attrs.get("magic", 0)) if isinstance(attrs, dict) else 0
    ess = float(attrs.get("essence", 6.0)) if isinstance(attrs, dict) else 6.0

    submersion = totals.get("Submersion_Grade", 0)
    initiation = totals.get("Initiation_Grade", 0)
    nuyen = totals.get("Nuyen", identity.get("nuyen", 4745))
    karma_avail = totals.get("Karma", identity.get("karma", 0))
    karma_life = totals.get("Lifetime_Karma", identity.get("total_karma", karma_avail))

    composure = wil + cha
    judge_intentions = int_val + wil
    memory = log_val + wil

    lines = []
    lines.append("=" * MAX_LINE_WIDTH)
    lines.append(f" SHADOWRUN 6E DOSSIER: {handle}")
    lines.append("=" * MAX_LINE_WIDTH)

    if res > 0:
        trad_str = f" ({stream})" if stream else ""
        lines.append(f" Real Name : {real_name:<18} | Metatype : {metatype}{trad_str}")
        lines.append(f" Submersion: Grade {submersion:<12} | Gender   : {gender} (Age: {age})")
        lines.append(f" Available Nuyen : {nuyen:,}¥ | Karma: {karma_avail} Pool ({karma_life} Lifetime)")
        lines.append("-" * MAX_LINE_WIDTH)

        asdf = ModifierEngine.get_living_persona_asdf(char_data)
        mdef = ModifierEngine.get_full_matrix_defense(char_data)
        matrix_init = ModifierEngine.get_matrix_initiative(char_data)

        att_str = asdf.get("attack", 7)
        slz_rea = asdf.get("sleaze", 9)
        dp_agi = asdf.get("data_processing", 7)
        fw_bod = asdf.get("firewall", 9)

        phys_boxes = 8 + ((fw_bod + 1) // 2)
        stun_boxes = 8 + ((wil + 1) // 2)

        lines.append(" ATTRIBUTES & DERIVED RATINGS:")
        lines.append(f"  ATT (STR): {att_str:<2} | SLZ (REA): {slz_rea:<2} | DP (AGI): {dp_agi:<2} | FW (BOD): {fw_bod:<2}")
        lines.append(f"  WIL: {wil:<2}       | LOG: {log_val:<2}       | INT: {int_val:<2}      | CHA: {cha:<2}")
        lines.append(f"  EDG: {edg:<2}       | RES: {res:<2}       | MAG: {mag:<2}      | ESS: {ess:<3.1f}")
        lines.append(f"  Derived Pools       : Composure [{composure}] | Judge Int [{judge_intentions}] | Memory [{memory}]")
        lines.append(f"  Condition Monitors  : Physical [{phys_boxes} boxes] | Stun [{stun_boxes} boxes]")
        lines.append("-" * MAX_LINE_WIDTH)
        lines.append(" LIVING PERSONA / MATRIX STATS:")
        lines.append(f"  ASDF Ratings        : A:{att_str} | S:{slz_rea} | D:{dp_agi} | F:{fw_bod}")
        
        mdef_line = f"  Full Matrix Defense : {mdef['pool']}d6 ({mdef['effective_hits']} Hits)"
        if len(mdef_line) + len(mdef['breakdown']) + 3 <= MAX_LINE_WIDTH:
            lines.append(f"{mdef_line} [{mdef['breakdown']}]")
        else:
            lines.append(mdef_line)
            lines.extend(_wrap(f"[{mdef['breakdown']}]", initial_indent="    ", subsequent_indent="    "))
            
        lines.append(f"  Matrix Initiative   : {matrix_init}")
    elif "monad" in mortype.lower() or "monad" in tradition.lower() or "monad" in str(identity.get("heritage", "")).lower():
        nv = int(identity.get("nanite_volume", 6))
        lines.append(f" Real Name : {real_name:<18} | Metatype : {metatype} (Monad)")
        lines.append(f" Status    : Monad Dual Identity  | Nanite Volume: NV {nv} (Age: {age})")
        lines.append(f" Available Nuyen : {nuyen:,}¥ | Karma: {karma_avail} Pool ({karma_life} Lifetime)")
        lines.append("-" * MAX_LINE_WIDTH)

        asdf = ModifierEngine.get_living_persona_asdf(char_data)
        mdef = ModifierEngine.get_full_matrix_defense(char_data)
        matrix_init = ModifierEngine.get_matrix_initiative(char_data)

        att_str = asdf.get("attack", 3)
        slz_rea = asdf.get("sleaze", 6)
        dp_agi = asdf.get("data_processing", 8)
        fw_bod = asdf.get("firewall", 8)

        # Monad Toughness adds NV/2 (3) to Condition Monitors
        phys_boxes = 8 + ((bod + 1) // 2) + (nv // 2)
        stun_boxes = 8 + ((wil + 1) // 2) + (nv // 2)

        lines.append(" ATTRIBUTES & DERIVED RATINGS:")
        lines.append(f"  BOD: {bod:<2}       | AGI: {agi:<2}       | REA: {rea:<2}      | STR: {str_val:<2}")
        lines.append(f"  WIL: {wil:<2}       | LOG: {log_val:<2}       | INT: {int_val:<2}      | CHA: {cha:<2}")
        lines.append(f"  EDG: {edg:<2}       | RES: {res:<2}       | MAG: {mag:<2}      | ESS: {ess:<3.1f}")
        lines.append(f"  Derived Pools       : Composure [{composure}] | Judge Int [{judge_intentions}] | Memory [{memory}]")
        lines.append(f"  Condition Monitors  : Physical [{phys_boxes} boxes] | Stun [{stun_boxes} boxes] (Monad Toughness)")
        lines.append("-" * MAX_LINE_WIDTH)
        lines.append(" MONAD LIVING PERSONA MATRIX STATS (Whisper Nets p. 149):")
        lines.append(f"  ASDF Ratings        : A:{att_str} | S:{slz_rea} | D:{dp_agi} | F:{fw_bod}")
        
        mdef_line = f"  Full Matrix Defense : {mdef['pool']}d6 ({mdef['effective_hits']} Hits)"
        if len(mdef_line) + len(mdef['breakdown']) + 3 <= MAX_LINE_WIDTH:
            lines.append(f"{mdef_line} [{mdef['breakdown']}]")
        else:
            lines.append(mdef_line)
            lines.extend(_wrap(f"[{mdef['breakdown']}]", initial_indent="    ", subsequent_indent="    "))
            
        lines.append(f"  Matrix Initiative   : {matrix_init}")
    else:
        trad_str = f" ({tradition})" if tradition else ""
        lines.append(f" Real Name : {real_name:<18} | Metatype : {metatype}{trad_str}")
        if mag > 0:
            lines.append(f" Initiation: Grade {initiation:<12} | Gender   : {gender} (Age: {age})")
        else:
            lines.append(f" Status    : Mundane             | Gender   : {gender} (Age: {age})")
        lines.append(f" Available Nuyen : {nuyen:,}¥ | Karma: {karma_avail} Pool ({karma_life} Lifetime)")
        lines.append("-" * MAX_LINE_WIDTH)

        phys_boxes = 8 + ((bod + 1) // 2)
        stun_boxes = 8 + ((wil + 1) // 2)

        lines.append(" ATTRIBUTES & DERIVED RATINGS:")
        lines.append(f"  BOD: {bod:<2}       | AGI: {agi:<2}       | REA: {rea:<2}      | STR: {str_val:<2}")
        lines.append(f"  WIL: {wil:<2}       | LOG: {log_val:<2}       | INT: {int_val:<2}      | CHA: {cha:<2}")
        lines.append(f"  EDG: {edg:<2}       | RES: {res:<2}       | MAG: {mag:<2}      | ESS: {ess:<3.1f}")
        lines.append(f"  Derived Pools       : Composure [{composure}] | Judge Int [{judge_intentions}] | Memory [{memory}]")
        lines.append(f"  Condition Monitors  : Physical [{phys_boxes} boxes] | Stun [{stun_boxes} boxes]")

        if mag > 0:
            lines.append("-" * MAX_LINE_WIDTH)
            lines.append(" MAGICAL TRADITION & PROTOCOLS:")
            lines.append(f"  Tradition           : {tradition or 'Hermetic / Shamanic'}")
            drain_pool = wil + cha
            drain_hits = drain_pool // 4
            lines.append(f"  Drain Resistance    : {drain_pool}d6 ({drain_hits} Hits) [WIL {wil} + CHA {cha} = {drain_pool}d6]")
            pp_val = attrs.get("power_points", 0)
            if pp_val:
                lines.append(f"  Adept Power Points  : {pp_val} PP")

    lines.append("-" * MAX_LINE_WIDTH)
    lines.append(" ACTIVE SKILLS & TABLE-RELEVANT DICE POOLS:")
    for s in skills:
        if isinstance(s, dict):
            s_name = s.get("name", "Skill")
            s_attr = s.get("attribute", "logic")
            s_rating = int(s.get("rating", 1))

            calc = ModifierEngine.calculate_skill_pool(
                char_data,
                skill_name=s_name,
                skill_rating=s_rating,
                linked_attribute=s_attr
            )
            s_line = f"  - {s_name:<20}: {calc['effective_pool']}d6  [{calc['breakdown']}]"
            lines.extend(_wrap(s_line, subsequent_indent="    "))
        elif isinstance(s, str):
            lines.extend(_wrap(f"  - {s}", subsequent_indent="    "))

    pos_raw = qualities.get("positive", []) if isinstance(qualities, dict) else []
    neg_raw = qualities.get("negative", []) if isinstance(qualities, dict) else []
    pos_q = [_get_name(q) for q in (pos_raw if isinstance(pos_raw, list) else [])]
    neg_q = [_get_name(q) for q in (neg_raw if isinstance(neg_raw, list) else [])]
    lines.append("-" * MAX_LINE_WIDTH)
    lines.append(" QUALITIES:")
    lines.extend(_wrap(f"  Positive: {', '.join(pos_q) if pos_q else 'None'}", subsequent_indent="    "))
    lines.extend(_wrap(f"  Negative: {', '.join(neg_q) if neg_q else 'None'}", subsequent_indent="    "))
    lines.append("=" * MAX_LINE_WIDTH)

    return "\n".join(lines)


def export_contacts_sheet(char_data: Dict[str, Any]) -> str:
    """Generates the Contacts Directory strictly within 76-character line bounds."""
    identity = char_data.get("identity", {})
    contacts = char_data.get("contacts", [])
    handle = identity.get("handle", "Unknown").upper() if isinstance(identity, dict) else "UNKNOWN"
    lines = []
    lines.append("=" * MAX_LINE_WIDTH)
    lines.append(f" CONTACTS DIRECTORY: {handle}")
    lines.append("=" * MAX_LINE_WIDTH)
    lines.extend(_wrap(" Note: Connection ratings for official SRM Canonical Contacts are fixed by the SRM Guide.", initial_indent=" ", subsequent_indent=" "))
    lines.append("-" * MAX_LINE_WIDTH)
    if not contacts:
        lines.append("  No recorded contacts in dossier.")
    else:
        for idx, c in enumerate(contacts, 1):
            if isinstance(c, dict):
                name = c.get("name", "Unknown Contact")
                conn = c.get("connection", 1)
                loy = c.get("loyalty", 1)
                arch = c.get("archetype", c.get("type", "Contact"))
                favors = c.get("favors", c.get("favor_balance", 0))
                desc = c.get("description", c.get("notes", "Character Creation"))
                reg = c.get("region", "")
                reg_str = f" [{reg}]" if reg else ""
                
                header_line = f" [{idx:02d}] {name.upper()} ({arch}){reg_str}"
                lines.extend(_wrap(header_line, subsequent_indent="      "))
                lines.append(f"      Connection: {conn} (Fixed) | Loyalty: {loy} | Active Favors: {favors}")
                lines.extend(_wrap(f"History / Changes: {desc}", initial_indent="      ", subsequent_indent="      "))
            else:
                lines.append(f" [{idx:02d}] {str(c).upper()}")
            lines.append("-" * MAX_LINE_WIDTH)
    return "\n".join(lines)


def export_combat_sheet(char_data: Dict[str, Any]) -> str:
    """Generates the Weapons, Armament Arrays & Ballistics Protection Sheet strictly within 76 columns."""
    identity = char_data.get("identity", {})
    handle = identity.get("handle", "Unknown").upper() if isinstance(identity, dict) else "UNKNOWN"
    
    raw_weapons = char_data.get("weapons", [])
    weapons = _safe_item_list(raw_weapons)

    raw_armors = char_data.get("armors", char_data.get("armor", []))
    armors = _safe_item_list(raw_armors)

    lines = []
    lines.append("=" * MAX_LINE_WIDTH)
    lines.append(f" COMBAT, WEAPON ARRAYS & BALLISTICS: {handle}")
    lines.append("=" * MAX_LINE_WIDTH)
    
    lines.append(" WEAPONS & TACTICAL ARRAYS:")
    if not weapons:
        lines.append("  No weapons listed in dossier.")
    else:
        for w in weapons:
            if isinstance(w, dict):
                name = w.get("name", w.get("ref", "Weapon")).upper()
                dmg = w.get("damage", w.get("dv", "N/A"))
                ar = w.get("attack_rating", w.get("ar", "-"))
                modes = w.get("mode", w.get("modes", "SS/SA"))
                ammo = w.get("ammo", "N/A")
                mods = w.get("accessories", w.get("modifications", []))
                notes = w.get("notes", "")

                lines.append(f"  * {name}")
                lines.append(f"    DV: {dmg:<4} | Modes: {modes:<6} | Ammo: {ammo:<6} | AR: {ar}")
                if mods:
                    lines.extend(_wrap(f"Accessories/Mods: {', '.join(str(m) for m in mods)}", initial_indent="    ", subsequent_indent="    "))
                if notes:
                    lines.extend(_wrap(f"Tactical Notes  : {notes}", initial_indent="    ", subsequent_indent="    "))
            else:
                lines.append(f"  * {str(w).upper()}")
            lines.append("-" * MAX_LINE_WIDTH)

    lines.append(" BALLISTIC ARMOR & DEFENSIVE PROTECTION:")
    if not armors:
        lines.append("  Standard Street Clothes (0 Defense Rating)")
    else:
        for a in armors:
            if isinstance(a, dict):
                name = a.get("name", a.get("ref", "Armor")).upper()
                dr = a.get("defense_rating", a.get("rating", 0))
                mods = a.get("modifications", [])
                lines.append(f"  * {name} (Defense Rating Bonus: +{dr})")
                if mods:
                    lines.extend(_wrap(f"Installed Modifications: {', '.join(str(m) for m in mods)}", initial_indent="    ", subsequent_indent="    "))
            else:
                lines.append(f"  * {str(a).upper()}")
            lines.append("-" * MAX_LINE_WIDTH)

    return "\n".join(lines)


def export_inventory_sheet(char_data: Dict[str, Any]) -> str:
    """Generates the Gear, Inventory, Programs, Autosofts & Electronics Sheet strictly within 76 columns."""
    identity = char_data.get("identity", {})
    handle = identity.get("handle", "Unknown").upper() if isinstance(identity, dict) else "UNKNOWN"
    
    matrix_devices = char_data.get("matrix_devices", {})
    commlinks = matrix_devices.get("commlinks", []) if isinstance(matrix_devices, dict) else []
    if not commlinks:
        commlinks = _safe_item_list(char_data.get("commlinks", []))
    hosts = matrix_devices.get("hosts", []) if isinstance(matrix_devices, dict) else []
    programs = _safe_item_list(char_data.get("programs", []))
    autosofts = _safe_item_list(char_data.get("autosofts", []))
    gear = _safe_item_list(char_data.get("gear", []))
    sins = _safe_item_list(char_data.get("sins", []))
    licenses = _safe_item_list(char_data.get("licenses", []))
    lifestyles = _safe_item_list(char_data.get("lifestyles", []))
    raw_activesofts = char_data.get("activesofts", [])
    activesofts = _safe_item_list(raw_activesofts)

    lines = []
    lines.append("=" * MAX_LINE_WIDTH)
    lines.append(f" INVENTORY, MATRIX HARDWARE & SOFTWARE: {handle}")
    lines.append("=" * MAX_LINE_WIDTH)
    
    lines.append(" TACTICAL OPERATING CENTERS & MATRIX DEVICES:")
    if commlinks:
        for c in commlinks:
            if isinstance(c, dict):
                c_str = f"  - Commlink: {c.get('name', 'Commlink')} (DR: {c.get('device_rating', 1)} | DP: {c.get('data_processing', 1)} | FW: {c.get('firewall', 1)})"
                lines.extend(_wrap(c_str, subsequent_indent="    "))
            else:
                lines.append(f"  - Commlink: {c}")
    if hosts:
        for h in hosts:
            if isinstance(h, dict):
                h_str = f"  - Framework Host: {h.get('name', 'Host')} (Rating {h.get('rating', 2)}, {h.get('scale', 'Micro')})"
                lines.extend(_wrap(h_str, subsequent_indent="    "))
                if h.get("notes"):
                    lines.extend(_wrap(f"Notes: {h.get('notes')}", initial_indent="    ", subsequent_indent="    "))
            else:
                lines.append(f"  - Host: {h}")

    lines.append("-" * MAX_LINE_WIDTH)
    lines.append(" SOFTWARE & PROGRAMS:")

    # 1. Skillwires Activesofts (Rating 6)
    if activesofts:
        act_names = []
        for a in activesofts:
            if isinstance(a, dict):
                n = a.get("name", "Activesoft")
                r = a.get("rating", 6)
                act_names.append(f"{n} R{r}" if f"R{r}" not in n else n)
            else:
                act_names.append(str(a))
        lines.extend(_wrap(f"  Activesofts: {', '.join(act_names)}", subsequent_indent="               "))

    # 2. Classify Programs (Basic, Hacking, Rigging)
    BASIC_SET = {"baby monitor", "browse", "configurator", "edit", "emulator", "encryption", "search", "signal scrubber", "toolbox", "virtual machine"}
    HACKING_SET = {"armor", "biofeedback", "biofeedback shield", "bootstrap", "cat's paw", "crash", "decryption", "defense pods", "defensive pods", "demolition", "directional shield", "directional shields", "exploit", "fork", "hitchhiker", "lockdown", "nexus protocol", "overclock", "paint", "swerve", "tar baby", "trace"}
    RIGGER_SET = {"smartsoft", "swarm", "encryption (rigger)"}

    basic_progs = []
    hacking_progs = []
    rigger_progs = []

    for p in programs:
        p_name = _get_name(p)
        p_lower = p_name.lower()
        p_cat = (p.get("category", "") if isinstance(p, dict) else "").lower()

        if p_cat == "basic" or p_lower in BASIC_SET:
            basic_progs.append(p_name)
        elif p_cat == "hacking" or p_lower in HACKING_SET:
            hacking_progs.append(p_name)
        elif p_cat in ["rigger", "rigging"] or p_lower in RIGGER_SET:
            rigger_progs.append(p_name)
        else:
            basic_progs.append(p_name)

    if basic_progs:
        lines.extend(_wrap(f"  Basic   : {', '.join(basic_progs)}", subsequent_indent="            "))
    if hacking_progs:
        lines.extend(_wrap(f"  Hacking : {', '.join(hacking_progs)}", subsequent_indent="            "))
    if rigger_progs:
        lines.extend(_wrap(f"  Rigging : {', '.join(rigger_progs)}", subsequent_indent="            "))

    # 3. Clean Autosofts (Strip redundant 'Autosoft' suffix)
    if autosofts:
        def clean_auto_name(a: Any) -> str:
            raw_n = _get_name(a)
            clean = re.sub(r"\s+autosoft\b", "", raw_n, flags=re.IGNORECASE).strip()
            rtg = a.get("rating") if isinstance(a, dict) else None
            if rtg and not re.search(r"\bR\d+\b", clean):
                clean = f"{clean} R{rtg}"
            return clean

        auto_names = [clean_auto_name(a) for a in autosofts]
        lines.extend(_wrap(f"  Autosoft: {', '.join(auto_names)}", subsequent_indent="            "))

    # 4. Commlink Programs & Apps
    APP_KEYWORDS = ["facial scanner", "p-ice spines", "personal assistant", "social hud", "thermal mood", "vocal tension", "lie detector", "map software", "fitness tracker", "app"]
    commlink_apps = []
    physical_gear = []

    for g in gear:
        g_name = _get_name(g, "Item")
        g_lower = g_name.lower()
        if any(kw in g_lower for kw in APP_KEYWORDS):
            commlink_apps.append(g_name)
        else:
            physical_gear.append(g)

    raw_apps = _safe_item_list(char_data.get("apps", char_data.get("commlink_apps", [])))
    for a in raw_apps:
        a_n = _get_name(a)
        if a_n not in commlink_apps:
            commlink_apps.append(a_n)

    if commlink_apps:
        lines.extend(_wrap(f"  Commlink: {', '.join(commlink_apps)}", subsequent_indent="            "))

    if not activesofts and not basic_progs and not hacking_progs and not autosofts and not commlink_apps:
        lines.append("  No specialized matrix programs or autosofts installed.")

    lines.append("-" * MAX_LINE_WIDTH)
    lines.append(" FIELD GEAR, MUNITIONS & AMMUNITION:")
    if physical_gear:
        for g in physical_gear:
            g_name = _get_name(g, "Item")
            qty = g.get("qty", g.get("quantity", 1)) if isinstance(g, dict) else 1
            lines.extend(_wrap(f"  - [Qty: {qty}] {g_name}", subsequent_indent="    "))
    else:
        lines.append("  Standard runner kit and survival provisions.")

    lines.append("-" * MAX_LINE_WIDTH)
    lines.append(" SINS, LICENSES & LIFESTYLES:")
    if sins:
        for s in sins:
            lines.extend(_wrap(f"  - SIN: {_get_name(s)} (Rating {s.get('rating', 1) if isinstance(s, dict) else 1})", subsequent_indent="    "))
    if licenses:
        for lic in licenses:
            lines.extend(_wrap(f"  - License: {_get_name(lic)}", subsequent_indent="    "))
    if lifestyles:
        for l in lifestyles:
            lines.extend(_wrap(f"  - Lifestyle: {_get_name(l)}", subsequent_indent="    "))

    lines.append("=" * MAX_LINE_WIDTH)
    return "\n".join(lines)


def export_vehicles_sheet(char_data: Dict[str, Any]) -> str:
    """Generates the Vehicles & Inhabited Drones Sheet strictly within 76-character line bounds."""
    identity = char_data.get("identity", {})
    handle = identity.get("handle", "Unknown").upper() if isinstance(identity, dict) else "UNKNOWN"
    
    raw_drones = char_data.get("drones", [])
    raw_vehicles = char_data.get("vehicles", [])
    
    drones = _safe_item_list(raw_drones)
    vehicles = _safe_item_list(raw_vehicles)

    lines = []
    lines.append("=" * MAX_LINE_WIDTH)
    lines.append(f" VEHICLES, DRONES & RIGGING DEPLOYMENTS: {handle}")
    lines.append("=" * MAX_LINE_WIDTH)

    if not drones and not vehicles:
        lines.append(" No vehicles or drones listed in dossier.")
        lines.append("=" * MAX_LINE_WIDTH)
        return "\n".join(lines)

    for item in vehicles + drones:
        if not isinstance(item, dict):
            continue
        v_name = item.get("name", "Vehicle / Drone").upper()
        v_role = item.get("role", "")
        v_header = f" * {v_name}" + (f" ({v_role})" if v_role else "")
        lines.append(v_header)

        # Standardized SR6 Abbreviations
        # HAN (Handling on/off), ACC (Accel on/off), TS (Top Speed), INT (Interval), BOD (Body), ARM (Armor), PIL (Pilot), SEN (Sensor), STS (Seats)
        han_on = item.get("handling_on", item.get("handling", 3))
        han_off = item.get("handling_off", han_on)
        acc_on = item.get("accel_on", item.get("accel", 10))
        acc_off = item.get("accel_off", acc_on)
        spd = item.get("speed", item.get("top_speed", 120))
        interval = item.get("interval", 15)
        bod = item.get("body", 1)
        arm = item.get("armor", 0)
        pil = item.get("pilot", 1)
        sen = item.get("sensor", 1)
        seats = item.get("seats", "-")

        stat_line = f"   HAN:{han_on}/{han_off} | ACC:{acc_on}/{acc_off} | SPD:{spd} (INT {interval}) | BOD:{bod} | ARM:{arm} | PIL:{pil} | SEN:{sen} | STS:{seats}"
        lines.append(stat_line)

        # Installed Modifications
        raw_mods = item.get("modifications", [])
        if raw_mods:
            mod_names = [str(m.get("name", m)) if isinstance(m, dict) else str(m) for m in raw_mods]
            lines.extend(_wrap(f"   Mods: {', '.join(mod_names)}", initial_indent="", subsequent_indent="         "))

        # Inhabited Action Pools
        pools = calculate_drone_action_pools(char_data, item)
        if pools:
            pool_parts = []
            for p_name in ["piloting", "gunnery", "evasion", "perception", "stealth"]:
                p_data = pools.get(p_name)
                if isinstance(p_data, dict):
                    p_short = p_name.replace("_", " ").title()
                    p_pool = p_data.get("pool", 0)
                    p_hits = p_pool // 4
                    pool_parts.append(f"{p_short} {p_pool}d6 ({p_hits}H)")
            if pool_parts:
                lines.extend(_wrap(f"   Rigged Action Pools: {' | '.join(pool_parts)}", initial_indent="", subsequent_indent="                        "))

        lines.append("-" * MAX_LINE_WIDTH)

    lines.append("=" * MAX_LINE_WIDTH)
    return "\n".join(lines)


def export_powers_sheet(char_data: Dict[str, Any]) -> str:
    """Generates the Powers, Spells, Complex Forms & Cyberware Sheet."""
    identity = char_data.get("identity", {})
    handle = identity.get("handle", "Unknown").upper() if isinstance(identity, dict) else "UNKNOWN"
    mortype = str(identity.get("mortype", "")).lower()

    cforms = _safe_item_list(char_data.get("complex_forms", []))
    echoes = _safe_item_list(char_data.get("submersion_echoes", char_data.get("metamagics", [])))
    spells = _safe_item_list(char_data.get("spells", []))
    adept = _safe_item_list(char_data.get("powers", char_data.get("adept_powers", [])))
    monad_abilities = _safe_item_list(char_data.get("monad_abilities", []))

    lines = []
    lines.append("=" * MAX_LINE_WIDTH)
    lines.append(f" POWERS, COMPLEX FORMS, ABILITIES & CYBERWARE: {handle}")
    lines.append("=" * MAX_LINE_WIDTH)

    if monad_abilities or "monad" in mortype:
        nv = identity.get("nanite_volume", 6)
        lines.append(f" MONAD ABILITIES & NANITE SWARM TRAITS (NV {nv}):")
        if monad_abilities:
            for ma in monad_abilities:
                if isinstance(ma, dict):
                    name = ma.get("name", "Ability")
                    effect = ma.get("effect", ma.get("notes", ""))
                    lines.append(f"  * {name}")
                    if effect:
                        lines.extend(_wrap(effect, initial_indent="    ", subsequent_indent="    "))
                else:
                    lines.append(f"  * {str(ma)}")
        else:
            lines.append("  * Monad Toughness (+3 Condition boxes, shifts wound penalties down by 1)")
            lines.append("  * Physical Attribute Boost (Minor Action; Simple NV test to boost BOD/AGI/REA/STR)")
            lines.append("  * Mental Attribute Boost (Minor Action; Simple NV test to boost WIL/LOG/INT/CHA)")
            lines.append("  * Monad Matrix Attributes (NV 6 allocated to Living Persona ASDF)")
            lines.append("  * Rapid Healing (Cellular nanite damage repair)")
            lines.append("  * Tech Infestation (Physical nanite electronics & hardware override)")
            lines.append("  * Adrenal Control (WIL + NV test to remain conscious)")
            lines.append("  * Resculpt (INT + Con test, 1 combat round appearance alteration)")
        lines.append("-" * MAX_LINE_WIDTH)

    if cforms:
        lines.append(" COMPLEX FORMS:")
        lines.extend(_wrap("  Abbreviations: FV (Fading Value), Dur (Duration: P=Perm, S=Sust, I=Inst)", subsequent_indent="  "))
        for cf in cforms:
            if isinstance(cf, dict):
                name = cf.get("name", cf.get("ref", "Complex Form"))
                fad = cf.get("fading", cf.get("fv", 0))
                raw_dur = str(cf.get("duration", "Instant")).lower()
                dur = "P" if "perm" in raw_dur else ("S" if "sust" in raw_dur else "I")
                lines.append(f"  - {name:<26} | FV: {fad:<2} | Dur: {dur}")
            else:
                lines.append(f"  - {str(cf)}")
        lines.append("-" * MAX_LINE_WIDTH)

    if echoes:
        lines.append(" SUBMERSION ECHOES / METAMAGIC:")
        echo_names = [_get_name(me) for me in echoes]
        for i in range(0, len(echo_names), 2):
            e1 = echo_names[i]
            e2 = echo_names[i+1] if i+1 < len(echo_names) else ""
            lines.append(f"  - {e1:<32} {('| ' + e2) if e2 else ''}")
        lines.append("-" * MAX_LINE_WIDTH)

    if spells:
        lines.append(" SPELLS & SORCERY:")
        for sp in spells:
            if isinstance(sp, dict):
                name = sp.get("name", sp.get("ref", "Spell"))
                drn = sp.get("drain", 0)
                lines.append(f"  - {name:<26} | Drain: {drn}")
            else:
                lines.append(f"  - {str(sp)}")
        lines.append("-" * MAX_LINE_WIDTH)

    if adept:
        lines.append(" ADEPT POWERS:")
        for ap in adept:
            if isinstance(ap, dict):
                name = ap.get("name", ap.get("ref", "Power"))
                cost = ap.get("cost", 0)
                lines.append(f"  - {name:<26} | Cost: {cost} PP")
            else:
                lines.append(f"  - {str(ap)}")
        lines.append("-" * MAX_LINE_WIDTH)

    # Augmentations (Cyberware & Bioware)
    augmentations = _safe_item_list(char_data.get("cyberware")) + _safe_item_list(char_data.get("bioware")) + _safe_item_list(char_data.get("augmentations"))
    if augmentations:
        lines.append(" CYBERWARE & BIOWARE AUGMENTATIONS:")
        for aug in augmentations:
            if isinstance(aug, dict):
                name = aug.get("name", aug.get("ref", "Augmentation"))
                rating = aug.get("rating", "")
                grade = aug.get("grade", "")
                r_str = f" R{rating}" if rating else ""
                g_str = f" [{grade.title()} Grade]" if grade else ""
                lines.append(f"  - {name + r_str:<30} {g_str}")
            else:
                lines.append(f"  - {str(aug)}")
        lines.append("-" * MAX_LINE_WIDTH)

    return "\n".join(lines)


def export_vtt_text(char_data: Dict[str, Any]) -> str:
    """Backwards-compatible default plain-text export (returns Base Sheet)."""
    return export_base_sheet(char_data)


def export_modular_text_sheets(char_data: Dict[str, Any], char_id: str, char_repo_path: Optional[str] = None) -> Dict[str, str]:
    """Generates all modular character sub-sheets as a dictionary of filename -> content."""
    return {
        f"{char_id}_base.txt": export_base_sheet(char_data, char_repo_path=char_repo_path),
        f"{char_id}_contacts.txt": export_contacts_sheet(char_data),
        f"{char_id}_combat.txt": export_combat_sheet(char_data),
        f"{char_id}_inventory.txt": export_inventory_sheet(char_data),
        f"{char_id}_vehicles.txt": export_vehicles_sheet(char_data),
        f"{char_id}_powers.txt": export_powers_sheet(char_data),
    }
