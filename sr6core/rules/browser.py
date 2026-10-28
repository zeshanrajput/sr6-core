"""
Rules Catalog Browser & Category Listing for SR6 Core.
Provides instant, tabular browsing of Echoes, Streams, Complex Forms, Metamagics, Qualities, and Actions.
"""

import os
import re
import json
import sqlite3
from typing import Dict, Any, List, Optional
from sr6core.rules.db import RulesDB, DEFAULT_DB_PATH


def list_rules_category(
    category: str,
    filter_query: Optional[str] = None,
    json_output: bool = False
) -> str:
    """
    Lists and formats rules catalog items by category.
    Supported categories: echoes, streams, forms (complex_forms), metamagics, qualities, actions.
    """
    cat = category.strip().lower()
    q = filter_query.strip().lower() if filter_query else None

    if cat in ["echo", "echoes", "submersion", "submersions"]:
        return _list_echoes(filter_q=q, json_output=json_output)
    elif cat in ["stream", "streams", "technomancer_streams"]:
        return _list_streams(filter_q=q, json_output=json_output)
    elif cat in ["form", "forms", "complex_form", "complex_forms", "complexform", "complexforms"]:
        return _list_complex_forms(filter_q=q, json_output=json_output)
    elif cat in ["metamagic", "metamagics", "initiation", "initiations", "magic"]:
        return _list_metamagics(filter_q=q, json_output=json_output)
    elif cat in ["quality", "qualities"]:
        return _list_qualities(filter_q=q, json_output=json_output)
    elif cat in ["action", "actions"]:
        return _list_actions(filter_q=q, json_output=json_output)
    else:
        return f"[Error] Unknown category '{category}'. Available: echoes, streams, forms, metamagics, qualities, actions."


def _list_echoes(filter_q: Optional[str] = None, json_output: bool = False) -> str:
    rdb = RulesDB()
    rdb.populate_sub_items()
    cur = rdb.conn.cursor()
    rows = cur.execute(
        "SELECT name, content FROM sub_items WHERE namespace = 'echoes' ORDER BY name ASC"
    ).fetchall()

    items = []
    for r in rows:
        name = r[0]
        desc = r[1]
        if (
            name.lower() in ["prerequisite", "game information"]
            or name.lower().startswith("see description")
            or name.lower().startswith("adjust the text")
        ):
            continue
        source = "CRB"
        src_match = re.search(r"\[(Hack and Slash|Falling Point|SR6 Core[^\]]*|CRB|HnS|FP)[^\]]*\]", desc)
        if src_match:
            source = src_match.group(1).replace("SR6 Core Rulebook", "CRB").replace("Hack and Slash", "Hack & Slash")
            clean_desc = re.sub(r"\s*\[(Hack and Slash|Falling Point|SR6 Core[^\]]*|CRB|HnS|FP)[^\]]*\]", "", desc).strip()
        else:
            clean_desc = desc.strip()

        if filter_q and filter_q not in name.lower() and filter_q not in clean_desc.lower():
            continue

        items.append({
            "name": name,
            "source": source,
            "description": clean_desc
        })

    if json_output:
        return json.dumps(items, indent=2)

    lines = ["### Shadowrun 6e Submersion Echoes Directory\n"]
    lines.append("| Submersion Echo | Source | Mechanics / Summary |")
    lines.append("| :--- | :---: | :--- |")
    for it in items:
        lines.append(f"| **{it['name']}** | {it['source']} | {it['description']} |")
    lines.append(f"\n*Total: {len(items)} echoes. Run `uv run sr6 card echo \"<name>\"` for full card.*")
    return "\n".join(lines)


