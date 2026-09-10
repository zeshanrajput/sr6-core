"""
PACKs Catalog Parser & Reference Engine for SR6 Core.
Extracts pre-assembled character and equipment PACKs from Sixth World Companion (pp. 58–68)
and indexes them into SQLite ref_packs in ~/.sr6/rules_index.db.
"""

import os
import re
import json
import sqlite3
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple


def get_packs_table_schema() -> str:
    return """
    CREATE TABLE IF NOT EXISTS ref_packs (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        cost INTEGER NOT NULL,
        essence REAL,
        description TEXT,
        contents TEXT,
        alternate_grades_json TEXT,
        raw_text TEXT,
        source TEXT NOT NULL,
        page TEXT
    );
    CREATE INDEX IF NOT EXISTS idx_ref_packs_name ON ref_packs(name);
    CREATE INDEX IF NOT EXISTS idx_ref_packs_category ON ref_packs(category);
    """


def parse_6wc_packs(md_path: Optional[Path] = None) -> List[Dict[str, Any]]:
    """
    Parses PACKs from Sixth World Companion markdown file.
    """
    if md_path is None:
        from sr6core.source_explorer import resolve_book_file
        md_path, _ = resolve_book_file("6wc")
        if not md_path or not md_path.exists():
            return []

    with open(md_path, "r", encoding="utf-8", errors="replace") as f:
        text = f.read()

    # Locate the SUIT UP / PACKs section
    start_match = re.search(r"##\s*SUIT UP", text)
    if not start_match:
        start_idx = 0
    else:
        start_idx = start_match.start()

    lines = text[start_idx:].splitlines()
    entries: List[str] = []
    current_lines: List[str] = []

    for l in lines:
        is_new_header = (
            l.startswith("## ") 
            and not l.startswith("## (") 
            and not l.startswith("## **") 
            and not l.startswith("## Alternate")
        )
        if is_new_header:
            if current_lines:
                entries.append("\n".join(current_lines))
                current_lines = []
        current_lines.append(l)
    if current_lines:
        entries.append("\n".join(current_lines))

    packs: List[Dict[str, Any]] = []
    current_category = "General"

    for entry in entries:
        entry = entry.strip()
        if not entry.startswith("##"):
            continue

        lines = entry.splitlines()
        first_line = lines[0].strip()
        title = re.sub(r"^##\s*", "", first_line).strip()

        # Check if category header
        if title in (
            "SUIT UP", "Complete Character PACKs", "Weapons PACKs", "Armor PACKs",
            "Sensor PACKs", "Identity PACKs", "Augmentation PACKs", "Bikes", "Cars",
            "Heavy Pistols", "Light Pistols", "Hold-out Pistols", "Machine Pistols",
            "Tasers", "Shotguns", "Submachine Guns", "Rifles", "Machine Guns", "Launchers", "Crossbows"
        ):
            current_category = title
            # Also parse any inline item PACKs within this category section!
            for l in lines[1:]:
                m_inline = re.search(r"\*\*([^*:]+)\*\*\s*(?:\(([^)]+)\))?[:\s]*\*\*([\d,]+)\s*nuyen\*\*", l)
                if m_inline:
                    iname = m_inline.group(1).strip()
                    icontents = m_inline.group(2).strip() if m_inline.group(2) else ""
                    icost = int(m_inline.group(3).replace(",", ""))
                    iid = re.sub(r"[^a-z0-9_]", "", iname.lower().replace(" ", "_")).strip("_")
                    packs.append({
                        "id": iid,
                        "name": iname,
                        "category": current_category,
                        "cost": icost,
                        "essence": None,
                        "description": f"{current_category} PACK: {iname}",
                        "contents": icontents or l,
                        "alternate_grades_json": None,
                        "raw_text": l,
                        "source": "Sixth World Companion",
                        "page": "58-68"
                    })
            continue

        # Extract Cost
        cost_match = re.search(r"\((\d[\d,]*)\s*nuyen\)", entry, re.IGNORECASE)
        cost = 0
        if cost_match:
            cost = int(cost_match.group(1).replace(",", ""))

        # Extract Essence
        essence_match = re.search(r"Essence(?:\s*Cost)?[:\*]*\s*(\d+(?:\.\d+)?)", entry, re.IGNORECASE)
        essence = float(essence_match.group(1)) if essence_match else None

        # Extract Alternate grades
        alt_match = re.search(r"Alternate grade costs:([^\n]+)", entry, re.IGNORECASE)
        alt_grades: Dict[str, Any] = {}
        if alt_match:
            alt_text = alt_match.group(1)
            for grade in ["used", "alpha", "beta", "delta"]:
                m = re.search(rf"{grade}\s+([\d,]+)\s*nuyen(?:/([\d\.]+)\s*Essence)?", alt_text, re.IGNORECASE)
                if m:
                    alt_grades[grade] = {
                        "cost": int(m.group(1).replace(",", "")),
                        "essence": float(m.group(2)) if m.group(2) else None
                    }

        cat = current_category
        name_lower = title.lower()
        if "cyberarm" in name_lower or "cyberleg" in name_lower or "springheel" in name_lower:
            cat = "Cyberlimbs"
        elif "torso" in name_lower or "skull" in name_lower or "dome" in name_lower:
            cat = "Bodyware"
        elif "cybereyes" in name_lower:
            cat = "Eyeware"
        elif "cyberears" in name_lower:
            cat = "Earware"
        elif "skill rig" in name_lower or "reflexes" in name_lower:
            cat = "Neuralware"
        elif "hacker" in name_lower or "decker" in name_lower:
            cat = "Decker"
        elif "rigger" in name_lower:
            cat = "Rigger"
        elif "bike" in name_lower or "harley" in name_lower or "mirage" in name_lower or "growler" in name_lower:
            cat = "Vehicles"
        elif "car" in name_lower or "hyundai" in name_lower or "ford" in name_lower or "eurocar" in name_lower:
            cat = "Vehicles"

        # Separate description vs contents
        body_lines = [l.strip() for l in lines[1:] if l.strip() and not l.startswith("## (") and not l.startswith("## **Essence")]
        desc_lines = []
        contents_lines = []
        for l in body_lines:
            if l.startswith("Alternate grade costs:"):
                continue
            clean_l = re.sub(r"^##\s*", "", l)
            if any(clean_l.startswith(prefix) for prefix in [
                "Augmentations:", "Weapons:", "Armor:", "Drones:", "Vehicles:",
                "Software:", "Cyberdeck:", "Other Gear:", "Cyberarm (", "Cyberleg (",
                "Cybertorso (", "Cyberskull (", "Cybereyes (", "Cyberears (", "Included PACK:"
            ]):
                contents_lines.append(clean_l)
            else:
                desc_lines.append(clean_l)

        pack_id = re.sub(r"[^a-z0-9_]", "", title.lower().replace(" ", "_").replace(":", "_").replace("-", "_")).strip("_")
        if not pack_id:
            continue

        packs.append({
            "id": pack_id,
            "name": title,
            "category": cat,
            "cost": cost,
            "essence": essence,
            "description": " ".join(desc_lines).strip(),
            "contents": "\n".join(contents_lines).strip() or " ".join(body_lines),
            "alternate_grades_json": json.dumps(alt_grades) if alt_grades else None,
            "raw_text": entry,
            "source": "Sixth World Companion",
            "page": "58-68"
        })

    return packs


