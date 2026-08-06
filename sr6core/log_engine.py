"""
Quarto Campaign Session Log & Code Evaluator for SR6.
Parses campaign session logs, executes embedded Python blocks, and computes totals for Karma, Nuyen, Reputation, and Contacts.
Exposes standard Quarto tracking helpers so character logs can import sr6core.log_engine cleanly.
"""

import os
import re
import io
import contextlib
from typing import Dict, Any, List, Optional, Tuple, Union

# Global state dictionary for Quarto rendering scope
_GLOBAL_LOG_STATE: Dict[str, Any] = {
    "Karma": 0,
    "Lifetime_Karma": 0,
    "Nuyen": 0,
    "Heat": 0,
    "Resonance": 6,
    "Submersion_Grade": 0,
    "Reputation": {},
    "Sprites": [],
    "Contacts": {},
    "Missions": []
}

state = _GLOBAL_LOG_STATE


def reset_log_state():
    global _GLOBAL_LOG_STATE
    _GLOBAL_LOG_STATE = {
        "Karma": 0,
        "Lifetime_Karma": 0,
        "Nuyen": 0,
        "Heat": 0,
        "Resonance": 6,
        "Submersion_Grade": 0,
        "Reputation": {},
        "Sprites": [],
        "Contacts": {},
        "Missions": []
    }


def inc(resource: str, amount: int) -> str:
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
    op = "+=" if amount >= 0 else "-="
    return f"{res} {op} {abs(amount)}"


def assign(name: str, value: Any) -> Any:
    global _GLOBAL_LOG_STATE
    _GLOBAL_LOG_STATE[name] = value
    return value


def inc_many(*args: Any) -> str:
    if len(args) == 1 and isinstance(args[0], (list, tuple)):
        pairs = args[0]
    elif len(args) > 0 and isinstance(args[0], (list, tuple)):
        pairs = args
    elif len(args) % 2 == 0 and all(isinstance(a, (str, int)) for a in args):
        pairs = [(args[i], args[i+1]) for i in range(0, len(args), 2)]
    else:
        pairs = args

    res = []
    for item in pairs:
        if isinstance(item, (list, tuple)) and len(item) == 2:
            r, a = item
            res.append(inc(r, a))
    return ", ".join(res)


def contact(name: str, connection: int = 1, loyalty: int = 1, fp: int = 1, type_name: str = "", region: str = "", notes: str = "") -> Dict[str, Any]:
    global _GLOBAL_LOG_STATE
    c_info = {
        "name": name,
        "connection": connection,
        "loyalty": loyalty,
        "favors": fp,
        "type": type_name,
        "region": region,
        "notes": notes
    }
    _GLOBAL_LOG_STATE["Contacts"][name] = c_info
    return c_info


def add_rep(faction: str, points: int) -> Dict[str, int]:
    global _GLOBAL_LOG_STATE
    rep = _GLOBAL_LOG_STATE["Reputation"]
    rep[faction] = rep.get(faction, 0) + points
    return rep


def add_sprite(name: str, rating: int = 7, sprite_type: str = "Registered", autosofts: str = "", is_ally: bool = False, level: Optional[int] = None, type_name: Optional[str] = None, details: str = "") -> Dict[str, Any]:
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
    return s_info


def start_mission(code: str):
    global _GLOBAL_LOG_STATE
    _GLOBAL_LOG_STATE["Missions"].append(code)


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


def print_contacts_summary(contacts: Optional[Dict[str, Any]] = None):
    """Renders formatted markdown contact tables grouped by region."""
    global _GLOBAL_LOG_STATE
    targets = contacts if contacts is not None else _GLOBAL_LOG_STATE.get("Contacts", {})

    region_names = {
        "SEA": "Seattle (SEA)",
        "NOLA": "New Orleans (NOLA)",
        "AMS": "Amsterdam / UNL (AMS)",
        "KY": "Kentucky (KY)",
        "DW": "Desert Wars (DW)",
        "GEN": "General / Matrix / Other (GEN)"
    }

    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for name, c in targets.items():
        reg = c.get("region", "GEN") or "GEN"
        grouped.setdefault(reg, []).append(c)

    for reg in ["SEA", "NOLA", "AMS", "KY", "DW", "GEN"]:
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
        "start_mission": start_mission,
        "get_active_sprites": get_active_sprites,
        "print_contacts_summary": print_contacts_summary,
        "assign": assign,
        "state": _GLOBAL_LOG_STATE,
    })


