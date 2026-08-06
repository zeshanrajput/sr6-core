"""
Reference Card Generator and Character Card Deck Exporter for SR6.
Combines CommLink6 XML stat parameters with Rules Vault text descriptions.
"""

import os
import sqlite3
import html
from typing import Dict, Any, List, Optional, Tuple
from sr6core.rules_db import DEFAULT_DB_PATH, RulesDB
from sr6core.character_manager import CharacterManager


def get_item_card(category: str, item_id: str, db_path: str = DEFAULT_DB_PATH) -> Dict[str, Any]:
    """
    Looks up item stat fields in CommLink XML tables and rules vault text in SQLite.
    Returns structured card object and formatted Markdown/HTML string.
    """
    if not os.path.exists(db_path):
        return {"id": item_id, "name": item_id.title(), "category": category, "markdown": f"**{item_id.title()}** (Database not found)"}

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cat_table_map = {
        "quality": ("ref_qualities", "id"),
        "spell": ("ref_spells", "id"),
        "complex_form": ("ref_complex_forms", "id"),
        "weapon": ("ref_weapons", "id"),
        "cyberware": ("ref_cyberware", "id"),
        "adept_power": ("ref_adept_powers", "id"),
        "vehicle": ("ref_vehicles", "id"),
        "program": ("ref_programs", "id"),
        "gear": ("ref_gear", "id"),
    }

    table_info = cat_table_map.get(category.lower())
    stat_row = None
    if table_info:
        table, col = table_info
        try:
            stat_row = cursor.execute(f"SELECT * FROM {table} WHERE {col} = ? OR name LIKE ?", (item_id, f"%{item_id}%")).fetchone()
        except Exception:
            pass

    if not stat_row:
        # fallback search across all ref_ tables
        for t in ["ref_qualities", "ref_spells", "ref_complex_forms", "ref_weapons", "ref_cyberware", "ref_gear"]:
            try:
                stat_row = cursor.execute(f"SELECT * FROM {t} WHERE id = ? OR name LIKE ?", (item_id, f"%{item_id}%")).fetchone()
                if stat_row:
                    break
            except Exception:
                pass

    # Search rules vault for narrative description
    rdb = RulesDB(db_path=db_path)
    vault_rules = rdb.search_rules(item_id, limit=3)
    vault_text = ""
    source_citation = ""
    if vault_rules:
        best = vault_rules[0]
        raw_val = best.get("content") if isinstance(best, dict) else (best["content"] if best and "content" in best.keys() else "")
        vault_text = str(raw_val or "")
        # Remove frontmatter if present
        if vault_text.startswith("---"):
            parts = vault_text.split("---", 2)
            if len(parts) >= 3:
                vault_text = parts[2].strip()
        source = best.get("source", "SR6 Core") if isinstance(best, dict) else (best["source"] if "source" in best.keys() else "SR6 Core")
        page = best.get("page", "") if isinstance(best, dict) else (best["page"] if "page" in best.keys() else "")
        source_citation = f"[{source}{', Page ' + str(page) if page else ''}]"

    conn.close()

    card_name = item_id.replace("_", " ").title()
    stats = {}

    if stat_row:
        row_dict = dict(stat_row)
        card_name = row_dict.get("name", card_name)
        stats = {k: v for k, v in row_dict.items() if k not in ["raw_xml"]}

    # Format Markdown
    md_lines = [f"### [CARD] {card_name} ({category.replace('_', ' ').title()})"]
    if stats:
        stat_items = [f"**{k.replace('_', ' ').title()}**: {v}" for k, v in stats.items() if v not in [None, "", "-"]]
        md_lines.append("> " + " | ".join(stat_items))
    
    if vault_text:
        md_lines.append("\n" + vault_text[:500] + ("..." if len(vault_text) > 500 else ""))
    
    if source_citation:
        md_lines.append(f"\n*Source: {source_citation}*")

    card_md = "\n".join(md_lines)

    return {
        "id": item_id,
        "name": card_name,
        "category": category,
        "stats": stats,
        "vault_text": vault_text,
        "citation": source_citation,
        "markdown": card_md
    }


def _extract_id(item: Any) -> str:
    if isinstance(item, str):
        return item
    if isinstance(item, dict):
        return str(item.get("id") or item.get("name") or item.get("ref") or "")
    return str(item)


