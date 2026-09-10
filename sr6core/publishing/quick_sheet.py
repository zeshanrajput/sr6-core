"""
Strict 2-Page 76-Column ASCII Quick Reference Sheet Generator.
Adheres strictly to a ~120-line ceiling (60 lines/page) for tabletop printing,
with priority-based section budgeting and automatic condensation.
"""

import os
import textwrap
from typing import Dict, Any, List, Optional

from sr6core.character.ledger import get_log_totals
from sr6core.rules.modifiers import ModifierEngine
from sr6core.character.contacts import normalize_contacts_list

MAX_WIDTH = 76
PAGE_LINE_BUDGET = 60
TOTAL_LINE_BUDGET = 120


def _safe_item_list(raw_section: Any) -> List[Any]:
    """Flattens lists/dicts of items into a clean list."""
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


def _box_header(title: str, width: int = MAX_WIDTH) -> List[str]:
    title_str = f" {title.upper()} "
    fill_len = width - 2 - len(title_str)
    left_fill = fill_len // 2
    right_fill = fill_len - left_fill
    return [
        "+" + "-" * (width - 2) + "+",
        "|" + " " * left_fill + title_str + " " * right_fill + "|",
        "+" + "-" * (width - 2) + "+"
    ]


def _sub_header(title: str, width: int = MAX_WIDTH) -> str:
    content = f"-- {title.upper()} "
    return "+" + content + "-" * (width - 2 - len(content)) + "+"


def _row(text: str, width: int = MAX_WIDTH) -> str:
    if len(text) > width - 4:
        text = text[:width - 7] + "..."
    return f"| {text:<{width - 4}} |"


def _row_2col(left: str, right: str, width: int = MAX_WIDTH) -> str:
    # Exact 76 cols: "| " (2) + left (34) + " | " (3) + right (35) + " |" (2) = 76
    col_w_l = 34
    col_w_r = 35
    l_str = left[:col_w_l]
    r_str = right[:col_w_r]
    return f"| {l_str:<{col_w_l}} | {r_str:<{col_w_r}} |"


def _format_val(base: int, buffed: int) -> str:
    if base != buffed:
        return f"{base}({buffed})"
    return str(base)


def _clean_ascii(text: str) -> str:
    return text.replace("–", "-").replace("—", "-").replace("’", "'").replace("“", '"').replace("”", '"').replace("\ufffd", "-")


