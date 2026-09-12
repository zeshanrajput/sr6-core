"""
Quarto Campaign Session Log & Code Evaluator for SR6.
Parses campaign session logs, executes embedded Python blocks, and computes totals for Karma, Nuyen, Reputation, and Contacts.
Exposes standard Quarto tracking helpers so character logs can import sr6core.log_engine cleanly.
"""

import os
import re
import io
import textwrap
import contextlib
from typing import Dict, Any, List, Optional, Tuple, Union

from sr6core.character.contacts import (
    is_canonical_contact,
    get_canonical_contact,
    get_contact,
    parse_contact_types,
    infer_contact_types,
    search_contacts,
    format_contacts_table,
)
from sr6core.character.missions import get_mission, normalize_mission_code

CHARGEN_BASELINES: Dict[str, Dict[str, Any]] = {
    "reiko": {
        "Nuyen": 90000,
        "Karma": 1,
        "Submersion_Grade": 2,
        "Resonance": 6,
        "Heat": 0,
    },
    "velvet": {
        "Nuyen": 50000,
        "Karma": 0,
        "Initiation_Grade": 0,
        "Coven_Loyalty": 8,
        "Heat": 0,
    },
    "venn": {
        "Nuyen": 570,
        "Karma": 3,
        "Nanite_Volume": 6,
        "Total_Reputation": 0,
        "Heat": 0,
    }
}


def init_character(char_id: str) -> str:
    """
    Declares the active character for this Quarto log.
    If evaluating standalone, loads starting chargen resources/balances.
    If evaluated as part of a Trio (after character_purchases.qmd), preserves existing ledger balances.
    """
    global _GLOBAL_LOG_STATE
    cid = char_id.lower().strip()
    _GLOBAL_LOG_STATE["Character"] = cid

    baseline = CHARGEN_BASELINES.get(cid, {})
    if cid == "venn":
        _GLOBAL_LOG_STATE["Nuyen"] = baseline.get("Nuyen", 570)
        _GLOBAL_LOG_STATE["Lifetime_Nuyen"] = baseline.get("Nuyen", 570)
        _GLOBAL_LOG_STATE["Karma"] = baseline.get("Karma", 3)
        _GLOBAL_LOG_STATE["Lifetime_Karma"] = baseline.get("Karma", 3)
        _GLOBAL_LOG_STATE["Nanite_Volume"] = baseline.get("Nanite_Volume", 6)
    else:
        if _GLOBAL_LOG_STATE.get("Nuyen", 0) == 0:
            _GLOBAL_LOG_STATE["Nuyen"] = baseline.get("Nuyen", 0)
            _GLOBAL_LOG_STATE["Lifetime_Nuyen"] = baseline.get("Nuyen", 0)

        if "Karma" not in _GLOBAL_LOG_STATE or _GLOBAL_LOG_STATE.get("Karma", 0) == 0:
            _GLOBAL_LOG_STATE["Karma"] = baseline.get("Karma", 0)
            _GLOBAL_LOG_STATE["Lifetime_Karma"] = baseline.get("Karma", 0)

    for k, v in baseline.items():
        if k not in ["Nuyen", "Karma", "Lifetime_Nuyen", "Lifetime_Karma"]:
            _GLOBAL_LOG_STATE[k] = v

    return ""

# Global state dictionary for Quarto rendering scope
_GLOBAL_LOG_STATE: Dict[str, Any] = {
    "Karma": 0,
    "Lifetime_Karma": 0,
    "Nuyen": 0,
    "Lifetime_Nuyen": 0,
    "Heat": 0,
    "Resonance": 6,
    "Submersion_Grade": 0,
    "Initiation_Grade": 0,
    "Nanite_Volume": 0,
    "Reputation": {},
    "Sprites": [],
    "Spirits": [],
    "Contacts": {},
    "Missions": [],
    "Modifiers": [],
    "Spells": [],
    "Complex_Forms": [],
    "Adept_Powers": [],
    "Metamagic": [],
    "Echoes": [],
    "Knowledge_Skills": []
}

state = _GLOBAL_LOG_STATE


def reset_log_state():
    global _GLOBAL_LOG_STATE
    _GLOBAL_LOG_STATE.clear()
    _GLOBAL_LOG_STATE.update({
        "Karma": 0,
        "Lifetime_Karma": 0,
        "Nuyen": 0,
        "Lifetime_Nuyen": 0,
        "Heat": 0,
        "Resonance": 6,
        "Submersion_Grade": 0,
        "Initiation_Grade": 0,
        "Nanite_Volume": 0,
        "Reputation": {},
        "Sprites": [],
        "Spirits": [],
        "Contacts": {},
        "Missions": [],
        "Modifiers": [],
        "Spells": [],
        "Complex_Forms": [],
        "Adept_Powers": [],
        "Metamagic": [],
        "Echoes": [],
        "Knowledge_Skills": []
    })


def inc(resource: str, amount: Union[int, float]) -> str:
    global _GLOBAL_LOG_STATE
    raw_res = resource.strip()
    if raw_res in _GLOBAL_LOG_STATE:
        res = raw_res
    else:
        title_res = raw_res.title()
        res = title_res if title_res in _GLOBAL_LOG_STATE else raw_res
    current = _GLOBAL_LOG_STATE.get(res, 0)
    _GLOBAL_LOG_STATE[res] = current + amount
    if res == "Karma" and amount > 0:
        _GLOBAL_LOG_STATE["Lifetime_Karma"] = _GLOBAL_LOG_STATE.get("Lifetime_Karma", 0) + amount
    elif res == "Nuyen" and amount > 0:
        _GLOBAL_LOG_STATE["Lifetime_Nuyen"] = _GLOBAL_LOG_STATE.get("Lifetime_Nuyen", 0) + amount
    op = "+=" if amount >= 0 else "-="
    return f"{res} {op} {abs(amount)}"


def assign(name: str, value: Any) -> Any:
    global _GLOBAL_LOG_STATE
    _GLOBAL_LOG_STATE[name] = value
    return value