def _list_streams(filter_q: Optional[str] = None, json_output: bool = False) -> str:
    streams = [
        {
            "stream": "Technoshaman",
            "mental_focus": "Charisma",
            "specialty": "Sprite communion, Great Sprite powers (Harmonize, Override, Phantom)",
            "sprites": "Courier, Crack, Data, Fault, Machine",
            "source": "CRB p. 191 / HnS p. 60"
        },
        {
            "stream": "Sourceror",
            "mental_focus": "Logic",
            "specialty": "Multi-form sustaining up to Resonance rating, attribution fading discounts, hyperthreading",
            "sprites": "Courier, Crack, Data, Fault, Machine",
            "source": "Hack & Slash p. 60"
        },
        {
            "stream": "Machinist",
            "mental_focus": "Logic / Intuition",
            "specialty": "Drone & vehicle synergy (+1 Pilot, +2 Sensors), autosoft sharing, Machine Merge",
            "sprites": "Machine, Fault, Crack",
            "source": "Hack & Slash p. 62"
        },
        {
            "stream": "Cyberadept",
            "mental_focus": "Logic / Willpower",
            "specialty": "Cyberware integration, bioware overclocking, overcoming Resonance loss penalties",
            "sprites": "Data, Fault, Machine",
            "source": "Hack & Slash p. 61"
        },
        {
            "stream": "Dissonant",
            "mental_focus": "Willpower",
            "specialty": "Dissonance pools, corrupting sprites, Dissonance Spike/Diffusion complex forms",
            "sprites": "Dissonance Corrupted Sprites",
            "source": "Shadow Cast / Falling Point"
        }
    ]

    if filter_q:
        streams = [
            s for s in streams
            if filter_q in s["stream"].lower() or filter_q in s["specialty"].lower() or filter_q in s["sprites"].lower()
        ]

    if json_output:
        return json.dumps(streams, indent=2)

    lines = ["### Shadowrun 6e Technomancer Streams Directory\n"]
    lines.append("| Stream | Mental Focus | Core Mechanical Specialty | Native Sprites | Source |")
    lines.append("| :--- | :---: | :--- | :--- | :---: |")
    for s in streams:
        lines.append(f"| **{s['stream']}** | {s['mental_focus']} | {s['specialty']} | {s['sprites']} | {s['source']} |")
    lines.append("\n*Stream shift cost: 20 Karma. Run `uv run sr6 cheat streams` for detailed mechanics.*")
    return "\n".join(lines)


def _list_complex_forms(filter_q: Optional[str] = None, json_output: bool = False) -> str:
    rdb = RulesDB()
    cur = rdb.conn.cursor()
    rows = cur.execute(
        "SELECT name, target, duration, fade, source FROM ref_complex_forms ORDER BY name ASC"
    ).fetchall()

    forms = []
    for r in rows:
        name, target, duration, fade, source = r[0], r[1], r[2], r[3], r[4]
        src_label = source.replace("_", " ").title() if source else "CRB"
        if filter_q and filter_q not in name.lower() and filter_q not in src_label.lower():
            continue
        forms.append({
            "name": name,
            "target": target or "Persona/Device",
            "duration": duration or "Instant",
            "fade": str(fade) if fade is not None else "-",
            "source": src_label
        })

    # Include supplement forms from sub_items if not already present
    supp_rows = cur.execute(
        "SELECT name, content FROM sub_items WHERE namespace = 'complex_forms' ORDER BY name ASC"
    ).fetchall()
    existing_names = {f["name"].lower() for f in forms}
    for sr in supp_rows:
        sname = sr[0]
        if sname.lower() in existing_names:
            continue
        scontent = sr[1]
        target = "Persona/Device"
        duration = "Instant"
        fade = "Net Hits"
        source = "Shadow Cast"
        t_m = re.search(r"Target:\s*([^|]+)", scontent)
        d_m = re.search(r"Duration:\s*([^|]+)", scontent)
        f_m = re.search(r"Fade:\s*([^|]+)", scontent)
        s_m = re.search(r"\[(Shadow Cast[^\]]*)\]", scontent)
        if t_m: target = t_m.group(1).strip()
        if d_m: duration = d_m.group(1).strip()
        if f_m: fade = f_m.group(1).strip()
        if s_m: source = s_m.group(1).strip()

        if filter_q and filter_q not in sname.lower() and filter_q not in source.lower():
            continue
        forms.append({
            "name": sname,
            "target": target,
            "duration": duration,
            "fade": fade,
            "source": source
        })

    forms.sort(key=lambda x: x["name"])

    if json_output:
        return json.dumps(forms, indent=2)

    lines = ["### Shadowrun 6e Complex Forms Directory\n"]
    lines.append("| Complex Form | Target | Duration | Fade | Source |")
    lines.append("| :--- | :--- | :---: | :---: | :---: |")
    for f in forms:
        lines.append(f"| **{f['name']}** | {f['target']} | {f['duration']} | {f['fade']} | {f['source']} |")
    lines.append(f"\n*Total: {len(forms)} complex forms. Run `uv run sr6 card \"<name>\"` for full card.*")
    return "\n".join(lines)


