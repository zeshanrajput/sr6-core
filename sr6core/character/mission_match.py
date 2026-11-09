"""
SRM Table Matchmaker, Availability Tracker, Campaign Auditing, and Career Runway.
Provides:
- Instant table matchmaking for posted missions across all character rosters.
- Available mission queries across both 2081 and 2083 seasons.
- Duplicate mission detection and 2-SRM lifestyle/rent cadence linter.
- Career runway projection and mechanical plan feasibility checks.
"""

import os
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from sr6core.character.manager import CharacterManager
from sr6core.character.mission_registry import (
    CANONICAL_MISSIONS,
    normalize_mission_code,
    get_mission_record,
)

LIFESTYLE_COSTS = {
    "Street": 0,
    "Squatter": 500,
    "Low": 2000,
    "Middle": 5000,
    "High": 10000,
    "Luxury": 100000,
}


def parse_character_missions_log(log_path: str) -> Dict[str, Any]:
    """
    Parses a character's character_log.qmd to extract all logged missions and lifestyle events.
    """
    p = Path(log_path)
    if not p.exists():
        return {"missions": [], "lifestyles": [], "exists": False}

    with open(p, "r", encoding="utf-8") as f:
        lines = f.readlines()

    missions = []
    lifestyles = []

    mission_regex = re.compile(r'mission\(\s*["\']([^"\']+)["\'](?P<kwargs>[^\)]*)\)')
    lifestyle_regex = re.compile(r'lifestyle\(\s*["\']?([^"\'\),]+)?["\']?(?P<kwargs>[^\)]*)\)')

    for idx, line in enumerate(lines, 1):
        m = mission_regex.search(line)
        if m:
            raw_code = m.group(1).strip()
            norm_code = normalize_mission_code(raw_code)
            kwargs_str = m.group("kwargs")

            d_match = re.search(r'date\s*=\s*["\']([^"\']+)["\']', kwargs_str)
            date_val = d_match.group(1) if d_match else ""

            k_match = re.search(r'karma\s*=\s*([0-9\-]+)', kwargs_str)
            karma_val = int(k_match.group(1)) if k_match else 0

            n_match = re.search(r'nuyen\s*=\s*([0-9\-]+)', kwargs_str)
            nuyen_val = int(n_match.group(1)) if n_match else 0

            gm_match = re.search(r'gm\s*=\s*["\']([^"\']+)["\']', kwargs_str)
            gm_val = gm_match.group(1) if gm_match else ""

            diff_match = re.search(r'difficulty\s*=\s*["\']([^"\']+)["\']', kwargs_str)
            diff_val = diff_match.group(1) if diff_match else "Normal"

            missions.append({
                "raw_code": raw_code,
                "norm_code": norm_code,
                "date": date_val,
                "karma": karma_val,
                "nuyen": nuyen_val,
                "gm": gm_val,
                "difficulty": diff_val,
                "line": idx,
                "raw": line.strip()
            })

        l = lifestyle_regex.search(line)
        if l:
            level = (l.group(1) or "Low").strip().title()
            kwargs_str = l.group("kwargs")
            waived = bool(re.search(r'waived\s*=\s*True', kwargs_str, re.IGNORECASE))
            notes_match = re.search(r'notes\s*=\s*["\']([^"\']+)["\']', kwargs_str)
            notes = notes_match.group(1) if notes_match else ""

            lifestyles.append({
                "level": level,
                "waived": waived,
                "notes": notes,
                "line": idx,
                "raw": line.strip()
            })

    return {"missions": missions, "lifestyles": lifestyles, "exists": True}


def _get_character_log_path(char_info: Dict[str, Any]) -> Optional[str]:
    """Resolves character_log.qmd path from CharacterManager character info."""
    repo_dir = Path(char_info.get("repo_dir") or Path(char_info["path"]).parent)
    candidates = [
        repo_dir / "core" / "character_log.qmd",
        repo_dir / "character_log.qmd",
        repo_dir / "chapters" / "character_log.qmd"
    ]
    for c in candidates:
        if c.exists():
            return str(c)
    return None