def initiate(echo_or_power: str = "", coven_loyalty: int = 0) -> str:
    """
    Calculates Initiation cost based on formula (10 + current_grade)
    minus Coven/Group Loyalty discount, increments Initiation_Grade by 1,
    and deducts Karma.
    """
    global _GLOBAL_LOG_STATE
    curr_grade = _GLOBAL_LOG_STATE.get("Initiation_Grade", 0)
    target_grade = curr_grade + 1
    base_cost = 10 + curr_grade
    final_cost = max(1, base_cost - coven_loyalty)
    _GLOBAL_LOG_STATE["Initiation_Grade"] = target_grade
    inc("Karma", -final_cost)
    return f"Initiation Grade {target_grade} ({echo_or_power}): -{final_cost} Karma"


def modifier(
    name: str,
    applies_to: str,
    value: Union[int, float, str],
    type: str = "teamwork",
    sub_skill: Optional[str] = None,
    rule_anchor: Optional[str] = None,
    notes: Optional[str] = None,
    enabled: bool = True
) -> str:
    """
    Registers a structured modifier in the Quarto evaluation scope.
    Allowed types:
      - 'teamwork': skills/activesofts/autosofts, capped at that skill's rating
      - 'augmentation': cyberware, bioware, magic, adept powers, drugs (+4 cap for attribute/skill)
      - 'skill bonus': adds bonus dice to all skill tests linked to that attribute (e.g. nanite neural amps/pattern reinforcement)
      - 'specialization': adds +2 to that skill in that sub-skill
      - 'expertise': adds +3 to that skill in that sub-skill
      - 'gear': items/gear providing specific situational or Edge benefits
      - 'other': weird things like adrenaline pumps, suprathyroid glands, wireless on skillwires
    """
    global _GLOBAL_LOG_STATE
    valid_type = type.lower().strip()
    if valid_type in ["skill bonus", "skill_bonus", "skill-bonus"]:
        valid_type = "skill bonus"
    elif valid_type not in ["teamwork", "augmentation", "specialization", "expertise", "other", "focus", "symbiosis", "gear", "attribute_substitution"]:
        valid_type = "other"

    val_num = int(value) if isinstance(value, (int, float)) or (isinstance(value, str) and value.lstrip("-+").isdigit()) else value

    mod_entry = {
        "id": name.lower().replace(" ", "_").replace("(", "").replace(")", "").replace("+", ""),
        "name": name,
        "target": applies_to.lower().strip(),
        "value": val_num,
        "type": valid_type,
        "sub_skill": sub_skill,
        "rule_anchor": rule_anchor,
        "notes": notes,
        "enabled": enabled
    }
    existing_mods = _GLOBAL_LOG_STATE.setdefault("Modifiers", [])
    for idx, em in enumerate(existing_mods):
        if em.get("id") == mod_entry["id"] and em.get("target") == mod_entry["target"]:
            existing_mods[idx] = mod_entry
            val_disp = f"+{val_num}" if isinstance(val_num, int) and val_num > 0 else f"{val_num}"
            return f"**{name}**: {applies_to} ({val_disp} [{valid_type}])"
    existing_mods.append(mod_entry)
    
    val_disp = f"+{val_num}" if isinstance(val_num, int) and val_num > 0 else f"{val_num}"
    return f"**{name}**: {applies_to} ({val_disp} [{valid_type}])"


def submerge(echo: str = "", group_loyalty: int = 0) -> str:
    """
    Calculates Submersion cost based on formula (10 + current_grade)
    minus Group Loyalty discount, increments Submersion_Grade by 1,
    and deducts Karma.
    """
    global _GLOBAL_LOG_STATE
    curr_grade = _GLOBAL_LOG_STATE.get("Submersion_Grade", 0)
    target_grade = curr_grade + 1
    base_cost = 10 + curr_grade
    final_cost = max(1, base_cost - group_loyalty)
    _GLOBAL_LOG_STATE["Submersion_Grade"] = target_grade
    if echo:
        _GLOBAL_LOG_STATE.setdefault("Echoes", []).append({
            "name": echo,
            "ref": echo.lower().replace(" ", "_"),
            "grade": target_grade
        })
    inc("Karma", -final_cost)
    return f"Submersion Grade {target_grade} ({echo}): -{final_cost} Karma"


def spell(
    name: str,
    category: str = "Combat",
    duration: str = "Instant",
    spell_type: str = "Physical",
    spell_range: str = "Line of Sight",
    drain: int = 3,
    notes: Optional[str] = None
) -> str:
    global _GLOBAL_LOG_STATE
    entry = {
        "name": name,
        "ref": name.lower().replace(" ", "_"),
        "category": category,
        "duration": duration,
        "type": spell_type,
        "range": spell_range,
        "drain": drain,
        "notes": notes or ""
    }
    _GLOBAL_LOG_STATE.setdefault("Spells", []).append(entry)
    return f"**Spell ({name})**: {category} [{duration}, {spell_type}, Drain {drain}]"


def complex_form(
    name: str,
    fading: int = 2,
    duration: str = "Immediate",
    target: str = "Device",
    notes: Optional[str] = None
) -> str:
    global _GLOBAL_LOG_STATE
    entry = {
        "name": name,
        "ref": name.lower().replace(" ", "_"),
        "fading": fading,
        "duration": duration,
        "target": target,
        "notes": notes or ""
    }
    _GLOBAL_LOG_STATE.setdefault("Complex_Forms", []).append(entry)
    return f"**Complex Form ({name})**: Fading {fading} [{duration}, Target: {target}]"


def adept_power(
    name: str,
    rating: int = 1,
    cost_pp: float = 1.0,
    action: str = "Passive",
    source: str = "natural",
    notes: Optional[str] = None
) -> str:
    global _GLOBAL_LOG_STATE
    entry = {
        "name": name,
        "ref": name.lower().replace(" ", "_"),
        "rating": rating,
        "cost": f"{cost_pp} PP",
        "cost_pp": cost_pp,
        "action": action,
        "source": source,
        "notes": notes or ""
    }
    _GLOBAL_LOG_STATE.setdefault("Adept_Powers", []).append(entry)
    return f"**Adept Power ({name} R{rating})**: {cost_pp} PP ({action})"


