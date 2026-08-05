"""
Quarto Campaign Session Log & Code Evaluator for SR6.
Parses campaign session logs, executes embedded Python blocks, and computes totals for Karma, Nuyen, Reputation, and Contacts.
Exposes standard Quarto tracking helpers so character logs can import sr6core.log_engine cleanly.
"""

import os
import re
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


def inc(resource: str, amount: int) -> int:
    global _GLOBAL_LOG_STATE
    res = resource.strip().title()
    current = _GLOBAL_LOG_STATE.get(res, 0)
    _GLOBAL_LOG_STATE[res] = current + amount
    if res == "Karma" and amount > 0:
        _GLOBAL_LOG_STATE["Lifetime_Karma"] = _GLOBAL_LOG_STATE.get("Lifetime_Karma", 0) + amount
    return _GLOBAL_LOG_STATE[res]


def inc_many(*pairs: Tuple[str, int]):
    for resource, amount in pairs:
        inc(resource, amount)


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


def add_sprite(name: str, rating: int, sprite_type: str = "Registered", autosofts: str = "") -> Dict[str, Any]:
    global _GLOBAL_LOG_STATE
    s_info = {
        "name": name,
        "rating": rating,
        "type": sprite_type,
        "autosofts": autosofts,
        "status": "Active"
    }
    _GLOBAL_LOG_STATE["Sprites"].append(s_info)
    return s_info


def start_mission(code: str):
    global _GLOBAL_LOG_STATE
    _GLOBAL_LOG_STATE["Missions"].append(code)


def get_active_sprites() -> List[Dict[str, Any]]:
    global _GLOBAL_LOG_STATE
    return [s for s in _GLOBAL_LOG_STATE.get("Sprites", []) if s.get("status") == "Active"]


def create_quarto_eval_env() -> Dict[str, Any]:
    """Returns an execution environment pre-populated with standard SR6 log helpers."""
    reset_log_state()
    return {
        "inc": inc,
        "inc_many": inc_many,
        "contact": contact,
        "add_rep": add_rep,
        "add_sprite": add_sprite,
        "start_mission": start_mission,
        "get_active_sprites": get_active_sprites,
        "state": _GLOBAL_LOG_STATE,
        "Karma": 0,
        "Lifetime_Karma": 0,
        "Nuyen": 0,
        "Heat": 0,
        "Reputation": {},
        "Sprites": [],
        "Contacts": {},
        "Missions": []
    }


def get_log_totals(log_path: Optional[Any] = None) -> Dict[str, Any]:
    if log_path is None:
        files = []
    elif isinstance(log_path, list):
        files = [p for p in log_path if os.path.exists(p)]
    elif isinstance(log_path, str) and os.path.isdir(log_path):
        target_files = [
            os.path.join(log_path, "chapters", "character_log.qmd"),
            os.path.join(log_path, "chapters", "character_purchases.qmd")
        ]
        files = [p for p in target_files if os.path.exists(p)]
    elif isinstance(log_path, str) and os.path.exists(log_path):
        files = [log_path]
    else:
        files = []

    contents = []
    for fpath in files:
        with open(fpath, "r", encoding="utf-8") as f:
            contents.append(f.read())

    content = "\n\n".join(contents)
    env = create_quarto_eval_env()

    pattern = re.compile(r'```\{python\}(.*?)```|`\{python\}\s*(.*?)`', re.DOTALL)
    for match in pattern.finditer(content):
        block = match.group(1)
        inline = match.group(2)
        if block is not None:
            clean_lines = [line for line in block.splitlines() if not line.strip().startswith('#|')]
            try:
                exec("\n".join(clean_lines), env)
            except Exception:
                pass
        elif inline is not None:
            try:
                eval(inline.strip(), env)
            except Exception:
                try:
                    exec(inline.strip(), env)
                except Exception:
                    pass

    final_karma = env.get("Karma", _GLOBAL_LOG_STATE.get("Karma", 0))
    final_lifetime_karma = env.get("Lifetime_Karma", _GLOBAL_LOG_STATE.get("Lifetime_Karma", final_karma))
    final_nuyen = env.get("Nuyen", _GLOBAL_LOG_STATE.get("Nuyen", 0))

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

    return {
        "Karma": final_karma,
        "Lifetime_Karma": final_lifetime_karma,
        "Nuyen": final_nuyen,
        "Heat": _GLOBAL_LOG_STATE.get("Heat", 0),
        "Submersion_Grade": _GLOBAL_LOG_STATE.get("Submersion_Grade", 0),
        "Reputation": _GLOBAL_LOG_STATE.get("Reputation", {}),
        "Sprites": _GLOBAL_LOG_STATE.get("Sprites", []),
        "Active_Sprites": get_active_sprites(),
        "Contacts": _GLOBAL_LOG_STATE.get("Contacts", {}),
        "Missions": _GLOBAL_LOG_STATE.get("Missions", []),
        "Session_Logs": session_logs
    }