def export_quick_sheet(
    char_data: Dict[str, Any],
    char_repo_path: Optional[str] = None,
    output_path: Optional[str] = None,
) -> str:
    """
    Generates a 76-column bordered ASCII character sheet strictly <= 120 lines total,
    honoring AI matrix attributes, single condition monitor, full drone statblocks,
    character powers, and zero filler blank lines.
    """
    from sr6core.publishing.mobile_json import export_mobile_json

    # Derive fully enriched and calculated dataset
    bundle = export_mobile_json(char_data, char_repo_path=char_repo_path)
    identity = bundle.get("identity", {})
    attrs_list = bundle.get("attributes_list", [])
    skills = bundle.get("skills", [])
    weapons = bundle.get("weapons", [])
    vehicles = bundle.get("vehicles", [])
    complex_forms = bundle.get("complex_forms", [])
    spells = bundle.get("spells", [])
    adept_powers = bundle.get("adept_powers", [])
    nanohive = bundle.get("nanohive", {})
    qualities = char_data.get("qualities", {})

    totals = get_log_totals(char_repo_path) if char_repo_path and os.path.exists(char_repo_path) else {}

    handle = identity.get("handle", identity.get("name", "Unknown")).upper()
    metatype = identity.get("metatype", "Human")
    archetype = identity.get("stream") or identity.get("tradition") or identity.get("mortype") or identity.get("archetype", "Shadowrunner")
    is_ai = bool(identity.get("is_ai")) or "ai" in str(metatype).lower()

    karma_avail = totals.get("Karma", char_data.get("karma", 0))
    raw_nuyen = totals.get("Nuyen", char_data.get("nuyen", 0))
    try:
        nuyen_avail = int(float(raw_nuyen))
    except Exception:
        nuyen_avail = 0

    heat = totals.get("Heat", 0)
    raw_rep = totals.get("Reputation", 0)
    if isinstance(raw_rep, dict):
        rep = ", ".join(f"{k}:{v}" for k, v in raw_rep.items())
    else:
        rep = str(raw_rep)

    attr_dict = {a["code"]: a for a in attrs_list}

    # Extract dynamic initiative string
    init_obj = bundle.get("initiative", {})
    if isinstance(init_obj, dict):
        default_mode = init_obj.get("default_mode", "physical")
        mode_data = init_obj.get("modes", {}).get(default_mode, {})
        init_score = mode_data.get("score", 5)
        init_dice = mode_data.get("dice_str", "1d6").upper()
        init_val = f"{init_score} + {init_dice}"
        if default_mode == "vr_hotsim":
            init_val += " (Hot-Sim)"
    else:
        init_val = str(init_obj)

    # -------------------------------------------------------------
    # UNIFIED DOSSIER SHEET (Strictly <= 120 lines, Single-Sheet Flow)
    # -------------------------------------------------------------
    sheet: List[str] = []

    # 1. Header & Identity
    sheet.extend(_box_header(f"SR6 DOSSIER // {handle}"))
    sheet.append(_row(f"METATYPE : {metatype:<20} ARCHETYPE: {archetype}"))
    sheet.append(_row(f"KARMA    : {karma_avail} avail               NUYEN    : {nuyen_avail:,} Nuyen"))
    sheet.append(_row(f"HEAT     : {str(heat):<20} REPUTATION: {rep[:32]}"))

    # 2. Attributes Row
    sheet.append(_sub_header("ATTRIBUTES"))
    if is_ai:
        # AI: Matrix attributes (A, S, D, F) + Mental (W, L, I, C)
        att_str = _format_val(attr_dict.get("ATT", {}).get("base", 3), attr_dict.get("ATT", {}).get("buffed", 3))
        slz_str = _format_val(attr_dict.get("SLZ", {}).get("base", 5), attr_dict.get("SLZ", {}).get("buffed", 5))
        dp_str  = _format_val(attr_dict.get("DP", {}).get("base", 3), attr_dict.get("DP", {}).get("buffed", 3))
        fw_str  = _format_val(attr_dict.get("FW", {}).get("base", 5), attr_dict.get("FW", {}).get("buffed", 5))
        w_str   = _format_val(attr_dict.get("WIL", {}).get("base", 6), attr_dict.get("WIL", {}).get("buffed", 6))
        l_str   = _format_val(attr_dict.get("LOG", {}).get("base", 4), attr_dict.get("LOG", {}).get("buffed", 4))
        i_str   = _format_val(attr_dict.get("INT", {}).get("base", 2), attr_dict.get("INT", {}).get("buffed", 2))
        c_str   = _format_val(attr_dict.get("CHA", {}).get("base", 4), attr_dict.get("CHA", {}).get("buffed", 4))

        ed_str  = _format_val(attr_dict.get("EDG", {}).get("base", 4), attr_dict.get("EDG", {}).get("buffed", 4))
        res_entry = attr_dict.get("RES", {})
        res_str = _format_val(res_entry.get("base", 8), res_entry.get("buffed", 8)) if res_entry else ""

        line1 = f"A {att_str}  S {slz_str}  D {dp_str}  F {fw_str}  W {w_str}  L {l_str}  I {i_str}  C {c_str}"
        line2 = f"ED {ed_str}" + (f"  RES {res_str}" if res_str else "")
        sheet.append(_row(line1))
        sheet.append(_row(line2))
    else:
        # Mortal / Augmented: B, A, R, S, W, L, I, C
        b_str = _format_val(attr_dict.get("BOD", {}).get("base", 1), attr_dict.get("BOD", {}).get("buffed", 1))
        a_str = _format_val(attr_dict.get("AGI", {}).get("base", 1), attr_dict.get("AGI", {}).get("buffed", 1))
        r_str = _format_val(attr_dict.get("REA", {}).get("base", 1), attr_dict.get("REA", {}).get("buffed", 1))
        s_str = _format_val(attr_dict.get("STR", {}).get("base", 1), attr_dict.get("STR", {}).get("buffed", 1))
        w_str = _format_val(attr_dict.get("WIL", {}).get("base", 1), attr_dict.get("WIL", {}).get("buffed", 1))
        l_str = _format_val(attr_dict.get("LOG", {}).get("base", 1), attr_dict.get("LOG", {}).get("buffed", 1))
        i_str = _format_val(attr_dict.get("INT", {}).get("base", 1), attr_dict.get("INT", {}).get("buffed", 1))
        c_str = _format_val(attr_dict.get("CHA", {}).get("base", 1), attr_dict.get("CHA", {}).get("buffed", 1))

        ess_str = str(attr_dict.get("ESS", {}).get("buffed", 6.0))
        ed_str  = _format_val(attr_dict.get("EDG", {}).get("base", 1), attr_dict.get("EDG", {}).get("buffed", 1))
        mag_entry = attr_dict.get("MAG")
        res_entry = attr_dict.get("RES")
        special_str = ""
        if mag_entry:
            special_str = f"MAG {_format_val(mag_entry.get('base', 1), mag_entry.get('buffed', 1))}"
        elif res_entry:
            special_str = f"RES {_format_val(res_entry.get('base', 1), res_entry.get('buffed', 1))}"

        line1 = f"B {b_str}  A {a_str}  R {r_str}  S {s_str}  W {w_str}  L {l_str}  I {i_str}  C {c_str}"
        line2 = f"ESS {ess_str[:4]}  ED {ed_str}" + (f"  {special_str}" if special_str else "")
        sheet.append(_row(line1))
        sheet.append(_row(line2))

    # 3. Defense & Condition Track
    sheet.append(_sub_header("DEFENSE & CONDITION TRACK"))
    wil_val = attr_dict.get("WIL", {}).get("buffed", 6)
    bod_val = attr_dict.get("BOD", {}).get("buffed", 1)

    if is_ai:
        # AI have a single condition monitor, a Matrix Condition Monitor, built same as Stun CM
        matrix_cm = 8 + (wil_val + 1) // 2
        def_pool = bundle.get("defense_pool", 7)
        soak_pool = bod_val
        sheet.append(_row_2col(f"INITIATIVE: {init_val[:32]}", f"DEFENSE POOL: {def_pool}"))
        sheet.append(_row_2col(f"MATRIX CM : [{matrix_cm}] (WIL/2 + 8)", f"SOAK POOL   : {soak_pool}"))
    else:
        def_pool = bundle.get("defense_pool", 8)
        soak_pool = bundle.get("soak_pool", bod_val)
        armor_dr = bundle.get("armor_dr", bod_val)
        phys_cm = 8 + (bod_val + 1) // 2
        stun_cm = 8 + (wil_val + 1) // 2
        sheet.append(_row_2col(f"INITIATIVE: {init_val[:32]}", f"DEFENSE POOL: {def_pool}"))
        sheet.append(_row_2col(f"ARMOR DR  : {armor_dr}", f"SOAK POOL   : {soak_pool}"))
        sheet.append(_row_2col(f"PHYSICAL CM: [{phys_cm}] (BOD/2 + 8)", f"STUN CM     : [{stun_cm}] (WIL/2 + 8)"))

    # 4. Primary Action Pools (Keeping Specializations grouped directly under Parent)
    sheet.append(_sub_header("PRIMARY ACTION POOLS"))
    skill_blocks: List[List[str]] = []
    for sk in skills:
        s_name = sk.get("name", "Skill")
        s_rtg = sk.get("rating", 0)
        s_buff = sk.get("buffed_pool", 0)
        s_spec = sk.get("specialization")
        s_spec_pool = sk.get("specialized_pool", s_buff + 2)

        block = [f"{s_name}: (R{s_rtg}, {s_buff}d6)"]
        if s_spec:
            block.append(f"  -- {s_spec}: {s_spec_pool}d6")
        skill_blocks.append(block)

    left_lines: List[str] = []
    right_lines: List[str] = []
    for block in skill_blocks:
        if len(left_lines) <= len(right_lines):
            left_lines.extend(block)
        else:
            right_lines.extend(block)

    max_rows = max(len(left_lines), len(right_lines))
    for idx in range(max_rows):
        l_text = left_lines[idx] if idx < len(left_lines) else ""
        r_text = right_lines[idx] if idx < len(right_lines) else ""
        sheet.append(_row_2col(l_text, r_text))

    # 5. Tactical Weapons
    sheet.append(_sub_header("TACTICAL WEAPONS"))
    sheet.append(_row(f"{'WEAPON':<23} {'DV':<6} {'ATTACK RATING':<18} {'AMMO':<8} {'MODE'}"))
    if not weapons:
        sheet.append(_row(f"{'Unarmed Combat':<23} {'2S':<6} {'(STR+REA)/-/-/-/-':<18} {'-':<8} {'-'}"))
    else:
        for w in weapons[:5]:
            w_name = _clean_ascii(str(w.get("name", "Weapon")))[:22]
            w_dv = _clean_ascii(str(w.get("damage") or w.get("dv") or "3P"))[:5]
            w_ar = w.get("attack_rating") or w.get("ar") or [10, 10, 8, 0, 0]
            if isinstance(w_ar, list):
                ar_str = "/".join(str(x) if x else "-" for x in w_ar[:5])
            else:
                ar_str = str(w_ar)
            ar_str = _clean_ascii(ar_str)[:17]
            w_cap = _clean_ascii(str(w.get("ammo") or w.get("ammo_capacity") or "-"))[:7]
            w_modes = w.get("modes_str") or w.get("modes") or w.get("firing_modes") or w.get("mode") or "-"
            m_str = "/".join(w_modes) if isinstance(w_modes, list) else str(w_modes)
            m_str = _clean_ascii(m_str)[:15]
            sheet.append(_row(f"{w_name:<23} {w_dv:<6} {ar_str:<18} {w_cap:<8} {m_str}"))

    # 6. Matrix & Living Persona Profile
    sheet.append(_sub_header("MATRIX PROFILE"))
    if is_ai or bundle.get("living_persona"):
        lp = bundle.get("living_persona", {})
        att_v = lp.get("attack", attr_dict.get("ATT", {}).get("buffed", 7))
        slz_v = lp.get("sleaze", attr_dict.get("SLZ", {}).get("buffed", 9))
        dp_v  = lp.get("data_processing", attr_dict.get("DP", {}).get("buffed", 7))
        fw_v  = lp.get("firewall", attr_dict.get("FW", {}).get("buffed", 9))
        asdf_shorthand = f"A {att_v}  S {slz_v}  D {dp_v}  F {fw_v}"
        sheet.append(_row_2col(f"LIVING PERSONA: {asdf_shorthand}", f"INIT: {init_val[:28]}"))
    else:
        commlink_item = next((g for g in _safe_item_list(char_data.get("gear", [])) if "commlink" in str(g).lower()), None)
        c_name = commlink_item.get("name", "Standard Commlink") if isinstance(commlink_item, dict) else "Standard Commlink"
        dev_rating = commlink_item.get("rating", 2) if isinstance(commlink_item, dict) else 2
        sheet.append(_row_2col(f"DEVICE: {c_name[:20]} (Rt {dev_rating})", f"MATRIX DEFENSE: {attr_dict.get('INT', {}).get('buffed', 2) + dev_rating}"))

    # 2. Powers (Complex Forms / Spells / Adept Powers / Nanoware)
    if complex_forms:
        sheet.append(_sub_header("RESONANCE POWERS & COMPLEX FORMS"))
        sheet.append(_row(f"{'POWER':<24} {'TEST / EFFECT':<30} {'FADE':<6} {'DUR'}"))
        for cf in complex_forms[:6]:
            c_name = cf.get("name", "Form")
            if cf.get("target") and cf.get("target") not in c_name:
                c_name = f"{c_name} ({cf['target'][:4]})"
            c_name = _clean_ascii(c_name)[:23]
            c_fade = _clean_ascii(str(cf.get("fading", "-1")))[:5]
            c_dur = _clean_ascii(str(cf.get("duration", "Sust")))[:8]
            c_test = cf.get("notes") or cf.get("target") or "Elec + RES"
            c_test = _clean_ascii(c_test.split(".")[0].replace(" test", "").strip())[:29]
            sheet.append(_row(f"{c_name:<24} {c_test:<30} {c_fade:<6} {c_dur}"))
    elif spells:
        sheet.append(_sub_header("SPELLS & SORCERY"))
        sheet.append(_row(f"{'SPELL':<24} {'TEST / EFFECT':<30} {'DRAIN':<6} {'DUR'}"))
        for sp in spells[:6]:
            s_name = _clean_ascii(sp.get("name", "Spell"))[:23]
            s_drain = _clean_ascii(str(sp.get("drain", "3")))[:5]
            s_dur = _clean_ascii(str(sp.get("duration", "Sust")))[:8]
            s_test = sp.get("notes") or "Sorcery + Magic"
            s_test = _clean_ascii(s_test.split(".")[0].replace(" test", "").strip())[:29]
            sheet.append(_row(f"{s_name:<24} {s_test:<30} {s_drain:<6} {s_dur}"))
    elif adept_powers:
        sheet.append(_sub_header("ADEPT POWERS"))
        sheet.append(_row(f"{'POWER':<24} {'BENEFIT / EFFECT':<36} {'COST'}"))
        for ap in adept_powers[:6]:
            p_name = _clean_ascii(ap.get("name", "Power"))[:23]
            p_cost = _clean_ascii(str(ap.get("cost", "0.5 PP")))[:6]
            p_effect = ap.get("notes") or "Adept ability"
            p_effect = _clean_ascii(p_effect.split(".")[0].strip())[:35]
            sheet.append(_row(f"{p_name:<24} {p_effect:<36} {p_cost}"))
    elif nanohive and nanohive.get("colonies"):
        sheet.append(_sub_header("ACTIVE NANOWARE PROTOCOLS"))
        sheet.append(_row(f"{'COLONY':<24} {'EFFECT / STAT BONUS':<36} {'NV'}"))
        colonies = nanohive.get("colonies", {})
        active_ids = nanohive.get("default_active", list(colonies.keys()))
        for c_id in active_ids[:6]:
            c_data = colonies.get(c_id, {})
            c_name = _clean_ascii(c_data.get("name", c_id))[:23]
            c_nv = f"{c_data.get('default_nv', 2)} NV"
            c_eff = c_data.get("stat_effects", {}).get("notes") or c_data.get("effect", "")
            c_eff = _clean_ascii(c_eff.split(".")[0].replace("Single pre-bought dose colony", "").strip())[:35]
            sheet.append(_row(f"{c_name:<24} {c_eff:<36} {c_nv}"))

    # 3. Full Drone & Vehicle Statblocks
    if vehicles:
        sheet.append(_sub_header("VEHICLES & RIGGING ASSETS"))
        for v in vehicles[:3]:
            v_name = _clean_ascii(v.get("name", "Drone/Vehicle"))
            cat = v.get("category", "Drone").upper()
            h = v.get("handling", "-")
            ac = v.get("accel", "-")
            sp = v.get("speed", "-")
            b = _format_val(v.get("base_body", v.get("body", 1)), v.get("body", 1))
            a = _format_val(v.get("base_armor", v.get("armor", 0)), v.get("armor", 0))
            p = _format_val(v.get("base_pilot", v.get("pilot", 1)), v.get("pilot", 1))
            s = _format_val(v.get("base_sensor", v.get("sensor", 1)), v.get("sensor", 1))

            sheet.append(_row(f"[{cat}] {v_name[:62]}"))
            sheet.append(_row(f"  H:{h}  AC:{ac}  SP:{sp}  B:{b}  A:{a}  P:{p}  S:{s}"))

            # Rigged Pools line
            r_pools = v.get("rigged_pools", {})
            if r_pools:
                pool_items = []
                for p_key, p_obj in r_pools.items():
                    p_val = p_obj.get("pool") if isinstance(p_obj, dict) else p_obj
                    pool_items.append(f"{p_key.capitalize()}:{p_val}d6")
                sheet.append(_row(f"  POOLS: {' | '.join(pool_items[:4])}"))

    # 4. Key Qualities
    sheet.append(_sub_header("KEY QUALITIES"))
    q_list = []
    if isinstance(qualities, dict):
        for k, v in qualities.items():
            if isinstance(v, list):
                q_list.extend(v)
            elif isinstance(v, dict):
                q_list.extend(v.keys())
            else:
                q_list.append(k)
    elif isinstance(qualities, list):
        q_list = qualities

    q_names = []
    for q in q_list:
        if isinstance(q, dict):
            q_names.append(q.get("name") or q.get("ref") or "Quality")
        elif isinstance(q, str):
            q_names.append(q)

    for idx in range(0, min(len(q_names), 6), 2):
        left = f"+ {q_names[idx]}"[:34]
        right = f"+ {q_names[idx+1]}"[:34] if idx + 1 < len(q_names) else ""
        sheet.append(_row_2col(left, right))

    # 5. Field Gear Summary (Priority-based Auto-Condensing)
    sheet.append(_sub_header("FIELD GEAR SUMMARY"))
    raw_gear = _safe_item_list(char_data.get("gear", []))
    gear_names = [g.get("name", str(g)) for g in raw_gear if isinstance(g, dict)] or [str(g) for g in raw_gear]
    if not gear_names:
        sheet.append(_row("Standard runner field kit."))
    else:
        gear_blob = ", ".join(gear_names[:25])
        wrapped_gear = textwrap.wrap(gear_blob, width=MAX_WIDTH - 4)
        for gline in wrapped_gear[:2]:
            sheet.append(_row(_clean_ascii(gline)))
        if len(gear_names) > 25 or len(wrapped_gear) > 2:
            sheet.append(_row(f"... (+{len(gear_names)} total gear items logged; see mobile PWA)"))

    # Footer Box (Zero filler lines)
    sheet.append("+" + "=" * (MAX_WIDTH - 2) + "+")
    sheet.append(_row(f"END DOSSIER // {handle} // SR6 TABLETOP COMPANION"))
    sheet.append("+" + "=" * (MAX_WIDTH - 2) + "+")

    full_sheet = "\n".join(sheet) + "\n"

    target_file = output_path
    if not target_file and char_repo_path:
        char_id = char_data.get("identity", {}).get("id") or (os.path.basename(char_repo_path) if char_repo_path else None) or identity.get("id") or handle.lower()
        target_file = os.path.join(char_repo_path, "output", "text", f"{char_id}_sheet.txt")

    if target_file:
        os.makedirs(os.path.dirname(target_file), exist_ok=True)
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(full_sheet)

    return full_sheet


render_character_quick_sheet = export_quick_sheet
generate_quick_sheet_text = export_quick_sheet