def _list_metamagics(filter_q: Optional[str] = None, json_output: bool = False) -> str:
    rdb = RulesDB()
    rdb.populate_sub_items()
    cur = rdb.conn.cursor()
    rows = cur.execute(
        "SELECT name, content FROM sub_items WHERE namespace = 'metamagic' ORDER BY name ASC"
    ).fetchall()

    metas = []
    seen = set()
    for r in rows:
        name = r[0]
        desc = r[1]
        n_low = name.lower()
        if "focus" in n_low or n_low in seen or "disian" in desc.lower():
            continue
        if filter_q and filter_q not in n_low and filter_q not in desc.lower():
            continue
        seen.add(n_low)
        metas.append({
            "name": name,
            "description": desc
        })

    if json_output:
        return json.dumps(metas, indent=2)

    lines = ["### Shadowrun 6e Initiations & Metamagics Directory\n"]
    lines.append("| Metamagic | Mechanics / Summary |")
    lines.append("| :--- | :--- |")
    for m in metas:
        lines.append(f"| **{m['name']}** | {m['description']} |")
    lines.append(f"\n*Total: {len(metas)} metamagics. Run `uv run sr6 cheat metamagic` for rules breakdown.*")
    return "\n".join(lines)


def _list_qualities(filter_q: Optional[str] = None, json_output: bool = False) -> str:
    rdb = RulesDB()
    cur = rdb.conn.cursor()
    base_sql = "SELECT name, quality_type, karma, max_rating, source, srm_status FROM ref_qualities"
    params = []
    if filter_q:
        base_sql += " WHERE lower(name) LIKE ? OR lower(quality_type) LIKE ? OR lower(source) LIKE ?"
        term = f"%{filter_q}%"
        params.extend([term, term, term])
    base_sql += " ORDER BY quality_type DESC, name ASC LIMIT 60"
    rows = cur.execute(base_sql, params).fetchall()

    quals = []
    for r in rows:
        quals.append({
            "name": r[0],
            "type": (r[1] or "positive").title(),
            "karma": r[2],
            "max_rating": r[3] or 1,
            "source": (r[4] or "CRB").replace("_", " ").title(),
            "srm_status": r[5] or "Legal"
        })

    if json_output:
        return json.dumps(quals, indent=2)

    lines = ["### Shadowrun 6e Qualities Catalog\n"]
    lines.append("| Quality Name | Type | Karma | Max Rating | Source | SRM Status |")
    lines.append("| :--- | :---: | :---: | :---: | :---: | :---: |")
    for q in quals:
        lines.append(f"| **{q['name']}** | {q['type']} | {q['karma']} | {q['max_rating']} | {q['source']} | {q['srm_status']} |")
    lines.append(f"\n*Showing {len(quals)} qualities (limited to 60). Use `--filter <term>` to narrow search.*")
    return "\n".join(lines)


def _list_actions(filter_q: Optional[str] = None, json_output: bool = False) -> str:
    rdb = RulesDB()
    rdb.populate_sub_items()
    cur = rdb.conn.cursor()
    rows = cur.execute(
        "SELECT name, namespace, content FROM sub_items WHERE namespace IN ('matrix_actions', 'combat_actions') ORDER BY namespace ASC, name ASC"
    ).fetchall()

    actions = []
    for r in rows:
        name = r[0]
        ns = r[1].replace("_", " ").title()
        desc = r[2]
        if filter_q and filter_q not in name.lower() and filter_q not in desc.lower():
            continue
        actions.append({
            "name": name,
            "category": ns,
            "description": desc
        })

    if json_output:
        return json.dumps(actions, indent=2)

    lines = ["### Shadowrun 6e Tabletop Actions Directory\n"]
    lines.append("| Action | Subsystem | Description |")
    lines.append("| :--- | :---: | :--- |")
    for a in actions:
        lines.append(f"| **{a['name']}** | {a['category']} | {a['description']} |")
    lines.append(f"\n*Total: {len(actions)} actions. Run `uv run sr6 cheat actions` or `uv run sr6 cheat matrix` for full mechanics.*")
    return "\n".join(lines)