def metamagic(name: str, notes: Optional[str] = None) -> str:
    global _GLOBAL_LOG_STATE
    entry = {
        "name": name,
        "ref": name.lower().replace(" ", "_"),
        "notes": notes or ""
    }
    _GLOBAL_LOG_STATE.setdefault("Metamagic", []).append(entry)
    return f"**Metamagic ({name})**"


def echo(name: str, notes: Optional[str] = None) -> str:
    global _GLOBAL_LOG_STATE
    entry = {
        "name": name,
        "ref": name.lower().replace(" ", "_"),
        "notes": notes or ""
    }
    _GLOBAL_LOG_STATE.setdefault("Echoes", []).append(entry)
    return f"**Echo ({name})**"


def sprite_power(
    name: str,
    source: str = "Taz",
    power_type: str = "Sprite Power (Symbiosis)",
    target: Optional[str] = None,
    action: Optional[str] = None,
    effect: Optional[str] = None,
    origin: str = "native",
    doc_link: Optional[str] = None
) -> str:
    """
    Declares an active sprite power accessible via Sprite Symbiosis (e.g. from Taz).
    origin can be 'native' (inherent to sprite archetype) or 'added' (added during compilation).
    """
    global _GLOBAL_LOG_STATE
    entry = {
        "name": name,
        "source": source,
        "type": power_type,
        "target": target or "PAN / Matrix Icon",
        "action": action or "Minor Action",
        "effect": effect or "",
        "origin": origin,
        "doc_link": doc_link or "chapters/rules_sprites.html#sprite-symbiosis-powers"
    }
    _GLOBAL_LOG_STATE.setdefault("Sprite_Powers", []).append(entry)
    return f"**Sprite Power ({name})**: {power_type} via {source} [{origin.title()}]"


def monad_ability(
    name: str,
    effect: Optional[str] = None,
    action: str = "Minor Action",
    notes: Optional[str] = None,
    doc_link: Optional[str] = None
) -> str:
    global _GLOBAL_LOG_STATE
    entry = {
        "name": name,
        "ref": name.lower().replace(" ", "_"),
        "effect": effect or notes or "",
        "action": action,
        "notes": notes or effect or "",
        "doc_link": doc_link or "rules/rules_and_downtime.html#monad-nanite-boosts"
    }
    _GLOBAL_LOG_STATE.setdefault("Monad_Abilities", []).append(entry)
    return f"**Monad Ability ({name})**: {action} [{effect or notes or ''}]"


def knowledge_skill(name: str, rating: Optional[int] = None, notes: Optional[str] = None) -> str:
    global _GLOBAL_LOG_STATE
    entry = {
        "name": name,
        "rating": rating,
        "notes": notes or ""
    }
    _GLOBAL_LOG_STATE.setdefault("Knowledge_Skills", []).append(entry)
    rtg_str = f" R{rating}" if rating is not None else ""
    return f"**Knowledge Skill ({name}{rtg_str})**"


def language(name: str, rating: int = 4, notes: Optional[str] = None) -> str:
    """
    Languages are rated knowledge skills:
      - 1: Basic
      - 2: Specialist
      - 3: Expert
      - 4: Native
      - 5: Linguasoft
    """
    global _GLOBAL_LOG_STATE
    labels = {1: "Basic", 2: "Specialist", 3: "Expert", 4: "Native", 5: "Linguasoft"}
    level_label = labels.get(rating, f"Rating {rating}")
    entry = {
        "name": name,
        "rating": rating,
        "level": level_label,
        "is_native": rating == 4,
        "is_linguasoft": rating >= 5,
        "notes": notes or ""
    }
    _GLOBAL_LOG_STATE.setdefault("Knowledge_Skills", []).append(entry)
    return f"**Language ({name} - {level_label})**"



def inc_many(*args: Any) -> str:
    if len(args) == 1 and isinstance(args[0], (list, tuple)):
        pairs = args[0]
    elif len(args) > 0 and isinstance(args[0], (list, tuple)):
        pairs = args
    elif len(args) % 2 == 0 and all(isinstance(a, (str, int, float)) for a in args):
        pairs = [(args[i], args[i+1]) for i in range(0, len(args), 2)]
    else:
        pairs = args

    res = []
    for item in pairs:
        if isinstance(item, (list, tuple)) and len(item) == 2:
            r, a = item
            res.append(inc(r, a))
    return ", ".join(res)