def export_character_card_deck(char_id: str, db_path: str = DEFAULT_DB_PATH) -> Tuple[str, str]:
    """
    Scans a character dossier and generates a full reference card deck in Markdown and HTML formats.
    """
    cm = CharacterManager()
    char = cm.load_character(char_id)
    if not char or "data" not in char:
        raise ValueError(f"Character '{char_id}' not found in portfolio configuration.")

    data = char["data"]
    char_name = data.get("name", char_id.title())
    archetype = data.get("archetype", "Shadowrunner")

    cards = []

    # 1. Qualities
    for q in data.get("qualities", []):
        qid = _extract_id(q)
        if qid:
            cards.append(get_item_card("quality", qid, db_path=db_path))

    # 2. Spells
    for s in data.get("spells", []):
        sid = _extract_id(s)
        if sid:
            cards.append(get_item_card("spell", sid, db_path=db_path))

    # 3. Complex Forms
    for cf in data.get("complex_forms", []):
        cid = _extract_id(cf)
        if cid:
            cards.append(get_item_card("complex_form", cid, db_path=db_path))

    # 4. Weapons
    for w in data.get("weapons", []):
        wid = _extract_id(w)
        if wid:
            cards.append(get_item_card("weapon", wid, db_path=db_path))

    # 5. Cyberware / Bioware
    for c in data.get("cyberware", []):
        cid = _extract_id(c)
        if cid:
            cards.append(get_item_card("cyberware", cid, db_path=db_path))

    # 6. Drones / Vehicles
    for v in data.get("drones", []) + data.get("vehicles", []):
        vid = _extract_id(v)
        if vid:
            cards.append(get_item_card("vehicle", vid, db_path=db_path))

    # 7. Programs
    for p in data.get("programs", []):
        pid = _extract_id(p)
        if pid:
            cards.append(get_item_card("program", pid, db_path=db_path))

    # Generate Deck Markdown
    md_deck_lines = [
        f"# [CARD] Reference Card Deck: {char_name} ({archetype})",
        f"*Total Reference Cards: {len(cards)}*\n",
        "---"
    ]
    for c in cards:
        md_deck_lines.append(c["markdown"])
        md_deck_lines.append("\n---\n")

    full_md = "\n".join(md_deck_lines)

    # Generate Styled HTML Deck
    html_cards = []
    for c in cards:
        stat_badges = "".join([
            f'<span class="badge"><b>{html.escape(k.title())}:</b> {html.escape(str(v))}</span> '
            for k, v in c["stats"].items() if v not in [None, "", "-"]
        ])
        card_html = f"""
        <div class="card">
            <div class="card-header">
                <span class="card-title">{html.escape(c["name"])}</span>
                <span class="card-cat">{html.escape(c["category"].replace('_', ' ').upper())}</span>
            </div>
            <div class="card-stats">{stat_badges}</div>
            <div class="card-body">{html.escape(c["vault_text"][:400])}</div>
            <div class="card-footer">{html.escape(c["citation"])}</div>
        </div>
        """
        html_cards.append(card_html)

    full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Reference Cards - {html.escape(char_name)}</title>
    <style>
        body {{ font-family: 'Segoe UI', system-ui, sans-serif; background: #0f172a; color: #f8fafc; padding: 20px; }}
        h1 {{ color: #38bdf8; border-bottom: 2px solid #0284c7; padding-bottom: 10px; }}
        .deck {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 16px; margin-top: 20px; }}
        .card {{ background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 16px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3); }}
        .card-header {{ display: flex; justify-space-between; align-items: center; border-bottom: 1px solid #334155; padding-bottom: 8px; margin-bottom: 12px; }}
        .card-title {{ font-weight: bold; font-size: 1.1em; color: #f1f5f9; }}
        .card-cat {{ font-size: 0.75em; background: #0284c7; color: #fff; padding: 2px 8px; border-radius: 4px; font-weight: bold; }}
        .card-stats {{ margin-bottom: 12px; font-size: 0.85em; }}
        .badge {{ display: inline-block; background: #334155; padding: 2px 6px; border-radius: 4px; margin-right: 4px; margin-bottom: 4px; }}
        .card-body {{ font-size: 0.9em; line-height: 1.4; color: #cbd5e1; white-space: pre-wrap; }}
        .card-footer {{ font-size: 0.8em; color: #38bdf8; margin-top: 12px; font-style: italic; }}
    </style>
</head>
<body>
    <h1>🃏 Reference Cards: {html.escape(char_name)} ({html.escape(archetype)})</h1>
    <div class="deck">
        {"".join(html_cards)}
    </div>
</body>
</html>
"""

    return full_md, full_html
