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

from sr6core.contacts import is_canonical_contact, get_canonical_contact

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
      - 'specialization': adds +2 to that skill in that sub-skill
      - 'expertise': adds +3 to that skill in that sub-skill
      - 'other': weird things like adrenaline pumps, suprathyroid glands, wireless on skillwires
    """
    global _GLOBAL_LOG_STATE
    valid_type = type.lower().strip()
    if valid_type not in ["teamwork", "augmentation", "specialization", "expertise", "other", "focus", "symbiosis", "gear", "attribute_substitution"]:
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
    _GLOBAL_LOG_STATE.setdefault("Modifiers", []).append(mod_entry)
    
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
    connection: Optional[int] = None,
    loyalty: Optional[int] = None,
    fp: int = 0,
    type_name: str = "",
    region: str = "",
    notes: str = "",
    event: str = ""
) -> Dict[str, Any]:
    """
    Records or updates a campaign contact.
    - Canonical SRM contacts: Connection rating is locked; description is locked to official SRM text.
    - Non-canonical contacts: Connection and Loyalty can be raised; description fixed on first encounter.
    - Favor points accumulate, and Loyalty automatically increases when enough favor is accumulated.
    """
    global _GLOBAL_LOG_STATE
    name_clean = name.strip()
    canon_info = get_canonical_contact(name_clean)
    is_canon = canon_info is not None

    contacts = _GLOBAL_LOG_STATE["Contacts"]
    
    # Identify mission or event context
    curr_m_idx = len(_GLOBAL_LOG_STATE.get("Missions", []))
    m_name = _GLOBAL_LOG_STATE["Missions"][-1] if curr_m_idx > 0 else "Character Creation"
    event_label = event or notes or m_name

    if not region:
        for prefix in ["SEA", "NOLA", "AMS", "KY", "DW", "HK", "GEN"]:
            if type_name.startswith(prefix) or (notes and notes.startswith(prefix)):
                region = prefix
                break

    is_first_encounter = name_clean not in contacts
    promoted_levels = 0

    if is_first_encounter:
        if is_canon:
            eff_conn = canon_info["connection"]
            eff_type = canon_info.get("job", type_name)
            eff_region = canon_info.get("region", region or "GEN")
            eff_desc = canon_info.get("description", "")
        else:
            eff_conn = connection if connection is not None else 1
            eff_type = type_name
            eff_region = region if region else "GEN"
            eff_desc = notes

        eff_loyalty = loyalty if loyalty is not None else (1 if fp == 0 else 0)
        c_info = {
            "name": name_clean,
            "canonical_name": name_clean,
            "is_canonical": is_canon,
            "connection": eff_conn,
            "loyalty": eff_loyalty,
            "favors": fp,
            "type": eff_type,
            "region": eff_region,
            "description": eff_desc,
            "notes": eff_desc,
            "history": [f"{event_label} (Met: C{eff_conn} L{eff_loyalty}, +{fp} FP)" if fp else f"{event_label} (Met: C{eff_conn} L{eff_loyalty})"]
        }
        contacts[name_clean] = c_info
    else:
        c_info = contacts[name_clean]
        
        # Connection: immutable for canonical contacts; can increase for non-canon
        if not is_canon and connection is not None and connection > c_info["connection"]:
            c_info["connection"] = connection
        
        # Loyalty: update if explicitly passed higher
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

    # Formulate clean string output for Quarto rendering
    if is_first_encounter:
        type_str = f" ({c_info['type']})" if c_info.get("type") else ""
        if promoted_levels > 0:
            return f"**{name_clean}**{type_str} [C:{c_info['connection']}] — Auto-Promoted to Loyalty {c_info['loyalty']}! ({c_info['favors']} FP remaining)"
        elif fp > 0:
            return f"**{name_clean}**{type_str} [C:{c_info['connection']} L:{c_info['loyalty']}] (+{fp} Favor)"
        else:
            return f"**{name_clean}**{type_str} [C:{c_info['connection']} L:{c_info['loyalty']}]"
    else:
        if promoted_levels > 0:
            return f"**{name_clean}** (+{fp} Favor → Auto-Promoted to Loyalty {c_info['loyalty']}! [{c_info['favors']} FP remaining])"
        elif fp != 0:
            return f"**{name_clean}** ({'+' if fp >= 0 else ''}{fp} Favor → {c_info['favors']} FP total, Loyalty {c_info['loyalty']})"
        else:
            return f"**{name_clean}** [C:{c_info['connection']} L:{c_info['loyalty']}]"


def add_rep(faction: str, points: int) -> Dict[str, int]:
    global _GLOBAL_LOG_STATE
    rep = _GLOBAL_LOG_STATE["Reputation"]
    rep[faction] = rep.get(faction, 0) + points
    return rep


def add_sprite(name: str, rating: int = 7, sprite_type: str = "Registered", autosofts: str = "", is_ally: bool = False, level: Optional[int] = None, type_name: Optional[str] = None, details: str = "") -> str:
    global _GLOBAL_LOG_STATE
    eff_rating = level if level is not None else rating
    eff_type = type_name if type_name is not None else sprite_type
    eff_details = details if details else autosofts
    curr_m_idx = len(_GLOBAL_LOG_STATE.get("Missions", []))
    m_name = _GLOBAL_LOG_STATE["Missions"][-1] if curr_m_idx > 0 else "Character Creation"
    s_info = {
        "name": name,
        "rating": eff_rating,
        "level": eff_rating,
        "type": eff_type,
        "autosofts": eff_details,
        "details": eff_details,
        "is_ally": is_ally,
        "registered_mission": curr_m_idx,
        "registered_mission_name": m_name,
        "status": "Active"
    }
    _GLOBAL_LOG_STATE["Sprites"].append(s_info)
    details_str = f" ({eff_details})" if eff_details else ""
    return f"**{name}** (Rating {eff_rating} {eff_type}{details_str})"


def add_spirit(
    name: str,
    force: int = 5,
    spirit_type: str = "Kin",
    tasks: int = 2,
    powers: str = "",
    is_great_form: bool = False,
    is_ally: bool = False,
    details: str = ""
) -> str:
    global _GLOBAL_LOG_STATE
    curr_m_idx = len(_GLOBAL_LOG_STATE.get("Missions", []))
    m_name = _GLOBAL_LOG_STATE["Missions"][-1] if curr_m_idx > 0 else "Character Creation"
    eff_details = details if details else powers
    s_info = {
        "name": name,
        "force": force,
        "type": spirit_type,
        "tasks": tasks,
        "powers": eff_details,
        "details": eff_details,
        "is_great_form": is_great_form,
        "is_ally": is_ally,
        "bound_mission": curr_m_idx,
        "bound_mission_name": m_name,
        "status": "Active"
    }
    if "Spirits" not in _GLOBAL_LOG_STATE:
        _GLOBAL_LOG_STATE["Spirits"] = []
    _GLOBAL_LOG_STATE["Spirits"].append(s_info)
    great_str = "Great Form " if is_great_form else ""
    details_str = f" ({eff_details})" if eff_details else ""
    return f"**{name}** ({great_str}Force {force} {spirit_type} Spirit, {tasks} Tasks/Missions{details_str})"


def start_mission(code: str) -> str:
    global _GLOBAL_LOG_STATE
    _GLOBAL_LOG_STATE["Missions"].append(code)
    return ""


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
            print("| Contact Name | Connection | Loyalty | Favors | Type / Archetype | Notes |")
            print("|---|:---:|:---:|:---:|---|---|")
            for c in grouped[reg]:
                c_type = c.get("type", "") or c.get("archetype", "")
                c_notes = c.get("notes", "") or c.get("description", "")
                print(f"| {c['name']} | {c['connection']} | {c['loyalty']} | {c.get('favors', 0)} | {c_type} | {c_notes} |")
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
        "inc": inc,
        "inc_many": inc_many,
        "contact": contact,
        "add_rep": add_rep,
        "add_sprite": add_sprite,
        "add_spirit": add_spirit,
        "start_mission": start_mission,
        "get_active_sprites": get_active_sprites,
        "get_active_spirits": get_active_spirits,
        "print_contacts_summary": print_contacts_summary,
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

    session_sections = re.split(r'\n(?=#{2,3}\s+\*\*)', content)
    session_logs = []

    for section in session_sections:
        if not re.match(r'^#{2,3}\s+\*\*', section.strip()):
            continue

        header_match = re.search(r'#{2,3}\s+\*\*(?:(\d{4}-[A-Za-z]{3}-\d{2}|\d{4}-\d{2}-\d{2}):\s*)?([^*]+)\*\*(?:`\{python\}\s*start_mission\((.*?)\)`|\s*)', section)
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
        "Session_Logs": session_logs
    }