def contact(
    name: str,
    fp: int = 0,
    loyalty: Optional[int] = None,
    connection: Optional[int] = None,
    type_name: str = "",
    region: str = "",
    types: Optional[Union[str, List[str]]] = None,
    notes: str = "",
    event: str = ""
) -> str:
    """
    Records or updates a campaign contact.
    - Master catalog (reference/contacts.yaml) automatically resolves connection, job, region, canonical status.
    - Canonical SRM contacts: Connection rating is locked.
    - Favor points accumulate, and Loyalty automatically increases when enough favor is accumulated.
    """
    global _GLOBAL_LOG_STATE
    name_clean = name.strip()
    c_reg = get_contact(name_clean)

    contacts = _GLOBAL_LOG_STATE["Contacts"]
    
    curr_m_idx = len(_GLOBAL_LOG_STATE.get("Missions", []))
    m_name = _GLOBAL_LOG_STATE["Missions"][-1] if curr_m_idx > 0 else "Character Creation"
    event_label = event or notes or m_name

    if c_reg:
        canonical_name = c_reg.get("name", name_clean)
        is_canon = c_reg.get("canonical", False)
        eff_conn = c_reg.get("connection", connection if connection is not None else 1)
        eff_type = type_name or c_reg.get("job", "")
        eff_region = region or c_reg.get("region", "GEN")
        if is_canon:
            eff_desc = c_reg.get("description", "") or notes
        else:
            eff_desc = notes or c_reg.get("description", "")
    else:
        canonical_name = name_clean
        is_canon = is_canonical_contact(name_clean)
        eff_conn = connection if connection is not None else 1
        eff_type = type_name
        eff_region = region if region else "GEN"
        eff_desc = notes

    if not eff_region:
        for prefix in ["SEA", "NOLA", "AMS", "KY", "DW", "HK", "GEN"]:
            if eff_type.startswith(prefix) or (notes and notes.startswith(prefix)):
                eff_region = prefix
                break

    # Parse and normalize contact types
    raw_types = types if types is not None else (c_reg.get("types") if c_reg else None)
    eff_types = parse_contact_types(raw_types)
    if not eff_types:
        eff_types = infer_contact_types(eff_type, eff_desc)

    is_first_encounter = canonical_name not in contacts
    promoted_levels = 0

    if is_first_encounter:
        eff_loyalty = loyalty if loyalty is not None else (1 if fp == 0 else 0)
        c_info = {
            "name": canonical_name,
            "canonical_name": canonical_name,
            "is_canonical": is_canon,
            "connection": eff_conn,
            "loyalty": eff_loyalty,
            "favors": fp,
            "type": eff_type,
            "region": eff_region or "GEN",
            "types": eff_types,
            "types_str": ", ".join(eff_types) if eff_types else "General",
            "description": eff_desc,
            "notes": eff_desc,
            "history": [f"{event_label} (Met: C{eff_conn} L{eff_loyalty}, +{fp} FP)" if fp else f"{event_label} (Met: C{eff_conn} L{eff_loyalty})"]
        }
        contacts[canonical_name] = c_info
    else:
        c_info = contacts[canonical_name]
        if eff_types and not c_info.get("types"):
            c_info["types"] = eff_types
            c_info["types_str"] = ", ".join(eff_types)
        
        # Connection: immutable for canonical contacts; can increase for non-canon
        if not is_canon and connection is not None and connection > c_info["connection"]:
            c_info["connection"] = connection
        
        if loyalty is not None and loyalty > c_info["loyalty"]:
            c_info["loyalty"] = loyalty

        if fp != 0:
            c_info["favors"] += fp
            
        hist_entry = f"{event_label} ({'+' if fp >= 0 else ''}{fp} FP)" if fp != 0 else event_label
        c_info["history"].append(hist_entry)

    old_loyalty = c_info["loyalty"]

    # Automatic Favor-to-Loyalty Upgrade:
    # Upgrading to Loyalty L+1 costs (L+1) Favor points (capped at Loyalty 6)
    while c_info["favors"] >= (c_info["loyalty"] + 1) and c_info["loyalty"] < 6:
        cost = c_info["loyalty"] + 1
        c_info["loyalty"] += 1
        c_info["favors"] -= cost
        promoted_levels += 1
        c_info["history"].append(f"Auto-Promoted to Loyalty {c_info['loyalty']} (-{cost} FP)")

    type_str = f" ({c_info['type']})" if c_info.get("type") else ""
    if is_first_encounter:
        if promoted_levels > 0:
            return f"**{canonical_name}**{type_str} [C:{c_info['connection']}] — Auto-Promoted to Loyalty {c_info['loyalty']}! ({c_info['favors']} FP banked)"
        elif fp > 0:
            return f"**{canonical_name}**{type_str} [C:{c_info['connection']} L:{c_info['loyalty']}] (+{fp} Favor)"
        else:
            return f"**{canonical_name}**{type_str} [C:{c_info['connection']} L:{c_info['loyalty']}]"
    else:
        if promoted_levels > 0:
            return f"**{canonical_name}** (+{fp} Favor → Auto-Promoted to Loyalty {c_info['loyalty']}! [{c_info['favors']} FP banked])"
        elif fp != 0:
            return f"**{canonical_name}** ({'+' if fp >= 0 else ''}{fp} Favor → {c_info['favors']} FP total, Loyalty {c_info['loyalty']})"
        else:
            return f"**{canonical_name}** [C:{c_info['connection']} L:{c_info['loyalty']}]"


def add_rep(faction: str, points: int) -> Dict[str, int]:
    global _GLOBAL_LOG_STATE
    rep = _GLOBAL_LOG_STATE["Reputation"]
    rep[faction] = rep.get(faction, 0) + points
    return rep