def compile_packs_to_db(db_path: Optional[str] = None) -> Tuple[int, str]:
    """
    Compiles all 6WC PACKs into ~/.sr6/rules_index.db.
    """
    from sr6core.rules_db import DEFAULT_DB_PATH
    path = db_path or DEFAULT_DB_PATH
    if not os.path.exists(path):
        return 0, f"Rules database not found at '{path}'"

    conn = sqlite3.connect(path)
    try:
        conn.executescript(get_packs_table_schema())
        packs = parse_6wc_packs()
        if not packs:
            return 0, "No PACKs could be parsed from Sixth World Companion."

        cursor = conn.cursor()
        for p in packs:
            cursor.execute(
                """INSERT OR REPLACE INTO ref_packs 
                   (id, name, category, cost, essence, description, contents, alternate_grades_json, raw_text, source, page)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    p["id"], p["name"], p["category"], p["cost"], p["essence"],
                    p["description"], p["contents"], p["alternate_grades_json"],
                    p["raw_text"], p["source"], p["page"]
                )
            )
        conn.commit()
        return len(packs), f"Successfully indexed {len(packs)} PACKs into ref_packs table."
    finally:
        conn.close()


def get_pack(identifier: str, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Retrieves a pack by ID or partial name from ref_packs.
    """
    from sr6core.rules_db import DEFAULT_DB_PATH
    path = db_path or DEFAULT_DB_PATH
    if not os.path.exists(path):
        return None

    clean = identifier.strip().lower()
    norm = clean.replace(" ", "_").replace(":", "_").replace("-", "_")

    conn = sqlite3.connect(path)
    try:
        cursor = conn.cursor()
        # Check if table exists, auto-compile if missing
        has_table = cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ref_packs'").fetchone()
        if not has_table:
            conn.executescript(get_packs_table_schema())
            compile_packs_to_db(path)

        row = cursor.execute(
            """SELECT * FROM ref_packs 
               WHERE id = ? OR lower(name) = ? OR id = ? OR lower(name) LIKE ?""",
            (clean, clean, norm, f"%{clean}%")
        ).fetchone()

        if not row:
            return None

        cols = [desc[0] for desc in cursor.description]
        data = dict(zip(cols, row))
        if data.get("alternate_grades_json"):
            data["alternate_grades"] = json.loads(data["alternate_grades_json"])
        else:
            data["alternate_grades"] = {}
        return data
    finally:
        conn.close()


def format_pack_card(pack: Dict[str, Any]) -> str:
    """
    Renders a markdown reference card for a PACK.
    """
    lines = [f"### [PACK] {pack['name']} ({pack['category']})"]
    meta = [f"**Cost**: {pack['cost']:,}¥"]
    if pack.get("essence") is not None:
        meta.append(f"**Essence**: {pack['essence']}")
    meta.append(f"**Source**: {pack.get('source', '6WC')} (p. {pack.get('page', '58-68')})")
    lines.append("> " + " | ".join(meta))
    lines.append("")

    if pack.get("description"):
        lines.append(f"*{pack['description']}*\n")

    if pack.get("contents"):
        lines.append("**Contents & Included Gear:**")
        for line in pack["contents"].splitlines():
            lines.append(f"- {line}")
        lines.append("")

    if pack.get("alternate_grades"):
        lines.append("**Alternate Grade Options:**")
        for grade, ginfo in pack["alternate_grades"].items():
            cost_str = f"{ginfo['cost']:,}¥"
            ess_str = f" / {ginfo['essence']} Essence" if ginfo.get("essence") is not None else ""
            lines.append(f"- **{grade.capitalize()}**: {cost_str}{ess_str}")
        lines.append("")

    return "\n".join(lines)