def match_mission(query: str, char_ids: Optional[List[str]] = None, active_only: bool = True) -> Dict[str, Any]:
    """
    Checks an announced mission against character portfolios.
    By default, checks active campaign runners (reiko, velvet), ignoring lab incubator prototypes.
    """
    norm_id = normalize_mission_code(query)
    mission_rec = get_mission_record(norm_id) or get_mission_record(query)

    cm = CharacterManager()
    all_chars = cm.discover_characters()
    if char_ids:
        target_chars = {k: v for k, v in all_chars.items() if k in char_ids}
    elif active_only:
        target_chars = {
            k: v for k, v in all_chars.items()
            if v.get("config", {}).get("status") == "active" or "lab" not in str(v.get("repo_dir", "")).lower()
        }
    else:
        target_chars = all_chars

    results = {
        "query": query,
        "norm_id": norm_id,
        "mission": mission_rec or {
            "id": norm_id,
            "code": norm_id,
            "title": query,
            "season": "Unknown",
            "arc": "Unknown",
            "type": "Unknown",
            "region": "GEN",
            "synopsis": "",
            "file_path": ""
        },
        "characters": {}
    }

    for cid, cinfo in target_chars.items():
        log_path = _get_character_log_path(cinfo)
        if not log_path:
            results["characters"][cid] = {
                "name": cinfo.get("name", cid),
                "status": "AVAILABLE",
                "available": True,
                "runs": []
            }
            continue

        log_data = parse_character_missions_log(log_path)
        matching_runs = [m for m in log_data["missions"] if m["norm_code"] == norm_id]

        if matching_runs:
            results["characters"][cid] = {
                "name": cinfo.get("name", cid),
                "status": "ALREADY PLAYED",
                "available": False,
                "runs": matching_runs,
                "log_path": log_path
            }
        else:
            results["characters"][cid] = {
                "name": cinfo.get("name", cid),
                "status": "AVAILABLE",
                "available": True,
                "runs": [],
                "log_path": log_path
            }

    return results


def get_available_missions(char_id: str) -> Dict[str, Any]:
    """
    Returns all unplayed missions for a character across BOTH 2081 and 2083 seasons,
    grouped by Arc.
    """
    cm = CharacterManager()
    all_chars = cm.discover_characters()
    if char_id not in all_chars:
        raise ValueError(f"Character '{char_id}' not found in portfolio.")

    cinfo = all_chars[char_id]
    log_path = _get_character_log_path(cinfo)
    played_codes = set()
    if log_path:
        log_data = parse_character_missions_log(log_path)
        played_codes = {m["norm_code"] for m in log_data["missions"]}

    by_arc: Dict[str, List[Dict[str, Any]]] = {}
    played_count = 0
    available_count = 0

    for m_id, meta in CANONICAL_MISSIONS.items():
        arc = meta.get("arc", "Other Missions")
        if arc not in by_arc:
            by_arc[arc] = []

        is_played = m_id in played_codes
        if is_played:
            played_count += 1
        else:
            available_count += 1

        by_arc[arc].append({
            "id": m_id,
            "code": meta.get("code", m_id),
            "title": meta.get("title", m_id),
            "season": meta.get("season", "GEN"),
            "type": meta.get("type", "SRM"),
            "region": meta.get("region", "GEN"),
            "played": is_played
        })

    return {
        "char_id": char_id,
        "name": cinfo.get("name", char_id),
        "total_missions": len(CANONICAL_MISSIONS),
        "played_count": played_count,
        "available_count": available_count,
        "completion_pct": round((played_count / len(CANONICAL_MISSIONS)) * 100, 1) if CANONICAL_MISSIONS else 0,
        "arcs": by_arc
    }