def mission(
    code_or_title: str,
    date: str = "",
    karma: int = 0,
    nuyen: int = 0,
    rep: Union[int, Dict[str, int]] = 0,
    heat: int = 0,
    bribe: int = 0,
    gm: str = "",
    difficulty: str = "",
    team: str = "",
    summary: str = "",
    expenses: int = 0
) -> str:
    """
    Consolidated mission runner.
    Resolves official metadata from reference/missions.yaml, increments Karma/Nuyen balances,
    applies regional reputation and post-run Heat/bribes, and registers session log entry.
    When date is provided, formats as an automatic H3 section banner.
    """
    global _GLOBAL_LOG_STATE
    m_info = get_mission(code_or_title)
    if m_info:
        code = m_info.get("id", code_or_title)
        title = m_info.get("title", code_or_title)
        region = m_info.get("region", "GEN")
    else:
        code = normalize_mission_code(code_or_title)
        title = code_or_title
        region = "GEN"

    _GLOBAL_LOG_STATE["Missions"].append(code)

    if karma != 0:
        inc("Karma", karma)
    if nuyen > 0:
        inc("Nuyen", nuyen)
    total_deductions = expenses + bribe
    if total_deductions > 0:
        inc("Nuyen", -total_deductions)

    net_heat = heat
    if bribe > 0:
        reduction = max(1, bribe // 1000)
        net_heat = max(0, net_heat - reduction)
    if net_heat != 0:
        inc("Heat", net_heat)

    if isinstance(rep, int) and rep != 0:
        add_rep(region, rep)
    elif isinstance(rep, dict):
        for r_faction, r_val in rep.items():
            add_rep(r_faction, r_val)

    session_entry = {
        "title": f"{code} | {title}" if code != title else title,
        "code": code,
        "date": date,
        "gm": gm,
        "difficulty": difficulty,
        "karma": karma,
        "nuyen": nuyen,
        "expenses": expenses + bribe,
        "bribe": bribe,
        "heat": net_heat,
        "reputation": rep,
        "summary": summary,
        "team": team
    }
    _GLOBAL_LOG_STATE.setdefault("Session_Logs", []).append(session_entry)

    parts = []
    if karma != 0:
        parts.append(f"{'+' if karma > 0 else ''}{karma} Karma")
    if nuyen != 0:
        parts.append(f"{'+' if nuyen > 0 else ''}{nuyen:,}¥")
    if rep:
        rep_val = rep if isinstance(rep, int) else sum(rep.values())
        parts.append(f"+{rep_val} Rep [{region}]")
    if bribe > 0:
        parts.append(f"-{bribe:,}¥ Bribe (Heat ±0)")
    elif net_heat > 0:
        parts.append(f"+{net_heat} Heat")
    if expenses > 0:
        parts.append(f"-{expenses:,}¥ Expenses")
    meta = []
    if gm:
        meta.append(f"GM: {gm}")
    if difficulty and difficulty.strip().lower() not in ["", "normal"]:
        meta.append(difficulty)
    meta_str = f"({' · '.join(meta)})" if meta else ""

    summary_str = ", ".join(parts)
    reward_str = f"*{summary_str}*" if summary_str else ""
    banner_parts = [p for p in [meta_str, reward_str] if p]
    banner = " — ".join(banner_parts)

    if date:
        heading = f"### {date} | {code}: {title}"
        return f"{heading}\n\n{banner}" if banner else heading
    else:
        suffix = f" — {banner}" if banner else ""
        return f"**{code}: {title}**{suffix}"


def start_mission(code: str) -> str:
    global _GLOBAL_LOG_STATE
    _GLOBAL_LOG_STATE["Missions"].append(code)
    return ""


def work_for_the_people(count: int = 1, nuyen_cost: int = 2000, funded: bool = False) -> str:
    """SRM Downtime: Trade 2,000¥ for 1 Karma per count (or 0¥ if funded by Hooder)."""
    cost = 0 if funded else nuyen_cost * count
    inc("Karma", count)
    if cost != 0:
        inc("Nuyen", -cost)
        return f"Working for the People ({count}x): +{count} Karma, -{cost:,}¥"
    return f"Working for the People ({count}x): +{count} Karma (Funded by Hooder)"


def work_for_the_man(count: int = 1) -> str:
    """SRM Downtime: Trade 1 Karma for 2,000¥ per count."""
    inc("Karma", -count)
    inc("Nuyen", 2000 * count)
    return f"Working for the Man ({count}x): +{2000 * count:,}¥, -{count} Karma"


def bribe(amount: int = 1000, heat_reduced: int = 1) -> str:
    """SRM Post-Run: Bribe authorities to negate Heat."""
    inc("Nuyen", -amount)
    curr_heat = _GLOBAL_LOG_STATE.get("Heat", 0)
    _GLOBAL_LOG_STATE["Heat"] = max(0, curr_heat - heat_reduced)
    return f"Bribe: -{amount:,}¥ (Heat -{heat_reduced})"


LIFESTYLE_RATES = {
    "Street": 0,
    "Squatter": 500,
    "Low": 2000,
    "Middle": 5000,
    "High": 10000,
    "Luxury": 100000
}


def lifestyle(level: str = "High", cost: Optional[int] = None, waived: bool = False, notes: str = "") -> str:
    """Tracks SRM bi-monthly lifestyle rent payment."""
    if waived:
        desc = f" ({notes})" if notes else ""
        return f"Lifestyle [{level}]: Waived{desc}"
    
    actual_cost = cost if cost is not None else LIFESTYLE_RATES.get(level.title(), 10000)
    inc("Nuyen", -actual_cost)
    desc = f" ({notes})" if notes else ""
    return f"Lifestyle [{level}]: -{actual_cost:,}¥{desc}"


def _query_db_row(query: str, params: Tuple[Any, ...]) -> Optional[Dict[str, Any]]:
    import sqlite3
    db_candidates = [
        os.environ.get("SR6_RULES_DB_PATH"),
        os.path.join(os.path.expanduser("~"), ".sr6", "rules_index.db"),
        os.path.join(os.getcwd(), "data", "sr6_rules.db"),
        os.path.join(os.path.dirname(__file__), "..", "..", "data", "sr6_rules.db")
    ]
    for p in db_candidates:
        if p and os.path.exists(p):
            try:
                conn = sqlite3.connect(p)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(query, params)
                row = cursor.fetchone()
                conn.close()
                if row:
                    return dict(row)
            except Exception:
                pass
    return None


def learn_complex_form(name: str) -> str:
    """Learns a Complex Form from database (-5 Karma)."""
    clean_name = name.strip()
    slug = clean_name.lower().replace(" ", "_")
    row = _query_db_row("SELECT * FROM ref_complex_forms WHERE lower(name) = ? OR lower(id) = ?", (clean_name.lower(), slug))
    fading = 2
    duration = "Immediate"
    target = "Device"
    notes = ""
    if row:
        fading_raw = row.get("fade", "2")
        fading = int(fading_raw) if str(fading_raw).isdigit() else 2
        duration = row.get("duration", "Immediate")
        target = row.get("target", "Device")
        notes = f"Source: {row.get('source', '')}"

    inc("Karma", -5)
    complex_form(clean_name, fading=fading, duration=duration, target=target, notes=notes)
    return f"Learned Complex Form: **{clean_name}** (-5 Karma) [Fading {fading}, {duration}, Target: {target}]"


def learn_spell(name: str) -> str:
    """Learns a Spell from database (-5 Karma)."""
    clean_name = name.strip()
    slug = clean_name.lower().replace(" ", "_")
    row = _query_db_row("SELECT * FROM ref_spells WHERE lower(name) = ? OR lower(id) = ?", (clean_name.lower(), slug))
    category = "Combat"
    duration = "Instant"
    spell_type = "Physical"
    spell_range = "Line of Sight"
    drain = 3
    notes = ""
    if row:
        drain_raw = row.get("drain", "3")
        drain = int(drain_raw) if str(drain_raw).isdigit() else 3
        duration = row.get("duration", "Instant")
        category = row.get("category", "Combat")
        spell_type = row.get("type", "Physical")
        spell_range = row.get("range", "Line of Sight")
        notes = f"Source: {row.get('source', '')}"

    inc("Karma", -5)
    spell(clean_name, category=category, duration=duration, spell_type=spell_type, spell_range=spell_range, drain=drain, notes=notes)
    return f"Learned Spell: **{clean_name}** (-5 Karma) [{category}, Drain {drain}, {duration}]"


def add_sprite(
    type_or_name: str = "Modular",
    level: int = 7,
    sprite_type: str = "Registered",
    count: int = 1,
    is_ally: bool = False,
    name: Optional[str] = None,
    details: str = "",
    autosofts: str = "",
    rating: Optional[int] = None,
    type_name: Optional[str] = None
) -> str:
    global _GLOBAL_LOG_STATE
    eff_level = rating if rating is not None else level
    
    # Handle both new add_sprite("Modular", 7) and legacy add_sprite("Sprite-M1", 7, "Modular")
    standard_types = ["Modular", "Assassin", "Crack", "Courier", "Fault", "Machine", "Data", "Companion"]
    if type_or_name in standard_types and not type_name and sprite_type in ["Registered", "Modular", ""]:
        eff_type = type_or_name
        eff_name = name or f"Sprite-{eff_type}"
    elif type_name:
        eff_type = type_name
        eff_name = type_or_name
    elif sprite_type not in ["Registered", ""]:
        eff_type = sprite_type
        eff_name = type_or_name
    else:
        eff_type = type_or_name
        eff_name = name or f"Sprite-{eff_type}"

    if isinstance(count, str):
        if not details:
            details = count
        count = 1
    else:
        try:
            count = int(count)
        except (ValueError, TypeError):
            count = 1

    eff_details = details if details else autosofts
    curr_m_idx = len(_GLOBAL_LOG_STATE.get("Missions", []))
    m_name = _GLOBAL_LOG_STATE["Missions"][-1] if curr_m_idx > 0 else "Character Creation"

    for i in range(count):
        s_name = eff_name if count == 1 else f"{eff_name}_{i+1}"
        s_info = {
            "name": s_name,
            "rating": eff_level,
            "level": eff_level,
            "type": eff_type,
            "autosofts": eff_details,
            "details": eff_details,
            "is_ally": is_ally,
            "registered_mission": curr_m_idx,
            "registered_mission_name": m_name,
            "status": "Active"
        }
        _GLOBAL_LOG_STATE["Sprites"].append(s_info)

    if count > 1:
        return f"Registered Sprites: **{eff_type}** (Rating {eff_level}) x{count}"
    elif is_ally:
        return f"Ally Sprite: **{eff_name}** (Rating {eff_level} {eff_type})"
    else:
        details_str = f" ({eff_details})" if eff_details else ""
        return f"**{eff_name}** (Rating {eff_level} {eff_type}{details_str})"


def add_spirit(
    spirit_type_or_name: str = "Fire",
    force: int = 5,
    spirit_type: Optional[str] = None,
    tasks: int = 4,
    count: int = 1,
    powers: str = "",
    is_great_form: bool = False,
    is_ally: bool = False,
    details: str = "",
    name: Optional[str] = None
) -> str:
    global _GLOBAL_LOG_STATE
    curr_m_idx = len(_GLOBAL_LOG_STATE.get("Missions", []))
    m_name = _GLOBAL_LOG_STATE["Missions"][-1] if curr_m_idx > 0 else "Character Creation"

    if isinstance(count, str):
        if not details:
            details = count
        count = 1
    else:
        try:
            count = int(count)
        except (ValueError, TypeError):
            count = 1

    eff_details = details if details else powers

    standard_spirits = ["Fire", "Water", "Air", "Earth", "Beast", "Man", "Guardian", "Guidance", "Plant", "Task"]
    if spirit_type_or_name in standard_spirits and not spirit_type:
        eff_type = spirit_type_or_name
        eff_name = name or f"Spirit of {eff_type}"
    elif spirit_type:
        eff_type = spirit_type
        eff_name = spirit_type_or_name
    else:
        eff_type = spirit_type_or_name
        eff_name = name or f"Spirit of {eff_type}"

    if not eff_details:
        eff_details = f"{tasks} Bound Tasks / {tasks} SRM Missions, Combat & Channeling"

    for i in range(count):
        s_name = eff_name if count == 1 else f"{eff_name}_{i+1}"
        s_info = {
            "name": s_name,
            "force": force,
            "type": eff_type,
            "tasks": tasks,
            "powers": eff_details,
            "details": eff_details,
            "is_great_form": is_great_form,
            "is_ally": is_ally,
            "bound_mission": curr_m_idx,
            "bound_mission_name": m_name,
            "status": "Active"
        }
        _GLOBAL_LOG_STATE.setdefault("Spirits", []).append(s_info)

    great_str = "Great Form " if is_great_form else ""
    if count > 1:
        return f"Bound Spirits: **{great_str}{eff_type}** (Force {force}, {tasks} Tasks) x{count}"
    else:
        return f"**{eff_name}** ({great_str}Force {force} {eff_type} Spirit, {tasks} Tasks/Missions)"


def get_active_sprites() -> List[Dict[str, Any]]:
    global _GLOBAL_LOG_STATE
    curr_m_idx = len(_GLOBAL_LOG_STATE.get("Missions", []))
    active = []
    for s in _GLOBAL_LOG_STATE.get("Sprites", []):
        if s.get("is_ally"):
            active.append(s)
        else:
            reg_m = s.get("registered_mission", 0)
            elapsed = curr_m_idx - reg_m
            if elapsed <= 3:
                active.append(s)
            else:
                s["status"] = "Expired"
    return active


def get_active_spirits() -> List[Dict[str, Any]]:
    global _GLOBAL_LOG_STATE
    curr_m_idx = len(_GLOBAL_LOG_STATE.get("Missions", []))
    active = []
    for s in _GLOBAL_LOG_STATE.get("Spirits", []):
        if s.get("is_ally"):
            active.append(s)
        else:
            bound_m = s.get("bound_mission", 0)
            tasks = s.get("tasks", 2)
            elapsed = curr_m_idx - bound_m
            if elapsed < tasks:
                active.append(s)
            else:
                s["status"] = "Expired"
    return active


def print_contacts_summary(contacts: Optional[Dict[str, Any]] = None):
    """Renders formatted markdown contact tables grouped by region."""
    global _GLOBAL_LOG_STATE
    targets = contacts if contacts is not None else _GLOBAL_LOG_STATE.get("Contacts", {})

    region_names = {
        "SEA": "Seattle (SEA)",
        "NOLA": "New Orleans (NOLA)",
        "AMS": "Amsterdam / UNL (AMS)",
        "HK": "Hong Kong / Southeast Asia (HK)",
        "KY": "Kentucky (KY)",
        "DW": "Desert Wars (DW)",
        "GEN": "General / Matrix / Other (GEN)"
    }

    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for name, c in targets.items():
        reg = c.get("region", "GEN") or "GEN"
        grouped.setdefault(reg, []).append(c)

    ordered_regions = ["SEA", "NOLA", "AMS", "HK", "KY", "DW", "GEN"]
    all_regions = ordered_regions + [r for r in grouped.keys() if r not in ordered_regions]

    for reg in all_regions:
        if reg in grouped:
            print(f"#### {region_names.get(reg, reg)}\n")
            print("| Contact Name | Connection | Loyalty | Favors | Types | Job / Archetype | Notes |")
            print("|---|:---:|:---:|:---:|---|---|---|")
            for c in grouped[reg]:
                c_types = c.get("types_str") or ", ".join(c.get("types", []))
                c_type = c.get("type", "") or c.get("archetype", "")
                c_notes = c.get("notes", "") or c.get("description", "")
                print(f"| {c['name']} | {c['connection']} | {c['loyalty']} | {c.get('favors', 0)} | {c_types} | {c_type} | {c_notes} |")
            print("\n")


class QuartoEvalEnv(dict):
    def __getitem__(self, key):
        if key in _GLOBAL_LOG_STATE:
            return _GLOBAL_LOG_STATE[key]
        return super().__getitem__(key)

    def get(self, key, default=None):
        if key in _GLOBAL_LOG_STATE:
            return _GLOBAL_LOG_STATE[key]
        return super().get(key, default)


def create_quarto_eval_env() -> Dict[str, Any]:
    """Returns an execution environment pre-populated with standard SR6 log helpers."""
    reset_log_state()
    return QuartoEvalEnv({
        "init_character": init_character,
        "mission": mission,
        "start_mission": start_mission,
        "contact": contact,
        "add_rep": add_rep,
        "add_sprite": add_sprite,
        "add_spirit": add_spirit,
        "work_for_the_people": work_for_the_people,
        "work_for_the_man": work_for_the_man,
        "bribe": bribe,
        "lifestyle": lifestyle,
        "learn_complex_form": learn_complex_form,
        "learn_spell": learn_spell,
        "get_active_sprites": get_active_sprites,
        "get_active_spirits": get_active_spirits,
        "print_contacts_summary": print_contacts_summary,
        "search_contacts": search_contacts,
        "format_contacts_table": format_contacts_table,
        "inc": inc,
        "inc_many": inc_many,
        "assign": assign,
        "initiate": initiate,
        "submerge": submerge,
        "modifier": modifier,
        "spell": spell,
        "complex_form": complex_form,
        "adept_power": adept_power,
        "metamagic": metamagic,
        "echo": echo,
        "sprite_power": sprite_power,
        "knowledge_skill": knowledge_skill,
        "language": language,
        "state": _GLOBAL_LOG_STATE,
    })


def resolve_existing_path(p: str) -> Optional[str]:
    if os.path.exists(p):
        return p
    candidates = [
        os.path.normpath(os.path.join(os.getcwd(), "..", p)),
        os.path.normpath(p.replace("chapters/", "core/")),
        os.path.normpath(p.replace("chapters/", "")),
        os.path.normpath(os.path.join("core", p)),
        os.path.normpath(os.path.join("chapters", p)),
        os.path.normpath(os.path.join("..", p))
    ]
    for cand in candidates:
        if os.path.exists(cand):
            return cand
    return None


def get_log_totals(log_path: Optional[Any] = None) -> Dict[str, Any]:
    # Alias for process_character_log

    if log_path is None:
        # Default fallback: search current directory and parent directory for core/ or chapters/ character_log.qmd
        possible_paths = [
            "core/character_log.qmd",
            "chapters/character_log.qmd",
            "character_log.qmd",
            "../core/character_log.qmd",
            "../chapters/character_log.qmd"
        ]
        files = [p for p in possible_paths if os.path.exists(p)][:1]
    elif isinstance(log_path, list):
        files = []
        for p in log_path:
            res = resolve_existing_path(p)
            if res:
                files.append(res)
    elif isinstance(log_path, str) and os.path.isdir(log_path):
        candidate_trios = [
            [os.path.join(log_path, "core", "character_build.qmd"), os.path.join(log_path, "core", "character_purchases.qmd"), os.path.join(log_path, "core", "character_log.qmd")],
            [os.path.join(log_path, "chapters", "character_build.qmd"), os.path.join(log_path, "chapters", "character_purchases.qmd"), os.path.join(log_path, "chapters", "character_log.qmd")],
            [os.path.join(log_path, "character_build.qmd"), os.path.join(log_path, "character_purchases.qmd"), os.path.join(log_path, "character_log.qmd")],
            [os.path.join(log_path, "..", "core", "character_build.qmd"), os.path.join(log_path, "..", "core", "character_purchases.qmd"), os.path.join(log_path, "..", "core", "character_log.qmd")],
            [os.path.join(log_path, "..", "chapters", "character_build.qmd"), os.path.join(log_path, "..", "chapters", "character_purchases.qmd"), os.path.join(log_path, "..", "chapters", "character_log.qmd")]
        ]
        files = []
        for trio in candidate_trios:
            matched = [p for p in trio if os.path.exists(p)]
            if matched:
                files = matched
                break
    elif isinstance(log_path, str):
        res = resolve_existing_path(log_path)
        files = [res] if res else []
    else:
        files = []

    def _trio_sort_key(fpath: str) -> int:
        base = os.path.basename(fpath).lower()
        if "build" in base:
            return 0
        if "purchase" in base or "gear" in base or "equipment" in base:
            return 1
        if "log" in base or "session" in base:
            return 2
        return 3

    files.sort(key=_trio_sort_key)


    contents = []
    for fpath in files:
        with open(fpath, "r", encoding="utf-8") as f:
            contents.append(f.read())

    content = "\n\n".join(contents)
    env = create_quarto_eval_env()

    pattern = re.compile(r'```\{python\}(.*?)```|`\{python\}\s*(.*?)`', re.DOTALL)
    with contextlib.redirect_stdout(io.StringIO()):
        for match in pattern.finditer(content):
            block = match.group(1)
            inline = match.group(2)
            if block is not None:
                clean_lines = [line for line in block.splitlines() if not line.strip().startswith('#|')]
                try:
                    exec(textwrap.dedent("\n".join(clean_lines)), env)
                except Exception:
                    pass
            elif inline is not None:
                code_str = inline.strip()
                try:
                    eval(code_str, env)
                except Exception:
                    try:
                        exec(code_str, env)
                    except Exception:
                        pass

    final_karma = _GLOBAL_LOG_STATE.get("Karma", 0)
    final_lifetime_karma = _GLOBAL_LOG_STATE.get("Lifetime_Karma", final_karma)
    final_nuyen = _GLOBAL_LOG_STATE.get("Nuyen", 0)
    final_lifetime_nuyen = _GLOBAL_LOG_STATE.get("Lifetime_Nuyen", final_nuyen)

    session_logs = list(_GLOBAL_LOG_STATE.get("Session_Logs", []))
    if not session_logs:
        session_sections = re.split(r'\n(?=#{2,3}\s+\*\*)', content)
        for section in session_sections:
            if not re.match(r'^#{2,3}\s+\*\*', section.strip()):
                continue

            header_match = re.search(r'#{2,3}\s+\*\*(?:(\d{4}-[A-Za-z]{3}-\d{2}|\d{4}-\d{2}-\d{2}):\s*)?([^*]+)\*\*(?:\s*`\{python\}\s*start_mission\((.*?)\)`|\s*)', section)
            if not header_match:
                continue

            date_str = header_match.group(1) or ""
            title_str = header_match.group(2).strip()

            if not date_str:
                date_match = re.search(r'\*\s+\*\*Date:\*\*\s*(\d{4}-[A-Za-z]{3}-\d{2}|\d{4}-\d{2}-\d{2})', section)
                if date_match:
                    date_str = date_match.group(1).strip()

            gm_match = re.search(r'\*\s+\*\*GM:\*\*\s*(.+)', section)
            gm_str = gm_match.group(1).strip() if gm_match else ""

            # Extract base mission rewards specifically from * **Rewards:** line or main body before Downtime
            main_part = section.split("### Downtime")[0].split("### Purchases")[0]
            rewards_line_match = re.search(r'\*\s+\*\*Rewards:\*\*\s*(.+)', main_part)
            rewards_line = rewards_line_match.group(1) if rewards_line_match else main_part

            karma_val = 0
            karma_matches = re.findall(r"inc\s*\(\s*'Karma'\s*,\s*(-?\d+)\s*\)|inc_many\s*\(\s*\(\s*'Karma'\s*,\s*(-?\d+)\s*\)", rewards_line)
            for km in karma_matches:
                k1, k2 = km
                val = int(k1 or k2)
                if val > 0:
                    karma_val += val

            nuyen_val = 0
            nuyen_matches = re.findall(r"inc\s*\(\s*'Nuyen'\s*,\s*(-?\d+)\s*\)|inc_many\s*\(\s*\(\s*'Nuyen'\s*,\s*(-?\d+)\s*\)", rewards_line)
            for nm in nuyen_matches:
                n1, n2 = nm
                val = int(n1 or n2)
                if val > 0:
                    nuyen_val += val

            if karma_val > 0 or nuyen_val > 0 or "start_mission" in section:
                session_logs.append({
                    "title": title_str,
                    "date": date_str,
                    "gm": gm_str,
                    "karma": karma_val,
                    "nuyen": nuyen_val
                })

    rep_dict = _GLOBAL_LOG_STATE.get("Reputation", {})
    total_rep = sum(rep_dict.values()) if isinstance(rep_dict, dict) else 0
    active_sprites = get_active_sprites()
    active_spirits = get_active_spirits()

    return {
        "Karma": final_karma,
        "Lifetime_Karma": final_lifetime_karma,
        "Nuyen": final_nuyen,
        "Lifetime_Nuyen": final_lifetime_nuyen,
        "Heat": _GLOBAL_LOG_STATE.get("Heat", 0),
        "Submersion_Grade": _GLOBAL_LOG_STATE.get("Submersion_Grade", 0),
        "Initiation_Grade": _GLOBAL_LOG_STATE.get("Initiation_Grade", 0),
        "Nanite_Volume": _GLOBAL_LOG_STATE.get("Nanite_Volume", 6 if _GLOBAL_LOG_STATE.get("Character") == "venn" else 0),
        "Reputation": rep_dict,
        "Total_Reputation": total_rep,
        "Sprites": _GLOBAL_LOG_STATE.get("Sprites", []),
        "Active_Sprites": active_sprites,
        "Active_Sprite_Count": len(active_sprites),
        "Spirits": _GLOBAL_LOG_STATE.get("Spirits", []),
        "Active_Spirits": active_spirits,
        "Active_Spirit_Count": len(active_spirits),
        "Contacts": _GLOBAL_LOG_STATE.get("Contacts", {}),
        "Missions": _GLOBAL_LOG_STATE.get("Missions", []),
        "Modifiers": _GLOBAL_LOG_STATE.get("Modifiers", []),
        "Spells": _GLOBAL_LOG_STATE.get("Spells", []),
        "Complex_Forms": _GLOBAL_LOG_STATE.get("Complex_Forms", []),
        "Adept_Powers": _GLOBAL_LOG_STATE.get("Adept_Powers", []),
        "Metamagic": _GLOBAL_LOG_STATE.get("Metamagic", []),
        "Echoes": _GLOBAL_LOG_STATE.get("Echoes", []),
        "Sprite_Powers": _GLOBAL_LOG_STATE.get("Sprite_Powers", []),
        "Knowledge_Skills": _GLOBAL_LOG_STATE.get("Knowledge_Skills", []),
        "Monad_Abilities": _GLOBAL_LOG_STATE.get("Monad_Abilities", []),
        "Session_Logs": session_logs
    }


# Backwards compatibility alias
process_character_log = get_log_totals