def resolve_existing_path(p: str) -> Optional[str]:
    if os.path.exists(p):
        return p
    candidates = [
        os.path.normpath(os.path.join(os.getcwd(), "..", p)),
        os.path.normpath(p.replace("chapters/", "")),
        os.path.normpath(os.path.join("chapters", p)),
        os.path.normpath(os.path.join("..", p))
    ]
    for cand in candidates:
        if os.path.exists(cand):
            return cand
    return None


def get_log_totals(log_path: Optional[Any] = None) -> Dict[str, Any]:
    if log_path is None:
        # Default fallback: search current directory and parent directory for chapters/character_log.qmd
        possible_paths = [
            "chapters/character_log.qmd",
            "character_log.qmd",
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
        target_files = [
            os.path.join(log_path, "chapters", "character_log.qmd"),
            os.path.join(log_path, "chapters", "character_purchases.qmd")
        ]
        files = [p for p in target_files if os.path.exists(p)]
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
                clean_lines = [line.strip() for line in block.splitlines() if not line.strip().startswith('#|')]
                try:
                    exec("\n".join(clean_lines), env)
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

    session_sections = re.split(r'\n(?=###\s+\*\*)', content)
    session_logs = []

    for section in session_sections:
        if not section.strip().startswith("### **"):
            continue

        header_match = re.search(r'###\s+\*\*(?:(\d{4}-[A-Za-z]{3}-\d{2}):\s*)?([^*]+)\*\*(?:`\{python\}\s*start_mission\((.*?)\)`|\s*)', section)
        if not header_match:
            continue

        date_str = header_match.group(1) or ""
        title_str = header_match.group(2).strip()

        gm_match = re.search(r'\*\s+\*\*GM:\*\*\s*(.+)', section)
        gm_str = gm_match.group(1).strip() if gm_match else ""

        # Extract base mission rewards specifically from * **Rewards:** line if present
        rewards_line_match = re.search(r'\*\s+\*\*Rewards:\*\*\s*(.+)', section)
        rewards_line = rewards_line_match.group(1) if rewards_line_match else section

        karma_val = 0
        karma_matches = re.findall(r"inc\s*\(\s*'Karma'\s*,\s*(-?\d+)\s*\)|inc_many\s*\(\s*\(\s*'Karma'\s*,\s*(-?\d+)\s*\)", rewards_line)
        for km in karma_matches:
            k1, k2 = km
            if k1:
                karma_val += int(k1)
            if k2:
                karma_val += int(k2)

        nuyen_val = 0
        nuyen_matches = re.findall(r"inc\s*\(\s*'Nuyen'\s*,\s*(-?\d+)\s*\)|inc_many\s*\(\s*\(\s*'Nuyen'\s*,\s*(-?\d+)\s*\)", rewards_line)
        for nm in nuyen_matches:
            n1, n2 = nm
            if n1:
                nuyen_val += int(n1)
            if n2:
                nuyen_val += int(n2)

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

    return {
        "Karma": final_karma,
        "Lifetime_Karma": final_lifetime_karma,
        "Nuyen": final_nuyen,
        "Heat": _GLOBAL_LOG_STATE.get("Heat", 0),
        "Submersion_Grade": _GLOBAL_LOG_STATE.get("Submersion_Grade", 0),
        "Reputation": rep_dict,
        "Total_Reputation": total_rep,
        "Sprites": _GLOBAL_LOG_STATE.get("Sprites", []),
        "Active_Sprites": active_sprites,
        "Active_Sprite_Count": len(active_sprites),
        "Contacts": _GLOBAL_LOG_STATE.get("Contacts", {}),
        "Missions": _GLOBAL_LOG_STATE.get("Missions", []),
        "Session_Logs": session_logs
    }