def audit_character_missions(char_id: str) -> Dict[str, Any]:
    """
    Audits character_log.qmd for:
    1. Duplicate mission runs (strictly illegal in SRM).
    2. 2-SRM lifestyle & debt rent cadence (must be paid every other SRM across 2081 and 2083).
    """
    cm = CharacterManager()
    all_chars = cm.discover_characters()
    if char_id not in all_chars:
        raise ValueError(f"Character '{char_id}' not found in portfolio.")

    cinfo = all_chars[char_id]
    log_path = _get_character_log_path(cinfo)
    if not log_path:
        return {
            "char_id": char_id,
            "valid": True,
            "errors": [],
            "warnings": [f"No character_log.qmd found for {char_id}."]
        }

    log_data = parse_character_missions_log(log_path)
    missions = log_data["missions"]
    lifestyles = log_data["lifestyles"]

    errors = []
    warnings = []

    # 1. Duplicate Detection
    seen: Dict[str, Dict[str, Any]] = {}
    for m in missions:
        code = m["norm_code"]
        if code in seen:
            prev = seen[code]
            errors.append(
                f"DUPLICATE MISSION: '{code}' played multiple times! "
                f"First at line {prev['line']} (date: {prev['date']}), "
                f"repeated at line {m['line']} (date: {m['date']})."
            )
        else:
            seen[code] = m

    # 2. 2-SRM Rent Cadence Check
    # Interleave events in chronological line order
    events = []
    for m in missions:
        # Check if mission is an SRM (not CMP, SMH, or special)
        mtype = "SRM" if "SRM" in m["norm_code"] else ("CMP" if "CMP" in m["norm_code"] else "OTHER")
        events.append({"type": "MISSION", "mtype": mtype, "data": m, "line": m["line"]})
    for l in lifestyles:
        events.append({"type": "LIFESTYLE", "data": l, "line": l["line"]})

    events.sort(key=lambda x: x["line"])

    srm_count = 0
    rent_payments = 0
    expected_rent_cycles = 0
    last_rent_srm = 0

    for ev in events:
        if ev["type"] == "MISSION":
            if ev["mtype"] == "SRM":
                srm_count += 1
                if srm_count % 2 == 0:
                    expected_rent_cycles += 1
        elif ev["type"] == "LIFESTYLE":
            rent_payments += 1
            delta = srm_count - last_rent_srm
            is_waived = ev["data"].get("waived", False)

            # Normal cadence is 2 SRMs between rent payments
            if delta < 1 and not is_waived:
                warnings.append(
                    f"Line {ev['line']}: Consecutive lifestyle payment '{ev['data']['level']}' recorded "
                    f"without advancing an SRM (SRM count: {srm_count})."
                )
            elif delta > 2:
                warnings.append(
                    f"Line {ev['line']}: Lifestyle payment '{ev['data']['level']}' recorded after {delta} SRMs "
                    f"(SRM #{srm_count}, last paid at SRM #{last_rent_srm}). Rent is due every 2 SRMs."
                )
            last_rent_srm = srm_count

    if rent_payments < expected_rent_cycles:
        missing = expected_rent_cycles - rent_payments
        errors.append(
            f"RENT CADENCE DEFICIT: {srm_count} SRMs completed requires {expected_rent_cycles} lifestyle payments, "
            f"but only {rent_payments} payments were recorded ({missing} missing)."
        )

    return {
        "char_id": char_id,
        "name": cinfo.get("name", char_id),
        "log_path": log_path,
        "srm_count": srm_count,
        "cmp_count": len([m for m in missions if "CMP" in m["norm_code"]]),
        "total_missions": len(missions),
        "rent_payments": rent_payments,
        "expected_rent_cycles": expected_rent_cycles,
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }


def calculate_runway(char_id: str) -> Dict[str, Any]:
    """
    Calculates projected remaining career Karma, Nuyen, and Rent drag
    across all unplayed missions in BOTH 2081 and 2083 arcs.
    Compares against queued upgrades in reference/mechanical_plan.md.
    """
    avail = get_available_missions(char_id)
    cm = CharacterManager()
    cinfo = cm.discover_characters()[char_id]

    remaining_srm = 0
    remaining_cmp = 0
    remaining_pm = 0

    for arc, m_list in avail["arcs"].items():
        for m in m_list:
            if not m["played"]:
                mtype = m.get("type", "SRM")
                if mtype == "SRM":
                    remaining_srm += 1
                elif mtype == "CMP":
                    remaining_cmp += 1
                elif mtype == "PM":
                    remaining_pm += 1

    total_remaining = remaining_srm + remaining_cmp + remaining_pm

    # Payout estimates:
    # Standard SRM/CMP: ~7 Karma, ~9,000¥
    # Veteran SRM/CMP: ~8-9 Karma, ~12,000¥
    # Prime Mission: ~11 Karma, ~20,000¥
    base_karma = (remaining_srm + remaining_cmp) * 7 + remaining_pm * 11
    veteran_karma = (remaining_srm + remaining_cmp) * 8.5 + remaining_pm * 12
    max_karma = veteran_karma + total_remaining  # If using Work for the People (+1K/run)

    base_nuyen = (remaining_srm + remaining_cmp) * 9000 + remaining_pm * 20000
    veteran_nuyen = (remaining_srm + remaining_cmp) * 12000 + remaining_pm * 25000

    # Rent drag
    # Low lifestyle = 2000¥ per 2 SRMs
    lifestyle_level = "Low"
    monthly_cost = LIFESTYLE_COSTS.get(lifestyle_level, 2000)
    rent_cycles = remaining_srm // 2
    rent_drag = rent_cycles * monthly_cost

    net_nuyen_base = base_nuyen - rent_drag
    net_nuyen_veteran = veteran_nuyen - rent_drag

    # Check mechanical plan for pending Karma/Nuyen costs
    repo_dir = Path(cinfo.get("repo_dir") or Path(cinfo["path"]).parent)
    plan_path = repo_dir / "reference" / "mechanical_plan.md"
    pending_plan = []
    total_plan_karma = 0
    total_plan_nuyen = 0

    if plan_path.exists():
        with open(plan_path, "r", encoding="utf-8") as f:
            content = f.read()
        # Find markdown table rows with Karma costs
        table_rows = re.findall(r'\|\s*\*\*?([0-9A-Za-z]+)\*\*?\s*\|([^\|]+)\|([^\|]+)\|\s*([0-9]+)\s*Karma', content)
        for step, name, cat, k_cost in table_rows:
            k_int = int(k_cost)
            clean_name = re.sub(r'[\*\`]', '', name).split('<br>')[0].strip()
            total_plan_karma += k_int
            pending_plan.append({"step": step, "name": clean_name, "category": cat.strip(), "karma": k_int})

    return {
        "char_id": char_id,
        "name": avail["name"],
        "played_missions": avail["played_count"],
        "remaining_missions": total_remaining,
        "remaining_srms": remaining_srm,
        "remaining_cmps": remaining_cmp,
        "remaining_pms": remaining_pm,
        "projected_karma": {
            "conservative": int(base_karma),
            "expected_veteran": int(veteran_karma),
            "max_with_work_for_people": int(max_karma)
        },
        "projected_nuyen": {
            "gross_conservative": int(base_nuyen),
            "gross_veteran": int(veteran_nuyen),
            "rent_drag": rent_drag,
            "rent_cycles": rent_cycles,
            "net_conservative": int(net_nuyen_base),
            "net_veteran": int(net_nuyen_veteran)
        },
        "mechanical_plan": {
            "has_plan": len(pending_plan) > 0,
            "pending_steps": pending_plan[:6],
            "total_karma_queued": total_plan_karma,
            "achievable": total_plan_karma <= veteran_karma,
            "runway_consumption_pct": round((total_plan_karma / veteran_karma) * 100, 1) if veteran_karma > 0 else 0
        }
    }
